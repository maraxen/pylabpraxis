import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from praxis.backend.utils.db import Base

# Use PostgreSQL test database - NO SQLITE FALLBACK
# The application uses PostgreSQL-specific features (JSONB) that SQLite doesn't support.
# Tests must run against the actual production database to ensure compatibility.
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://test_user:test_password@localhost:5433/test_db",
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Creates a session-wide event loop for testing.
    This ensures pytest-asyncio uses a single loop.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Creates a session-wide test database engine and initializes the schema.

    IMPORTANT: This requires a running PostgreSQL database. Start it with:
        docker compose -f docker-compose.test.yml up -d

    If the database is unavailable, tests requiring it will fail with a clear error.
    This is intentional - we must test against PostgreSQL due to JSONB and other
    PostgreSQL-specific features used in production.
    """
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        # Re-create the database schema for a clean test run
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture(scope="session")
def db_sessionmaker(
    db_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Creates a session-wide sessionmaker bound to the test engine."""
    return async_sessionmaker(
        bind=db_engine, class_=AsyncSession, expire_on_commit=False
    )


@pytest_asyncio.fixture(scope="function")
async def db_session(
    db_sessionmaker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """
    Yields a single, transacted session for one test function.
    The transaction is rolled back after the test completes.
    """
    async with db_sessionmaker() as session:
        transaction = await session.begin()
        try:
            yield session
        finally:
            await transaction.rollback()
