# pylint: disable=too-many-arguments,broad-except
"""Services for Protocol Scheduler operations.

This module provides service layer functions for managing protocol scheduling,
resource reservations, and execution history. These services work with the
scheduler ORM models and provide the business logic for the scheduler API.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from sqlalchemy import and_, desc, asc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from praxis.backend.models.scheduler_orm import (
  ScheduleEntryOrm,
  ScheduleStatusEnum,
  AssetReservationOrm,
  AssetReservationStatusEnum,
  ScheduleHistoryOrm,
)
from praxis.backend.utils.logging import get_logger
from praxis.backend.utils.uuid import uuid7

logger = get_logger(__name__)


# Schedule Entry Services


async def create_schedule_entry(
  db: AsyncSession,
  protocol_run_accession_id: uuid.UUID,
  priority: int = 1,
  estimated_duration_ms: Optional[int] = None,
  estimated_resource_count: Optional[int] = None,
  analysis_details_json: Optional[Dict[str, Any]] = None,
  scheduling_metadata_json: Optional[Dict[str, Any]] = None,
) -> ScheduleEntryOrm:
  """Create a new schedule entry for a protocol run."""
  schedule_entry = ScheduleEntryOrm(
    accession_id=uuid7(),
    protocol_run_accession_id=protocol_run_accession_id,
    status=ScheduleStatusEnum.QUEUED,
    priority=priority,
    estimated_duration_ms=estimated_duration_ms,
    estimated_resource_count=estimated_resource_count,
    analysis_details_json=analysis_details_json,
    scheduling_metadata_json=scheduling_metadata_json,
    scheduled_at=datetime.now(timezone.utc),
    status_details="Protocol run queued for scheduling",
  )

  db.add(schedule_entry)
  await db.flush()
  await db.refresh(schedule_entry)

  logger.info(
    "Created schedule entry %s for protocol run %s",
    schedule_entry.accession_id,
    protocol_run_accession_id,
  )

  # Log the scheduling event
  await log_schedule_event(
    db,
    schedule_entry.accession_id,
    "SCHEDULE_CREATED",
    new_status=ScheduleStatusEnum.QUEUED.value,
    event_details_json={"priority": priority},
  )

  return schedule_entry


async def read_schedule_entry(
  db: AsyncSession,
  schedule_entry_accession_id: uuid.UUID,
  include_reservations: bool = True,
) -> Optional[ScheduleEntryOrm]:
  """Read a schedule entry by ID."""
  stmt = select(ScheduleEntryOrm).filter(
    ScheduleEntryOrm.accession_id == schedule_entry_accession_id
  )

  if include_reservations:
    stmt = stmt.options(selectinload(ScheduleEntryOrm.resource_reservations))

  result = await db.execute(stmt)
  return result.scalar_one_or_none()


async def read_schedule_entry_by_protocol_run(
  db: AsyncSession,
  protocol_run_accession_id: uuid.UUID,
  include_reservations: bool = True,
) -> Optional[ScheduleEntryOrm]:
  """Read a schedule entry by protocol run ID."""
  stmt = select(ScheduleEntryOrm).filter(
    ScheduleEntryOrm.protocol_run_accession_id == protocol_run_accession_id
  )

  if include_reservations:
    stmt = stmt.options(selectinload(ScheduleEntryOrm.resource_reservations))

  result = await db.execute(stmt)
  return result.scalar_one_or_none()


async def list_schedule_entries(
  db: AsyncSession,
  status_filter: Optional[List[ScheduleStatusEnum]] = None,
  protocol_run_ids: Optional[List[uuid.UUID]] = None,
  priority_min: Optional[int] = None,
  priority_max: Optional[int] = None,
  created_after: Optional[datetime] = None,
  created_before: Optional[datetime] = None,
  include_completed: bool = False,
  include_cancelled: bool = False,
  limit: int = 50,
  offset: int = 0,
  order_by: str = "created_at",
  order_desc: bool = True,
) -> List[ScheduleEntryOrm]:
  """List schedule entries with optional filters."""
  stmt = select(ScheduleEntryOrm)

  # Apply filters
  if status_filter:
    stmt = stmt.filter(ScheduleEntryOrm.status.in_(status_filter))
  elif not include_completed and not include_cancelled:
    # Default: exclude completed and cancelled unless explicitly requested
    exclude_statuses = []
    if not include_completed:
      exclude_statuses.extend([ScheduleStatusEnum.COMPLETED])
    if not include_cancelled:
      exclude_statuses.append(ScheduleStatusEnum.CANCELLED)
    if exclude_statuses:
      stmt = stmt.filter(~ScheduleEntryOrm.status.in_(exclude_statuses))

  if protocol_run_ids:
    stmt = stmt.filter(ScheduleEntryOrm.protocol_run_accession_id.in_(protocol_run_ids))

  if priority_min is not None:
    stmt = stmt.filter(ScheduleEntryOrm.priority >= priority_min)

  if priority_max is not None:
    stmt = stmt.filter(ScheduleEntryOrm.priority <= priority_max)

  if created_after:
    stmt = stmt.filter(ScheduleEntryOrm.created_at >= created_after)

  if created_before:
    stmt = stmt.filter(ScheduleEntryOrm.created_at <= created_before)

  # Apply ordering
  if order_by == "created_at":
    order_col = ScheduleEntryOrm.created_at
  elif order_by == "priority":
    order_col = ScheduleEntryOrm.priority
  elif order_by == "scheduled_at":
    order_col = ScheduleEntryOrm.scheduled_at
  else:
    order_col = ScheduleEntryOrm.created_at

  if order_desc:
    stmt = stmt.order_by(desc(order_col))
  else:
    stmt = stmt.order_by(asc(order_col))

  # Apply pagination
  stmt = stmt.offset(offset).limit(limit)

  # Include reservations
  stmt = stmt.options(selectinload(ScheduleEntryOrm.resource_reservations))

  result = await db.execute(stmt)
  return list(result.scalars().all())


async def update_schedule_entry_status(
  db: AsyncSession,
  schedule_entry_accession_id: uuid.UUID,
  new_status: ScheduleStatusEnum,
  status_details: Optional[str] = None,
  error_details_json: Optional[Dict[str, Any]] = None,
  started_at: Optional[datetime] = None,
  completed_at: Optional[datetime] = None,
) -> Optional[ScheduleEntryOrm]:
  """Update the status of a schedule entry."""
  schedule_entry = await read_schedule_entry(db, schedule_entry_accession_id)
  if not schedule_entry:
    return None

  previous_status = schedule_entry.status
  schedule_entry.status = new_status

  if status_details:
    schedule_entry.status_details = status_details

  if error_details_json:
    schedule_entry.error_details_json = error_details_json

  if started_at:
    schedule_entry.started_at = started_at

  if completed_at:
    schedule_entry.completed_at = completed_at

  await db.flush()
  await db.refresh(schedule_entry)

  # Log the status change
  await log_schedule_event(
    db,
    schedule_entry_accession_id,
    f"STATUS_CHANGED_{new_status.value}",
    previous_status=previous_status.value,
    new_status=new_status.value,
    event_details_json={"status_details": status_details},
    error_details_json=error_details_json,
  )

  logger.info(
    "Updated schedule entry %s status: %s -> %s",
    schedule_entry_accession_id,
    previous_status,
    new_status,
  )

  return schedule_entry


async def update_schedule_entry_priority(
  db: AsyncSession,
  schedule_entry_accession_id: uuid.UUID,
  new_priority: int,
  reason: Optional[str] = None,
) -> Optional[ScheduleEntryOrm]:
  """Update the priority of a schedule entry."""
  schedule_entry = await read_schedule_entry(db, schedule_entry_accession_id)
  if not schedule_entry:
    return None

  old_priority = schedule_entry.priority
  schedule_entry.priority = new_priority

  await db.flush()
  await db.refresh(schedule_entry)

  # Log the priority change
  await log_schedule_event(
    db,
    schedule_entry_accession_id,
    "PRIORITY_CHANGED",
    event_details_json={
      "old_priority": old_priority,
      "new_priority": new_priority,
      "reason": reason,
    },
  )

  logger.info(
    "Updated schedule entry %s priority: %d -> %d",
    schedule_entry_accession_id,
    old_priority,
    new_priority,
  )

  return schedule_entry


async def delete_schedule_entry(
  db: AsyncSession,
  schedule_entry_accession_id: uuid.UUID,
) -> bool:
  """Delete a schedule entry and all associated data."""
  schedule_entry = await read_schedule_entry(db, schedule_entry_accession_id)
  if not schedule_entry:
    return False

  # Log the deletion
  await log_schedule_event(
    db,
    schedule_entry_accession_id,
    "SCHEDULE_DELETED",
    event_details_json={"final_status": schedule_entry.status.value},
  )

  await db.delete(schedule_entry)
  await db.flush()

  logger.info("Deleted schedule entry %s", schedule_entry_accession_id)
  return True


# Resource Reservation Services


async def create_resource_reservation(
  db: AsyncSession,
  schedule_entry_accession_id: uuid.UUID,
  resource_type: str,
  resource_name: str,
  resource_identifier: Optional[str] = None,
  redis_lock_key: Optional[str] = None,
  redis_reservation_id: Optional[uuid.UUID] = None,
  required_capabilities_json: Optional[Dict[str, Any]] = None,
  constraint_details_json: Optional[Dict[str, Any]] = None,
  estimated_duration_ms: Optional[int] = None,
  expires_at: Optional[datetime] = None,
) -> ResourceReservationOrm:
  """Create a new resource reservation."""
  reservation = ResourceReservationOrm(
    accession_id=uuid7(),
    schedule_entry_accession_id=schedule_entry_accession_id,
    resource_type=resource_type,
    resource_name=resource_name,
    resource_identifier=resource_identifier,
    status=ResourceReservationStatusEnum.PENDING,
    redis_lock_key=redis_lock_key or f"resource:{resource_type}:{resource_name}",
    redis_lock_value=str(redis_reservation_id or uuid7()),
    required_capabilities_json=required_capabilities_json,
    constraint_details_json=constraint_details_json,
    estimated_usage_duration_ms=estimated_duration_ms,
    expires_at=expires_at,
    status_details="Resource reservation created",
  )

  db.add(reservation)
  await db.flush()
  await db.refresh(reservation)

  logger.info(
    "Created resource reservation %s for %s:%s",
    reservation.accession_id,
    resource_type,
    resource_name,
  )

  return reservation


async def read_resource_reservation(
  db: AsyncSession,
  reservation_accession_id: uuid.UUID,
) -> Optional[ResourceReservationOrm]:
  """Read a resource reservation by ID."""
  stmt = select(ResourceReservationOrm).filter(
    ResourceReservationOrm.accession_id == reservation_accession_id
  )

  result = await db.execute(stmt)
  return result.scalar_one_or_none()


async def list_resource_reservations(
  db: AsyncSession,
  schedule_entry_accession_id: Optional[uuid.UUID] = None,
  resource_type: Optional[str] = None,
  resource_name: Optional[str] = None,
  status_filter: Optional[List[ResourceReservationStatusEnum]] = None,
  active_only: bool = False,
  limit: int = 100,
  offset: int = 0,
) -> List[ResourceReservationOrm]:
  """List resource reservations with optional filters."""
  stmt = select(ResourceReservationOrm)

  if schedule_entry_accession_id:
    stmt = stmt.filter(
      ResourceReservationOrm.schedule_entry_accession_id == schedule_entry_accession_id
    )

  if resource_type:
    stmt = stmt.filter(ResourceReservationOrm.resource_type == resource_type)

  if resource_name:
    stmt = stmt.filter(ResourceReservationOrm.resource_name == resource_name)

  if status_filter:
    stmt = stmt.filter(ResourceReservationOrm.status.in_(status_filter))
  elif active_only:
    stmt = stmt.filter(
      ResourceReservationOrm.status.in_(
        [
          ResourceReservationStatusEnum.PENDING,
          ResourceReservationStatusEnum.RESERVED,
          ResourceReservationStatusEnum.ACTIVE,
        ]
      )
    )

  stmt = stmt.order_by(ResourceReservationOrm.created_at).offset(offset).limit(limit)

  result = await db.execute(stmt)
  return list(result.scalars().all())


async def update_resource_reservation_status(
  db: AsyncSession,
  reservation_accession_id: uuid.UUID,
  new_status: ResourceReservationStatusEnum,
  status_details: Optional[str] = None,
  error_details_json: Optional[Dict[str, Any]] = None,
  reserved_at: Optional[datetime] = None,
  released_at: Optional[datetime] = None,
) -> Optional[ResourceReservationOrm]:
  """Update the status of a resource reservation."""
  reservation = await read_resource_reservation(db, reservation_accession_id)
  if not reservation:
    return None

  reservation.status = new_status

  if status_details:
    reservation.status_details = status_details

  if error_details_json:
    reservation.error_details_json = error_details_json

  if reserved_at:
    reservation.reserved_at = reserved_at

  if released_at:
    reservation.released_at = released_at

  await db.flush()
  await db.refresh(reservation)

  logger.info(
    "Updated resource reservation %s status to %s",
    reservation_accession_id,
    new_status,
  )

  return reservation


async def cleanup_expired_reservations(
  db: AsyncSession,
  current_time: Optional[datetime] = None,
) -> int:
  """Clean up expired resource reservations."""
  if current_time is None:
    current_time = datetime.now(timezone.utc)

  stmt = select(ResourceReservationOrm).filter(
    and_(
      ResourceReservationOrm.expires_at < current_time,
      ResourceReservationOrm.status.in_(
        [
          ResourceReservationStatusEnum.PENDING,
          ResourceReservationStatusEnum.RESERVED,
          ResourceReservationStatusEnum.ACTIVE,
        ]
      ),
    )
  )

  result = await db.execute(stmt)
  expired_reservations = list(result.scalars().all())

  count = 0
  for reservation in expired_reservations:
    reservation.status = ResourceReservationStatusEnum.EXPIRED
    reservation.released_at = current_time
    reservation.status_details = "Reservation expired due to timeout"
    count += 1

  if count > 0:
    await db.flush()
    logger.info("Cleaned up %d expired resource reservations", count)

  return count


# Schedule History Services


async def log_schedule_event(
  db: AsyncSession,
  schedule_entry_accession_id: uuid.UUID,
  event_type: str,
  previous_status: Optional[str] = None,
  new_status: Optional[str] = None,
  event_details_json: Optional[Dict[str, Any]] = None,
  error_details_json: Optional[Dict[str, Any]] = None,
  message: Optional[str] = None,
  duration_ms: Optional[int] = None,
  triggered_by: Optional[str] = None,
) -> ScheduleHistoryOrm:
  """Log a scheduling event for history and analytics."""
  history_entry = ScheduleHistoryOrm(
    accession_id=uuid7(),
    schedule_entry_accession_id=schedule_entry_accession_id,
    event_type=event_type,
    from_status=previous_status,
    to_status=new_status,
    event_data_json=event_details_json,
    error_details=str(error_details_json) if error_details_json else None,
    message=message,
    duration_ms=duration_ms,
  )

  db.add(history_entry)
  await db.flush()
  await db.refresh(history_entry)

  return history_entry


async def get_schedule_history(
  db: AsyncSession,
  schedule_entry_accession_id: uuid.UUID,
  limit: int = 100,
  offset: int = 0,
) -> List[ScheduleHistoryOrm]:
  """Get scheduling history for a specific schedule entry."""
  stmt = (
    select(ScheduleHistoryOrm)
    .filter(
      ScheduleHistoryOrm.schedule_entry_accession_id == schedule_entry_accession_id
    )
    .order_by(desc(ScheduleHistoryOrm.timestamp))
    .offset(offset)
    .limit(limit)
  )

  result = await db.execute(stmt)
  return list(result.scalars().all())


async def get_scheduling_metrics(
  db: AsyncSession,
  start_time: datetime,
  end_time: datetime,
) -> Dict[str, Any]:
  """Get scheduling metrics for a time period."""
  # Get status counts
  status_count_stmt = (
    select(ScheduleHistoryOrm.to_status, func.count().label("count"))
    .filter(
      and_(
        ScheduleHistoryOrm.timestamp >= start_time,
        ScheduleHistoryOrm.timestamp <= end_time,
      )
    )
    .group_by(ScheduleHistoryOrm.to_status)
  )

  status_result = await db.execute(status_count_stmt)
  status_counts = {row.to_status: row.count for row in status_result}

  # Get average timing metrics
  avg_stmt = select(
    func.avg(ScheduleHistoryOrm.duration_ms).label("avg_duration"),
  ).filter(
    and_(
      ScheduleHistoryOrm.timestamp >= start_time,
      ScheduleHistoryOrm.timestamp <= end_time,
      ScheduleHistoryOrm.duration_ms.isnot(None),
    )
  )

  avg_result = await db.execute(avg_stmt)
  avg_data = avg_result.first()

  # Get error count
  error_count_stmt = select(func.count()).filter(
    and_(
      ScheduleHistoryOrm.timestamp >= start_time,
      ScheduleHistoryOrm.timestamp <= end_time,
      ScheduleHistoryOrm.error_details.isnot(None),
    )
  )

  error_result = await db.execute(error_count_stmt)
  error_count = error_result.scalar()

  return {
    "status_counts": status_counts,
    "avg_duration_ms": avg_data.avg_duration if avg_data else None,
    "error_count": error_count,
    "total_events": sum(status_counts.values()),
  }
