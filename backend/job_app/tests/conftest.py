import os

# job_app/tests/conftest.py
from collections.abc import AsyncGenerator
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from job_app.database import Base, get_db
from job_app.dependency import valkey_client
from job_app.__main__ import app


# 🚀 No more hardcoded connection strings! 
# Uses os.environ to throw an immediate clear error if the variable is missing.
try:
    TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]
except KeyError:
    raise RuntimeError(
        "CRITICAL TESTING ERROR: The 'TEST_DATABASE_URL' variable is missing from your .env configuration file."
    ) from None

#  The manual 'def event_loop():' function has been deleted!

@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Initializes a completely empty test database structure."""
    engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Creates a transactional database session for isolation."""
    engine = create_async_engine(TEST_DATABASE_URL)
    testing_session_local = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with testing_session_local() as session:
        yield session
    await engine.dispose()

@pytest.fixture(autouse=True)
async def clean_valkey():
    """Wipes Valkey testing session data before every test."""
    await valkey_client.flushdb()
    yield

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provides an isolated Async HTTPX Client with database dependencies mocked."""
    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://testserver") as async_client:
        yield async_client
    app.dependency_overrides.clear()
