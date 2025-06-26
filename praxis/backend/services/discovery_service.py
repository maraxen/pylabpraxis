# pylint: disable=too-few-public-methods,broad-except,fixme,unused-argument
"""Praxis protocol function discovery service.

praxis/protocol_core/discovery_service.py
Service responsible for discovering protocol functions, transforming their
metadata into structured Pydantic models, and upserting them into a database
via the protocol_data_service. It also updates the in-memory PROTOCOL_REGISTRY
with the database ID of the discovered protocols.
"""

import importlib
import inspect
import logging
import os
import sys
import traceback
import uuid
from typing import (
  Any,
  Callable,
  List,
  Optional,
  Set,
  Tuple,
  Union,
  get_args,
  get_origin,
)

from pylabrobot.resources import Resource
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker  # MODIFIED

# Global in-memory registry (populated by decorators, updated by this service)
from praxis.backend.core.run_context import PROTOCOL_REGISTRY
from praxis.backend.models.protocol_pydantic_models import (
  AssetRequirementModel,
  FunctionProtocolDefinitionModel,
  ParameterMetadataModel,
)

# MODIFIED: Import async version of upsert
from praxis.backend.services.protocols import (
  upsert_function_protocol_definition,
)
from praxis.backend.utils.uuid import uuid7
from praxis.backend.utils.type_inspection import (
  fqn_from_hint,
  is_pylabrobot_resource,
  serialize_type_hint,
)

logger = logging.getLogger(__name__)


# --- End Helper Functions ---


class ProtocolDiscoveryService:
  """Service for discovering and managing protocol functions.

  Discovers protocol functions, prepares their definitions, upserts them to the DB,
  and updates the in-memory PROTOCOL_REGISTRY with their database IDs.
  """

  def __init__(
    self, db_session_factory: Optional[async_sessionmaker[AsyncSession]] = None
  ):
    """Initialize the ProtocolDiscoveryService.

    Args:
      db_session_factory: An async session factory for database operations.
        If not provided, the service will not be able to upsert definitions.

    """
    self.db_session_factory = db_session_factory

  def _extract_protocol_definitions_from_paths(
    self,
    search_paths: Union[str, List[str]],
  ) -> List[Tuple[FunctionProtocolDefinitionModel, Optional[Callable]]]:
    """Extract protocol function definitions from Python files in the given paths.

    Scans the specified directories for Python files, inspects their functions,
    and extracts protocol definitions based on the presence of a custom attribute
    `_protocol_definition` on the function objects. If the attribute is not found,
    it infers the protocol definition from the function signature and docstring.
    This method supports both single path strings and lists of paths.
    It also handles reloading of modules to ensure the latest definitions are used.
    It returns a list of tuples, each containing a FunctionProtocolDefinitionModel
    and the corresponding function reference. If a function cannot be found or
    processed, it logs an error and continues with the next function.
    This method is synchronous and should be called before any async operations
    to ensure the definitions are ready for upsert.
    This method is designed to be robust against various issues that can arise
    during module import and function inspection, such as circular imports,
    missing attributes, or unexpected function signatures.
    It also ensures that the search paths are valid directories and handles
    cases where the provided paths do not exist or are not directories.
    It returns a list of tuples containing the FunctionProtocolDefinitionModel
    and the corresponding function reference, or None if the function could not
    be found or processed.

    Args:
      search_paths: A single path or a list of paths to search for Python files.

    Returns:
      A list of tuples containing the FunctionProtocolDefinitionModel and the
      corresponding function reference, or None if the function could not be found.

    """
    if isinstance(search_paths, str):
      search_paths = [search_paths]

    extracted_definitions: List[
      Tuple[FunctionProtocolDefinitionModel, Optional[Callable]]
    ] = []  # type: ignore
    processed_func_accession_ids: Set[int] = set()
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
            rel_module_path = os.path.relpath(
              module_file_path, potential_package_parent
            )
            module_import_name = os.path.splitext(rel_module_path)[0].replace(
              os.sep, "."
            )

            try:
              module = None
              if (
                module_import_name in loaded_module_names
                and module_import_name in sys.modules
              ):
                module = importlib.reload(sys.modules[module_import_name])
              else:
                module = importlib.import_module(module_import_name)
              loaded_module_names.add(module_import_name)

              for name, func_obj in inspect.getmembers(module, inspect.isfunction):
                if func_obj.__module__ != module_import_name:
                  continue
                if id(func_obj) in processed_func_accession_ids:
                  continue
                processed_func_accession_ids.add(id(func_obj))

                protocol_def_attr = getattr(func_obj, "_protocol_definition", None)
                if protocol_def_attr and isinstance(
                  protocol_def_attr, FunctionProtocolDefinitionModel
                ):
                  extracted_definitions.append((protocol_def_attr, func_obj))
                else:
                  sig = inspect.signature(func_obj)
                  params_list: List[ParameterMetadataModel] = []
                  assets_list: List[AssetRequirementModel] = []

                  for (
                    param_name,
                    param_obj_sig,
                  ) in sig.parameters.items():
                    param_type_hint = param_obj_sig.annotation
                    is_opt = (
                      get_origin(param_type_hint) is Union
                      and type(None) in get_args(param_type_hint)
                    ) or (param_obj_sig.default is not inspect.Parameter.empty)
                    fqn = fqn_from_hint(param_type_hint)

                    type_for_plr_check = param_type_hint
                    origin_check, args_check = (
                      get_origin(param_type_hint),
                      get_args(param_type_hint),
                    )
                    if origin_check is Union and type(None) in args_check:
                      non_none_args = [
                        arg for arg in args_check if arg is not type(None)
                      ]
                      if len(non_none_args) == 1:
                        type_for_plr_check = non_none_args[0]

                    common_args = {
                      "name": param_name,
                      "type_hint": serialize_type_hint(param_type_hint),
                      "fqn": fqn,
                      "optional": is_opt,
                      "default_value_repr": repr(param_obj_sig.default)
                      if param_obj_sig.default is not inspect.Parameter.empty
                      else None,
                    }
                    if is_pylabrobot_resource(type_for_plr_check):
                      assets_list.append(AssetRequirementModel(**common_args))
                    else:
                      params_list.append(
                        ParameterMetadataModel(**common_args, is_deck_param=False)
                      )

                  inferred_model = FunctionProtocolDefinitionModel(
                    accession_id=uuid7(),  # TODO: ensure that if a reinspection happens it is assigned the already existing
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
              logger.error(
                f"DiscoveryService: Could not import/process module "
                f"'{module_import_name}' from '{module_file_path}': {e}"
              )
              traceback.print_exc()
      if path_added_to_sys and potential_package_parent in sys.path:
        sys.path.remove(potential_package_parent)
    sys.path = original_sys_path
    return extracted_definitions

  async def discover_and_upsert_protocols(
    self,
    search_paths: Union[str, List[str]], # Re-added search_paths argument
    source_repository_accession_id: Optional[uuid.UUID] = None,
    commit_hash: Optional[str] = None,
    file_system_source_accession_id: Optional[uuid.UUID] = None,
  ) -> List[Any]:
    """Discover protocol functions in the given paths and upsert them to the DB.

    Scans the specified paths for Python files, extracts protocol definitions,
    and upserts them into the database using the provided session factory.
    If a source repository ID and commit hash are provided, they are linked to the
    protocol definitions. If a file system source ID is provided, it is used instead.
    If no definitions are found, it logs a warning and returns an empty list.
    If the DB session factory is not provided, it logs an error and returns an empty
    list.
    This method is asynchronous and should be awaited to ensure proper execution.

    Args:
      search_paths: A single path or a list of paths to search for protocol files.
      source_repository_accession_id: Optional[uuid.UUID]; ID of the source repository to link
      definitions.
      commit_hash: Optional[str]; commit hash to link definitions to a specific commit.
      file_system_source_accession_id: Optional[uuid.UUID]; ID of the file system source to link
      definitions.

    Returns:
      A list of upserted protocol definitions as ORM objects, or an empty list if none
      found.

    """
    if not self.db_session_factory:
      logger.error(
        "DiscoveryService: DB session factory not provided to ProtocolDiscoveryService."
        " Cannot upsert definitions."
      )
      return []

    logger.info(f"DiscoveryService: Starting protocol discovery in paths: {search_paths}...")
    extracted_definitions = self._extract_protocol_definitions_from_paths(search_paths)

    if not extracted_definitions:
      logger.warning("DiscoveryService: No protocol definitions found from scan.")
      return []

    logger.info(
      f"DiscoveryService: Found {len(extracted_definitions)} protocol functions. "
      f"Upserting to DB..."
    )
    upserted_definitions_orm: List[Any] = []

    async with self.db_session_factory() as session:
      for protocol_pydantic_model, func_ref in extracted_definitions:
        protocol_name_for_error = protocol_pydantic_model.name
        protocol_version_for_error = protocol_pydantic_model.version
        try:  # TODO: have these pull from the protocol database  ORM
          if source_repository_accession_id and commit_hash:
            protocol_pydantic_model.source_repository_name = str(
              source_repository_accession_id
            )
            protocol_pydantic_model.commit_hash = commit_hash
          elif file_system_source_accession_id:
            protocol_pydantic_model.file_system_source_name = str(
              file_system_source_accession_id
            )

          def_orm = await upsert_function_protocol_definition(
            db=session,
            protocol_pydantic=protocol_pydantic_model,
            source_repository_accession_id=source_repository_accession_id,
            commit_hash=commit_hash,
            file_system_source_accession_id=file_system_source_accession_id,
          )
          upserted_definitions_orm.append(def_orm)

          protocol_unique_key = (
            f"{protocol_pydantic_model.name}_v{protocol_pydantic_model.version}"
          )

          func_ref_protocol_def = getattr(func_ref, "_protocol_definition", None)
          if func_ref and func_ref_protocol_def is protocol_pydantic_model:
            if hasattr(def_orm, "id") and def_orm.accession_id is not None:
              setattr(func_ref_protocol_def, "db_accession_id", def_orm.accession_id)

          if protocol_unique_key in PROTOCOL_REGISTRY:
            if hasattr(def_orm, "id") and def_orm.accession_id is not None:
              PROTOCOL_REGISTRY[protocol_unique_key]["db_accession_id"] = (
                def_orm.accession_id
              )
              pydantic_def_in_registry = PROTOCOL_REGISTRY[protocol_unique_key].get(
                "pydantic_definition"
              )  # type: ignore
              if pydantic_def_in_registry and isinstance(
                pydantic_def_in_registry,
                FunctionProtocolDefinitionModel,
              ):
                setattr(
                  pydantic_def_in_registry, "db_accession_id", def_orm.accession_id
                )
            else:
              logger.warning(
                f"DiscoveryService: Upserted ORM object for '{protocol_unique_key}' has"
                f" no 'id'. Cannot update PROTOCOL_REGISTRY."
              )

        except Exception as e:
          logger.error(
            f"ERROR: Failed to process or upsert protocol '{protocol_name_for_error} "
            f"v{protocol_version_for_error}': {e}"
          )
          traceback.print_exc()
      # Commit happens when the session context manager exits if no exceptions

    num_successful_upserts = len(
      [
        d
        for d in upserted_definitions_orm
        if hasattr(d, "id") and d.accession_id is not None
      ]
    )
    logger.info(
      f"Successfully upserted {num_successful_upserts} protocol definition(s) to DB."
    )
    return upserted_definitions_orm
