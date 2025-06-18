# pylint: disable=too-few-public-methods,broad-except,fixme
"""Protocol Execution Integration Service.

This module provides a high-level service that ties together the Scheduler,
Orchestrator, and Celery tasks for complete protocol execution workflow.
It serves as the main entry point for protocol execution requests.
"""

import json
import uuid
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import praxis.backend.services as svc
from praxis.backend.core.asset_manager import AssetManager
from praxis.backend.core.orchestrator import Orchestrator
from praxis.backend.core.protocol_code_manager import ProtocolCodeManager
from praxis.backend.core.scheduler import ProtocolScheduler
from praxis.backend.core.workcell_runtime import WorkcellRuntime
from praxis.backend.models import ProtocolRunStatusEnum
from praxis.backend.utils.logging import get_logger
from praxis.backend.utils.uuid import uuid7

logger = get_logger(__name__)


class ProtocolExecutionService:
  """High-level service for protocol execution management.

  This service orchestrates the entire protocol execution workflow:
  1. Creates protocol runs in the database
  2. Uses the Scheduler to analyze resource requirements and queue execution
  3. Coordinates with Celery workers for async execution
  4. Provides status monitoring and control capabilities
  """

  def __init__(
    self,
    db_session_factory: async_sessionmaker[AsyncSession],
    asset_manager: AssetManager,
    workcell_runtime: WorkcellRuntime,
    scheduler: Optional[ProtocolScheduler] = None,
    orchestrator: Optional[Orchestrator] = None,
  ):
    """Initialize the Protocol Execution Service.

    Args:
        db_session_factory: Factory for creating database sessions.
        asset_manager: AssetManager instance for resource management.
        workcell_runtime: WorkcellRuntime instance for live object management.
        scheduler: Optional ProtocolScheduler instance. If None, creates a new one.
        orchestrator: Optional Orchestrator instance. If None, creates a new one.
    """
    self.db_session_factory = db_session_factory
    self.asset_manager = asset_manager
    self.workcell_runtime = workcell_runtime

    # Initialize scheduler with dependency injection
    self.scheduler = scheduler or ProtocolScheduler(db_session_factory)

    # Initialize orchestrator with all its dependencies
    protocol_code_manager = ProtocolCodeManager()
    self.orchestrator = orchestrator or Orchestrator(
      db_session_factory=db_session_factory,
      asset_manager=asset_manager,
      workcell_runtime=workcell_runtime,
      protocol_code_manager=protocol_code_manager,
    )

    logger.info("ProtocolExecutionService initialized.")

  async def execute_protocol_immediately(
    self,
    protocol_name: str,
    user_input_params: Optional[Dict[str, Any]] = None,
    initial_state_data: Optional[Dict[str, Any]] = None,
    protocol_version: Optional[str] = None,
    commit_hash: Optional[str] = None,
    source_name: Optional[str] = None,
  ):
    """Execute a protocol immediately (synchronously) without scheduling.

    This bypasses the scheduler and executes the protocol directly.
    Useful for testing, debugging, or immediate execution scenarios.

    Args:
        protocol_name: Name of the protocol to execute.
        user_input_params: User-provided parameters.
        initial_state_data: Initial state data.
        protocol_version: Specific version of the protocol.
        commit_hash: Specific commit hash if from Git source.
        source_name: Name of the protocol source.

    Returns:
        The ProtocolRunOrm object representing the execution result.
    """
    logger.info(
      "Executing protocol '%s' immediately (bypassing scheduler)", protocol_name
    )

    return await self.orchestrator.execute_protocol(
      protocol_name=protocol_name,
      input_parameters=user_input_params,
      initial_state_data=initial_state_data,
      protocol_version=protocol_version,
      commit_hash=commit_hash,
      source_name=source_name,
    )

  async def schedule_protocol_execution(
    self,
    protocol_name: str,
    user_input_params: Optional[Dict[str, Any]] = None,
    initial_state_data: Optional[Dict[str, Any]] = None,
    protocol_version: Optional[str] = None,
    commit_hash: Optional[str] = None,
    source_name: Optional[str] = None,
  ):
    """Schedule a protocol for asynchronous execution via the scheduler.

    This creates a protocol run, analyzes resource requirements,
    reserves resources, and queues the execution with Celery.

    Args:
        protocol_name: Name of the protocol to execute.
        user_input_params: User-provided parameters.
        initial_state_data: Initial state data.
        protocol_version: Specific version of the protocol.
        commit_hash: Specific commit hash if from Git source.
        source_name: Name of the protocol source.

    Returns:
        The ProtocolRunOrm object representing the scheduled run.

    Raises:
        ValueError: If protocol definition is not found.
        RuntimeError: If scheduling fails.
    """
    logger.info("Scheduling protocol '%s' for asynchronous execution", protocol_name)

    user_input_params = user_input_params or {}
    initial_state_data = initial_state_data or {}
    run_accession_id = uuid7()

    async with self.db_session_factory() as db_session:
      # Get protocol definition
      protocol_def_orm = await svc.read_protocol_definition_by_name(
        db=db_session,
        name=protocol_name,
        version=protocol_version,
        source_name=source_name,
        commit_hash=commit_hash,
      )

      if not protocol_def_orm or not protocol_def_orm.accession_id:
        error_msg = (
          f"Protocol '{protocol_name}' (v:{protocol_version}, "
          f"commit:{commit_hash}, src:{source_name}) not found or invalid DB ID."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

      # Create protocol run record
      protocol_run_orm = await svc.create_protocol_run(
        db=db_session,
        run_accession_id=run_accession_id,
        top_level_protocol_definition_accession_id=protocol_def_orm.accession_id,
        status=ProtocolRunStatusEnum.PREPARING,
        input_parameters_json=json.dumps(user_input_params),
        initial_state_json=json.dumps(initial_state_data),
      )
      await db_session.flush()
      await db_session.refresh(protocol_run_orm)
      await db_session.commit()

      # Schedule the protocol run
      success = await self.scheduler.schedule_protocol_execution(
        protocol_run_orm, user_input_params, initial_state_data
      )

      if not success:
        logger.error("Failed to schedule protocol run %s", run_accession_id)
        raise RuntimeError(f"Failed to schedule protocol run {run_accession_id}")

      logger.info(
        "Successfully scheduled protocol run %s for execution", run_accession_id
      )
      return protocol_run_orm

  async def get_protocol_run_status(
    self, protocol_run_id: uuid.UUID
  ) -> Optional[Dict[str, Any]]:
    """Get the current status of a protocol run.

    Args:
        protocol_run_id: UUID of the protocol run.

    Returns:
        Dictionary with run status information, or None if not found.
    """
    # Check scheduler status first
    schedule_status = await self.scheduler.get_schedule_status(protocol_run_id)

    # Get database status
    async with self.db_session_factory() as db_session:
      protocol_run_orm = await svc.read_protocol_run(
        db_session, run_accession_id=protocol_run_id
      )

      if not protocol_run_orm:
        return None

      status_info = {
        "protocol_run_id": str(protocol_run_id),
        "status": protocol_run_orm.status.value
        if protocol_run_orm.status
        else "UNKNOWN",
        "created_at": protocol_run_orm.created_at.isoformat()
        if protocol_run_orm.created_at
        else None,
        "start_time": protocol_run_orm.start_time.isoformat()
        if protocol_run_orm.start_time
        else None,
        "end_time": protocol_run_orm.end_time.isoformat()
        if protocol_run_orm.end_time
        else None,
        "duration_ms": protocol_run_orm.duration_ms,
        "protocol_name": (
          protocol_run_orm.top_level_protocol_definition.name
          if protocol_run_orm.top_level_protocol_definition
          else "Unknown"
        ),
        "schedule_info": schedule_status,
      }

      # Add output data if available
      if protocol_run_orm.output_data_json:
        try:
          status_info["output_data"] = json.load(protocol_run_orm.output_data_json)  # type: ignore
        except json.JSONDecodeError:
          status_info["output_data_raw"] = protocol_run_orm.output_data_json

      return status_info

  async def cancel_protocol_run(self, protocol_run_id: uuid.UUID) -> bool:
    """Cancel a protocol run.

    Args:
        protocol_run_id: UUID of the protocol run to cancel.

    Returns:
        True if successfully cancelled, False otherwise.
    """
    logger.info("Cancelling protocol run %s", protocol_run_id)

    # Cancel in scheduler (releases resources and stops Celery task if possible)
    scheduler_cancelled = await self.scheduler.cancel_scheduled_run(protocol_run_id)

    # Update database status
    async with self.db_session_factory() as db_session:
      try:
        await svc.update_protocol_run_status(
          db_session,
          protocol_run_id,
          ProtocolRunStatusEnum.CANCELLED,
          output_data_json=json.dumps(
            {
              "status": "Cancelled by user via ProtocolExecutionService",
              "cancelled_at": json.dumps(None),  # Would use actual timestamp
            }
          ),
        )
        await db_session.commit()
        database_cancelled = True
      except Exception as e:
        logger.error(
          "Failed to update database status for cancelled run %s: %s",
          protocol_run_id,
          e,
        )
        database_cancelled = False

    success = scheduler_cancelled and database_cancelled
    if success:
      logger.info("Successfully cancelled protocol run %s", protocol_run_id)
    else:
      logger.warning("Partial cancellation of protocol run %s", protocol_run_id)

    return success
