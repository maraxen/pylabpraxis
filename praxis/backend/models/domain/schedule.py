import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Optional

from pydantic import computed_field
from sqlalchemy import UUID, Column
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlmodel import Field, Relationship, SQLModel

from praxis.backend.models.domain.sqlmodel_base import PraxisBase
from praxis.backend.models.enums import (
  AssetReservationStatusEnum,
  AssetType,
  ScheduleHistoryEventEnum,
  ScheduleHistoryEventTriggerEnum,
  ScheduleStatusEnum,
)
from praxis.backend.utils.db import JsonVariant

if TYPE_CHECKING:
  from praxis.backend.models.domain.machine import Machine
  from praxis.backend.models.domain.protocol import ProtocolRun
  from praxis.backend.models.domain.resource import Resource

# =============================================================================
# Schedule Entry
# =============================================================================


class ScheduleEntryBase(PraxisBase):
  """Base schema for ScheduleEntry - shared fields for create/update/response."""

  status: ScheduleStatusEnum = Field(
    default=ScheduleStatusEnum.QUEUED,
    sa_column=Column(SAEnum(ScheduleStatusEnum), default=ScheduleStatusEnum.QUEUED),
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
  priority: int = Field(default=1, index=True, description="Priority for scheduling")
  estimated_duration_ms: int | None = Field(default=None, description="Estimated duration")
  required_asset_count: int = Field(default=0, description="Required asset count")
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

  # Relationships
  protocol_run: Optional["ProtocolRun"] = Relationship()
  asset_reservations: list["AssetReservation"] = Relationship(
    sa_relationship=relationship(
      "AssetReservation",
      back_populates="schedule_entry",
      cascade="all, delete-orphan",
    )
  )
  history: list["ScheduleHistory"] = Relationship(
    sa_relationship=relationship(
      "ScheduleHistory",
      back_populates="schedule_entry",
      cascade="all, delete-orphan",
    )
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
    default_factory=lambda: datetime.now(timezone.utc),
    sa_column_kwargs={"server_default": func.now()},
    index=True,
    description="When the asset was reserved",
  )
  released_at: datetime | None = Field(
    default=None, index=True, description="When the asset was released"
  )
  expires_at: datetime | None = Field(default=None)
  is_active: bool = Field(
    default=True, index=True, description="Whether the reservation is currently active"
  )
  status: AssetReservationStatusEnum = Field(
    default=AssetReservationStatusEnum.PENDING,
    description="Status of the reservation",
  )
  asset_type: AssetType = Field(
    default=AssetType.ASSET,
    description="Type of the reserved asset",
  )
  asset_name: str = Field(index=True)
  redis_lock_key: str = Field(index=True)
  redis_lock_value: str | None = Field(default=None)
  lock_timeout_seconds: int = Field(default=3600)
  required_capabilities_json: dict[str, Any] | None = Field(default=None, sa_type=JsonVariant)
  estimated_usage_duration_ms: int | None = Field(default=None)


class AssetReservation(AssetReservationBase, table=True):
  """AssetReservation ORM model - represents a reservation of an asset for a schedule entry."""

  __tablename__ = "asset_reservations"

  status: AssetReservationStatusEnum = Field(
    default=AssetReservationStatusEnum.PENDING,
    sa_column=Column(SAEnum(AssetReservationStatusEnum), default=AssetReservationStatusEnum.PENDING, nullable=False),
  )
  asset_type: AssetType = Field(
    default=AssetType.ASSET,
    sa_column=Column(SAEnum(AssetType), default=AssetType.ASSET, nullable=False),
  )

  # Foreign keys
  # Soft FK for asset_accession_id (no foreign_key constraint)
  asset_accession_id: uuid.UUID | None = Field(
    default=None,
    sa_column=Column(UUID, nullable=True),
    description="Reference to Asset ID (Soft FK)",
  )

  schedule_entry_accession_id: uuid.UUID = Field(
    foreign_key="schedule_entries.accession_id", index=True
  )
  protocol_run_accession_id: uuid.UUID = Field(foreign_key="protocol_runs.accession_id", index=True)

  # Relationships
  schedule_entry: Optional["ScheduleEntry"] = Relationship(back_populates="asset_reservations")
  protocol_run: Optional["ProtocolRun"] = Relationship(back_populates="asset_reservations")
  # Explicit relationships to concrete assets
  machine: Optional["Machine"] = Relationship(
    sa_relationship=relationship(
      "Machine",
      back_populates="asset_reservations",
      primaryjoin="foreign(AssetReservation.asset_accession_id) == Machine.accession_id",
      foreign_keys="[AssetReservation.asset_accession_id]",
      overlaps="resource",
    )
  )
  resource: Optional["Resource"] = Relationship(
    sa_relationship=relationship(
      "Resource",
      back_populates="asset_reservations",
      primaryjoin="foreign(AssetReservation.asset_accession_id) == Resource.accession_id",
      foreign_keys="[AssetReservation.asset_accession_id]",
      overlaps="machine",
    )
  )

  @property
  def asset(self) -> object | None:
    """Return the concrete asset (machine or resource) for convenience."""
    return self.machine or self.resource

  @asset.setter
  def asset(self, value: object | None) -> None:
    """Set the concrete asset, clearing the other relationship.

    Uses simple runtime type checks (by class name) to avoid import cycles.
    """
    if value is None:
      # Clear relationships and persisted reference for soft-FK
      self.machine = None
      self.resource = None
      self.asset_accession_id = None
      self.asset_type = AssetType.ASSET
      return

    cls_name = value.__class__.__name__
    if cls_name == "Machine":
      # Write FK/type directly to avoid ambiguity, then set relationship
      self.asset_accession_id = value.accession_id
      self.asset_type = AssetType.MACHINE
      self.machine = value
    else:
      # Write FK/type directly to avoid ambiguity, then set relationship
      self.asset_accession_id = value.accession_id
      self.asset_type = AssetType.RESOURCE
      self.resource = value


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
  event_type: ScheduleHistoryEventEnum = Field(description="Type of the schedule history event")
  from_status: ScheduleStatusEnum | None = Field(default=None, description="Status before the event")
  to_status: ScheduleStatusEnum | None = Field(default=None, description="Status after the event")
  message: str | None = Field(default=None)
  error_details: str | None = Field(default=None)
  event_start: datetime | None = Field(
    default_factory=lambda: datetime.now(timezone.utc),
  )
  event_end: datetime | None = Field(default=None)

  @computed_field
  @property
  def completed_duration_ms(self) -> int | None:
    """Calculated duration between start and end in ms."""
    if self.event_start and self.event_end:
      delta = self.event_end - self.event_start
      return int(delta.total_seconds() * 1000)
    return None

  override_duration_ms: int | None = Field(default=None)
  asset_count: int | None = Field(default=None)
  triggered_by: ScheduleHistoryEventTriggerEnum = Field(
    default=ScheduleHistoryEventTriggerEnum.SYSTEM,
    description="What triggered the event",
  )


class ScheduleHistory(ScheduleHistoryBase, table=True):
  __tablename__ = "schedule_history"

  event_type: ScheduleHistoryEventEnum = Field(
    default=ScheduleHistoryEventEnum.STATUS_CHANGED,
    sa_column=Column(SAEnum(ScheduleHistoryEventEnum), default=ScheduleHistoryEventEnum.STATUS_CHANGED, nullable=False)
  )
  from_status: ScheduleStatusEnum | None = Field(
    default=None,
    sa_column=Column(SAEnum(ScheduleStatusEnum), nullable=True)
  )
  to_status: ScheduleStatusEnum | None = Field(
    default=None,
    sa_column=Column(SAEnum(ScheduleStatusEnum), nullable=True)
  )
  triggered_by: ScheduleHistoryEventTriggerEnum = Field(
    default=ScheduleHistoryEventTriggerEnum.SYSTEM,
    sa_column=Column(SAEnum(ScheduleHistoryEventTriggerEnum), default=ScheduleHistoryEventTriggerEnum.SYSTEM)
  )

  event_data_json: dict[str, Any] | None = Field(default=None, sa_type=JsonVariant)

  schedule_entry_accession_id: uuid.UUID = Field(
    foreign_key="schedule_entries.accession_id", index=True
  )

  # Relationships
  schedule_entry: Optional["ScheduleEntry"] = Relationship(back_populates="history")


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
  """Request model for updating a schedule entry's priority.

  Accepts both `new_priority` (used by API/tests) and `priority` for
  backward-compatibility with older clients.
  """

  new_priority: int
  reason: str | None = None
  # Backwards-compatible alias
  priority: int | None = None


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
