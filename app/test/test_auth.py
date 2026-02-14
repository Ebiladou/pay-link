import pytest
from datetime import datetime
from sqlmodel import select
from httpx import AsyncClient
from starlette.testclient import TestClient
from app.core.model import Users, Token
from app.core.enum import TokenType
from app.utils.user_utils import hash_password

async def test_signup_ok(client: AsyncClient):
    user_data = {
        "name": "Big Lads",
        "email": "biglads@example.com",
        "password": "randomeight@"
    }

    response = await client.post(
        url="auth/signup",
        json=user_data
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Account Registered successfully. Check your email to verify."


async def test_signup_fail_duplicate_email(client: AsyncClient, session):
    user_data = {
        "name": "Big Lads",
        "email": "biglads@example.com",
        "password": "randomeight@"
    }

    user = Users(
        name=user_data["name"],
        email=user_data["email"],
        password=hash_password(user_data["password"])
    )
    session.add(user)
    await session.commit()

    response = await client.post(
        url="auth/signup",
        json=user_data
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email already exists"


async def test_signup_fail_short_password(client: AsyncClient):
    response = await client.post(
        url="auth/signup",
        json={
            "name": "Big Lads",
            "email": "biglads@example.com",
            "password": "short"
        }
    )

    assert response.status_code == 422


async def test_signup_fail_password_no_special_char(client: AsyncClient):
    response = await client.post(
        url="auth/signup",
        json={
            "name": "Big Lads",
            "email": "biglads@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 422


async def test_confirm_email_ok(client: AsyncClient, session):
    user = Users(
        name="Big Lads",
        email="biglads@example.com",
        password=hash_password("randomeight@")
    )
    session.add(user)
    await session.commit()

    token = Token(
        creator=user.email,
        token_type=TokenType.CONFIRM_EMAIL
    )
    session.add(token)
    await session.commit()

    response = await client.get(
        url="auth/confirm-email",
        params={"token": token.token}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

    result = await session.exec(select(Users).where(Users.email == user.email))
    updated_user = result.first()
    assert updated_user.is_active is True

async def test_confirm_email_fail_invalid_token(client: AsyncClient):
    response = await client.get(
        url="auth/confirm-email",
        params={"token": "invalid-token"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid token"


async def test_login_ok(client: AsyncClient, session):
    user = Users(
        name="Big Lads",
        email="biglads@example.com",
        password=hash_password("randomeight@"),
        is_active=True
    )
    session.add(user)
    await session.commit()

    response = await client.post(
        url="auth/login",
        json={
            "email": "biglads@example.com",
            "password": "randomeight@"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "User signed in successfully"
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

async def test_login_fail_wrong_password(client: AsyncClient, session):
    user = Users(
        name="Big Lads",
        email="biglads@example.com",
        password=hash_password("randomeight@"),
        is_active=True
    )
    session.add(user)
    await session.commit()

    response = await client.post(
        url="auth/login",
        json={
            "email": "biglads@example.com",
            "password": "wrongpassword@"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials."


async def test_login_fail_wrong_email(client: AsyncClient, session):
    response = await client.post(
        url="auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "randomeight@"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials."


async def test_resend_email_ok(client: AsyncClient, session):
    user = Users(
        name="Big Lads",
        email="biglads@example.com",
        password=hash_password("randomeight@"),
        is_active=False
    )
    session.add(user)
    await session.commit()

    token = Token(
        token="old-token-123",
        creator=user.email,
        token_type=TokenType.CONFIRM_EMAIL
    )
    session.add(token)
    await session.commit()

    response = await client.post(
        url="auth/resend-email",
        json={"email": user.email}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Confirmation mail sent. Check your email to verify your account."

async def test_resend_email_fail_already_active(client: AsyncClient, session):
    user = Users(
        name="Big Lads",
        email="biglads@example.com",
        password=hash_password("randomeight@"),
        is_active=True
    )
    session.add(user)
    await session.commit()

    response = await client.post(
        url="auth/resend-email",
        json={"email": user.email}
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Account has already been confirmed."


async def test_reset_password_request_ok(client: AsyncClient, session):
    user = Users(
        name="Big Lads",
        email="biglads@example.com",
        password=hash_password("randomeight@"),
        is_active=True
    )
    session.add(user)
    await session.commit()

    response = await client.post(
        url="auth/reset-password-request",
        json={"email": user.email}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Check your email for link to change password."


async def test_reset_password_request_fail_user_not_found(client: AsyncClient):
    response = await client.post(
        url="auth/reset-password-request",
        json={"email": "nonexistent@example.com"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


async def test_complete_reset_password_ok(client: AsyncClient, session):
    user = Users(
        name="Big Lads",
        email="biglads@example.com",
        password=hash_password("randomeight@"),
        is_active=True
    )
    session.add(user)
    await session.commit()

    token = Token(
        creator=user.email,
        token_type=TokenType.RESET_PASSWORD
    )
    session.add(token)
    await session.commit()

    response = await client.post(
        url="auth/password-reset",
        json={
            "token": token.token,
            "password": "newpassword@"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Password change successful"

async def test_complete_reset_password_fail_invalid_token(client: AsyncClient):
    response = await client.post(
        url="auth/password-reset",
        json={
            "token": "invalid-token",
            "password": "newpassword@"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Invalid token"


async def test_logout_ok(authorized_client: AsyncClient):
    response = await authorized_client.post(url="auth/logout")

    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out."