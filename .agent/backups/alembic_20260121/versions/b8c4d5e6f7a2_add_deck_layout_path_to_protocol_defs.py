"""add deck_layout_path to function_protocol_definitions.

Revision ID: b8c4d5e6f7a2
Revises: a7f3e8c9d2b1
Create Date: 2026-01-02
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b8c4d5e6f7a2"
down_revision: str | None = "a7f3e8c9d2b1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add deck_layout_path column to function_protocol_definitions.

    This column stores the path to a JSON file defining user-specified
    deck layout, allowing protocols to override auto-layout.
    """
    op.add_column(
        "function_protocol_definitions",
        sa.Column(
            "deck_layout_path",
            sa.String(),
            nullable=True,
            comment="Path to JSON file defining user-specified deck layout (overrides auto-layout).",
        ),
    )


def downgrade() -> None:
    """Remove deck_layout_path column from function_protocol_definitions."""
    op.drop_column("function_protocol_definitions", "deck_layout_path")
