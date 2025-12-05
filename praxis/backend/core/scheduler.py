# pylint: disable=too-many-arguments,fixme
"""Protocol Scheduler - Manages protocol execution scheduling and asset allocation."""

import uuid
from datetime import datetime, timezone
from typing import Any, Protocol

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from praxis.backend.models.orm.protocol import (
  FunctionProtocolDefinitionOrm,
  ProtocolRunOrm,
  ProtocolRunStatusEnum,
)
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

    self._active_schedules: dict[uuid.UUID, ScheduleEntry] = {}
    self._asset_reservations: dict[str, set[uuid.UUID]] = {}
    logger.info("ProtocolScheduler initialized.")

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
        accession_id=uuid.uuid4(),
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
  ) -> bool:
    """Reserve assets for a protocol run."""
    logger.info(
      "Attempting to reserve %d assets for run %s",
      len(requirements),
      protocol_run_id,
    )

    reserved_assets: list[str] = []

    try:
      for requirement in requirements:
        asset_key = f"{requirement.asset_type}:{requirement.asset_definition.name}"
        if asset_key not in self._asset_reservations:
          self._asset_reservations[asset_key] = set()

        if self._asset_reservations[asset_key]:
          error_msg = (
            f"Asset {asset_key} is already reserved by runs: {self._asset_reservations[asset_key]}"
          )
          logger.warning(error_msg)
          await self._release_reservations(reserved_assets, protocol_run_id)
          raise AssetAcquisitionError(error_msg)

        self._asset_reservations[asset_key].add(protocol_run_id)
        requirement.reservation_id = uuid.uuid4()
        reserved_assets.append(asset_key)
        logger.debug(
          "Reserved asset %s for run %s (reservation: %s)",
          asset_key,
          protocol_run_id,
          requirement.reservation_id,
        )

      logger.info(
        "Successfully reserved all %d assets for run %s",
        len(requirements),
        protocol_run_id,
      )
      return True

    except AssetAcquisitionError:
      raise
    except Exception as e:
      logger.exception(
        "Error during asset reservation for run %s",
        protocol_run_id,
      )
      await self._release_reservations(reserved_assets, protocol_run_id)
      msg = f"Unexpected error during asset reservation: {e!s}"
      raise AssetAcquisitionError(msg) from e

  async def _release_reservations(
    self,
    asset_keys: list[str],
    protocol_run_id: uuid.UUID,
  ) -> None:
    """Release asset reservations for a protocol run."""
    for asset_key in asset_keys:
      if asset_key in self._asset_reservations:
        self._asset_reservations[asset_key].discard(protocol_run_id)
        if not self._asset_reservations[asset_key]:
          del self._asset_reservations[asset_key]
        logger.debug("Released reservation for asset %s", asset_key)

  async def schedule_protocol_execution(
    self,
    protocol_run_orm: ProtocolRunOrm,
    user_params: dict[str, Any],
    initial_state: dict[str, Any] | None = None,
  ) -> bool:
    """Schedule a protocol for execution."""
    logger.info(
      "Scheduling protocol execution for run %s (%s)",
      protocol_run_orm.accession_id,
      protocol_run_orm.top_level_protocol_definition.name
      if protocol_run_orm.top_level_protocol_definition
      else "Unknown",
    )

    try:
      async with self.db_session_factory() as db_session:
        protocol_def = protocol_run_orm.top_level_protocol_definition
        if not protocol_def:
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
      if isinstance(e, (AssetAcquisitionError, OrchestratorError)):
        raise
      msg = f"Failed to schedule protocol execution: {e!s}"
      raise OrchestratorError(msg) from e

  async def _queue_execution_task(
    self,
    protocol_run_id: uuid.UUID,
    user_params: dict[str, Any],
    initial_state: dict[str, Any] | None,
  ) -> bool:
    """Queue a protocol execution task using Celery."""
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

    except Exception:
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
        if asset_key in self._asset_reservations:
          self._asset_reservations[asset_key].discard(protocol_run_id)
          if not self._asset_reservations[asset_key]:
            del self._asset_reservations[asset_key]

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
