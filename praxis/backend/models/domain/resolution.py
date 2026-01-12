"""Unified SQLModel definition for StateResolutionLog."""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func
from sqlmodel import Field, SQLModel

from praxis.backend.models.domain.sqlmodel_base import PraxisBase
from praxis.backend.models.enums.resolution import ResolutionActionEnum, ResolutionTypeEnum
from praxis.backend.utils.db import JsonVariant


class StateResolutionLogBase(PraxisBase):
  """Base schema for StateResolutionLog."""

  operation_id: str = Field(index=True, description="Unique ID of the operation that failed.")
  operation_description: str = Field(description="Human-readable description.")
  error_message: str = Field(description="Error message from the failed operation.")
  error_type: str | None = Field(default=None, description="Type/class of the error.")

  uncertain_states_json: dict[str, Any] = Field(
    default_factory=dict, sa_type=JsonVariant, description="Uncertain states"
  )
  resolution_json: dict[str, Any] = Field(
    default_factory=dict, sa_type=JsonVariant, description="Resolution details"
  )

  resolution_type: ResolutionTypeEnum = Field(index=True)
  resolved_by: str = Field(default="user")
  resolved_at: datetime = Field(
    default_factory=lambda: datetime.now(timezone.utc),
    sa_column_kwargs={"server_default": func.now()},
  )
  notes: str | None = Field(default=None)
  action_taken: ResolutionActionEnum = Field(index=True)


class StateResolutionLog(StateResolutionLogBase, table=True):
  """StateResolutionLog ORM model."""

  __tablename__ = "state_resolution_log"

  schedule_entry_accession_id: uuid.UUID = Field(
    foreign_key="schedule_entries.accession_id", index=True
  )
  protocol_run_accession_id: uuid.UUID = Field(foreign_key="protocol_runs.accession_id", index=True)


class StateResolutionLogCreate(StateResolutionLogBase):
  """Schema for creating a StateResolutionLog."""

  schedule_entry_accession_id: uuid.UUID
  protocol_run_accession_id: uuid.UUID


class StateResolutionLogRead(StateResolutionLogBase):
  """Schema for reading a StateResolutionLog."""

  accession_id: uuid.UUID
  schedule_entry_accession_id: uuid.UUID
  protocol_run_accession_id: uuid.UUID
