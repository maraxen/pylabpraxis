"""add dimensions and metadata to resource_definition_catalog.

Revision ID: d1e2f3a4b5c6
Revises: c9d5e6f7a8b3
Create Date: 2026-01-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d1e2f3a4b5c6"
down_revision: str | None = "c9d5e6f7a8b3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add dimensions and metadata columns to resource_definition_catalog."""
    op.add_column(
        "resource_definition_catalog",
        sa.Column("resource_type", sa.String(), nullable=True, comment="Human-readable type of the resource.")
    )
    op.add_column(
        "resource_definition_catalog",
        sa.Column("is_consumable", sa.Boolean(), nullable=False, server_default="false")
    )
    op.add_column(
        "resource_definition_catalog",
        sa.Column("nominal_volume_ul", sa.Float(), nullable=True, comment="Nominal volume in microliters, if applicable.")
    )
    op.add_column(
        "resource_definition_catalog",
        sa.Column("material", sa.String(), nullable=True, comment="Material of the resource, e.g., 'polypropylene', 'glass'.")
    )
    op.add_column(
        "resource_definition_catalog",
        sa.Column("manufacturer", sa.String(), nullable=True, comment="Manufacturer of the resource, if applicable.")
    )
    op.add_column(
        "resource_definition_catalog",
        sa.Column(
            "plr_definition_details_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Additional PyLabRobot specific definition details as JSONB."
        )
    )
    op.add_column(
        "resource_definition_catalog",
        sa.Column("ordering", sa.String(), nullable=True, comment="Ordering information for the resource, if applicable.")
    )
    op.add_column(
        "resource_definition_catalog",
        sa.Column("size_x_mm", sa.Float(), nullable=True, comment="Size in X dimension (mm).")
    )
    op.add_column(
        "resource_definition_catalog",
        sa.Column("size_y_mm", sa.Float(), nullable=True, comment="Size in Y dimension (mm).")
    )
    op.add_column(
        "resource_definition_catalog",
        sa.Column("size_z_mm", sa.Float(), nullable=True, comment="Size in Z dimension (mm).")
    )
    op.add_column(
        "resource_definition_catalog",
        sa.Column("model", sa.String(), nullable=True, comment="Model of the resource, if applicable.")
    )
    op.add_column(
        "resource_definition_catalog",
        sa.Column(
            "rotation_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Represents PLR Resource.rotation as JSON."
        )
    )


def downgrade() -> None:
    """Remove dimensions and metadata columns from resource_definition_catalog."""
    op.drop_column("resource_definition_catalog", "rotation_json")
    op.drop_column("resource_definition_catalog", "model")
    op.drop_column("resource_definition_catalog", "size_z_mm")
    op.drop_column("resource_definition_catalog", "size_y_mm")
    op.drop_column("resource_definition_catalog", "size_x_mm")
    op.drop_column("resource_definition_catalog", "ordering")
    op.drop_column("resource_definition_catalog", "plr_definition_details_json")
    op.drop_column("resource_definition_catalog", "manufacturer")
    op.drop_column("resource_definition_catalog", "material")
    op.drop_column("resource_definition_catalog", "nominal_volume_ul")
    op.drop_column("resource_definition_catalog", "is_consumable")
    op.drop_column("resource_definition_catalog", "resource_type")
