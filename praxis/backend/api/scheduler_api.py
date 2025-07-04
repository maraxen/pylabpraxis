# pylint: disable=too-many-arguments,broad-except
"""FastAPI endpoints for Protocol Scheduler.

This module provides REST API endpoints for managing protocol scheduling,
asset_lock reservations, and execution monitoring. It integrates with the
scheduler core components and provides comprehensive scheduling capabilities.
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.api.dependencies import get_db
from praxis.backend.core.scheduler import ProtocolScheduler
from praxis.backend.core.asset_lock_manager import AssetLockManager
from praxis.backend.models.scheduler_pydantic import (
  ScheduleProtocolRequest,
  ScheduleEntryResponse,
  ScheduleStatusResponse,
  CancelScheduleRequest,
  SchedulerSystemStatusResponse,
  ScheduleHistoryResponse,
  ScheduleListResponse,
  AssetAvailabilityResponse,
  SchedulePriorityUpdateRequest,
  SchedulerMetricsResponse,
  ScheduleEntryStatus,
)
from praxis.backend.models.scheduler_orm import ScheduleStatusEnum
from praxis.backend.services import scheduler as scheduler_svc
from praxis.backend.services import protocols as protocol_svc
from praxis.backend.utils.errors import PraxisAPIError
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)
router = APIRouter(prefix="/scheduler", tags=["scheduler"])

# This would be injected via dependency injection in a real application
_global_scheduler: Optional[ProtocolScheduler] = None
_global_asset_lock_manager: Optional[AssetLockManager] = None


def get_scheduler() -> ProtocolScheduler:
  """Get the global scheduler instance."""
  global _global_scheduler
  if _global_scheduler is None:
    raise HTTPException(
      status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
      detail="Scheduler not initialized",
    )
  return _global_scheduler


def get_asset_manager() -> AssetLockManager:
  """Get the global asset manager instance."""
  global _global_asset_lock_manager
  if _global_asset_lock_manager is None:
    raise HTTPException(
      status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
      detail="Asset manager not initialized",
    )
  return _global_asset_lock_manager


async def initialize_scheduler_components(
  db_session_factory, redis_url: str = "redis://localhost:6379/0"
):
  """Initialize global scheduler components."""
  global _global_scheduler, _global_asset_lock_manager

  _global_asset_lock_manager = AssetLockManager(redis_url=redis_url)
  await _global_asset_lock_manager.initialize()

  _global_scheduler = ProtocolScheduler(
    db_session_factory=db_session_factory,
    redis_url=redis_url,
  )

  logger.info("Scheduler components initialized")


# Schedule Management Endpoints


@router.post("/schedule", response_model=ScheduleEntryResponse)
@log_async_runtime_errors(logger, raises=True, raises_exception=PraxisAPIError)
async def schedule_protocol(
  request: ScheduleProtocolRequest,
  db: AsyncSession = Depends(get_db),
  scheduler: ProtocolScheduler = Depends(get_scheduler),
) -> ScheduleEntryResponse:
  """Schedule a protocol run for execution.

  This endpoint analyzes asset requirements, reserves necessary assets,
  and queues the protocol for execution using Celery workers.
  """
  # Get the protocol run
  protocol_run = await protocol_svc.read_protocol_run(db, request.protocol_run_id)
  if not protocol_run:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Protocol run {request.protocol_run_id} not found",
    )

  # Check if already scheduled
  existing_schedule = await scheduler_svc.read_schedule_entry_by_protocol_run(
    db, request.protocol_run_id
  )
  if existing_schedule:
    raise HTTPException(
      status_code=status.HTTP_409_CONFLICT,
      detail=f"Protocol run {request.protocol_run_id} is already scheduled",
    )

  # Schedule the protocol
  success = await scheduler.schedule_protocol_execution(
    protocol_run_orm=protocol_run,
    user_params=request.user_params,
    initial_state=request.initial_state,
  )

  if not success:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail="Failed to schedule protocol execution",
    )

  # Get the created schedule entry
  schedule_entry = await scheduler_svc.read_schedule_entry_by_protocol_run(
    db, request.protocol_run_id, include_reservations=True
  )

  if not schedule_entry:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail="Schedule entry not found after creation",
    )

  return ScheduleEntryResponse.model_validate(schedule_entry)


@router.get("/schedule/{schedule_id}", response_model=ScheduleStatusResponse)
@log_async_runtime_errors(logger, raises=True, raises_exception=PraxisAPIError)
async def get_schedule_status(
  schedule_id: uuid.UUID,
  db: AsyncSession = Depends(get_db),
  scheduler: ProtocolScheduler = Depends(get_scheduler),
) -> ScheduleStatusResponse:
  """Get the current status of a scheduled protocol run."""
  schedule_entry = await scheduler_svc.read_schedule_entry(
    db, schedule_id, include_reservations=True
  )
  if not schedule_entry:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Schedule entry {schedule_id} not found",
    )

  # Get protocol information
  protocol_run = await protocol_svc.read_protocol_run(
    db, schedule_entry.protocol_run_accession_id
  )

  protocol_name = None
  protocol_version = None
  if protocol_run and protocol_run.top_level_protocol_definition:
    protocol_def = protocol_run.top_level_protocol_definition
    protocol_name = protocol_def.name
    protocol_version = protocol_def.version

  # Calculate queue position (simplified)
  queue_position = None
  if schedule_entry.status == ScheduleStatusEnum.QUEUED:
    # TODO: Add scheduler service method or include in model to get queue position
    # queued_before = await scheduler_svc.get_queue_position(db, schedule_id)
    # queue_position = queued_before + 1
    queue_position = None  # Placeholder until service method is implemented

  return ScheduleStatusResponse(
    schedule_entry=ScheduleEntryResponse.model_validate(schedule_entry),
    protocol_name=protocol_name,
    protocol_version=protocol_version,
    queue_position=queue_position,
    estimated_start_time=None,  # TODO: Calculate based on queue
    resource_availability=None,  # TODO: Get from asset manager
  )


@router.post("/schedule/{schedule_id}/cancel", response_model=ScheduleEntryResponse)
@log_async_runtime_errors(logger, raises=True, raises_exception=PraxisAPIError)
async def cancel_schedule(
  schedule_id: uuid.UUID,
  request: CancelScheduleRequest,
  db: AsyncSession = Depends(get_db),
  scheduler: ProtocolScheduler = Depends(get_scheduler),
) -> ScheduleEntryResponse:
  """Cancel a scheduled protocol run."""
  schedule_entry = await scheduler_svc.read_schedule_entry(db, schedule_id)
  if not schedule_entry:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Schedule entry {schedule_id} not found",
    )

  # Check if cancellation is allowed
  if schedule_entry.status in [
    ScheduleStatusEnum.CANCELLED,
    ScheduleStatusEnum.FAILED,
  ]:
    raise HTTPException(
      status_code=status.HTTP_409_CONFLICT,
      detail=f"Schedule entry is already {schedule_entry.status}",
    )

  if schedule_entry.status == ScheduleStatusEnum.CELERY_QUEUED and not request.force:
    raise HTTPException(
      status_code=status.HTTP_409_CONFLICT,
      detail="Protocol is already queued for execution. Use force=true to cancel.",
    )

  # Cancel the schedule
  success = await scheduler.cancel_scheduled_run(
    schedule_entry.protocol_run_accession_id
  )
  if not success:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail="Failed to cancel schedule",
    )

  # Update status in database
  updated_entry = await scheduler_svc.update_schedule_entry_status(
    db,
    schedule_id,
    ScheduleStatusEnum.CANCELLED,
    error_details=f"Cancelled by user: {request.reason or 'No reason provided'}",
  )

  await db.commit()

  return ScheduleEntryResponse.model_validate(updated_entry)


@router.get("/schedules", response_model=ScheduleListResponse)
@log_async_runtime_errors(logger, raises=True, raises_exception=PraxisAPIError)
async def list_schedules(
  status: Optional[List[ScheduleEntryStatus]] = Query(None),
  protocol_run_ids: Optional[List[uuid.UUID]] = Query(None),
  priority_min: Optional[int] = Query(None, ge=1, le=10),
  priority_max: Optional[int] = Query(None, ge=1, le=10),
  created_after: Optional[datetime] = Query(None),
  created_before: Optional[datetime] = Query(None),
  include_completed: bool = Query(False),
  include_cancelled: bool = Query(False),
  limit: int = Query(50, ge=1, le=1000),
  offset: int = Query(0, ge=0),
  db: AsyncSession = Depends(get_db),
) -> ScheduleListResponse:
  """List scheduled protocol runs with optional filters."""
  # Convert status to ORM enum
  status_filter = None
  if status:
    status_filter = [ScheduleStatusEnum(s.value) for s in status]

  schedules = await scheduler_svc.list_schedule_entries(
    db,
    status_filter=status_filter,
    protocol_run_ids=protocol_run_ids,
    priority_min=priority_min,
    priority_max=priority_max,
    created_after=created_after,
    created_before=created_before,
    include_completed=include_completed,
    include_cancelled=include_cancelled,
    limit=limit + 1,  # Get one extra to check if there are more
    offset=offset,
  )

  has_more = len(schedules) > limit
  if has_more:
    schedules = schedules[:limit]

  # Get total count (simplified - in production, you'd want to optimize this)
  total_count = len(schedules)  # This is incorrect but functional for now

  schedule_responses = [
    ScheduleEntryResponse.model_validate(schedule) for schedule in schedules
  ]

  return ScheduleListResponse(
    schedules=schedule_responses,
    total_count=total_count,
    limit=limit,
    offset=offset,
    has_more=has_more,
  )


@router.put("/schedule/{schedule_id}/priority", response_model=ScheduleEntryResponse)
@log_async_runtime_errors(logger, raises=True, raises_exception=PraxisAPIError)
async def update_schedule_priority(
  schedule_id: uuid.UUID,
  request: SchedulePriorityUpdateRequest,
  db: AsyncSession = Depends(get_db),
) -> ScheduleEntryResponse:
  """Update the priority of a scheduled protocol run."""
  updated_entry = await scheduler_svc.update_schedule_entry_priority(
    db,
    schedule_id,
    request.new_priority,
    request.reason,
  )

  if not updated_entry:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Schedule entry {schedule_id} not found",
    )

  await db.commit()

  return ScheduleEntryResponse.model_validate(updated_entry)


# Resource Management Endpoints


@router.get(
  "/assets/availability/{asset_type}/{asset_name}",
  response_model=AssetAvailabilityResponse,
)
@log_async_runtime_errors(logger, raises=True, raises_exception=PraxisAPIError)
async def check_asset_availability(
  asset_type: str,
  asset_name: str,
  asset_manager: AssetLockManager = Depends(get_asset_manager),
) -> AssetAvailabilityResponse:
  """Check if a specific asset is currently available."""
  availability_data = await asset_manager.check_asset_availability(
    asset_type, asset_name
  )

  is_available = availability_data is None
  current_reservation = None

  if not is_available and availability_data:
    # Convert to reservation response if needed
    # This is simplified - in practice you'd query the database for full details
    pass

  return AssetAvailabilityResponse(
    asset_type=asset_type,
    asset_name=asset_name,
    is_available=is_available,
    current_reservation=current_reservation,
    estimated_available_at=None,  # TODO: Calculate from reservation data
    alternative_assets=None,  # TODO: Find alternatives
  )


# System Status and Monitoring Endpoints


@router.get("/status", response_model=SchedulerSystemStatusResponse)
@log_async_runtime_errors(logger, raises=True, raises_exception=PraxisAPIError)
async def get_system_status(
  db: AsyncSession = Depends(get_db),
  asset_manager: AssetLockManager = Depends(get_asset_manager),
) -> SchedulerSystemStatusResponse:
  """Get current scheduler system status and health metrics."""
  # Get Redis system status
  redis_status = await asset_manager.get_system_status()

  # TODO: Add scheduler service methods to get these statistics
  # For now, returning placeholder values
  total_queued = 0  # TODO: await scheduler_svc.get_queued_count(db)
  total_running = 0  # TODO: await scheduler_svc.get_running_count(db)
  total_completed_today = 0  # TODO: await scheduler_svc.get_completed_today_count(db)
  total_failed_today = 0  # TODO: await scheduler_svc.get_failed_today_count(db)

  return SchedulerSystemStatusResponse(
    total_queued=total_queued,
    total_running=total_running,
    total_completed_today=total_completed_today,
    total_failed_today=total_failed_today,
    active_resource_locks=redis_status.get("active_locks", 0),
    active_reservations=redis_status.get("active_reservations", 0),
    available_machines=0,  # TODO: Query from machine service
    available_resources=0,  # TODO: Query from resource service
    redis_connected=True,  # TODO: Get from Redis health check
    celery_workers_active=0,  # TODO: Get from Celery inspection
    database_healthy=True,  # TODO: Perform DB health check
    average_queue_time_ms=None,  # TODO: Calculate from metrics
    average_execution_time_ms=None,  # TODO: Calculate from metrics
    system_load_percentage=None,  # TODO: Get system metrics
    timestamp=datetime.now(timezone.utc),
    uptime_seconds=0,  # TODO: Track uptime
    last_cleanup_timestamp=None,  # TODO: Track cleanup times
  )


@router.get(
  "/schedule/{schedule_id}/history", response_model=List[ScheduleHistoryResponse]
)
@log_async_runtime_errors(logger, raises=True, raises_exception=PraxisAPIError)
async def get_schedule_history(
  schedule_id: uuid.UUID,
  limit: int = Query(100, ge=1, le=1000),
  db: AsyncSession = Depends(get_db),
) -> List[ScheduleHistoryResponse]:
  """Get the scheduling history for a specific schedule entry."""
  history_entries = await scheduler_svc.get_schedule_history(db, schedule_id, limit)

  return [ScheduleHistoryResponse.model_validate(entry) for entry in history_entries]


@router.get("/metrics", response_model=SchedulerMetricsResponse)
@log_async_runtime_errors(logger, raises=True, raises_exception=PraxisAPIError)
async def get_scheduler_metrics(
  start_time: Optional[datetime] = Query(None),
  end_time: Optional[datetime] = Query(None),
  db: AsyncSession = Depends(get_db),
) -> SchedulerMetricsResponse:
  """Get scheduler performance metrics for a time period."""
  if not start_time:
    start_time = datetime.now(timezone.utc) - timedelta(days=1)
  if not end_time:
    end_time = datetime.now(timezone.utc)

  metrics = await scheduler_svc.get_scheduling_metrics(db, start_time, end_time)

  status_counts = metrics.get("status_counts", {})

  return SchedulerMetricsResponse(
    period_start=start_time,
    period_end=end_time,
    protocols_scheduled=metrics.get("total_schedules", 0),
    protocols_completed=status_counts.get("COMPLETED", 0),  # When we add this status
    protocols_failed=status_counts.get("FAILED", 0),
    protocols_cancelled=status_counts.get("CANCELLED", 0),
    average_queue_time_seconds=(metrics.get("average_queue_time_ms", 0) or 0) / 1000.0,
    average_execution_time_seconds=0.0,  # TODO: Calculate from protocol runs
    average_resource_reservation_time_ms=metrics.get("average_reservation_time_ms", 0)
    or 0.0,
    peak_concurrent_protocols=0,  # TODO: Calculate from history
    average_resource_utilization_percentage=0.0,  # TODO: Calculate
    most_contested_resources=[],  # TODO: Calculate from reservation conflicts
    scheduling_errors=metrics.get("error_count", 0),
    resource_conflicts=0,  # TODO: Count reservation failures
    timeout_errors=0,  # TODO: Count timeout events
    redis_availability_percentage=100.0,  # TODO: Calculate from monitoring
    database_availability_percentage=100.0,  # TODO: Calculate from monitoring
    celery_task_success_rate=100.0,  # TODO: Calculate from Celery metrics
  )


# Administrative Endpoints


@router.post("/cleanup")
@log_async_runtime_errors(logger, raises=True, raises_exception=PraxisAPIError)
async def cleanup_expired_asset_locks(
  db: AsyncSession = Depends(get_db),
  asset_manager: AssetLockManager = Depends(get_asset_manager),
) -> Dict[str, int]:
  """Clean up expired asset_locks and reservations."""
  # Clean up database reservations
  db_cleanup_count = await scheduler_svc.cleanup_expired_reservations(db)
  await db.commit()

  # Clean up Redis locks
  redis_cleanup_count = await asset_manager.cleanup_expired_locks()

  logger.info(
    "Cleanup completed: %d DB reservations, %d Redis locks",
    db_cleanup_count,
    redis_cleanup_count,
  )

  return {
    "database_reservations_cleaned": db_cleanup_count,
    "redis_locks_cleaned": redis_cleanup_count,
  }
