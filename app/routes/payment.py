from sqlmodel import select
from fastapi import APIRouter, HTTPException, Request, Depends
from app.core.database import SessionDep
from app.core.schema import LinkResponse, LinkStatus, TransactionInitializeSchema
from app.core.enum import TransactionStatus
from app.core.model import Links, Transactions, Users
import secrets
from app.services.paystack import paystack_service
from app.core.logger import logger
import httpx

payment_router = APIRouter(prefix="/payments")

@payment_router.get("/{link_id}", response_model=LinkResponse)
async def get_link_by_id(request: Request, link_id: int, session: SessionDep):
    result = await session.exec(select(Links).where(Links.id==link_id))
    link = result.first()
    if link is None:
        raise HTTPException(
            status_code=404,
            detail="Link not found"
        )

    return link

@payment_router.post("/{link_id}/pay")
async def make_payment(request: Request, link_id: int, session: SessionDep):
    result = await session.exec(select(Links).where(Links.id==link_id))
    link = result.first()
    if link is None:
        raise HTTPException(
            status_code=404,
            detail="Link not found"
        )
    
    if link.status != LinkStatus.ACTIVE:
        raise HTTPException(
            status_code=400, 
            detail="Payment link is not active"
        )

    result = await session.exec(select(Users).where(Users.id == link.creator))
    user = result.first()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User with link not found"
        )
    
    reference = f"txn_{secrets.token_urlsafe(16)}"
    
    transaction_data = TransactionInitializeSchema(
        amount=link.amount,
        email=link.email,
        currency="NGN",
        subaccount=user.bank_details.subaccount_code,
        reference=reference,
        metadata={
            "link_id": link.id,
            "creator_id": user.id,
            "creator": user.name
        }
    )

    try:
        response = await paystack_service.initialize_transaction(transaction_data)
    except httpx.HTTPStatusError as e:
        logger.error(f"status_code: {e.response.status_code} details: {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text
        )

    transaction = Transactions(
        payment_link_id=link.id,
        amount=link.amount,
        reference=reference,
        email=link.email,
        status=TransactionStatus.PENDING
    )
    session.add(transaction)
    await session.commit()
    
    return {
        "status": "success",
        "authorization_url": response["data"]["authorization_url"],
        "access_code": response["data"]["access_code"],
        "reference": reference
    }


@payment_router.post("/verify-payment")
async def verify_payment(request: Request, reference: str, session: SessionDep):
    result = await session.exec(select(Transactions).where(Transactions.reference==reference))
    transaction = result.first()
    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction with reference not found"
        )
    
    try:
        response = await paystack_service.verify_transaction(reference)
    except httpx.HTTPStatusError as e:
        logger.error(f"status_code: {e.response.status_code} details: {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text
        )
    
    return {
        "message": response["gateway_response"]
    }