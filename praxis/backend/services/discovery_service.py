# pylint: disable=too-few-public-methods,broad-except,fixme,unused-argument
"""
praxis/protocol_core/discovery_service.py

Service responsible for discovering protocol functions, transforming their
metadata into structured Pydantic models, and upserting them into a database
via the protocol_data_service. It also updates the in-memory PROTOCOL_REGISTRY
with the database ID of the discovered protocols.

Version 3: Ensures robust db_id update to PROTOCOL_REGISTRY.
"""
import os
import importlib
import inspect
import sys
from typing import List, Dict, Any, Optional, Union, Set

from sqlalchemy.orm import Session as DbSession

# Pydantic models for structuring data before DB interaction
from praxis.protocol_core.protocol_definition_models import (
    FunctionProtocolDefinition as FunctionProtocolDefinitionPydantic,
    _convert_decorator_metadata_to_definition_v2 # Using the v2 converter
)
# Global in-memory registry (populated by decorators, updated by this service)
from praxis.protocol_core.definitions import PROTOCOL_REGISTRY
# Database service for actual DB operations
# TODO: DS-1: Ensure praxis.db_services.protocol_data_service is correctly imported and fully functional.
try:
    from praxis.db_services.protocol_data_service import upsert_function_protocol_definition
except ImportError:
    print("WARNING: DS-1: Could not import from praxis.db_services.protocol_data_service. DB operations will be placeholder/skipped by DiscoveryService.")
    def upsert_function_protocol_definition(db, protocol_pydantic, **kwargs): # type: ignore
        print(f"[DiscoveryService-PlaceholderDB] Skipping DB upsert for: {protocol_pydantic.name}")
        class DummyOrm: id = abs(hash(protocol_pydantic.name + protocol_pydantic.version)); parameters = []; assets = [] # type: ignore
        return DummyOrm()


class ProtocolDiscoveryService:
    """
    Discovers protocol functions, prepares their definitions, upserts them to the DB,
    and updates the in-memory PROTOCOL_REGISTRY with their database IDs.
    """

    def __init__(self, db_session: Optional[DbSession] = None):
        self.db_session = db_session
        # self._discovered_raw_metadata_list: List[Dict[str, Any]] = [] # Not strictly needed as member var

    def _scan_and_load_modules(
        self,
        search_paths: Union[str, List[str]],
    ) -> List[Dict[str, Any]]:
        """
        Scans Python files, imports them, and collects raw metadata from decorated functions.
        Decorator populates PROTOCOL_REGISTRY; this function ensures modules are loaded
        and can optionally re-collect metadata if PROTOCOL_REGISTRY is cleared per scan.
        """
        if isinstance(search_paths, str): search_paths = [search_paths]

        # Using a set to track unique metadata dicts based on the function object's ID
        # to handle reloads or multiple scan paths pointing to same modules.
        # The metadata dicts themselves are stored in PROTOCOL_REGISTRY by the decorator.
        # We are essentially ensuring all relevant modules are loaded and then iterating
        # through the populated PROTOCOL_REGISTRY.

        # Keep track of modules we've tried to import to avoid redundant reloads if not necessary,
        # though reloading ensures freshness if files changed.
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
                            if module_import_name in loaded_module_names and module_import_name in sys.modules:
                                # print(f"DEBUG: Reloading module: {module_import_name}")
                                module = importlib.reload(sys.modules[module_import_name])
                            else:
                                # print(f"DEBUG: Importing module: {module_import_name}")
                                module = importlib.import_module(module_import_name)
                            loaded_module_names.add(module_import_name)
                            # Decorators within 'module' should have populated PROTOCOL_REGISTRY
                        except Exception as e: # Catch ImportError and other potential issues
                            print(f"Could not import/reload module '{module_import_name}' from '{module_file_path}': {e}")

            if path_added_to_sys: # Restore sys.path
                if potential_package_parent in sys.path: sys.path.remove(potential_package_parent)
                else: sys.path = original_sys_path # Fallback

        # Return a list of metadata dicts from the now-populated PROTOCOL_REGISTRY
        # This ensures we only process what the decorators registered.
        return list(PROTOCOL_REGISTRY.values())


    def discover_and_upsert_protocols(
        self,
        search_paths: Union[str, List[str]],
        source_repository_id: Optional[int] = None,
        commit_hash: Optional[str] = None,
        file_system_source_id: Optional[int] = None
    ) -> List[Any]: # Returns list of ORM objects or Dummies
        """
        Scans for protocols, converts metadata, upserts to DB, and updates PROTOCOL_REGISTRY.
        """
        if not self.db_session:
            print("ERROR: DB session not provided to ProtocolDiscoveryService. Cannot upsert definitions.")
            return []

        # TODO: DS-3: Revisit source linking. If no source provided, how are unmanaged protocols handled?
        #             Current upsert in data_service requires a source.
        if not ((source_repository_id and commit_hash) or file_system_source_id):
            print("WARNING: DS-3: No source linkage provided for discovery. Protocols will not be upserted if service requires it.")
            # Depending on upsert_function_protocol_definition strictness, this might fail.
            # For now, we proceed, and upsert might raise error or handle it.

        print(f"Starting protocol discovery in paths: {search_paths}...")
        # _scan_and_load_modules ensures PROTOCOL_REGISTRY is populated by decorators.
        # We then iterate over a snapshot of its values.
        raw_metadata_list = self._scan_and_load_modules(search_paths)

        if not raw_metadata_list:
            print("No raw protocol metadata found from scan (PROTOCOL_REGISTRY might be empty or scan paths incorrect).")
            return []

        print(f"Found {len(raw_metadata_list)} raw protocol entries. Converting and upserting to DB...")

        upserted_definitions_orm: List[Any] = [] # List of ORM objects or Dummies

        for raw_meta in raw_metadata_list:
            # Ensure raw_meta is a dictionary, as expected by the converter
            if not isinstance(raw_meta, dict):
                print(f"WARNING: Skipping non-dict metadata entry: {type(raw_meta)}")
                continue

            protocol_name_for_error = raw_meta.get('name', 'UnknownProtocol')
            protocol_version_for_error = raw_meta.get('version', 'N/A')
            try:
                protocol_pydantic = _convert_decorator_metadata_to_definition_v2(raw_meta)

                def_orm = upsert_function_protocol_definition(
                    db=self.db_session,
                    protocol_pydantic=protocol_pydantic,
                    source_repository_id=source_repository_id,
                    commit_hash=commit_hash,
                    file_system_source_id=file_system_source_id
                )
                upserted_definitions_orm.append(def_orm)

                # CRUCIAL: Update the in-memory PROTOCOL_REGISTRY with the database ID
                protocol_unique_key_from_meta = raw_meta.get("protocol_unique_key")
                if protocol_unique_key_from_meta and protocol_unique_key_from_meta in PROTOCOL_REGISTRY:
                    # Ensure def_orm.id exists (it should if upsert was successful)
                    if hasattr(def_orm, 'id') and def_orm.id is not None:
                        PROTOCOL_REGISTRY[protocol_unique_key_from_meta]["db_id"] = def_orm.id
                        # print(f"DEBUG: Updated PROTOCOL_REGISTRY for '{protocol_unique_key_from_meta}' with db_id: {def_orm.id}")
                    else:
                        print(f"WARNING: Upserted ORM object for '{protocol_unique_key_from_meta}' has no 'id'. Cannot update PROTOCOL_REGISTRY.")
                else:
                    print(f"WARNING: Could not find '{protocol_unique_key_from_meta}' in PROTOCOL_REGISTRY to update db_id. Registry state: {list(PROTOCOL_REGISTRY.keys())}")

            except Exception as e:
                print(f"ERROR: Failed to process or upsert protocol '{protocol_name_for_error} v{protocol_version_for_error}': {e}")
                traceback.print_exc()


        num_successful_upserts = len([d for d in upserted_definitions_orm if hasattr(d, 'id') and d.id is not None])
        print(f"Successfully upserted {num_successful_upserts} protocol definition(s) to DB.")
        return upserted_definitions_orm


if __name__ == "__main__":
    # (Main test block remains largely the same as v2 of this file,
    #  ensure it calls discover_and_upsert_protocols and checks PROTOCOL_REGISTRY db_id)
    print("--- Protocol Discovery Service Integration Test (v3) ---")
    test_db_session = None # Placeholder for actual DB session
    if not test_db_session: print("WARNING: No DB session for test, DB operations will be placeholder/skipped.")

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    praxis_root_dir = os.path.dirname(os.path.dirname(current_script_dir))
    if praxis_root_dir not in sys.path:
        sys.path.insert(0, praxis_root_dir)
        print(f"INFO: Added '{praxis_root_dir}' to sys.path for test imports of 'praxis.xxx'.")

    temp_protocols_base_dir = os.path.join(current_script_dir, "temp_ds_protocols_v3")
    dummy_protocol_dir_main = os.path.join(temp_protocols_base_dir, "main_protos")
    os.makedirs(dummy_protocol_dir_main, exist_ok=True)
    with open(os.path.join(temp_protocols_base_dir, "__init__.py"), "w", encoding="utf-8") as f: f.write("# temp_ds_protocols_v3 package\n")
    with open(os.path.join(dummy_protocol_dir_main, "__init__.py"), "w", encoding="utf-8") as f: f.write("# main_protos subpackage\n")

    protocol_content_alpha = """
from praxis.protocol_core.decorators import protocol_function
from praxis.protocol_core.definitions import Pipette, Plate, PraxisState
from typing import Optional, Dict

@protocol_function(name="AlphaPrep", version="1.2", is_top_level=True, description="Alpha sample preparation.")
def alpha_preparation(state: PraxisState, main_pipette: Pipette, samples: int = 12):
    '''Alpha protocol v1.2 documentation.'''
    print(f"Running AlphaPrep v1.2 with {samples} samples. State: {state.data.get('run_count', 0)}")
    state.set("run_count", state.data.get("run_count", 0) + 1)
    return {"status": "alpha_v1.2_done", "samples_processed": samples}

@protocol_function(name="HelperDelta", version="0.7")
def helper_delta(plate_in: Plate, factor: float):
    print(f"Helper Delta processing {getattr(plate_in, 'name', plate_in)} with factor {factor}")
    return "delta_helper_finished"
"""
    with open(os.path.join(dummy_protocol_dir_main, "alpha_delta_set.py"), "w", encoding="utf-8") as f:
        f.write(protocol_content_alpha)
    print(f"Created dummy protocol files in: {dummy_protocol_dir_main}")

    # Clear PROTOCOL_REGISTRY before test scan to ensure clean state for this test run
    PROTOCOL_REGISTRY.clear()
    print(f"PROTOCOL_REGISTRY cleared. Current size: {len(PROTOCOL_REGISTRY)}")


    discovery_service = ProtocolDiscoveryService(db_session=test_db_session)

    # Conceptual: Assume a FileSystemProtocolSourceOrm record exists with ID 1
    # and its base_path points to a directory that makes `temp_ds_protocols_v3` importable.
    # For this test, the scan_path is `temp_protocols_base_dir`.
    # The `_scan_and_load_modules` adds parent of `temp_protocols_base_dir` to sys.path.
    # So, modules will be imported as `temp_ds_protocols_v3.main_protos.alpha_delta_set`.

    print(f"\n--- Running Discovery and Upsert (searching in '{temp_protocols_base_dir}')... ---")
    # For testing, we'll pass a dummy file_system_source_id.
    # In a real scenario, this ID would come from a previously created source entry.
    discovered_definitions_orm = discovery_service.discover_and_upsert_protocols(
        search_paths=[temp_protocols_base_dir],
        file_system_source_id=1 # Dummy FS source ID
    )

    if discovered_definitions_orm:
        print(f"\n--- {len(discovered_definitions_orm)} Protocol Definitions Processed/Upserted ---")
        for i, def_orm_instance in enumerate(discovered_definitions_orm):
            db_id_val = def_orm_instance.id if hasattr(def_orm_instance, 'id') else 'N/A (placeholder DB)'
            print(f"\n--- Definition {i+1} (DB ID: {db_id_val}) ---")
            print(f"  Name: {def_orm_instance.name}, Version: {def_orm_instance.version}")
            print(f"  Module: {def_orm_instance.module_name}, Function: {def_orm_instance.function_name}")

            meta_key = f"{def_orm_instance.name}_v{def_orm_instance.version}"
            if meta_key in PROTOCOL_REGISTRY:
                reg_entry = PROTOCOL_REGISTRY[meta_key]
                print(f"  PROTOCOL_REGISTRY['{meta_key}']['db_id']: {reg_entry.get('db_id')}")
                if hasattr(def_orm_instance, 'id') and reg_entry.get('db_id') != def_orm_instance.id:
                    print(f"  ERROR: Mismatch between ORM ID ({def_orm_instance.id}) and Registry DB ID ({reg_entry.get('db_id')})")
            else:
                print(f"  ERROR: '{meta_key}' not found in PROTOCOL_REGISTRY after discovery.")
    else:
        print("\nNo protocol definitions were processed by discovery service.")

    print(f"\nFinal PROTOCOL_REGISTRY size: {len(PROTOCOL_REGISTRY)}")
    print("--- End of Protocol Discovery Service Integration Test (v3) ---")

    # Cleanup (optional)
    # import shutil
    # if os.path.exists(temp_protocols_base_dir): shutil.rmtree(temp_protocols_base_dir)
    # if praxis_root_dir in sys.path: sys.path.remove(praxis_root_dir)

