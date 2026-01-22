"""add required_plr_category to protocol_asset_requirements.

Revision ID: h5c6d7e8f9a0
Revises: g4b5c6d7e8f9
Create Date: 2026-01-10
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "h5c6d7e8f9a0"
down_revision: str | None = "g4b5c6d7e8f9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add required_plr_category column to protocol_asset_requirements.

    This column stores the PLR category (Plate, TipRack, Carrier, LiquidHandler, etc.)
    that the asset requirement expects. Computed by the backend during protocol analysis.
    This enables the frontend to filter assets by explicit category rather than
    inferring from FQN strings.
    """
    op.add_column(
        "protocol_asset_requirements",
        sa.Column(
            "required_plr_category",
            sa.String(),
            nullable=True,
            comment="PLR category required (Plate, TipRack, Carrier, LiquidHandler, etc). "
            "Computed by backend during protocol analysis.",
        ),
    )
    op.create_index(
        "ix_protocol_asset_requirements_required_plr_category",
        "protocol_asset_requirements",
        ["required_plr_category"],
    )


def downgrade() -> None:
    """Remove required_plr_category column from protocol_asset_requirements."""
    op.drop_index(
        "ix_protocol_asset_requirements_required_plr_category",
        table_name="protocol_asset_requirements",
    )
    op.drop_column("protocol_asset_requirements", "required_plr_category")
