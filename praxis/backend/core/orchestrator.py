# pylint: disable=too-many-arguments,too-many-locals,broad-except,fixme,unused-argument,too-many-statements,too-many-branches
"""
praxis/core/orchestrator.py

The Orchestrator is responsible for managing the lifecycle of protocol runs.
It fetches protocol definitions, prepares the execution environment (including state),
invokes the protocol functions, and oversees logging.

Version 5: Adds Pause, Resume, Cancel functionality.
"""
import importlib
import os
import sys
import uuid
import json
import datetime
import traceback
from typing import Dict, Any, Optional, Callable, Tuple, List, Union, get_origin, get_args
import contextlib
import time
import subprocess
import inspect # ADDED FOR TYPE HINT INSPECTION

from sqlalchemy.orm import Session as DbSession

# Utilities
from praxis.backend.utils.run_control import get_control_command, clear_control_command # ADDED (ALLOWED_COMMANDS not directly used here)
from praxis.utils.state import State as PraxisState
from praxis.protocol_core.definitions import (
    PraxisRunContext, PlrDeck, DeckInputType, PlrResource, PROTOCOL_REGISTRY
)
from praxis.backend.core.asset_manager import AssetManager, AssetAcquisitionError

# JSONSchema validation
from praxis.backend.protocol.jsonschema_utils import definition_model_parameters_to_jsonschema
try:
    from jsonschema import validate as validate_jsonschema, ValidationError as JsonSchemaValidationError
except ImportError: # pragma: no cover
    print("WARNING: ORCH-JSONSCHEMA: jsonschema library not installed. Parameter validation will be skipped.")
    validate_jsonschema = None # type: ignore
    JsonSchemaValidationError = None # type: ignore
from praxis.backend.protocol_core.protocol_definition_models import FunctionProtocolDefinitionModel, AssetRequirementModel

# ORM Models & Data Services
from praxis.database_models.protocol_definitions_orm import (
    FunctionProtocolDefinitionOrm,
    ProtocolRunOrm,
    ProtocolRunStatusEnum,
    ProtocolSourceRepositoryOrm,
    FileSystemProtocolSourceOrm,
    LabwareInstanceStatusEnum,
    ManagedDeviceStatusEnum 
)
try:
    from praxis.backend.services.protocol_data_service import ( 
        create_protocol_run,
        update_protocol_run_status,
        get_protocol_definition_details
    )
    from praxis.backend.services import asset_data_service # ADDED FOR FQN LOOKUP
except ImportError: # pragma: no cover
    print("WARNING: ORCH-0: Could not import from praxis.db_services.protocol_data_service. Orchestrator DB operations will be placeholder/limited.")
    def create_protocol_run(db, run_guid, top_level_protocol_definition_id, **kwargs): # type: ignore
        print(f"[Orch-PlaceholderDB] Create ProtocolRun: guid={run_guid}, def_id={top_level_protocol_definition_id}")
        class DummyRun: id = abs(hash(run_guid)); run_guid=run_guid; status=kwargs.get('status'); # type: ignore
        return DummyRun()
    def update_protocol_run_status(db, protocol_run_id, new_status, **kwargs): # type: ignore
        print(f"[Orch-PlaceholderDB] Update ProtocolRun: id={protocol_run_id}, status={new_status.name}")
        class DummyRun: id = protocol_run_id; status=new_status # type: ignore
        return DummyRun()
    def get_protocol_definition_details(db, name, version=None, source_name=None, commit_hash=None): # type: ignore
        print(f"[Orch-PlaceholderDB] Get ProtocolDef: name={name}, v={version}")
        return None
    asset_data_service = None # type: ignore


@contextlib.contextmanager
def temporary_sys_path(path_to_add: Optional[str]):
    original_sys_path = list(sys.path)
    path_added = False
    if path_to_add and path_to_add not in sys.path:
        sys.path.insert(0, path_to_add)
        path_added = True
    try:
        yield
    finally:
        if path_added and path_to_add:
            if path_to_add in sys.path: sys.path.remove(path_to_add)
            else: sys.path = original_sys_path


from praxis.backend.core.workcell_runtime import WorkcellRuntime # Add import

class AssetAcquisitionError(RuntimeError): pass
class ProtocolCancelledError(Exception): pass # ADDED

class Orchestrator:
    def __init__(self, db_session: DbSession, workcell_config: Optional[Dict[str, Any]] = None):
        self.db_session = db_session
        self.workcell_config = workcell_config or {}
        # Create and pass a WorkcellRuntime instance
        self.workcell_runtime = WorkcellRuntime(db_session=self.db_session) # Create WCR
        self.asset_manager = AssetManager(db_session=self.db_session, workcell_runtime=self.workcell_runtime) # Pass WCR

    def _run_git_command(self, command: List[str], cwd: str, suppress_output: bool = False, timeout: int = 300) -> str:
        """
        Helper to run a Git command and handle errors.
        Includes a timeout to prevent indefinite hangs.
        Default timeout is 300 seconds (5 minutes).
        """
        try:
            # Construct a more readable command string for logging, being mindful of potential injection if not careful with inputs.
            # However, 'command' is a List[str] from internal calls, so it's safer.
            logged_command = ' '.join(command)
            print(f"INFO: ORCH-GIT: Running command: {logged_command} in {cwd} with timeout {timeout}s")
            process = subprocess.run(
                command,
                cwd=cwd,
                check=True, # Raises CalledProcessError on non-zero exit codes.
                capture_output=True,
                text=True,
                timeout=timeout # Added timeout
            )
            # Log output only if not suppressed, and if there's actual content.
            if not suppress_output:
                stdout_stripped = process.stdout.strip()
                stderr_stripped = process.stderr.strip() # Git often uses stderr for non-error info like 'Already up to date.'
                if stdout_stripped: print(f"INFO: ORCH-GIT: STDOUT: {stdout_stripped}")
                if stderr_stripped: print(f"INFO: ORCH-GIT: STDERR: {stderr_stripped}")
            return process.stdout.strip()
        except subprocess.TimeoutExpired as e:
            error_message = (
                f"ERROR: ORCH-GIT: Command '{' '.join(e.cmd)}' timed out after {e.timeout} seconds in {cwd}.\n"
                f"Stderr: {e.stderr.decode(errors='ignore').strip() if e.stderr else 'N/A'}\n"
                f"Stdout: {e.stdout.decode(errors='ignore').strip() if e.stdout else 'N/A'}"
            )
            print(error_message)
            # Propagate as RuntimeError to be caught by the calling function for consistent error handling.
            raise RuntimeError(error_message) from e
        except subprocess.CalledProcessError as e:
            # Ensure stderr and stdout are decoded if they are bytes, though text=True should handle this.
            stderr_output = e.stderr.strip() if isinstance(e.stderr, str) else e.stderr.decode(errors='ignore').strip() if e.stderr else "N/A"
            stdout_output = e.stdout.strip() if isinstance(e.stdout, str) else e.stdout.decode(errors='ignore').strip() if e.stdout else "N/A"
            error_message = (
                f"ERROR: ORCH-GIT: Command '{' '.join(e.cmd)}' failed with exit code {e.returncode} in {cwd}.\n"
                f"Stderr: {stderr_output}\n"
                f"Stdout: {stdout_output}"
            )
            print(error_message)
            # Propagate as RuntimeError
            raise RuntimeError(error_message) from e
        except FileNotFoundError: # pragma: no cover
            error_message = f"ERROR: ORCH-GIT: Git command (usually 'git') not found. Ensure git is installed and in PATH. Command attempted: {' '.join(command)}"
            print(error_message)
            raise RuntimeError(error_message) # from None explicitly, as FileNotFoundError doesn't chain well here for the intended purpose.

    def _get_protocol_definition_orm_from_db(
        self,
        protocol_name: str,
        version: Optional[str] = None,
        commit_hash: Optional[str] = None,
        source_name: Optional[str] = None
    ) -> Optional[FunctionProtocolDefinitionOrm]:
        return get_protocol_definition_details(
            db=self.db_session,
            name=protocol_name,
            version=version,
            source_name=source_name,
            commit_hash=commit_hash
        )

    def _prepare_protocol_code(
        self,
        protocol_def_orm: FunctionProtocolDefinitionOrm
    ) -> Tuple[Callable, Dict[str, Any]]:
        module_path_to_add_for_sys_path: Optional[str] = None
        if protocol_def_orm.source_repository_id and protocol_def_orm.source_repository:
            repo = protocol_def_orm.source_repository
            checkout_path = repo.local_checkout_path
            commit_hash_to_checkout = protocol_def_orm.commit_hash

            if not checkout_path: # Should be validated by caller or DB constraints
                raise ValueError(f"CRITICAL: Local checkout path not configured for repo '{repo.name}'. This should be pre-validated.")
            if not commit_hash_to_checkout: # Should be validated by caller or DB constraints
                raise ValueError(f"CRITICAL: Commit hash not specified for protocol '{protocol_def_orm.name}' from repo '{repo.name}'. This should be pre-validated.")
            if not repo.git_url: # Should be validated by caller or DB constraints
                raise ValueError(f"CRITICAL: Git URL not configured for repo '{repo.name}'. This should be pre-validated.")

            # Ensure checkout_path is an absolute path for security and clarity
            # If relative paths are allowed, they should be relative to a configured, secure base directory.
            # For now, let's assume checkout_path from DB is intended to be absolute or relative to a known location.
            # If it's user-configurable, it MUST be validated upstream to prevent traversal.
            # We'll proceed assuming it's a valid, designated path for this repo.

            self._ensure_git_repo_and_fetch(repo.git_url, checkout_path, repo.name)

            print(f"INFO: ORCH-GIT: Checking out commit '{commit_hash_to_checkout}' in '{checkout_path}'...")
            # Use --force for checkout if needed to discard local changes, though this should ideally be clean.
            # For now, a simple checkout. If it fails due to local changes, that's an issue with the repo state.
            self._run_git_command(["git", "checkout", commit_hash_to_checkout], cwd=checkout_path)

            # Verify HEAD is at the correct commit
            try:
                current_commit = self._run_git_command(["git", "rev-parse", "HEAD"], cwd=checkout_path, suppress_output=True)
                if current_commit != commit_hash_to_checkout:
                    # This could happen if the commit_hash is an annotated tag, checkout might resolve it to the commit
                    # Let's check if the resolved commit of the checked-out ref matches the target hash
                    resolved_target_commit = self._run_git_command(["git", "rev-parse", commit_hash_to_checkout + "^{commit}"], cwd=checkout_path, suppress_output=True)
                    if current_commit != resolved_target_commit:
                        raise RuntimeError(
                            f"Failed to checkout commit '{commit_hash_to_checkout}'. "
                            f"HEAD is at '{current_commit}', expected '{resolved_target_commit}'. Repo: '{repo.name}'"
                        )
                    print(f"INFO: ORCH-GIT: Successfully checked out '{commit_hash_to_checkout}' (resolved to '{current_commit}').")
                else:
                    print(f"INFO: ORCH-GIT: Successfully checked out commit '{commit_hash_to_checkout}'. HEAD is at '{current_commit}'.")
            except RuntimeError as e: # pragma: no cover (should be caught by checkout command itself, but as a safeguard)
                raise RuntimeError(f"Failed to verify commit after checkout for repo '{repo.name}': {e}")


            module_path_to_add_for_sys_path = checkout_path
        elif protocol_def_orm.file_system_source_id and protocol_def_orm.file_system_source:
            fs_source = protocol_def_orm.file_system_source
            if not os.path.isdir(fs_source.base_path): # Should be validated upstream
                 raise ValueError(f"CRITICAL: Base path '{fs_source.base_path}' for FS source '{fs_source.name}' invalid. This should be pre-validated.")
            module_path_to_add_for_sys_path = fs_source.base_path
        else: # pragma: no cover (should ideally not happen if data is consistent)
            print(f"WARNING: Protocol '{protocol_def_orm.name}' v{protocol_def_orm.version} has no linked Git or FS source. Direct import attempt from current sys.path.")
            # No specific path to add for sys.path in this case, relies on existing PYTHONPATH

        # Security Note: Importing and executing code from the checked-out repository
        # implies trust in the source of the protocol code. The code runs with the
        # same privileges as the Orchestrator process. Ensure repositories are from
        # trusted sources and code is reviewed.
        with temporary_sys_path(module_path_to_add_for_sys_path):
            # Ensure the target module for the protocol is reloaded to pick up changes if already imported.
            # This is crucial if multiple versions or protocols from the same module are run.
            if protocol_def_orm.module_name in sys.modules:
                module = importlib.reload(sys.modules[protocol_def_orm.module_name])
            else:
                module = importlib.import_module(protocol_def_orm.module_name)

        
        if not hasattr(module, protocol_def_orm.function_name):
            raise AttributeError(f"Function '{protocol_def_orm.function_name}' not found in module '{protocol_def_orm.module_name}' from path '{module_path_to_add_for_sys_path or 'PYTHONPATH'}'.")

        func_wrapper = getattr(module, protocol_def_orm.function_name)
        if not hasattr(func_wrapper, 'protocol_metadata'): # Check for decorator
            raise AttributeError(f"Function '{protocol_def_orm.function_name}' in '{protocol_def_orm.module_name}' is not a valid @protocol_function (missing protocol_metadata).")

        decorator_metadata: Dict[str, Any] = func_wrapper.protocol_metadata
        # Update DB ID in decorator metadata if necessary (though ideally it's consistent)
        if decorator_metadata.get("db_id") != protocol_def_orm.id: # pragma: no cover
            print(f"WARN: ORCH-META: Decorator DB ID mismatch for '{protocol_def_orm.name}'. Forcing DB ID from {decorator_metadata.get('db_id')} to {protocol_def_orm.id}")
            decorator_metadata["db_id"] = protocol_def_orm.id
            # Also update the global registry if this protocol was registered
            registry_key = decorator_metadata.get("protocol_unique_key")
            if registry_key and registry_key in PROTOCOL_REGISTRY:
                PROTOCOL_REGISTRY[registry_key]["db_id"] = protocol_def_orm.id
        
        return func_wrapper, decorator_metadata

    def _ensure_git_repo_and_fetch(self, git_url: str, checkout_path: str, repo_name_for_logging: str) -> None:
        """
        Ensures that checkout_path is a valid git repo for git_url, clones if necessary, and fetches.
        """
        is_git_repo = False
        if os.path.exists(checkout_path):
            try:
                result = self._run_git_command(["git", "rev-parse", "--is-inside-work-tree"], cwd=checkout_path, suppress_output=True)
                is_git_repo = result == "true"
                if not is_git_repo:
                    print(f"WARN: ORCH-GIT: Path '{checkout_path}' for repo '{repo_name_for_logging}' exists but is not a git work-tree root.")
            except RuntimeError: # Error running git rev-parse (e.g. not a git repo, or git not installed)
                is_git_repo = False
                print(f"INFO: ORCH-GIT: Path '{checkout_path}' for repo '{repo_name_for_logging}' is not a git repository or git command failed.")

        if is_git_repo:
            # Verify remote URL matches
            try:
                current_remote_url = self._run_git_command(["git", "config", "--get", "remote.origin.url"], cwd=checkout_path, suppress_output=True)
                if current_remote_url != git_url:
                    # This is a problematic state: a different repo exists at the expected path.
                    # For safety, we should not proceed. Manual intervention is likely needed.
                    raise ValueError(
                        f"Path '{checkout_path}' for repo '{repo_name_for_logging}' is a Git repository, "
                        f"but its remote 'origin' URL ('{current_remote_url}') does not match the expected URL ('{git_url}'). "
                        "Manual intervention required to resolve this conflict."
                    )
            except RuntimeError as e: # git config might fail if 'origin' doesn't exist or other issues
                raise ValueError(
                    f"Failed to verify remote URL for existing repo at '{checkout_path}' for '{repo_name_for_logging}'. Error: {e}. Manual intervention may be needed."
                ) from e

            print(f"INFO: ORCH-GIT: '{checkout_path}' for repo '{repo_name_for_logging}' is an existing Git repository. Fetching origin...")
            self._run_git_command(["git", "fetch", "origin"], cwd=checkout_path) # Consider adding --prune
        else:
            # Path is not a git repo or does not exist. Attempt to clone.
            if os.path.exists(checkout_path):
                if os.listdir(checkout_path): # Directory is not empty
                    # This state was previously checked, but as a safeguard if logic changes.
                    raise ValueError(
                        f"Path '{checkout_path}' for repo '{repo_name_for_logging}' exists, is not a Git repository, and is not empty. "
                        f"Cannot clone into it."
                    )
                else: # Directory exists but is empty
                    print(f"INFO: ORCH-GIT: Path '{checkout_path}' for repo '{repo_name_for_logging}' exists and is empty. Cloning into it.")
            else: # Path does not exist
                print(f"INFO: ORCH-GIT: Path '{checkout_path}' for repo '{repo_name_for_logging}' does not exist. Creating and cloning...")
                try:
                    os.makedirs(checkout_path, exist_ok=True)
                except OSError as e: # pragma: no cover
                    raise ValueError(f"Failed to create directory '{checkout_path}' for repo '{repo_name_for_logging}': {e}") from e
            
            print(f"INFO: ORCH-GIT: Cloning repository '{git_url}' into '{checkout_path}' for repo '{repo_name_for_logging}'...")
            # Clone into the specific checkout_path. The last argument to clone is the directory to clone into.
            self._run_git_command(["git", "clone", git_url, "."], cwd=checkout_path)


    def _prepare_arguments(
        self,
    def _prepare_arguments(
        self,
        protocol_def_orm: FunctionProtocolDefinitionOrm,
        decorator_metadata: Dict[str, Any],
        user_input_params: Dict[str, Any],
        canonical_run_state: PraxisState,
        protocol_wrapper_func: Callable # ADDED to get __wrapped__
    ) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]], List[Dict[str, Any]]]:

        pydantic_def: Optional[FunctionProtocolDefinitionModel] = decorator_metadata.get("pydantic_definition")

        if validate_jsonschema and JsonSchemaValidationError and pydantic_def:
            if hasattr(pydantic_def, 'parameters') and pydantic_def.parameters:
                try:
                    schema_title = f"{pydantic_def.name} v{pydantic_def.version} Parameters"
                    schema_description = pydantic_def.description or "Protocol parameters"
                    param_schema = definition_model_parameters_to_jsonschema(
                        parameters=pydantic_def.parameters,
                        protocol_name=schema_title,
                        protocol_description=schema_description
                    )
                    validate_jsonschema(instance=user_input_params, schema=param_schema)
                    print(f"INFO: User input parameters for '{pydantic_def.name}' validated successfully.")
                except JsonSchemaValidationError as e:
                    raise ValueError(f"Parameter validation failed for protocol '{pydantic_def.name}': {e.message}") from e
                except Exception as schema_gen_e:
                    raise ValueError(f"Schema generation/validation error for '{pydantic_def.name}': {schema_gen_e}") from schema_gen_e
            elif not hasattr(pydantic_def, 'parameters') and user_input_params: # No params defined, but some provided
                 print(f"Warning: Protocol '{pydantic_def.name}' defines no parameters, but input parameters were provided: {list(user_input_params.keys())}")


        final_args: Dict[str, Any] = {}
        state_dict_to_pass: Optional[Dict[str, Any]] = None
        defined_params_from_meta = decorator_metadata.get("parameters", {})
        # This set will track params already handled by explicit decorator definitions (params, state, deck)
        # or explicit asset definitions in @protocol_function(assets=[...])
        processed_param_names_for_asset_inference: set[str] = set(defined_params_from_meta.keys())

        # Handle explicitly defined parameters (non-assets) first
        for param_name_in_sig, param_meta_from_decorator in defined_params_from_meta.items():
            if param_meta_from_decorator.get("is_deck_param"): continue # Deck handled later
            if param_meta_from_decorator.get("is_asset_param"): continue # Assets handled later by combined list

            is_state_param_match = (param_name_in_sig == decorator_metadata.get("state_param_name") and
                                    decorator_metadata.get("found_state_param_details"))
            if is_state_param_match:
                # processed_param_names_for_asset_inference.add(param_name_in_sig) # Already added from defined_params_from_meta.keys()
                state_details = decorator_metadata["found_state_param_details"]
                if state_details.get("expects_praxis_state"): final_args[param_name_in_sig] = canonical_run_state
                elif state_details.get("expects_dict"):
                    state_dict_to_pass = canonical_run_state.data.copy()
                    final_args[param_name_in_sig] = state_dict_to_pass
                else: final_args[param_name_in_sig] = canonical_run_state # Default to PraxisState object
                continue

            if param_name_in_sig in user_input_params:
                final_args[param_name_in_sig] = user_input_params[param_name_in_sig]
            elif not param_meta_from_decorator.get("optional"):
                raise ValueError(f"Mandatory param '{param_name_in_sig}' missing for '{protocol_def_orm.name}'.")

        # --- Asset Inference from Type Hints ---
        inferred_assets_requirements: List[AssetRequirementModel] = []
        if asset_data_service: # Ensure service is available
            original_function = getattr(protocol_wrapper_func, '__wrapped__', protocol_wrapper_func)
            sig = inspect.signature(original_function)

            # Add names of explicitly defined assets from @protocol_function(assets=[...]) to prevent re-processing
            if pydantic_def and pydantic_def.assets:
                for asset_req in pydantic_def.assets:
                    processed_param_names_for_asset_inference.add(asset_req.name)
            # Add state and deck param names as well
            if decorator_metadata.get("state_param_name"):
                processed_param_names_for_asset_inference.add(decorator_metadata["state_param_name"])
            if protocol_def_orm.deck_param_name: # deck_param_name is from DB (FunctionProtocolDefinitionOrm)
                 processed_param_names_for_asset_inference.add(protocol_def_orm.deck_param_name)


            for param_name, param_obj in sig.parameters.items():
                if param_name in processed_param_names_for_asset_inference or param_name.startswith("__praxis_"):
                    continue

                annotation = param_obj.annotation
                if annotation == inspect.Parameter.empty or annotation == Any:
                    continue

                actual_annotation = annotation
                is_optional = get_origin(annotation) is Union and type(None) in get_args(annotation)
                if is_optional:
                    possible_types = [arg for arg in get_args(annotation) if arg is not type(None)]
                    if not possible_types: continue 
                    actual_annotation = possible_types[0]
                
                fqn: Optional[str] = None
                if inspect.isclass(actual_annotation):
                    fqn = f"{actual_annotation.__module__}.{actual_annotation.__name__}"
                elif isinstance(actual_annotation, str): 
                    fqn = actual_annotation.strip("'\"")
                else: 
                    print(f"DEBUG: ORCH-ARG-INFER: Skipping param '{param_name}' due to unhandled annotation type: {type(actual_annotation)}")
                    continue
                
                # Heuristic: focus on PyLabRobot and Praxis types. This can be made configurable.
                # For now, only pylabrobot.resources and direct submodules.
                if not fqn or not (fqn.startswith("pylabrobot.resources") or fqn.startswith("pylabrobot.liquid_handling") or fqn.startswith("pylabrobot.plate_reading") or fqn.startswith("praxis.")):
                    print(f"DEBUG: ORCH-ARG-INFER: Param '{param_name}' with FQN '{fqn}' does not seem to be a known asset type package. Skipping inference.")
                    continue

                print(f"DEBUG: ORCH-ARG-INFER: Potential asset '{param_name}' with FQN '{fqn}', Optional={is_optional}")
                
                asset_type_str_for_model: str
                labware_def_orm = asset_data_service.get_labware_definition_by_fqn(self.db_session, fqn)
                if labware_def_orm:
                    asset_type_str_for_model = labware_def_orm.pylabrobot_definition_name
                    print(f"DEBUG: ORCH-ARG-INFER: Inferred '{param_name}' as LABWARE, maps to definition '{asset_type_str_for_model}'.")
                else:
                    asset_type_str_for_model = fqn # Assume it's a device FQN
                    print(f"DEBUG: ORCH-ARG-INFER: Inferred '{param_name}' as DEVICE with FQN '{asset_type_str_for_model}'.")

                inferred_req = AssetRequirementModel(
                    name=param_name,
                    actual_type_str=asset_type_str_for_model,
                    constraints_json={}, 
                    is_optional=is_optional
                )
                inferred_assets_requirements.append(inferred_req)
                # No need to add to processed_param_names_for_asset_inference here, as this loop already checks it.
        else: # pragma: no cover
            print("WARN: ORCH-ARG-INFER: AssetDataService not available, skipping type hint based asset inference.")

        # --- Combine explicit and inferred assets ---
        final_assets_to_acquire: List[AssetRequirementModel] = []
        final_asset_names_processed: set[str] = set()

        # Add explicitly defined assets first (from @protocol_function(assets=[...]))
        if pydantic_def and pydantic_def.assets:
            for asset_req in pydantic_def.assets:
                final_assets_to_acquire.append(asset_req)
                final_asset_names_processed.add(asset_req.name)
        
        # Add inferred assets only if not already covered by an explicit definition
        for inferred_req in inferred_assets_requirements:
            if inferred_req.name not in final_asset_names_processed:
                final_assets_to_acquire.append(inferred_req)
                final_asset_names_processed.add(inferred_req.name)
            else:
                print(f"DEBUG: ORCH-ARG-INFER: Inferred asset '{inferred_req.name}' was already explicitly defined. Prioritizing explicit definition.")

        # --- Acquire all assets ---
        acquired_assets_details: List[Dict[str, Any]] = []
        if final_assets_to_acquire:
            for asset_req_model in final_assets_to_acquire:
                try:
                    print(f"INFO: ORCH-ACQUIRE: Acquiring asset '{asset_req_model.name}' (type: '{asset_req_model.actual_type_str}', optional: {asset_req_model.is_optional}) for run '{canonical_run_state.run_guid}'.")
                    
                    if not hasattr(self, 'asset_manager') or self.asset_manager is None: # pragma: no cover
                        raise RuntimeError("AssetManager not initialized in Orchestrator.")

                    live_obj, orm_id, asset_kind_str = self.asset_manager.acquire_asset( 
                        protocol_run_guid=canonical_run_state.run_guid,
                        asset_requirement=asset_req_model
                    )
                    final_args[asset_req_model.name] = live_obj
                    acquired_assets_details.append({
                        "type": asset_kind_str, 
                        "orm_id": orm_id,
                        "name_in_protocol": asset_req_model.name
                    })
                    print(f"INFO: ORCH-ACQUIRE: Asset '{asset_req_model.name}' (Kind: {asset_kind_str}, ORM ID: {orm_id}) acquired: {live_obj}")

                except AssetAcquisitionError as e:
                    if asset_req_model.is_optional:
                        print(f"INFO: ORCH-ACQUIRE: Optional asset '{asset_req_model.name}' could not be acquired: {e}. Proceeding as it's optional.")
                        final_args[asset_req_model.name] = None 
                    else:
                        error_msg = f"Failed to acquire mandatory asset '{asset_req_model.name}' for protocol '{pydantic_def.name if pydantic_def else 'unknown'}': {e}"
                        print(f"ERROR: {error_msg}")
                        raise ValueError(error_msg) from e
                except Exception as e_general: # pragma: no cover
                    error_msg = f"Unexpected error acquiring asset '{asset_req_model.name}' for protocol '{pydantic_def.name if pydantic_def else 'unknown'}': {e_general}"
                    print(f"ERROR: {error_msg}")
                    raise ValueError(error_msg) from e_general

        # --- Deck Preconfiguration (after other assets) ---
        if protocol_def_orm.preconfigure_deck and protocol_def_orm.deck_param_name:
            # Ensure deck param name isn't accidentally processed as a regular asset if it was also type-hinted
            # Though `processed_param_names_for_asset_inference` should handle this.
            if protocol_def_orm.deck_param_name in final_args: # pragma: no cover
                 print(f"WARN: ORCH-DECK: Deck parameter '{protocol_def_orm.deck_param_name}' may have been already processed as an asset. Check protocol definition and type hints.")
            
            deck_input = user_input_params.get(protocol_def_orm.deck_param_name)
            deck_to_pass_to_protocol: Optional[Any] = None

            if isinstance(deck_input, str): # Deck layout name
                print(f"INFO: ORCH-DECK: Deck preconfiguration requested for layout '{deck_input}'. Applying...")
                if not hasattr(self.asset_manager, 'apply_deck_configuration'): # pragma: no cover
                    raise NotImplementedError("AssetManager does not have 'apply_deck_configuration' method.")
                configured_plr_deck_obj = self.asset_manager.apply_deck_configuration(
                    deck_identifier=deck_input, protocol_run_guid=canonical_run_state.run_guid)
                deck_to_pass_to_protocol = configured_plr_deck_obj
            elif isinstance(deck_input, PlrDeck): # praxis.protocol_core.definitions.PlrDeck
                deck_layout_name = deck_input.name
                print(f"INFO: ORCH-DECK: Deck preconfiguration with PlrDeck object (layout: '{deck_layout_name}'). Applying...")
                if not hasattr(self.asset_manager, 'apply_deck_configuration'): # pragma: no cover
                    raise NotImplementedError("AssetManager does not have 'apply_deck_configuration' method.")
                configured_plr_deck_obj = self.asset_manager.apply_deck_configuration(
                    deck_identifier=deck_layout_name, protocol_run_guid=canonical_run_state.run_guid)
                deck_to_pass_to_protocol = configured_plr_deck_obj
            elif deck_input is not None:
                 raise ValueError(f"Unsupported type for deck param '{protocol_def_orm.deck_param_name}': {type(deck_input)}. Expected str or PlrDeck.")

            if deck_to_pass_to_protocol:
                final_args[protocol_def_orm.deck_param_name] = deck_to_pass_to_protocol
            elif protocol_def_orm.deck_param_name in defined_params_from_meta and \
                 not defined_params_from_meta[protocol_def_orm.deck_param_name].get("optional") and \
                 deck_input is None: # Mandatory, but not provided
                raise ValueError(f"Mandatory deck param '{protocol_def_orm.deck_param_name}' not provided.")
            
        return final_args, state_dict_to_pass, acquired_assets_details


    def execute_protocol(
        self,
        protocol_name: str, protocol_version: Optional[str] = None,
        commit_hash: Optional[str] = None, source_name: Optional[str] = None,
        user_input_params: Optional[Dict[str, Any]] = None,
        initial_state_data: Optional[Dict[str, Any]] = None,
    ) -> ProtocolRunOrm:
        user_input_params = user_input_params or {}
        initial_state_data = initial_state_data or {}
        run_guid = str(uuid.uuid4())
        utc_now = datetime.datetime.now(datetime.timezone.utc)

        protocol_def_orm = self._get_protocol_definition_orm_from_db(
            protocol_name, protocol_version, commit_hash, source_name
        )

        if not protocol_def_orm or not protocol_def_orm.id:
            error_msg = f"Protocol '{protocol_name}' (v:{protocol_version}, commit:{commit_hash}, src:{source_name}) not found or invalid DB ID."
            error_protocol_def_id = protocol_def_orm.id if protocol_def_orm and protocol_def_orm.id else -1
            error_run_db_obj = create_protocol_run(
                db=self.db_session, run_guid=run_guid,
                top_level_protocol_definition_id=error_protocol_def_id, # type: ignore
                status=ProtocolRunStatusEnum.FAILED,
                input_parameters_json=json.dumps(user_input_params),
                initial_state_json=json.dumps(initial_state_data)
            )
            self.db_session.flush()
            self.db_session.refresh(error_run_db_obj)
            update_protocol_run_status(
                db=self.db_session, protocol_run_id=error_run_db_obj.id, # type: ignore
                new_status=ProtocolRunStatusEnum.FAILED,
                output_data_json=json.dumps({"error": error_msg})
            )
            raise ValueError(error_msg)

        protocol_run_db_obj = create_protocol_run(
            db=self.db_session, run_guid=run_guid,
            top_level_protocol_definition_id=protocol_def_orm.id, # type: ignore
            status=ProtocolRunStatusEnum.PREPARING,
            input_parameters_json=json.dumps(user_input_params),
            initial_state_json=json.dumps(initial_state_data),
        )
        self.db_session.flush()
        self.db_session.refresh(protocol_run_db_obj)

        # --- Initial CANCEL check ---
        initial_command = get_control_command(run_guid)
        if initial_command == "CANCEL":
            print(f"INFO: Protocol run {run_guid} received CANCEL command before preparation.")
            clear_control_command(run_guid)
            update_protocol_run_status(self.db_session, protocol_run_db_obj.id, ProtocolRunStatusEnum.CANCELING)
            # self._handle_cancel_protocol(run_guid, protocol_run_db_obj, []) # No assets acquired yet
            update_protocol_run_status(self.db_session, protocol_run_db_obj.id, ProtocolRunStatusEnum.CANCELLED, output_data_json=json.dumps({"status": "Cancelled by user before preparation."}))
            self.db_session.commit() # Commit status changes
            return protocol_run_db_obj


        canonical_run_state = PraxisState(run_guid=run_guid) 
        if initial_state_data:
            canonical_run_state.update(initial_state_data) 
        run_context = PraxisRunContext(
            protocol_run_db_id=protocol_run_db_obj.id, # type: ignore
            run_guid=run_guid,
            canonical_state=canonical_run_state,
            current_db_session=self.db_session,
            current_call_log_db_id=None 
        )

        prepared_args: Dict[str, Any] = {}
        protocol_wrapper_func: Optional[Callable] = None
        decorator_metadata: Optional[Dict[str, Any]] = None
        state_dict_passed_to_top_level: Optional[Dict[str, Any]] = None
        acquired_assets_info: List[Dict[str, Any]] = [] 

        try:
            protocol_wrapper_func, decorator_metadata = self._prepare_protocol_code(protocol_def_orm)
            prepared_args, state_dict_passed_to_top_level, acquired_assets_info = self._prepare_arguments(
                protocol_def_orm, decorator_metadata, user_input_params, canonical_run_state, protocol_wrapper_func
            )

            # --- Pre-execution command check (PAUSE/CANCEL) ---
            command = get_control_command(run_guid)
            if command == "PAUSE":
                print(f"INFO: Protocol run {run_guid} PAUSED before execution.")
                clear_control_command(run_guid)
                update_protocol_run_status(self.db_session, protocol_run_db_obj.id, ProtocolRunStatusEnum.PAUSING)
                # TODO: Persist non-PraxisState context if necessary for true pause/resume.
                update_protocol_run_status(self.db_session, protocol_run_db_obj.id, ProtocolRunStatusEnum.PAUSED)
                self.db_session.commit()

                while True:
                    new_command = get_control_command(run_guid)
                    if new_command == "RESUME":
                        clear_control_command(run_guid)
                        update_protocol_run_status(self.db_session, protocol_run_db_obj.id, ProtocolRunStatusEnum.RESUMING)
                        # TODO: Restore non-PraxisState context if necessary.
                        update_protocol_run_status(self.db_session, protocol_run_db_obj.id, ProtocolRunStatusEnum.RUNNING)
                        self.db_session.commit()
                        print(f"INFO: Protocol run {run_guid} resumed.")
                        break 
                    elif new_command == "CANCEL":
                        clear_control_command(run_guid)
                        update_protocol_run_status(self.db_session, protocol_run_db_obj.id, ProtocolRunStatusEnum.CANCELING)
                        # self._handle_cancel_protocol(run_guid, protocol_run_db_obj, acquired_assets_info) # Placeholder
                        update_protocol_run_status(self.db_session, protocol_run_db_obj.id, ProtocolRunStatusEnum.CANCELLED, output_data_json=json.dumps({"status": "Cancelled by user during pause."}))
                        self.db_session.commit()
                        raise ProtocolCancelledError(f"Protocol run {run_guid} cancelled by user during pause.")
                    time.sleep(2) 
            elif command == "CANCEL":
                print(f"INFO: Protocol run {run_guid} CANCELLED before execution.")
                clear_control_command(run_guid)
                update_protocol_run_status(self.db_session, protocol_run_db_obj.id, ProtocolRunStatusEnum.CANCELING)
                # self._handle_cancel_protocol(run_guid, protocol_run_db_obj, acquired_assets_info) # Placeholder
                update_protocol_run_status(self.db_session, protocol_run_db_obj.id, ProtocolRunStatusEnum.CANCELLED, output_data_json=json.dumps({"status": "Cancelled by user before execution."}))
                self.db_session.commit()
                raise ProtocolCancelledError(f"Protocol run {run_guid} cancelled by user before execution.")

            if protocol_run_db_obj.status != ProtocolRunStatusEnum.RUNNING: # If not already set to RUNNING (e.g. after RESUME)
                 update_protocol_run_status(self.db_session, protocol_run_db_obj.id, ProtocolRunStatusEnum.RUNNING)
                 self.db_session.commit()


            result = protocol_wrapper_func(**prepared_args, __praxis_run_context__=run_context)

            update_protocol_run_status(
                self.db_session, protocol_run_db_obj.id, ProtocolRunStatusEnum.COMPLETED, 
                output_data_json=json.dumps(result, default=str)
            )
        except ProtocolCancelledError as ce:
            print(f"INFO: {ce}") # Status already set to CANCELLED
            # The finally block will handle asset release and final state commit
        except Exception as e:
            print(f"ERROR during protocol execution for run {run_guid}: {e}")
            error_info = {"error_type": type(e).__name__, "error_message": str(e), "traceback": traceback.format_exc()}
            # Check current status before overriding with FAILED
            current_status_in_db = self.db_session.query(ProtocolRunOrm.status).filter_by(id=protocol_run_db_obj.id).scalar()
            if current_status_in_db not in [ProtocolRunStatusEnum.CANCELLED, ProtocolRunStatusEnum.CANCELING]:
                 update_protocol_run_status(
                    self.db_session, protocol_run_db_obj.id, ProtocolRunStatusEnum.FAILED, 
                    output_data_json=json.dumps(error_info)
                )
        finally:
            final_protocol_run_db_obj = self.db_session.query(ProtocolRunOrm).get(protocol_run_db_obj.id) 
            if final_protocol_run_db_obj:
                if state_dict_passed_to_top_level is not None and protocol_def_orm.is_top_level:
                    print(f"INFO: Merging back state from dict for run {run_guid}.")
                    canonical_run_state.update_from_dict(state_dict_passed_to_top_level)

                final_protocol_run_db_obj.final_state_json = json.dumps(canonical_run_state.to_dict(), default=str)
                if not final_protocol_run_db_obj.end_time:
                    final_protocol_run_db_obj.end_time = datetime.datetime.now(datetime.timezone.utc)
                if final_protocol_run_db_obj.start_time and final_protocol_run_db_obj.end_time and \
                   final_protocol_run_db_obj.duration_ms is None :
                    duration = final_protocol_run_db_obj.end_time - final_protocol_run_db_obj.start_time
                    final_protocol_run_db_obj.duration_ms = int(duration.total_seconds() * 1000)
                
                if acquired_assets_info: 
                    print(f"INFO: Releasing {len(acquired_assets_info)} acquired assets for run {run_guid}...")
                    for asset_info in acquired_assets_info:
                        try:
                            asset_type = asset_info.get("type")
                            orm_id = asset_info.get("orm_id")
                            name_in_protocol = asset_info.get("name_in_protocol", "UnknownAsset")

                            if asset_type == "device":
                                self.asset_manager.release_device(device_orm_id=orm_id) # type: ignore
                            elif asset_type == "labware":
                                self.asset_manager.release_labware(
                                    labware_instance_orm_id=orm_id, # type: ignore
                                    final_status=LabwareInstanceStatusEnum.AVAILABLE_IN_STORAGE 
                                )
                            print(f"INFO: Released asset '{name_in_protocol}' (Type: {asset_type}, ORM ID: {orm_id}).")
                        except Exception as release_err: # pragma: no cover
                            print(f"ERROR: Failed to release asset '{asset_info.get('name_in_protocol', 'UnknownAsset')}' (ORM ID: {asset_info.get('orm_id')}): {release_err}")
                
                try: self.db_session.commit()
                except Exception as db_err: # pragma: no cover
                    print(f"CRITICAL: Failed to commit final Orchestrator updates to DB for run {run_guid}: {db_err}")
                    self.db_session.rollback()

        self.db_session.refresh(protocol_run_db_obj) 
        return protocol_run_db_obj 

```
