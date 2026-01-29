from fastapi import Request, HTTPException
from app.core.model import Users

async def get_current_user(request: Request) -> Users:
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(
            status_code=401, 
            detail="User not authenticated."
        )
    
    return user

async def require_user(request: Request) -> Users:
    user = await get_current_user(request)
    
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