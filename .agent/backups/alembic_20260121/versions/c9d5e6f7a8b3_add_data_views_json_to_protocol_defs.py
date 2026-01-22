"""add data_views_json to function_protocol_definitions.

Revision ID: c9d5e6f7a8b3
Revises: b8c4d5e6f7a2
Create Date: 2026-01-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c9d5e6f7a8b3"
down_revision: str | None = "b8c4d5e6f7a2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add data_views_json column to function_protocol_definitions.

    This column stores data view definitions that specify input data
    requirements for protocols, linking to PLR state or function outputs.
    """
    op.add_column(
        "function_protocol_definitions",
        sa.Column(
            "data_views_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Data view definitions specifying input data requirements (PLR state, function outputs).",
        ),
    )


def downgrade() -> None:
    """Remove data_views_json column from function_protocol_definitions."""
    op.drop_column("function_protocol_definitions", "data_views_json")
