"""Script to create database tables from ORM models for testing.

This creates all tables defined in the ORM models directly, bypassing Alembic migrations.
"""

import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

# Import all ORM models to ensure they're registered
import praxis.backend.models  # noqa: F401 - models must be imported to register with Base
from praxis.backend.utils.db import Base


async def create_tables():
  """Create all database tables."""
  database_url = "sqlite+aiosqlite:///praxis.db"
  engine = create_async_engine(database_url, echo=True)

  async with engine.begin() as conn:
    # Drop all tables (for clean slate)
    await conn.run_sync(Base.metadata.drop_all)
    # Create all tables
    await conn.run_sync(Base.metadata.create_all)

  await engine.dispose()


if __name__ == "__main__":
  asyncio.run(create_tables())
