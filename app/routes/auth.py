from sqlmodel import select
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_session
from app.core.schema import UserCreate
from app.core.model import User, Token
from sqlmodel.ext.asyncio.session import AsyncSession
from app.utils.user_utils import hash_password
from app.core.enum import TokenType
import secrets
from datetime import datetime, UTC

auth_router = APIRouter()

# sign up users here, verify their account and set it to active. Refresh tokens and all of that here. Reset password.
# define the deps in dep.py file and import for simple use.
# get sendgrid api key to send confirm mail link to users.

@auth_router.post("/register")
async def register(
    data: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    hashed_password = hash_password(data.password)

    existing_user = await session.exec(select(User).where(User.email==data.email)).first()
    if existing_user is not None:
        raise HTTPException(
            status_code=409,
            detail="User with this email already exists"
        )

    user = User(
        **data.model_dump(exclude={"password"}),
        password=hashed_password
    )

    await session.add(user)
    await session.commit(user)

    generate_token = secrets.token_urlsafe(42)

    token = await Token(
        token=generate_token, 
        creator=user.email, 
        token_type=TokenType.CONFIRM_EMAIL, 
        created_at=datetime.now(UTC)
    )

    await session.add(token)
    await session.commit(token)

    # use sendgrid or whatever to dispatch the link. & find a cleaner way to perform db writes, current approach is horrible. 

    return {
        "message": "Please check and confirm your mail"
    }