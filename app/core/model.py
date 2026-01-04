from sqlmodel import Field, SQLModel
from pydantic import EmailStr
from typing import Optional
from datetime import datetime, UTC
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(unique=True, index=True)
    password: str
    is_active: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime(UTC))
    update_at: datetime = Field(default_factory=datetime(UTC))