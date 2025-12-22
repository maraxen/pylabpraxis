"""Remove unique constraint from name in PLR definitions

Revision ID: 577d92edf9a5
Revises: 3a1fe0851e06
Create Date: 2025-12-21 12:48:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '577d92edf9a5'
down_revision: Union[str, Sequence[str], None] = '3a1fe0851e06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove unique constraint from name columns in PLR type definition tables.

    Multiple pylabrobot resources can have the same short name (e.g., "Plate"),
    so name should not be unique. The fqn (fully qualified name) is already unique.
    """
    # Drop unique index on resource_definition_catalog.name
    op.drop_index('ix_resource_definition_catalog_name', table_name='resource_definition_catalog')
    op.create_index('ix_resource_definition_catalog_name', 'resource_definition_catalog', ['name'], unique=False)

    # Drop unique index on machine_definition_catalog.name
    op.drop_index('ix_machine_definition_catalog_name', table_name='machine_definition_catalog')
    op.create_index('ix_machine_definition_catalog_name', 'machine_definition_catalog', ['name'], unique=False)

    # Drop unique index on deck_definition_catalog.name
    op.drop_index('ix_deck_definition_catalog_name', table_name='deck_definition_catalog')
    op.create_index('ix_deck_definition_catalog_name', 'deck_definition_catalog', ['name'], unique=False)


def downgrade() -> None:
    """Restore unique constraint to name columns (not recommended)."""
    # Recreate unique indexes
    op.drop_index('ix_resource_definition_catalog_name', table_name='resource_definition_catalog')
    op.create_index('ix_resource_definition_catalog_name', 'resource_definition_catalog', ['name'], unique=True)

    op.drop_index('ix_machine_definition_catalog_name', table_name='machine_definition_catalog')
    op.create_index('ix_machine_definition_catalog_name', 'machine_definition_catalog', ['name'], unique=True)

    op.drop_index('ix_deck_definition_catalog_name', table_name='deck_definition_catalog')
    op.create_index('ix_deck_definition_catalog_name', 'deck_definition_catalog', ['name'], unique=True)
