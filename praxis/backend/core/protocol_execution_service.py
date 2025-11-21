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
from praxis.backend.models import ProtocolRunOrm, ProtocolRunStatusEnum
from praxis.backend.models.pydantic_internals.protocol import ProtocolRunCreate
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
  ) -> ProtocolRunOrm:
    """Execute a protocol immediately (synchronously) without scheduling."""
    logger.info(
      "Executing protocol '%s' immediately (bypassing scheduler)",
      protocol_name,
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
    user_input_params: dict[str, Any] | None = None,
    initial_state_data: dict[str, Any] | None = None,
    protocol_version: str | None = None,
    commit_hash: str | None = None,
    source_name: str | None = None,
  ) -> ProtocolRunOrm:
    """Schedule a protocol for asynchronous execution via the scheduler."""
    logger.info("Scheduling protocol '%s' for asynchronous execution", protocol_name)

    user_input_params = user_input_params or {}
    initial_state_data = initial_state_data or {}
    run_accession_id = uuid7()

    async with self.db_session_factory() as db_session:
      # Get protocol definition
      protocol_def_orm = await self.protocol_definition_service.get_by_name(
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
      protocol_run_orm = await self.protocol_run_service.create(
        db=db_session,
        obj_in=ProtocolRunCreate(
          run_accession_id=run_accession_id,
          top_level_protocol_definition_accession_id=protocol_def_orm.accession_id,
          status=ProtocolRunStatusEnum.PREPARING,
          input_parameters_json=user_input_params,
          initial_state_json=initial_state_data,
        ),
      )
      await db_session.flush()
      await db_session.refresh(protocol_run_orm)
      await db_session.commit()

      # Schedule the protocol run
      success = await self.scheduler.schedule_protocol_execution(
        protocol_run_orm,
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
      return protocol_run_orm

  async def get_protocol_run_status(
    self,
    protocol_run_id: uuid.UUID,
  ) -> dict[str, Any] | None:
    """Get the current status of a protocol run."""
    # Check scheduler status first
    schedule_status = await self.scheduler.get_schedule_status(protocol_run_id)

    # Get database status
    async with self.db_session_factory() as db_session:
      protocol_run_orm = await self.protocol_run_service.get(
        db_session,
        accession_id=protocol_run_id,
      )

      if not protocol_run_orm:
        return None

      status_info = {
        "protocol_run_id": str(protocol_run_id),
        "status": protocol_run_orm.status.value if protocol_run_orm.status else "UNKNOWN",
        "created_at": protocol_run_orm.created_at.isoformat()
        if protocol_run_orm.created_at
        else None,
        "start_time": protocol_run_orm.start_time.isoformat()
        if protocol_run_orm.start_time
        else None,
        "end_time": protocol_run_orm.end_time.isoformat() if protocol_run_orm.end_time else None,
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
          status_info["output_data"] = json.loads(protocol_run_orm.output_data_json)  # type: ignore[no-untyped-call]
        except json.JSONDecodeError:
          status_info["output_data_raw"] = protocol_run_orm.output_data_json

      return status_info

  async def cancel_protocol_run(self, protocol_run_id: uuid.UUID) -> bool:
    """Cancel a protocol run."""
    logger.info("Cancelling protocol run %s", protocol_run_id)

    # Cancel in scheduler (releases resources and stops Celery task if possible)
    scheduler_cancelled = await self.scheduler.cancel_scheduled_run(protocol_run_id)

    # Update database status
    async with self.db_session_factory() as db_session:
      try:
        await self.protocol_run_service.update_run_status(
          db_session,
          protocol_run_id,
          ProtocolRunStatusEnum.CANCELLED,
          output_data_json=json.dumps(
            {
              "status": "Cancelled by user via ProtocolExecutionService",
              "cancelled_at": json.dumps(None),  # Would use actual timestamp
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

    success = scheduler_cancelled and database_cancelled
    if success:
      logger.info("Successfully cancelled protocol run %s", protocol_run_id)
    else:
      logger.warning("Partial cancellation of protocol run %s", protocol_run_id)

    return success
