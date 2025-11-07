# In: tests/api/conftest.py
import pytest_asyncio
from collections.abc import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from main import app  # Import your main FastAPI application
from praxis.backend.api.dependencies import get_db


from sqlalchemy.ext.asyncio import create_async_engine


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[tuple[AsyncClient, sessionmaker[AsyncSession]], None]:
    """
    Fixture to get an AsyncClient for the FastAPI app and a sessionmaker.
    """
    from tests.conftest import ASYNC_DATABASE_URL
    engine = create_async_engine(ASYNC_DATABASE_URL)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db_for_client() -> AsyncGenerator[AsyncSession, None]:
        async with Session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db_for_client

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c, Session

    await engine.dispose()
