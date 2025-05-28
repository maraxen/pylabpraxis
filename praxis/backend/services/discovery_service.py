# pylint: disable=too-few-public-methods,broad-except,fixme,unused-argument
"""
praxis/protocol_core/discovery_service.py

Service responsible for discovering protocol functions, transforming their
metadata into structured Pydantic models, and upserting them into a database
via the protocol_data_service. It also updates the in-memory PROTOCOL_REGISTRY
with the database ID of the discovered protocols.

Version 5: Added None check before accessing db_id on pydantic_definition in PROTOCOL_REGISTRY.
"""
import os
import importlib
import inspect
import sys
from typing import List, Dict, Any, Optional, Union, Set, Callable, Tuple, get_origin, get_args
import traceback

from sqlalchemy.orm import Session as DbSession

# Updated Pydantic model imports
from praxis.backend.protocol_core.protocol_definition_models import (
    FunctionProtocolDefinitionModel, ParameterMetadataModel, AssetRequirementModel, UIHint
)
# Global in-memory registry (populated by decorators, updated by this service)
from praxis.backend.protocol_core.definitions import PROTOCOL_REGISTRY

from praxis.backend.services.protocol_data_service import upsert_function_protocol_definition


# --- Helper Functions (copied from decorators.py modification plan) ---
def is_pylabrobot_resource(obj_type: Any) -> bool:
    if obj_type is inspect.Parameter.empty: return False
    origin = get_origin(obj_type); t_args = get_args(obj_type)
    if origin is Union: return any(is_pylabrobot_resource(arg) for arg in t_args if arg is not type(None))
    try:
        if inspect.isclass(obj_type):
            from praxis.backend.protocol_core.definitions import PlrResource
            return issubclass(obj_type, PlrResource)
    except TypeError: pass
    return False

def get_actual_type_str_from_hint(type_hint: Any) -> str:
    if type_hint == inspect.Parameter.empty: return "Any"
    actual_type = type_hint
    origin = get_origin(type_hint); t_args = get_args(type_hint)
    if origin is Union and type(None) in t_args:
        non_none_args = [arg for arg in t_args if arg is not type(None)]
        if len(non_none_args) == 1: actual_type = non_none_args[0]
        else: actual_type = non_none_args[0] if non_none_args else type_hint
    if hasattr(actual_type, "__name__"):
        module = getattr(actual_type, "__module__", "")
        # For praxis types, pylabrobot types, and builtins, include module for clarity if not builtin
        if module.startswith("praxis.") or module.startswith("pylabrobot.") or module == "builtins":
            return f"{module}.{actual_type.__name__}" if module and module != "builtins" else actual_type.__name__
        return actual_type.__name__ # For other types, just the name
    return str(actual_type)

def serialize_type_hint_str(type_hint: Any) -> str:
    if type_hint == inspect.Parameter.empty: return "Any"
    return str(type_hint)
# --- End Helper Functions ---


class ProtocolDiscoveryService:
    """
    Discovers protocol functions, prepares their definitions, upserts them to the DB,
    and updates the in-memory PROTOCOL_REGISTRY with their database IDs.
    """

    def __init__(self, db_session: Optional[DbSession] = None):
        self.db_session = db_session

    def _extract_protocol_definitions_from_paths(
        self,
        search_paths: Union[str, List[str]],
    ) -> List[Tuple[FunctionProtocolDefinitionModel, Optional[Callable]]]:
        if isinstance(search_paths, str): search_paths = [search_paths]

        extracted_definitions: List[Tuple[FunctionProtocolDefinitionModel, Optional[Callable]]] = []
        processed_func_ids: Set[int] = set()
        loaded_module_names: Set[str] = set()
        original_sys_path = list(sys.path)

        for path_item in search_paths:
            abs_path_item = os.path.abspath(path_item)
            if not os.path.isdir(abs_path_item):
                print(f"Warning: Search path '{abs_path_item}' is not a directory. Skipping.")
                continue

            potential_package_parent = os.path.dirname(abs_path_item)
            path_added_to_sys = False
            if potential_package_parent not in sys.path:
                sys.path.insert(0, potential_package_parent)
                path_added_to_sys = True

            for root, _, files in os.walk(abs_path_item):
                for file in files:
                    if file.endswith(".py") and not file.startswith("_"):
                        module_file_path = os.path.join(root, file)
                        rel_module_path = os.path.relpath(module_file_path, potential_package_parent)
                        module_import_name = os.path.splitext(rel_module_path)[0].replace(os.sep, '.')

                        try:
                            module = None
                            if module_import_name in loaded_module_names and module_import_name in sys.modules:
                                module = importlib.reload(sys.modules[module_import_name])
                            else:
                                module = importlib.import_module(module_import_name)
                            loaded_module_names.add(module_import_name)

                            for name, func_obj in inspect.getmembers(module, inspect.isfunction):
                                if func_obj.__module__ != module_import_name: continue
                                if id(func_obj) in processed_func_ids: continue
                                processed_func_ids.add(id(func_obj))

                                # Use getattr for safer access
                                protocol_def_attr = getattr(func_obj, '_protocol_definition', None)
                                if protocol_def_attr and isinstance(protocol_def_attr, FunctionProtocolDefinitionModel):
                                    extracted_definitions.append((protocol_def_attr, func_obj))
                                else:
                                    # Infer metadata for non-decorated functions
                                    sig = inspect.signature(func_obj)
                                    params_list: List[ParameterMetadataModel] = []
                                    assets_list: List[AssetRequirementModel] = []

                                    for param_name, param_obj_sig in sig.parameters.items():
                                        param_type_hint = param_obj_sig.annotation
                                        is_opt = (get_origin(param_type_hint) is Union and type(None) in get_args(param_type_hint)) or \
                                                 (param_obj_sig.default is not inspect.Parameter.empty)
                                        actual_type_str = get_actual_type_str_from_hint(param_type_hint)

                                        type_for_plr_check = param_type_hint
                                        origin_check, args_check = get_origin(param_type_hint), get_args(param_type_hint)
                                        if origin_check is Union and type(None) in args_check:
                                            non_none_args = [arg for arg in args_check if arg is not type(None)]
                                            if len(non_none_args) == 1: type_for_plr_check = non_none_args[0]

                                        common_args = {
                                            "name": param_name,
                                            "type_hint_str": serialize_type_hint_str(param_type_hint),
                                            "actual_type_str": actual_type_str,
                                            "optional": is_opt,
                                            "default_value_repr": repr(param_obj_sig.default) if param_obj_sig.default is not inspect.Parameter.empty else None,
                                        }
                                        if is_pylabrobot_resource(type_for_plr_check):
                                            assets_list.append(AssetRequirementModel(**common_args))
                                        else:
                                            params_list.append(ParameterMetadataModel(**common_args, is_deck_param=False))

                                    inferred_model = FunctionProtocolDefinitionModel(
                                        name=func_obj.__name__,
                                        version="0.0.0-inferred",
                                        description=inspect.getdoc(func_obj) or "Inferred from code.",
                                        source_file_path=inspect.getfile(func_obj),
                                        module_name=func_obj.__module__,
                                        function_name=func_obj.__name__,
                                        parameters=params_list,
                                        assets=assets_list,
                                        is_top_level=False,
                                    )
                                    extracted_definitions.append((inferred_model, func_obj))
                        except Exception as e:
                            print(f"Could not import/process module '{module_import_name}' from '{module_file_path}': {e}")
                            traceback.print_exc()

            if path_added_to_sys and potential_package_parent in sys.path:
                sys.path.remove(potential_package_parent)

        sys.path = original_sys_path
        return extracted_definitions

    def discover_and_upsert_protocols(
        self,
        search_paths: Union[str, List[str]],
        source_repository_id: Optional[int] = None,
        commit_hash: Optional[str] = None,
        file_system_source_id: Optional[int] = None
    ) -> List[Any]:
        if not self.db_session:
            print("ERROR: DB session not provided to ProtocolDiscoveryService. Cannot upsert definitions.")
            return []

        if not ((source_repository_id and commit_hash) or file_system_source_id):
            print("WARNING: DS-3: No source linkage provided for discovery. Protocols may not be correctly linked or upserted if service requires it.")

        print(f"Starting protocol discovery in paths: {search_paths}...")
        extracted_definitions = self._extract_protocol_definitions_from_paths(search_paths)

        if not extracted_definitions:
            print("No protocol definitions found from scan.")
            return []

        print(f"Found {len(extracted_definitions)} protocol functions. Upserting to DB...")
        upserted_definitions_orm: List[Any] = []

        for protocol_pydantic_model, func_ref in extracted_definitions:
            protocol_name_for_error = protocol_pydantic_model.name
            protocol_version_for_error = protocol_pydantic_model.version
            try:
                if source_repository_id and commit_hash:
                    protocol_pydantic_model.source_repository_name = str(source_repository_id)
                    protocol_pydantic_model.commit_hash = commit_hash
                elif file_system_source_id:
                     protocol_pydantic_model.file_system_source_name = str(file_system_source_id)

                def_orm = upsert_function_protocol_definition(
                    db=self.db_session,
                    protocol_pydantic=protocol_pydantic_model,
                    source_repository_id=source_repository_id,
                    commit_hash=commit_hash,
                    file_system_source_id=file_system_source_id
                )
                upserted_definitions_orm.append(def_orm)

                protocol_unique_key = f"{protocol_pydantic_model.name}_v{protocol_pydantic_model.version}"

                # Use getattr for safer access
                func_ref_protocol_def = getattr(func_ref, '_protocol_definition', None)
                if func_ref and func_ref_protocol_def is protocol_pydantic_model:
                    if hasattr(def_orm, 'id') and def_orm.id is not None:
                        setattr(func_ref_protocol_def, 'db_id', def_orm.id)

                if protocol_unique_key in PROTOCOL_REGISTRY:
                    if hasattr(def_orm, 'id') and def_orm.id is not None:
                        PROTOCOL_REGISTRY[protocol_unique_key]["db_id"] = def_orm.id
                        # Add a check for pydantic_definition existence and None before accessing db_id
                        pydantic_def_in_registry = PROTOCOL_REGISTRY[protocol_unique_key].get("pydantic_definition")
                        if pydantic_def_in_registry and isinstance(pydantic_def_in_registry, FunctionProtocolDefinitionModel):
                            setattr(pydantic_def_in_registry, 'db_id', def_orm.id)
                    else:
                        print(f"WARNING: Upserted ORM object for '{protocol_unique_key}' has no 'id'. Cannot update PROTOCOL_REGISTRY.")

            except Exception as e:
                print(f"ERROR: Failed to process or upsert protocol '{protocol_name_for_error} v{protocol_version_for_error}': {e}")
                traceback.print_exc()

        num_successful_upserts = len([d for d in upserted_definitions_orm if hasattr(d, 'id') and d.id is not None])
        print(f"Successfully upserted {num_successful_upserts} protocol definition(s) to DB.")
        return upserted_definitions_orm
