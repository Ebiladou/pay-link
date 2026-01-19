import jwt
from fastapi import HTTPException
from datetime import datetime, timedelta, UTC
from pydantic import EmailStr
from app.core.model import User
from app.core.config import settings
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
import logging

logger = logging.getLogger(__name__)

class AuthenticationService:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = 7

    def create_access_token(self, user_id: EmailStr, token_type: str = "access_token"):
        now = datetime.now(UTC)

        if token_type == "refresh_token":
            expiry = now + timedelta(days=self.refresh_token_expire_days)
        else:
            expiry = now + timedelta(minutes=self.access_token_expire_minutes)

        payload = {
            "user_id": user_id,
            "iat": int(now.timestamp()),
            "exp": int(expiry.timestamp()),
            "type": token_type
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def create_refresh_token(self, user_id: EmailStr):
        return self.create_access_token(user_id, token_type="refresh_token")

    def decode_token(self, token: str):
        if not token:
            raise HTTPException(
                status_code=401,
                detail="Token not provided"
            )
        
        try:
            decoded_token = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return decoded_token

        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        except jwt.InvalidSignatureError as e:
            logger.warning(f"Invalid JWT token: {e}")
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
        except Exception as e:
            logger.exception(f"JWT decode error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Token validation failed"
            )

    async def verify_jwt(self, token: str, session: AsyncSession, expected_token_type: str = "access_token"):
        if not token:
            logger.warning("Empty token provided for verification")
            return None

        try:
            payload = self.decode_token(token)

            token_type = payload.get("type")
            if token_type != expected_token_type:
                logger.warning(
                    f"Token type mismatch. Expected: {expected_token_type}, got: {token_type}"
                )
                return None

            user_id = payload.get("user_id")
            if not user_id:
                logger.warning("Token missing user_id")
                return None

            statement = select(User).where(User.email == user_id)
            result = await session.exec(statement)
            user = result.scalar_one_or_none()

            if not user:
                logger.warning("User not found")
                return None

            return user

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error during JWT verification: {e}")
            return None

    async def refresh_access_token(self, refresh_token: str, session: AsyncSession):
        user = await self.verify_jwt(
            refresh_token, 
            session, 
            expected_token_type="refresh_token"
        )
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )

        new_access_token = self.create_access_token(user.email)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    
authentication_service = AuthenticationService()