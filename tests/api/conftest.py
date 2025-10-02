import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.api import discovery, outputs, protocols, resources, workcell
from praxis.backend.api.dependencies import get_db
from praxis.backend.utils.db import AsyncSessionLocal, async_engine, init_praxis_db_schema


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_test_database_session() -> None:
    """Create test tables once per session."""
    await init_praxis_db_schema()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provides a test database session, rolling back changes after each test."""
    async with async_engine.connect() as connection:
        async with connection.begin() as transaction:
            async_session = AsyncSessionLocal(bind=connection)
            yield async_session
            await transaction.rollback()


@pytest.fixture
def client(db_session: AsyncSession) -> Generator[TestClient, None, None]:
    """Provides a TestClient instance for a test-specific FastAPI app."""
    test_app = FastAPI()

    # Include routers from the application
    test_app.include_router(
        outputs.router,
        prefix="/api/v1/data-outputs",
        tags=["Data Outputs"],
    )
    test_app.include_router(protocols.router, prefix="/api/v1/protocols", tags=["Protocols"])
    test_app.include_router(workcell.router, prefix="/api/v1/workcell", tags=["Workcell"])
    test_app.include_router(resources.router, prefix="/api/v1/assets", tags=["Assets"])
    test_app.include_router(discovery.router, prefix="/api/v1/discovery", tags=["Discovery"])

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    with TestClient(test_app) as c:
        yield c
    del test_app.dependency_overrides[get_db]
