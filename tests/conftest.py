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
from sqlalchemy.pool import NullPool

from praxis.backend.utils.db import Base

# Use PostgreSQL test database - NO SQLITE FALLBACK
# The application uses PostgreSQL-specific features (JSONB) that SQLite doesn't support.
# Tests must run against the actual production database to ensure compatibility.
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://test_user:test_password@localhost:5432/test_db",
)


@pytest.fixture(scope="function")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Creates a function-scoped event loop for testing.
    This ensures each test gets a fresh event loop.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Creates a function-scoped test database engine and creates/drops tables.
    """
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(
    db_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Yields a single, transacted session for one test function.
    The transaction is rolled back after the test completes.

    Uses connection-level transactions to ensure proper rollback.
    """
    async with db_engine.connect() as connection:
        async with connection.begin() as transaction:
            # Create session bound to this connection
            session = AsyncSession(bind=connection, expire_on_commit=False)

            try:
                yield session
            finally:
                # Clean up session and transaction
                # Catch all errors to prevent test failures from cleanup operations
                try:
                    session.expunge_all()
                except Exception:
                    pass

                try:
                    await session.close()
                except Exception:
                    pass

                # Rollback transaction, catching circular dependency errors
                # These can occur when tests delete objects with complex cascade relationships
                try:
                    await transaction.rollback()
                except Exception:
                    # Ignore rollback errors - transaction will be cleaned up when connection closes
                    pass
