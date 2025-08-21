# pylint: disable=fixme
"""Celery tasks for protocol execution.

This module defines the async tasks for executing protocols in the background.
It uses the dependency injection container to get the Celery app instance
and to inject dependencies into the tasks.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from celery.utils.log import get_task_logger
from dependency_injector.wiring import inject, Provide

from praxis.backend.core.celery import celery_app
from praxis.backend.core.container import Container
from praxis.backend.models import ProtocolRunStatusEnum
from praxis.backend.services.protocols import protocol_run_service
from praxis.backend.services.state import PraxisState
from praxis.backend.utils.logging import get_logger

if TYPE_CHECKING:
    import uuid

    from celery import Task
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from praxis.backend.core.orchestrator import Orchestrator

# Standard loggers
task_logger = get_task_logger(__name__)
logger = get_logger(__name__)



@celery_app.task(bind=True, name="execute_protocol_run")
@inject
def execute_protocol_run_task(
    self: Task,
    protocol_run_id: uuid.UUID,
    input_parameters: dict[str, Any],
    initial_state: dict[str, Any] | None = None,
    orchestrator: Orchestrator = Provide[Container.orchestrator],
    db_session_factory: async_sessionmaker[AsyncSession] = Provide[Container.db_session_factory],
) -> dict[str, Any]:
    """Celery task to execute a full protocol run."""
    task_logger.info(
        "Starting protocol execution for run_id=%s (task_id=%s)",
        protocol_run_id,
        self.request.id,
    )

    try:
        result = asyncio.run(
            _execute_protocol_async(
                protocol_run_id,
                input_parameters,
                initial_state,
                self.request.id,
                orchestrator,
                db_session_factory,
            ),
        )
        task_logger.info("Protocol execution task completed for run_id=%s", protocol_run_id)

    except Exception as e:
        error_msg = f"Protocol execution failed for run_id={protocol_run_id}: {e}"
        task_logger.exception(error_msg)
        try:
            asyncio.run(_update_run_status_on_error(protocol_run_id, str(e), db_session_factory))
        except Exception as update_error:
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
    orchestrator: Orchestrator,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> dict[str, Any]:
    """Asynchronously executes a protocol run using the Orchestrator."""
    validated_initial_state: PraxisState | None = None
    if initial_state is not None:
        try:
            validated_initial_state = PraxisState.model_validate(initial_state)
        except Exception as e:
            msg = f"Invalid initial_state format: {e}"
            raise ValueError(msg) from e

    async with db_session_factory() as db_session:
        try:
            protocol_run_orm = await protocol_run_service.read_protocol_run(
                db_session, run_accession_id=protocol_run_id,
            )
            if not protocol_run_orm:
                msg = f"Protocol run {protocol_run_id} not found."
                raise ValueError(msg)

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

            result_run_orm = await orchestrator.execute_existing_protocol_run(
                protocol_run_orm, input_parameters, validated_initial_state,
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
            raise


async def _update_run_status_on_error(
    protocol_run_id: uuid.UUID,
    error_message: str,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """A final-resort function to update a protocol run's status to FAILED."""
    async with db_session_factory() as db_session:
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
        except Exception as e:
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
