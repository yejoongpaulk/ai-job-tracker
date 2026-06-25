import os
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Use asyncpg or psycopg async driver via +psycopg suffix
# Example: postgresql+psycopg://user:pass@localhost:5432/dbname

# Using os.environ["KEY"] raises an immediate KeyError if the variable does not exist
try:
    DATABASE_URL = os.environ["DATABASE_URL"]
except KeyError:
    raise RuntimeError(
        "CRITICAL STARTUP ERROR: The 'DATABASE_URL' environment variable is not set. " +
        "Please configure your environment or .env file before launching."
    ) from None


# 1. Create high-performance Async Engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL log debugging
    pool_pre_ping=True,  # Automatically recovers dropped connections
)

# 2. Configure Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # Prevents unnecessary DB reads after commits
)

# 3. Modern SQLAlchemy 2.0 Base Class
class Base(DeclarativeBase):
    pass

# 4. Clean Async Dependency Provider
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
