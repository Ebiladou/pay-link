from fastapi import APIRouter
from app.api.routes import user, auth

api_router = APIRouter()

api_router.include_router(
    auth.auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    user.user_router, 
    prefix="/users", 
    tags=["Users"]
)