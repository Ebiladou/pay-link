from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.database import engine
from app.services.auth import authentication_service
from app.routes.auth import blacklisted_tokens

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.cookies.get("access_token")
        
        if token and token not in blacklisted_tokens:
            async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            async with async_session() as session:
                try:
                    user = await authentication_service.verify_jwt(token, session, "access_token")
                except HTTPException:
                    user = None
                request.state.user = user
        else:
            request.state.user = None
    
        response = await call_next(request)
        return response