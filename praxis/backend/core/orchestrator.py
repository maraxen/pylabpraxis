# pylint: disable=too-many-arguments,too-many-locals,broad-except,fixme,unused-argument,too-many-statements,too-many-branches
"""
praxis.backend.core.orchestrator

The Orchestrator is responsible for managing the lifecycle of protocol runs.
It fetches protocol definitions, prepares the execution environment (including state),
invokes the protocol functions, and oversees logging and run control.
"""

import asyncio
import contextlib
import datetime
import importlib
import inspect
import json
import os
import subprocess
import sys
import traceback
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast

import uuid_utils as uuid  # For UUID type hints and generation
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import praxis.backend.services as svc
from praxis.backend.core.asset_manager import AssetManager
from praxis.backend.core.decorators import (
  get_actual_type_str_from_hint,
  serialize_type_hint_str,
)
from praxis.backend.core.run_context import PraxisRunContext, serialize_arguments
from praxis.backend.core.workcell import Workcell, WorkcellView
from praxis.backend.core.workcell_runtime import WorkcellRuntime
from praxis.backend.models import (
  AssetRequirementModel,  # Pydantic model from decorator
  DeckConfigurationOrm,
  FunctionProtocolDefinitionModel,  # Pydantic model from decorator
  FunctionProtocolDefinitionOrm,
  MachineStatusEnum,
  ProtocolRunOrm,
  ProtocolRunStatusEnum,
  ResourceInstanceStatusEnum,
)
from praxis.backend.utils.errors import (
  AssetAcquisitionError,
  ProtocolCancelledError,
  PyLabRobotGenericError,
  PyLabRobotVolumeError,
)
from praxis.backend.utils.logging import get_logger
from praxis.backend.utils.run_control import clear_control_command, get_control_command
from praxis.backend.utils.state import State as PraxisState

logger = get_logger(__name__)


@contextlib.contextmanager
def temporary_sys_path(path_to_add: Optional[str]):
  """Add a path to sys.path temporarily.

  A context manager to temporarily add a path to sys.path.
  Ensures the path is removed from sys.path on exit, even if errors occur.

  Args:
    path_to_add (Optional[str]): The path to add to sys.path. If None, does nothing.

  Yields:
    None: Yields control back to the caller, allowing them to execute code with the
    modified sys.path.

  Raises:
    ValueError: If the path_to_add is not a string or is empty.

  """
  original_sys_path = list(sys.path)
  path_added_successfully = False
  if path_to_add and path_to_add not in sys.path:
    sys.path.insert(0, path_to_add)
    path_added_successfully = True
    logger.debug(f"Added '{path_to_add}' to sys.path.")
  try:
    yield
  finally:
    if path_added_successfully and path_to_add:
      try:
        sys.path.remove(path_to_add)
        logger.debug(f"Removed '{path_to_add}' from sys.path.")
      except ValueError:  # pragma: no cover
        # Path was already removed or sys.path was modified externally
        logger.warning(
          f"Path '{path_to_add}' was not in sys.path upon exit, restoring original."
        )
        sys.path = original_sys_path
    elif (
      path_to_add and path_to_add in sys.path and sys.path != original_sys_path
    ):  # pragma: no cover
      # This case handles if path_to_add was already in sys.path but sys.path got modified
      logger.debug(
        f"Restoring original sys.path as it was modified externally but '{path_to_add}' was originally present."
      )
      sys.path = original_sys_path


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
  ):
    """Initialize the Orchestrator.

    Args:
        db_session_factory: A factory to create SQLAlchemy AsyncSession instances.
        asset_manager: An instance of AssetManager for asset allocation.
        workcell_runtime: An instance of WorkcellRuntime to manage live PLR objects.

    Raises:
        ValueError: If any of the arguments are invalid.
        TypeError: If any of the arguments are of the wrong type.

    """
    self.db_session_factory = db_session_factory
    self.asset_manager = asset_manager
    self.workcell_runtime = workcell_runtime
    logger.info("Orchestrator initialized.")

  async def _run_git_command(
    self,
    command: List[str],
    cwd: str,
    suppress_output: bool = False,
    timeout: int = 300,
  ) -> str:
    """Run a Git command and handle errors, including timeout.

    Args:
      command: The Git command to run as a list of strings.
      cwd: The working directory where the command should be executed.
      suppress_output: If True, suppresses stdout and stderr logging.
      timeout: Timeout in seconds for the command execution.

    Returns:
      The standard output of the command as a string.

    Raises:
      RuntimeError: If the command fails or times out.
      FileNotFoundError: If the Git command is not found in the system path.

    """
    try:
      logged_command = " ".join(command)
      logger.debug(
        f"ORCH-GIT: Running command: {logged_command} in {cwd} with timeout {timeout}s"
      )
      process = await asyncio.to_thread(
        subprocess.run,
        command,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout,
      )
      if not suppress_output:
        stdout_stripped = process.stdout.strip()
        stderr_stripped = process.stderr.strip()
        if stdout_stripped:
          logger.debug(f"ORCH-GIT: STDOUT: {stdout_stripped}")
        if stderr_stripped:
          logger.debug(
            f"ORCH-GIT: STDERR: {stderr_stripped}"
          )  # Git often uses stderr for info
      return process.stdout.strip()
    except subprocess.TimeoutExpired as e:
      error_message = (
        f"ORCH-GIT: Command '{' '.join(e.cmd)}' timed out after {e.timeout} seconds in"
        f" {cwd}.\n"
        f"Stderr: {e.stderr.decode(errors='ignore').strip() if e.stderr else 'N/A'}\n"
        f"Stdout: {e.stdout.decode(errors='ignore').strip() if e.stdout else 'N/A'}"
      )
      logger.error(error_message)
      raise RuntimeError(error_message) from e
    except subprocess.CalledProcessError as e:
      stderr_output = (
        e.stderr.strip()
        if isinstance(e.stderr, str)
        else e.stderr.decode(errors="ignore").strip()
        if e.stderr
        else "N/A"
      )
      stdout_output = (
        e.stdout.strip()
        if isinstance(e.stdout, str)
        else e.stdout.decode(errors="ignore").strip()
        if e.stdout
        else "N/A"
      )
      error_message = (
        f"ORCH-GIT: Command '{' '.join(e.cmd)}' failed with exit code {e.returncode} in"
        f"{cwd}.\n"
        f"Stderr: {stderr_output}\n"
        f"Stdout: {stdout_output}"
      )
      logger.error(error_message)
      raise RuntimeError(error_message) from e
    except FileNotFoundError:  # pragma: no cover
      error_message = f"ORCH-GIT: Git command not found. Ensure git is installed. \
        Command: {' '.join(command)}"
      logger.error(error_message)
      raise RuntimeError(error_message) from None

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
      f"Fetching protocol ORM: Name='{protocol_name}', Version='{version}', "
      f"Commit='{commit_hash}', Source='{source_name}'"
    )
    return await svc.get_protocol_definition_details(
      db=db_session,
      name=protocol_name,
      version=version,
      source_name=source_name,
      commit_hash=commit_hash,
    )

  async def _prepare_protocol_code(
    self, protocol_def_orm: FunctionProtocolDefinitionOrm
  ) -> Tuple[Callable, FunctionProtocolDefinitionModel]:
    """Load the protocol code from its source (Git or FileSystem).

    Args:
      protocol_def_orm: The ORM object representing the protocol definition.

    Returns:
      A tuple containing the callable function and its Pydantic definition model.

    Raises:
      ValueError: If the protocol definition is incomplete or invalid.
      AttributeError: If the function or its Pydantic definition is not found.
      RuntimeError: If there is an error checking out a Git commit or if the commit
        does not match the expected state.

    """
    logger.info(
      f"Preparing code for protocol: {protocol_def_orm.name} v{protocol_def_orm.version}"
    )
    module_path_to_add_for_sys_path: Optional[str] = None

    if protocol_def_orm.source_repository_id and protocol_def_orm.source_repository:
      repo = protocol_def_orm.source_repository
      checkout_path = repo.local_checkout_path
      commit_hash_to_checkout = protocol_def_orm.commit_hash

      if not checkout_path or not commit_hash_to_checkout or not repo.git_url:
        raise ValueError(
          f"Incomplete Git source info for protocol '{protocol_def_orm.name}'."
        )

      await self._ensure_git_repo_and_fetch(repo.git_url, checkout_path, repo.name)
      logger.info(
        f"ORCH-GIT: Checking out commit '{commit_hash_to_checkout}' in '{checkout_path}'..."
      )
      await self._run_git_command(
        ["git", "checkout", commit_hash_to_checkout], cwd=checkout_path
      )

      current_commit = await self._run_git_command(
        ["git", "rev-parse", "HEAD"], cwd=checkout_path, suppress_output=True
      )
      resolved_target_commit = await self._run_git_command(
        ["git", "rev-parse", commit_hash_to_checkout + "^{commit}"],
        cwd=checkout_path,
        suppress_output=True,
      )
      if current_commit != resolved_target_commit:
        raise RuntimeError(
          f"Failed to checkout commit '{commit_hash_to_checkout}'. HEAD is at '{current_commit}', "
          f"expected '{resolved_target_commit}'. Repo: '{repo.name}'"
        )
      logger.info(
        f"ORCH-GIT: Successfully checked out '{commit_hash_to_checkout}' (resolved to '{current_commit}')."
      )
      module_path_to_add_for_sys_path = checkout_path

    elif protocol_def_orm.file_system_source_id and protocol_def_orm.file_system_source:
      fs_source = protocol_def_orm.file_system_source
      if not os.path.isdir(fs_source.base_path):
        raise ValueError(
          f"Invalid base path '{fs_source.base_path}' for FS source '{fs_source.name}'."
        )
      module_path_to_add_for_sys_path = fs_source.base_path
    else:
      logger.warning(
        f"Protocol '{protocol_def_orm.name}' has no linked source. Attempting direct import."
      )

    with temporary_sys_path(module_path_to_add_for_sys_path):
      if protocol_def_orm.module_name in sys.modules:
        module = importlib.reload(sys.modules[protocol_def_orm.module_name])
        logger.debug(f"Reloaded module: {protocol_def_orm.module_name}")
      else:
        module = importlib.import_module(protocol_def_orm.module_name)
        logger.debug(f"Imported module: {protocol_def_orm.module_name}")

    if not hasattr(module, protocol_def_orm.function_name):
      raise AttributeError(
        f"Function '{protocol_def_orm.function_name}' not found in module "
        f"'{protocol_def_orm.module_name}' from path '{module_path_to_add_for_sys_path or 'PYTHONPATH'}'."
      )

    func_wrapper = getattr(module, protocol_def_orm.function_name)
    pydantic_def: Optional[FunctionProtocolDefinitionModel] = getattr(
      func_wrapper, "_protocol_definition", None
    )

    if not pydantic_def or not isinstance(
      pydantic_def, FunctionProtocolDefinitionModel
    ):
      raise AttributeError(
        f"Function '{protocol_def_orm.function_name}' in '{protocol_def_orm.module_name}' "
        "is not a valid @protocol_function (missing or invalid _protocol_definition attribute)."
      )

    if protocol_def_orm.id and (
      not pydantic_def.db_id or pydantic_def.db_id != protocol_def_orm.id
    ):
      pydantic_def.db_id = protocol_def_orm.id  # type: ignore[assignment]
      logger.debug(
        f"Updated Pydantic definition DB ID for '{pydantic_def.name}' to {protocol_def_orm.id}"
      )

    return func_wrapper, pydantic_def

  async def _ensure_git_repo_and_fetch(
    self, git_url: str, checkout_path: str, repo_name_for_logging: str
  ) -> None:
    """Ensure a git repo exists at checkout_path, clones if not, and fetches updates."""
    is_git_repo = False
    if os.path.exists(checkout_path):
      try:
        result = await self._run_git_command(
          ["git", "rev-parse", "--is-inside-work-tree"],
          cwd=checkout_path,
          suppress_output=True,
        )
        is_git_repo = result == "true"
        if not is_git_repo:
          logger.warning(
            f"ORCH-GIT: Path '{checkout_path}' for repo '{repo_name_for_logging}' exists but is not a git work-tree root."
          )
      except RuntimeError:
        is_git_repo = False
        logger.info(
          f"ORCH-GIT: Path '{checkout_path}' for repo '{repo_name_for_logging}' is not a git repository or git command failed."
        )

    if is_git_repo:
      try:
        current_remote_url = await self._run_git_command(
          ["git", "config", "--get", "remote.origin.url"],
          cwd=checkout_path,
          suppress_output=True,
        )
        if current_remote_url != git_url:
          raise ValueError(
            f"Path '{checkout_path}' for repo '{repo_name_for_logging}' is a Git repository, "
            f"but its remote 'origin' URL ('{current_remote_url}') does not match the expected URL ('{git_url}'). "
            "Manual intervention required."
          )
      except RuntimeError as e:
        raise ValueError(
          f"Failed to verify remote URL for existing repo at '{checkout_path}'. Error: {e}"
        ) from e

      logger.info(
        f"ORCH-GIT: '{checkout_path}' is existing repo for '{repo_name_for_logging}'. Fetching origin..."
      )
      await self._run_git_command(
        ["git", "fetch", "origin", "--prune"], cwd=checkout_path
      )
    else:
      if os.path.exists(checkout_path):
        if os.listdir(checkout_path):
          raise ValueError(
            f"Path '{checkout_path}' for repo '{repo_name_for_logging}' exists, is not Git, and not empty. Cannot clone."
          )
        logger.info(
          f"ORCH-GIT: Path '{checkout_path}' for repo '{repo_name_for_logging}' exists and is empty. Cloning into it."
        )
      else:
        logger.info(
          f"ORCH-GIT: Path '{checkout_path}' for repo '{repo_name_for_logging}' does not exist. Creating and cloning..."
        )
        try:
          os.makedirs(checkout_path, exist_ok=True)
        except OSError as e:
          raise ValueError(f"Failed to create directory '{checkout_path}': {e}") from e
      logger.info(
        f"ORCH-GIT: Cloning repository '{git_url}' into '{checkout_path}' for repo '{repo_name_for_logging}'..."
      )
      await self._run_git_command(["git", "clone", git_url, "."], cwd=checkout_path)

  async def _prepare_arguments(
    self,
    db_session: AsyncSession,
    protocol_pydantic_def: FunctionProtocolDefinitionModel,
    user_input_params: Dict[str, Any],
    praxis_state: PraxisState,
    workcell_view: WorkcellView,
    protocol_run_guid: uuid.UUID,
  ) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]], Dict[uuid.UUID, Any]]:
    """Prepare arguments for protocol execution, including acquiring assets."""
    logger.info(f"Preparing arguments for protocol: {protocol_pydantic_def.name}")
    final_args: Dict[str, Any] = {}
    state_dict_to_pass: Optional[Dict[str, Any]] = None
    acquired_assets_details: Dict[uuid.UUID, Any] = {}

    for param_meta in protocol_pydantic_def.parameters:
      if param_meta.is_deck_param:
        continue
      if param_meta.name == protocol_pydantic_def.state_param_name:
        continue

      if param_meta.name in user_input_params:
        final_args[param_meta.name] = user_input_params[param_meta.name]
        logger.debug(f"Using user input for param '{param_meta.name}'.")
      elif not param_meta.optional:
        raise ValueError(
          f"Mandatory parameter '{param_meta.name}' missing for protocol '{protocol_pydantic_def.name}'."
        )
      else:
        logger.debug(f"Optional param '{param_meta.name}' not provided by user.")

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
            f"Injecting PraxisState object for param '{protocol_pydantic_def.state_param_name}'."
          )
        elif "dict" in state_param_meta.actual_type_str.lower():
          state_dict_to_pass = praxis_state.to_dict()
          final_args[protocol_pydantic_def.state_param_name] = state_dict_to_pass
          logger.debug(
            f"Injecting state dictionary for param '{protocol_pydantic_def.state_param_name}'."
          )
        else:
          final_args[protocol_pydantic_def.state_param_name] = praxis_state
          logger.debug(
            f"Defaulting to injecting PraxisState object for param '{protocol_pydantic_def.state_param_name}'."
          )

    for asset_req_model in protocol_pydantic_def.assets:
      try:
        logger.info(
          f"ORCH-ACQUIRE: Acquiring asset '{asset_req_model.name}' "
          f"(Type: '{asset_req_model.actual_type_str}', Optional: {asset_req_model.optional}) "
          f"for run '{protocol_run_guid}'."
        )
        live_obj, orm_id, asset_kind_str = await self.asset_manager.acquire_asset(
          protocol_run_guid=protocol_run_guid, asset_requirement=asset_req_model
        )
        final_args[asset_req_model.name] = live_obj
        acquired_assets_details[orm_id] = {
          "type": asset_kind_str,
          "orm_id": orm_id,
          "name_in_protocol": asset_req_model.name,
        }
        logger.info(
          f"ORCH-ACQUIRE: Asset '{asset_req_model.name}' "
          f"(Kind: {asset_kind_str}, ORM ID: {orm_id}) acquired: {live_obj}"
        )
      except AssetAcquisitionError as e:
        if asset_req_model.optional:
          logger.warning(
            f"ORCH-ACQUIRE: Optional asset '{asset_req_model.name}' could not be acquired: {e}. "
            "Proceeding as it's optional."
          )
          final_args[asset_req_model.name] = None
        else:
          error_msg = (
            f"Failed to acquire mandatory asset '{asset_req_model.name}' for "
            f"protocol '{protocol_pydantic_def.name}': {e}"
          )
          logger.error(error_msg)
          raise ValueError(error_msg) from e
      except Exception as e_general:
        error_msg = (
          f"Unexpected error acquiring asset '{asset_req_model.name}' for "
          f"protocol '{protocol_pydantic_def.name}': {e_general}"
        )
        logger.error(error_msg, exc_info=True)
        raise ValueError(error_msg) from e_general

    if (
      protocol_pydantic_def.preconfigure_deck and protocol_pydantic_def.deck_param_name
    ):
      deck_param_name = protocol_pydantic_def.deck_param_name
      deck_identifier_from_user = user_input_params.get(deck_param_name)

      if deck_identifier_from_user is None and not next(
        (
          p
          for p in protocol_pydantic_def.parameters
          if p.name == deck_param_name and p.optional
        ),
        False,
      ):
        raise ValueError(
          f"Mandatory deck parameter '{deck_param_name}' for preconfiguration not provided."
        )

      if deck_identifier_from_user is not None:
        if not isinstance(deck_identifier_from_user, (str, uuid.UUID)):
          raise ValueError(
            f"Deck identifier for preconfiguration ('{deck_param_name}') must be a string (name) or UUID (ID), "
            f"got {type(deck_identifier_from_user)}."
          )

        logger.info(
          f"ORCH-DECK: Applying deck configuration '{deck_identifier_from_user}' for run '{protocol_run_guid}'."
        )

        deck_config_orm_id_to_apply: uuid.UUID
        if isinstance(deck_identifier_from_user, str):
          deck_config_orm = await svc.get_deck_config_by_name(
            db_session, deck_identifier_from_user
          )
          if not deck_config_orm:
            raise ValueError(
              f"Deck configuration named '{deck_identifier_from_user}' not found."
            )
          deck_config_orm_id_to_apply = deck_config_orm.id
        else:
          deck_config_orm_id_to_apply = deck_identifier_from_user

        live_deck_object = await self.asset_manager.apply_deck_configuration(
          deck_config_orm_id=deck_config_orm_id_to_apply,
          protocol_run_guid=protocol_run_guid,
        )
        final_args[deck_param_name] = live_deck_object
        logger.info(
          f"ORCH-DECK: Deck '{live_deck_object.name}' configured and injected as '{deck_param_name}'."
        )
      elif deck_param_name in final_args:
        logger.warning(
          f"Deck parameter '{deck_param_name}' was already processed (e.g., as an asset). Review protocol definition."
        )

    return final_args, state_dict_to_pass, acquired_assets_details

  async def execute_protocol(
    self,
    protocol_name: str,
    user_input_params: Optional[Dict[str, Any]] = None,
    initial_state_data: Optional[Dict[str, Any]] = None,
    protocol_version: Optional[str] = None,
    commit_hash: Optional[str] = None,
    source_name: Optional[str] = None,
  ) -> ProtocolRunOrm:
    """
    Executes a specified protocol.

    Args:
        protocol_name: Name of the protocol to execute.
        user_input_params: Dictionary of parameters provided by the user.
        initial_state_data: Initial data for the PraxisState.
        protocol_version: Specific version of the protocol.
        commit_hash: Specific commit hash if from a Git source.
        source_name: Name of the protocol source (Git repo or FS).

    Returns:
        The ProtocolRunOrm object representing the completed or failed run.
    """
    user_input_params = user_input_params or {}
    initial_state_data = initial_state_data or {}
    run_guid = uuid.uuid7()
    start_iso_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    logger.info(
      f"ORCH: Initiating protocol run {run_guid} for '{protocol_name}' at {start_iso_timestamp}."
      f" User params: {user_input_params}, Initial state: {initial_state_data}"
    )

    async with self.db_session_factory() as db_session:
      protocol_def_orm = await self._get_protocol_definition_orm_from_db(
        db_session, protocol_name, protocol_version, commit_hash, source_name
      )

      if not protocol_def_orm or not protocol_def_orm.id:
        error_msg = (
          f"Protocol '{protocol_name}' (v:{protocol_version}, commit:{commit_hash}, src:{source_name}) "
          "not found or invalid DB ID."
        )
        logger.error(error_msg)

        protocol_def_id_for_error_run = (
          protocol_def_orm.id if protocol_def_orm and protocol_def_orm.id else None
        )

        if protocol_def_id_for_error_run is None:
          raise ProtocolCancelledError(
            f"Protocol definition '{protocol_name}' completely not found, \
              cannot link failed run to a definition."
          )

        error_run_db_obj = await svc.create_protocol_run(
          db=db_session,
          run_guid=run_guid,
          top_level_protocol_definition_id=protocol_def_id_for_error_run,
          status=ProtocolRunStatusEnum.FAILED,
          input_parameters_json=json.dumps(user_input_params),
          initial_state_json=json.dumps(initial_state_data),
        )
        await db_session.flush()
        await db_session.refresh(error_run_db_obj)
        await svc.update_protocol_run_status(
          db=db_session,
          protocol_run_id=error_run_db_obj.id,
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
        run_guid=run_guid,
        top_level_protocol_definition_id=protocol_def_orm.id,
        status=ProtocolRunStatusEnum.PREPARING,
        input_parameters_json=json.dumps(user_input_params),
        initial_state_json=json.dumps(initial_state_data),
      )
      await db_session.flush()
      await db_session.refresh(protocol_run_db_obj)

      initial_command = await get_control_command(run_guid)
      if initial_command == "CANCEL":
        logger.info(f"ORCH: Run {run_guid} CANCELLED before preparation.")
        await clear_control_command(run_guid)
        await svc.update_protocol_run_status(
          db_session,
          protocol_run_db_obj.id,
          ProtocolRunStatusEnum.CANCELLED,
          output_data_json=json.dumps(
            {"status": "Cancelled by user before preparation."}
          ),
        )
        await db_session.commit()
        return protocol_run_db_obj

      praxis_state = PraxisState(run_guid=run_guid)
      if initial_state_data:
        praxis_state.update(initial_state_data)

      run_context = PraxisRunContext(
        run_guid=run_guid,
        canonical_state=praxis_state,
        current_db_session=db_session,
        current_call_log_db_id=None,
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
        f"Workcell state snapshot captured and stored in PraxisState for run {run_guid}."
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
          user_input_params=user_input_params,
          praxis_state=praxis_state,
          workcell_view=workcell_view_for_protocol,
          protocol_run_guid=run_guid,
        )

        protocol_run_db_obj.resolved_assets_json = acquired_assets_info
        await db_session.merge(protocol_run_db_obj)
        await db_session.flush()

        command = await get_control_command(run_guid)
        if command == "PAUSE":
          logger.info(f"ORCH: Run {run_guid} PAUSED before execution.")
          await clear_control_command(run_guid)
          await svc.update_protocol_run_status(
            db_session, protocol_run_db_obj.id, ProtocolRunStatusEnum.PAUSED
          )
          await db_session.commit()
          while True:
            await asyncio.sleep(1)
            new_command = await get_control_command(run_guid)
            if new_command == "RESUME":
              logger.info(f"ORCH: Run {run_guid} RESUMING.")
              await clear_control_command(run_guid)
              await svc.update_protocol_run_status(
                db_session, protocol_run_db_obj.id, ProtocolRunStatusEnum.RUNNING
              )
              await db_session.commit()
              break
            elif new_command == "CANCEL":
              logger.info(f"ORCH: Run {run_guid} CANCELLED during pause.")
              await clear_control_command(run_guid)
              await svc.update_protocol_run_status(
                db_session,
                protocol_run_db_obj.id,
                ProtocolRunStatusEnum.CANCELLED,
                output_data_json=json.dumps(
                  {"status": "Cancelled by user during pause."}
                ),
              )
              await db_session.commit()
              raise ProtocolCancelledError(
                f"Run {run_guid} cancelled by user during pause."
              )
        elif command == "CANCEL":
          logger.info(f"ORCH: Run {run_guid} CANCELLED before execution.")
          await clear_control_command(run_guid)
          await svc.update_protocol_run_status(
            db_session,
            protocol_run_db_obj.id,
            ProtocolRunStatusEnum.CANCELLED,
            output_data_json=json.dumps(
              {"status": "Cancelled by user before execution."}
            ),
          )
          await db_session.commit()
          raise ProtocolCancelledError(
            f"Run {run_guid} cancelled by user before execution."
          )

        current_run_status_orm = await db_session.get(
          ProtocolRunOrm, protocol_run_db_obj.id
        )
        if (
          current_run_status_orm
          and current_run_status_orm.status != ProtocolRunStatusEnum.RUNNING
        ):
          await svc.update_protocol_run_status(
            db_session, protocol_run_db_obj.id, ProtocolRunStatusEnum.RUNNING
          )
          await db_session.commit()

        logger.info(
          f"ORCH: Executing protocol '{protocol_pydantic_def.name}' for run {run_guid}."
        )
        result = await callable_protocol_func(
          **prepared_args,
          __praxis_run_context__=run_context,
          __function_db_id__=protocol_def_orm.id,
        )
        logger.info(
          f"ORCH: Protocol '{protocol_pydantic_def.name}' run {run_guid} completed successfully."
        )

        await svc.update_protocol_run_status(
          db_session,
          protocol_run_db_obj.id,
          ProtocolRunStatusEnum.COMPLETED,
          output_data_json=json.dumps(result, default=str),
        )

      except ProtocolCancelledError as pce:
        logger.info(f"ORCH: Protocol run {run_guid} was cancelled: {pce}")
        run_after_cancel = await db_session.get(ProtocolRunOrm, protocol_run_db_obj.id)
        if (
          run_after_cancel
          and run_after_cancel.status != ProtocolRunStatusEnum.CANCELLED
        ):
          await svc.update_protocol_run_status(
            db_session,
            protocol_run_db_obj.id,
            ProtocolRunStatusEnum.CANCELLED,
            output_data_json=json.dumps({"status": str(pce)}),
          )
      except Exception as e:
        logger.error(
          f"ORCH: ERROR during protocol execution for run {run_guid} ('{protocol_def_orm.name}'): {e}",
          exc_info=True,
        )
        error_info = {
          "error_type": type(e).__name__,
          "error_message": str(e),
          "traceback": traceback.format_exc(),
        }

        try:
          if praxis_state is None:
            praxis_state = PraxisState(run_guid=run_guid)
          last_good_snapshot = await praxis_state.set(
            "workcell_last_successful_snapshot", None
          )
          logger.debug(
            f"ORCH: Clearing last successful workcell state snapshot for run {run_guid} due to error."
          )
          if last_good_snapshot:
            self.workcell_runtime.apply_state_snapshot(last_good_snapshot)
            logger.warning(
              f"ORCH: Workcell state for run {run_guid} rolled back successfully."
            )
          else:
            logger.warning(
              f"ORCH: No prior workcell state snapshot found for run {run_guid} to rollback."
            )
        except Exception as rollback_error:
          logger.critical(
            f"ORCH: CRITICAL - Failed to rollback workcell state for run {run_guid}: {rollback_error}",
            exc_info=True,
          )

        final_run_status = ProtocolRunStatusEnum.FAILED
        status_details = json.dumps(error_info)

        if isinstance(e, PyLabRobotVolumeError):
          logger.info(
            f"Specific PyLabRobot error 'VolumeError' detected for run {run_guid}. Setting status to REQUIRES_INTERVENTION."
          )
          final_run_status = ProtocolRunStatusEnum.REQUIRES_INTERVENTION
          status_details = json.dumps(
            {
              "error_type": "VolumeError",
              "error_message": str(e),
              "action_required": "User intervention needed to verify liquid levels and proceed.",
              "traceback": traceback.format_exc(),
            }
          )
        elif isinstance(e, PyLabRobotGenericError):
          logger.info(
            f"Generic PyLabRobot error detected for run {run_guid}. Setting status to FAILED."
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

        run_after_error = await db_session.get(ProtocolRunOrm, protocol_run_db_obj.id)
        if run_after_error and run_after_error.status not in [
          ProtocolRunStatusEnum.CANCELLED,
          ProtocolRunStatusEnum.FAILED,
          ProtocolRunStatusEnum.REQUIRES_INTERVENTION,
          ProtocolRunStatusEnum.FAILED,
        ]:
          await svc.update_protocol_run_status(
            db_session,
            protocol_run_db_obj.id,
            final_run_status,
            output_data_json=status_details,
          )
      finally:
        logger.info(f"ORCH: Finalizing protocol run {run_guid}.")
        final_run_orm = await db_session.get(ProtocolRunOrm, protocol_run_db_obj.id)
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
              f"ORCH: Releasing {len(acquired_assets_info)} assets for run {run_guid}."
            )
            for asset_orm_id, asset_info in acquired_assets_info.items():
              try:
                asset_type = asset_info.get("type")
                name_in_protocol = asset_info.get("name_in_protocol", "UnknownAsset")

                if asset_type == "machine":
                  await self.asset_manager.release_machine(
                    machine_orm_id=asset_orm_id,
                    final_status=MachineStatusEnum.AVAILABLE,
                  )
                elif asset_type == "resource":
                  await self.asset_manager.release_resource(
                    resource_instance_orm_id=asset_orm_id,
                    final_status=ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
                  )
                logger.info(
                  f"ORCH-RELEASE: Asset '{name_in_protocol}' (Type: {asset_type}, ORM ID: {asset_orm_id}) released."
                )
              except Exception as release_err:
                logger.error(
                  f"ORCH-RELEASE: Failed to release asset '{asset_info.get('name_in_protocol', 'UnknownAsset')}' "
                  f"(ORM ID: {asset_info.get('orm_id')}): {release_err}",
                  exc_info=True,
                )
          await db_session.merge(final_run_orm)
        try:
          await db_session.commit()
          logger.info(f"ORCH: Final DB commit for run {run_guid} successful.")
        except Exception as db_final_err:
          logger.error(
            f"ORCH: CRITICAL - Failed to commit final updates for run {run_guid}: {db_final_err}",
            exc_info=True,
          )
          await db_session.rollback()

      await db_session.refresh(protocol_run_db_obj)
      return protocol_run_db_obj
