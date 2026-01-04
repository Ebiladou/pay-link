from pydantic import BaseModel, Field, field_validator, ConfigDict, EmailStr, model_validator, field_serializer
from datetime import datetime
from typing import Optional
import re

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Reason must be at least 10 characters")
    
        special_characters = r"[!@#$%^&*(),.?\":{}|<>]"
        if not re.search(special_characters, v):
            raise ValueError("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)")
        
        return v

    model_config = ConfigDict(
		json_schema_extra={
			"example": {
				"name": "Big Lads",
                "email": "biglads@example.com",
                "password": "randomeight@"
			}
		}
	)

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Reason must be at least 10 characters")
    
        special_characters = r"[!@#$%^&*(),.?\":{}|<>]"
        if not re.search(special_characters, v):
            raise ValueError("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)")
        
        return v

    model_config = ConfigDict(
		json_schema_extra={
			"example": {
				"name": "Big Lads",
                "email": "biglads@example.com",
                "password": "randomeight@"
			}
		}
	)
class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)