# pylint: disable=too-many-arguments,broad-except,fixme
"""Protocol Code Manager - Handles protocol code preparation and loading.

This module is responsible for preparing protocol code for execution, including:
- Git repository management and checkout operations
- Module imports and reloading
- Protocol function loading and validation
- Source code path management

This separates the code preparation concerns from the main Orchestrator,
allowing for cleaner separation of responsibilities.
"""

import asyncio
import contextlib
import importlib
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from praxis.backend.models import (
  FunctionProtocolDefinitionCreate,
  FunctionProtocolDefinitionOrm,
)
from praxis.backend.utils.logging import get_logger

logger = get_logger(__name__)


@contextlib.contextmanager
def temporary_sys_path(path_to_add: str | None):
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


class ProtocolCodeManager:

  """Manages protocol code preparation and loading for execution.

  This class handles all aspects of preparing protocol code for execution,
  including Git operations, module imports, and function loading. It provides
  a clean interface for the Orchestrator to get executable protocol functions
  without worrying about the underlying source management complexity.
  """

  def __init__(self) -> None:
    """Initialize the Protocol Code Manager."""
    logger.info("ProtocolCodeManager initialized.")

  async def _run_git_command(
    self,
    command: list[str],
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
        "CODE-GIT: Running command: %s in %s with timeout %ds",
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
          logger.debug("CODE-GIT: STDOUT: %s", stdout_stripped)
        if stderr_stripped:
          logger.debug("CODE-GIT: STDERR: %s", stderr_stripped)
      return process.stdout.strip()
    except subprocess.TimeoutExpired as e:
      cmd_str = " ".join(e.cmd)
      stderr_str = e.stderr.decode(errors="ignore").strip() if e.stderr else "N/A"
      stdout_str = e.stdout.decode(errors="ignore").strip() if e.stdout else "N/A"
      error_message = (
        f"CODE-GIT: Command '{cmd_str}' timed out after {e.timeout} seconds in {cwd}.\n"
        f"Stderr: {stderr_str}\nStdout: {stdout_str}"
      )
      logger.exception(error_message)
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
      cmd_str = " ".join(e.cmd)
      error_message = (
        f"CODE-GIT: Command '{cmd_str}' failed with exit code {e.returncode} in {cwd}.\n"
        f"Stderr: {stderr_output}\nStdout: {stdout_output}"
      )
      logger.exception(error_message)
      raise RuntimeError(error_message) from e
    except FileNotFoundError:  # pragma: no cover
      cmd_str = " ".join(command)
      error_message = f"CODE-GIT: Git command not found. Ensure git is installed. Command: {cmd_str}"
      logger.exception(error_message)
      raise RuntimeError(error_message) from None

  async def _ensure_git_repo_and_fetch(
    self,
    git_url: str,
    checkout_path: str,
    repo_name_for_logging: str,
  ) -> None:
    """Ensure a git repo exists at checkout_path, clones if not, and fetches updates.

    Args:
        git_url: The Git repository URL to clone/fetch from.
        checkout_path: Local path where the repository should be checked out.
        repo_name_for_logging: Human-readable name for logging purposes.

    Raises:
        ValueError: If there are conflicts with existing repositories or paths.
        RuntimeError: If Git operations fail.

    """
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
            "CODE-GIT: Path '%s' for repo '%s' exists but is not a git work-tree root.",
            checkout_path,
            repo_name_for_logging,
          )
      except RuntimeError:
        is_git_repo = False
        logger.info(
          "CODE-GIT: Path '%s' for repo '%s' is not a git repository or git command failed.",
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
          msg = (
            f"Path '{checkout_path}' for repo '{repo_name_for_logging}' is a Git repository, "
            f"but its remote 'origin' URL ('{current_remote_url}') does not match the expected "
            f"URL ('{git_url}'). Manual intervention required."
          )
          raise ValueError(
            msg,
          )
      except RuntimeError as e:
        msg = f"Failed to verify remote URL for existing repo at '{checkout_path}'. Error: {e}"
        raise ValueError(
          msg,
        ) from e

      logger.info(
        "CODE-GIT: '%s' is existing repo for '%s'. Fetching origin...",
        checkout_path,
        repo_name_for_logging,
      )
      await self._run_git_command(
        ["git", "fetch", "origin", "--prune"],
        cwd=checkout_path,
      )
    else:
      if os.path.exists(checkout_path):
        if any(Path(checkout_path).iterdir()):
          msg = (
            f"Path '{checkout_path}' for repo '{repo_name_for_logging}' exists, "
            f"is not Git, and not empty. Cannot clone."
          )
          raise ValueError(
            msg,
          )
        logger.info(
          "CODE-GIT: Path '%s' for repo '%s' exists and is empty. Cloning into it.",
          checkout_path,
          repo_name_for_logging,
        )
      else:
        logger.info(
          "CODE-GIT: Path '%s' for repo '%s' does not exist. Creating and cloning...",
          checkout_path,
          repo_name_for_logging,
        )
        try:
          os.makedirs(checkout_path, exist_ok=True)
        except OSError as e:
          msg = f"Failed to create directory '{checkout_path}': {e}"
          raise ValueError(msg) from e

      logger.info(
        "CODE-GIT: Cloning repository '%s' into '%s' for repo '%s'...",
        git_url,
        checkout_path,
        repo_name_for_logging,
      )
      await self._run_git_command(["git", "clone", git_url, "."], cwd=checkout_path)

  async def _checkout_specific_commit(
    self,
    checkout_path: str,
    commit_hash: str,
    repo_name_for_logging: str,
  ) -> None:
    """Checkout a specific commit and verify it's correct.

    Args:
        checkout_path: Local path of the Git repository.
        commit_hash: The commit hash to checkout.
        repo_name_for_logging: Human-readable name for logging purposes.

    Raises:
        RuntimeError: If the checkout fails or verification fails.

    """
    logger.info(
      "CODE-GIT: Checking out commit '%s' in '%s'...",
      commit_hash,
      checkout_path,
    )
    await self._run_git_command(["git", "checkout", commit_hash], cwd=checkout_path)

    # Verify the checkout was successful
    current_commit = await self._run_git_command(
      ["git", "rev-parse", "HEAD"],
      cwd=checkout_path,
      suppress_output=True,
    )
    resolved_target_commit = await self._run_git_command(
      ["git", "rev-parse", commit_hash + "^{commit}"],
      cwd=checkout_path,
      suppress_output=True,
    )
    if current_commit != resolved_target_commit:
      msg = (
        f"Failed to checkout commit '{commit_hash}'. HEAD is at '{current_commit}', "
        f"expected '{resolved_target_commit}'. Repo: '{repo_name_for_logging}'"
      )
      raise RuntimeError(
        msg,
      )
    logger.info(
      "CODE-GIT: Successfully checked out '%s' (resolved to '%s').",
      commit_hash,
      current_commit,
    )

  def _load_protocol_function(
    self,
    module_name: str,
    function_name: str,
    module_path: str | None = None,
  ) -> tuple[Callable, FunctionProtocolDefinitionCreate]:
    """Load a protocol function from its module.

    Args:
        module_name: The Python module name containing the function.
        function_name: The name of the protocol function to load.
        module_path: Optional path to add to sys.path for importing.

    Returns:
        A tuple containing the callable function and its Pydantic definition model.

    Raises:
        AttributeError: If the function or its definition is not found.
        ImportError: If the module cannot be imported.

    """
    with temporary_sys_path(module_path):
      if module_name in sys.modules:
        module = importlib.reload(sys.modules[module_name])
        logger.debug("Reloaded module: %s", module_name)
      else:
        module = importlib.import_module(module_name)
        logger.debug("Imported module: %s", module_name)

    if not hasattr(module, function_name):
      msg = (
        f"Function '{function_name}' not found in module '{module_name}' "
        f"from path '{module_path or 'PYTHONPATH'}'."
      )
      raise AttributeError(
        msg,
      )

    func_wrapper = getattr(module, function_name)
    pydantic_def: FunctionProtocolDefinitionCreate | None = getattr(
      func_wrapper,
      "_protocol_definition",
      None,
    )

    if not pydantic_def or not isinstance(
      pydantic_def,
      FunctionProtocolDefinitionCreate,
    ):
      msg = (
        f"Function '{function_name}' in '{module_name}' is not a valid @protocol_function "
        f"(missing or invalid _protocol_definition attribute)."
      )
      raise AttributeError(
        msg,
      )

    return func_wrapper, pydantic_def

  def _load_callable_from_fqn(self, fqn: str) -> Callable:
    """Dynamically load a callable (function or class) from its fully qualified name.

    Args:
        fqn (str): The fully qualified name of the callable (e.g., "my_module.my_function").

    Returns:
        Callable: The loaded callable object.

    Raises:
        ValueError: If the FQN is invalid or the callable cannot be found.
        ImportError: If the module cannot be imported.
        AttributeError: If the callable is not found within the module.

    """
    if not fqn or "." not in fqn:
      msg = f"Invalid fully qualified name for callable: {fqn}"
      raise ValueError(msg)

    module_name, callable_name = fqn.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, callable_name)

  async def prepare_protocol_code(
    self,
    protocol_def_orm: FunctionProtocolDefinitionOrm,
  ) -> tuple[Callable, FunctionProtocolDefinitionCreate]:
    """Prepare protocol code for execution from its ORM definition.

    This method handles all the complexities of loading protocol code from various sources:
    - Git repositories (with specific commit checkout)
    - File system sources
    - Direct Python imports

    Args:
        protocol_def_orm: The ORM object representing the protocol definition.

    Returns:
        A tuple containing the callable function and its Pydantic definition model.

    Raises:
        ValueError: If the protocol definition is incomplete or invalid.
        AttributeError: If the function or its Pydantic definition is not found.
        RuntimeError: If there is an error with Git operations.

    """
    logger.info(
      "Preparing code for protocol: %s v%s",
      protocol_def_orm.name,
      protocol_def_orm.version,
    )
    module_path_to_add_for_sys_path: str | None = None

    # Handle Git repository sources
    if protocol_def_orm.source_repository_accession_id and protocol_def_orm.source_repository:
      repo = protocol_def_orm.source_repository
      checkout_path = repo.local_checkout_path
      commit_hash_to_checkout = protocol_def_orm.commit_hash

      if not checkout_path or not commit_hash_to_checkout or not repo.git_url:
        msg = f"Incomplete Git source info for protocol '{protocol_def_orm.name}'."
        raise ValueError(
          msg,
        )

      await self._ensure_git_repo_and_fetch(repo.git_url, checkout_path, repo.name)
      await self._checkout_specific_commit(
        checkout_path,
        commit_hash_to_checkout,
        repo.name,
      )
      module_path_to_add_for_sys_path = checkout_path

    # Handle file system sources
    elif protocol_def_orm.file_system_source_accession_id and protocol_def_orm.file_system_source:
      fs_source = protocol_def_orm.file_system_source
      if not os.path.isdir(fs_source.base_path):
        msg = f"Invalid base path '{fs_source.base_path}' for FS source '{fs_source.name}'."
        raise ValueError(
          msg,
        )
      module_path_to_add_for_sys_path = fs_source.base_path

    # Handle protocols without explicit sources
    else:
      logger.warning(
        "Protocol '%s' has no linked source. Attempting direct import.",
        protocol_def_orm.name,
      )

    # Load the actual function
    try:
      func_wrapper, pydantic_def = self._load_protocol_function(
        protocol_def_orm.module_name,
        protocol_def_orm.function_name,
        module_path_to_add_for_sys_path,
      )

      if protocol_def_orm.accession_id and (
        not pydantic_def.accession_id or pydantic_def.accession_id != protocol_def_orm.accession_id
      ):
        pydantic_def.accession_id = protocol_def_orm.accession_id
        logger.debug(
          "Updated Pydantic definition DB ID for '%s' to %s",
          pydantic_def.name,
          protocol_def_orm.accession_id,
        )

      return func_wrapper, pydantic_def

    except Exception:
      logger.exception(
        "Failed to load protocol function '%s' from module '%s'",
        protocol_def_orm.function_name,
        protocol_def_orm.module_name,
      )
      raise
