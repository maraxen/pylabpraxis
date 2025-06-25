# pylint: disable=too-many-arguments,too-many-locals,broad-except,fixme,\
#   unused-argument,too-many-statements,too-many-branches
"""The Orchestrator manages the lifecycle of protocol runs."""

import asyncio
import datetime
import json
import traceback
import uuid
from typing import Any, Callable, Dict, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import praxis.backend.services as svc
from praxis.backend.core.asset_manager import AssetManager
from praxis.backend.core.protocol_code_manager import ProtocolCodeManager
from praxis.backend.core.run_context import PraxisRunContext
from praxis.backend.core.workcell import WorkcellView
from praxis.backend.core.workcell_runtime import WorkcellRuntime
from praxis.backend.models import (
  FunctionProtocolDefinitionModel,
  FunctionProtocolDefinitionOrm,
  MachineStatusEnum,
  ProtocolRunOrm,
  ProtocolRunStatusEnum,
  ResourceInstanceStatusEnum,
)
from praxis.backend.services.state import PraxisState as PraxisState
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
    protocol_code_manager: Optional[ProtocolCodeManager] = None,
  ):
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
    version: Optional[str] = None,
    commit_hash: Optional[str] = None,
    source_name: Optional[str] = None,
  ) -> Optional[FunctionProtocolDefinitionOrm]:
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
    self, protocol_def_orm: FunctionProtocolDefinitionOrm
  ) -> Tuple[Callable, FunctionProtocolDefinitionModel]:
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

  async def _prepare_arguments(
    self,
    db_session: AsyncSession,
    protocol_pydantic_def: FunctionProtocolDefinitionModel,
    input_parameters: Dict[str, Any],
    praxis_state: PraxisState,
    workcell_view: WorkcellView,
    protocol_run_accession_id: uuid.UUID,
  ) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]], Dict[uuid.UUID, Any]]:
    """Prepare arguments for protocol execution, including acquiring assets."""
    logger.info("Preparing arguments for protocol: %s", protocol_pydantic_def.name)
    final_args: Dict[str, Any] = {}
    state_dict_to_pass: Optional[Dict[str, Any]] = None
    acquired_assets_details: Dict[uuid.UUID, Any] = {}

    for param_meta in protocol_pydantic_def.parameters:
      if param_meta.is_deck_param:
        continue
      if param_meta.name == protocol_pydantic_def.state_param_name:
        continue

      if param_meta.name in input_parameters:
        final_args[param_meta.name] = input_parameters[param_meta.name]
        logger.debug("Using user input for param '%s'.", param_meta.name)
      elif not param_meta.optional:
        raise ValueError(
          "Mandatory parameter '%s' missing for protocol '%s'.",
          param_meta.name,
          protocol_pydantic_def.name,
        )
      else:
        logger.debug("Optional param '%s' not provided by user.", param_meta.name)

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
            "ORCH-ACQUIRE: Optional asset '%s' could not be acquired: %s."
            " Proceeding as it's optional.",
            asset_req_model.name,
            e,
          )
          final_args[asset_req_model.name] = None
        else:
          error_msg = (
            "Failed to acquire mandatory asset '%s' for protocol '%s': %s"
          ) % (
            asset_req_model.name,
            protocol_pydantic_def.name,
            e,
          )
          logger.error(error_msg)
          raise ValueError(error_msg) from e
      except Exception as e_general:
        error_msg = ("Unexpected error acquiring asset '%s' for protocol '%s': %s") % (
          asset_req_model.name,
          protocol_pydantic_def.name,
          e_general,
        )
        logger.error(error_msg, exc_info=True)
        raise ValueError(error_msg) from e_general

    if (
      protocol_pydantic_def.preconfigure_deck and protocol_pydantic_def.deck_param_name
    ):
      deck_param_name = protocol_pydantic_def.deck_param_name
      deck_accession_identifier_from_user = input_parameters.get(deck_param_name)

      if deck_accession_identifier_from_user is None and not next(
        (
          p
          for p in protocol_pydantic_def.parameters
          if p.name == deck_param_name and p.optional
        ),
        False,
      ):
        raise ValueError(
          "Mandatory deck parameter '%s' for preconfiguration not provided.",
          deck_param_name,
        )

      if deck_accession_identifier_from_user is not None:
        if not isinstance(deck_accession_identifier_from_user, (str, uuid.UUID)):
          raise ValueError(
            "Deck identifier for preconfiguration ('%s') must be a string "
            "(name) or UUID (ID), got %s.",
            deck_param_name,
            type(deck_accession_identifier_from_user),
          )

        logger.info(
          "ORCH-DECK: Applying deck instanceuration '%s' for run '%s'.",
          deck_accession_identifier_from_user,
          protocol_run_accession_id,
        )

        deck_config_orm_accession_id_to_apply: uuid.UUID
        if isinstance(deck_accession_identifier_from_user, str):
          deck_config_orm = await svc.read_deck_instance_by_name(
            db_session, deck_accession_identifier_from_user
          )
          if not deck_config_orm:
            raise ValueError(
              "Deck configuration named '%s' not found.",
              deck_accession_identifier_from_user,
            )
          deck_config_orm_accession_id_to_apply = deck_config_orm.accession_id
        else:
          deck_config_orm_accession_id_to_apply = deck_accession_identifier_from_user

        live_deck_object = await self.asset_manager.apply_deck_instance(
          deck_instance_orm_accession_id=deck_config_orm_accession_id_to_apply,
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
          "Deck parameter '%s' was already processed (e.g., as an asset)."
          " Review protocol definition.",
          deck_param_name,
        )

    return final_args, state_dict_to_pass, acquired_assets_details

  async def execute_protocol(
    self,
    protocol_name: str,
    input_parameters: Optional[Dict[str, Any]] = None,
    initial_state_data: Optional[Dict[str, Any]] = None,
    protocol_version: Optional[str] = None,
    commit_hash: Optional[str] = None,
    source_name: Optional[str] = None,
  ) -> ProtocolRunOrm:
    """Execute a specified protocol.

    Args:
      protocol_name: Name of the protocol to execute.
      user_input_params: Dictionary of parameters provided by the user.
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
      "ORCH: Initiating protocol run %s for '%s' at %s. "
      "User params: %s, Initial state: %s",
      run_accession_id,
      protocol_name,
      start_iso_timestamp,
      input_parameters,
      initial_state_data,
    )

    async with self.db_session_factory() as db_session:
      protocol_def_orm = await self._get_protocol_definition_orm_from_db(
        db_session, protocol_name, protocol_version, commit_hash, source_name
      )

      if not protocol_def_orm or not protocol_def_orm.accession_id:
        error_msg = (
          "Protocol '%s' (v:%s, commit:%s, src:%s) not found or invalid DB ID."
        ) % (protocol_name, protocol_version, commit_hash, source_name)
        logger.error(error_msg)

        protocol_def_accession_id_for_error_run = (
          protocol_def_orm.accession_id
          if protocol_def_orm and protocol_def_orm.accession_id
          else None
        )

        if protocol_def_accession_id_for_error_run is None:
          raise ProtocolCancelledError(
            f"Protocol definition '{protocol_name}' completely not found, cannot link "
            f"failed run to a definition."
          )

        error_run_db_obj = await svc.create_protocol_run(
          db=db_session,
          run_accession_id=run_accession_id,
          top_level_protocol_definition_accession_id=protocol_def_accession_id_for_error_run,
          status=ProtocolRunStatusEnum.FAILED,
          input_parameters_json=json.dumps(input_parameters),
          initial_state_json=json.dumps(initial_state_data),
        )
        await db_session.flush()
        await db_session.refresh(error_run_db_obj)
        await svc.update_protocol_run_status(
          db=db_session,
          protocol_run_accession_id=error_run_db_obj.accession_id,
          new_status=ProtocolRunStatusEnum.FAILED,
          output_data_json=json.dumps(
            {
              "error": error_msg,
              "details": "Protocol definition not found in database.",
            }
          ),
        )
        await db_session.commit()
        raise ValueError(error_msg)

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

      initial_command = await get_control_command(run_accession_id)
      if initial_command == "CANCEL":
        logger.info("ORCH: Run %s CANCELLED before preparation.", run_accession_id)
        await clear_control_command(run_accession_id)
        await svc.update_protocol_run_status(
          db_session,
          protocol_run_db_obj.accession_id,
          ProtocolRunStatusEnum.CANCELLED,
          output_data_json=json.dumps(
            {"status": "Cancelled by user before preparation."}
          ),
        )
        await db_session.commit()
        return protocol_run_db_obj

      praxis_state = PraxisState(run_accession_id=run_accession_id)
      if initial_state_data:
        praxis_state.update(initial_state_data)

      run_context = PraxisRunContext(
        run_accession_id=run_accession_id,
        canonical_state=praxis_state,
        current_db_session=db_session,
        current_call_log_db_accession_id=None,
      )

      prepared_args: Dict[str, Any] = {}
      callable_protocol_func: Optional[Callable] = None
      protocol_pydantic_def: Optional[FunctionProtocolDefinitionModel] = None
      state_dict_passed_to_top_level: Optional[Dict[str, Any]] = None
      acquired_assets_info: Dict[uuid.UUID, dict] = {}

      main_workcell_container = self.workcell_runtime.get_main_workcell()
      if not main_workcell_container:
        raise RuntimeError(
          "Main Workcell container not available from WorkcellRuntime."
        )

      # Capture snapshot of workcell state
      current_workcell_snapshot = self.workcell_runtime.get_state_snapshot()
      await praxis_state.set(
        "workcell_last_successful_snapshot", current_workcell_snapshot
      )
      logger.debug(
        "Workcell state snapshot captured and stored in PraxisState for run %s.",
        run_accession_id,
      )

      try:
        (
          callable_protocol_func,
          protocol_pydantic_def,
        ) = await self._prepare_protocol_code(protocol_def_orm)

        workcell_view_for_protocol = WorkcellView(
          parent_workcell=main_workcell_container,
          protocol_name=protocol_pydantic_def.name,
          required_assets=protocol_pydantic_def.assets,
        )

        (
          prepared_args,
          state_dict_passed_to_top_level,
          acquired_assets_info,
        ) = await self._prepare_arguments(
          db_session=db_session,
          protocol_pydantic_def=protocol_pydantic_def,
          input_parameters=input_parameters,
          praxis_state=praxis_state,
          workcell_view=workcell_view_for_protocol,
          protocol_run_accession_id=run_accession_id,
        )

        protocol_run_db_obj.resolved_assets_json = acquired_assets_info
        await db_session.merge(protocol_run_db_obj)
        await db_session.flush()

        command = await get_control_command(run_accession_id)
        if command == "PAUSE":
          logger.info("ORCH: Run %s PAUSED before execution.", run_accession_id)
          await clear_control_command(run_accession_id)
          await svc.update_protocol_run_status(
            db_session, protocol_run_db_obj.accession_id, ProtocolRunStatusEnum.PAUSED
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
                protocol_run_db_obj.accession_id,
                ProtocolRunStatusEnum.RUNNING,
              )
              await db_session.commit()
              break
            elif new_command == "CANCEL":
              logger.info("ORCH: Run %s CANCELLED during pause.", run_accession_id)
              await clear_control_command(run_accession_id)
              await svc.update_protocol_run_status(
                db_session,
                protocol_run_db_obj.accession_id,
                ProtocolRunStatusEnum.CANCELLED,
                output_data_json=json.dumps(
                  {"status": "Cancelled by user during pause."}
                ),
              )
              await db_session.commit()
              raise ProtocolCancelledError(
                f"Run {run_accession_id} cancelled by user during pause."
              )
        elif command == "CANCEL":
          logger.info("ORCH: Run %s CANCELLED before execution.", run_accession_id)
          await clear_control_command(run_accession_id)
          await svc.update_protocol_run_status(
            db_session,
            protocol_run_db_obj.accession_id,
            ProtocolRunStatusEnum.CANCELLED,
            output_data_json=json.dumps(
              {"status": "Cancelled by user before execution."}
            ),
          )
          await db_session.commit()
          raise ProtocolCancelledError(
            f"Run {run_accession_id} cancelled by user before execution."
          )

        current_run_status_orm = await db_session.get(
          ProtocolRunOrm, protocol_run_db_obj.accession_id
        )
        if (
          current_run_status_orm
          and current_run_status_orm.status != ProtocolRunStatusEnum.RUNNING
        ):
          await svc.update_protocol_run_status(
            db_session, protocol_run_db_obj.accession_id, ProtocolRunStatusEnum.RUNNING
          )
          await db_session.commit()

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

        await svc.update_protocol_run_status(
          db_session,
          protocol_run_db_obj.accession_id,
          ProtocolRunStatusEnum.COMPLETED,
          output_data_json=json.dumps(result, default=str),
        )

      except ProtocolCancelledError as pce:
        logger.info("ORCH: Protocol run %s was cancelled: %s", run_accession_id, pce)
        run_after_cancel = await db_session.get(
          ProtocolRunOrm, protocol_run_db_obj.accession_id
        )
        if (
          run_after_cancel
          and run_after_cancel.status != ProtocolRunStatusEnum.CANCELLED
        ):
          await svc.update_protocol_run_status(
            db_session,
            protocol_run_db_obj.accession_id,
            ProtocolRunStatusEnum.CANCELLED,
            output_data_json=json.dumps({"status": str(pce)}),
          )
      except Exception as e:
        logger.error(
          "ORCH: ERROR during protocol execution for run %s ('%s'): %s",
          run_accession_id,
          protocol_def_orm.name,
          e,
          exc_info=True,
        )
        error_info = {
          "error_type": type(e).__name__,
          "error_message": str(e),
          "traceback": traceback.format_exc(),
        }

        try:
          if praxis_state is None:
            praxis_state = PraxisState(run_accession_id=run_accession_id)
          last_good_snapshot = await praxis_state.set(
            "workcell_last_successful_snapshot", None
          )
          logger.debug(
            "ORCH: Clearing last successful workcell state snapshot for "
            "run %s due to error.",
            run_accession_id,
          )
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
        except Exception as rollback_error:
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
            "Specific PyLabRobot error 'VolumeError' detected for run %s."
            " Setting status to REQUIRES_INTERVENTION.",
            run_accession_id,
          )
          final_run_status = ProtocolRunStatusEnum.REQUIRES_INTERVENTION
          status_details = json.dumps(
            {
              "error_type": "VolumeError",
              "error_message": str(e),
              "action_required": (
                "User intervention needed to verify liquid levels and proceed."
              ),
              "traceback": traceback.format_exc(),
            }
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
            }
          )

        run_after_error = await db_session.get(
          ProtocolRunOrm, protocol_run_db_obj.accession_id
        )
        if run_after_error and run_after_error.status not in [
          ProtocolRunStatusEnum.CANCELLED,
          ProtocolRunStatusEnum.FAILED,
          ProtocolRunStatusEnum.REQUIRES_INTERVENTION,
          ProtocolRunStatusEnum.FAILED,
        ]:
          await svc.update_protocol_run_status(
            db_session,
            protocol_run_db_obj.accession_id,
            final_run_status,
            output_data_json=status_details,
          )
      finally:
        logger.info("ORCH: Finalizing protocol run %s.", run_accession_id)
        final_run_orm = await db_session.get(
          ProtocolRunOrm, protocol_run_db_obj.accession_id
        )
        if final_run_orm:
          final_run_orm.final_state_json = praxis_state.to_dict()

          if not final_run_orm.end_time:
            final_run_orm.end_time = datetime.datetime.now(datetime.timezone.utc)
          if (
            final_run_orm.start_time
            and final_run_orm.end_time
            and final_run_orm.duration_ms is None
          ):
            duration = final_run_orm.end_time - final_run_orm.start_time
            final_run_orm.duration_ms = int(duration.total_seconds() * 1000)

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
                    resource_instance_orm_accession_id=asset_orm_accession_id,
                    final_status=(ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE),
                  )
                logger.info(
                  "ORCH-RELEASE: Asset '%s' (Type: %s, ORM ID: %s) released.",
                  name_in_protocol,
                  asset_type,
                  asset_orm_accession_id,
                )
              except Exception as release_err:
                logger.error(
                  "ORCH-RELEASE: Failed to release asset '%s' (ORM ID: %s): %s",
                  asset_info.get("name_in_protocol", "UnknownAsset"),
                  asset_info.get("orm_accession_id"),
                  release_err,
                  exc_info=True,
                )
          await db_session.merge(final_run_orm)
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

      await db_session.refresh(protocol_run_db_obj)
      return protocol_run_db_obj

  async def execute_existing_protocol_run(
    self,
    protocol_run_orm: ProtocolRunOrm,
    user_input_params: Optional[Dict[str, Any]] = None,
    initial_state_data: Optional[Dict[str, Any]] = None,
  ) -> ProtocolRunOrm:
    """Execute an existing protocol run (typically called from Celery workers).

    This method takes an existing ProtocolRunOrm object and executes it,
    unlike execute_protocol which creates a new run. This is designed for
    the scheduler/Celery integration where the run is already created and
    queued for execution.

    Args:
      protocol_run_orm: Existing protocol run ORM object to execute.
      user_input_params: Dictionary of parameters provided by the user.
      initial_state_data: Initial data for the PraxisState.

    Returns:
      The updated ProtocolRunOrm object representing the completed or failed run.

    Raises:
      ValueError: If the protocol definition is not found or invalid.
      ProtocolCancelledError: If the protocol run is cancelled by the user.
      RuntimeError: If there is an error during protocol execution.

    """
    user_input_params = user_input_params or {}
    initial_state_data = initial_state_data or {}
    run_accession_id = protocol_run_orm.accession_id

    protocol_name = (
      protocol_run_orm.top_level_protocol_definition.name
      if protocol_run_orm.top_level_protocol_definition
      else "Unknown"
    )
    logger.info(
      "ORCH: Executing existing protocol run %s for '%s'. User params: %s, "
      "Initial state: %s",
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
            }
          ),
        )
        await db_session.commit()
        raise ValueError(error_msg)

      # Check for cancellation before starting
      initial_command = await get_control_command(run_accession_id)
      if initial_command == "CANCEL":
        logger.info("ORCH: Run %s CANCELLED before execution.", run_accession_id)
        await clear_control_command(run_accession_id)
        await svc.update_protocol_run_status(
          db_session,
          run_accession_id,
          ProtocolRunStatusEnum.CANCELLED,
          output_data_json=json.dumps(
            {"status": "Cancelled by user before execution."}
          ),
        )
        await db_session.commit()
        return protocol_run_orm

      # Initialize state and context
      praxis_state = PraxisState(run_accession_id=run_accession_id)
      if initial_state_data:
        praxis_state.update(initial_state_data)

      run_context = PraxisRunContext(
        run_accession_id=run_accession_id,
        canonical_state=praxis_state,
        current_db_session=db_session,
        current_call_log_db_accession_id=None,
      )

      # Prepare execution variables
      prepared_args: Dict[str, Any] = {}
      callable_protocol_func: Optional[Callable] = None
      protocol_pydantic_def: Optional[FunctionProtocolDefinitionModel] = None
      acquired_assets_info: Dict[uuid.UUID, dict] = {}

      main_workcell_container = self.workcell_runtime.get_main_workcell()
      if not main_workcell_container:
        raise RuntimeError(
          "Main Workcell container not available from WorkcellRuntime."
        )

      # Capture workcell state snapshot
      current_workcell_snapshot = self.workcell_runtime.get_state_snapshot()
      await praxis_state.set(
        "workcell_last_successful_snapshot", current_workcell_snapshot
      )
      logger.debug(
        "Workcell state snapshot captured and stored in PraxisState for run %s.",
        run_accession_id,
      )

      try:
        # Prepare protocol code
        protocol_def_orm = protocol_run_orm.top_level_protocol_definition
        (
          callable_protocol_func,
          protocol_pydantic_def,
        ) = await self._prepare_protocol_code(protocol_def_orm)

        # Create workcell view
        workcell_view_for_protocol = WorkcellView(
          parent_workcell=main_workcell_container,
          protocol_name=protocol_pydantic_def.name,
          required_assets=protocol_pydantic_def.assets,
        )

        # Prepare arguments (including asset acquisition)
        (
          prepared_args,
          state_dict_passed_to_top_level,
          acquired_assets_info,
        ) = await self._prepare_arguments(
          db_session=db_session,
          protocol_pydantic_def=protocol_pydantic_def,
          input_parameters=user_input_params,
          praxis_state=praxis_state,
          workcell_view=workcell_view_for_protocol,
          protocol_run_accession_id=run_accession_id,
        )

        # Update the protocol run with asset information
        protocol_run_orm.resolved_assets_json = acquired_assets_info
        await db_session.merge(protocol_run_orm)
        await db_session.flush()

        # Handle pause/resume logic
        command = await get_control_command(run_accession_id)
        if command == "PAUSE":
          logger.info("ORCH: Run %s PAUSED before execution.", run_accession_id)
          await clear_control_command(run_accession_id)
          await svc.update_protocol_run_status(
            db_session, run_accession_id, ProtocolRunStatusEnum.PAUSED
          )
          await db_session.commit()

          while True:
            await asyncio.sleep(1)
            new_command = await get_control_command(run_accession_id)
            if new_command == "RESUME":
              logger.info("ORCH: Run %s RESUMING.", run_accession_id)
              await clear_control_command(run_accession_id)
              await svc.update_protocol_run_status(
                db_session, run_accession_id, ProtocolRunStatusEnum.RUNNING
              )
              await db_session.commit()
              break
            elif new_command == "CANCEL":
              logger.info("ORCH: Run %s CANCELLED during pause.", run_accession_id)
              await clear_control_command(run_accession_id)
              await svc.update_protocol_run_status(
                db_session,
                run_accession_id,
                ProtocolRunStatusEnum.CANCELLED,
                output_data_json=json.dumps(
                  {"status": "Cancelled by user during pause."}
                ),
              )
              await db_session.commit()
              raise ProtocolCancelledError(
                f"Run {run_accession_id} cancelled by user during pause."
              )

        elif command == "CANCEL":
          logger.info("ORCH: Run %s CANCELLED before execution.", run_accession_id)
          await clear_control_command(run_accession_id)
          await svc.update_protocol_run_status(
            db_session,
            run_accession_id,
            ProtocolRunStatusEnum.CANCELLED,
            output_data_json=json.dumps(
              {"status": "Cancelled by user before execution."}
            ),
          )
          await db_session.commit()
          raise ProtocolCancelledError(
            f"Run {run_accession_id} cancelled by user before execution."
          )

        # Update status to RUNNING
        await svc.update_protocol_run_status(
          db_session, run_accession_id, ProtocolRunStatusEnum.RUNNING
        )
        await db_session.commit()

        # Execute the protocol
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

        # Update status to COMPLETED
        await svc.update_protocol_run_status(
          db_session,
          run_accession_id,
          ProtocolRunStatusEnum.COMPLETED,
          output_data_json=json.dumps(result, default=str),
        )

      except ProtocolCancelledError as pce:
        logger.info("ORCH: Protocol run %s was cancelled: %s", run_accession_id, pce)
        run_after_cancel = await db_session.get(ProtocolRunOrm, run_accession_id)
        if (
          run_after_cancel
          and run_after_cancel.status != ProtocolRunStatusEnum.CANCELLED
        ):
          await svc.update_protocol_run_status(
            db_session,
            run_accession_id,
            ProtocolRunStatusEnum.CANCELLED,
            output_data_json=json.dumps({"status": str(pce)}),
          )

      except Exception as e:
        logger.error(
          "ORCH: ERROR during protocol execution for run %s: %s",
          run_accession_id,
          e,
          exc_info=True,
        )
        error_info = {
          "error_type": type(e).__name__,
          "error_message": str(e),
          "traceback": traceback.format_exc(),
        }

        # Handle workcell state rollback
        try:
          if praxis_state is None:
            praxis_state = PraxisState(run_accession_id=run_accession_id)
          if praxis_state is None:
            raise RuntimeError(
              "PraxisState object not initialized for run %s." % run_accession_id
            )
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
        except Exception as rollback_error:
          logger.critical(
            "ORCH: CRITICAL - Failed to rollback workcell state for run %s: %s",
            run_accession_id,
            rollback_error,
            exc_info=True,
          )

        # Determine final status based on error type
        final_run_status = ProtocolRunStatusEnum.FAILED
        status_details = json.dumps(error_info)

        if isinstance(e, PyLabRobotVolumeError):
          logger.info(
            "Specific PyLabRobot error 'VolumeError' detected for run %s. "
            "Setting status to REQUIRES_INTERVENTION.",
            run_accession_id,
          )
          final_run_status = ProtocolRunStatusEnum.REQUIRES_INTERVENTION
          status_details = json.dumps(
            {
              "error_type": "VolumeError",
              "error_message": str(e),
              "action_required": (
                "User intervention needed to verify liquid levels and proceed."
              ),
              "traceback": traceback.format_exc(),
            }
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
            }
          )

        # Update run status
        run_after_error = await db_session.get(ProtocolRunOrm, run_accession_id)
        if run_after_error and run_after_error.status not in [
          ProtocolRunStatusEnum.CANCELLED,
          ProtocolRunStatusEnum.FAILED,
          ProtocolRunStatusEnum.REQUIRES_INTERVENTION,
        ]:
          await svc.update_protocol_run_status(
            db_session,
            run_accession_id,
            final_run_status,
            output_data_json=status_details,
          )

      finally:
        # Finalize the protocol run
        logger.info("ORCH: Finalizing protocol run %s.", run_accession_id)
        final_run_orm = await db_session.get(ProtocolRunOrm, run_accession_id)
        if final_run_orm:
          final_run_orm.final_state_json = praxis_state.to_dict()

          if not final_run_orm.end_time:
            final_run_orm.end_time = datetime.datetime.now(datetime.timezone.utc)
          if (
            final_run_orm.start_time
            and final_run_orm.end_time
            and final_run_orm.duration_ms is None
          ):
            duration = final_run_orm.end_time - final_run_orm.start_time
            final_run_orm.duration_ms = int(duration.total_seconds() * 1000)

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
                    resource_instance_orm_accession_id=asset_orm_accession_id,
                    final_status=ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
                  )
                logger.info(
                  "ORCH-RELEASE: Asset '%s' (Type: %s, ORM ID: %s) released.",
                  name_in_protocol,
                  asset_type,
                  asset_orm_accession_id,
                )
              except Exception as release_err:
                logger.error(
                  "ORCH-RELEASE: Failed to release asset '%s' (ORM ID: %s): %s",
                  asset_info.get("name_in_protocol", "UnknownAsset"),
                  asset_info.get("orm_accession_id"),
                  release_err,
                  exc_info=True,
                )

          await db_session.merge(final_run_orm)

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
