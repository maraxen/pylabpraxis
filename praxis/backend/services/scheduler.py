# pylint: disable=too-many-arguments,broad-except,fixme,unused-argument,too-many-lines
"""Service layer for Protocol Scheduler operations.

praxis/backend/services/scheduler.py

Service layer for interacting with protocol scheduling, asset reservation,
and execution history data in the database. This includes schedule entries,
asset reservations, and schedule history tracking for protocol execution
management.
"""

import uuid
from datetime import datetime, timezone
from functools import partial
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
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors
from praxis.backend.utils.uuid import uuid7

logger = get_logger(__name__)

scheduler_service_log = partial(
  log_async_runtime_errors,
  logger_instance=logger,
  exception_type=Exception,
  raises=True,
  raises_exception=ValueError,
  return_=None,
)


# Schedule Entry Services


@scheduler_service_log(
  prefix="Schedule Entry Service: Creating schedule entry - ",
  suffix=" - Ensure the protocol run ID is valid and unique.",
)
async def create_schedule_entry(
  db: AsyncSession,
  protocol_run_accession_id: uuid.UUID,
  priority: int = 1,
  estimated_duration_ms: Optional[int] = None,
  estimated_resource_count: Optional[int] = None,
  analysis_details_json: Optional[Dict[str, Any]] = None,
  scheduling_metadata_json: Optional[Dict[str, Any]] = None,
) -> ScheduleEntryOrm:
  """Create a new schedule entry for a protocol run.

  This function creates a new `ScheduleEntryOrm` for scheduling a protocol run
  for execution with asset management and priority handling.

  Args:
      db (AsyncSession): The database session.
      protocol_run_accession_id (uuid.UUID): The unique identifier of the
          protocol run to be scheduled.
      priority (int, optional): The scheduling priority (higher numbers =
          higher priority). Defaults to 1.
      estimated_duration_ms (Optional[int], optional): Estimated execution
          duration in milliseconds. Defaults to None.
      estimated_resource_count (Optional[int], optional): Estimated number of
          assets required for execution. Defaults to None.
      analysis_details_json (Optional[Dict[str, Any]], optional): Asset
          requirements analysis results stored as JSON. Defaults to None.
      scheduling_metadata_json (Optional[Dict[str, Any]], optional): Additional
          user-provided scheduling parameters stored as JSON. Defaults to None.

  Returns:
      ScheduleEntryOrm: The created schedule entry object.

  Raises:
      ValueError: If a schedule entry for the same protocol run already exists.
      Exception: For any other unexpected errors during the process.

  """
  log_prefix = (
    f"Schedule Entry (Protocol Run: '{protocol_run_accession_id}', creating new):"
  )
  logger.info("%s Attempting to create new schedule entry.", log_prefix)

  # Check if a schedule entry for this protocol run already exists
  existing_entry = await db.execute(
    select(ScheduleEntryOrm).filter(
      ScheduleEntryOrm.protocol_run_accession_id == protocol_run_accession_id
    )
  )
  if existing_entry.scalar_one_or_none():
    error_message = (
      f"{log_prefix} A schedule entry for protocol run "
      f"'{protocol_run_accession_id}' already exists. Use the update function for "
      f"existing schedule entries."
    )
    logger.error(error_message)
    raise ValueError(error_message)

  # Create a new ScheduleEntryOrm
  schedule_entry = ScheduleEntryOrm(
    accession_id=uuid7(),
    protocol_run_accession_id=protocol_run_accession_id,
    status=ScheduleStatusEnum.QUEUED,
    priority=priority,
    estimated_duration_ms=estimated_duration_ms,
    required_asset_count=estimated_resource_count or 0,
    asset_requirements_json=analysis_details_json,
    user_params_json=scheduling_metadata_json,
    scheduled_at=datetime.now(timezone.utc),
  )
  db.add(schedule_entry)
  logger.info("%s Initialized new schedule entry for creation.", log_prefix)

  try:
    await db.flush()
    logger.debug("%s Flushed new schedule entry to get ID.", log_prefix)

    # Log the scheduling event
    await log_schedule_event(
      db,
      schedule_entry.accession_id,
      "SCHEDULE_CREATED",
      new_status=ScheduleStatusEnum.QUEUED.value,
      event_details_json={"priority": priority},
    )

    await db.commit()
    logger.info(
      "%s Successfully created schedule entry %s for protocol run %s",
      log_prefix,
      schedule_entry.accession_id,
      protocol_run_accession_id,
    )

    return schedule_entry

  except Exception as exc:
    await db.rollback()
    error_message = f"{log_prefix} Failed to create schedule entry: {exc}"
    logger.error(error_message, exc_info=True)
    raise Exception(error_message) from exc


async def read_schedule_entry(
  db: AsyncSession,
  schedule_entry_accession_id: uuid.UUID,
  include_reservations: bool = True,
) -> Optional[ScheduleEntryOrm]:
  """Read a schedule entry by ID.

  Args:
      db (AsyncSession): The database session.
      schedule_entry_accession_id (uuid.UUID): The unique identifier of the
          schedule entry.
      include_reservations (bool, optional): Whether to include related asset
          reservations. Defaults to True.

  Returns:
      Optional[ScheduleEntryOrm]: The schedule entry object if found, None otherwise.

  """
  stmt = select(ScheduleEntryOrm).filter(
    ScheduleEntryOrm.accession_id == schedule_entry_accession_id
  )

  if include_reservations:
    stmt = stmt.options(selectinload(ScheduleEntryOrm.asset_reservations))

  result = await db.execute(stmt)
  return result.scalar_one_or_none()


async def read_schedule_entry_by_protocol_run(
  db: AsyncSession,
  protocol_run_accession_id: uuid.UUID,
  include_reservations: bool = True,
) -> Optional[ScheduleEntryOrm]:
  """Read a schedule entry by protocol run ID.

  Args:
      db (AsyncSession): The database session.
      protocol_run_accession_id (uuid.UUID): The unique identifier of the
          protocol run.
      include_reservations (bool, optional): Whether to include related asset
          reservations. Defaults to True.

  Returns:
      Optional[ScheduleEntryOrm]: The schedule entry object if found, None otherwise.

  """
  stmt = select(ScheduleEntryOrm).filter(
    ScheduleEntryOrm.protocol_run_accession_id == protocol_run_accession_id
  )

  if include_reservations:
    stmt = stmt.options(selectinload(ScheduleEntryOrm.asset_reservations))

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
  """List schedule entries with optional filters.

  Args:
      db (AsyncSession): The database session.
      status_filter (Optional[List[ScheduleStatusEnum]], optional): Filter by
          specific statuses. Defaults to None.
      protocol_run_ids (Optional[List[uuid.UUID]], optional): Filter by specific
          protocol run IDs. Defaults to None.
      priority_min (Optional[int], optional): Minimum priority filter.
          Defaults to None.
      priority_max (Optional[int], optional): Maximum priority filter.
          Defaults to None.
      created_after (Optional[datetime], optional): Filter entries created after
          this timestamp. Defaults to None.
      created_before (Optional[datetime], optional): Filter entries created before
          this timestamp. Defaults to None.
      include_completed (bool, optional): Whether to include completed entries.
          Defaults to False.
      include_cancelled (bool, optional): Whether to include cancelled entries.
          Defaults to False.
      limit (int, optional): Maximum number of results to return. Defaults to 50.
      offset (int, optional): Number of results to skip. Defaults to 0.
      order_by (str, optional): Field to order by. Defaults to "created_at".
      order_desc (bool, optional): Whether to order in descending order.
          Defaults to True.

  Returns:
      List[ScheduleEntryOrm]: List of schedule entry objects matching the filters.

  """
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
  stmt = stmt.options(selectinload(ScheduleEntryOrm.asset_reservations))

  result = await db.execute(stmt)
  return list(result.scalars().all())


async def update_schedule_entry_status(
  db: AsyncSession,
  schedule_entry_accession_id: uuid.UUID,
  new_status: ScheduleStatusEnum,
  error_details: Optional[str] = None,
  started_at: Optional[datetime] = None,
  completed_at: Optional[datetime] = None,
) -> Optional[ScheduleEntryOrm]:
  """Update the status of a schedule entry.

  Args:
      db (AsyncSession): The database session.
      schedule_entry_accession_id (uuid.UUID): The unique identifier of the
          schedule entry to update.
      new_status (ScheduleStatusEnum): The new status to set.
      error_details (Optional[str], optional): Error message if status change
          is due to an error. Defaults to None.
      started_at (Optional[datetime], optional): Timestamp when execution started.
          Defaults to None.
      completed_at (Optional[datetime], optional): Timestamp when execution completed.
          Defaults to None.

  Returns:
      Optional[ScheduleEntryOrm]: The updated schedule entry, or None if not found.

  """
  schedule_entry = await read_schedule_entry(db, schedule_entry_accession_id)
  if not schedule_entry:
    return None

  previous_status = schedule_entry.status
  schedule_entry.status = new_status

  if error_details:
    schedule_entry.last_error_message = error_details

  if started_at:
    schedule_entry.execution_started_at = started_at

  if completed_at:
    schedule_entry.execution_completed_at = completed_at

  await db.flush()
  await db.refresh(schedule_entry)

  # Log the status change
  await log_schedule_event(
    db,
    schedule_entry_accession_id,
    f"STATUS_CHANGED_{new_status.value}",
    previous_status=previous_status.value,
    new_status=new_status.value,
    event_details_json={"error_details": error_details},
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
  """Update the priority of a schedule entry.

  Args:
      db (AsyncSession): The database session.
      schedule_entry_accession_id (uuid.UUID): The unique identifier of the
          schedule entry to update.
      new_priority (int): The new priority value.
      reason (Optional[str], optional): Reason for the priority change.
          Defaults to None.

  Returns:
      Optional[ScheduleEntryOrm]: The updated schedule entry, or None if not found.

  """
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
  """Delete a schedule entry and all associated data.

  Args:
      db (AsyncSession): The database session.
      schedule_entry_accession_id (uuid.UUID): The unique identifier of the
          schedule entry to delete.

  Returns:
      bool: True if the schedule entry was deleted, False if not found.

  """
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


# Asset Reservation Services


@scheduler_service_log(
  prefix="Asset Reservation Service: Creating asset reservation - ",
  suffix=" - Ensure the schedule entry ID is valid.",
)
async def create_asset_reservation(
  db: AsyncSession,
  schedule_entry_accession_id: uuid.UUID,
  asset_type: str,
  asset_name: str,
  asset_instance_accession_id: Optional[uuid.UUID] = None,
  redis_lock_key: Optional[str] = None,
  redis_lock_value: Optional[str] = None,
  required_capabilities_json: Optional[Dict[str, Any]] = None,
  estimated_duration_ms: Optional[int] = None,
  expires_at: Optional[datetime] = None,
) -> AssetReservationOrm:
  """Create a new asset reservation.

  Args:
      db (AsyncSession): The database session.
      schedule_entry_accession_id (uuid.UUID): The ID of the associated schedule entry.
      asset_type (str): The type of asset (e.g., "machine", "deck").
      asset_name (str): The name of the asset to reserve.
      asset_instance_accession_id (Optional[uuid.UUID], optional): The specific
          asset instance ID. Defaults to None.
      redis_lock_key (Optional[str], optional): Redis lock key for distributed
          locking. Defaults to None.
      redis_lock_value (Optional[str], optional): Redis lock value for distributed
          locking. Defaults to None.
      required_capabilities_json (Optional[Dict[str, Any]], optional): Required
          capabilities for the asset. Defaults to None.
      estimated_duration_ms (Optional[int], optional): Estimated usage duration
          in milliseconds. Defaults to None.
      expires_at (Optional[datetime], optional): When the reservation expires.
          Defaults to None.

  Returns:
      AssetReservationOrm: The created asset reservation object.

  Raises:
      Exception: For any unexpected errors during the process.

  """
  log_prefix = f"Asset Reservation (Asset: '{asset_type}:{asset_name}', creating new):"
  logger.info("%s Attempting to create new asset reservation.", log_prefix)

  reservation = AssetReservationOrm(
    accession_id=uuid7(),
    schedule_entry_accession_id=schedule_entry_accession_id,
    asset_type=asset_type,
    asset_name=asset_name,
    asset_instance_accession_id=asset_instance_accession_id,
    status=AssetReservationStatusEnum.PENDING,
    redis_lock_key=redis_lock_key or f"asset:{asset_type}:{asset_name}",
    redis_lock_value=redis_lock_value or str(uuid7()),
    required_capabilities_json=required_capabilities_json,
    estimated_usage_duration_ms=estimated_duration_ms,
    expires_at=expires_at,
  )
  logger.info("%s Initialized new asset reservation for creation.", log_prefix)

  try:
    db.add(reservation)
    await db.flush()
    await db.refresh(reservation)

    logger.info(
      "%s Successfully created asset reservation %s for %s:%s",
      log_prefix,
      reservation.accession_id,
      asset_type,
      asset_name,
    )

    return reservation

  except Exception as exc:
    await db.rollback()
    error_message = f"{log_prefix} Failed to create asset reservation: {exc}"
    logger.error(error_message, exc_info=True)
    raise Exception(error_message) from exc


async def read_asset_reservation(
  db: AsyncSession,
  reservation_accession_id: uuid.UUID,
) -> Optional[AssetReservationOrm]:
  """Read an asset reservation by ID.

  Args:
      db (AsyncSession): The database session.
      reservation_accession_id (uuid.UUID): The unique identifier of the
          asset reservation.

  Returns:
      Optional[AssetReservationOrm]: The asset reservation object if found,
          None otherwise.

  """
  stmt = select(AssetReservationOrm).filter(
    AssetReservationOrm.accession_id == reservation_accession_id
  )

  result = await db.execute(stmt)
  return result.scalar_one_or_none()


async def list_asset_reservations(
  db: AsyncSession,
  schedule_entry_accession_id: Optional[uuid.UUID] = None,
  asset_type: Optional[str] = None,
  asset_name: Optional[str] = None,
  status_filter: Optional[List[AssetReservationStatusEnum]] = None,
  active_only: bool = False,
  limit: int = 100,
  offset: int = 0,
) -> List[AssetReservationOrm]:
  """List asset reservations with optional filters.

  Args:
      db (AsyncSession): The database session.
      schedule_entry_accession_id (Optional[uuid.UUID], optional): Filter by
          schedule entry ID. Defaults to None.
      asset_type (Optional[str], optional): Filter by asset type. Defaults to None.
      asset_name (Optional[str], optional): Filter by asset name. Defaults to None.
      status_filter (Optional[List[AssetReservationStatusEnum]], optional): Filter by
          specific statuses. Defaults to None.
      active_only (bool, optional): Whether to only include active reservations.
          Defaults to False.
      limit (int, optional): Maximum number of results to return. Defaults to 100.
      offset (int, optional): Number of results to skip. Defaults to 0.

  Returns:
      List[AssetReservationOrm]: List of asset reservation objects matching filters.

  """
  stmt = select(AssetReservationOrm)

  if schedule_entry_accession_id:
    stmt = stmt.filter(
      AssetReservationOrm.schedule_entry_accession_id == schedule_entry_accession_id
    )

  if asset_type:
    stmt = stmt.filter(AssetReservationOrm.asset_type == asset_type)

  if asset_name:
    stmt = stmt.filter(AssetReservationOrm.asset_name == asset_name)

  if status_filter:
    stmt = stmt.filter(AssetReservationOrm.status.in_(status_filter))
  elif active_only:
    stmt = stmt.filter(
      AssetReservationOrm.status.in_(
        [
          AssetReservationStatusEnum.PENDING,
          AssetReservationStatusEnum.RESERVED,
          AssetReservationStatusEnum.ACTIVE,
        ]
      )
    )

  stmt = stmt.order_by(AssetReservationOrm.created_at).offset(offset).limit(limit)

  result = await db.execute(stmt)
  return list(result.scalars().all())


async def update_asset_reservation_status(
  db: AsyncSession,
  reservation_accession_id: uuid.UUID,
  new_status: AssetReservationStatusEnum,
  reserved_at: Optional[datetime] = None,
  released_at: Optional[datetime] = None,
) -> Optional[AssetReservationOrm]:
  """Update the status of an asset reservation.

  Args:
      db (AsyncSession): The database session.
      reservation_accession_id (uuid.UUID): The unique identifier of the
          asset reservation to update.
      new_status (AssetReservationStatusEnum): The new status to set.
      reserved_at (Optional[datetime], optional): Timestamp when reservation
          was made. Defaults to None.
      released_at (Optional[datetime], optional): Timestamp when reservation
          was released. Defaults to None.

  Returns:
      Optional[AssetReservationOrm]: The updated asset reservation, or None
          if not found.

  """
  reservation = await read_asset_reservation(db, reservation_accession_id)
  if not reservation:
    return None

  reservation.status = new_status

  if reserved_at:
    reservation.reserved_at = reserved_at

  if released_at:
    reservation.released_at = released_at

  await db.flush()
  await db.refresh(reservation)

  logger.info(
    "Updated asset reservation %s status to %s",
    reservation_accession_id,
    new_status,
  )

  return reservation


async def cleanup_expired_reservations(
  db: AsyncSession,
  current_time: Optional[datetime] = None,
) -> int:
  """Clean up expired asset reservations.

  Args:
      db (AsyncSession): The database session.
      current_time (Optional[datetime], optional): The current time to compare
          against expiration times. Defaults to None (uses current UTC time).

  Returns:
      int: The number of expired reservations that were cleaned up.

  """
  if current_time is None:
    current_time = datetime.now(timezone.utc)

  stmt = select(AssetReservationOrm).filter(
    and_(
      AssetReservationOrm.expires_at < current_time,
      AssetReservationOrm.status.in_(
        [
          AssetReservationStatusEnum.PENDING,
          AssetReservationStatusEnum.RESERVED,
          AssetReservationStatusEnum.ACTIVE,
        ]
      ),
    )
  )

  result = await db.execute(stmt)
  expired_reservations = list(result.scalars().all())

  count = 0
  for reservation in expired_reservations:
    reservation.status = AssetReservationStatusEnum.EXPIRED
    reservation.released_at = current_time
    count += 1

  if count > 0:
    await db.flush()
    logger.info("Cleaned up %d expired asset reservations", count)

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
  """Log a scheduling event for history and analytics.

  Args:
      db (AsyncSession): The database session.
      schedule_entry_accession_id (uuid.UUID): The schedule entry this event relates to.
      event_type (str): The type of event (e.g., "STATUS_CHANGED", "PRIORITY_CHANGED").
      previous_status (Optional[str], optional): The previous status if applicable.
          Defaults to None.
      new_status (Optional[str], optional): The new status if applicable.
          Defaults to None.
      event_details_json (Optional[Dict[str, Any]], optional): Additional event data.
          Defaults to None.
      error_details_json (Optional[Dict[str, Any]], optional): Error information if
          applicable. Defaults to None.
      message (Optional[str], optional): Human-readable message. Defaults to None.
      duration_ms (Optional[int], optional): Duration of the operation in milliseconds.
          Defaults to None.
      triggered_by (Optional[str], optional): Who or what triggered this event.
          Defaults to None.

  Returns:
      ScheduleHistoryOrm: The created history entry.

  """
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
  """Get scheduling history for a specific schedule entry.

  Args:
      db (AsyncSession): The database session.
      schedule_entry_accession_id (uuid.UUID): The schedule entry to get history for.
      limit (int, optional): Maximum number of results to return. Defaults to 100.
      offset (int, optional): Number of results to skip. Defaults to 0.

  Returns:
      List[ScheduleHistoryOrm]: List of history entries for the schedule entry.

  """
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
  """Get scheduling metrics for a time period.

  Args:
      db (AsyncSession): The database session.
      start_time (datetime): The start of the time period to analyze.
      end_time (datetime): The end of the time period to analyze.

  Returns:
      Dict[str, Any]: Dictionary containing scheduling metrics including status counts,
          average durations, error counts, and total events.

  """
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
  status_counts = {row.to_status: row[1] for row in status_result}

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
    "total_events": (sum(list(status_counts.values())) if status_counts else 0),
  }
