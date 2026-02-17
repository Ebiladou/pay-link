import pytest
from sqlmodel import select
from httpx import AsyncClient
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
        url="links/",
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
        url="links/",
        json=link_data
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Add your bank details before creating a link."

async def test_get_links_ok_with_pagination(authorized_client: AsyncClient, session):
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

    for i in range(10):
        link = Links(
            creator=user.id,
            token=f"test-token-{i}",
            title=f"Payment for Service {i}",
            description="Payment link for consulting service",
            amount=5000,
            email="ladou@gmail.com",
            type=LinkType.CLOSED.value
        )
        session.add(link)
    await session.commit()

    response = await authorized_client.get(
        url="links/",
        params={"page_number": 1, "page_size": 5}
    )

    assert response.status_code == 200
    assert len(response.json()) == 5

    response = await authorized_client.get(
        url="links/",
        params={"page_number": 2, "page_size": 5}
    )

    assert response.status_code == 200
    assert len(response.json()) == 5

    response = await authorized_client.get(
        url="links/",
        params={"status": "inactive"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "No links found"

async def test_get_link_ok(authorized_client: AsyncClient, session):
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

    link = Links(
        creator=user.id,
        token="test-token",
        title="Payment for consult",
        description="Payment link for consulting service",
        amount=5000,
        email="ladou@gmail.com",
        type=LinkType.CLOSED.value
    )

    session.add(link)
    await session.commit()

    response = await authorized_client.get(
        url=f"links/{link.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Payment for consult"

async def test_get_link_fail_no_link(authorized_client: AsyncClient, session):
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

    response = await authorized_client.get(
        url=f"links/1"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Link not found"

async def test_get_link_fail_unauthenticated_user(authorized_client: AsyncClient, client: AsyncClient, session):
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

    link = Links(
        creator=user.id,
        token="test-token",
        title="Payment for consult",
        description="Payment link for consulting service",
        amount=5000,
        email="ladou@gmail.com",
        type=LinkType.CLOSED.value
    )

    session.add(link)
    await session.commit()

    response = await client.get(
        url=f"links/{link.id}"
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "User not authenticated."

async def test_update_link_ok(authorized_client: AsyncClient, session):
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

    link = Links(
        creator=user.id,
        token="test-token",
        title="Payment for consult",
        description="Payment link for consulting service",
        amount=5000,
        email="ladou@gmail.com",
        type=LinkType.CLOSED.value
    )

    session.add(link)
    await session.commit()

    response = await authorized_client.put(
        url=f"links/{link.id}",
        json={
            "amount": 10000
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 10000

async def test_update_link_fail_unauthorized_user(authorized_client: AsyncClient, client: AsyncClient, session):
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

    link = Links(
        creator=user.id,
        token="test-token",
        title="Payment for consult",
        description="Payment link for consulting service",
        amount=5000,
        email="ladou@gmail.com",
        type=LinkType.CLOSED.value
    )

    session.add(link)
    await session.commit()

    response = await client.put(
        url=f"links/{link.id}",
        json={
            "amount": 10000
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "User not authenticated."

async def test_update_link_fail_no_link(authorized_client: AsyncClient, session):
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

    response = await authorized_client.put(
        url=f"links/1",
        json={
            "amount": 10000
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Link not found"

async def test_delete_link_ok(authorized_client: AsyncClient, session):
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

    link = Links(
        creator=user.id,
        token="test-token",
        title="Payment for consult",
        description="Payment link for consulting service",
        amount=5000,
        email="ladou@gmail.com",
        type=LinkType.CLOSED.value
    )

    session.add(link)
    await session.commit()

    response = await authorized_client.delete(
        url=f"links/{link.id}"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Link deleted successfully"

async def test_delete_link_fail_unauthorized_user(authorized_client: AsyncClient, client: AsyncClient, session):
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

    link = Links(
        creator=user.id,
        token="test-token",
        title="Payment for consult",
        description="Payment link for consulting service",
        amount=5000,
        email="ladou@gmail.com",
        type=LinkType.CLOSED.value
    )

    session.add(link)
    await session.commit()

    response = await client.delete(
        url=f"links/{link.id}"
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "User not authenticated."

async def test_delete_link_fail_no_link(authorized_client: AsyncClient, session):
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

    response = await authorized_client.delete(
        url=f"links/1"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Link not found"