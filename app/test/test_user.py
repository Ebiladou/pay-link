import pytest
from datetime import datetime
from sqlmodel import select
from httpx import AsyncClient
from app.core.model import Users

async def test_get_user_ok(authorized_client: AsyncClient):
    response = await authorized_client.get(url="users/me")

    assert response.status_code == 200
    assert response.json() is not None
    assert response.json()["email"] == "support@paylink.co"
    assert response.json()["name"] == "Test User"
    assert response.json()["is_active"] is True

async def test_get_user_fail_user_unauthenticated(client: AsyncClient):
    response = await client.get(url="users/me")

    assert response.status_code == 401
    assert response.json() is not None
    assert response.json()["detail"] == "User not authenticated."

async def test_update_user_name_ok(authorized_client: AsyncClient, session):
    response = await authorized_client.put(
        url="users/update-profile",
        json={"name": "Updated Name"}
    )

    assert response.status_code == 200
    assert response.json() is not None
    assert response.json()["name"] == "Updated Name"
    assert response.json()["email"] == "support@paylink.co"

    result = await session.exec(select(Users).where(Users.email == "support@paylink.co"))
    user = result.first()
    assert user.name == "Updated Name"

async def test_update_user_name_and_email_ok(authorized_client: AsyncClient, session):
    response = await authorized_client.put(
        url="users/update-profile",
        json={
            "name": "New Name",
            "email": "newemail@example.com"
        }
    )

    assert response.status_code == 200
    assert response.json() is not None
    assert response.json()["name"] == "New Name"
    assert response.json()["email"] == "newemail@example.com"

    result = await session.exec(select(Users).where(Users.email == "newemail@example.com"))
    user = result.first()
    assert user is not None
    assert user.name == "New Name"
    assert user.updated_at is not None


async def test_update_user_fail_user_unauthenticated(client: AsyncClient):
    response = await client.put(
        url="users/update-profile",
        json={"name": "Updated Name"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "User not authenticated."


async def test_deactivate_user_ok(authorized_client: AsyncClient, session):
    response = await authorized_client.delete(url="users/deactivate")

    assert response.status_code == 200
    assert response.json() is not None
    assert response.json()["message"] == "Account will be parmenantely deleted in 30 days"

    result = await session.exec(select(Users).where(Users.email == "support@paylink.co"))
    user = result.first()
    assert user.deletion_requested is True

async def test_deactivate_user_fail_user_unauthenticated(client: AsyncClient):
    response = await client.delete(url="users/deactivate")

    assert response.status_code == 401
    assert response.json()["detail"] == "User not authenticated."


async def test_reactivate_user_ok(authorized_client: AsyncClient, session):
    result = await session.exec(select(Users).where(Users.email == "support@paylink.co"))
    user = result.first()
    user.deletion_requested = True
    session.add(user)
    await session.commit()

    response = await authorized_client.post(url="users/reactivate")

    assert response.status_code == 200
    assert response.json() is not None
    assert response.json()["message"] == "Account reactivated successfully"

    await session.refresh(user)
    assert user.deletion_requested is False

async def test_reactivate_user_fail_user_not_deactivated(authorized_client: AsyncClient):
    response = await authorized_client.post(url="users/reactivate")

    assert response.status_code == 400
    assert response.json() is not None
    assert response.json()["detail"] == "Account not deactivated"


async def test_reactivate_user_fail_user_unauthenticated(client: AsyncClient):
    response = await client.post(url="users/reactivate")

    assert response.status_code == 401
    assert response.json()["detail"] == "User not authenticated."

async def test_add_user_bank_details_ok(authorized_client: AsyncClient, session):
    response = await authorized_client.post(
        url="users/add-bank",
        json={
            "business_name": "Neo's business",
			"settlement_bank": "033",
			"account_number": "2122594324",
        }
    )
 
    assert response.status_code == 200
    assert response.json() is not None

    result = await session.exec(select(Users).where(Users.email == "support@paylink.co"))
    user = result.first()
    assert user.bank_details["bank"] == "United Bank For Africa"