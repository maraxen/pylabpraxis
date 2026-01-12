"""Make Resource.resource_definition_accession_id nullable.

Revision ID: 3a1fe0851e06
Revises:
Create Date: 2025-11-10 18:42:40.749914

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3a1fe0851e06"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
  """Make resource_definition_accession_id nullable to work around MappedAsDataclass FK issue."""
  op.alter_column(
    "resources",
    "resource_definition_accession_id",
    nullable=True,
    existing_type=sa.UUID(),
  )


def downgrade() -> None:
  """Revert resource_definition_accession_id to NOT NULL."""
  op.alter_column(
    "resources",
    "resource_definition_accession_id",
    nullable=False,
    existing_type=sa.UUID(),
  )
