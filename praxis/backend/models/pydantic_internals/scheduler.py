# pylint: disable=too-few-public-methods
"""Pydantic models for Protocol Scheduler API.

This module defines the request/response models for the scheduler API endpoints,
providing type safety and validation for scheduling operations.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import ConfigDict, Field

from praxis.backend.models.enums.schedule import ScheduleStatusEnum
from praxis.backend.models.pydantic_internals.filters import SearchFilters
from praxis.backend.models.pydantic_internals.pydantic_base import PraxisBaseModel


class ResourceReservationStatus(str, Enum):

  """Resource reservation status enum for API."""

  PENDING = "PENDING"
  RESERVED = "RESERVED"
  ACTIVE = "ACTIVE"
  RELEASED = "RELEASED"
  EXPIRED = "EXPIRED"
  FAILED = "FAILED"


class ResourceRequirementRequest(PraxisBaseModel):

  """Request model for defining resource requirements."""

  model_config = ConfigDict(from_attributes=True)

  resource_type: str = Field(
    ...,
    description="Type of resource (machine, resource, deck)",
  )
  resource_name: str = Field(..., description="Name/identifier of the resource")
  required_capabilities: dict[str, Any] | None = Field(
    default=None,
    description="Required capabilities for the resource",
  )
  estimated_duration_ms: int | None = Field(
    default=None,
    description="Estimated duration in milliseconds",
  )
  priority: int = Field(default=1, description="Priority level (1-10)")


class ResourceReservationResponse(PraxisBaseModel):

  """Response model for resource reservations."""

  # Remove accession_id and created_at fields, they are inherited.
  # The model_config is also inherited from PraxisBaseModel.

  resource_type: str
  resource_name: str
  resource_identifier: str | None
  status: ResourceReservationStatus
  redis_lock_key: str | None
  redis_reservation_id: uuid.UUID | None
  required_capabilities: dict[str, Any] | None = Field(
    alias="required_capabilities_json",
  )
  constraint_details: dict[str, Any] | None = Field(alias="constraint_details_json")
  # created_at is inherited
  reserved_at: datetime | None
  released_at: datetime | None
  expires_at: datetime | None
  estimated_duration_ms: int | None
  status_details: str | None
  error_details: dict[str, Any] | None = Field(alias="error_details_json")

  # Add model_config if you need to override values from PraxisBaseModel.
  # Otherwise, remove it as it is inherited.
  model_config = ConfigDict(
    from_attributes=True,
  )


class ScheduleProtocolRequest(PraxisBaseModel):

  """Request model for scheduling a protocol run."""

  model_config = ConfigDict(from_attributes=True)

  protocol_run_id: uuid.UUID = Field(
    ...,
    description="ID of the protocol run to schedule",
  )
  user_params: dict[str, Any] = Field(..., description="User-provided parameters")
  initial_state: dict[str, Any] | None = Field(
    default=None,
    description="Initial state data for the protocol",
  )
  priority: int = Field(default=1, description="Schedule priority (1-10)")
  estimated_duration_ms: int | None = Field(
    default=None,
    description="Estimated execution duration",
  )
  resource_requirements: list[ResourceRequirementRequest] | None = Field(
    default=None,
    description="Override resource requirements analysis",
  )
  scheduling_constraints: dict[str, Any] | None = Field(
    default=None,
    description="Additional scheduling constraints",
  )


class ScheduleEntryResponse(PraxisBaseModel):

  """Response model for schedule entries."""

  protocol_run_accession_id: uuid.UUID
  status: ScheduleStatusEnum
  priority: int
  scheduled_at: datetime | None
  started_at: datetime | None
  completed_at: datetime | None
  estimated_duration_ms: int | None
  estimated_resource_count: int | None
  analysis_details: dict[str, Any] | None = Field(alias="analysis_details_json")
  scheduling_metadata: dict[str, Any] | None = Field(
    alias="scheduling_metadata_json",
  )
  error_details: dict[str, Any] | None = Field(alias="error_details_json")
  status_details: str | None
  resource_reservations: list[ResourceReservationResponse] | None = None


class ScheduleStatusResponse(PraxisBaseModel):

  """Response model for schedule status queries."""

  model_config = ConfigDict(from_attributes=True)

  schedule_entry: ScheduleEntryResponse
  protocol_name: str | None
  protocol_version: str | None
  queue_position: int | None
  estimated_start_time: datetime | None
  resource_availability: dict[str, Any] | None


class CancelScheduleRequest(PraxisBaseModel):

  """Request model for cancelling a scheduled run."""

  model_config = ConfigDict(from_attributes=True)

  reason: str | None = Field(default=None, description="Reason for cancellation")
  force: bool = Field(default=False, description="Force cancellation even if running")


class ScheduleAnalysisResponse(PraxisBaseModel):

  """Response model for schedule analysis."""

  model_config = ConfigDict(from_attributes=True)

  protocol_run_id: uuid.UUID
  resource_requirements: list[ResourceRequirementRequest]
  estimated_duration_ms: int | None
  analysis_timestamp: datetime
  analysis_details: dict[str, Any]
  warnings: list[str] | None = None
  errors: list[str] | None = None


class SchedulerSystemStatusResponse(PraxisBaseModel):

  """Response model for scheduler system status."""

  model_config = ConfigDict(from_attributes=True)

  # Queue statistics
  total_queued: int
  total_running: int
  total_completed_today: int
  total_failed_today: int

  # Resource statistics
  active_resource_locks: int
  active_reservations: int
  available_machines: int
  available_resources: int

  # System health
  redis_connected: bool
  celery_workers_active: int
  database_healthy: bool

  # Performance metrics
  average_queue_time_ms: float | None
  average_execution_time_ms: float | None
  system_load_percentage: float | None

  # Current system state
  timestamp: datetime
  uptime_seconds: int
  last_cleanup_timestamp: datetime | None


class ScheduleHistoryResponse(PraxisBaseModel):

  """Response model for schedule history entries."""

  schedule_entry_accession_id: uuid.UUID
  event_type: str
  event_timestamp: datetime
  previous_status: str | None
  new_status: str | None
  duration_ms: int | None
  resource_analysis_time_ms: int | None
  resource_reservation_time_ms: int | None
  queue_wait_time_ms: int | None
  active_schedules_count: int | None
  system_load_metrics: dict[str, Any] | None = Field(
    alias="system_load_metrics_json",
  )
  event_details: dict[str, Any] | None = Field(alias="event_details_json")
  error_details: dict[str, Any] | None = Field(alias="error_details_json")
  triggered_by: str | None


class ScheduleListRequest(PraxisBaseModel):

  """Request model for listing schedules with filters."""

  model_config = ConfigDict(from_attributes=True)

  status: list[ScheduleStatusEnum] | None = Field(
    default=None,
    description="Filter by schedule status",
  )
  protocol_run_ids: list[uuid.UUID] | None = Field(
    default=None,
    description="Filter by specific protocol run IDs",
  )
  priority_min: int | None = Field(default=None, description="Minimum priority")
  priority_max: int | None = Field(default=None, description="Maximum priority")
  created_after: datetime | None = Field(
    default=None,
    description="Filter by creation time (after)",
  )
  created_before: datetime | None = Field(
    default=None,
    description="Filter by creation time (before)",
  )
  include_completed: bool = Field(
    default=False,
    description="Include completed schedules",
  )
  include_cancelled: bool = Field(
    default=False,
    description="Include cancelled schedules",
  )
  limit: int = Field(default=50, ge=1, le=1000, description="Maximum results")
  offset: int = Field(default=0, ge=0, description="Results offset")


class ScheduleListResponse(PraxisBaseModel):

  """Response model for schedule listing."""

  model_config = ConfigDict(from_attributes=True)

  schedules: list[ScheduleEntryResponse]
  total_count: int
  limit: int
  offset: int
  has_more: bool


class AssetAvailabilityResponse(PraxisBaseModel):

  """Response model for asset availability check."""

  model_config = ConfigDict(from_attributes=True)

  asset_type: str
  asset_name: str
  is_available: bool
  current_reservation: ResourceReservationResponse | None
  estimated_available_at: datetime | None
  alternative_assets: list[str] | None


class SchedulePriorityUpdateRequest(PraxisBaseModel):

  """Request model for updating schedule priority."""

  model_config = ConfigDict(from_attributes=True)

  new_priority: int = Field(..., ge=1, le=100, description="New priority level")
  reason: str | None = Field(default=None, description="Reason for priority change")


class SchedulerMetricsResponse(PraxisBaseModel):

  """Response model for scheduler performance metrics."""

  model_config = ConfigDict(from_attributes=True)

  # Time-based metrics
  period_start: datetime
  period_end: datetime

  # Throughput metrics
  protocols_scheduled: int
  protocols_completed: int
  protocols_failed: int
  protocols_cancelled: int

  # Performance metrics
  average_queue_time_seconds: float
  average_execution_time_seconds: float
  average_resource_reservation_time_ms: float

  # Resource utilization
  peak_concurrent_protocols: int
  average_resource_utilization_percentage: float
  most_contested_resources: list[dict[str, Any]]

  # Error metrics
  scheduling_errors: int
  resource_conflicts: int
  timeout_errors: int

  # System health
  redis_availability_percentage: float
  database_availability_percentage: float
  celery_task_success_rate: float


class ScheduleListFilters(PraxisBaseModel):

  """Model for filtering schedule lists."""

  search_filters: SearchFilters
  status: list[ScheduleStatusEnum] | None = None
  protocol_run_ids: list[uuid.UUID] | None = None
  priority_min: int | None = None
  priority_max: int | None = None
  include_completed: bool = False
  include_cancelled: bool = False


class ScheduleEntryCreate(PraxisBaseModel):

  """Request model for creating a schedule entry."""

  model_config = ConfigDict(from_attributes=True)

  name: str = Field(..., description="Unique name for the schedule entry")

  protocol_run_accession_id: uuid.UUID = Field(
    ...,
    description="ID of the protocol run to schedule",
  )
  priority: int = Field(default=1, description="Schedule priority (1-10)")
  estimated_duration_ms: int | None = Field(
    default=None,
    description="Estimated execution duration",
  )
  required_asset_count: int | None = Field(
    default=None,
    description="Estimated number of assets required",
  )
  asset_requirements_json: dict[str, Any] | None = Field(
    default=None,
    description="Asset requirements analysis results",
  )
  user_params_json: dict[str, Any] | None = Field(
    default=None,
    description="User-provided scheduling parameters",
  )
  status: ScheduleStatusEnum = Field(default=ScheduleStatusEnum.QUEUED, description="Initial status")


class ScheduleEntryUpdate(PraxisBaseModel):

  """Request model for updating a schedule entry."""

  model_config = ConfigDict(from_attributes=True)

  status: ScheduleStatusEnum | None = None
  priority: int | None = None
  last_error_message: str | None = None
  execution_started_at: datetime | None = None
  execution_completed_at: datetime | None = None
