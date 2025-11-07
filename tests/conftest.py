import asyncio
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

# Import the 'schedule' module to ensure its event listeners are registered.
import praxis.backend.models.orm.schedule
from praxis.backend.utils.db import Base

import asyncio
# Use the PostgreSQL database from the docker-compose.test.yml file
ASYNC_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5433/test_db"


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    """Set up the database schema for each test function."""
    from tests.conftest import ASYNC_DATABASE_URL
    engine = create_async_engine(ASYNC_DATABASE_URL)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    except Exception:
        pass
    yield
    await engine.dispose()




