# pylint: disable=too-few-public-methods,missing-class-docstring
"""Unified SQLModel definitions for Schedule and AssetReservation."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel

from praxis.backend.models.domain.sqlmodel_base import PraxisBase, json_field
from praxis.backend.models.enums import ScheduleStatusEnum

# =============================================================================
# Schedule Entry
# =============================================================================


class ScheduleEntryBase(PraxisBase):
  """Base schema for ScheduleEntry - shared fields for create/update/response."""

  status: ScheduleStatusEnum = Field(
    default=ScheduleStatusEnum.QUEUED,
    sa_column=Column(
      SAEnum(ScheduleStatusEnum, name="schedule_status_enum"), nullable=False, index=True
    ),
  )
  scheduled_at: datetime | None = Field(
    default=None, index=True, description="Scheduled start time"
  )
  execution_started_at: datetime | None = Field(
    default=None, index=True, description="Actual start time"
  )
  execution_completed_at: datetime | None = Field(
    default=None, index=True, description="Actual end time"
  )
  priority: int = Field(default=0, index=True, description="Priority for scheduling")
  estimated_duration_ms: int | None = Field(default=None, description="Estimated duration")
  required_asset_count: int | None = Field(default=None, description="Required asset count")
  user_params_json: dict[str, Any] | None = json_field(default=None, description="User parameters")
  asset_requirements_json: dict[str, Any] | None = json_field(
    default=None, description="Asset requirements"
  )


class ScheduleEntry(ScheduleEntryBase, table=True):
  """ScheduleEntry ORM model - represents a scheduled protocol execution."""

  __tablename__ = "schedule_entries"

  metadata_json: dict[str, Any] | None = json_field(default=None, description="Additional metadata")

  # Foreign keys
  protocol_run_accession_id: uuid.UUID | None = Field(
    default=None, foreign_key="protocol_runs.accession_id", index=True
  )
  workcell_accession_id: uuid.UUID | None = Field(
    default=None, foreign_key="workcells.accession_id", index=True
  )


class ScheduleEntryCreate(ScheduleEntryBase):
  """Schema for creating a ScheduleEntry."""

  protocol_run_accession_id: uuid.UUID


class ScheduleEntryRead(ScheduleEntryBase):
  """Schema for reading a ScheduleEntry (API response)."""

  accession_id: uuid.UUID


class ScheduleEntryUpdate(SQLModel):
  """Schema for updating a ScheduleEntry (partial update)."""

  name: str | None = None
  status: ScheduleStatusEnum | None = None
  scheduled_at: datetime | None = None
  execution_started_at: datetime | None = None
  execution_completed_at: datetime | None = None
  priority: int | None = None
  last_error_message: str | None = None


# =============================================================================
# Asset Reservation
# =============================================================================


class AssetReservationBase(PraxisBase):
  """Base schema for AssetReservation - shared fields for create/update/response."""

  reserved_at: datetime | None = Field(
    default=None, index=True, description="When the asset was reserved"
  )
  released_at: datetime | None = Field(
    default=None, index=True, description="When the asset was released"
  )
  is_active: bool = Field(
    default=True, index=True, description="Whether the reservation is currently active"
  )


class AssetReservation(AssetReservationBase, table=True):
  """AssetReservation ORM model - represents a reservation of an asset for a schedule entry."""

  __tablename__ = "asset_reservations"

  # Foreign keys
  asset_accession_id: uuid.UUID = Field(foreign_key="assets.accession_id", index=True)
  schedule_entry_accession_id: uuid.UUID = Field(
    foreign_key="schedule_entries.accession_id", index=True
  )


class AssetReservationCreate(AssetReservationBase):
  """Schema for creating an AssetReservation."""

  asset_accession_id: uuid.UUID
  schedule_entry_accession_id: uuid.UUID


class AssetReservationRead(AssetReservationBase):
  """Schema for reading an AssetReservation (API response)."""

  accession_id: uuid.UUID
  asset_accession_id: uuid.UUID
  schedule_entry_accession_id: uuid.UUID


class AssetReservationUpdate(SQLModel):
  """Schema for updating an AssetReservation (partial update)."""

  name: str | None = None
  released_at: datetime | None = None
  is_active: bool | None = None
