"""add properties_json to resource_definition

Revision ID: a7f3e8c9d2b1
Revises: cd193888759e
Create Date: 2025-12-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "a7f3e8c9d2b1"
down_revision: Union[str, None] = "cd193888759e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


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
