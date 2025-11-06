import asyncio
from typing import AsyncGenerator

import pytest
from _pytest.monkeypatch import MonkeyPatch
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

# Import the 'schedule' module to ensure its event listeners are registered.
import praxis.backend.models.orm.schedule
from praxis.backend.utils.db import Base

# Use the PostgreSQL database from the docker-compose.test.yml file
ASYNC_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5433/test_db"




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


@pytest_asyncio.fixture(scope="function", autouse=True)
async def factories_session(db: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture that provides the db session to all factory-boy factories.
    """
    from tests.factories import WorkcellFactory, MachineFactory, ResourceDefinitionFactory, DeckDefinitionFactory, DeckFactory
    factories = [WorkcellFactory, MachineFactory, ResourceDefinitionFactory, DeckDefinitionFactory, DeckFactory]
    for factory in factories:
        factory._meta.sqlalchemy_session = db
        factory._meta.sqlalchemy_session_persistence = "flush"
    yield db
