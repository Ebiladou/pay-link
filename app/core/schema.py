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
            raise ValueError("Password must be at least 6 characters")
    
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

    model_config = ConfigDict(
		json_schema_extra={
			"example": {
				"name": "Big Lads",
                "email": "biglads@example.com"
			}
		}
	)

class UserEmailSchema(BaseModel):
    email: str
     
    model_config = ConfigDict(
		json_schema_extra={
			"example": {
                "email": "biglads@example.com"
			}
		}
	)

class ResetPasswordSchema(BaseModel):
    token: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
    
        special_characters = r"[!@#$%^&*(),.?\":{}|<>]"
        if not re.search(special_characters, v):
            raise ValueError("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)")
        
        return v
     
    model_config = ConfigDict(
		json_schema_extra={
			"example": {
				"token": "token123",
				"password": "randomeight@"
			}
		}
	)
class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AccessTokenResponse(BaseModel):
	access_token: str
	refresh_token: str

	model_config = ConfigDict(
		json_schema_extra={
			"example": {
				"access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYWJkdWxAeW91bmdlc3QuZGV2IiwiZXhwaXJlcyI6MTY0OTQyMTY5OC42OTUyNDR9.ULOUfgRqhc1An2PtWbhDiWuBmGyi1TNGfr6eNwgJ368",
				"refresh_token": "eyJ0XXAncu8iJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYWJkdWxAeW91bmdlc3QuZGV2IiwiZXhwaXJlcyI6MTY0OTQyMTY5OC42OTUyNDR9.ULOUfgRqhc1An2PtWbhDiWuBmGyi1TNGfr6eNwgJ368"
			}
		}
	)

class SignInUser(BaseModel):
	email: EmailStr
	password: str
     
	@field_validator("email")
	def lowercase_email(cls, v: str) -> str:
		return v.lower()

	model_config = ConfigDict(
		json_schema_extra={
			"example": {
				"email": "biglads@example.com",
                "password": "randomeight@"
			}
		})
