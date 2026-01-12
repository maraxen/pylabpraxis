# pylint: disable=too-few-public-methods,missing-class-docstring
"""Unified SQLModel definitions for Schedule and AssetReservation."""

import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Field, SQLModel

from praxis.backend.models.domain.sqlmodel_base import PraxisBase, json_field
from praxis.backend.models.enums import (
  AssetReservationStatusEnum,
  AssetType,
  ScheduleHistoryEventEnum,
  ScheduleHistoryEventTriggerEnum,
  ScheduleStatusEnum,
)
from praxis.backend.utils.db import JsonVariant

# =============================================================================
# Schedule Entry
# =============================================================================


class ScheduleEntryBase(PraxisBase):
  """Base schema for ScheduleEntry - shared fields for create/update/response."""

  status: ScheduleStatusEnum = Field(
    default=ScheduleStatusEnum.QUEUED,
    index=True,
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
  user_params_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="User parameters"
  )
  asset_requirements_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Asset requirements"
  )
  # Additional fields from ORM
  asset_analysis_completed_at: datetime | None = Field(default=None)
  assets_reserved_at: datetime | None = Field(default=None)
  celery_task_id: str | None = Field(default=None, index=True)
  celery_queue_name: str | None = Field(default=None, index=True)
  retry_count: int = Field(default=0)
  max_retries: int = Field(default=3)
  last_error_message: str | None = Field(default=None)
  initial_state_json: dict[str, Any] | None = Field(default=None, sa_type=JsonVariant)


class ScheduleEntry(ScheduleEntryBase, table=True):
  """ScheduleEntry ORM model - represents a scheduled protocol execution."""

  __tablename__ = "schedule_entries"

  metadata_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Additional metadata"
  )

  # Foreign keys
  protocol_run_accession_id: uuid.UUID | None = Field(
    default=None, foreign_key="protocol_runs.accession_id", index=True
  )
  # workcell_accession_id: uuid.UUID | None = Field(
  #   default=None, foreign_key="workcells.accession_id", index=True
  # ) # Not present in legacy ORM? Checked, seemingly not. Removing to match legacy for now.


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
  expires_at: datetime | None = Field(default=None)
  is_active: bool = Field(
    default=True, index=True, description="Whether the reservation is currently active"
  )
  status: AssetReservationStatusEnum = Field(default=AssetReservationStatusEnum.PENDING, index=True)
  asset_type: AssetType = Field(default=AssetType.ASSET, index=True)
  asset_name: str = Field(index=True)
  redis_lock_key: str = Field(index=True)
  redis_lock_value: str | None = Field(default=None)
  lock_timeout_seconds: int = Field(default=3600)
  required_capabilities_json: dict[str, Any] | None = Field(default=None, sa_type=JsonVariant)
  estimated_usage_duration_ms: int | None = Field(default=None)


class AssetReservation(AssetReservationBase, table=True):
  """AssetReservation ORM model - represents a reservation of an asset for a schedule entry."""

  __tablename__ = "asset_reservations"

  # Foreign keys
  # Soft FK for asset_accession_id (no foreign_key constraint)
  asset_accession_id: uuid.UUID = Field(index=True, description="Reference to Asset ID (Soft FK)")

  schedule_entry_accession_id: uuid.UUID = Field(
    foreign_key="schedule_entries.accession_id", index=True
  )
  protocol_run_accession_id: uuid.UUID = Field(foreign_key="protocol_runs.accession_id", index=True)


class AssetReservationCreate(AssetReservationBase):
  """Schema for creating an AssetReservation."""

  asset_accession_id: uuid.UUID
  schedule_entry_accession_id: uuid.UUID
  protocol_run_accession_id: uuid.UUID


class AssetReservationRead(AssetReservationBase):
  """Schema for reading an AssetReservation (API response)."""

  accession_id: uuid.UUID
  asset_accession_id: uuid.UUID
  schedule_entry_accession_id: uuid.UUID
  protocol_run_accession_id: uuid.UUID


class AssetReservationUpdate(SQLModel):
  """Schema for updating an AssetReservation (partial update)."""

  name: str | None = None
  released_at: datetime | None = None
  is_active: bool | None = None
  status: AssetReservationStatusEnum | None = None


# =============================================================================
# Schedule History
# =============================================================================


class ScheduleHistoryBase(PraxisBase):
  event_type: ScheduleHistoryEventEnum = Field(index=True)
  from_status: ScheduleStatusEnum | None = Field(default=None)
  to_status: ScheduleStatusEnum | None = Field(default=None)
  message: str | None = Field(default=None)
  error_details: str | None = Field(default=None)
  event_start: datetime | None = Field(default=None)
  event_end: datetime | None = Field(default=None)
  completed_duration_ms: int | None = Field(default=None)
  override_duration_ms: int | None = Field(default=None)
  asset_count: int | None = Field(default=None)
  triggered_by: ScheduleHistoryEventTriggerEnum = Field(
    default=ScheduleHistoryEventTriggerEnum.SYSTEM
  )


class ScheduleHistory(ScheduleHistoryBase, table=True):
  __tablename__ = "schedule_history"

  event_data_json: dict[str, Any] | None = Field(default=None, sa_type=JsonVariant)

  schedule_entry_accession_id: uuid.UUID = Field(
    foreign_key="schedule_entries.accession_id", index=True
  )


class ScheduleHistoryRead(ScheduleHistoryBase):
  accession_id: uuid.UUID
  event_data_json: dict[str, Any] | None = None


class ScheduleHistoryCreate(ScheduleHistoryBase):
  schedule_entry_accession_id: uuid.UUID


class ScheduleHistoryUpdate(SQLModel):
  message: str | None = None
  error_details: str | None = None
  event_end: datetime | None = None


# =============================================================================
# Scheduler Metrics View
# =============================================================================


class SchedulerMetricsView(SQLModel, table=True):
  """Read-only ORM class mapped to the scheduler_metrics_mv materialized view."""

  __tablename__ = "scheduler_metrics_mv"
  __table_args__ = {"extend_existing": True}

  # We redefine properties_json as None because Views might not have it,
  # or rely on PraxisBase default. But PraxisBase has name/etc.
  # The view has specific columns.

  metric_timestamp: datetime = Field(primary_key=True)
  protocols_scheduled: int
  protocols_completed: int
  protocols_failed: int
  protocols_cancelled: int
  avg_queue_wait_time_ms: float
  avg_execution_time_ms: float

  # Exclude base fields that don't exist in the view if necessary
  # But PraxisBase adds accession_id, created_at, updated_at, name.
  # The view doesn't have these!
  # So SchedulerMetricsView shouldn't inherit PraxisBase probably.
  # Or I should override them.
  # I'll make it inherit SQLModel directly.


class SchedulerMetricsResponse(SQLModel):
  metric_timestamp: datetime
  protocols_scheduled: int
  protocols_completed: int
  protocols_failed: int
  protocols_cancelled: int
  avg_queue_wait_time_ms: float
  avg_execution_time_ms: float


# =============================================================================
# Auxiliary Models
# =============================================================================


class CancelScheduleRequest(SQLModel):
  run_id: uuid.UUID
  reason: str | None = None


class ResourceReservationStatus(SQLModel):
  resource_id: uuid.UUID
  status: AssetReservationStatusEnum
  reserved_by_run_id: uuid.UUID | None = None


class ScheduleAnalysisResponse(SQLModel):
  estimated_start_time: datetime | None = None
  conflicts: list[dict[str, Any]] = []


class ScheduleListFilters(SQLModel):
  status: list[ScheduleStatusEnum] | None = None
  start_time_from: datetime | None = None
  start_time_to: datetime | None = None
  limit: int = 100
  offset: int = 0


class ScheduleListRequest(SQLModel):
  filters: ScheduleListFilters | None = None


class ScheduleListResponse(SQLModel):
  entries: list[ScheduleEntryRead]
  total: int


class SchedulePriorityUpdateRequest(SQLModel):
  priority: int


class ScheduleProtocolRequest(SQLModel):
  protocol_id: uuid.UUID
  params: dict[str, Any] | None = None
  priority: int = 0
  scheduled_time: datetime | None = None


class SchedulerSystemStatusResponse(SQLModel):
  status: str
  active_runs: int
  queued_runs: int
  available_resources: int


class ScheduleStatusResponse(SQLModel):
  status: ScheduleStatusEnum
  position: int | None = None
  estimated_start: datetime | None = None


class ReleaseReservationResponse(SQLModel):
  """Response model for releasing asset reservations."""
  asset_key: str
  released: bool
  message: str
  released_count: int
