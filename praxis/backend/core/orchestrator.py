# pylint: disable=too-many-arguments,too-many-locals,fixme,unused-argument
"""The Orchestrator manages the lifecycle of protocol runs."""
# broad-except is justified at method level where necessary.

import asyncio
import datetime
import inspect
import json
import traceback
import uuid
from collections.abc import Callable
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import praxis.backend.services as svc
from praxis.backend.core.asset_manager import AssetManager
from praxis.backend.core.protocol_code_manager import ProtocolCodeManager
from praxis.backend.core.run_context import PraxisRunContext
from praxis.backend.core.workcell_runtime import WorkcellRuntime
from praxis.backend.models import (
  FunctionProtocolDefinitionCreate,
  FunctionProtocolDefinitionOrm,
  MachineStatusEnum,
  ProtocolRunOrm,
  ProtocolRunStatusEnum,
  ResourceStatusEnum,
)
from praxis.backend.services.state import PraxisState
from praxis.backend.utils.errors import (
  AssetAcquisitionError,
  ProtocolCancelledError,
  PyLabRobotGenericError,
  PyLabRobotVolumeError,
)
from praxis.backend.utils.logging import get_logger
from praxis.backend.utils.run_control import clear_control_command, get_control_command
from praxis.backend.utils.uuid import uuid7

logger = get_logger(__name__)


class Orchestrator:
  """Central component for managing and executing laboratory protocols.

  The Orchestrator is responsible for coordinating the execution of protocols.
  It coordinates asset allocation, runtime environment setup, protocol execution,
  logging, and run control.
  """

  def __init__(
    self,
    db_session_factory: async_sessionmaker[AsyncSession],
    asset_manager: AssetManager,
    workcell_runtime: WorkcellRuntime,
    protocol_code_manager: ProtocolCodeManager | None = None,
  ) -> None:
    """Initialize the Orchestrator.

    Args:
        db_session_factory: A factory to create SQLAlchemy AsyncSession instances.
        asset_manager: An instance of AssetManager for asset allocation.
        workcell_runtime: An instance of WorkcellRuntime to manage live PLR objects.
        protocol_code_manager: An instance of ProtocolCodeManager for code preparation.
            If None, a new instance will be created.

    Raises:
        ValueError: If any of the arguments are invalid.
        TypeError: If any of the arguments are of the wrong type.

    """
    self.db_session_factory = db_session_factory
    self.asset_manager = asset_manager
    self.workcell_runtime = workcell_runtime
    self.protocol_code_manager = protocol_code_manager or ProtocolCodeManager()
    logger.info("Orchestrator initialized.")

  async def _get_protocol_definition_orm_from_db(
    self,
    db_session: AsyncSession,
    protocol_name: str,
    version: str | None = None,
    commit_hash: str | None = None,
    source_name: str | None = None,
  ) -> FunctionProtocolDefinitionOrm | None:
    """Retrieve a protocol definition ORM from the database.

    Args:
      db_session: The SQLAlchemy AsyncSession to use for database operations.
      protocol_name: The name of the protocol to fetch.
      version: Optional version of the protocol. If None, fetches the latest version.
      commit_hash: Optional commit hash if the protocol is from a Git source.
      source_name: Optional name of the source (Git repo or FileSystem).

    Returns:
      An instance of FunctionProtocolDefinitionOrm if found, otherwise None.

    Raises:
      ValueError: If the protocol name is empty or invalid.
      RuntimeError: If there is an error fetching the protocol definition from the
      database.

    """
    logger.debug(
      "Fetching protocol ORM: Name='%s', Version='%s', Commit='%s', Source='%s'",
      protocol_name,
      version,
      commit_hash,
      source_name,
    )
    return await svc.read_protocol_definition_by_name(
      db=db_session,
      name=protocol_name,
      version=version,
      source_name=source_name,
      commit_hash=commit_hash,
    )

  async def _prepare_protocol_code(
    self,
    protocol_def_orm: FunctionProtocolDefinitionOrm,
  ) -> tuple[Callable, FunctionProtocolDefinitionCreate]:
    """Load the protocol code from its source using the ProtocolCodeManager.

    Args:
      protocol_def_orm: The ORM object representing the protocol definition.

    Returns:
      A tuple containing the callable function and its Pydantic definition model.

    Raises:
      ValueError: If the protocol definition is incomplete or invalid.
      AttributeError: If the function or its Pydantic definition is not found.
      RuntimeError: If there is an error preparing the protocol code.

    """
    return await self.protocol_code_manager.prepare_protocol_code(protocol_def_orm)

  async def _initialize_run_context(
    self,
    protocol_run_orm: ProtocolRunOrm,
    initial_state_data: dict[str, Any],
    db_session: AsyncSession,
  ) -> PraxisRunContext:
    """Initialize PraxisState and PraxisRunContext for a protocol run."""
    praxis_state = PraxisState(run_accession_id=protocol_run_orm.run_accession_id)
    if initial_state_data:
      praxis_state.update(initial_state_data)

    logger.debug(
      "Initializing PraxisState for run %s with initial data: %s",
      protocol_run_orm.run_accession_id,
      initial_state_data,
    )

    if praxis_state is None:
      error_msg = "Failed to initialize PraxisState for the protocol run."
      logger.error(error_msg)
      raise RuntimeError(error_msg)

    current_workcell_snapshot = self.workcell_runtime.get_state_snapshot()
    await praxis_state.set(
      "workcell_last_successful_snapshot",
      current_workcell_snapshot,
    )
    logger.debug(
      "Workcell state snapshot captured and stored in PraxisState for run %s.",
      protocol_run_orm.run_accession_id,
    )

    return PraxisRunContext(
      run_accession_id=protocol_run_orm.run_accession_id,
      canonical_state=praxis_state,
      current_db_session=db_session,
      current_call_log_db_accession_id=None,
    )

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
    deck_construction_func: Callable | None = None
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

  def _process_input_parameters(
    self,
    protocol_pydantic_def: FunctionProtocolDefinitionCreate,
    input_parameters: dict[str, Any],
    final_args: dict[str, Any],
  ) -> None:
    """Process input parameters and populate final_args."""
    for param_meta in protocol_pydantic_def.parameters:
      if param_meta.is_deck_param:
        continue
      if param_meta.name == protocol_pydantic_def.state_param_name:
        continue

      if param_meta.name in input_parameters:
        final_args[param_meta.name] = input_parameters[param_meta.name]
        logger.debug("Using user input for param '%s'.", param_meta.name)
      elif not param_meta.optional:
        error_msg = f"Mandatory parameter '{param_meta.name}' missing for protocol "
        f"'{protocol_pydantic_def.name}'."
        raise ValueError(error_msg)
      else:
        logger.debug("Optional param '%s' not provided by user.", param_meta.name)

  def _inject_praxis_state(
    self,
    protocol_pydantic_def: FunctionProtocolDefinitionCreate,
    praxis_state: PraxisState,
    final_args: dict[str, Any],
  ) -> dict[str, Any] | None:
    """Inject PraxisState object or its dictionary representation into final_args."""
    state_dict_to_pass: dict[str, Any] | None = None
    if protocol_pydantic_def.state_param_name:
      state_param_meta = next(
        (
          p
          for p in protocol_pydantic_def.parameters
          if p.name == protocol_pydantic_def.state_param_name
        ),
        None,
      )
      if state_param_meta:
        if "PraxisState" in state_param_meta.actual_type_str:
          final_args[protocol_pydantic_def.state_param_name] = praxis_state
          logger.debug(
            "Injecting PraxisState object for param '%s'.",
            protocol_pydantic_def.state_param_name,
          )
        elif "dict" in state_param_meta.actual_type_str.lower():
          state_dict_to_pass = praxis_state.to_dict()
          final_args[protocol_pydantic_def.state_param_name] = state_dict_to_pass
          logger.debug(
            "Injecting state dictionary for param '%s'.",
            protocol_pydantic_def.state_param_name,
          )
        else:
          final_args[protocol_pydantic_def.state_param_name] = praxis_state
          logger.debug(
            "Defaulting to injecting PraxisState object for param '%s'.",
            protocol_pydantic_def.state_param_name,
          )
    return state_dict_to_pass

  async def _acquire_assets(
    self,
    protocol_pydantic_def: FunctionProtocolDefinitionCreate,
    protocol_run_accession_id: uuid.UUID,
    final_args: dict[str, Any],
    acquired_assets_details: dict[uuid.UUID, Any],
  ) -> None:
    """Acquire assets required by the protocol."""
    for asset_req_model in protocol_pydantic_def.assets:
      try:
        logger.info(
          "ORCH-ACQUIRE: Acquiring asset '%s' (Type: '%s', Optional: %s) for run '%s'.",
          asset_req_model.name,
          asset_req_model.fqn,
          asset_req_model.optional,
          protocol_run_accession_id,
        )
        (
          live_obj,
          orm_accession_id,
          asset_kind_str,
        ) = await self.asset_manager.acquire_asset(
          protocol_run_accession_id=protocol_run_accession_id,
          asset_requirement=asset_req_model,
        )
        final_args[asset_req_model.name] = live_obj
        acquired_assets_details[orm_accession_id] = {
          "type": asset_kind_str,
          "orm_accession_id": orm_accession_id,
          "name_in_protocol": asset_req_model.name,
        }
        logger.info(
          "ORCH-ACQUIRE: Asset '%s' (Kind: %s, ORM ID: %s) acquired: %s",
          asset_req_model.name,
          asset_kind_str,
          orm_accession_id,
          live_obj,
        )
      except AssetAcquisitionError as e:
        if asset_req_model.optional:
          logger.warning(
            "ORCH-ACQUIRE: Optional asset '%s' could not be acquired: %s. Proceeding as it's optional.",
            asset_req_model.name,
            e,
          )
          final_args[asset_req_model.name] = None
        else:
          error_msg = (
            f"Failed to acquire mandatory asset '{asset_req_model.name}' for "
            f"protocol '{protocol_pydantic_def.name}': {e}"
          )
          logger.exception(error_msg)
          raise ValueError(error_msg) from e
      except Exception as e_general:
        error_msg = (
          f"Unexpected error acquiring asset '{asset_req_model.name}' for "
          f"protocol '{protocol_pydantic_def.name}': {e_general}"
        )
        logger.exception(error_msg)
        raise ValueError(error_msg) from e_general

  async def _handle_deck_preconfiguration(
    self,
    db_session: AsyncSession,
    protocol_pydantic_def: FunctionProtocolDefinitionCreate,
    input_parameters: dict[str, Any],
    protocol_run_accession_id: uuid.UUID,
    final_args: dict[str, Any],
  ) -> None:
    """Handle deck preconfiguration if specified in the protocol definition."""
    if protocol_pydantic_def.preconfigure_deck and protocol_pydantic_def.deck_param_name:
      deck_param_name = protocol_pydantic_def.deck_param_name
      deck_accession_identifier_from_user = input_parameters.get(deck_param_name)

      if deck_accession_identifier_from_user is None and not next(
        (p for p in protocol_pydantic_def.parameters if p.name == deck_param_name and p.optional),
        False,
      ):
        error_msg = (
          f"Mandatory deck parameter '{deck_param_name}' for preconfiguration not provided."
        )
        raise ValueError(error_msg)

      if deck_accession_identifier_from_user is not None:
        if not isinstance(deck_accession_identifier_from_user, str | uuid.UUID):
          error_msg = (
            f"Deck identifier for preconfiguration ('{deck_param_name}') must be "
            f"a string (name) or UUID (ID), got {type(deck_accession_identifier_from_user)}."
          )
          raise ValueError(error_msg)

        logger.info(
          "ORCH-DECK: Applying deck instantiation '%s' for run '%s'.",
          deck_accession_identifier_from_user,
          protocol_run_accession_id,
        )

        deck_config_orm_accession_id_to_apply: uuid.UUID | None = None
        if isinstance(deck_accession_identifier_from_user, str):
          deck_config_orm = await svc.read_deck_by_name(
            db_session,
            deck_accession_identifier_from_user,
          )
          if not deck_config_orm:
            error_msg = (
              f"Deck configuration named '{deck_accession_identifier_from_user}' not found."
            )
            raise ValueError(error_msg)
          deck_config_orm_accession_id_to_apply = deck_config_orm.accession_id
        elif isinstance(deck_accession_identifier_from_user, uuid.UUID):
          deck_config_orm_accession_id_to_apply = deck_accession_identifier_from_user

        if deck_config_orm_accession_id_to_apply is None:
          raise RuntimeError("Internal error: Deck accession ID not resolved.")

        live_deck_object = await self.asset_manager.apply_deck(
          deck_orm_accession_id=deck_config_orm_accession_id_to_apply,
          protocol_run_accession_id=protocol_run_accession_id,
        )
        final_args[deck_param_name] = live_deck_object
        logger.info(
          "ORCH-DECK: Deck '%s' configured and injected as '%s'.",
          live_deck_object.name,
          deck_param_name,
        )
      elif deck_param_name in final_args:
        logger.warning(
          "Deck parameter '%s' was already processed (e.g., as an asset). Review protocol definition.",
          deck_param_name,
        )

  async def _prepare_arguments(
    self,
    db_session: AsyncSession,
    protocol_pydantic_def: FunctionProtocolDefinitionCreate,
    input_parameters: dict[str, Any],
    praxis_state: PraxisState,
    protocol_run_accession_id: uuid.UUID,
  ) -> tuple[dict[str, Any], dict[str, Any] | None, dict[uuid.UUID, Any]]:
    """Prepare arguments for protocol execution, including acquiring assets."""
    logger.info("Preparing arguments for protocol: %s", protocol_pydantic_def.name)
    final_args: dict[str, Any] = {}
    state_dict_to_pass: dict[str, Any] | None = None
    acquired_assets_details: dict[uuid.UUID, Any] = {}

    self._process_input_parameters(
      protocol_pydantic_def,
      input_parameters,
      final_args,
    )
    state_dict_to_pass = self._inject_praxis_state(
      protocol_pydantic_def,
      praxis_state,
      final_args,
    )
    await self._acquire_assets(
      db_session,
      protocol_pydantic_def,
      protocol_run_accession_id,
      final_args,
      acquired_assets_details,
    )
    await self._handle_deck_preconfiguration(
      db_session,
      protocol_pydantic_def,
      input_parameters,
      protocol_run_accession_id,
      final_args,
    )

    return final_args, state_dict_to_pass, acquired_assets_details

  async def _handle_protocol_execution_error(
    self,
    run_accession_id: uuid.UUID,
    protocol_def_name: str,
    e: Exception,
    praxis_state: PraxisState,
    db_session: AsyncSession,
  ) -> None:
    """Handle errors during protocol execution, including rollback and status update."""
    logger.error(
      "ORCH: ERROR during protocol execution for run %s ('%s'): %s",
      run_accession_id,
      protocol_def_name,
      e,
      exc_info=True,
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
    except Exception as rollback_error:  # pylint: disable=broad-except # noqa: BLE001
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

    await svc.update_protocol_run_status(
      db_session,
      run_accession_id,
      final_run_status,
      status_details,
    )

  async def _finalize_protocol_run(  # This method was already correct, but its usage was not.
    self,
    protocol_run_orm: ProtocolRunOrm,
    praxis_state: PraxisState,
    acquired_assets_info: dict[uuid.UUID, Any],
    db_session: AsyncSession,
  ) -> None:
    """Finalize the protocol run, update timestamps, state, and release assets."""
    run_accession_id = protocol_run_orm.run_accession_id
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
        except Exception as release_err:  # pylint: disable=broad-except
          logger.error(
            "ORCH-RELEASE: Failed to release asset '%s' (ORM ID: %s): %s",
            asset_info.get("name_in_protocol", "UnknownAsset"),
            asset_info.get("orm_accession_id"),
            release_err,
            exc_info=True,
          )

    await db_session.merge(protocol_run_orm)

  async def execute_protocol(
    self,
    protocol_name: str,
    input_parameters: dict[str, Any] | None = None,
    initial_state_data: dict[str, Any] | None = None,
    protocol_version: str | None = None,
    commit_hash: str | None = None,
    source_name: str | None = None,
  ) -> ProtocolRunOrm:
    """Execute a specified protocol.

    Args:
      protocol_name: Name of the protocol to execute.
      input_parameters: Dictionary of parameters provided by the user.
      initial_state_data: Initial data for the PraxisState.
      protocol_version: Specific version of the protocol.
      commit_hash: Specific commit hash if from a Git source.
      source_name: Name of the protocol source (Git repo or FS).

    Returns:
      The ProtocolRunOrm object representing the completed or failed run.

    Raises:
      ValueError: If the protocol definition is not found or invalid.
      ProtocolCancelledError: If the protocol run is cancelled by the user.
      RuntimeError: If there is an error during protocol execution or preparation.

    """
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
