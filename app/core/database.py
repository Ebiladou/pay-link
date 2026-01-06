from fastapi import Depends
from app.core.config import settings
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import Annotated

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True if settings.ENVIRONMENT == "dev" else False,
    future=True
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session():
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]