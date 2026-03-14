from sqlmodel import select
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import func
from app.core.database import SessionDep
from app.core.deps import require_user
from app.core.model import Users, Transactions, Links
from app.core.enum import TransactionStatus
from app.core.schema import TransactionResponse, AggTransactionResponse
from datetime import datetime
from typing import Optional

transaction_router = APIRouter(prefix="/transactions")

@transaction_router.get("/{id}", response_model=TransactionResponse)
async def get_transaction(id: int, session: SessionDep, user: Users = Depends(require_user)):
    result = await session.exec(select(Transactions).where(Transactions.id == id, Transactions.owner == user.email))
    transaction = result.first()

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )
    
    link_result = await session.exec(select(Links).where(Links.id == transaction.link_id, Links.creator == user.id))
    link = link_result.first()
    
    return TransactionResponse(
        id = transaction.id,
        link_name = link.title if link is not None else "link deleted",
        amount = transaction.amount,
        email = transaction.email,
        status = transaction.status,
        created_at = transaction.created_at
    )

@transaction_router.get("/", response_model=AggTransactionResponse)
async def get_transactions(session: SessionDep, page_number: int = 1, page_size: int = 10, status: Optional[TransactionStatus] = None, user: Users = Depends(require_user)):
    query = select(Transactions).where(Transactions.owner == user.email)

    if status is not None:
        query = query.where(Transactions.status == status)

    count_result = await session.exec(select(func.count()).select_from(query.subquery()))
    total = count_result.one()

    offset = (page_number - 1) * page_size
    result = await session.exec(query.offset(offset).limit(page_size))
    transactions = result.all()

    if transactions == []:
        raise HTTPException(
            status_code=404, 
            detail="No transactions found"
        )

    link_ids = [t.link_id for t in transactions]
    links_result = await session.exec(select(Links).where(Links.id.in_(link_ids), Links.creator == user.id))
    links = {link.id: link for link in links_result.all()}

    data = [
        TransactionResponse(
            id=t.id,
            link_name=links[t.link_id].title if t.link_id in links else "link deleted",
            amount=t.amount,
            email=t.email,
            status=t.status,
            created_at=t.created_at
        )
        for t in transactions
    ]

    return AggTransactionResponse(
        total=total,
        data=data
    )