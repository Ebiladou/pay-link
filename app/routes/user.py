from sqlmodel import select
from fastapi import APIRouter, HTTPException, Response, Request, Depends
from app.core.database import SessionDep
from app.core.schema import UserResponse, UserUpdate
from app.core.model import User
from app.core.deps import require_user, get_current_user
from datetime import datetime, UTC

user_router = APIRouter(prefix="/users")

@user_router.get("/me", response_model=UserResponse)
async def get_user(request: Request, session: SessionDep, user: User = Depends(require_user)):
    return user

@user_router.put("/update-profile", response_model=UserResponse)
async def update_user(request: Request, data: UserUpdate, session: SessionDep, user: User = Depends(require_user)):

    update_data = data.model_dump(exclude_unset=True)

    user.sqlmodel_update(update_data)
    session.add(user)
    await session.commit()

    return user

@user_router.delete("/deactivate")
async def delete_user(request: Request, session: SessionDep, user: User = Depends(require_user)):
    user.deletion_requested = True
    user.updated_at = datetime.now(UTC)
    session.add(user)
    await session.commit()

    return {
        "message": "Account will be parmenantely deleted in 30 days"
    }

@user_router.post("/reactivate")
async def reactivate_account(session: SessionDep, user: User = Depends(get_current_user)):
    if not user.deletion_requested:
        raise HTTPException(
            status_code=400,
            detail="Account not deactivated"
        )
    
    user.deletion_requested = False
    user.updated_at = datetime.now(UTC)
    
    session.add(user)
    await session.commit()
    
    return {"message": "Account reactivated successfully"}
