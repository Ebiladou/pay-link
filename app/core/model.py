from sqlmodel import Field, SQLModel
from pydantic import EmailStr
from typing import Optional
from datetime import datetime, UTC
from app.core.enum import TokenType

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(unique=True, index=True)
    password: str
    is_active: bool = Field(default=False)
    deletion_requested: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)  
    updated_at: datetime = Field(default_factory=datetime.now)  

class Token(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    token: str
    creator: str
    token_type: TokenType
    created_at: datetime = Field(default_factory=datetime.now)  