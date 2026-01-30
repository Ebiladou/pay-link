from pydantic import BaseModel, Field, field_validator, ConfigDict, EmailStr, model_validator, field_serializer
from datetime import datetime
from typing import Optional, List
import re
from app.core.enum import LinkType, LinkStatus, PaystackChannel

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
     
class CreateLinkSchema(BaseModel):
	title: str
	description: Optional[str] = None
	amount: int
	type: LinkType

	model_config = ConfigDict(
		json_schema_extra={
			"example": {
				"title": "Payment for Service",
				"description": "Payment link for consulting service",
				"amount": 5000,
				"type": "close"
			}
		}
	)

class UpdateLinkSchema(BaseModel):
	title: Optional[str] = None
	description: Optional[str] = None
	amount: Optional[int] = None
	type: Optional[LinkType] = None

	model_config = ConfigDict(
		json_schema_extra={
			"example": {
				"title": "Updated Payment for Service",
				"description": "Updated payment link for consulting service",
				"amount": 6000,
				"type": "open"
			}
		}
	)
     
class LinkResponse(BaseModel):
    id: int
    creator: int
    token: str
    title: str
    description: Optional[str] = None
    amount: int
    type: LinkType
    status: LinkStatus
    created_at: datetime
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
				"id": 1,
				"creator": 1,
				"token": "mkjk867bnsdy78879snb789909u89090fhjjk",
				"title": "Payment for Service",
				"description": "Payment link for consulting service",
				"amount": 5000,
				"type": "close",
				"status": "active",
				"created_at": "2023-01-01T00:00:00Z"
			}
		}
	)
    
class BankCreateSchema(BaseModel):
    account_number: str
    bank_code: str 
    
    model_config = ConfigDict(
		json_schema_extra={
			"example": {
                "account_number": "1234567890",
				"bank_code": "058"	
			}
		}
	)
    
class SubAccountCreateSchema(BaseModel):
	business_name: str
	settlement_bank: str
	account_number: str
	percentage_charge: float = 0.5
	
	model_config = ConfigDict(
		json_schema_extra={
			"example": {
				"business_name": "My Business",
				"settlement_bank": "058",
				"account_number": "1234567890",
				"percentage_charge": 0.5	
			}
		}
	)
     	 
class BankDetails(BaseModel):
    bank: str
    account_number: str
    subaccount_code: str
     
class TransactionInitializeSchema(BaseModel):
    amount: int
    email: EmailStr
    channels: Optional[List[PaystackChannel]] = None
    currency: Optional[str] = "NGN"
    subaccount: Optional[str] = None

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "amount": 50000,
                "email": "customer@example.com",
                "subaccount": "ACCT_8f4s1eq7ml6rlzj",
                "channels": ["card", "bank_transfer"],
                "currency": "NGN"
            }
        }
    )
