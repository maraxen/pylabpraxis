# In: tests/api/conftest.py
import pytest_asyncio
from collections.abc import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from main import app  # Import your main FastAPI application
from praxis.backend.api.dependencies import get_db
from tests.conftest import engine  # Import the TEST engine from your service tests


@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture to get an AsyncClient for the FastAPI app with
    the overridden db dependency.
    """
    async def override_get_db_for_client() -> AsyncGenerator[AsyncSession, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db_for_client

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    # Clean up the override after the test
    del app.dependency_overrides[get_db]
