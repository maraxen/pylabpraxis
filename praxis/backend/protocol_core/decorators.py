# pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements,fixme
"""
praxis/protocol_core/decorators.py

Decorator for defining PylabPraxis protocol functions.
Version 4: Refined PraxisRunContext usage and DB logging for hierarchical calls.
"""
import inspect
import functools
import re
import time
import uuid
import json
import traceback
from typing import Callable, Optional, Any, Dict, Union

from praxis.backend.protocol_core.definitions import (
    PROTOCOL_REGISTRY, PlrResource, PlrDeck, DeckInputType,
    PraxisState, PraxisRunContext, serialize_arguments
)
from praxis.backend.database_models import FunctionCallStatusEnum
# TODO: DEC-1: Ensure praxis.backend.services.protocol_data_service is importable.
from praxis.backend.services.protocol_data_service import log_function_call_start, log_function_call_end

DEFAULT_DECK_PARAM_NAME = "deck"
DEFAULT_STATE_PARAM_NAME = "state"
TOP_LEVEL_NAME_REGEX = r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$"

# Helper Functions (assumed to be defined or imported, same as v3 of this file)
# TODO: DEC-2: Define or import actually usable versions of these helper functions
def is_pylabrobot_resource(obj_type: Any) -> bool: # Simplified for brevity
    if obj_type is inspect.Parameter.empty: return False
    origin = get_origin(obj_type); args = get_args(obj_type) # TODO: define get_origin and get_args or import actual methods
    if origin is Union: return any(is_pylabrobot_resource(arg) for arg in args if arg is not type(None))
    return inspect.isclass(obj_type) and issubclass(obj_type, PlrResource)
def get_actual_type_from_optional(optional_type: Any) -> Any: # Simplified
    origin = get_origin(optional_type); args = get_args(optional_type)
    if origin is Union: non_none_args = [arg for arg in args if arg is not type(None)]; return non_none_args[0] if len(non_none_args) == 1 else optional_type
    return optional_type
def serialize_type_hint(type_hint: Any) -> str: # Simplified
    if type_hint == inspect.Parameter.empty: return "Any"
    if hasattr(type_hint, "__name__"): module = getattr(type_hint, "__module__", ""); return f"{module}.{type_hint.__name__}" if module and module != "builtins" else type_hint.__name__
    return str(type_hint)
# --- End Helper Functions ---

def protocol_function(
    name: str, version: str = "0.1.0", description: Optional[str] = None,
    solo: bool = False, is_top_level: bool = False, preconfigure_deck: bool = False,
    deck_param_name: str = DEFAULT_DECK_PARAM_NAME, state_param_name: str = DEFAULT_STATE_PARAM_NAME,
    param_constraints: Optional[dict[str, dict[str, Any]]] = None,
    asset_constraints: Optional[dict[str, dict[str, Any]]] = None,
    top_level_name_format: Optional[str] = TOP_LEVEL_NAME_REGEX
):
    if not name: raise ValueError("The 'name' argument for @protocol_function is mandatory.")
    if top_level_name_format and not re.match(top_level_name_format, name):
        raise ValueError(f"Protocol name '{name}' does not match format: {top_level_name_format}")

    def decorator(func: Callable):
        protocol_unique_key = f"{name}_v{version}"
        # --- Metadata Extraction (same as v3 of this file) ---
        sig = inspect.signature(func); parameters_info: Dict[str, Dict[str, Any]] = {}; assets_info: Dict[str, Dict[str, Any]] = {}
        found_deck_param = False; found_state_param_details: Optional[Dict[str, Any]] = None
        for param_name_sig, param_obj in sig.parameters.items():
            param_type_hint = param_obj.annotation; actual_param_type = get_actual_type_from_optional(param_type_hint)
            is_optional_param = (get_origin(param_type_hint) is Union and type(None) in get_args(param_type_hint)) or \
                                (param_obj.default is not inspect.Parameter.empty)
            param_info_base = {"name": param_name_sig, "type_hint_str": serialize_type_hint(param_type_hint),
                               "actual_type_str": serialize_type_hint(actual_param_type), "optional": is_optional_param,
                               "default_repr": repr(param_obj.default) if param_obj.default is not inspect.Parameter.empty else None,
                               "constraints": (param_constraints or {}).get(param_name_sig, {})}
            if preconfigure_deck and param_name_sig == deck_param_name:
                parameters_info[param_name_sig] = {**param_info_base, "is_deck_param": True}; found_deck_param = True; continue
            if param_name_sig == state_param_name:
                is_state_type = actual_param_type == PraxisState; is_dict_type = actual_param_type == dict
                found_state_param_details = {**param_info_base, "is_state_param": True, "expects_praxis_state": is_state_type, "expects_dict": is_dict_type}
                parameters_info[param_name_sig] = found_state_param_details; continue
            if is_pylabrobot_resource(actual_param_type): assets_info[param_name_sig] = {**param_info_base}
            else: parameters_info[param_name_sig] = {**param_info_base, "is_deck_param": False, "is_state_param": False}
        if preconfigure_deck and not found_deck_param: raise TypeError(f"Protocol '{name}' (preconfigure_deck=True) missing '{deck_param_name}' param.")
        if is_top_level and not found_state_param_details: raise TypeError(f"Top-level protocol '{name}' must define a '{state_param_name}' parameter.")
        # --- End Metadata Extraction ---

        protocol_metadata = {
            "name": name, "version": version, "protocol_unique_key": protocol_unique_key,
            "description": description or inspect.getdoc(func) or "No description provided.",
            "parameters": parameters_info, "assets": assets_info, "solo": solo,
            "is_top_level": is_top_level, "preconfigure_deck": preconfigure_deck,
            "deck_param_name": deck_param_name if preconfigure_deck else None,
            "state_param_name": state_param_name, "found_state_param_details": found_state_param_details,
            "source_file": inspect.getfile(func), "module": func.__module__,
            "function_name": func.__name__, "function_ref": func, "callable_wrapper": None,
            "db_id": None # Populated by DiscoveryService after DB upsert
        }
        PROTOCOL_REGISTRY[protocol_unique_key] = protocol_metadata

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            praxis_run_context: Optional[PraxisRunContext] = kwargs.pop('__praxis_run_context__', None)

            # This function's own static definition DB ID from its metadata
            # This should have been populated by the DiscoveryService.
            this_function_def_db_id = protocol_metadata.get("db_id")

            if not isinstance(praxis_run_context, PraxisRunContext):
                # TODO: DEC-3: Define behavior for direct calls. For now, console log and no DB interaction.
                print(f"WARNING: Protocol '{name}' v{version} called outside orchestrated context. Logging to console.")
                # Create a dummy context for the wrapper to proceed without DB logging
                praxis_run_context = PraxisRunContext(
                    protocol_run_db_id=0, run_guid="direct_call_" + str(uuid.uuid4())[:8],
                    canonical_state=PraxisState() if found_state_param_details else None, # type: ignore
                    current_db_session=None, current_call_log_db_id=None
                )
                # If db_id is not in metadata, this_function_def_db_id will be None, and DB logging is skipped.

            # --- Argument Preparation (State) ---
            processed_args = list(args)
            processed_kwargs = dict(kwargs)
            if found_state_param_details:
                state_arg_name_in_sig = found_state_param_details["name"]
                if state_arg_name_in_sig in processed_kwargs and praxis_run_context.protocol_run_db_id != 0:
                    del processed_kwargs[state_arg_name_in_sig] # Orchestrator provides state

                if found_state_param_details["expects_praxis_state"]:
                    processed_kwargs[state_arg_name_in_sig] = praxis_run_context.canonical_state
                elif found_state_param_details["expects_dict"]:
                    # Top-level dict state is handled by Orchestrator (copy + merge back).
                    # Nested calls expecting dict get a fresh copy to avoid side effects on shared canonical state.
                    # The Orchestrator passes the special dict for top-level. This wrapper handles nested.
                    # If this is a nested call, and it expects a dict, give it a copy.
                    # If this is the top-level call, Orchestrator has already placed the special dict in processed_kwargs.
                    if state_arg_name_in_sig not in processed_kwargs: # Not already set by Orchestrator for top-level dict
                         processed_kwargs[state_arg_name_in_sig] = praxis_run_context.canonical_state.data.copy() if praxis_run_context.canonical_state else {}

            # --- DB Logging: Start of Call ---
            current_call_log_db_id_for_this_func: Optional[int] = None
            parent_log_id_for_this_call = praxis_run_context.current_call_log_db_id # Parent is the currently active call log ID in context

            if praxis_run_context.current_db_session and this_function_def_db_id is not None:
                try:
                    sequence_val = praxis_run_context.get_and_increment_sequence_val()
                    serialized_input_args = serialize_arguments(tuple(processed_args), processed_kwargs)

                    call_log_entry_orm = log_function_call_start(
                        db=praxis_run_context.current_db_session,
                        protocol_run_orm_id=praxis_run_context.protocol_run_db_id,
                        function_definition_id=this_function_def_db_id,
                        sequence_in_run=sequence_val,
                        input_args_json=serialized_input_args,
                        parent_function_call_log_id=parent_log_id_for_this_call
                    )
                    current_call_log_db_id_for_this_func = call_log_entry_orm.id
                except Exception as log_e:
                    print(f"ERROR: Failed to log_function_call_start for '{name}': {log_e}")
            else:
                print(f"[ConsoleLog] START Call: {name} v{version} (DefID: {this_function_def_db_id}, Run: {praxis_run_context.run_guid}, ParentLog: {parent_log_id_for_this_call}) Args: Shortened for brevity")

            # --- Prepare Context for User Code & Any Nested Calls It Makes ---
            # The context passed to user code will have its `current_call_log_db_id`
            # set to the log ID of *this current function's execution*.
            context_for_user_code = praxis_run_context.create_context_for_nested_call(
                new_parent_call_log_db_id=current_call_log_db_id_for_this_func
            )

            # --- Actual Function Call ---
            result = None; error = None; status = FunctionCallStatusEnum.SUCCESS
            start_time = time.perf_counter()
            try:
                # Pass the new context for any nested calls made by `func`
                processed_kwargs_for_call = processed_kwargs.copy()
                processed_kwargs_for_call['__praxis_run_context__'] = context_for_user_code
                result = func(*processed_args, **processed_kwargs_for_call)
            except Exception as e:
                error = e; status = FunctionCallStatusEnum.ERROR
                print(f"ERROR in '{name}' v{version} (Run: {praxis_run_context.run_guid}): {e}")
            finally:
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000

                # --- DB Logging: End of Call ---
                if praxis_run_context.current_db_session and current_call_log_db_id_for_this_func is not None:
                    try:
                        # TODO: DEC-5: Robust serialization for result (using serialize_arguments for now as a placeholder concept)
                        serialized_result = json.dumps(result, default=str) if error is None else None # Basic
                        log_function_call_end(
                            db=praxis_run_context.current_db_session,
                            function_call_log_id=current_call_log_db_id_for_this_func,
                            status=status,
                            return_value_json=serialized_result,
                            error_message=str(error) if error else None,
                            error_traceback=traceback.format_exc() if error else None,
                            duration_ms=duration_ms # Pass duration to service
                        )
                    except Exception as log_e:
                        print(f"ERROR: Failed to log_function_call_end for '{name}': {log_e}")
                else:
                    print(f"[ConsoleLog] END Call: {name} v{version} (LogID: {current_call_log_db_id_for_this_func}, Run: {praxis_run_context.run_guid}). Status: {status.name}. Duration: {duration_ms:.2f}ms")

            if error:
                raise error # Re-raise after logging, for Orchestrator or calling wrapper to handle

            return result

        protocol_metadata["callable_wrapper"] = wrapper
        wrapper.protocol_metadata = protocol_metadata # type: ignore
        return wrapper
    return decorator

