# In: tests/api/conftest.py
import pytest_asyncio
from collections.abc import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from main import app  # Import your main FastAPI application
from praxis.backend.api.dependencies import get_db
from tests.services.conftest import engine  # Import the TEST engine from your service tests

# This is the key: an override for the 'get_db' dependency
async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency override for tests.

    This fixture yields a session wrapped in a transaction, which is
    rolled back after the test, ensuring test isolation.

    This pattern is identical to your service-level 'db' fixture.
    """
    async with engine.connect() as connection:
        # Begin a transaction that will be rolled back
        async with connection.begin() as transaction:
            # Create a session bound to this specific connection/transaction
            TestSession = sessionmaker(
                bind=connection, class_=AsyncSession, expire_on_commit=False
            )
            session = TestSession()

            try:
                yield session
            finally:
                # Close the session and roll back the transaction
                await session.close()
                await transaction.rollback()

# --- Apply the override to the app ---
# This is the most important step!
app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture to get an AsyncClient for the FastAPI app with
    the overridden db dependency.
    """
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
