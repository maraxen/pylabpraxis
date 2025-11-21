"""Protocol execution logic for the Orchestrator."""

import asyncio
import datetime
import inspect
import json
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import praxis.backend.services as svc
from praxis.backend.core.protocol_code_manager import ProtocolCodeManager
from praxis.backend.core.run_context import PraxisRunContext
from praxis.backend.core.workcell_runtime import WorkcellRuntime
from praxis.backend.models import (
  FunctionProtocolDefinitionOrm,
  ProtocolRunOrm,
  ProtocolRunStatusEnum,
)
from praxis.backend.services.state import PraxisState
from praxis.backend.utils.errors import ProtocolCancelledError
from praxis.backend.utils.logging import get_logger
from praxis.backend.utils.run_control import clear_control_command, get_control_command
from praxis.backend.utils.uuid import uuid7

logger = get_logger(__name__)


class ExecutionMixin:
  """Mixin for executing protocols."""

  # Type hints for dependencies
  db_session_factory: async_sessionmaker[AsyncSession]
  workcell_runtime: WorkcellRuntime
  protocol_code_manager: ProtocolCodeManager

  # Type hints for methods from other mixins
  async def _get_protocol_definition_orm_from_db(self, *args, **kwargs) -> Any: ...
  async def _prepare_protocol_code(self, *args, **kwargs) -> Any: ...
  async def _initialize_run_context(self, *args, **kwargs) -> Any: ...
  async def _prepare_arguments(self, *args, **kwargs) -> Any: ...
  async def _finalize_protocol_run(self, *args, **kwargs) -> Any: ...
  async def _handle_protocol_execution_error(self, *args, **kwargs) -> Any: ...

  async def _handle_pre_execution_checks(
    self,
    protocol_run_orm: ProtocolRunOrm,
    db_session: AsyncSession,
  ) -> None:
    """Handle pause/cancel commands before main execution starts."""
    run_accession_id = protocol_run_orm.run_accession_id
    command = await get_control_command(run_accession_id)

    if command == "PAUSE":
      logger.info("ORCH: Run %s PAUSED before execution.", run_accession_id)
      await clear_control_command(run_accession_id)
      await svc.update_protocol_run_status(
        db_session,
        protocol_run_orm.accession_id,
        ProtocolRunStatusEnum.PAUSED,
      )
      await db_session.commit()
      while True:
        await asyncio.sleep(1)
        new_command = await get_control_command(run_accession_id)
        if new_command == "RESUME":
          logger.info("ORCH: Run %s RESUMING.", run_accession_id)
          await clear_control_command(run_accession_id)
          await svc.update_protocol_run_status(
            db_session,
            protocol_run_orm.accession_id,
            ProtocolRunStatusEnum.RUNNING,
          )
          await db_session.commit()
          break
        if new_command == "CANCEL":
          logger.info("ORCH: Run %s CANCELLED during pause.", run_accession_id)
          await clear_control_command(run_accession_id)
          await svc.update_protocol_run_status(
            db_session,
            protocol_run_orm.accession_id,
            ProtocolRunStatusEnum.CANCELLED,
            output_data_json=json.dumps({"status": "Cancelled by user during pause."}),
          )
          await db_session.commit()
          cancel_msg = f"Run {run_accession_id} cancelled by user during pause."
          raise ProtocolCancelledError(cancel_msg)
    elif command == "CANCEL":
      logger.info("ORCH: Run %s CANCELLED before execution.", run_accession_id)
      await clear_control_command(run_accession_id)
      await svc.update_protocol_run_status(
        db_session,
        protocol_run_orm.accession_id,
        ProtocolRunStatusEnum.CANCELLED,
        output_data_json=json.dumps({"status": "Cancelled by user before execution."}),
      )
      await db_session.commit()
      cancel_msg = f"Run {run_accession_id} cancelled by user before execution."
      raise ProtocolCancelledError(cancel_msg)

  async def _execute_protocol_main_logic(
    self,
    protocol_run_orm: ProtocolRunOrm,
    protocol_def_orm: FunctionProtocolDefinitionOrm,
    input_parameters: dict[str, Any],
    praxis_state: PraxisState,
    run_context: PraxisRunContext,
    db_session: AsyncSession,
  ) -> tuple[Any, dict[uuid.UUID, Any]]:  # Return result and acquired_assets_info
    """Execute the core protocol logic, including asset acquisition and function call."""
    run_accession_id = protocol_run_orm.run_accession_id

    callable_protocol_func, protocol_pydantic_def = await self._prepare_protocol_code(
      protocol_def_orm,
    )

    main_workcell_container = self.workcell_runtime.get_main_workcell()
    if not main_workcell_container:
      error_msg = "Main Workcell container not available from WorkcellRuntime."
      raise RuntimeError(error_msg)

    (
      prepared_args,
      _,
      acquired_assets_info,
    ) = await self._prepare_arguments(  # acquired_assets_info is populated here
      db_session=db_session,
      protocol_pydantic_def=protocol_pydantic_def,
      input_parameters=input_parameters,
      praxis_state=praxis_state,
      protocol_run_accession_id=run_accession_id,
    )

    protocol_run_orm.resolved_assets_json = acquired_assets_info
    await db_session.merge(protocol_run_orm)
    await db_session.flush()

    # Load deck construction function if specified
    deck_construction_func = None
    if protocol_pydantic_def.deck_construction_function_fqn:
      deck_construction_func = self.protocol_code_manager._load_callable_from_fqn(
        protocol_pydantic_def.deck_construction_function_fqn,
      )

    # Execute deck construction function if provided
    if deck_construction_func:
      logger.info(
        "ORCH: Executing deck construction function for run %s.",
        run_accession_id,
      )
      # Filter prepared_args to only include assets expected by deck_construction_func
      deck_construction_params = inspect.signature(deck_construction_func).parameters
      args_for_deck_construction = {
        k: v for k, v in prepared_args.items() if k in deck_construction_params
      }
      await deck_construction_func(**args_for_deck_construction)
      logger.info(
        "ORCH: Deck construction function completed for run %s.",
        run_accession_id,
      )

    logger.info(
      "ORCH: Executing protocol '%s' for run %s.",
      protocol_pydantic_def.name,
      run_accession_id,
    )
    result = await callable_protocol_func(
      **prepared_args,
      __praxis_run_context__=run_context,
      __function_db_accession_id__=protocol_def_orm.accession_id,
    )
    logger.info(
      "ORCH: Protocol '%s' run %s completed successfully.",
      protocol_pydantic_def.name,
      run_accession_id,
    )
    return result, acquired_assets_info  # Return acquired_assets_info

  async def execute_protocol(
    self,
    protocol_name: str,
    input_parameters: dict[str, Any] | None = None,
    initial_state_data: dict[str, Any] | None = None,
    protocol_version: str | None = None,
    commit_hash: str | None = None,
    source_name: str | None = None,
  ) -> ProtocolRunOrm:
    """Execute a specified protocol."""
    input_parameters = input_parameters or {}
    initial_state_data = initial_state_data or {}
    run_accession_id = uuid7()
    start_iso_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    logger.info(
      "ORCH: Initiating protocol run %s for '%s' at %s. User params: %s, Initial state: %s",
      run_accession_id,
      protocol_name,
      start_iso_timestamp,
      input_parameters,
      initial_state_data,
    )

    async with self.db_session_factory() as db_session:
      protocol_def_orm = await self._get_protocol_definition_orm_from_db(
        db_session,
        protocol_name,
        protocol_version,
        commit_hash,
        source_name,
      )

      if not protocol_def_orm or not protocol_def_orm.accession_id:
        error_msg = (
          f"Protocol '{protocol_name}' (v:{protocol_version}, commit:{commit_hash}, "
          f"src:{source_name}) not found or invalid DB ID."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

      # Create protocol run record
      protocol_run_db_obj = await svc.create_protocol_run(
        db=db_session,
        run_accession_id=run_accession_id,
        top_level_protocol_definition_accession_id=protocol_def_orm.accession_id,
        status=ProtocolRunStatusEnum.PREPARING,
        input_parameters_json=json.dumps(input_parameters),
        initial_state_json=json.dumps(initial_state_data),
      )
      await db_session.flush()
      await db_session.refresh(protocol_run_db_obj)

      # Initialize run context
      run_context = await self._initialize_run_context(
        protocol_run_db_obj,
        initial_state_data,
        db_session,
      )
      praxis_state = run_context.canonical_state  # For direct access in this method

      # Handle pre-execution commands (PAUSE/CANCEL)
      await self._handle_pre_execution_checks(protocol_run_db_obj, db_session)

      # Update status to RUNNING if not already cancelled/paused
      await db_session.refresh(protocol_run_db_obj)
      if protocol_run_db_obj.status == ProtocolRunStatusEnum.PREPARING:
        await svc.update_protocol_run_status(
          db_session,
          protocol_run_db_obj.accession_id,
          ProtocolRunStatusEnum.RUNNING,
        )
        await db_session.commit()

      result: Any = None
      acquired_assets_info: dict[uuid.UUID, Any] = {}

      try:
        result, acquired_assets_info = await self._execute_protocol_main_logic(
          protocol_run_db_obj,
          protocol_def_orm,
          input_parameters,
          praxis_state,
          run_context,
          db_session,
        )
        await svc.update_protocol_run_status(
          db_session,
          protocol_run_db_obj.accession_id,
          ProtocolRunStatusEnum.COMPLETED,
          output_data_json=json.dumps(result, default=str),
        )
      except ProtocolCancelledError:
        pass  # Status already updated by the handler
      except Exception as e:  # pylint: disable=broad-except # noqa: BLE001
        await self._handle_protocol_execution_error(
          run_accession_id,
          protocol_def_orm.name,
          e,
          praxis_state,
          db_session,
        )
      finally:
        await self._finalize_protocol_run(
          protocol_run_db_obj,
          praxis_state,
          acquired_assets_info,
          db_session,
        )
        try:
          await db_session.commit()
          logger.info("ORCH: Final DB commit for run %s successful.", run_accession_id)
        except Exception as db_final_err:  # pylint: disable=broad-except
          logger.error(
            "ORCH: CRITICAL - Failed to commit final updates for run %s: %s",
            run_accession_id,
            db_final_err,
            exc_info=True,
          )
          await db_session.rollback()

      await db_session.refresh(protocol_run_db_obj)
      return protocol_run_db_obj

  async def execute_existing_protocol_run(
    self,
    protocol_run_orm: ProtocolRunOrm,
    user_input_params: dict[str, Any] | None = None,
    initial_state_data: dict[str, Any] | None = None,
  ) -> ProtocolRunOrm:
    """Execute an existing protocol run (typically called from Celery workers)."""
    user_input_params = user_input_params or {}
    initial_state_data = initial_state_data or {}
    run_accession_id = protocol_run_orm.accession_id

    protocol_name = (
      protocol_run_orm.top_level_protocol_definition.name
      if protocol_run_orm.top_level_protocol_definition
      else "Unknown"
    )
    logger.info(
      "ORCH: Executing existing protocol run %s for '%s'. User params: %s, Initial state: %s",
      run_accession_id,
      protocol_name,
      user_input_params,
      initial_state_data,
    )

    async with self.db_session_factory() as db_session:
      # Refresh the protocol run object and load relationships
      await db_session.refresh(protocol_run_orm)

      if not protocol_run_orm.top_level_protocol_definition:
        error_msg = f"Protocol definition not found for run {run_accession_id}"
        logger.error(error_msg)
        await svc.update_protocol_run_status(
          db_session,
          run_accession_id,
          ProtocolRunStatusEnum.FAILED,
          output_data_json=json.dumps(
            {
              "error": error_msg,
              "details": "Protocol definition not loaded or missing.",
            },
          ),
        )
        await db_session.commit()
        raise ValueError(error_msg)

      protocol_def_orm = protocol_run_orm.top_level_protocol_definition

      # Initialize state and context
      run_context = await self._initialize_run_context(
        protocol_run_orm,
        initial_state_data,
        db_session,
      )
      praxis_state = run_context.canonical_state

      # Handle pre-execution commands (PAUSE/CANCEL)
      await self._handle_pre_execution_checks(protocol_run_orm, db_session)

      # Update status to RUNNING if not already cancelled/paused
      await db_session.refresh(protocol_run_orm)
      if protocol_run_orm.status in [
        ProtocolRunStatusEnum.PREPARING,
        ProtocolRunStatusEnum.QUEUED,
      ]:
        await svc.update_protocol_run_status(
          db_session,
          protocol_run_orm.accession_id,
          ProtocolRunStatusEnum.RUNNING,
        )
        await db_session.commit()

      result: Any = None
      acquired_assets_info: dict[uuid.UUID, Any] = {}

      try:
        result, acquired_assets_info = await self._execute_protocol_main_logic(
          protocol_run_orm,
          protocol_def_orm,
          user_input_params,
          praxis_state,
          run_context,
          db_session,
        )
        await svc.update_protocol_run_status(
          db_session,
          protocol_run_orm.accession_id,
          ProtocolRunStatusEnum.COMPLETED,
          output_data_json=json.dumps(result, default=str),
        )
      except ProtocolCancelledError:
        pass  # Status already updated by the handler
      except Exception as e:  # pylint: disable=broad-except # noqa: BLE001
        await self._handle_protocol_execution_error(
          run_accession_id,
          protocol_def_orm.name,
          e,
          praxis_state,
          db_session,
        )
      finally:
        # The ORM object might be stale after the try/except block, especially
        # if status was updated. We get the latest version before finalizing.
        final_run_orm = await db_session.get(ProtocolRunOrm, run_accession_id)
        if final_run_orm:
          await self._finalize_protocol_run(
            final_run_orm,
            praxis_state,
            acquired_assets_info,
            db_session,
          )
        else:  # Should not happen in normal operation
          logger.error(
            "Could not retrieve ProtocolRunOrm with ID %s for finalization.",
            run_accession_id,
          )

        try:
          await db_session.commit()
          logger.info("ORCH: Final DB commit for run %s successful.", run_accession_id)
        except Exception as db_final_err:
          logger.error(
            "ORCH: CRITICAL - Failed to commit final updates for run %s: %s",
            run_accession_id,
            db_final_err,
            exc_info=True,
          )
          await db_session.rollback()

      await db_session.refresh(protocol_run_orm)
      return protocol_run_orm
