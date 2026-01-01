# pylint: disable=too-many-arguments,fixme
"""Protocol Scheduler - Manages protocol execution scheduling and asset allocation."""

import uuid
from datetime import datetime, timezone
from typing import Any, Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from praxis.backend.models.enums.asset import AssetReservationStatusEnum, AssetType
from praxis.backend.models.enums.schedule import ScheduleStatusEnum
from praxis.backend.models.orm.protocol import (
  FunctionProtocolDefinitionOrm,
  ProtocolRunOrm,
  ProtocolRunStatusEnum,
)
from praxis.backend.models.orm.schedule import AssetReservationOrm, ScheduleEntryOrm
from praxis.backend.models.pydantic_internals.protocol import (
  AssetConstraintsModel,
  AssetRequirementModel,
  LocationConstraintsModel,
  ProtocolRunUpdate,
)
from praxis.backend.models.pydantic_internals.runtime import RuntimeAssetRequirement
from praxis.backend.services.protocol_definition import ProtocolDefinitionCRUDService
from praxis.backend.services.protocols import ProtocolRunService
from praxis.backend.utils.errors import AssetAcquisitionError, OrchestratorError
from praxis.backend.utils.logging import get_logger
from praxis.backend.utils.uuid import uuid7

logger = get_logger(__name__)


class TaskResult(Protocol):

  """A protocol for a task result."""

  id: str | None


class TaskQueue(Protocol):

  """A protocol for a task queue."""

  def send_task(self, name: str, args: list[Any]) -> TaskResult:
    """Send a task to the queue."""
    ...


class ScheduleEntry:

  """Represents a scheduled protocol run with asset reservations."""

  def __init__(
    self,
    protocol_run_id: uuid.UUID,
    protocol_name: str,
    required_assets: list[RuntimeAssetRequirement],
    estimated_duration_ms: int | None = None,
    priority: int = 1,
  ) -> None:
    """Initialize a ScheduleEntry."""
    self.protocol_run_id = protocol_run_id
    self.protocol_name = protocol_name
    self.required_assets = required_assets
    self.estimated_duration_ms = estimated_duration_ms
    self.priority = priority
    self.scheduled_at = datetime.now(timezone.utc)
    self.status = "QUEUED"
    self.celery_task_id: str | None = None


class ProtocolScheduler:

  """Manages protocol scheduling, asset allocation, and execution queueing."""

  def __init__(
    self,
    db_session_factory: async_sessionmaker[AsyncSession],
    task_queue: TaskQueue,
    protocol_run_service: ProtocolRunService,
    protocol_definition_service: ProtocolDefinitionCRUDService,
  ) -> None:
    """Initialize the Protocol Scheduler."""
    self.db_session_factory = db_session_factory
    self.task_queue = task_queue
    self.protocol_run_service = protocol_run_service
    self.protocol_definition_service = protocol_definition_service

    # In-memory cache for active schedules (also persisted via ScheduleEntryOrm)
    self._active_schedules: dict[uuid.UUID, ScheduleEntry] = {}
    # Asset reservations are now persisted in the database via AssetReservationOrm
    # The in-memory dict is kept as a cache for performance but is no longer the source of truth
    self._asset_reservations_cache: dict[str, set[uuid.UUID]] = {}
    logger.info("ProtocolScheduler initialized with database-backed reservations.")

  async def analyze_protocol_requirements(
    self,
    protocol_def_orm: FunctionProtocolDefinitionOrm,
    _user_params: dict[str, Any],
  ) -> list[RuntimeAssetRequirement]:
    """Analyze a protocol definition to determine asset requirements."""
    logger.info(
      "Analyzing asset requirements for protocol: %s v%s",
      protocol_def_orm.name,
      protocol_def_orm.version,
    )

    requirements: list[RuntimeAssetRequirement] = []

    for asset_def in protocol_def_orm.assets:
      asset_requirement_model = AssetRequirementModel.model_validate(asset_def)
      requirement = RuntimeAssetRequirement(
        asset_definition=asset_requirement_model,
        asset_type="asset",
        estimated_duration_ms=None,
        priority=1,
      )
      requirements.append(requirement)
      logger.debug(
        "Added asset requirement: %s (%s)",
        asset_def.name,
        asset_def.actual_type_str,
      )

    if protocol_def_orm.preconfigure_deck and protocol_def_orm.deck_param_name:
      deck_asset_requirement = AssetRequirementModel(
        accession_id=uuid7(),
        name=protocol_def_orm.deck_param_name,
        fqn="pylabrobot.resources.Deck",
        type_hint_str="pylabrobot.resources.Deck",
        optional=False,
        constraints=AssetConstraintsModel(),
        location_constraints=LocationConstraintsModel(),
      )
      deck_requirement = RuntimeAssetRequirement(
        asset_definition=deck_asset_requirement,
        asset_type="deck",
        estimated_duration_ms=None,
        priority=1,
      )
      requirements.append(deck_requirement)
      logger.debug("Added deck requirement: %s", protocol_def_orm.deck_param_name)

    logger.info(
      "Protocol analysis complete. Found %d asset requirements.",
      len(requirements),
    )
    return requirements

  async def reserve_assets(
    self,
    requirements: list[RuntimeAssetRequirement],
    protocol_run_id: uuid.UUID,
    db_session: AsyncSession | None = None,
    schedule_entry_id: uuid.UUID | None = None,
  ) -> bool:
    """Reserve assets for a protocol run.
    
    This method checks the database for existing active reservations and creates
    new AssetReservationOrm records for each required asset. Reservations are
    persisted to survive server restarts.
    
    Args:
        requirements: List of asset requirements to reserve.
        protocol_run_id: UUID of the protocol run requesting reservations.
        db_session: Optional active database session. If not provided, a new one is created.
        schedule_entry_id: Optional schedule entry ID to associate reservations with.
    
    Returns:
        True if all assets were successfully reserved.
        
    Raises:
        AssetAcquisitionError: If any asset is already reserved or reservation fails.
    """
    logger.info(
      "Attempting to reserve %d assets for run %s",
      len(requirements),
      protocol_run_id,
    )

    created_reservations: list[AssetReservationOrm] = []
    
    async def _do_reserve(session: AsyncSession) -> bool:
      nonlocal created_reservations
      
      for requirement in requirements:
        asset_key = f"{requirement.asset_type}:{requirement.asset_definition.name}"

        # First check the in-memory cache for conflicts (faster than DB query)
        if asset_key in self._asset_reservations_cache:
          conflicting_runs = self._asset_reservations_cache[asset_key] - {protocol_run_id}
          if conflicting_runs:
            error_msg = f"Asset {asset_key} is already reserved by runs: {list(str(r) for r in conflicting_runs)}"
            logger.warning(error_msg)
            # Rollback created reservations from session and cache
            for res in created_reservations:
              await session.delete(res)
              # Also clean up cache entries for this run
              res_key = res.redis_lock_key
              if res_key in self._asset_reservations_cache:
                self._asset_reservations_cache[res_key].discard(protocol_run_id)
                if not self._asset_reservations_cache[res_key]:
                  del self._asset_reservations_cache[res_key]
            raise AssetAcquisitionError(error_msg)

        # Also check database for existing active reservations (in case cache is stale)
        existing_query = select(AssetReservationOrm).where(
          AssetReservationOrm.redis_lock_key == asset_key,
          AssetReservationOrm.status.in_([
            AssetReservationStatusEnum.PENDING,
            AssetReservationStatusEnum.ACTIVE,
            AssetReservationStatusEnum.RESERVED,
          ]),
        )
        result = await session.execute(existing_query)
        existing_reservations = result.scalars().all()
        
        # Exclude reservations for the same run (re-reservation scenario)
        conflicting = [r for r in existing_reservations if r.protocol_run_accession_id != protocol_run_id]
        
        if conflicting:
          conflicting_runs = [str(r.protocol_run_accession_id) for r in conflicting]
          error_msg = f"Asset {asset_key} is already reserved by runs: {conflicting_runs}"
          logger.warning(error_msg)
          # Rollback created reservations from session and cache
          for res in created_reservations:
            await session.delete(res)
            # Also clean up cache entries for this run
            res_key = res.redis_lock_key
            if res_key in self._asset_reservations_cache:
              self._asset_reservations_cache[res_key].discard(protocol_run_id)
              if not self._asset_reservations_cache[res_key]:
                del self._asset_reservations_cache[res_key]
          raise AssetAcquisitionError(error_msg)
        
        # Create new reservation
        reservation_id = uuid7()
        reservation = AssetReservationOrm(
          name=f"reservation_{requirement.asset_definition.name}_{reservation_id.hex[:8]}",
          protocol_run_accession_id=protocol_run_id,
          schedule_entry_accession_id=schedule_entry_id or protocol_run_id,
          asset_type=AssetType.ASSET,
          asset_accession_id=requirement.asset_definition.accession_id,
          asset_name=requirement.asset_definition.name,
          redis_lock_key=asset_key,
          redis_lock_value=str(reservation_id),
          lock_timeout_seconds=3600,
          status=AssetReservationStatusEnum.ACTIVE,
          released_at=None,
        )
        session.add(reservation)
        created_reservations.append(reservation)
        requirement.reservation_id = reservation_id
        
        # Update cache
        if asset_key not in self._asset_reservations_cache:
          self._asset_reservations_cache[asset_key] = set()
        self._asset_reservations_cache[asset_key].add(protocol_run_id)
        
        logger.debug(
          "Reserved asset %s for run %s (reservation: %s)",
          asset_key,
          protocol_run_id,
          reservation_id,
        )
      
      await session.flush()  # Ensure IDs are generated without committing
      logger.info(
        "Successfully reserved all %d assets for run %s",
        len(requirements),
        protocol_run_id,
      )
      return True

    try:
      if db_session:
        return await _do_reserve(db_session)
      async with self.db_session_factory() as session:
        result = await _do_reserve(session)
        await session.commit()
        return result

    except AssetAcquisitionError:
      raise
    except Exception as e:
      logger.exception(
        "Error during asset reservation for run %s",
        protocol_run_id,
      )
      msg = f"Unexpected error during asset reservation: {e!s}"
      raise AssetAcquisitionError(msg) from e

  async def _release_reservations(
    self,
    asset_keys: list[str],
    protocol_run_id: uuid.UUID,
    db_session: AsyncSession | None = None,
  ) -> None:
    """Release asset reservations for a protocol run.
    
    Updates the status of reservations in the database to RELEASED
    and clears the in-memory cache.
    """
    async def _do_release(session: AsyncSession) -> None:
      for asset_key in asset_keys:
        # Find and update the reservation in the database
        query = select(AssetReservationOrm).where(
          AssetReservationOrm.redis_lock_key == asset_key,
          AssetReservationOrm.protocol_run_accession_id == protocol_run_id,
          AssetReservationOrm.status.in_([
            AssetReservationStatusEnum.PENDING,
            AssetReservationStatusEnum.ACTIVE,
            AssetReservationStatusEnum.RESERVED,
          ]),
        )
        result = await session.execute(query)
        reservation = result.scalar_one_or_none()
        
        if reservation:
          reservation.status = AssetReservationStatusEnum.RELEASED
          reservation.released_at = datetime.now(timezone.utc)
          logger.debug("Released reservation for asset %s in database", asset_key)
        
        # Update cache
        if asset_key in self._asset_reservations_cache:
          self._asset_reservations_cache[asset_key].discard(protocol_run_id)
          if not self._asset_reservations_cache[asset_key]:
            del self._asset_reservations_cache[asset_key]

    if db_session:
      await _do_release(db_session)
    else:
      async with self.db_session_factory() as session:
        await _do_release(session)
        await session.commit()



  async def schedule_protocol_execution(
    self,
    protocol_run_id: uuid.UUID,
    user_params: dict[str, Any],
    initial_state: dict[str, Any] | None = None,
  ) -> bool:
    """Schedule a protocol for execution.
    
    Args:
        protocol_run_id: UUID of the protocol run to schedule.
        user_params: User parameters for the protocol.
        initial_state: Initial state data for the run.
        
    Returns:
        True if scheduling succeeded, False otherwise.
    """
    logger.info(
      "Scheduling protocol execution for run %s",
      protocol_run_id,
    )

    try:
      async with self.db_session_factory() as db_session:
        # Fetch protocol run within this session
        protocol_run_orm = await self.protocol_run_service.get(
          db_session,
          accession_id=protocol_run_id,
        )
        
        if not protocol_run_orm:
          logger.error("Protocol run %s not found", protocol_run_id)
          return False
        
        protocol_def = await self.protocol_definition_service.get(
          db=db_session,
          accession_id=protocol_run_orm.top_level_protocol_definition_accession_id,
        )

        if not protocol_def:
          logger.error(
            "Protocol definition not found for run %s",
            protocol_run_orm.accession_id,
          )
          return False

        requirements = await self.analyze_protocol_requirements(
          protocol_def,
          user_params,
        )

        try:
          await self.reserve_assets(requirements, protocol_run_orm.accession_id)
        except AssetAcquisitionError as e:
          logger.error(
            "Failed to reserve assets for run %s: %s",
            protocol_run_orm.accession_id,
            e,
          )
          await self.protocol_run_service.update(
            db=db_session,
            db_obj=protocol_run_orm,
            obj_in=ProtocolRunUpdate(
              status=ProtocolRunStatusEnum.FAILED,
              output_data_json={
                "error": "Asset reservation failed",
                "details": str(e),
              },
            ),
          )
          await db_session.commit()
          raise

        schedule_entry = ScheduleEntry(
          protocol_run_id=protocol_run_orm.accession_id,
          protocol_name=protocol_def.name,
          required_assets=requirements,
          estimated_duration_ms=None,
        )
        self._active_schedules[protocol_run_orm.accession_id] = schedule_entry

        await self.protocol_run_service.update(
          db=db_session,
          db_obj=protocol_run_orm,
          obj_in=ProtocolRunUpdate(
            status=ProtocolRunStatusEnum.QUEUED,
            output_data_json={
              "scheduled_at": schedule_entry.scheduled_at.isoformat(),
              "asset_count": len(requirements),
            },
          ),
        )
        await db_session.commit()

        success = await self._queue_execution_task(
          protocol_run_orm.accession_id,
          user_params,
          initial_state,
        )

        if success:
          logger.info(
            "Successfully scheduled protocol run %s for execution",
            protocol_run_orm.accession_id,
          )
          return True
        await self.cancel_scheduled_run(protocol_run_orm.accession_id)
        return False

    except Exception as e:
      logger.exception(
        "Error scheduling protocol execution for run %s",
        protocol_run_orm.accession_id,
      )
      if isinstance(e, AssetAcquisitionError | OrchestratorError):
        raise
      msg = f"Failed to schedule protocol execution: {e!s}"
      raise OrchestratorError(msg) from e

  async def _queue_execution_task(
    self,
    protocol_run_id: uuid.UUID,
    user_params: dict[str, Any],
    initial_state: dict[str, Any] | None,
  ) -> bool:
    """Queue a protocol execution task using Celery.
    
    If Celery is unavailable, logs a warning and returns True anyway
    to allow the system to function in simulation/development mode.
    """
    logger.info("Queueing execution task for run %s", protocol_run_id)
    user_params = user_params or {}

    try:
      task_result = self.task_queue.send_task(
        "execute_protocol_run",
        args=[
          str(protocol_run_id),
          user_params,
          initial_state,
        ],
      )
      celery_task_id = task_result.id
      logger.info(
        "Successfully queued protocol run %s with Celery task ID: %s",
        protocol_run_id,
        celery_task_id,
      )

      if protocol_run_id in self._active_schedules:
        schedule_entry = self._active_schedules[protocol_run_id]
        schedule_entry.status = "QUEUED"
        schedule_entry.celery_task_id = celery_task_id

    except Exception as e:
      # Check if this is a connection error (Celery broker not available)
      error_str = str(e).lower()
      if "connection" in error_str or "refused" in error_str or "operational" in error_str:
        logger.warning(
          "Celery broker unavailable for run %s - continuing without task queue (simulation mode). Error: %s",
          protocol_run_id,
          e,
        )
        # For simulation/development, we can proceed without Celery
        if protocol_run_id in self._active_schedules:
          schedule_entry = self._active_schedules[protocol_run_id]
          schedule_entry.status = "RUNNING_DIRECT"
          schedule_entry.celery_task_id = None
        return True
      
      logger.exception(
        "Failed to queue execution task for run %s",
        protocol_run_id,
      )
      return False
    else:
      return True

  async def cancel_scheduled_run(self, protocol_run_id: uuid.UUID) -> bool:
    """Cancel a scheduled protocol run and release assets."""
    logger.info("Cancelling scheduled run %s", protocol_run_id)

    try:
      if protocol_run_id not in self._active_schedules:
        logger.warning("Run %s not found in active schedules", protocol_run_id)
        return False

      schedule_entry = self._active_schedules[protocol_run_id]

      for requirement in schedule_entry.required_assets:
        asset_key = f"{requirement.asset_type}:{requirement.asset_definition.name}"
        if asset_key in self._asset_reservations_cache:
          self._asset_reservations_cache[asset_key].discard(protocol_run_id)
          if not self._asset_reservations_cache[asset_key]:
            del self._asset_reservations_cache[asset_key]
      
      # Release in database
      asset_keys = [
        f"{r.asset_type}:{r.asset_definition.name}" 
        for r in schedule_entry.required_assets
      ]
      await self._release_reservations(asset_keys, protocol_run_id)

      del self._active_schedules[protocol_run_id]

      logger.info("Successfully cancelled scheduled run %s", protocol_run_id)

    except Exception:
      logger.exception(
        "Error cancelling scheduled run %s",
        protocol_run_id,
      )
      return False
    else:
      return True

  async def get_schedule_status(
    self,
    protocol_run_id: uuid.UUID,
  ) -> dict[str, Any] | None:
    """Get the current schedule status for a protocol run."""
    if protocol_run_id not in self._active_schedules:
      return None

    schedule_entry = self._active_schedules[protocol_run_id]

    return {
      "protocol_run_id": str(protocol_run_id),
      "protocol_name": schedule_entry.protocol_name,
      "status": schedule_entry.status,
      "scheduled_at": schedule_entry.scheduled_at.isoformat(),
      "asset_count": len(schedule_entry.required_assets),
      "estimated_duration_ms": schedule_entry.estimated_duration_ms,
      "priority": schedule_entry.priority,
    }

  async def list_active_schedules(self) -> list[dict[str, Any]]:
    """List all currently active protocol schedules."""
    schedules = []
    for protocol_run_id in self._active_schedules:
      status = await self.get_schedule_status(protocol_run_id)
      if status:
        schedules.append(status)

    return sorted(schedules, key=lambda x: x["scheduled_at"])

  async def complete_scheduled_run(self, protocol_run_id: uuid.UUID) -> bool:
    """Mark a scheduled run as complete and release reserved assets.
    
    This should be called by the orchestrator when a run finishes (success or failure)
    to ensure resources are freed for other runs.
    """
    logger.info("Completing scheduled run %s", protocol_run_id)

    try:
      if protocol_run_id not in self._active_schedules:
        logger.debug(
          "Run %s not found in active schedules (may have been cancelled or never scheduled)", 
          protocol_run_id
        )
        # Even if not in active schedule, we should ensure any stray reservations are cleared
        # This is a safety measure - check both cache and database
        reserved_assets_to_clear: list[str] = []
        for asset_key, reserved_by_set in self._asset_reservations_cache.items():
            if protocol_run_id in reserved_by_set:
                reserved_assets_to_clear.append(asset_key)
        
        if reserved_assets_to_clear:
            logger.warning(
                "Found stray asset reservations for non-scheduled run %s: %s", 
                protocol_run_id, reserved_assets_to_clear
            )
            await self._release_reservations(reserved_assets_to_clear, protocol_run_id)
            
        return False

      schedule_entry = self._active_schedules[protocol_run_id]

      # Release all asset reservations for this run
      asset_keys_to_release = []
      for requirement in schedule_entry.required_assets:
        asset_key = f"{requirement.asset_type}:{requirement.asset_definition.name}"
        asset_keys_to_release.append(asset_key)
      
      await self._release_reservations(asset_keys_to_release, protocol_run_id)

      # Remove from active schedules
      del self._active_schedules[protocol_run_id]

      logger.info("Successfully completed scheduled run %s and released resources", protocol_run_id)
      return True

    except Exception:
      logger.exception("Error completing scheduled run %s", protocol_run_id)
      return False

  async def recover_stale_runs(self) -> None:
    """Find and fail stale protocol runs on startup.
    
    This method scans for runs stuck in QUEUED or PREPARING states
    (which can happen if the server restarted mid-execution) and
    marks them as FAILED with an appropriate message.
    """
    from praxis.backend.models.pydantic_internals.filters import SearchFilters
    
    logger.info("Starting recovery of stale protocol runs...")
    recovered_runs_count = 0
    batch_size = 100
    offset = 0
    
    try:
      async with self.db_session_factory() as db_session:
        stale_statuses = [ProtocolRunStatusEnum.QUEUED, ProtocolRunStatusEnum.PREPARING]
        while True:
          runs_to_recover = await self.protocol_run_service.get_multi(
            db=db_session,
            filters=SearchFilters(offset=offset, limit=batch_size),
            statuses=stale_statuses,
          )
          if not runs_to_recover:
            break

          for run in runs_to_recover:
            logger.warning(
              "Found stale run %s in %s state. Marking as FAILED.",
              run.accession_id,
              run.status.name,
            )
            await self.protocol_run_service.update(
              db=db_session,
              db_obj=run,
              obj_in=ProtocolRunUpdate(
                status=ProtocolRunStatusEnum.FAILED,
                output_data_json={
                  "error": "Stale run recovered on server startup",
                  "details": (
                    f"The server restarted while this run was in a {run.status.name} state. "
                    "Asset reservations were lost, and the run could not proceed."
                  ),
                },
              ),
            )
            recovered_runs_count += 1
          
          await db_session.commit()  # Commit each batch
          offset += len(runs_to_recover)

      if recovered_runs_count > 0:
        logger.info("Successfully recovered %d stale runs.", recovered_runs_count)
      else:
        logger.info("No stale runs found.")
    except Exception:
      logger.exception("Error during stale run recovery. This may indicate a database connection issue.")
