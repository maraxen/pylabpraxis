"""add bytecode cache columns to function_protocol_definitions.

Revision ID: g4b5c6d7e8f9
Revises: f3a4b5c6d7e8
Create Date: 2026-01-05
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "g4b5c6d7e8f9"
down_revision: str | None = "f3a4b5c6d7e8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add cloudpickle bytecode cache columns to function_protocol_definitions.

    These columns enable caching of serialized protocol functions:
    - cached_bytecode: Cloudpickle serialized function
    - bytecode_python_version: Python version for compatibility checking
    - bytecode_cache_version: Format version for invalidation
    - bytecode_cached_at: When the cache was created
    """
    op.add_column(
        "function_protocol_definitions",
        sa.Column(
            "cached_bytecode",
            sa.LargeBinary(),
            nullable=True,
            comment="Cloudpickle serialized protocol function for caching/distributed execution.",
        ),
    )
    op.add_column(
        "function_protocol_definitions",
        sa.Column(
            "bytecode_python_version",
            sa.String(16),
            nullable=True,
            comment="Python version when bytecode was cached (e.g., '3.13.5').",
        ),
    )
    op.add_column(
        "function_protocol_definitions",
        sa.Column(
            "bytecode_cache_version",
            sa.String(16),
            nullable=True,
            comment="Cache format version for invalidation.",
        ),
    )
    op.add_column(
        "function_protocol_definitions",
        sa.Column(
            "bytecode_cached_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Timestamp when bytecode was cached.",
        ),
    )


def downgrade() -> None:
    """Remove bytecode cache columns from function_protocol_definitions."""
    op.drop_column("function_protocol_definitions", "bytecode_cached_at")
    op.drop_column("function_protocol_definitions", "bytecode_cache_version")
    op.drop_column("function_protocol_definitions", "bytecode_python_version")
    op.drop_column("function_protocol_definitions", "cached_bytecode")
