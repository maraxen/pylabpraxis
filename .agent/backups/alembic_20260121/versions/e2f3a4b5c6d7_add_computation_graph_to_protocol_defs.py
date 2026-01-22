"""add computation_graph_json, source_hash, graph_cached_at to function_protocol_definitions.

Revision ID: e2f3a4b5c6d7
Revises: bb6b6f27cedb
Create Date: 2026-01-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e2f3a4b5c6d7"
down_revision: str | None = "bb6b6f27cedb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add computation graph caching columns to function_protocol_definitions.

    - computation_graph_json: Stores the extracted ProtocolComputationGraph
    - source_hash: Hash of the source code for cache invalidation
    - graph_cached_at: Timestamp when the graph was last cached
    """
    op.add_column(
        "function_protocol_definitions",
        sa.Column(
            "computation_graph_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Computation graph extracted from protocol (ProtocolComputationGraph).",
        ),
    )
    op.add_column(
        "function_protocol_definitions",
        sa.Column(
            "source_hash",
            sa.String(),
            nullable=True,
            comment="Hash of the protocol source code for cache invalidation.",
        ),
    )
    op.add_column(
        "function_protocol_definitions",
        sa.Column(
            "graph_cached_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Timestamp when the computation graph was last cached.",
        ),
    )


def downgrade() -> None:
    """Remove computation graph caching columns from function_protocol_definitions."""
    op.drop_column("function_protocol_definitions", "graph_cached_at")
    op.drop_column("function_protocol_definitions", "source_hash")
    op.drop_column("function_protocol_definitions", "computation_graph_json")
