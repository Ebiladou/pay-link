from sqlmodel import select
from fastapi import APIRouter, HTTPException, Request, Depends
from app.core.database import SessionDep
from app.core.schema import TransactionInitializeSchema
from app.core.model import Links

payment_router = APIRouter(prefix="/payments")