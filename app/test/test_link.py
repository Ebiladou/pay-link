import pytest
from datetime import datetime
from sqlmodel import select
from httpx import AsyncClient
from starlette.testclient import TestClient
from app.core.model import Users, Links
from app.core.enum import LinkStatus, LinkType

async def test_create_link_ok(authorized_client: AsyncClient, session):
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

    link_data = {
        "title": "Payment for Service",
		"description": "Payment link for consulting service",
		"amount": 2000,
        "email": "ladou@gmail.com",
		"type": LinkType.CLOSED.value
    }

    response = await authorized_client.post(
        url="/links/",
        json=link_data
    )

    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "Payment for Service"
    assert data["amount"] == 2000
    assert data["status"] == LinkStatus.ACTIVE.value

async def test_create_link_fail_no_bank_account(authorized_client: AsyncClient, session):
    link_data = {
        "title": "Payment for Service",
		"description": "Payment link for consulting service",
		"amount": 2000,
        "email": "ladou@gmail.com",
		"type": LinkType.CLOSED.value
    }

    response = await authorized_client.post(
        url="/links/",
        json=link_data
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Add your bank details before creating a link."