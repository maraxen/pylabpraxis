"""add is_reusable to resource_definitions.

Revision ID: i6d7e8f9g0h1
Revises: 3a1fe0851e06
Create Date: 2026-01-16
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "i6d7e8f9g0h1"
down_revision: str | None = "3a1fe0851e06"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add is_reusable column to resource_definitions.

    This column indicates whether a resource type can be reused across multiple
    protocol runs (e.g., plates are reusable, tips are not). Default is True.
    This was previously tracked in the browser-mode schema but missing from the
    backend source-of-truth.
    """
    op.add_column(
        "resource_definitions",
        sa.Column(
            "is_reusable",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
            comment="Whether the resource can be reused (e.g., plates are reusable, tips are not)",
        ),
    )


def downgrade() -> None:
    """Remove is_reusable column from resource_definitions."""
    op.drop_column("resource_definitions", "is_reusable")
