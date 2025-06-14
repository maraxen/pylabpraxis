# pylint: disable=too-many-arguments,too-many-locals,broad-except,fixme,\
#   unused-argument,too-many-statements,too-many-branches
"""The Orchestrator manages the lifecycle of protocol runs."""

import asyncio
import contextlib
import datetime
import importlib
import json
import os
import subprocess
import sys
import traceback
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast

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
  DeckInstanceOrm,
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
from praxis.backend.utils.uuid import uuid7

logger = get_logger(__name__)


@contextlib.contextmanager
def temporary_sys_path(path_to_add: Optional[str]):
  """Add a path to sys.path temporarily.

  A context manager to temporarily add a path to sys.path.
  Ensures the path is removed from sys.path on exit, even if errors occur.

  Args:
    path_to_add (Optional[str]): The path to add to sys.path. If None,
      does nothing.

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
    logger.debug("Added '%s' to sys.path.", path_to_add)
  try:
    yield
  finally:
    if path_added_successfully and path_to_add:
      try:
        sys.path.remove(path_to_add)
        logger.debug("Removed '%s' from sys.path.", path_to_add)
      except ValueError:  # pragma: no cover
        # Path was already removed or sys.path was modified externally
        logger.warning(
          "Path '%s' was not in sys.path upon exit, restoring original.",
          path_to_add,
        )
        sys.path = original_sys_path
    elif (
      path_to_add and path_to_add in sys.path and sys.path != original_sys_path
    ):  # pragma: no cover
      # This case handles if path_to_add was already in sys.path
      # but sys.path got modified
      logger.debug(
        "Restoring original sys.path as it was modified externally but "
        "'%s' was originally present.",
        path_to_add,
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
        "ORCH-GIT: Running command: %s in %s with timeout %ds",
        logged_command,
        cwd,
        timeout,
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
          logger.debug("ORCH-GIT: STDOUT: %s", stdout_stripped)
        if stderr_stripped:
          logger.debug(
            "ORCH-GIT: STDERR: %s",
            stderr_stripped,
          )  # Git often uses stderr for info
      return process.stdout.strip()
    except subprocess.TimeoutExpired as e:
      error_message = (
        "ORCH-GIT: Command '%s' timed out after %d seconds in %s.\n"
        "Stderr: %s\n"
        "Stdout: %s"
      ) % (
        " ".join(e.cmd),
        e.timeout,
        cwd,
        e.stderr.decode(errors="ignore").strip() if e.stderr else "N/A",
        e.stdout.decode(errors="ignore").strip() if e.stdout else "N/A",
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
        "ORCH-GIT: Command '%s' failed with exit code %d in %s.\n"
        "Stderr: %s\n"
        "Stdout: %s"
      ) % (
        " ".join(e.cmd),
        e.returncode,
        cwd,
        stderr_output,
        stdout_output,
      )
      logger.error(error_message)
      raise RuntimeError(error_message) from e
    except FileNotFoundError:  # pragma: no cover
      error_message = (
        "ORCH-GIT: Git command not found. Ensure git is installed. " "Command: %s"
      ) % (" ".join(command))
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
      "Fetching protocol ORM: Name='%s', Version='%s', Commit='%s', Source='%s'",
      protocol_name,
      version,
      commit_hash,
      source_name,
    )
    return await svc.read_protocol_definition_details(
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
      "Preparing code for protocol: %s v%s",
      protocol_def_orm.name,
      protocol_def_orm.version,
    )
    module_path_to_add_for_sys_path: Optional[str] = None

    if (
      protocol_def_orm.source_repository_accession_id
      and protocol_def_orm.source_repository
    ):
      repo = protocol_def_orm.source_repository
      checkout_path = repo.local_checkout_path
      commit_hash_to_checkout = protocol_def_orm.commit_hash

      if not checkout_path or not commit_hash_to_checkout or not repo.git_url:
        raise ValueError(
          "Incomplete Git source info for protocol '%s'.",
          protocol_def_orm.name,
        )

      await self._ensure_git_repo_and_fetch(repo.git_url, checkout_path, repo.name)
      logger.info(
        "ORCH-GIT: Checking out commit '%s' in '%s'...",
        commit_hash_to_checkout,
        checkout_path,
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
          "Failed to checkout commit '%s'. HEAD is at '%s', expected '%s'."
          " Repo: '%s'",
          commit_hash_to_checkout,
          current_commit,
          resolved_target_commit,
          repo.name,
        )
      logger.info(
        "ORCH-GIT: Successfully checked out '%s' (resolved to '%s').",
        commit_hash_to_checkout,
        current_commit,
      )
      module_path_to_add_for_sys_path = checkout_path

    elif (
      protocol_def_orm.file_system_source_accession_id
      and protocol_def_orm.file_system_source
    ):
      fs_source = protocol_def_orm.file_system_source
      if not os.path.isdir(fs_source.base_path):
        raise ValueError(
          "Invalid base path '%s' for FS source '%s'.",
          fs_source.base_path,
          fs_source.name,
        )
      module_path_to_add_for_sys_path = fs_source.base_path
    else:
      logger.warning(
        "Protocol '%s' has no linked source. Attempting direct import.",
        protocol_def_orm.name,
      )

    with temporary_sys_path(module_path_to_add_for_sys_path):
      if protocol_def_orm.module_name in sys.modules:
        module = importlib.reload(sys.modules[protocol_def_orm.module_name])
        logger.debug("Reloaded module: %s", protocol_def_orm.module_name)
      else:
        module = importlib.import_module(protocol_def_orm.module_name)
        logger.debug("Imported module: %s", protocol_def_orm.module_name)

    if not hasattr(module, protocol_def_orm.function_name):
      raise AttributeError(
        "Function '%s' not found in module '%s' from path '%s'.",
        protocol_def_orm.function_name,
        protocol_def_orm.module_name,
        module_path_to_add_for_sys_path or "PYTHONPATH",
      )

    func_wrapper = getattr(module, protocol_def_orm.function_name)
    pydantic_def: Optional[FunctionProtocolDefinitionModel] = getattr(
      func_wrapper, "_protocol_definition", None
    )

    if not pydantic_def or not isinstance(
      pydantic_def, FunctionProtocolDefinitionModel
    ):
      raise AttributeError(
        "Function '%s' in '%s' is not a valid @protocol_function "
        "(missing or invalid _protocol_definition attribute).",
        protocol_def_orm.function_name,
        protocol_def_orm.module_name,
      )

    if protocol_def_orm.accession_id and (
      not pydantic_def.db_accession_id
      or pydantic_def.db_accession_id != protocol_def_orm.accession_id
    ):
      pydantic_def.db_accession_id = protocol_def_orm.accession_id  # type: ignore[assignment]
      logger.debug(
        "Updated Pydantic definition DB ID for '%s' to %s",
        pydantic_def.name,
        protocol_def_orm.accession_id,
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
            "ORCH-GIT: Path '%s' for repo '%s' exists but is not a git "
            "work-tree root.",
            checkout_path,
            repo_name_for_logging,
          )
      except RuntimeError:
        is_git_repo = False
        logger.info(
          "ORCH-GIT: Path '%s' for repo '%s' is not a git repository or git "
          "command failed.",
          checkout_path,
          repo_name_for_logging,
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
            "Path '%s' for repo '%s' is a Git repository, but its remote "
            "'origin' URL ('%s') does not match the expected URL ('%s'). "
            "Manual intervention required.",
            checkout_path,
            repo_name_for_logging,
            current_remote_url,
            git_url,
          )
      except RuntimeError as e:
        raise ValueError(
          "Failed to verify remote URL for existing repo at '%s'. Error: %s",
          checkout_path,
          e,
        ) from e

      logger.info(
        "ORCH-GIT: '%s' is existing repo for '%s'. Fetching origin...",
        checkout_path,
        repo_name_for_logging,
      )
      await self._run_git_command(
        ["git", "fetch", "origin", "--prune"], cwd=checkout_path
      )
    else:
      if os.path.exists(checkout_path):
        if os.listdir(checkout_path):
          raise ValueError(
            "Path '%s' for repo '%s' exists, is not Git, and not empty. "
            "Cannot clone.",
            checkout_path,
            repo_name_for_logging,
          )
        logger.info(
          "ORCH-GIT: Path '%s' for repo '%s' exists and is empty. " "Cloning into it.",
          checkout_path,
          repo_name_for_logging,
        )
      else:
        logger.info(
          "ORCH-GIT: Path '%s' for repo '%s' does not exist. "
          "Creating and cloning...",
          checkout_path,
          repo_name_for_logging,
        )
        try:
          os.makedirs(checkout_path, exist_ok=True)
        except OSError as e:
          raise ValueError(
            "Failed to create directory '%s': %s", checkout_path, e
          ) from e
      logger.info(
        "ORCH-GIT: Cloning repository '%s' into '%s' for repo '%s'...",
        git_url,
        checkout_path,
        repo_name_for_logging,
      )
      await self._run_git_command(["git", "clone", git_url, "."], cwd=checkout_path)

  async def _prepare_arguments(
    self,
    db_session: AsyncSession,
    protocol_pydantic_def: FunctionProtocolDefinitionModel,
    user_input_params: Dict[str, Any],
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

      if param_meta.name in user_input_params:
        final_args[param_meta.name] = user_input_params[param_meta.name]
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
          "ORCH-ACQUIRE: Acquiring asset '%s' (Type: '%s', Optional: %s) "
          "for run '%s'.",
          asset_req_model.name,
          asset_req_model.actual_type_str,
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
      deck_accession_identifier_from_user = user_input_params.get(deck_param_name)

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
    user_input_params: Optional[Dict[str, Any]] = None,
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
    user_input_params = user_input_params or {}
    initial_state_data = initial_state_data or {}
    run_accession_id = uuid7()
    start_iso_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    logger.info(
      "ORCH: Initiating protocol run %s for '%s' at %s. "
      "User params: %s, Initial state: %s",
      run_accession_id,
      protocol_name,
      start_iso_timestamp,
      user_input_params,
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
          input_parameters_json=json.dumps(user_input_params),
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
        input_parameters_json=json.dumps(user_input_params),
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
          user_input_params=user_input_params,
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
              "ORCH: No prior workcell state snapshot found for run %s to" " rollback.",
              run_accession_id,
            )
        except Exception as rollback_error:
          logger.critical(
            "ORCH: CRITICAL - Failed to rollback workcell state for run %s:" " %s",
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
                "User intervention needed to verify liquid levels and" " proceed."
              ),
              "traceback": traceback.format_exc(),
            }
          )
        elif isinstance(e, PyLabRobotGenericError):
          logger.info(
            "Generic PyLabRobot error detected for run %s. Setting status"
            " to FAILED.",
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
                  "ORCH-RELEASE: Asset '%s' (Type: %s, ORM ID: %s)" " released.",
                  name_in_protocol,
                  asset_type,
                  asset_orm_accession_id,
                )
              except Exception as release_err:
                logger.error(
                  "ORCH-RELEASE: Failed to release asset '%s' (ORM ID:" " %s): %s",
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
