"""add_dynamic_filter_columns_to_resource_definitions.

Revision ID: cd193888759e
Revises: 577d92edf9a5
Create Date: 2025-12-21 19:33:48.579424

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cd193888759e"
down_revision: str | Sequence[str] | None = "577d92edf9a5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add dynamic filtering columns to resource_definition_catalog."""
    # Add new columns for dynamic filtering
    op.add_column("resource_definition_catalog", sa.Column(
        "num_items", sa.Integer(), nullable=True,
        comment="Number of items (wells for plates, tips for tip racks)."
    ))
    op.add_column("resource_definition_catalog", sa.Column(
        "plate_type", sa.String(), nullable=True,
        comment="Plate skirt type: 'skirted', 'semi-skirted', 'non-skirted'."
    ))
    op.add_column("resource_definition_catalog", sa.Column(
        "well_volume_ul", sa.Float(), nullable=True,
        comment="Well volume in microliters for plates."
    ))
    op.add_column("resource_definition_catalog", sa.Column(
        "tip_volume_ul", sa.Float(), nullable=True,
        comment="Tip volume in microliters for tip racks."
    ))
    op.add_column("resource_definition_catalog", sa.Column(
        "vendor", sa.String(), nullable=True,
        comment="Vendor/manufacturer extracted from FQN (e.g., 'corning', 'opentrons')."
    ))

    # Create indexes for efficient filtering
    op.create_index(
        "ix_resource_definition_catalog_num_items",
        "resource_definition_catalog", ["num_items"]
    )
    op.create_index(
        "ix_resource_definition_catalog_plate_type",
        "resource_definition_catalog", ["plate_type"]
    )
    op.create_index(
        "ix_resource_definition_catalog_well_volume_ul",
        "resource_definition_catalog", ["well_volume_ul"]
    )
    op.create_index(
        "ix_resource_definition_catalog_tip_volume_ul",
        "resource_definition_catalog", ["tip_volume_ul"]
    )
    op.create_index(
        "ix_resource_definition_catalog_vendor",
        "resource_definition_catalog", ["vendor"]
    )


def downgrade() -> None:
    """Remove dynamic filtering columns from resource_definition_catalog."""
    # Drop indexes
    op.drop_index("ix_resource_definition_catalog_vendor", "resource_definition_catalog")
    op.drop_index("ix_resource_definition_catalog_tip_volume_ul", "resource_definition_catalog")
    op.drop_index("ix_resource_definition_catalog_well_volume_ul", "resource_definition_catalog")
    op.drop_index("ix_resource_definition_catalog_plate_type", "resource_definition_catalog")
    op.drop_index("ix_resource_definition_catalog_num_items", "resource_definition_catalog")

    # Drop columns
    op.drop_column("resource_definition_catalog", "vendor")
    op.drop_column("resource_definition_catalog", "tip_volume_ul")
    op.drop_column("resource_definition_catalog", "well_volume_ul")
    op.drop_column("resource_definition_catalog", "plate_type")
    op.drop_column("resource_definition_catalog", "num_items")
