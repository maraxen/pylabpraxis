import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

# Import the 'schedule' module to ensure its event listeners are registered.
import praxis.backend.models.orm.schedule
from praxis.backend.utils.db import Base

# Use the PostgreSQL database from the docker-compose.test.yml file
ASYNC_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5433/test_db"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Create a new engine for the test session."""
    async_engine = create_async_engine(ASYNC_DATABASE_URL)
    yield async_engine
    await async_engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database(engine):
    """Set up the database schema once for the test session."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture(scope="function")
async def db(engine, setup_database) -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture that provides a transaction-isolated session for each test function.
    """
    async with engine.connect() as connection:
        async with connection.begin() as transaction:
            SessionLocal = sessionmaker(
                bind=connection, class_=AsyncSession, expire_on_commit=False
            )
            session = SessionLocal()

            try:
                yield session
            finally:
                await session.close()
                await transaction.rollback()
