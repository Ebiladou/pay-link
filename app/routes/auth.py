from sqlmodel import select
from fastapi import APIRouter, HTTPException, Response, Request, Depends
from app.core.database import SessionDep
from app.core.schema import UserCreate, UserEmailSchema, ResetPasswordSchema, SignInUser
from app.core.model import User, Token
from app.utils.user_utils import hash_password, verify_password, generate_csrf_token, validate_csrf
from app.core.enum import TokenType
import secrets
from datetime import datetime, UTC
from app.services.emails import email_service
from app.services.auth import authentication_service

auth_router = APIRouter(prefix="/auth")

blacklisted_tokens = set([])

@auth_router.post("/register")
async def register(data: UserCreate, session: SessionDep):
    hashed_password = hash_password(data.password)

    result = await session.exec(select(User).where(User.email==data.email))
    existing_user = result.first()
    if existing_user is not None:
        raise HTTPException(
            status_code=409,
            detail="User with this email already exists"
        )

    user = User(
        **data.model_dump(exclude={"password"}),
        password=hashed_password
    )

    session.add(user)
    await session.commit()

    generate_token = secrets.token_urlsafe(42)

    token = Token(
        token=generate_token, 
        creator=user.email, 
        token_type=TokenType.CONFIRM_EMAIL, 
        created_at=datetime.now(UTC)
    )

    session.add(token)
    await session.commit()

    await email_service.send_verification_email(
        to=user.email,
        name=user.name,
        token=generate_token
    )

    return {
        "message": "Account Registered successfully. Check your email to verify."
    }

@auth_router.get("/confirm")
async def confirm_email(response: Response, token: str, session: SessionDep):
    result = await session.exec(
        select(Token).where(
            Token.token == token,
            Token.token_type == TokenType.CONFIRM_EMAIL
        )
    )

    existing_token = result.first()
    if existing_token is None:
        raise HTTPException(
            status_code=400, 
            detail="Invalid token"
        )
    
    result = await session.exec(select(User).where(User.email == existing_token.creator))
    user = result.first()
    
    if user is None:
        raise HTTPException(
            status_code=404, 
            detail="User not found"
        )
    
    user.is_active = True
    session.add(user)
    await session.commit()

    access_token = authentication_service.create_access_token(user.email)
    refresh_token_str = authentication_service.create_access_token(user.email, token_type="refresh_token")

    session.delete(existing_token)
    await session.commit()
    
    csrf_token = generate_csrf_token()

    response.set_cookie("access_token", access_token, httponly=True, secure=True, samesite="none", max_age=86400)
    response.set_cookie("refresh_token", refresh_token_str, httponly=True, secure=True, samesite="none", max_age=604800)
    response.set_cookie("csrf_token", csrf_token, httponly=False, secure=True, samesite="none", max_age=86400)

    return {
		"access_token": access_token,
		"refresh_token": refresh_token_str
	}

@auth_router.post("/resend-email")
async def resend_confirmation_mail(data: UserEmailSchema, session: SessionDep):
    result = await session.exec(select(User).where(User.email == data.email.lower()))
    user = result.first()

    if user is not None:
        if user.is_active is True:
            raise HTTPException(
                status_code=409,
                detail="Account has already been confirmed."
            )
        
    # find the exisiting token for that user and delete it

    result = await session.exec(select(Token).where(Token.creator == user.email, Token.token_type == TokenType.CONFIRM_EMAIL))
    existing_token = result.first()

    session.delete(existing_token)
    await session.commit()

    # then we generate a new token to be sent again
        
    generate_token = secrets.token_urlsafe(42)

    token = Token(
        token=generate_token, 
        creator=user.email, 
        token_type=TokenType.CONFIRM_EMAIL, 
        created_at=datetime.now(UTC)
    )

    session.add(token)
    await session.commit()

    await email_service.send_verification_email(
        to=user.email,
        name=user.name,
        token=generate_token
    )

    return {
        "message": "Confirmation mail snet. Check your email to verify your account."
    }

@auth_router.post("/reset-password-request")
async def reset_password_link(data: UserEmailSchema, session: SessionDep):
    result = await session.exec(select(User).where(User.email == data.email.lower()))
    user = result.first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )
    
    # find a token of the user and delete. if it's still in the database, then it has not been used / is expired. eitherway, useless, so delete. 

    result = await session.exec(select(Token).where(Token.creator == user.email, Token.token_type == TokenType.RESET_PASSWORD))
    existing_token = result.first()

    session.delete(existing_token)
    await session.commit()

    # create a new token and send link to user email

    generate_token = secrets.token_urlsafe(42)

    token = Token(
        token=generate_token, 
        creator=user.email, 
        token_type=TokenType.CONFIRM_EMAIL, 
        created_at=datetime.now(UTC)
    )

    session.add(token)
    await session.commit()

    await email_service.send_password_reset_email(
        to=user.email,
        name=user.name,
        token=generate_token
    )

    return {
        "message": "Check your email for link to change password."
    }

@auth_router.post("/reset-password-complete")
async def complete_reset_password(data: ResetPasswordSchema, session: SessionDep):
    result = await session.exec(select(Token).where(Token.token == data.token))
    token_exists = result.first()

    if token_exists is None:
        raise HTTPException(
			status_code=404,
			detail="Invalid token"
		)

    token_lifespan = abs(int(token_exists.created_at.timestamp()) - int(datetime.now().timestamp())) // 60

    if token_lifespan > 30:
        raise HTTPException(
			status_code=498,
			detail="Expired token"
		)

    if token_exists.token_type != TokenType.RESET_PASSWORD:
        raise HTTPException(
			status_code=498,
			detail="Invalid token"
		)
    
    result = await session.exec(select(User).where(User.email == token_exists.creator))
    user = result.first()

    if user is None:
        raise HTTPException(
			status_code=404,
			detail="User not found"
		)
    
    hashed_password = hash_password(data.password)
    user.password = hashed_password
    session.add(user)
    await session.commit()

    session.delete(token_exists)
    await session.commit()

    return {
		"message": "Password changed successful"
	}

@auth_router.post("/refresh", dependencies=[Depends(validate_csrf)])
async def refresh_token(request: Request, response: Response):
	result = authentication_service.decode_token(request.cookies.get("refresh_token"))
	if not result:
		raise HTTPException(status_code=401, detail="Refresh token has expired. Please start a new session.")

	csrf_token = generate_csrf_token()

	response.set_cookie("access_token", result.get("access_token"), httponly=True, secure=True, samesite="none", max_age=86400)

	response.set_cookie("csrf_token", csrf_token,  httponly=False, secure=True, samesite="none", max_age=86400)

	return True

@auth_router.post("/login")
async def login(response: Response, data: SignInUser, session: SessionDep):
    result = await session.exec(select(User).where(User.email == data.email))
    user = result.first()

    if user is None or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials."
        )
    
    token = authentication_service.create_access_token(user.email)
    refresh_token = authentication_service.create_access_token(user.email, token_type="refresh_token")
    csrf_token = generate_csrf_token()
    
    response.set_cookie("access_token", token, httponly=True, secure=True, samesite="none", max_age=86400)
    response.set_cookie("refresh_token", refresh_token, httponly=True, secure=True, samesite="none", max_age=604800)
    response.set_cookie("csrf_token", csrf_token, httponly=False, secure=True, samesite="none", max_age=86400)
    
    return {
		"message": "User signed in successfully",
		"access_token": token,
		"refresh_token": refresh_token
	}

@auth_router.post("/logout")
async def logout(request: Request, response: Response, session: SessionDep):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    csrf_token = request.cookies.get("csrf_token")
    
    if access_token:
        blacklisted_tokens.add(access_token)
        
    if refresh_token:
        blacklisted_tokens.add(refresh_token)
        
    if csrf_token:
        blacklisted_tokens.add(csrf_token)

    response.delete_cookie("access_token", path="/", secure=True, httponly=True, samesite="none")
    response.delete_cookie("refresh_token", path="/", secure=True, httponly=True, samesite="none")
    response.delete_cookie("csrf_token", path="/", secure=True, httponly=False, samesite="none")

    return {"message": "Successfully logged out."}