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
from typing import Callable, Optional, Any, Dict, Union, List, get_origin, get_args

from praxis.backend.protocol_core.definitions import (
    PROTOCOL_REGISTRY, PlrResource, PlrDeck, DeckInputType,
    PraxisState, PraxisRunContext, serialize_arguments
)
from praxis.backend.database_models import FunctionCallStatusEnum
# TODO: DEC-1: Ensure praxis.backend.services.protocol_data_service is importable.
from praxis.backend.services.protocol_data_service import log_function_call_start, log_function_call_end, update_protocol_run_status # Assuming this import works

# MODIFICATION: Import Pydantic models
# --- New Imports for Command Handling ---
from praxis.backend.utils.run_control import get_control_command, clear_control_command, ALLOWED_COMMANDS
from praxis.backend.database_models.protocol_definitions_orm import ProtocolRunStatusEnum
from praxis.backend.core.orchestrator import ProtocolCancelledError # Assuming this import works for now
# import time # Already imported for perf_counter, but good to note if it wasn't.
# json is already imported.
# --- End New Imports ---
from praxis.backend.protocol_core.protocol_definition_models import (
    FunctionProtocolDefinitionModel, ParameterMetadataModel, AssetRequirementModel, UIHint
)


DEFAULT_DECK_PARAM_NAME = "deck"
DEFAULT_STATE_PARAM_NAME = "state"
TOP_LEVEL_NAME_REGEX = r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$"

# Helper Functions
def is_pylabrobot_resource(obj_type: Any) -> bool:
    if obj_type is inspect.Parameter.empty: return False
    origin = get_origin(obj_type); args = get_args(obj_type)
    if origin is Union: return any(is_pylabrobot_resource(arg) for arg in args if arg is not type(None))
    try:
        if inspect.isclass(obj_type):
            return issubclass(obj_type, PlrResource)
    except TypeError: # pragma: no cover
        pass 
    return False

def get_actual_type_str_from_hint(type_hint: Any) -> str:
    if type_hint == inspect.Parameter.empty: return "Any"
    actual_type = type_hint
    origin = get_origin(type_hint)
    args = get_args(type_hint)
    if origin is Union and type(None) in args: 
        non_none_args = [arg for arg in args if arg is not type(None)]
        if len(non_none_args) == 1:
            actual_type = non_none_args[0]
        else: # pragma: no cover
            actual_type = non_none_args[0] if non_none_args else type_hint 
    
    if hasattr(actual_type, "__name__"):
        module = getattr(actual_type, "__module__", "")
        # Use fully qualified name for praxis types, otherwise just name
        if module.startswith("praxis.") or module == "builtins":
             return f"{module}.{actual_type.__name__}" if module and module != "builtins" else actual_type.__name__
        return actual_type.__name__ # For other types like PlrResource subclasses from pylabrobot
    return str(actual_type)

def serialize_type_hint_str(type_hint: Any) -> str:
    if type_hint == inspect.Parameter.empty: return "Any"
    return str(type_hint)
# --- End Helper Functions ---

def protocol_function(
    name: Optional[str] = None, 
    version: str = "0.1.0", description: Optional[str] = None,
    solo: bool = False, is_top_level: bool = False, preconfigure_deck: bool = False,
    deck_param_name: str = DEFAULT_DECK_PARAM_NAME, state_param_name: str = DEFAULT_STATE_PARAM_NAME,
    param_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    top_level_name_format: Optional[str] = TOP_LEVEL_NAME_REGEX
):
    actual_param_metadata = param_metadata or {}
    actual_tags = tags or []

    def decorator(func: Callable):
        resolved_name = name or func.__name__
        
        if not resolved_name: raise ValueError("Protocol function name cannot be empty (either provide 'name' argument or use a named function).")
        if is_top_level and top_level_name_format and not re.match(top_level_name_format, resolved_name):
            raise ValueError(f"Top-level protocol name '{resolved_name}' does not match format: {top_level_name_format}")

        protocol_unique_key = f"{resolved_name}_v{version}"
        
        sig = inspect.signature(func)
        parameters_list: List[ParameterMetadataModel] = []
        assets_list: List[AssetRequirementModel] = []
        
        found_deck_param = False
        # This dict will store essential info about the state param for the wrapper's direct use.
        found_state_param_details_for_wrapper: Optional[Dict[str, Any]] = None

        for param_name_sig, param_obj in sig.parameters.items():
            param_type_hint = param_obj.annotation
            is_optional_param = (get_origin(param_type_hint) is Union and type(None) in get_args(param_type_hint)) or \
                                (param_obj.default is not inspect.Parameter.empty)
            
            # Use get_actual_type_str_from_hint for a cleaner representation of the "core" type
            actual_type_cleaned_str = get_actual_type_str_from_hint(param_type_hint)
            
            param_meta_entry = actual_param_metadata.get(param_name_sig, {})
            p_description = param_meta_entry.get("description")
            p_constraints = param_meta_entry.get("constraints_json", {}) # Ensure this is a dict
            p_ui_hints_dict = param_meta_entry.get("ui_hints")
            p_ui_hints = UIHint(**p_ui_hints_dict) if isinstance(p_ui_hints_dict, dict) else None

            common_model_args = {
                "name": param_name_sig,
                "type_hint_str": serialize_type_hint_str(param_type_hint), # Full type hint string
                "actual_type_str": actual_type_cleaned_str, # Cleaned type string
                "optional": is_optional_param,
                "default_value_repr": repr(param_obj.default) if param_obj.default is not inspect.Parameter.empty else None,
                "description": p_description,
                "constraints_json": p_constraints if isinstance(p_constraints, dict) else {},
                "ui_hints": p_ui_hints,
            }

            if preconfigure_deck and param_name_sig == deck_param_name:
                parameters_list.append(ParameterMetadataModel(**common_model_args, is_deck_param=True))
                found_deck_param = True
                continue
            
            if param_name_sig == state_param_name:
                # Check actual_type_cleaned_str against known state type strings
                is_state_type_match = actual_type_cleaned_str == 'praxis.backend.protocol_core.definitions.PraxisState' or \
                                      actual_type_cleaned_str == 'PraxisState' # Might need fqn if not imported directly
                is_dict_type_match = actual_type_cleaned_str == 'dict'
                
                # Store details for wrapper's direct use
                found_state_param_details_for_wrapper = {
                    "name": param_name_sig, # Name of the state parameter
                    "expects_praxis_state": is_state_type_match, 
                    "expects_dict": is_dict_type_match
                }
                parameters_list.append(ParameterMetadataModel(**common_model_args)) # Add to Pydantic model list
                continue

            # Use get_actual_type_from_optional logic for is_pylabrobot_resource check
            # The get_actual_type_from_optional was effectively merged into get_actual_type_str_from_hint logic.
            # For is_pylabrobot_resource, we need the type object, not the string.
            type_for_plr_check = param_type_hint
            origin_check = get_origin(param_type_hint)
            args_check = get_args(param_type_hint)
            if origin_check is Union and type(None) in args_check:
                 non_none_args = [arg for arg in args_check if arg is not type(None)]
                 if len(non_none_args) == 1: type_for_plr_check = non_none_args[0]


            if is_pylabrobot_resource(type_for_plr_check):
                assets_list.append(AssetRequirementModel(**common_model_args))
            else:
                parameters_list.append(ParameterMetadataModel(**common_model_args))

        if preconfigure_deck and not found_deck_param: 
            raise TypeError(f"Protocol '{resolved_name}' (preconfigure_deck=True) missing '{deck_param_name}' param.")
        if is_top_level and not found_state_param_details_for_wrapper: 
            raise TypeError(f"Top-level protocol '{resolved_name}' must define a '{state_param_name}' parameter.")

        protocol_definition = FunctionProtocolDefinitionModel(
            name=resolved_name,
            version=version,
            description=(description or inspect.getdoc(func) or "No description provided."),
            source_file_path=inspect.getfile(func), 
            module_name=func.__module__,
            function_name=func.__name__,
            is_top_level=is_top_level,
            solo_execution=solo,
            preconfigure_deck=preconfigure_deck,
            deck_param_name=deck_param_name if preconfigure_deck else None,
            state_param_name=state_param_name,
            category=category,
            tags=actual_tags,
            parameters=parameters_list,
            assets=assets_list,
        )
        
        func._protocol_definition = protocol_definition

        legacy_protocol_metadata = {
            **protocol_definition.model_dump(exclude_none=True), # Pydantic v2, or .dict(exclude_none=True) for v1
            "protocol_unique_key": protocol_unique_key,
            "function_ref": func,
            "callable_wrapper": None, 
            "db_id": None, # Populated by DiscoveryService
            # Crucially, provide found_state_param_details for the existing wrapper logic
            "found_state_param_details": found_state_param_details_for_wrapper,
            "pydantic_definition": protocol_definition # Store the model itself too
        }
        PROTOCOL_REGISTRY[protocol_unique_key] = legacy_protocol_metadata

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # This wrapper part remains largely unchanged for this step.
            # It uses legacy_protocol_metadata from PROTOCOL_REGISTRY.
            current_meta = PROTOCOL_REGISTRY.get(protocol_unique_key)
            if not current_meta: # Should not happen
                raise RuntimeError(f"Protocol metadata not found for {protocol_unique_key} in PROTOCOL_REGISTRY.")

            praxis_run_context: Optional[PraxisRunContext] = kwargs.pop('__praxis_run_context__', None)
            this_function_def_db_id = current_meta.get("db_id")
            _found_state_param_details_wrapper = current_meta.get("found_state_param_details")


            if not isinstance(praxis_run_context, PraxisRunContext):
                print(f"WARNING: Protocol '{current_meta['name']}' v{current_meta['version']}' called outside orchestrated context. Logging to console.")
                praxis_run_context = PraxisRunContext(
                    protocol_run_db_id=0, run_guid="direct_call_" + str(uuid.uuid4())[:8],
                    canonical_state=PraxisState() if _found_state_param_details_wrapper else None, # type: ignore
                    current_db_session=None, current_call_log_db_id=None
                )

            processed_args = list(args)
            processed_kwargs = dict(kwargs)

            if _found_state_param_details_wrapper:
                state_arg_name_in_sig = _found_state_param_details_wrapper["name"]
                if state_arg_name_in_sig in processed_kwargs and praxis_run_context.protocol_run_db_id != 0:
                    del processed_kwargs[state_arg_name_in_sig] 

                if _found_state_param_details_wrapper["expects_praxis_state"]:
                    processed_kwargs[state_arg_name_in_sig] = praxis_run_context.canonical_state
                elif _found_state_param_details_wrapper["expects_dict"]:
                    if state_arg_name_in_sig not in processed_kwargs:
                         processed_kwargs[state_arg_name_in_sig] = praxis_run_context.canonical_state.data.copy() if praxis_run_context.canonical_state else {}
            
            current_call_log_db_id_for_this_func: Optional[int] = None
            parent_log_id_for_this_call = praxis_run_context.current_call_log_db_id

            if praxis_run_context.current_db_session and this_function_def_db_id is not None:
                try:
                    sequence_val = praxis_run_context.get_and_increment_sequence_val()
                    # TODO: DEC-4: Ensure serialize_arguments handles Pydantic models in kwargs if they appear
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
                except Exception as log_e: # pragma: no cover
                    print(f"ERROR: Failed to log_function_call_start for '{current_meta['name']}': {log_e}")
            else:
                print(f"[ConsoleLog] START Call: {current_meta['name']} v{current_meta['version']} (DefID: {this_function_def_db_id}, Run: {praxis_run_context.run_guid}, ParentLog: {parent_log_id_for_this_call}) Args: Shortened for brevity")

            context_for_user_code = praxis_run_context.create_context_for_nested_call(
                new_parent_call_log_db_id=current_call_log_db_id_for_this_func
            )
            
            result = None; error = None; status = FunctionCallStatusEnum.SUCCESS
            start_time = time.perf_counter()

            # --- MODIFICATION: Insert Command Handling Logic Here ---
            run_guid = praxis_run_context.run_guid
            current_protocol_run_db_id = praxis_run_context.protocol_run_db_id
            current_db_session = praxis_run_context.current_db_session

            # Initial Command Check Loop (Handle stacked commands before proceeding to user code):
            while True: # Loop to handle commands if multiple are sent or if a PAUSE transitions to CANCEL
                command = get_control_command(run_guid)
                if not command:
                    break # No command, proceed to execute the function

                if command not in ALLOWED_COMMANDS:
                    print(f"Warning: Invalid control command '{command}' received for run {run_guid}. Clearing.")
                    clear_control_command(run_guid)
                    continue # Check for another command

                # --- PAUSE Command ---
                if command == "PAUSE":
                    clear_control_command(run_guid)
                    print(f"INFO: Protocol run {run_guid} step PAUSING due to command.")
                    if current_db_session and current_protocol_run_db_id:
                        update_protocol_run_status(current_db_session, current_protocol_run_db_id, ProtocolRunStatusEnum.PAUSING)
                        current_db_session.commit() # Commit status change
                        update_protocol_run_status(current_db_session, current_protocol_run_db_id, ProtocolRunStatusEnum.PAUSED)
                        current_db_session.commit() # Commit status change

                    # Pause loop
                    pause_loop_command_after_resume = None
                    while True:
                        # print(f"DEBUG: Run {run_guid} is PAUSED. Waiting for RESUME or CANCEL.") # Optional debug log
                        time.sleep(1) # Check every second (or make configurable)
                        pause_loop_command = get_control_command(run_guid)
                        pause_loop_command_after_resume = pause_loop_command # Store for outer loop check

                        if pause_loop_command == "RESUME":
                            clear_control_command(run_guid)
                            print(f"INFO: Protocol run {run_guid} step RESUMING.")
                            if current_db_session and current_protocol_run_db_id:
                                update_protocol_run_status(current_db_session, current_protocol_run_db_id, ProtocolRunStatusEnum.RESUMING)
                                current_db_session.commit() # Commit status change
                                update_protocol_run_status(current_db_session, current_protocol_run_db_id, ProtocolRunStatusEnum.RUNNING)
                                current_db_session.commit() # Commit status change
                            break # Exit pause loop to continue execution
                        elif pause_loop_command == "CANCEL":
                            clear_control_command(run_guid)
                            print(f"INFO: Protocol run {run_guid} step CANCELLING during pause.")
                            if current_db_session and current_protocol_run_db_id:
                                update_protocol_run_status(current_db_session, current_protocol_run_db_id, ProtocolRunStatusEnum.CANCELING)
                                current_db_session.commit() # Commit status change
                                update_protocol_run_status(current_db_session, current_protocol_run_db_id, ProtocolRunStatusEnum.CANCELLED, output_data_json=json.dumps({"status": f"Cancelled by user during protocol step execution (from PAUSED state)."}))
                                current_db_session.commit() # Commit status change
                            raise ProtocolCancelledError(f"Protocol run {run_guid} cancelled by user during protocol step execution (from PAUSED state).")
                        elif pause_loop_command and pause_loop_command not in ["RESUME", "CANCEL"]:
                            print(f"Warning: Invalid command '{pause_loop_command}' received while PAUSED for run {run_guid}. Clearing and ignoring.")
                            clear_control_command(run_guid)
                    
                    if pause_loop_command_after_resume == "RESUME": # If resumed, break the outer command check loop too
                        break 
                    # If loop exited due to cancel, exception is already raised.

                # --- CANCEL Command (if not already handled in PAUSE) ---
                elif command == "CANCEL":
                    clear_control_command(run_guid)
                    print(f"INFO: Protocol run {run_guid} step CANCELLING due to command.")
                    if current_db_session and current_protocol_run_db_id:
                        update_protocol_run_status(current_db_session, current_protocol_run_db_id, ProtocolRunStatusEnum.CANCELING)
                        current_db_session.commit() # Commit status change
                        update_protocol_run_status(current_db_session, current_protocol_run_db_id, ProtocolRunStatusEnum.CANCELLED, output_data_json=json.dumps({"status": f"Cancelled by user during protocol step execution."}))
                        current_db_session.commit() # Commit status change
                    raise ProtocolCancelledError(f"Protocol run {run_guid} cancelled by user during protocol step execution.")
            # --- END MODIFICATION ---

            try:
                processed_kwargs_for_call = processed_kwargs.copy()
                
                # Logic for passing context to user function if it expects it
                sig_check = inspect.signature(func) # Re-inspect original func
                if '__praxis_run_context__' in sig_check.parameters:
                     processed_kwargs_for_call['__praxis_run_context__'] = context_for_user_code
                # Check if state_param_name is typed as PraxisRunContext
                elif _found_state_param_details_wrapper and \
                     _found_state_param_details_wrapper['name'] == state_param_name and \
                     sig_check.parameters[state_param_name].annotation == PraxisRunContext:
                    processed_kwargs_for_call[state_param_name] = context_for_user_code
                
                # If __praxis_run_context__ was added to processed_kwargs_for_call but func doesn't expect it by name or **kwargs
                if '__praxis_run_context__' in processed_kwargs_for_call and \
                   '__praxis_run_context__' not in func.__code__.co_varnames and \
                   not any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig_check.parameters.values()):
                    del processed_kwargs_for_call['__praxis_run_context__']

                result = func(*processed_args, **processed_kwargs_for_call)
            except Exception as e: # pragma: no cover
                error = e; status = FunctionCallStatusEnum.ERROR
                print(f"ERROR in '{current_meta['name']}' v{current_meta['version']}' (Run: {praxis_run_context.run_guid}): {e}") # type: ignore
                # print(traceback.format_exc()) # For more detailed debugging if needed
            finally:
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000
                if praxis_run_context.current_db_session and current_call_log_db_id_for_this_func is not None:
                    try:
                        serialized_result = None
                        if error is None:
                            # Import BaseModel directly if it's not already in the global scope of this file
                            # from pydantic import BaseModel # Not strictly needed if FunctionProtocolDefinitionModel etc. bring it in
                            # Check if FunctionProtocolDefinitionModel itself is a BaseModel subclass (it is)
                            # So, we can use it to check for general Pydantic models.
                            # However, for robustness, ensure BaseModel is accessible or import it.
                            # For now, assume it's accessible via the other pydantic imports.
                            # A more direct check: from pydantic import BaseModel as PydanticBaseModel

                            if any(isinstance(result, p_model) for p_model in [FunctionProtocolDefinitionModel, ParameterMetadataModel, AssetRequirementModel, UIHint]):
                                # This checks against specific known models.
                                # For a generic check, `isinstance(result, pydantic.BaseModel)` is better.
                                # Assuming BaseModel is available via other imports:
                                from pydantic import BaseModel as PydanticBaseModel # Make it explicit for this check
                                if isinstance(result, PydanticBaseModel):
                                    try:
                                        serialized_result = result.json(exclude_none=True) # Pydantic v1
                                    except AttributeError: 
                                        try:
                                            serialized_result = result.model_dump_json(exclude_none=True) # Pydantic v2
                                        except AttributeError: 
                                            serialized_result = json.dumps(result, default=str)
                                elif isinstance(result, (PlrResource, PlrDeck)): # PLR objects
                                    serialized_result = json.dumps(repr(result)) # Store repr as a JSON string
                                else: # Default for other types
                                    serialized_result = json.dumps(result, default=str)
                            elif isinstance(result, (PlrResource, PlrDeck)): # PLR objects
                                serialized_result = json.dumps(repr(result)) # Store repr as a JSON string
                            else: # Default for other types
                                serialized_result = json.dumps(result, default=str)
                        
                        log_function_call_end(
                            db=praxis_run_context.current_db_session,
                            function_call_log_id=current_call_log_db_id_for_this_func,
                            status=status,
                            return_value_json=serialized_result,
                            error_message=str(error) if error else None,
                            error_traceback=traceback.format_exc() if error else None,
                            duration_ms=duration_ms
                        )
                    except Exception as log_e: # pragma: no cover
                        print(f"ERROR: Failed to log_function_call_end for '{current_meta['name']}': {log_e}")
                else:
                    print(f"[ConsoleLog] END Call: {current_meta['name']} v{current_meta['version']} (LogID: {current_call_log_db_id_for_this_func}, Run: {praxis_run_context.run_guid}). Status: {status.name}. Duration: {duration_ms:.2f}ms")
            if error: # pragma: no cover
                raise error
            return result

        wrapper._protocol_definition = func._protocol_definition # type: ignore
        current_meta_in_registry = PROTOCOL_REGISTRY[protocol_unique_key]
        current_meta_in_registry["callable_wrapper"] = wrapper
        
        return wrapper
    return decorator

