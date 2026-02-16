import pytest
import jwt
import time
from collections.abc import AsyncIterator
from datetime import datetime
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import app
from app.core.database import get_session
from app.core.model import Users
from app.utils.user_utils import hash_password
from app.core.config import settings
from sqlalchemy.pool import NullPool

test_engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(autouse=True)
async def test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
async def session(test_db) -> AsyncIterator[AsyncSession]:
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
def fastapi_app(session: AsyncSession) -> FastAPI:
    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
async def client(fastapi_app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app),
        base_url="http://test/"
    ) as client:
        yield client


TEST_CSRF_TOKEN = "test-csrf-token"


@pytest.fixture
async def authorized_client(fastapi_app: FastAPI, session: AsyncSession) -> AsyncIterator[AsyncClient]:
    user = Users(
        name="Test User",
        email="support@paylink.co",
        password=hash_password("testpassword@"),
        is_active=True
    )
    session.add(user)
    await session.commit()

    payload = {
        "user_id": "support@paylink.co",
        "iat": int(datetime.now().timestamp()),
        "exp": int(time.time() + (60 * 60)),
        "type": "access_token",
    }

    access_token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    refresh_token = jwt.encode(
        {
            "user_id": "support@paylink.co",
            "iat": int(datetime.now().timestamp()),
            "exp": int(time.time() + (60 * 60)),
            "type": "refresh_token"
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app),
        base_url="http://test/"
    ) as client:
        client.cookies.set("access_token", access_token)
        client.cookies.set("refresh_token", refresh_token)
        client.cookies.set("csrf_token", TEST_CSRF_TOKEN)
        client.headers.update({"X-CSRF-Token": TEST_CSRF_TOKEN})

        yield client