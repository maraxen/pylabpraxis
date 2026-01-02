from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from main import app  # Import your main FastAPI application
from praxis.backend.api.dependencies import get_db
from tests.factories import (
    DeckDefinitionFactory,
    DeckFactory,
    MachineFactory,
    ResourceDefinitionFactory,
    WorkcellFactory,
)


@pytest_asyncio.fixture(scope="function")
async def client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """Creates the FastAPI test client.

    Crucially, it overrides the app's `get_db` dependency
    to use the *exact same session* as the test function and
    binds that session to all factory-boy factories.
    """

    # This is the magic: tell the app to use our test session
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Set up factories to use this session
    WorkcellFactory._meta.sqlalchemy_session = db_session
    MachineFactory._meta.sqlalchemy_session = db_session
    DeckDefinitionFactory._meta.sqlalchemy_session = db_session
    ResourceDefinitionFactory._meta.sqlalchemy_session = db_session
    DeckFactory._meta.sqlalchemy_session = db_session
    # ... set for all other factories ...

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Clean up the override
    del app.dependency_overrides[get_db]
