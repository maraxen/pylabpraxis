"""Error handling and finalization logic for the Orchestrator."""

import datetime
import json
import traceback
import uuid
from typing import Any, cast

from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.core.asset_manager import AssetManager
from praxis.backend.core.protocols.scheduler import IProtocolScheduler
from praxis.backend.core.workcell_runtime import WorkcellRuntime
from praxis.backend.models import (
  MachineStatusEnum,
  ProtocolRunOrm,
  ProtocolRunStatusEnum,
  ResourceStatusEnum,
)
from praxis.backend.services.protocols import ProtocolRunService
from praxis.backend.services.state import PraxisState
from praxis.backend.utils.errors import PyLabRobotGenericError, PyLabRobotVolumeError
from praxis.backend.utils.logging import get_logger

logger = get_logger(__name__)


class ErrorHandlingMixin:
  """Mixin for error handling and protocol finalization."""

  # Type hints for dependencies
  workcell_runtime: WorkcellRuntime
  asset_manager: AssetManager
  protocol_run_service: ProtocolRunService

  def _validate_praxis_state(self, praxis_state: PraxisState) -> None:
    """Validate the PraxisState object."""
    if praxis_state is None:
      msg = "PraxisState is None"
      raise ValueError(msg)

  async def _handle_protocol_execution_error(
    self,
    run_accession_id: uuid.UUID,
    protocol_def_name: str,
    e: Exception,
    praxis_state: PraxisState,
    db_session: AsyncSession,
  ) -> None:
    """Handle errors during protocol execution, including rollback and status update."""
    logger.exception(
      "ORCH: ERROR during protocol execution for run %s ('%s')",
      run_accession_id,
      protocol_def_name,
    )
    error_info = {
      "error_type": type(e).__name__,
      "error_message": str(e),
      "traceback": traceback.format_exc(),
    }

    try:
      self._validate_praxis_state(praxis_state)
      last_good_snapshot = praxis_state.get("workcell_last_successful_snapshot")
      if last_good_snapshot:
        self.workcell_runtime.apply_state_snapshot(last_good_snapshot)
        logger.warning(
          "ORCH: Workcell state for run %s rolled back successfully.",
          run_accession_id,
        )
      else:
        logger.warning(
          "ORCH: No prior workcell state snapshot found for run %s to rollback.",
          run_accession_id,
        )
    except Exception as rollback_error:  # pylint: disable=broad-except
      logger.critical(
        "ORCH: CRITICAL - Failed to rollback workcell state for run %s: %s",
        run_accession_id,
        rollback_error,
        exc_info=True,
      )

    final_run_status = ProtocolRunStatusEnum.FAILED
    status_details = json.dumps(error_info)

    if isinstance(e, PyLabRobotVolumeError):
      logger.info(
        "Specific PyLabRobot error 'VolumeError' detected for run %s. Setting status to REQUIRES_INTERVENTION.",
        run_accession_id,
      )
      final_run_status = ProtocolRunStatusEnum.REQUIRES_INTERVENTION
      status_details = json.dumps(
        {
          "error_type": "VolumeError",
          "error_message": str(e),
          "action_required": ("User intervention needed to verify liquid levels and proceed."),
          "traceback": traceback.format_exc(),
        },
      )
    elif isinstance(e, PyLabRobotGenericError):
      logger.info(
        "Generic PyLabRobot error detected for run %s. Setting status to FAILED.",
        run_accession_id,
      )
      final_run_status = ProtocolRunStatusEnum.FAILED
      status_details = json.dumps(
        {
          "error_type": type(e).__name__,
          "error_message": str(e),
          "details": "PyLabRobot operation failed.",
          "traceback": traceback.format_exc(),
        },
      )

    await self.protocol_run_service.update_run_status(
      db_session,
      run_accession_id,
      final_run_status,
      status_details,
    )

  async def _finalize_protocol_run(
    self,
    protocol_run_orm: ProtocolRunOrm,
    praxis_state: PraxisState,
    acquired_assets_info: dict[uuid.UUID, Any],
    db_session: AsyncSession,
  ) -> None:
    """Finalize the protocol run, update timestamps, state, and release assets."""
    run_accession_id = protocol_run_orm.accession_id
    logger.info("ORCH: Finalizing protocol run %s.", run_accession_id)

    protocol_run_orm.final_state_json = praxis_state.to_dict()

    if not protocol_run_orm.end_time:
      protocol_run_orm.end_time = datetime.datetime.now(datetime.timezone.utc)
    if (
      protocol_run_orm.start_time
      and protocol_run_orm.end_time
      and protocol_run_orm.duration_ms is None
    ):
      duration = protocol_run_orm.end_time - protocol_run_orm.start_time
      protocol_run_orm.duration_ms = int(duration.total_seconds() * 1000)

    # Release acquired assets
    if acquired_assets_info:
      logger.info(
        "ORCH: Releasing %d assets for run %s.",
        len(acquired_assets_info),
        run_accession_id,
      )
      for asset_orm_accession_id, asset_info in acquired_assets_info.items():
        try:
          asset_type = asset_info.get("type")
          name_in_protocol = asset_info.get("name_in_protocol", "UnknownAsset")

          if asset_type == "machine":
            await self.asset_manager.release_machine(
              machine_orm_accession_id=asset_orm_accession_id,
              final_status=MachineStatusEnum.AVAILABLE,
            )
          elif asset_type == "resource":
            await self.asset_manager.release_resource(
              resource_orm_accession_id=asset_orm_accession_id,
              final_status=ResourceStatusEnum.AVAILABLE_IN_STORAGE,
            )
          logger.info(
            "ORCH-RELEASE: Asset '%s' (Type: %s, ORM ID: %s) released.",
            name_in_protocol,
            asset_type,
            asset_orm_accession_id,
          )
        except Exception:  # pylint: disable=broad-except
          logger.exception(
            "ORCH-RELEASE: Failed to release asset '%s' (ORM ID: %s)",
            asset_info.get("name_in_protocol", "UnknownAsset"),
            asset_info.get("orm_accession_id"),
          )

    await db_session.merge(protocol_run_orm)

    # Release scheduler reservations
    # Note: self.scheduler is typed as Any | None in Orchestrator, so we check for existence
    if hasattr(self, "scheduler") and self.scheduler:
      try:
        await cast(IProtocolScheduler, self.scheduler).complete_scheduled_run(run_accession_id)
      except Exception:
        logger.exception(
          "ORCH: Failed to complete scheduled run %s in scheduler",
          run_accession_id,
        )
