from sqlmodel import SQLModel, Field, Column, Relationship
from pydantic import EmailStr
from typing import Optional, List
from datetime import datetime, UTC
from app.core.enum import TokenType, LinkType, LinkStatus, TransactionStatus
from app.core.schema import BankDetails
from sqlalchemy import JSON

class Users(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(unique=True, index=True)
    password: str
    is_active: bool = Field(default=False)
    bank_details: Optional[BankDetails] = Field(default=None, sa_column=Column(JSON))
    deletion_requested: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)  
    updated_at: datetime = Field(default_factory=datetime.now)  

class Token(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    token: str
    creator: str
    token_type: TokenType
    created_at: datetime = Field(default_factory=datetime.now)

class Links(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    creator: int = Field(foreign_key="users.id")
    token: str = Field(unique=True, index=True)
    title: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None)
    amount: int = Field (nullable=False)
    type: LinkType
    status: LinkStatus = Field(default=LinkStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Transactions(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    link_id: int = Field(foreign_key="links.id")
    amount: int = Field(nullable=False)
    email: str
    status: TransactionStatus = Field(default=TransactionStatus.PENDING)
    reference: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)