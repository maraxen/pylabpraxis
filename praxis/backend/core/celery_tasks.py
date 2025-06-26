# pylint: disable=fixme
"""Celery tasks for protocol execution. # broad-except is justified at task level.

This module defines the async tasks for executing protocols in the background.
It imports the shared Celery application instance and defines the business
logic for what happens when a task is executed by a worker.
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from celery.utils.log import get_task_logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import praxis.backend.services as svc

# Import the decoupled Celery app instance from its dedicated module
from praxis.backend.core.celery import celery_app
from praxis.backend.models import ProtocolRunStatusEnum
from praxis.backend.utils.logging import get_logger

# Standard loggers
task_logger = get_task_logger(__name__)
logger = get_logger(__name__)


class ProtocolExecutionContext:
  """A context object to hold shared dependencies for Celery tasks."""

  def __init__(
    self,
    db_session_factory: async_sessionmaker[AsyncSession],
    orchestrator: Optional[Any] = None,  # Avoid circular import with type hint
  ):
    """Initialize the protocol execution context.

    Args:
        db_session_factory: Factory for creating SQLAlchemy async sessions.
        orchestrator: The main orchestrator instance for protocol execution.

    """
    self.db_session_factory = db_session_factory
    self.orchestrator = orchestrator


# This global context will be initialized once during application startup.
_execution_context: Optional[ProtocolExecutionContext] = None


def initialize_celery_context(
  db_session_factory: async_sessionmaker[AsyncSession],
  orchestrator: Any,
):
  """Initialize the global context for Celery tasks with necessary dependencies.

  This function should be called when the main application starts to ensure
  that all Celery workers have access to the database and orchestrator.
  """
  global _execution_context
  if not _execution_context:
    _execution_context = ProtocolExecutionContext(db_session_factory, orchestrator)
    logger.info("Celery execution context initialized successfully.")


@celery_app.task(bind=True, name="execute_protocol_run")
def execute_protocol_run_task(
  self,
  protocol_run_id: str,
  user_params: Dict[str, Any],
  initial_state: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
  """Celery task to execute a full protocol run.

  This is the main entry point for a background protocol execution. It bridges
  the synchronous world of Celery with the asynchronous logic of the orchestrator.

  Args:
      self: The Celery task instance (available via bind=True).
      protocol_run_id: The UUID string of the protocol run to execute.
      user_params: User-provided parameters for the protocol.
      initial_state: Optional initial state data for the protocol.

  Returns:
      A dictionary containing the results and status of the execution.

  """
  task_logger.info(
    "Starting protocol execution for run_id=%s (task_id=%s)",
    protocol_run_id,
    self.request.id,
  )

  if not _execution_context:
    error_msg = "Celery execution context is not initialized. Cannot proceed."
    task_logger.error(error_msg)
    # We cannot update the run status without a DB session factory.
    return {"success": False, "error": error_msg}

  run_uuid = uuid.UUID(protocol_run_id)

  try:
    # Use asyncio.run to manage the event loop for the async logic.
    result = asyncio.run(
      _execute_protocol_async(run_uuid, user_params, initial_state, self.request.id)
    )
    task_logger.info("Protocol execution task completed for run_id=%s", protocol_run_id)
    # pylint: disable-next=broad-except
    # Justification: This is a top-level Celery task handler. Catching broad Exception
    # ensures that any unhandled error during async execution is caught, logged, and
    # the protocol run status is updated to FAILED, preventing silent failures.
    return result
  except Exception as e:
    error_msg = f"Protocol execution failed for run_id={protocol_run_id}: {e}"
    task_logger.error(error_msg, exc_info=True)
    # Attempt to update the run status to FAILED in the database.
    try:
      asyncio.run(_update_run_status_on_error(run_uuid, str(e)))
    except Exception as update_error:
      task_logger.error(
        "Critical error: Failed to update protocol run status after task failure. Error: %s",
        update_error,
      )
    return {"success": False, "error": error_msg}


async def _execute_protocol_async(
  protocol_run_id: uuid.UUID,
  user_params: Dict[str, Any],
  initial_state: Optional[Dict[str, Any]],
  celery_task_id: str,
) -> Dict[str, Any]:
  """Asynchronously executes a protocol run using the Orchestrator.

  Args:
      protocol_run_id: The UUID of the protocol run.
      user_params: User-provided parameters.
      initial_state: Optional initial state.
      celery_task_id: The ID of the parent Celery task for logging.

  Returns:
      A dictionary with execution results.

  Raises:
      RuntimeError: If the execution context or orchestrator is not available.
      ValueError: If the protocol run is not found in the database.

  """
  if not _execution_context or not _execution_context.orchestrator:
    raise RuntimeError("Execution context or orchestrator is not available.")

  async with _execution_context.db_session_factory() as db_session:
    try:
      protocol_run_orm = await svc.read_protocol_run(
        db_session, run_accession_id=protocol_run_id
      )
      if not protocol_run_orm:
        raise ValueError(f"Protocol run {protocol_run_id} not found.")

      # Update status to RUNNING and log the Celery task ID.
      await svc.update_protocol_run_status(
        db=db_session,
        protocol_run_accession_id=protocol_run_orm.accession_id,
        new_status=ProtocolRunStatusEnum.RUNNING,
        output_data_json=json.dumps(
          {
            "status": "Execution started by Celery worker",
            "celery_task_id": celery_task_id,
          }
        ),
      )
      await db_session.commit()

      # Delegate the core execution logic to the orchestrator.
      result_run_orm = (
        await _execution_context.orchestrator.execute_existing_protocol_run(
          protocol_run_orm, user_params, initial_state
        )
      )

      return {
        "success": True,
        "protocol_run_id": str(protocol_run_id),
        "final_status": result_run_orm.status.value,
        "message": "Protocol executed successfully via Orchestrator.",
      }
    except Exception as e:
      task_logger.error(
        "Error during async protocol execution for run_id=%s: %s",
        protocol_run_id,
        e,
        exc_info=True,
      )
      # Ensure status is marked as FAILED on any exception within this block.
      # pylint: disable-next=broad-except
      # Justification: This is a critical error handling path within an async task.
      # Catching broad Exception ensures that the protocol run status is updated to FAILED.
      await db_session.rollback()
      await svc.update_protocol_run_status(
        db=db_session,
        protocol_run_accession_id=protocol_run_id,
        new_status=ProtocolRunStatusEnum.FAILED,
        output_data_json=json.dumps(
          {
            "error": str(e),
            "status": "Protocol execution failed in Celery worker.",
          }
        ),
      )
      await db_session.commit()
      raise  # Re-raise the exception to be caught by the main task handler.


async def _update_run_status_on_error(protocol_run_id: uuid.UUID, error_message: str):
  """A final-resort function to update a protocol run's status to FAILED."""
  if not _execution_context:
    task_logger.error(
      "Cannot update run status on error: Execution context is missing."
    )
    return

  async with _execution_context.db_session_factory() as db_session:
    try:
      await svc.update_protocol_run_status(
        db=db_session,
        protocol_run_accession_id=protocol_run_id,
        new_status=ProtocolRunStatusEnum.FAILED,
        output_data_json=json.dumps(
          {
            "error": error_message,
            "status": "A critical error occurred in the Celery task.",
          }
        ),
      )
      await db_session.commit()
      task_logger.info(
        "Successfully updated run_id=%s to FAILED status.", protocol_run_id
      )
    # pylint: disable-next=broad-except
    # Justification: This is a last-resort error handler for DB updates.
    # Catching broad Exception is necessary to prevent further unhandled exceptions.
    except Exception as e:
      # If this fails, we log it, but there's little else we can do.
      task_logger.critical(
        "Could not update run status for run_id=%s. DB may be unreachable. Error: %s",
        protocol_run_id,
        e,
      )


@celery_app.task(name="health_check")
def health_check() -> Dict[str, str]:
  """A simple health check task to verify that Celery workers are responsive."""
  return {
    "status": "healthy",
    "timestamp": datetime.now(timezone.utc).isoformat(),
  }
