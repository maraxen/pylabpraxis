# pylint: disable=too-few-public-methods
"""Pydantic models for Protocol Scheduler API.

This module defines the request/response models for the scheduler API endpoints,
providing type safety and validation for scheduling operations.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field, ConfigDict

from praxis.backend.models.scheduler_orm import (
  ScheduleStatusEnum,
  AssetReservationStatusEnum,
)


class ScheduleEntryStatus(str, Enum):
  """Schedule entry status enum for API."""

  QUEUED = "QUEUED"
  RESOURCE_ANALYSIS = "RESOURCE_ANALYSIS"
  RESOURCE_RESERVATION = "RESOURCE_RESERVATION"
  READY_FOR_EXECUTION = "READY_FOR_EXECUTION"
  EXECUTION_QUEUED = "EXECUTION_QUEUED"
  CANCELLED = "CANCELLED"
  FAILED = "FAILED"


class ResourceReservationStatus(str, Enum):
  """Resource reservation status enum for API."""

  PENDING = "PENDING"
  RESERVED = "RESERVED"
  ACTIVE = "ACTIVE"
  RELEASED = "RELEASED"
  EXPIRED = "EXPIRED"
  FAILED = "FAILED"


class ResourceRequirementRequest(BaseModel):
  """Request model for defining resource requirements."""

  model_config = ConfigDict(from_attributes=True)

  resource_type: str = Field(
    ..., description="Type of resource (machine, resource, deck)"
  )
  resource_name: str = Field(..., description="Name/identifier of the resource")
  required_capabilities: Optional[Dict[str, Any]] = Field(
    default=None, description="Required capabilities for the resource"
  )
  estimated_duration_ms: Optional[int] = Field(
    default=None, description="Estimated duration in milliseconds"
  )
  priority: int = Field(default=1, description="Priority level (1-10)")


class ResourceReservationResponse(BaseModel):
  """Response model for resource reservations."""

  model_config = ConfigDict(from_attributes=True)

  accession_id: uuid.UUID
  resource_type: str
  resource_name: str
  resource_identifier: Optional[str]
  status: ResourceReservationStatus
  redis_lock_key: Optional[str]
  redis_reservation_id: Optional[uuid.UUID]
  required_capabilities: Optional[Dict[str, Any]] = Field(
    alias="required_capabilities_json"
  )
  constraint_details: Optional[Dict[str, Any]] = Field(alias="constraint_details_json")
  created_at: datetime
  reserved_at: Optional[datetime]
  released_at: Optional[datetime]
  expires_at: Optional[datetime]
  estimated_duration_ms: Optional[int]
  status_details: Optional[str]
  error_details: Optional[Dict[str, Any]] = Field(alias="error_details_json")


class ScheduleProtocolRequest(BaseModel):
  """Request model for scheduling a protocol run."""

  model_config = ConfigDict(from_attributes=True)

  protocol_run_id: uuid.UUID = Field(
    ..., description="ID of the protocol run to schedule"
  )
  user_params: Dict[str, Any] = Field(..., description="User-provided parameters")
  initial_state: Optional[Dict[str, Any]] = Field(
    default=None, description="Initial state data for the protocol"
  )
  priority: int = Field(default=1, description="Schedule priority (1-10)")
  estimated_duration_ms: Optional[int] = Field(
    default=None, description="Estimated execution duration"
  )
  resource_requirements: Optional[List[ResourceRequirementRequest]] = Field(
    default=None, description="Override resource requirements analysis"
  )
  scheduling_constraints: Optional[Dict[str, Any]] = Field(
    default=None, description="Additional scheduling constraints"
  )


class ScheduleEntryResponse(BaseModel):
  """Response model for schedule entries."""

  model_config = ConfigDict(from_attributes=True)

  accession_id: uuid.UUID
  protocol_run_accession_id: uuid.UUID
  status: ScheduleEntryStatus
  priority: int
  created_at: datetime
  scheduled_at: Optional[datetime]
  started_at: Optional[datetime]
  completed_at: Optional[datetime]
  estimated_duration_ms: Optional[int]
  estimated_resource_count: Optional[int]
  analysis_details: Optional[Dict[str, Any]] = Field(alias="analysis_details_json")
  scheduling_metadata: Optional[Dict[str, Any]] = Field(
    alias="scheduling_metadata_json"
  )
  error_details: Optional[Dict[str, Any]] = Field(alias="error_details_json")
  status_details: Optional[str]
  resource_reservations: Optional[List[ResourceReservationResponse]] = None


class ScheduleStatusResponse(BaseModel):
  """Response model for schedule status queries."""

  model_config = ConfigDict(from_attributes=True)

  schedule_entry: ScheduleEntryResponse
  protocol_name: Optional[str]
  protocol_version: Optional[str]
  queue_position: Optional[int]
  estimated_start_time: Optional[datetime]
  resource_availability: Optional[Dict[str, Any]]


class CancelScheduleRequest(BaseModel):
  """Request model for cancelling a scheduled run."""

  model_config = ConfigDict(from_attributes=True)

  reason: Optional[str] = Field(default=None, description="Reason for cancellation")
  force: bool = Field(default=False, description="Force cancellation even if running")


class ScheduleAnalysisResponse(BaseModel):
  """Response model for schedule analysis."""

  model_config = ConfigDict(from_attributes=True)

  protocol_run_id: uuid.UUID
  resource_requirements: List[ResourceRequirementRequest]
  estimated_duration_ms: Optional[int]
  analysis_timestamp: datetime
  analysis_details: Dict[str, Any]
  warnings: Optional[List[str]] = None
  errors: Optional[List[str]] = None


class SchedulerSystemStatusResponse(BaseModel):
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
  average_queue_time_ms: Optional[float]
  average_execution_time_ms: Optional[float]
  system_load_percentage: Optional[float]

  # Current system state
  timestamp: datetime
  uptime_seconds: int
  last_cleanup_timestamp: Optional[datetime]


class ScheduleHistoryResponse(BaseModel):
  """Response model for schedule history entries."""

  model_config = ConfigDict(from_attributes=True)

  accession_id: uuid.UUID
  schedule_entry_accession_id: uuid.UUID
  event_type: str
  event_timestamp: datetime
  previous_status: Optional[str]
  new_status: Optional[str]
  duration_ms: Optional[int]
  resource_analysis_time_ms: Optional[int]
  resource_reservation_time_ms: Optional[int]
  queue_wait_time_ms: Optional[int]
  active_schedules_count: Optional[int]
  system_load_metrics: Optional[Dict[str, Any]] = Field(
    alias="system_load_metrics_json"
  )
  event_details: Optional[Dict[str, Any]] = Field(alias="event_details_json")
  error_details: Optional[Dict[str, Any]] = Field(alias="error_details_json")
  triggered_by: Optional[str]


class ScheduleListRequest(BaseModel):
  """Request model for listing schedules with filters."""

  model_config = ConfigDict(from_attributes=True)

  status: Optional[List[ScheduleEntryStatus]] = Field(
    default=None, description="Filter by schedule status"
  )
  protocol_run_ids: Optional[List[uuid.UUID]] = Field(
    default=None, description="Filter by specific protocol run IDs"
  )
  priority_min: Optional[int] = Field(default=None, description="Minimum priority")
  priority_max: Optional[int] = Field(default=None, description="Maximum priority")
  created_after: Optional[datetime] = Field(
    default=None, description="Filter by creation time (after)"
  )
  created_before: Optional[datetime] = Field(
    default=None, description="Filter by creation time (before)"
  )
  include_completed: bool = Field(
    default=False, description="Include completed schedules"
  )
  include_cancelled: bool = Field(
    default=False, description="Include cancelled schedules"
  )
  limit: int = Field(default=50, ge=1, le=1000, description="Maximum results")
  offset: int = Field(default=0, ge=0, description="Results offset")


class ScheduleListResponse(BaseModel):
  """Response model for schedule listing."""

  model_config = ConfigDict(from_attributes=True)

  schedules: List[ScheduleEntryResponse]
  total_count: int
  limit: int
  offset: int
  has_more: bool


class AssetAvailabilityResponse(BaseModel):
  """Response model for asset availability check."""

  model_config = ConfigDict(from_attributes=True)

  asset_type: str
  asset_name: str
  is_available: bool
  current_reservation: Optional[ResourceReservationResponse]
  estimated_available_at: Optional[datetime]
  alternative_assets: Optional[List[str]]


class SchedulePriorityUpdateRequest(BaseModel):
  """Request model for updating schedule priority."""

  model_config = ConfigDict(from_attributes=True)

  new_priority: int = Field(..., ge=1, le=10, description="New priority level")
  reason: Optional[str] = Field(default=None, description="Reason for priority change")


class SchedulerMetricsResponse(BaseModel):
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
  most_contested_resources: List[Dict[str, Any]]

  # Error metrics
  scheduling_errors: int
  resource_conflicts: int
  timeout_errors: int

  # System health
  redis_availability_percentage: float
  database_availability_percentage: float
  celery_task_success_rate: float
