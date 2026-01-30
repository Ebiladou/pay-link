from sqlmodel import select
from fastapi import APIRouter, HTTPException, Response, Request, Depends
from app.core.database import SessionDep
from app.core.schema import UserResponse, UserUpdate
from app.core.model import Users
from app.core.deps import require_user, get_current_user
from datetime import datetime, UTC

user_router = APIRouter(prefix="/users")

@user_router.get("/me", response_model=UserResponse)
async def get_user(request: Request, session: SessionDep, user: Users = Depends(require_user)):
    return user

@user_router.put("/update-profile", response_model=UserResponse)
async def update_user(request: Request, data: UserUpdate, session: SessionDep, user: Users = Depends(require_user)):

    update_data = data.model_dump(exclude_unset=True)

    user.sqlmodel_update(update_data)
    user.updated_at = datetime.now(UTC)
    session.add(user)
    await session.commit()

    return user

@user_router.delete("/deactivate")
async def delete_user(request: Request, session: SessionDep, user: Users = Depends(require_user)):
    user.deletion_requested = True
    user.updated_at = datetime.now(UTC)
    
    # Re: line above.
    #  I was wondering if a new isolated field to track this time frame should be added to the model, but on second thought, if account is deactivated, that's the last recorded timestamp on the update field since no other operation can be performed. But i'll think about the pitfalls. 
    
    session.add(user)
    await session.commit()

    return {
        "message": "Account will be parmenantely deleted in 30 days"
    }

@user_router.post("/reactivate")
async def reactivate_account(session: SessionDep, user: Users = Depends(get_current_user)):
    if user.deletion_requested is False:
        raise HTTPException(
            status_code=400,
            detail="Account not deactivated"
        )
    
    user.deletion_requested = False
    user.updated_at = datetime.now(UTC)
    
    session.add(user)
    await session.commit()
    
    return {"message": "Account reactivated successfully"}
