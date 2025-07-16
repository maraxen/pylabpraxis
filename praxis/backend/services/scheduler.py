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
from typing import Any, cast

from sqlalchemy import and_, asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import InstrumentedAttribute

from praxis.backend.models.enums import AssetType, ScheduleStatusEnum, ScheduleHistoryEventEnum, ScheduleHistoryEventTriggerEnum
from praxis.backend.models.orm.schedule import (
  AssetReservationOrm,
  AssetReservationStatusEnum,
  ScheduleEntryOrm,
  ScheduleHistoryOrm,
  ScheduleStatusEnum,
)
from praxis.backend.models.pydantic.filters import SearchFilters
from praxis.backend.models.pydantic.scheduler import (
  ScheduleEntryCreate,
  ScheduleEntryStatus,
  ScheduleEntryUpdate,
)
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.services.utils.query_builder import (
  apply_date_range_filters,
  apply_pagination,
)
from praxis.backend.utils.db_decorator import handle_db_transaction
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


class ScheduleEntryCRUDService(
  CRUDBase[ScheduleEntryOrm, ScheduleEntryCreate, ScheduleEntryUpdate],
):
  """CRUD service for schedule entries."""

  @handle_db_transaction
  async def create(
    self,
    db: AsyncSession,
    *,
    obj_in: ScheduleEntryCreate,
  ) -> ScheduleEntryOrm:
    """Create a new schedule entry for a protocol run."""
    log_prefix = (
      f"Schedule Entry (Protocol Run: '{obj_in.protocol_run_accession_id}', creating new):"
    )
    logger.info("%s Attempting to create new schedule entry.", log_prefix)

    # Check if a schedule entry for this protocol run already exists
    existing_entry = await db.execute(
      select(self.model).filter(
        self.model.protocol_run_accession_id == obj_in.protocol_run_accession_id,
      ),
    )
    if existing_entry.scalar_one_or_none():
      error_message = (
        f"{log_prefix} A schedule entry for protocol run "
        f"'{obj_in.protocol_run_accession_id}' already exists. Use the update function for "
        f"existing schedule entries."
      )
      logger.error(error_message)
      raise ValueError(error_message)

    # Create a new ScheduleEntryOrm
    schedule_entry = self.model(
      **obj_in.model_dump(),
      status=ScheduleStatusEnum.QUEUED,
    )
    db.add(schedule_entry)
    logger.info("%s Initialized new schedule entry for creation.", log_prefix)

    await db.flush()
    logger.debug("%s Flushed new schedule entry to get ID.", log_prefix)

    # Log the scheduling event
    await log_schedule_event(
      db,
      schedule_entry.accession_id,
      ScheduleHistoryEventEnum.SCHEDULE_CREATED,
      new_status=ScheduleStatusEnum.QUEUED,
      event_details_json={"priority": schedule_entry.priority},
    )

    await db.refresh(schedule_entry)

    logger.info(
      "%s Successfully created schedule entry %s for protocol run %s",
      log_prefix,
      schedule_entry.accession_id,
      schedule_entry.protocol_run_accession_id,
    )

    return schedule_entry

  async def get_multi(
    self,
    db: AsyncSession,
    *,
    filters: SearchFilters,
  ) -> list[ScheduleEntryOrm]:
    """List schedule entries with optional filters."""
    stmt = select(self.model)

    # Apply generic filters from query_builder
    stmt = apply_date_range_filters(
      stmt,
      filters,
      cast(InstrumentedAttribute, self.model.created_at),
    )
    stmt = apply_pagination(stmt, filters)

    # Apply ordering
    order_col = self.model.created_at
    order_desc = True

    if filters.sort_by:
      if filters.sort_by == "created_at":
        order_col = self.model.created_at
      elif filters.sort_by == "priority":
        order_col = self.model.priority
      elif filters.sort_by == "scheduled_at":
        order_col = self.model.scheduled_at

      if filters.sort_by.endswith("_asc"):
        order_desc = False
      elif filters.sort_by.endswith("_desc"):
        order_desc = True

    stmt = stmt.order_by(desc(order_col)) if order_desc else stmt.order_by(asc(order_col))

    # Include reservations
    stmt = stmt.options(selectinload(self.model.asset_reservations))

    result = await db.execute(stmt)
    return list(result.scalars().all())

  async def update_status(
    self,
    db: AsyncSession,
    schedule_entry_accession_id: uuid.UUID,
    new_status: ScheduleStatusEnum,
    error_details: str | None = None,
    started_at: datetime | None = None,
    completed_at: datetime | None = None,
  ) -> ScheduleEntryOrm | None:
    """Update the status of a schedule entry."""
    schedule_entry = await self.get(db, schedule_entry_accession_id)
    if not schedule_entry:
      return None

    previous_status = schedule_entry.status
    update_schema = ScheduleEntryUpdate(
      status=ScheduleEntryStatus(new_status.value),
      last_error_message=error_details,
      execution_started_at=started_at,
      execution_completed_at=completed_at,
    )
    updated_entry = await self.update(db, db_obj=schedule_entry, obj_in=update_schema)

    # Log the status change
    await log_schedule_event(
      db,
      schedule_entry_accession_id,
      ScheduleHistoryEventEnum.STATUS_CHANGED,
      previous_status=previous_status,
      new_status=new_status,
      event_details_json={"error_details": error_details},
    )

    logger.info(
      "Updated schedule entry %s status: %s -> %s",
      schedule_entry_accession_id,
      previous_status,
      new_status,
    )

    return updated_entry

  async def update_priority(
    self,
    db: AsyncSession,
    schedule_entry_accession_id: uuid.UUID,
    new_priority: int,
    reason: str | None = None,
  ) -> ScheduleEntryOrm | None:
    """Update the priority of a schedule entry."""
    schedule_entry = await self.get(db, schedule_entry_accession_id)
    if not schedule_entry:
      return None

    old_priority = schedule_entry.priority
    update_schema = ScheduleEntryUpdate(priority=new_priority)
    updated_entry = await self.update(db, db_obj=schedule_entry, obj_in=update_schema)

    # Log the priority change
    await log_schedule_event(
      db,
      schedule_entry_accession_id,
      ScheduleHistoryEventEnum.PRIORITY_CHANGED,
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

    return updated_entry


schedule_entry_service = ScheduleEntryCRUDService(ScheduleEntryOrm)


# Asset Reservation Services


@handle_db_transaction
async def create_asset_reservation(
  db: AsyncSession,
  schedule_entry_accession_id: uuid.UUID,
  asset_type: AssetType,
  asset_name: str,
  protocol_run_accession_id: uuid.UUID,
  asset_accession_id: uuid.UUID,
  redis_lock_key: str | None = None,
  redis_lock_value: str | None = None,
  required_capabilities_json: dict[str, Any] | None = None,
  estimated_duration_ms: int | None = None,
  expires_at: datetime | None = None,
) -> AssetReservationOrm:
  """Create a new asset reservation."""
  log_prefix = f"Asset Reservation (Asset: '{asset_type}:{asset_name}', creating new):"
  logger.info("%s Attempting to create new asset reservation.", log_prefix)

  reservation = AssetReservationOrm(
    name=asset_name,
    asset_type=asset_type,
    asset_name=asset_name,
    schedule_entry_accession_id=schedule_entry_accession_id,
    protocol_run_accession_id=protocol_run_accession_id,
    asset_accession_id=asset_accession_id,
    released_at=None,
    status=AssetReservationStatusEnum.PENDING,
    redis_lock_key=redis_lock_key or f"asset:{asset_type}:{asset_name}",
    redis_lock_value=redis_lock_value or str(uuid7()),
    required_capabilities_json=required_capabilities_json,
    estimated_usage_duration_ms=estimated_duration_ms,
    expires_at=expires_at,
  )
  logger.info("%s Initialized new asset reservation for creation.", log_prefix)

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


async def read_asset_reservation(
  db: AsyncSession,
  reservation_accession_id: uuid.UUID,
) -> AssetReservationOrm | None:
  """Read an asset reservation by ID."""
  stmt = select(AssetReservationOrm).filter(
    AssetReservationOrm.accession_id == reservation_accession_id,
  )

  result = await db.execute(stmt)
  return result.scalar_one_or_none()


async def list_asset_reservations(
  db: AsyncSession,
  schedule_entry_accession_id: uuid.UUID | None = None,
  asset_type: str | None = None,
  asset_name: str | None = None,
  status_filter: list[AssetReservationStatusEnum] | None = None,
  active_only: bool = False,
) -> list[AssetReservationOrm]:
  """List asset reservations with optional filters."""
  stmt = select(AssetReservationOrm)

  if schedule_entry_accession_id:
    stmt = stmt.filter(
      AssetReservationOrm.schedule_entry_accession_id == schedule_entry_accession_id,
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
        ],
      ),
    )

  stmt = stmt.order_by(AssetReservationOrm.created_at)

  result = await db.execute(stmt)
  return list(result.scalars().all())


@handle_db_transaction
async def update_asset_reservation_status(
  db: AsyncSession,
  reservation_accession_id: uuid.UUID,
  new_status: AssetReservationStatusEnum,
  reserved_at: datetime | None = None,
  released_at: datetime | None = None,
) -> AssetReservationOrm | None:
  """Update the status of an asset reservation."""
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


@handle_db_transaction
async def cleanup_expired_reservations(
  db: AsyncSession,
  current_time: datetime | None = None,
) -> int:
  """Clean up expired asset reservations."""
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
        ],
      ),
    ),
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


@handle_db_transaction
async def log_schedule_event(
  db: AsyncSession,
  schedule_entry_accession_id: uuid.UUID,
  event_type: ScheduleHistoryEventEnum,
  previous_status: ScheduleStatusEnum | None = None,
  new_status: ScheduleStatusEnum | None = None,
  event_details_json: dict[str, Any] | None = None,
  error_details_json: dict[str, Any] | None = None,
  event_end: datetime | None = None,
  message: str | None = None,
  name: str | None = None,
  duration_ms: int | None = None,
  triggered_by: ScheduleHistoryEventTriggerEnum | None = None,
) -> ScheduleHistoryOrm:
  """Log a scheduling event for history and analytics."""
  if name is None:
    name = "Unnamed Event"
  history_entry = ScheduleHistoryOrm(
    name=name,
    schedule_entry_accession_id=schedule_entry_accession_id,
    event_type=event_type,
    event_end=event_end,
    from_status=previous_status,
    to_status=new_status,
    event_data_json=event_details_json,
    error_details=str(error_details_json) if error_details_json else None,
    message=message,
    override_duration_ms=duration_ms,
    triggered_by=triggered_by or ScheduleHistoryEventTriggerEnum.SYSTEM,
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
) -> list[ScheduleHistoryOrm]:
  """Get scheduling history for a specific schedule entry."""
  stmt = (
    select(ScheduleHistoryOrm)
    .filter(
      ScheduleHistoryOrm.schedule_entry_accession_id == schedule_entry_accession_id,
    )
    .order_by(desc(ScheduleHistoryOrm.created_at))
    .offset(offset)
    .limit(limit)
  )

  result = await db.execute(stmt)
  return list(result.scalars().all())


async def get_scheduling_metrics(
  db: AsyncSession,
  start_time: datetime,
  end_time: datetime,
) -> dict[str, Any]:
  """Get scheduling metrics for a time period."""
  # Get status counts
  status_count_stmt = (
    select(ScheduleHistoryOrm.to_status, func.count().label("count"))
    .filter(
      and_(
        ScheduleHistoryOrm.created_at >= start_time,
        ScheduleHistoryOrm.created_at <= end_time,
      ),
    )
    .group_by(ScheduleHistoryOrm.to_status)
  )

  status_result = await db.execute(status_count_stmt)
  status_counts = {row.to_status: row[1] for row in status_result}

  # Get average timing metrics
  avg_stmt = select(
    func.avg(ScheduleHistoryOrm.accession_id).label("avg_duration"),
  ).filter(
    and_(
      ScheduleHistoryOrm.created_at >= start_time,
      ScheduleHistoryOrm.created_at <= end_time,
    ),
  )

  avg_result = await db.execute(avg_stmt)
  avg_data = avg_result.first()

  # Get error count
  error_count_stmt = select(func.count()).filter(
    and_(
      ScheduleHistoryOrm.created_at >= start_time,
      ScheduleHistoryOrm.created_at <= end_time,
      ScheduleHistoryOrm.error_details.isnot(None),
    ),
  )

  error_result = await db.execute(error_count_stmt)
  error_count = error_result.scalar()

  return {
    "status_counts": status_counts,
    "avg_duration_ms": avg_data.avg_duration if avg_data else None,
    "error_count": error_count,
    "total_events": (sum(list(status_counts.values())) if status_counts else 0),
  }
