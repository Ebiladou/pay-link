from sqlmodel import select
from fastapi import APIRouter, HTTPException, Request, Depends
from app.core.database import SessionDep
from app.core.schema import LinkResponse, LinkStatus, TransactionInitializeSchema, WebhookEvent
from app.core.enum import TransactionStatus, PaystackWebhookEvent
from app.core.model import Links, Transactions, Users
from app.core.config import settings
import secrets
from app.services.paystack import paystack_service
from app.core.logger import logger
import httpx
import hmac
import hashlib
import json
from datetime import datetime, UTC

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

    result = await session.exec(select(Transactions).where(Transactions.link_id == link.id, Transactions.status != TransactionStatus.FAILED))
    existing_transaction = result.first()

    if existing_transaction is not None:
        raise HTTPException(
            status_code=400, 
            detail="Payment already made."
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
    
    transaction_reference = response["data"]["reference"]
    authorization_url = response["data"]["authorization_url"]
    access_code = response["data"]["access_code"]

    transaction = Transactions(
        link_id=link.id,
        amount=link.amount,
        email=link.email,
        status=TransactionStatus.PENDING,
        reference=transaction_reference
    )
    session.add(transaction)
    await session.commit()
    
    return {
        "status": "success",
        "authorization_url": authorization_url,
        "access_code": access_code,
        "reference": transaction_reference
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
        "status": response["data"]["status"],
        "amount_paid": response["data"]["amount"],
        "payment channel": response["data"]["channel"],
        "time paid": response["data"]["paid_at"]
    }

@payment_router.post("/webhook")
async def paystack_webhook(request: Request, session: SessionDep):
    allowed_ips = ["52.31.139.75", "52.49.173.169", "52.214.14.220"]
    client_ip = request.client.host
    if client_ip not in allowed_ips:
        logger.error(f"Webhook request from unauthorized IP: {client_ip}")
        raise HTTPException(
            status_code=403, 
            detail="Unauthorized IP"
        )
    
    body = await request.body()

    signature = request.headers.get("x-paystack-signature")
    if not signature:
        logger.error("No Paystack signature provided")
        raise HTTPException(
            status_code=400, 
            detail="No signature provided"
        )
    
    secret = settings.PAYSTACK_SECRET_KEY.encode("utf-8")
    expected_signature = hmac.new(secret, body, digestmod=hashlib.sha512).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        logger.error("Invalid Paystack signature")
        raise HTTPException(
            status_code=400, 
            detail="Invalid signature"
        )

    try:
        event_data = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400, 
            detail="Invalid JSON body"
        )
    
    event = WebhookEvent(event=event_data["event"])
    data = event_data["data"]
    logger.info(f"Received Paystack webhook event: {event.event}")
    
    if event.event == PaystackWebhookEvent.CHARGE_SUCCESS:
        reference = data.get("reference")
        if reference:
            result = await session.exec(select(Transactions).where(Transactions.reference == reference))
            transaction = result.first()
            if transaction is not None:
                transaction.status = TransactionStatus.SUCCESS
                transaction.updated_at = datetime.now(UTC)
                session.add(transaction)
                await session.commit()
                logger.info(f"Transaction {reference} updated to SUCCESS")
            else:
                logger.warning(f"Transaction with reference {reference} not found")
    
    elif event.event == PaystackWebhookEvent.CHARGE_FAILED:
        reference = data.get("reference")
        if reference:
            result = await session.exec(select(Transactions).where(Transactions.reference == reference))
            transaction = result.first()
            if transaction is not None:
                transaction.status = TransactionStatus.FAILED
                transaction.updated_at = datetime.now(UTC)
                session.add(transaction)
                await session.commit()
                logger.info(f"Transaction {reference} updated to FAILED")
            else:
                logger.warning(f"Transaction with reference {reference} not found")
    
    return {"status": "ok"}