import os
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from praxis.backend.utils.db import Base

from alembic.config import Config
from alembic import command

# Use the PostgreSQL database from the docker-compose.test.yml file
ASYNC_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5433/test_db"

@pytest_asyncio.fixture(scope="session")
async def apply_migrations():
    """Apply Alembic migrations once per test session."""
    engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        # Explicitly drop materialized view before creating all tables
        await conn.execute(text("DROP MATERIALIZED VIEW IF EXISTS scheduler_metrics_mv CASCADE"))

        # Temporarily remove the event listener for CreateMaterializedView
        from sqlalchemy import event
        from praxis.backend.utils.db import CreateMaterializedView, DropMaterializedView
        from praxis.backend.models.orm.schedule import metrics_query

        from praxis.backend.utils.db import SCHEDULER_METRICS_MV_CREATOR
        event.remove(Base.metadata, "after_create", SCHEDULER_METRICS_MV_CREATOR)

        await conn.run_sync(Base.metadata.create_all)

        # Re-add the event listener after creating all tables
        event.listen(Base.metadata, "after_create", SCHEDULER_METRICS_MV_CREATOR)

    print("Tables created using Base.metadata.create_all.")
@pytest_asyncio.fixture(scope="function")
async def db(apply_migrations) -> AsyncSession:
    """Create a new database session for each test."""
    engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)

    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with SessionLocal() as session:
        yield session

    # Drop all tables after the test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)