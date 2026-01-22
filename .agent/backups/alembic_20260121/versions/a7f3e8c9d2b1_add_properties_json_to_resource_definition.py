"""add properties_json to resource_definition.

Revision ID: a7f3e8c9d2b1
Revises: cd193888759e
Create Date: 2025-12-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a7f3e8c9d2b1"
down_revision: str | None = "cd193888759e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add properties_json column to resource_definition_catalog."""
    op.add_column(
        "resource_definition_catalog",
        sa.Column(
            "properties_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="All extracted PLR properties as structured JSON for faceted filtering.",
        ),
    )


def downgrade() -> None:
    """Remove properties_json column from resource_definition_catalog."""
    op.drop_column("resource_definition_catalog", "properties_json")
