import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlmodel import SQLModel

from api.main import app
from db.session import engine, init_db


@pytest.fixture
async def client():
    """Async HTTP client wired directly to the FastAPI app (no real server needed)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def async_client():
    """Async client with full DB lifecycle — creates tables on setup, drops on teardown."""
    await init_db()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
