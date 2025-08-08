# pylint: disable=fixme
"""Celery tasks for protocol execution.

This module defines the async tasks for executing protocols in the background.
It imports the shared Celery application instance and defines the business
logic for what happens when a task is executed by a worker.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
  import uuid

  from celery import Task
  from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

  from praxis.backend.core.orchestrator import Orchestrator


from celery.utils.log import get_task_logger

# Import the decoupled Celery app instance from its dedicated module
from praxis.backend.core.celery import celery_app
from praxis.backend.models import ProtocolRunStatusEnum
from praxis.backend.services.protocols import protocol_run_service
from praxis.backend.services.state import PraxisState
from praxis.backend.utils.logging import get_logger

# Standard loggers
task_logger = get_task_logger(__name__)
logger = get_logger(__name__)

# Global execution context - will be set by the application startup
_execution_context: ProtocolExecutionContext | None = None


class ProtocolExecutionContext:

  """A context object to hold shared dependencies for Celery tasks."""

  def __init__(
    self,
    db_session_factory: async_sessionmaker[AsyncSession],
    orchestrator: Orchestrator,  # Avoid circular import with type hint
  ) -> None:
    """Initialize the protocol execution context.

    Args:
        db_session_factory: Factory for creating SQLAlchemy async sessions.
        orchestrator: The main orchestrator instance for protocol execution.

    """
    self.db_session_factory = db_session_factory
    self.orchestrator = orchestrator


def get_execution_context() -> ProtocolExecutionContext:
  """Safely retrieve the execution context.

  Returns:
      The global execution context.

  Raises:
      RuntimeError: If the execution context is not initialized.

  """
  if not _execution_context:
    msg = "Celery execution context is not initialized. Cannot proceed."
    raise RuntimeError(msg)
  return _execution_context


def set_execution_context(context: ProtocolExecutionContext) -> None:
  """Set the global execution context.

  Args:
      context: The execution context to set.

  """
  global _execution_context  # pylint: disable=global-statement
  _execution_context = context


@celery_app.task(bind=True, name="execute_protocol_run")
def execute_protocol_run_task(
  self: Task,
  protocol_run_id: uuid.UUID,
  input_parameters: dict[str, Any],  # TODO(mar): Use ProtocolInputParameters when available
  initial_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
  """Celery task to execute a full protocol run.

  This is the main entry point for a background protocol execution. It bridges
  the synchronous world of Celery with the asynchronous logic of the orchestrator.

  Args:
      self: The Celery task instance (available via bind=True).
      protocol_run_id: The UUID of the protocol run to execute.
      input_parameters: Input parameters for the protocol execution.
      initial_state: Optional initial state data for the protocol (as dict to be validated).

  Returns:
      A dictionary containing the results and status of the execution.

  """
  task_logger.info(
    "Starting protocol execution for run_id=%s (task_id=%s)",
    protocol_run_id,
    self.request.id,
  )

  try:
    execution_context = get_execution_context()
  except RuntimeError as e:
    error_msg = str(e)
    task_logger.error(error_msg)
    return {"success": False, "error": error_msg}

  try:
    result = asyncio.run(
      _execute_protocol_async(protocol_run_id, input_parameters, initial_state, self.request.id),
    )
    task_logger.info("Protocol execution task completed for run_id=%s", protocol_run_id)

  except Exception as e:  # pylint: disable=broad-except
    error_msg = f"Protocol execution failed for run_id={protocol_run_id}: {e}"
    task_logger.exception(error_msg)
    try:
      asyncio.run(_update_run_status_on_error(protocol_run_id, str(e)))
    except Exception as update_error:  # pylint: disable=broad-except # noqa: BLE001
      task_logger.critical(
        "Critical error: Failed to update protocol run status after task failure. Error: %s",
        update_error,
      )
    return {"success": False, "error": error_msg}
  else:
    return result


async def _execute_protocol_async(
  protocol_run_id: uuid.UUID,
  input_parameters: dict[str, Any],
  initial_state: dict[str, Any] | None,
  celery_task_id: str,
) -> dict[str, Any]:
  """Asynchronously executes a protocol run using the Orchestrator.

  Args:
      protocol_run_id: The UUID of the protocol run.
      input_parameters: Input parameters for the protocol execution.
      initial_state: Optional initial state (will be validated as PraxisState).
      celery_task_id: The ID of the parent Celery task for logging.

  Returns:
      A dictionary with execution results.

  Raises:
      RuntimeError: If the execution context or orchestrator is not available.
      ValueError: If the protocol run is not found in the database or validation fails.

  """
  execution_context = get_execution_context()

  # Validate initial_state if provided
  validated_initial_state: PraxisState | None = None
  if initial_state is not None:
    try:
      validated_initial_state = PraxisState.model_validate(initial_state)
    except Exception as e:
      msg = f"Invalid initial_state format: {e}"
      raise ValueError(msg) from e

  async with execution_context.db_session_factory() as db_session:
    try:
      protocol_run_orm = await protocol_run_service.read_protocol_run(
        db_session, run_accession_id=protocol_run_id,
      )
      if not protocol_run_orm:
        msg = f"Protocol run {protocol_run_id} not found."
        raise ValueError(msg)

      # Update status to RUNNING and log the Celery task ID.
      await protocol_run_service.update_protocol_run_status(
        db=db_session,
        protocol_run_accession_id=protocol_run_orm.accession_id,
        new_status=ProtocolRunStatusEnum.RUNNING,
        output_data_json=json.dumps(
          {
            "status": "Execution started by Celery worker",
            "celery_task_id": celery_task_id,
          },
        ),
      )
      await db_session.commit()

      # Delegate the core execution logic to the orchestrator.
      result_run_orm = (
        await execution_context.orchestrator.execute_existing_protocol_run(
          protocol_run_orm, input_parameters, validated_initial_state,
        )
      )

      return {
        "success": True,
        "protocol_run_id": str(protocol_run_id),
        "final_status": result_run_orm.status.value,
        "message": "Protocol executed successfully via Orchestrator.",
      }
    # Justification: This is the primary error handler for the async execution logic.
    # A broad except is necessary to catch any failure from the Orchestrator,
    # log it, and ensure the database state is updated to FAILED before re-raising.
    except Exception as e:  # pylint: disable=broad-except
      task_logger.error(
        "Error during async protocol execution for run_id=%s: %s",
        protocol_run_id,
        e,
        exc_info=True,
      )
      # Ensure status is marked as FAILED on any exception within this block.
      await db_session.rollback()
      await protocol_run_service.update_protocol_run_status(
        db=db_session,
        protocol_run_accession_id=protocol_run_id,
        new_status=ProtocolRunStatusEnum.FAILED,
        output_data_json=json.dumps(
          {
            "error": str(e),
            "status": "Protocol execution failed in Celery worker.",
          },
        ),
      )
      await db_session.commit()
      raise  # Re-raise the exception to be caught by the main task handler.


async def _update_run_status_on_error(protocol_run_id: uuid.UUID, error_message: str) -> None:
  """A final-resort function to update a protocol run's status to FAILED."""
  try:
    execution_context = get_execution_context()
  except RuntimeError:
    task_logger.error(
      "Cannot update run status on error: Execution context is missing.",
    )
    return

  async with execution_context.db_session_factory() as db_session:
    try:
      await protocol_run_service.update_protocol_run_status(
        db=db_session,
        protocol_run_accession_id=protocol_run_id,
        new_status=ProtocolRunStatusEnum.FAILED,
        output_data_json=json.dumps(
          {
            "error": error_message,
            "status": "A critical error occurred in the Celery task.",
          },
        ),
      )
      await db_session.commit()
      task_logger.info(
        "Successfully updated run_id=%s to FAILED status.", protocol_run_id,
      )
    # Justification: This is a last-resort error handler for DB updates.
    # Catching broad Exception is necessary to prevent further unhandled exceptions
    # from crashing the Celery worker during its own error handling process.
    except Exception as e:  # pylint: disable=broad-except # noqa: BLE001
      task_logger.critical(
        "Could not update run status for run_id=%s. DB may be unreachable. Error: %s",
        protocol_run_id,
        e,
      )


@celery_app.task(name="health_check")
def health_check() -> dict[str, str]:
  """A simple health check task to verify that Celery workers are responsive."""
  return {
    "status": "healthy",
    "timestamp": datetime.now(timezone.utc).isoformat(),
  }
