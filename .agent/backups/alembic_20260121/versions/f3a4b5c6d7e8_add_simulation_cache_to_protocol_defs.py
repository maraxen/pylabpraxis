"""add simulation cache columns to function_protocol_definitions.

Revision ID: f3a4b5c6d7e8
Revises: e2f3a4b5c6d7
Create Date: 2026-01-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f3a4b5c6d7e8"
down_revision: str | None = "e2f3a4b5c6d7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add simulation cache columns to function_protocol_definitions.

    These columns cache the results of protocol state simulation:
    - simulation_result_json: Full ProtocolSimulationResult
    - inferred_requirements_json: Extracted state requirements
    - failure_modes_json: Known failure modes
    - simulation_version: Version string for cache invalidation
    - simulation_cached_at: Timestamp when simulation was last run
    """
    op.add_column(
        "function_protocol_definitions",
        sa.Column(
            "simulation_result_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Cached ProtocolSimulationResult from state simulation.",
        ),
    )
    op.add_column(
        "function_protocol_definitions",
        sa.Column(
            "inferred_requirements_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Inferred state requirements (tips, liquid, deck placement).",
        ),
    )
    op.add_column(
        "function_protocol_definitions",
        sa.Column(
            "failure_modes_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Known failure modes from simulation.",
        ),
    )
    op.add_column(
        "function_protocol_definitions",
        sa.Column(
            "simulation_version",
            sa.String(32),
            nullable=True,
            comment="Simulator version for cache invalidation.",
        ),
    )
    op.add_column(
        "function_protocol_definitions",
        sa.Column(
            "simulation_cached_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Timestamp when simulation was last run.",
        ),
    )


def downgrade() -> None:
    """Remove simulation cache columns from function_protocol_definitions."""
    op.drop_column("function_protocol_definitions", "simulation_cached_at")
    op.drop_column("function_protocol_definitions", "simulation_version")
    op.drop_column("function_protocol_definitions", "failure_modes_json")
    op.drop_column("function_protocol_definitions", "inferred_requirements_json")
    op.drop_column("function_protocol_definitions", "simulation_result_json")
