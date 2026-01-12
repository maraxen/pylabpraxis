# pylint: disable=too-few-public-methods,broad-except,fixme
"""Protocol Execution Integration Service.

This module provides a high-level service that ties together the Scheduler,
Orchestrator, and Celery tasks for complete protocol execution workflow.
It serves as the main entry point for protocol execution requests.
"""

import json
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from praxis.backend.core.protocols.asset_manager import IAssetManager
from praxis.backend.core.protocols.orchestrator import IOrchestrator
from praxis.backend.core.protocols.protocol_execution_service import IProtocolExecutionService
from praxis.backend.core.protocols.scheduler import IProtocolScheduler
from praxis.backend.core.protocols.workcell_runtime import IWorkcellRuntime
from praxis.backend.models import ProtocolRun, ProtocolRunStatusEnum
from praxis.backend.models.domain.protocol import ProtocolRunCreate
from praxis.backend.services.protocol_definition import ProtocolDefinitionCRUDService
from praxis.backend.services.protocols import ProtocolRunService
from praxis.backend.utils.logging import get_logger
from praxis.backend.utils.uuid import uuid7

logger = get_logger(__name__)


class ProtocolExecutionService(IProtocolExecutionService):
  """High-level service for protocol execution management."""

  def __init__(
    self,
    db_session_factory: async_sessionmaker[AsyncSession],
    asset_manager: IAssetManager,
    workcell_runtime: IWorkcellRuntime,
    scheduler: IProtocolScheduler,
    orchestrator: IOrchestrator,
    protocol_run_service: ProtocolRunService,
    protocol_definition_service: ProtocolDefinitionCRUDService,
  ) -> None:
    """Initialize the Protocol Execution Service."""
    self.db_session_factory = db_session_factory
    self.asset_manager = asset_manager
    self.workcell_runtime = workcell_runtime
    self.scheduler = scheduler
    self.orchestrator = orchestrator
    self.protocol_run_service = protocol_run_service
    self.protocol_definition_service = protocol_definition_service
    logger.info("ProtocolExecutionService initialized.")

  async def execute_protocol_immediately(
    self,
    protocol_name: str,
    user_input_params: dict[str, Any] | None = None,
    initial_state_data: dict[str, Any] | None = None,
    protocol_version: str | None = None,
    commit_hash: str | None = None,
    source_name: str | None = None,
    is_simulation: bool = False,
  ) -> ProtocolRun:
    """Execute a protocol immediately (synchronously) without scheduling.

    Args:
        protocol_name: Name of the protocol to execute.
        user_input_params: User-provided input parameters.
        initial_state_data: Initial state data for the run.
        protocol_version: Optional specific version to run.
        commit_hash: Optional commit hash for version control.
        source_name: Optional source name.
        is_simulation: If True, run in simulation mode (no hardware interaction).

    Returns:
        ProtocolRun: The completed protocol run record.

    """
    logger.info(
      "Executing protocol '%s' immediately (simulation=%s)",
      protocol_name,
      is_simulation,
    )

    return await self.orchestrator.execute_protocol(
      protocol_name=protocol_name,
      input_parameters=user_input_params,
      initial_state_data=initial_state_data,
      protocol_version=protocol_version,
      commit_hash=commit_hash,
      source_name=source_name,
      is_simulation=is_simulation,
    )

  async def schedule_protocol_execution(
    self,
    protocol_name: str,
    user_input_params: dict[str, Any] | None = None,
    initial_state_data: dict[str, Any] | None = None,
    protocol_version: str | None = None,
    commit_hash: str | None = None,
    source_name: str | None = None,
    is_simulation: bool = False,
  ) -> ProtocolRun:
    """Schedule a protocol for asynchronous execution via the scheduler.

    Args:
        protocol_name: Name of the protocol to schedule.
        user_input_params: User-provided input parameters.
        initial_state_data: Initial state data for the run.
        protocol_version: Optional specific version to run.
        commit_hash: Optional commit hash for version control.
        source_name: Optional source name.
        is_simulation: If True, run in simulation mode (no hardware interaction).

    Returns:
        ProtocolRun: The protocol run record with QUEUED status.

    """
    logger.info(
      "Scheduling protocol '%s' for execution (simulation=%s)",
      protocol_name,
      is_simulation,
    )
    user_input_params = user_input_params or {}
    initial_state_data = initial_state_data or {}
    run_accession_id = uuid7()

    async with self.db_session_factory() as db_session:
      # Get protocol definition - try by accession_id first (if it looks like a UUID)
      protocol_def_model = None
      try:
        # Check if protocol_name is a UUID (accession_id)
        protocol_uuid = uuid.UUID(protocol_name)
        protocol_def_model = await self.protocol_definition_service.get(
          db=db_session,
          accession_id=protocol_uuid,
        )
      except (ValueError, TypeError):
        # Not a valid UUID, ignore and fall through to name lookup
        pass

      # Fall back to name lookup if not found by ID
      if not protocol_def_model:
        protocol_def_model = await self.protocol_definition_service.get_by_name(
          db=db_session,
          name=protocol_name,
          version=protocol_version,
          commit_hash=commit_hash,
        )

      if not protocol_def_model or not protocol_def_model.accession_id:
        error_msg = (
          f"Protocol '{protocol_name}' (v:{protocol_version}, "
          f"commit:{commit_hash}, src:{source_name}) not found or invalid DB ID."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

      # Create protocol run record
      protocol_run_model = await self.protocol_run_service.create(
        db=db_session,
        obj_in=ProtocolRunCreate(
          run_accession_id=run_accession_id,
          top_level_protocol_definition_accession_id=protocol_def_model.accession_id,
          status=ProtocolRunStatusEnum.PREPARING,
          input_parameters_json=user_input_params,
          initial_state_json=initial_state_data,
        ),
      )
      await db_session.flush()
      await db_session.refresh(protocol_run_model)
      await db_session.commit()

      # Schedule the protocol run (pass ID to avoid session boundary issues)
      success = await self.scheduler.schedule_protocol_execution(
        protocol_run_model.accession_id,
        user_input_params,
        initial_state_data,
      )

      if not success:
        logger.error("Failed to schedule protocol run %s", run_accession_id)
        msg = f"Failed to schedule protocol run {run_accession_id}"
        raise RuntimeError(msg)

      logger.info(
        "Successfully scheduled protocol run %s for execution",
        run_accession_id,
      )
      return protocol_run_model

  async def get_protocol_run_status(
    self,
    protocol_run_id: uuid.UUID,
  ) -> dict[str, Any] | None:
    """Get the current status of a protocol run."""
    # Check scheduler status first
    schedule_status = await self.scheduler.get_schedule_status(protocol_run_id)

    # Get database status
    async with self.db_session_factory() as db_session:
      protocol_run_model = await self.protocol_run_service.get(
        db_session,
        accession_id=protocol_run_id,
      )

      if not protocol_run_model:
        return None

      status_info = {
        "protocol_run_id": str(protocol_run_id),
        "status": protocol_run_model.status.value if protocol_run_model.status else "UNKNOWN",
        "created_at": protocol_run_model.created_at.isoformat()
        if protocol_run_model.created_at
        else None,
        "start_time": protocol_run_model.start_time.isoformat()
        if protocol_run_model.start_time
        else None,
        "end_time": protocol_run_model.end_time.isoformat() if protocol_run_model.end_time else None,
        "duration_ms": protocol_run_model.duration_ms,
        "protocol_name": (
          protocol_run_model.top_level_protocol_definition.name
          if protocol_run_model.top_level_protocol_definition
          else "Unknown"
        ),
        "schedule_info": schedule_status,
      }

      # Add output data if available
      if protocol_run_model.output_data_json:
        try:
          status_info["output_data"] = json.loads(protocol_run_model.output_data_json)  # type: ignore[no-untyped-call]
        except json.JSONDecodeError:
          status_info["output_data_raw"] = protocol_run_model.output_data_json

      return status_info

  async def cancel_protocol_run(self, protocol_run_id: uuid.UUID) -> bool:
    """Cancel a protocol run."""
    logger.info("Cancelling protocol run %s", protocol_run_id)

    # 1. Send CANCEL command to orchestrator via Redis (for running protocols)
    from praxis.backend.utils.run_control import send_control_command

    redis_command_sent = await send_control_command(protocol_run_id, "CANCEL")
    if redis_command_sent:
      logger.info("Sent CANCEL command to orchestrator for run %s", protocol_run_id)
    else:
      logger.warning(
        "Failed to send CANCEL command to orchestrator for run %s (Redis error?)", protocol_run_id
      )

    # 2. Cancel in scheduler (releases resources and stops Celery task if possible)
    scheduler_cancelled = await self.scheduler.cancel_scheduled_run(protocol_run_id)

    # 3. Update database status
    database_cancelled = False
    async with self.db_session_factory() as db_session:
      try:
        # Check current status first
        current_run = await self.protocol_run_service.get(db_session, protocol_run_id)
        if current_run:
          # If already completed or cancelled, don't overwrite status
          if current_run.status in [
            ProtocolRunStatusEnum.COMPLETED,
            ProtocolRunStatusEnum.CANCELLED,
            ProtocolRunStatusEnum.FAILED,
          ]:
            logger.info(
              "Run %s is already in terminal state %s, not updating status",
              protocol_run_id,
              current_run.status,
            )
            database_cancelled = True  # Consider it a success as it's already done
          else:
            from datetime import datetime, timezone

            await self.protocol_run_service.update_run_status(
              db_session,
              protocol_run_id,
              ProtocolRunStatusEnum.CANCELLED,
              output_data_json=json.dumps(
                {
                  "status": "Cancelled by user via ProtocolExecutionService",
                  "cancelled_at": datetime.now(timezone.utc).isoformat(),
                },
              ),
            )
            await db_session.commit()
            database_cancelled = True
      except Exception:
        logger.exception(
          "Failed to update database status for cancelled run %s",
          protocol_run_id,
        )
        database_cancelled = False

    success = (scheduler_cancelled or redis_command_sent) and database_cancelled
    if success:
      logger.info("Successfully cancelled protocol run %s", protocol_run_id)
    else:
      logger.warning("Partial cancellation of protocol run %s", protocol_run_id)

    return success
