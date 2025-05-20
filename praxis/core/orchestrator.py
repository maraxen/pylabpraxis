# pylint: disable=too-many-arguments,too-many-locals,broad-except,fixme,unused-argument,too-many-statements,too-many-branches
"""
praxis/core/orchestrator.py

The Orchestrator is responsible for managing the lifecycle of protocol runs.
It fetches protocol definitions, prepares the execution environment (including state),
invokes the protocol functions, and oversees logging.

Version 4: Emphasizes db_id alignment in decorator_metadata for logging.
"""
import importlib
import os
import sys
import uuid
import json
import datetime
import traceback
from typing import Dict, Any, Optional, Callable, Tuple, List
import contextlib

from sqlalchemy.orm import Session as DbSession

from praxis.utils.state import State as PraxisState
from praxis.protocol_core.definitions import (
    PraxisRunContext, PlrDeck, DeckInputType, PlrResource, PROTOCOL_REGISTRY
)
from praxis.database_models.protocol_definitions_orm import (
    FunctionProtocolDefinitionOrm,
    ProtocolRunOrm,
    ProtocolRunStatusEnum,
    ProtocolSourceRepositoryOrm,
    FileSystemProtocolSourceOrm,
)
# Import the data service functions
# TODO: ORCH-0: Ensure praxis.db_services.protocol_data_service is fully implemented and importable.
try:
    from praxis.db_services.protocol_data_service import (
        create_protocol_run,
        update_protocol_run_status,
        get_protocol_definition_details # Using the service function now
    )
except ImportError:
    print("WARNING: ORCH-0: Could not import from praxis.db_services.protocol_data_service. Orchestrator DB operations will be placeholder/limited.")
    # Placeholder functions
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


# TODO: ORCH-1: Integrate with actual AssetManager and Workcell
# from praxis.core.asset_manager import AssetManager
# from praxis.core.workcell import Workcell


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


class Orchestrator:
    def __init__(self, db_session: DbSession, workcell_config: Optional[Dict[str, Any]] = None):
        self.db_session = db_session
        self.workcell_config = workcell_config or {}
        # TODO: ORCH-1: Initialize actual AssetManager

    def _get_protocol_definition_orm_from_db(
        self,
        protocol_name: str,
        version: Optional[str] = None,
        commit_hash: Optional[str] = None,
        source_name: Optional[str] = None
    ) -> Optional[FunctionProtocolDefinitionOrm]:
        """
        Fetches a specific protocol definition ORM object from the database
        using the protocol_data_service.
        """
        # TODO: ORCH-3: This call might need more sophisticated logic for 'latest from branch' etc.
        #              The data service's get_protocol_definition_details handles basic cases.
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
        """
        Ensures the protocol's Python code is accessible, imports the function,
        and returns the callable wrapper along with its decorator metadata.
        Crucially, it ensures the decorator_metadata['db_id'] is aligned with protocol_def_orm.id.
        """
        module_path_to_add_for_sys_path: Optional[str] = None
        if protocol_def_orm.source_repository_id and protocol_def_orm.source_repository:
            repo = protocol_def_orm.source_repository
            checkout_path = repo.local_checkout_path
            if not checkout_path or not os.path.isdir(checkout_path):
                raise ValueError(f"Local checkout path '{checkout_path}' for repo '{repo.name}' invalid.")
            # TODO: ORCH-4: Implement robust Git operations (clone, fetch, checkout commit_hash).
            print(f"INFO: ORCH-4 TODO: Ensure Git repo '{repo.name}' at '{checkout_path}' is at commit '{protocol_def_orm.commit_hash}'.")
            module_path_to_add_for_sys_path = checkout_path
        elif protocol_def_orm.file_system_source_id and protocol_def_orm.file_system_source:
            fs_source = protocol_def_orm.file_system_source
            if not os.path.isdir(fs_source.base_path):
                 raise ValueError(f"Base path '{fs_source.base_path}' for FS source '{fs_source.name}' invalid.")
            module_path_to_add_for_sys_path = fs_source.base_path
        else:
            print(f"WARNING: Protocol '{protocol_def_orm.name}' v{protocol_def_orm.version} has no linked source. Direct import attempt.")

        with temporary_sys_path(module_path_to_add_for_sys_path):
            module = importlib.import_module(protocol_def_orm.module_name)
            module = importlib.reload(module) # Ensure freshness

        func_wrapper = getattr(module, protocol_def_orm.function_name)
        if not hasattr(func_wrapper, 'protocol_metadata'):
            raise AttributeError(f"Function '{protocol_def_orm.function_name}' in '{protocol_def_orm.module_name}' not decorated.")

        decorator_metadata: Dict[str, Any] = func_wrapper.protocol_metadata # type: ignore

        # Align decorator_metadata['db_id'] with the authoritative ID from the database record.
        # This is vital for the decorator wrapper to log against the correct definition ID.
        if decorator_metadata.get("db_id") != protocol_def_orm.id:
            print(f"INFO: Aligning metadata db_id for {protocol_def_orm.name} v{protocol_def_orm.version}. "
                  f"Decorator metadata had: {decorator_metadata.get('db_id')}, DB ORM has: {protocol_def_orm.id}.")
            decorator_metadata["db_id"] = protocol_def_orm.id

            # Optionally, update the global PROTOCOL_REGISTRY if this function was found there.
            # This helps if other parts of the system might access the global registry directly
            # after the Orchestrator has loaded and potentially "corrected" the db_id.
            registry_key = decorator_metadata.get("protocol_unique_key")
            if registry_key and registry_key in PROTOCOL_REGISTRY:
                PROTOCOL_REGISTRY[registry_key]["db_id"] = protocol_def_orm.id

        return func_wrapper, decorator_metadata

    def _prepare_arguments(
        self,
        protocol_def_orm: FunctionProtocolDefinitionOrm,
        decorator_metadata: Dict[str, Any],
        user_input_params: Dict[str, Any],
        canonical_run_state: PraxisState,
    ) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        # (Logic remains the same as Orchestrator v3 - praxis_core_orchestrator_py_v3)
        # Condensed for brevity in this update, but full logic should be retained.
        final_args: Dict[str, Any] = {}
        state_dict_to_pass: Optional[Dict[str, Any]] = None
        defined_params_from_meta = decorator_metadata.get("parameters", {})

        for param_name_in_sig, param_meta_from_decorator in defined_params_from_meta.items():
            if param_meta_from_decorator.get("is_deck_param"): continue
            is_state_param_match = (param_name_in_sig == decorator_metadata.get("state_param_name") and
                                    decorator_metadata.get("found_state_param_details"))
            if is_state_param_match:
                state_details = decorator_metadata["found_state_param_details"]
                if state_details.get("expects_praxis_state"): final_args[param_name_in_sig] = canonical_run_state
                elif state_details.get("expects_dict"):
                    state_dict_to_pass = canonical_run_state.data.copy(); final_args[param_name_in_sig] = state_dict_to_pass
                else: final_args[param_name_in_sig] = canonical_run_state
                continue
            if param_name_in_sig in user_input_params:
                # TODO: ORCH-5: Validation; ORCH-6: Type casting
                final_args[param_name_in_sig] = user_input_params[param_name_in_sig]
            elif not param_meta_from_decorator.get("optional"):
                raise ValueError(f"Mandatory param '{param_name_in_sig}' missing for '{protocol_def_orm.name}'.")

        defined_assets_from_meta = decorator_metadata.get("assets", {})
        for asset_name_in_sig, asset_meta_from_decorator in defined_assets_from_meta.items():
            # TODO: ORCH-1: Asset Resolution
            print(f"INFO: ORCH-1 TODO: Acquiring asset '{asset_name_in_sig}' type '{asset_meta_from_decorator['actual_type_str']}'.")
            final_args[asset_name_in_sig] = f"DUMMY_ASSET_{asset_name_in_sig}" # Placeholder

        if protocol_def_orm.preconfigure_deck and protocol_def_orm.deck_param_name:
            # TODO: ORCH-7: Deck loading
            deck_input = user_input_params.get(protocol_def_orm.deck_param_name)
            if isinstance(deck_input, str): final_args[protocol_def_orm.deck_param_name] = PlrDeck(name=deck_input) # Placeholder
            elif isinstance(deck_input, PlrDeck): final_args[protocol_def_orm.deck_param_name] = deck_input
        return final_args, state_dict_to_pass


    def execute_protocol(
        self,
        protocol_name: str, protocol_version: Optional[str] = None,
        commit_hash: Optional[str] = None, source_name: Optional[str] = None,
        user_input_params: Optional[Dict[str, Any]] = None,
        initial_state_data: Optional[Dict[str, Any]] = None,
        # created_by_user_id: Optional[int] = None # TODO: ORCH-8
    ) -> ProtocolRunOrm:
        user_input_params = user_input_params or {}
        initial_state_data = initial_state_data or {}
        run_guid = str(uuid.uuid4())
        utc_now = datetime.datetime.now(datetime.timezone.utc)

        protocol_def_orm = self._get_protocol_definition_orm_from_db( # Using new internal method name
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
            # Ensure error_run_db_obj has an ID before updating
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
        # Ensure ID is available for context
        self.db_session.flush()
        self.db_session.refresh(protocol_run_db_obj)


        canonical_run_state = PraxisState(data=initial_state_data.copy())
        # Initialize PraxisRunContext for the top-level call
        run_context = PraxisRunContext(
            protocol_run_db_id=protocol_run_db_obj.id, # type: ignore
            run_guid=run_guid,
            canonical_state=canonical_run_state,
            current_db_session=self.db_session,
            current_call_log_db_id=None # Top-level call has no parent function call log
            # _call_sequence_next_val defaults to 1 in PraxisRunContext
        )

        prepared_args: Dict[str, Any] = {}
        protocol_wrapper_func: Optional[Callable] = None
        decorator_metadata: Optional[Dict[str, Any]] = None
        state_dict_passed_to_top_level: Optional[Dict[str, Any]] = None

        try:
            protocol_wrapper_func, decorator_metadata = self._prepare_protocol_code(protocol_def_orm)

            # The decorator_metadata["db_id"] is now aligned with protocol_def_orm.id by _prepare_protocol_code.
            # This is used by the top-level wrapper (protocol_wrapper_func) to log itself.

            prepared_args, state_dict_passed_to_top_level = self._prepare_arguments(
                protocol_def_orm, decorator_metadata, user_input_params, canonical_run_state
            )

            update_protocol_run_status(self.db_session, protocol_run_db_obj.id, ProtocolRunStatusEnum.RUNNING) # type: ignore

            # Pass the initial run_context. The decorator wrapper will use it.
            # The decorator wrapper is responsible for creating and passing NEW contexts to nested calls.
            result = protocol_wrapper_func(**prepared_args, __praxis_run_context__=run_context)

            update_protocol_run_status(
                self.db_session, protocol_run_db_obj.id, ProtocolRunStatusEnum.COMPLETED, # type: ignore
                output_data_json=json.dumps(result, default=str)
            )

        except Exception as e:
            print(f"ERROR during protocol execution for run {run_guid}: {e}")
            error_info = {"error_type": type(e).__name__, "error_message": str(e), "traceback": traceback.format_exc()}
            update_protocol_run_status(
                self.db_session, protocol_run_db_obj.id, ProtocolRunStatusEnum.FAILED, # type: ignore
                output_data_json=json.dumps(error_info)
            )
            # TODO: ORCH-11: Consider re-raising or specific exception types
        finally:
            # Fetch the run again to get the most up-to-date status and avoid detached instance errors
            final_protocol_run_db_obj = self.db_session.query(ProtocolRunOrm).get(protocol_run_db_obj.id) # type: ignore
            if final_protocol_run_db_obj:
                if state_dict_passed_to_top_level is not None and protocol_def_orm.is_top_level:
                    print(f"INFO: Merging back state from dict for run {run_guid}.")
                    canonical_run_state.update_from_dict(state_dict_passed_to_top_level)

                final_protocol_run_db_obj.final_state_json = json.dumps(canonical_run_state.data, default=str)
                if not final_protocol_run_db_obj.end_time:
                    final_protocol_run_db_obj.end_time = datetime.datetime.now(datetime.timezone.utc)
                if final_protocol_run_db_obj.start_time and final_protocol_run_db_obj.end_time and \
                   final_protocol_run_db_obj.duration_ms is None :
                    duration = final_protocol_run_db_obj.end_time - final_protocol_run_db_obj.start_time
                    final_protocol_run_db_obj.duration_ms = int(duration.total_seconds() * 1000)
                # TODO: ORCH-1: Release acquired assets
                try: self.db_session.commit()
                except Exception as db_err:
                    print(f"CRITICAL: Failed to commit final Orchestrator updates to DB for run {run_guid}: {db_err}")
                    self.db_session.rollback()

        self.db_session.refresh(protocol_run_db_obj) # type: ignore
        return protocol_run_db_obj # type: ignore

# TODO: ORCH-13 to ORCH-15 (Query methods, Source Management, Async execution)

