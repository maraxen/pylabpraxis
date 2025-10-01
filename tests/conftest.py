"""Pytest fixtures for the Praxis test suite."""
import asyncio
from collections.abc import AsyncGenerator, Generator
from os import getenv

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from main import app
from praxis.backend.utils.db import Base, get_async_db_session

# Use a separate database for testing
TEST_DATABASE_URL = getenv(
    "TEST_DATABASE_URL", "postgresql+asyncpg://praxis:praxis@localhost:5433/praxis_test_db"
)

# Create a new async engine for the test database
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

# Create a new async session maker for the test database
TestAsyncSessionLocal = async_sessionmaker(
    test_engine, expire_on_commit=False, autocommit=False, autoflush=False
)


async def _get_test_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a test database session.

    This is an async generator that yields a new SQLAlchemy `AsyncSession`
    from the `TestAsyncSessionLocal` session maker. It is used to override
    the `get_async_db_session` dependency in the main application during tests.

    Yields:
        An `AsyncSession` object for the test database.
    """
    async with TestAsyncSessionLocal() as session:
        yield session


# Override the get_async_db_session dependency with the test version
app.dependency_overrides[get_async_db_session] = _get_test_db_session


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database() -> AsyncGenerator[None, None]:
    """Set up the test database schema.

    This fixture runs once per session and is responsible for creating all
    database tables before the tests run, and dropping them after the tests
    are complete. This ensures a clean database state for each test run.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional database session for each test.

    This fixture creates a new database session and begins a transaction.
    After the test is complete, it rolls back the transaction to ensure
    that no changes are persisted between tests, maintaining test isolation.

    Yields:
        An `AsyncSession` object within a transaction.
    """
    async with TestAsyncSessionLocal() as session:
        await session.begin()
        try:
            yield session
        finally:
            await session.rollback()


@pytest.fixture
async def api_client() -> AsyncGenerator[AsyncClient, None]:
    """Provide a test client for the FastAPI application.

    This fixture creates an `AsyncClient` that can be used to make requests
    to the FastAPI application during tests.

    Yields:
        An `AsyncClient` instance.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def authenticated_api_client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an authenticated test client.

    This fixture overrides the `get_current_user` dependency to return a
    hardcoded test user. It allows for testing authenticated endpoints
    without needing to mock the entire authentication flow.

    Yields:
        An `AsyncClient` instance that is authenticated as a test user.
    """
    from praxis.backend.api.users import get_current_user, UserResponse
    from datetime import datetime
    import uuid

    def override_get_current_user() -> UserResponse:
        now = datetime.now()
        return UserResponse(
            accession_id=uuid.uuid4(),
            username="testuser",
            email="testuser@example.com",
            full_name="Test User",
            is_active=True,
            created_at=now,
            updated_at=now,
            properties_json={},
            name="testuser",
        )

    app.dependency_overrides[get_current_user] = override_get_current_user
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    del app.dependency_overrides[get_current_user]