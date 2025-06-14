# pylint: disable=too-many-arguments,broad-except,fixme
"""Protocol Scheduler - Manages protocol execution scheduling and resource allocation.

This module provides the scheduling layer between the API and the Orchestrator,
handling resource analysis, reservation, and asynchronous task queueing.
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import praxis.backend.services as svc
from praxis.backend.models import (
  AssetRequirementModel,
  FunctionProtocolDefinitionOrm,
  ProtocolRunOrm,
  ProtocolRunStatusEnum,
)
from praxis.backend.utils.logging import get_logger
from praxis.backend.utils.uuid import uuid7

logger = get_logger(__name__)


class ResourceRequirement:
  """Represents a resource requirement for protocol execution."""

  def __init__(
    self,
    resource_type: str,
    resource_name: str,
    required_capabilities: Optional[Dict[str, Any]] = None,
    estimated_duration_ms: Optional[int] = None,
    priority: int = 1,
  ):
    self.resource_type = resource_type
    self.resource_name = resource_name
    self.required_capabilities = required_capabilities or {}
    self.estimated_duration_ms = estimated_duration_ms
    self.priority = priority
    self.reservation_id: Optional[uuid.UUID] = None


class ScheduleEntry:
  """Represents a scheduled protocol run with resource reservations."""

  def __init__(
    self,
    protocol_run_id: uuid.UUID,
    protocol_name: str,
    required_resources: List[ResourceRequirement],
    estimated_duration_ms: Optional[int] = None,
    priority: int = 1,
  ):
    self.protocol_run_id = protocol_run_id
    self.protocol_name = protocol_name
    self.required_resources = required_resources
    self.estimated_duration_ms = estimated_duration_ms
    self.priority = priority
    self.scheduled_at = datetime.now(timezone.utc)
    self.status = "QUEUED"


class ProtocolScheduler:
  """Manages protocol scheduling, resource allocation, and execution queueing.

  This scheduler analyzes protocol requirements, reserves necessary resources,
  and queues protocol execution tasks using Celery. It provides the foundation
  for more advanced scheduling features like multi-protocol orchestration.
  """

  def __init__(
    self,
    db_session_factory: async_sessionmaker[AsyncSession],
    redis_url: str = "redis://localhost:6379/0",
  ):
    """Initialize the Protocol Scheduler.

    Args:
        db_session_factory: Factory for creating database sessions
        redis_url: Redis connection URL for Celery broker
    """
    self.db_session_factory = db_session_factory
    self.redis_url = redis_url

    # In-memory tracking (will be moved to Redis/DB for persistence)
    self._active_schedules: Dict[uuid.UUID, ScheduleEntry] = {}
    self._resource_reservations: Dict[str, Set[uuid.UUID]] = {}

    logger.info("ProtocolScheduler initialized with Redis: %s", redis_url)

  async def analyze_protocol_requirements(
    self,
    protocol_def_orm: FunctionProtocolDefinitionOrm,
    user_params: Dict[str, Any],
  ) -> List[ResourceRequirement]:
    """Analyze a protocol definition to determine resource requirements.

    Args:
        protocol_def_orm: The protocol definition from the database
        user_params: User-provided parameters for the protocol

    Returns:
        List of ResourceRequirement objects needed for execution
    """
    logger.info(
      "Analyzing resource requirements for protocol: %s v%s",
      protocol_def_orm.name,
      protocol_def_orm.version,
    )

    requirements: List[ResourceRequirement] = []

    # Analyze asset requirements from protocol definition
    for asset_def in protocol_def_orm.assets:
      requirement = ResourceRequirement(
        resource_type="asset",
        resource_name=asset_def.name,
        required_capabilities={
          "type": asset_def.actual_type_str,
          "optional": asset_def.optional,
        },
        # TODO: Estimate duration based on protocol analysis
        estimated_duration_ms=None,
      )
      requirements.append(requirement)
      logger.debug(
        "Added asset requirement: %s (%s)",
        asset_def.name,
        asset_def.actual_type_str,
      )

    # Analyze deck requirements
    if protocol_def_orm.preconfigure_deck and protocol_def_orm.deck_param_name:
      deck_requirement = ResourceRequirement(
        resource_type="deck",
        resource_name=protocol_def_orm.deck_param_name,
        required_capabilities={"preconfigure": True},
      )
      requirements.append(deck_requirement)
      logger.debug("Added deck requirement: %s", protocol_def_orm.deck_param_name)

    # TODO: Future enhancement - analyze protocol steps for granular resource needs
    # This would involve parsing the protocol function to understand:
    # - Sequential vs parallel resource usage
    # - Timing requirements
    # - Critical resource dependencies

    logger.info(
      "Protocol analysis complete. Found %d resource requirements.",
      len(requirements),
    )
    return requirements

  async def reserve_resources(
    self, requirements: List[ResourceRequirement], protocol_run_id: uuid.UUID
  ) -> bool:
    """Reserve resources for a protocol run.

    Args:
        requirements: List of resource requirements to reserve
        protocol_run_id: ID of the protocol run requesting resources

    Returns:
        True if all resources were successfully reserved, False otherwise
    """
    logger.info(
      "Attempting to reserve %d resources for run %s",
      len(requirements),
      protocol_run_id,
    )

    reserved_resources: List[str] = []

    try:
      for requirement in requirements:
        resource_key = f"{requirement.resource_type}:{requirement.resource_name}"

        # Simple resource locking (will be enhanced with Redis locks)
        if resource_key not in self._resource_reservations:
          self._resource_reservations[resource_key] = set()

        # Check if resource is available (not reserved by another run)
        if self._resource_reservations[resource_key]:
          logger.warning(
            "Resource %s is already reserved by runs: %s",
            resource_key,
            self._resource_reservations[resource_key],
          )
          # Rollback previous reservations
          await self._release_reservations(reserved_resources, protocol_run_id)
          return False

        # Reserve the resource
        self._resource_reservations[resource_key].add(protocol_run_id)
        requirement.reservation_id = uuid7()
        reserved_resources.append(resource_key)

        logger.debug(
          "Reserved resource %s for run %s (reservation: %s)",
          resource_key,
          protocol_run_id,
          requirement.reservation_id,
        )

      logger.info(
        "Successfully reserved all %d resources for run %s",
        len(requirements),
        protocol_run_id,
      )
      return True

    except Exception as e:
      logger.error(
        "Error during resource reservation for run %s: %s",
        protocol_run_id,
        e,
        exc_info=True,
      )
      # Rollback all reservations on error
      await self._release_reservations(reserved_resources, protocol_run_id)
      return False

  async def _release_reservations(
    self, resource_keys: List[str], protocol_run_id: uuid.UUID
  ) -> None:
    """Release resource reservations for a protocol run."""
    for resource_key in resource_keys:
      if resource_key in self._resource_reservations:
        self._resource_reservations[resource_key].discard(protocol_run_id)
        if not self._resource_reservations[resource_key]:
          del self._resource_reservations[resource_key]
        logger.debug("Released reservation for resource %s", resource_key)

  async def schedule_protocol_execution(
    self,
    protocol_run_orm: ProtocolRunOrm,
    user_params: Dict[str, Any],
    initial_state: Optional[Dict[str, Any]] = None,
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
          protocol_def = await svc.read_protocol_definition(
            db_session,
            definition_accession_id=protocol_run_orm.top_level_protocol_definition_accession_id,
          )

        if not protocol_def:
          logger.error(
            "Protocol definition not found for run %s",
            protocol_run_orm.accession_id,
          )
          return False

        # Analyze resource requirements
        requirements = await self.analyze_protocol_requirements(
          protocol_def, user_params
        )

        # Reserve resources
        if not await self.reserve_resources(
          requirements, protocol_run_orm.accession_id
        ):
          logger.error(
            "Failed to reserve resources for run %s",
            protocol_run_orm.accession_id,
          )
          # Update run status to indicate resource conflict
          await svc.update_protocol_run_status(
            db_session,
            protocol_run_orm.accession_id,
            ProtocolRunStatusEnum.FAILED,
            output_data_json=json.dumps(
              {
                "error": "Resource reservation failed",
                "details": "Required resources are not available",
              }
            ),
          )
          await db_session.commit()
          return False

        # Create schedule entry
        schedule_entry = ScheduleEntry(
          protocol_run_id=protocol_run_orm.accession_id,
          protocol_name=protocol_def.name,
          required_resources=requirements,
          # TODO: Estimate duration based on protocol analysis
          estimated_duration_ms=None,
        )

        self._active_schedules[protocol_run_orm.accession_id] = schedule_entry

        # Update run status to QUEUED
        await svc.update_protocol_run_status(
          db_session,
          protocol_run_orm.accession_id,
          ProtocolRunStatusEnum.QUEUED,
          output_data_json=json.dumps(
            {
              "scheduled_at": schedule_entry.scheduled_at.isoformat(),
              "resource_count": len(requirements),
            }
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
        else:
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
    user_params: Dict[str, Any],
    initial_state: Optional[Dict[str, Any]],
  ) -> bool:
    """Queue a protocol execution task.

    TODO: Replace with actual Celery task queueing
    """
    logger.info("Queueing execution task for run %s", protocol_run_id)

    # For now, this is a placeholder
    # In the full implementation, this would:
    # 1. Use Celery to queue an execution task
    # 2. Pass the protocol_run_id and parameters to the worker
    # 3. The worker would call the orchestrator with the existing run

    # Placeholder: simulate successful queueing
    await asyncio.sleep(0.1)
    return True

  async def cancel_scheduled_run(self, protocol_run_id: uuid.UUID) -> bool:
    """Cancel a scheduled protocol run and release resources.

    Args:
        protocol_run_id: ID of the protocol run to cancel

    Returns:
        True if successfully cancelled, False otherwise
    """
    logger.info("Cancelling scheduled run %s", protocol_run_id)

    try:
      if protocol_run_id in self._active_schedules:
        schedule_entry = self._active_schedules[protocol_run_id]

        # Release resource reservations
        for requirement in schedule_entry.required_resources:
          resource_key = f"{requirement.resource_type}:{requirement.resource_name}"
          if resource_key in self._resource_reservations:
            self._resource_reservations[resource_key].discard(protocol_run_id)
            if not self._resource_reservations[resource_key]:
              del self._resource_reservations[resource_key]

        # Remove from active schedules
        del self._active_schedules[protocol_run_id]

        logger.info("Successfully cancelled scheduled run %s", protocol_run_id)
        return True
      else:
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
    self, protocol_run_id: uuid.UUID
  ) -> Optional[Dict[str, Any]]:
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
      "resource_count": len(schedule_entry.required_resources),
      "estimated_duration_ms": schedule_entry.estimated_duration_ms,
      "priority": schedule_entry.priority,
    }

  async def list_active_schedules(self) -> List[Dict[str, Any]]:
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
