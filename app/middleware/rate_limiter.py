import redis.asyncio as redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi import Request
from app.core.config import settings
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class RouteRateLimit:
    path: str
    requests: int
    seconds: int

SPECIFIC_ROUTES = [
    RouteRateLimit(path="/auth/login", requests=5, seconds=60),
    RouteRateLimit(path="/auth/signup", requests=3, seconds=60),
    RouteRateLimit(path="/auth/forgot-password", requests=3, seconds=60),
    RouteRateLimit(path="/auth/password-reset", requests=3, seconds=60)
]

DEFAULT_ROUTES = RouteRateLimit(path="*", requests=10, seconds=60)

EXCLUDED_PATHS = {
    "/docs",
    "/redoc",
    "/openapi.json",
    "/health",
}

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, routes: List[RouteRateLimit] = None, default: RouteRateLimit = None):
        super().__init__(app)
        self.routes = {route.path: route for route in (routes or SPECIFIC_ROUTES)}
        self.default = default or DEFAULT_ROUTES
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = settings.ENVIRONMENT != "test"

    async def get_redis_client(self):
        if self.redis_client is None:
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
        return self.redis_client

    def get_identifier(self, request: Request):
        user = getattr(request.state, "user", None)
        if user:
            return f"user:{user.id}"
        else:
            client_ip = request.client.host
            return f"ip:{client_ip}"

    def resolve_route_config(self, path: str):
        normalized = path.removeprefix("/api/v1")

        if normalized in EXCLUDED_PATHS:
            return None

        if normalized in self.routes:
            return self.routes[normalized]

        return self.default

    async def check_rate_limit(self, redis_client, identifier: str, path: str, config: RouteRateLimit):
        rate_limit_key = f"rate_limit:{identifier}:{path}"

        current_count = await redis_client.incr(rate_limit_key)

        if current_count == 1:
            await redis_client.expire(rate_limit_key, config.seconds)

        exceeded = current_count > config.requests
        return exceeded, current_count

    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)
        
        path = request.url.path
        config = self.resolve_route_config(path)

        if config is None:
            return await call_next(request)

        identifier = self.get_identifier(request)

        limit_key = "*" if config.path == "*" else path

        try:
            redis_client = await self.get_redis_client()
            is_limited, current_count = await self.check_rate_limit(redis_client, identifier, limit_key, config)

            if is_limited:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": f"Rate limit exceeded. Max {config.requests} requests per {config.seconds}s."
                    },
                    headers={
                        "X-RateLimit-Limit": str(config.requests),
                        "X-RateLimit-Remaining": "0",
                        "Retry-After": str(config.seconds),
                    }
                )

            response = await call_next(request)

            response.headers["X-RateLimit-Limit"] = str(config.requests)
            response.headers["X-RateLimit-Remaining"] = str(max(0, config.requests - current_count))

            return response

        except Exception as e:
            return await call_next(request)

    async def close(self):
        if self.redis_client:
            await self.redis_client.close()