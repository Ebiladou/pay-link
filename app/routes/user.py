from sqlmodel import select
from fastapi import APIRouter, HTTPException, Response, Request, Depends
from app.core.database import SessionDep
from app.core.schema import UserResponse, UserUpdate, SubAccountCreateSchema, BankDetails
from app.core.model import Users
from app.core.deps import require_user, get_current_user
from datetime import datetime
from app.services.paystack import paystack_service
from app.core.logger import logger
import httpx

user_router = APIRouter(prefix="/users")

@user_router.get("/me", response_model=UserResponse)
async def get_user(request: Request, session: SessionDep, user: Users = Depends(require_user)):
    return user

@user_router.put("/update-profile", response_model=UserResponse)
async def update_user(request: Request, data: UserUpdate, session: SessionDep, user: Users = Depends(require_user)):

    update_data = data.model_dump(exclude_unset=True)

    user.sqlmodel_update(update_data)
    user.updated_at = datetime.now()
    session.add(user)
    await session.commit()

    return user

@user_router.delete("/deactivate")
async def delete_user(request: Request, session: SessionDep, user: Users = Depends(require_user)):
    user.deletion_requested = True
    user.updated_at = datetime.now()
    
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
    user.updated_at = datetime.now()
    
    session.add(user)
    await session.commit()
    
    return {
        "message": "Account reactivated successfully"
    }

@user_router.get("/banks")
async def get_banks(user: Users = Depends(require_user)):
    try:
        response = await paystack_service.list_banks()
    except httpx.HTTPStatusError as e:
        logger.error(f"status_code: {e.response.status_code} details: {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text
        )
    
    return {
        "bank_name": response["data"]["name"],
        "bank_code": response["data"]["code"]
    }

@user_router.post("/add-bank")
async def add_bank_account(session: SessionDep, data: SubAccountCreateSchema, user: Users = Depends(require_user)):
    if user.bank_details is not None:
        raise HTTPException(
            status_code=400,
            detail="Bank details already exist."
        )

    account_data = SubAccountCreateSchema(
        business_name=data.business_name,
        settlement_bank=data.settlement_bank,
        account_number=data.account_number
    )
    try:
        response = await paystack_service.create_subaccount(account_data)
    except httpx.HTTPStatusError as e:
        logger.error(f"status_code: {e.response.status_code} details: {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text
        )
    
    bank_name = response["data"]["settlement_bank"]
    account_number = response["data"]["account_number"]
    code = response["data"]["subaccount_code"]

    user.bank_details = BankDetails(
        bank=bank_name,
        account_number=account_number,
        subaccount_code=code
    ).model_dump()
    user.updated_at = datetime.now()

    # Ehnnn. Thinking about it, should've made it non repetitive to assign at once on the user object instead of defining first then assigning. --> eg; user.bank_details.bank = response["data"]["settlement_bank"]. Saying I've moved on sounds lazy, but I genuinly have moved and it's honestly a non issue, just a bit not DRY. Sigh.

    session.add(user)
    await session.commit()

    return {
        "message": "Account added successfully"
    }