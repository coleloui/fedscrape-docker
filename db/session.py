from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from api.config import settings

_database_url = (
    settings.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1).replace(
        "postgresql://", "postgresql+asyncpg://", 1
    )
)

engine = create_async_engine(_database_url, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """Create all tables (idempotent — safe to call on every startup)."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
