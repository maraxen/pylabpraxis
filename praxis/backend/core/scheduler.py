# pylint: disable=too-many-arguments,fixme
"""Protocol Scheduler - Manages protocol execution scheduling and asset allocation.
# broad-except is justified at method level.

This module provides the scheduling layer between the API and the Orchestrator,
handling asset analysis, reservation, and asynchronous task queueing.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from praxis.backend.services.protocol_definition import ProtocolDefinitionCRUDService
from praxis.backend.services.protocols import ProtocolRunService
from praxis.backend.models.pydantic.protocol import ProtocolRunUpdate
from praxis.backend.core.celery_tasks import execute_protocol_run_task
from praxis.backend.models.orm.protocol import (
    FunctionProtocolDefinitionOrm,
    ProtocolRunOrm,
    ProtocolRunStatusEnum,
)
from praxis.backend.models.pydantic.runtime import RuntimeAssetRequirement
from praxis.backend.models.pydantic.protocol import (
    AssetConstraintsModel,
    AssetRequirementModel,
    LocationConstraintsModel,
)
from praxis.backend.utils.logging import get_logger
from praxis.backend.utils.uuid import uuid7

logger = get_logger(__name__)


class ScheduleEntry:
  """Represents a scheduled protocol run with asset reservations."""

  def __init__(
    self,
    protocol_run_id: uuid.UUID,
    protocol_name: str,
    required_assets: list[RuntimeAssetRequirement],
    estimated_duration_ms: int | None = None,
    priority: int = 1,
  ):
    """Initialize a ScheduleEntry.

    Args:
        protocol_run_id: UUID of the protocol run.
        protocol_name: Name of the protocol.
        required_assets: List of asset requirements.
        estimated_duration_ms: Estimated execution duration in milliseconds.
        priority: Execution priority (higher numbers = higher priority).

    """
    self.protocol_run_id = protocol_run_id
    self.protocol_name = protocol_name
    self.required_assets = required_assets
    self.estimated_duration_ms = estimated_duration_ms
    self.priority = priority
    self.scheduled_at = datetime.now(timezone.utc)
    self.status = "QUEUED"
    self.celery_task_id: str | None = None


class ProtocolScheduler:
  """Manages protocol scheduling, asset allocation, and execution queueing.

  This scheduler analyzes protocol requirements, reserves necessary assets,
  and queues protocol execution tasks using Celery. It provides the foundation
  for more advanced scheduling features like multi-protocol orchestration.
  """

  def __init__(
    self,
    db_session_factory: async_sessionmaker[AsyncSession],
    redis_url: str = "redis://localhost:6379/0",
    celery_app_instance: Celery | None = None,
  ):
    """Initialize the Protocol Scheduler.

    Args:
        db_session_factory: Factory for creating database sessions
        redis_url: Redis connection URL for Celery broker
        celery_app_instance: Optional pre-configured Celery app instance

    """
    self.db_session_factory = db_session_factory
    self.redis_url = redis_url
    self.celery_app = celery_app_instance or Celery(
      "praxis_protocol_scheduler",
      broker=redis_url,
      backend=redis_url,
      include=["praxis.backend.core.celery_tasks"],
    )

    # In-memory tracking (will be moved to Redis/DB for persistence)
    self._active_schedules: dict[uuid.UUID, ScheduleEntry] = {}
    self._asset_reservations: dict[str, set[uuid.UUID]] = {}

    logger.info("ProtocolScheduler initialized with Redis: %s", redis_url)

  async def analyze_protocol_requirements(
    self,
    protocol_def_orm: FunctionProtocolDefinitionOrm,
    user_params: dict[str, Any],
  ) -> list[RuntimeAssetRequirement]:
    """Analyze a protocol definition to determine asset requirements.

    Args:
        protocol_def_orm: The protocol definition from the database
        user_params: User-provided parameters for the protocol

    Returns:
        List of RuntimeAssetRequirement objects needed for execution

    """
    logger.info(
      "Analyzing asset requirements for protocol: %s v%s",
      protocol_def_orm.name,
      protocol_def_orm.version,
    )

    requirements: list[RuntimeAssetRequirement] = []

    # Analyze asset requirements from protocol definition
    for asset_def in protocol_def_orm.assets:
      requirement = RuntimeAssetRequirement.from_asset_definition_orm(
        asset_def,
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

    # Analyze deck requirements
    if protocol_def_orm.preconfigure_deck and protocol_def_orm.deck_param_name:
      # Create a synthetic asset definition for deck

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

    # TODO: Future enhancement - analyze protocol steps for granular asset needs
    # This would involve parsing the protocol function to understand:
    # - Sequential vs parallel asset usage
    # - Timing requirements
    # - Critical asset dependencies

    logger.info(
      "Protocol analysis complete. Found %d asset requirements.",
      len(requirements),
    )
    return requirements

  async def reserve_assets(
    self, requirements: list[RuntimeAssetRequirement], protocol_run_id: uuid.UUID,
  ) -> bool:
    """Reserve assets for a protocol run.

    Args:
        requirements: List of runtime asset requirements to reserve
        protocol_run_id: ID of the protocol run requesting assets

    Returns:
        True if all assets were successfully reserved, False otherwise

    """
    logger.info(
      "Attempting to reserve %d assets for run %s",
      len(requirements),
      protocol_run_id,
    )

    reserved_assets: list[str] = []

    try:
      for requirement in requirements:
        asset_key = f"{requirement.asset_type}:{requirement.asset_definition.name}"

        # Simple asset locking (will be enhanced with Redis locks)
        if asset_key not in self._asset_reservations:
          self._asset_reservations[asset_key] = set()

        # Check if asset is available (not reserved by another run)
        if self._asset_reservations[asset_key]:
          logger.warning(
            "Asset %s is already reserved by runs: %s",
            asset_key,
            self._asset_reservations[asset_key],
          )
          # Rollback previous reservations
          await self._release_reservations(reserved_assets, protocol_run_id)
          return False

        # Reserve the asset
        self._asset_reservations[asset_key].add(protocol_run_id)
        requirement.reservation_id = uuid7()
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

    # pylint: disable-next=broad-except
    # Justification: This is a critical step in asset reservation. Catching broad Exception
    # ensures that any unhandled error leads to a rollback of reservations and a False return.
    except Exception as e:
      logger.error(
        "Error during asset reservation for run %s: %s",
        protocol_run_id,
        e,
        exc_info=True,
      )
      # Rollback all reservations on error
      await self._release_reservations(reserved_assets, protocol_run_id)
      return False

  async def _release_reservations(
    self, asset_keys: list[str], protocol_run_id: uuid.UUID,
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
    """Schedule a protocol for execution.

    Args:
        protocol_run_orm: The protocol run database object
        user_params: User-provided parameters
        initial_state: Initial state data for the protocol

    Returns:
        True if successfully scheduled, False otherwise

    """
    logger.info(
      "Scheduling protocol execution for run %s (%s)",
      protocol_run_orm.accession_id,
      protocol_run_orm.top_level_protocol_definition.name
      if protocol_run_orm.top_level_protocol_definition
      else "Unknown",
    )

    try:
      # Get protocol definition
      async with self.db_session_factory() as db_session:
        protocol_def = protocol_run_orm.top_level_protocol_definition
        if not protocol_def:
          # Fetch from database if not loaded
          protocol_definition_crud_service = ProtocolDefinitionCRUDService(FunctionProtocolDefinitionOrm)
          protocol_def = await protocol_definition_crud_service.get(
            db=db_session,
            accession_id=protocol_run_orm.top_level_protocol_definition_accession_id,
          )

        if not protocol_def:
          logger.error(
            "Protocol definition not found for run %s",
            protocol_run_orm.accession_id,
          )
          return False

        # Analyze asset requirements
        requirements = await self.analyze_protocol_requirements(
          protocol_def, user_params,
        )

        # Reserve assets
        if not await self.reserve_assets(requirements, protocol_run_orm.accession_id):
          logger.error(
            "Failed to reserve assets for run %s",
            protocol_run_orm.accession_id,
          )
          # Update run status to indicate asset conflict
          protocol_run_crud_service = ProtocolRunService(ProtocolRunOrm)
          await protocol_run_crud_service.update(
            db=db_session,
            db_obj=protocol_run_orm,
            obj_in=ProtocolRunUpdate(
              status=ProtocolRunStatusEnum.FAILED,
              output_data_json={
                "error": "Asset reservation failed",
                "details": "Required assets are not available",
              },
            ),
          )
          await db_session.commit()
          return False

        # Create schedule entry
        schedule_entry = ScheduleEntry(
          protocol_run_id=protocol_run_orm.accession_id,
          protocol_name=protocol_def.name,
          required_assets=requirements,
          # TODO: Estimate duration based on protocol analysis
          estimated_duration_ms=None,
        )

        self._active_schedules[protocol_run_orm.accession_id] = schedule_entry

        # Update run status to QUEUED
        protocol_run_crud_service = ProtocolRunService(ProtocolRunOrm)
        await protocol_run_crud_service.update(
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

        # Queue the execution task (placeholder for Celery integration)
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
        # Clean up reservations on queueing failure
        await self.cancel_scheduled_run(protocol_run_orm.accession_id)
        return False

    except Exception as e:
      logger.error(
        "Error scheduling protocol execution for run %s: %s",
        protocol_run_orm.accession_id,
        e,
        exc_info=True,
      )
      return False

  async def _queue_execution_task(
    self,
    protocol_run_id: uuid.UUID,
    user_params: dict[str, Any],
    initial_state: dict[str, Any] | None,
  ) -> bool:
    """Queue a protocol execution task using Celery.

    Args:
        protocol_run_id: UUID of the protocol run to execute.
        user_params: User-provided parameters for the protocol.
        initial_state: Initial state data for the protocol.

    Returns:
        True if successfully queued, False otherwise.

    """
    logger.info("Queueing execution task for run %s", protocol_run_id)

    # Ensure user_params is a dict (never None)
    user_params = user_params or {}

    try:
      # Queue the task with Celery
      try:
        # Try to use Celery task
        task_result = execute_protocol_run_task.delay(  # type: ignore
          str(protocol_run_id), user_params, initial_state,
        )
        celery_task_id = getattr(task_result, "id", None)
      except AttributeError as e:
        # Fallback: direct call to Celery task is not supported
        raise RuntimeError(
          "Direct call to execute_protocol_run_task is not supported. Celery worker must be running.",
        ) from e

      logger.info(
        "Successfully queued protocol run %s with Celery task ID: %s",
        protocol_run_id,
        celery_task_id,
      )

      # Update schedule entry with task ID
      if protocol_run_id in self._active_schedules:
        schedule_entry = self._active_schedules[protocol_run_id]
        schedule_entry.status = "QUEUED"
        # Store task ID for future reference/cancellation
        schedule_entry.celery_task_id = celery_task_id

      return True

    except Exception as e:
      logger.error(
        "Failed to queue execution task for run %s: %s",
        protocol_run_id,
        e,
        exc_info=True,
      )
      return False

  async def cancel_scheduled_run(self, protocol_run_id: uuid.UUID) -> bool:
    """Cancel a scheduled protocol run and release assets.

    Args:
        protocol_run_id: ID of the protocol run to cancel

    Returns:
        True if successfully cancelled, False otherwise

    """
    logger.info("Cancelling scheduled run %s", protocol_run_id)

    try:
      if protocol_run_id in self._active_schedules:
        schedule_entry = self._active_schedules[protocol_run_id]

        # Release asset reservations
        for requirement in schedule_entry.required_assets:
          asset_key = f"{requirement.asset_type}:{requirement.asset_definition.name}"
          if asset_key in self._asset_reservations:
            self._asset_reservations[asset_key].discard(protocol_run_id)
            if not self._asset_reservations[asset_key]:
              del self._asset_reservations[asset_key]

        # Remove from active schedules
        del self._active_schedules[protocol_run_id]

        logger.info("Successfully cancelled scheduled run %s", protocol_run_id)
        return True
      logger.warning("Run %s not found in active schedules", protocol_run_id)
      return False

    except Exception as e:
      logger.error(
        "Error cancelling scheduled run %s: %s",
        protocol_run_id,
        e,
        exc_info=True,
      )
      return False

  async def get_schedule_status(
    self, protocol_run_id: uuid.UUID,
  ) -> dict[str, Any] | None:
    """Get the current schedule status for a protocol run.

    Args:
        protocol_run_id: ID of the protocol run

    Returns:
        Dictionary with schedule information, or None if not found

    """
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
    """List all currently active protocol schedules.

    Returns:
        List of schedule status dictionaries

    """
    schedules = []
    for protocol_run_id in self._active_schedules:
      status = await self.get_schedule_status(protocol_run_id)
      if status:
        schedules.append(status)

    return sorted(schedules, key=lambda x: x["scheduled_at"])
