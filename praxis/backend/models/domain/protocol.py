# pylint: disable=too-few-public-methods,missing-class-docstring
"""Unified SQLModel definitions for Protocol-related entities.

Note: This is a simplified initial implementation focusing on ProtocolRun.
Additional models (FunctionProtocolDefinition, FunctionCallLog, etc.) can be added as needed.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel

from praxis.backend.models.domain.sqlmodel_base import PraxisBase, json_field
from praxis.backend.models.enums import ProtocolRunStatusEnum

# =============================================================================
# Protocol Run
# =============================================================================


class ProtocolRunBase(PraxisBase):
  """Base schema for ProtocolRun - shared fields for create/update/response."""

  function_name: str | None = Field(default=None, description="Name of the protocol function")
  function_file: str | None = Field(
    default=None, description="File containing the protocol function"
  )
  status: ProtocolRunStatusEnum = Field(
    default=ProtocolRunStatusEnum.QUEUED,
    sa_column=Column(
      SAEnum(ProtocolRunStatusEnum, name="protocol_run_status_enum"), nullable=False, index=True
    ),
  )
  started_at: datetime | None = Field(
    default=None, index=True, description="When the protocol run started"
  )
  completed_at: datetime | None = Field(
    default=None, index=True, description="When the protocol run completed"
  )
  error_message: str | None = Field(default=None, description="Error message if the run failed")
  data_directory_path: str | None = Field(default=None, description="Path to data directory")


class ProtocolRun(ProtocolRunBase, table=True):
  """ProtocolRun ORM model - represents a protocol execution."""

  __tablename__ = "protocol_runs"

  function_args_json: dict[str, Any] | None = json_field(
    default=None, description="Function arguments as JSON"
  )
  function_kwargs_json: dict[str, Any] | None = json_field(
    default=None, description="Function keyword arguments as JSON"
  )
  result_json: dict[str, Any] | None = json_field(
    default=None, description="Protocol run result as JSON"
  )
  plr_deck_layout_snapshot: dict[str, Any] | None = json_field(
    default=None, description="Snapshot of deck layout"
  )

  # Foreign keys
  schedule_entry_accession_id: uuid.UUID | None = Field(
    default=None, foreign_key="schedule_entries.accession_id", index=True
  )
  function_protocol_definition_accession_id: uuid.UUID | None = Field(
    default=None, foreign_key="function_protocol_definitions.accession_id", index=True
  )


class ProtocolRunCreate(ProtocolRunBase):
  """Schema for creating a ProtocolRun."""

  name: str | None = None
  top_level_protocol_definition_accession_id: uuid.UUID
  run_accession_id: uuid.UUID | None = None


class ProtocolRunRead(ProtocolRunBase):
  """Schema for reading a ProtocolRun (API response)."""

  accession_id: uuid.UUID
  function_args_json: dict[str, Any] | None = None
  function_kwargs_json: dict[str, Any] | None = None
  result_json: dict[str, Any] | None = None
  output_data_json: dict[str, Any] | None = None
  data_directory_path: str | None = None


class ProtocolRunUpdate(SQLModel):
  """Schema for updating a ProtocolRun (partial update)."""

  name: str | None = None
  status: ProtocolRunStatusEnum | None = None
  started_at: datetime | None = None
  completed_at: datetime | None = None
  error_message: str | None = None
  result_json: dict[str, Any] | None = None
  output_data_json: dict[str, Any] | None = None
  data_directory_path: str | None = None
