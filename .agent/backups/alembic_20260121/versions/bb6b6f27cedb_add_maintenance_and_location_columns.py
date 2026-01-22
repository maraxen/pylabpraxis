"""add_maintenance_and_location_columns

Revision ID: bb6b6f27cedb
Revises: d1e2f3a4b5c6
Create Date: 2026-01-02 10:54:27.953651

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb6b6f27cedb'
down_revision: Union[str, Sequence[str], None] = 'd1e2f3a4b5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    """Upgrade schema."""
    # Add columns to machines table
    op.add_column('machines', sa.Column('location_label', sa.String(), nullable=True))
    op.add_column('machines', sa.Column('maintenance_enabled', sa.Boolean(), server_default='1', nullable=False))
    op.add_column('machines', sa.Column('maintenance_schedule_json', sa.JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=True))
    op.add_column('machines', sa.Column('last_maintenance_json', sa.JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=True))
    
    # Add column to resources table
    op.add_column('resources', sa.Column('location_label', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove columns from resources table
    op.drop_column('resources', 'location_label')
    
    # Remove columns from machines table
    op.drop_column('machines', 'last_maintenance_json')
    op.drop_column('machines', 'maintenance_schedule_json')
    op.drop_column('machines', 'maintenance_enabled')
    op.drop_column('machines', 'location_label')
