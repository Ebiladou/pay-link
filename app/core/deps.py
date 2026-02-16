from fastapi import Request, HTTPException, Depends
from app.core.model import Users
from app.core.database import SessionDep
from app.services.auth import authentication_service

async def get_current_user(request: Request, session: SessionDep) -> Users:
    token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(status_code=401, detail="User not authenticated.")
    
    user = await authentication_service.verify_jwt(token, session, "access_token")
    
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated.")
    
    return user

async def require_user(user: Users = Depends(get_current_user)) -> Users:
    if user.is_active is False:
        raise HTTPException(
            status_code=403,
            detail="User inactive, verify your email."
        )
    
    if user.deletion_requested is True:
        raise HTTPException(
            status_code=403,
            detail="Account deactivated, reactivate to continue."
        )
    
    return user