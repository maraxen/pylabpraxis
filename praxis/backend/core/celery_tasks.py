# pylint: disable=broad-except,fixme
"""Celery application and tasks for protocol execution.

This module defines the Celery application and async tasks for executing
protocols in the background. It integrates with the scheduler and orchestrator
to provide scalable, fault-tolerant protocol execution.
"""

import asyncio
import json
import uuid
from typing import Any, Dict, Optional

from celery import Celery
from celery.utils.log import get_task_logger
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

import praxis.backend.services as svc
from praxis.backend.models import ProtocolRunStatusEnum
from praxis.backend.utils.logging import get_logger

# Celery application configuration
celery_app = Celery(
  "praxis_protocol_execution",
  broker="redis://localhost:6379/0",
  backend="redis://localhost:6379/0",
  include=["praxis.backend.core.celery_tasks"],
)

# Celery configuration
celery_app.conf.update(
  task_serializer="json",
  accept_content=["json"],
  result_serializer="json",
  timezone="UTC",
  enable_utc=True,
  task_track_started=True,
  task_time_limit=3600,  # 1 hour timeout
  task_soft_time_limit=3300,  # 55 minutes soft timeout
  worker_prefetch_multiplier=1,  # Important for long-running tasks
  task_acks_late=True,
  worker_disable_rate_limits=True,
)

# Task logger
task_logger = get_task_logger(__name__)
logger = get_logger(__name__)


class ProtocolExecutionContext:
  """Context object passed to protocol execution tasks."""

  def __init__(
    self,
    db_session_factory: async_sessionmaker[AsyncSession],
    orchestrator=None,  # Will be imported when needed to avoid circular imports
  ):
    self.db_session_factory = db_session_factory
    self.orchestrator = orchestrator


# Global context (will be initialized by the application)
_execution_context: Optional[ProtocolExecutionContext] = None


def initialize_celery_context(
  db_session_factory: async_sessionmaker[AsyncSession],
  orchestrator=None,
):
  """Initialize the global execution context for Celery tasks.

  This should be called during application startup to provide
  the necessary dependencies for protocol execution tasks.
  """
  global _execution_context
  _execution_context = ProtocolExecutionContext(db_session_factory, orchestrator)
  logger.info("Celery execution context initialized")


@celery_app.task(bind=True, name="execute_protocol_run")
def execute_protocol_run_task(
  self,
  protocol_run_id: str,
  user_params: Dict[str, Any],
  initial_state: Optional[Dict[str, Any]] = None,
):
  """Celery task to execute a protocol run.

  Args:
      self: Celery task instance (for bind=True)
      protocol_run_id: UUID string of the protocol run to execute
      user_params: User-provided parameters for the protocol
      initial_state: Initial state data for the protocol

  Returns:
      Dict with execution results and status information
  """
  task_logger.info(
    "Starting protocol execution task for run %s (task ID: %s)",
    protocol_run_id,
    self.request.id,
  )

  if not _execution_context:
    error_msg = "Celery execution context not initialized"
    task_logger.error(error_msg)
    return {"success": False, "error": error_msg}

  try:
    # Convert string UUID back to UUID object
    run_uuid = uuid.UUID(protocol_run_id)

    # Run the async protocol execution
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
      result = loop.run_until_complete(
        _execute_protocol_async(
          run_uuid,
          user_params,
          initial_state,
        )
      )
      task_logger.info("Protocol execution task completed for run %s", protocol_run_id)
      return result

    finally:
      loop.close()

  except Exception as e:
    error_msg = f"Protocol execution task failed for run {protocol_run_id}: {e}"
    task_logger.error(error_msg, exc_info=True)

    # Try to update the run status to failed
    try:
      loop = asyncio.new_event_loop()
      asyncio.set_event_loop(loop)
      try:
        loop.run_until_complete(
          _update_run_status_on_error(uuid.UUID(protocol_run_id), str(e))
        )
      finally:
        loop.close()
    except Exception as update_error:
      task_logger.error("Failed to update run status after error: %s", update_error)

    return {"success": False, "error": error_msg}


async def _execute_protocol_async(
  protocol_run_id: uuid.UUID,
  user_params: Dict[str, Any],
  initial_state: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
  """Execute a protocol run asynchronously.

  This function serves as the bridge between the Celery task and the
  orchestrator, handling the async execution within the task context.
  """
  if not _execution_context:
    raise RuntimeError("Execution context not available")

  async with _execution_context.db_session_factory() as db_session:
    try:
      # Get the protocol run from the database
      protocol_run_orm = await svc.read_protocol_run(
        db_session, run_accession_id=protocol_run_id
      )

      if not protocol_run_orm:
        raise ValueError(f"Protocol run {protocol_run_id} not found")

      # Update status to RUNNING
      await svc.update_protocol_run_status(
        db_session,
        protocol_run_orm.accession_id,
        ProtocolRunStatusEnum.RUNNING,
        output_data_json=json.dumps(
          {
            "status": "Execution started by Celery worker",
            "celery_task_id": None,  # Would get this from task context
          }
        ),
      )
      await db_session.commit()

      # TODO: Execute via orchestrator
      # For now, we'll need to refactor the orchestrator to accept
      # an existing ProtocolRunOrm instead of creating its own

      # Placeholder for orchestrator integration
      # This is where we'd call something like:
      # result = await _execution_context.orchestrator.execute_existing_run(
      #     protocol_run_orm, user_params, initial_state
      # )

      # For now, simulate successful execution
      await asyncio.sleep(1)  # Simulate work

      # Update status to COMPLETED
      await svc.update_protocol_run_status(
        db_session,
        protocol_run_orm.accession_id,
        ProtocolRunStatusEnum.COMPLETED,
        output_data_json=json.dumps(
          {
            "status": "Protocol execution completed successfully",
            "result": "Placeholder result",
          }
        ),
      )
      await db_session.commit()

      return {
        "success": True,
        "protocol_run_id": str(protocol_run_id),
        "status": "COMPLETED",
        "message": "Protocol executed successfully",
      }

    except Exception as e:
      # Update status to FAILED
      await svc.update_protocol_run_status(
        db_session,
        protocol_run_id,
        ProtocolRunStatusEnum.FAILED,
        output_data_json=json.dumps(
          {
            "error": str(e),
            "status": "Protocol execution failed in Celery worker",
          }
        ),
      )
      await db_session.commit()
      raise


async def _update_run_status_on_error(protocol_run_id: uuid.UUID, error_message: str):
  """Update protocol run status when an error occurs in the Celery task."""
  if not _execution_context:
    return

  async with _execution_context.db_session_factory() as db_session:
    try:
      await svc.update_protocol_run_status(
        db_session,
        protocol_run_id,
        ProtocolRunStatusEnum.FAILED,
        output_data_json=json.dumps(
          {
            "error": error_message,
            "status": "Celery task execution failed",
          }
        ),
      )
      await db_session.commit()
    except Exception as e:
      task_logger.error("Failed to update run status: %s", e)


# Celery beat schedule for periodic tasks (if needed)
celery_app.conf.beat_schedule = {
  # Example: Clean up old completed tasks
  # "cleanup-completed-runs": {
  #     "task": "cleanup_completed_protocol_runs",
  #     "schedule": crontab(minute=0, hour=2),  # Daily at 2 AM
  # },
}


@celery_app.task(name="health_check")
def health_check():
  """Simple health check task for monitoring Celery workers."""
  return {
    "status": "healthy",
    "worker_id": celery_app.control.inspect().active(),
    "timestamp": json.dumps(None),  # Would use actual timestamp
  }
