"""Portable SQLAlchemy column types for dialect compatibility.

This module provides type definitions that work across different database
backends (PostgreSQL, SQLite) while leveraging advanced features when available.

Usage:
    from praxis.backend.models.orm.types import JsonVariant

    class MyModel(Base):
        data: Mapped[dict] = mapped_column(JsonVariant, nullable=True)

The JsonVariant type automatically uses:
- JSONB on PostgreSQL (for efficient indexing and querying)
- JSON on SQLite and other databases

NOTE: JsonVariant is actually defined in praxis.backend.utils.db to avoid
circular imports (db.py defines Base which is needed by ORM models).
We re-export it here for convenience.
"""

from praxis.backend.utils.db import JsonVariant

__all__ = ["JsonVariant"]
