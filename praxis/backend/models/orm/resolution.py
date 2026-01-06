# pylint: disable=too-few-public-methods,missing-class-docstring,invalid-name
"""State Resolution ORM Models for Protocol Execution Error Handling.

This module defines ORM models for logging state resolutions during protocol
execution. When an operation fails and state becomes uncertain, users can
provide resolutions indicating what actually happened. These resolutions are
logged for audit purposes.

Key Features:
- Resolution audit logging
- Links to schedule entries and protocol runs
- Stores uncertain states and their resolutions
- Tracks resolution actions (resume, abort, retry)
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from . import ProtocolRunOrm, ScheduleEntryOrm

from sqlalchemy import (
  UUID,
  DateTime,
  ForeignKey,
  String,
  Text,
  func,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from praxis.backend.models.orm.types import JsonVariant
from praxis.backend.utils.db import Base


class ResolutionActionEnum(Enum):
  """Actions taken after state resolution."""

  RESUME = "resume"  # Continue protocol execution
  ABORT = "abort"  # Stop protocol execution
  RETRY = "retry"  # Retry the failed operation


class ResolutionTypeEnum(Enum):
  """Types of state resolution."""

  CONFIRMED_SUCCESS = "confirmed_success"  # Effect actually happened
  CONFIRMED_FAILURE = "confirmed_failure"  # Effect did not happen
  PARTIAL = "partial"  # Effect partially happened
  ARBITRARY = "arbitrary"  # User specified custom values
  UNKNOWN = "unknown"  # User cannot determine


class StateResolutionLogOrm(Base):
  """SQLAlchemy ORM model for logging state resolutions.

  This model provides an audit trail of all state resolutions made during
  protocol execution, capturing what uncertainty existed and how it was
  resolved by the user or system.
  """

  __tablename__ = "state_resolution_log"

  # Link to schedule entry
  schedule_entry_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("schedule_entries.accession_id"),
    nullable=False,
    index=True,
    comment="Foreign key to the schedule entry this resolution belongs to.",
    kw_only=True,
  )

  protocol_run_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("protocol_runs.accession_id"),
    nullable=False,
    index=True,
    comment="Foreign key to the protocol run this resolution belongs to.",
    kw_only=True,
  )

  # Operation details
  operation_id: Mapped[str] = mapped_column(
    String(255),
    nullable=False,
    index=True,
    comment="Unique ID of the operation that failed.",
    kw_only=True,
  )

  operation_description: Mapped[str] = mapped_column(
    Text,
    nullable=False,
    comment="Human-readable description of the failed operation.",
    kw_only=True,
  )

  error_message: Mapped[str] = mapped_column(
    Text,
    nullable=False,
    comment="Error message from the failed operation.",
    kw_only=True,
  )

  error_type: Mapped[str | None] = mapped_column(
    String(255),
    nullable=True,
    comment="Type/class of the error (e.g., 'PressureFault').",
    default=None,
  )

  # State information
  uncertain_states_json: Mapped[dict] = mapped_column(
    JsonVariant,
    nullable=False,
    comment="JSON list of UncertainStateChange objects.",
    kw_only=True,
  )

  resolution_json: Mapped[dict] = mapped_column(
    JsonVariant,
    nullable=False,
    comment="JSON representation of the StateResolution.",
    kw_only=True,
  )

  # Resolution metadata
  resolution_type: Mapped[ResolutionTypeEnum] = mapped_column(
    SAEnum(ResolutionTypeEnum, name="resolution_type_enum"),
    nullable=False,
    index=True,
    comment="Type of resolution applied.",
    kw_only=True,
  )

  resolved_by: Mapped[str] = mapped_column(
    String(255),
    nullable=False,
    default="user",
    comment="Identifier of who resolved (user ID or 'system').",
  )

  resolved_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    nullable=False,
    server_default=func.now(),
    comment="Timestamp when resolution was provided.",
    init=False,
  )

  notes: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    comment="Optional notes from the user about the resolution.",
    default=None,
  )

  # Post-resolution action
  action_taken: Mapped[ResolutionActionEnum] = mapped_column(
    SAEnum(ResolutionActionEnum, name="resolution_action_enum"),
    nullable=False,
    index=True,
    comment="Action taken after resolution (resume, abort, retry).",
    kw_only=True,
  )

  # Relationships
  schedule_entry: Mapped["ScheduleEntryOrm"] = relationship(
    "ScheduleEntryOrm",
    uselist=False,
    init=False,
    foreign_keys=[schedule_entry_accession_id],
  )

  protocol_run: Mapped["ProtocolRunOrm"] = relationship(
    "ProtocolRunOrm",
    uselist=False,
    init=False,
    foreign_keys=[protocol_run_accession_id],
  )
