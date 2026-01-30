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

DEFAULT_ROUTES = [
    RouteRateLimit(path="/auth/login", requests=5, seconds=60), 
    RouteRateLimit(path="/auth/signup", requests=3, seconds=60)
]

class RateLimiterMiddleware(BaseHTTPMiddleware):    
    def __init__(self, app, routes: List[RouteRateLimit] = None):
        super().__init__(app)
        self.routes = {route.path: route for route in (routes or DEFAULT_ROUTES)}
        self.redis_client: Optional[redis.Redis] = None
    
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
    
    async def dispatch(self, request: Request, call_next):
        identifier = self.get_identifier(request)
        path = request.url.path
        
        # Check if this route has a rate limit
        if path not in self.routes:
            return await call_next(request)
        
        route_config = self.routes[path]
        rate_limit_key = f"rate_limit:{identifier}:{path}"
        
        try:
            redis_client = await self.get_redis_client()
            
            # Increment request count
            current_count = await redis_client.incr(rate_limit_key)
            
            # Set expiry on first request
            if current_count == 1:
                await redis_client.expire(rate_limit_key, route_config.seconds)
            
            # Check if limit exceeded
            if current_count > route_config.requests:
                return JSONResponse(
                    status_code=429,
                    content={"detail": f"Rate limit exceeded. Maximum {route_config.requests} requests per {route_config.seconds} seconds."}
                )
            
            # Process request
            response = await call_next(request)
            
            return response
            
        except Exception as e:
            return await call_next(request)
    
    async def close(self):
        if self.redis_client:
            await self.redis_client.close()