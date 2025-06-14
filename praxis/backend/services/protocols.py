# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""Manage protocol-related data interactions.

praxis/db_services/protocol_data_service.py

Service layer for interacting with protocol-related data in the database.
This includes definitions for protocol sources, static protocol definitions,
protocol run instances, and function call logs.

"""

import datetime
import json
import logging
from typing import Dict, List, Optional, Union

import uuid
from sqlalchemy import desc, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, joinedload, selectinload

from praxis.backend.models import (
  AssetDefinitionOrm,
  FileSystemProtocolSourceOrm,
  FunctionCallLogOrm,
  FunctionCallStatusEnum,
  FunctionProtocolDefinitionModel,
  FunctionProtocolDefinitionOrm,
  ParameterDefinitionOrm,
  ProtocolRunOrm,
  ProtocolRunStatusEnum,
  ProtocolSourceRepositoryOrm,
  ProtocolSourceStatusEnum,
)

logger = logging.getLogger(__name__)


async def create_protocol_source_repository(
  db: AsyncSession,
  name: str,
  git_url: str,
  default_ref: str = "main",
  local_checkout_path: Optional[str] = None,
  status: ProtocolSourceStatusEnum = ProtocolSourceStatusEnum.ACTIVE,
  auto_sync_enabled: bool = True,
) -> ProtocolSourceRepositoryOrm:
  """Add a new protocol source repository.

  Args:
      db (AsyncSession): The database session.
      name (str): The unique name of the protocol source repository.
      git_url (str): The Git URL of the repository.
      default_ref (str, optional): The default Git reference (branch/tag) to
          use. Defaults to "main".
      local_checkout_path (Optional[str], optional): The local file system
          path where the repository is checked out. Defaults to None.
      status (ProtocolSourceStatusEnum, optional): The current status of the
          protocol source. Defaults to `ProtocolSourceStatusEnum.ACTIVE`.
      auto_sync_enabled (bool, optional): Whether automatic synchronization
          is enabled for this repository. Defaults to True.

  Returns:
      ProtocolSourceRepositoryOrm: The created protocol source repository object.

  Raises:
      ValueError: If a repository with the same `name` already exists.
      Exception: For any other unexpected errors during the process.

  """
  log_prefix = f"Protocol Source Repository (Name: '{name}', creating new):"
  logger.info("%s Attempting to create new repository.", log_prefix)

  # Check if a repository with this name already exists
  result = await db.execute(
    select(ProtocolSourceRepositoryOrm).filter(ProtocolSourceRepositoryOrm.name == name)
  )
  if result.scalar_one_or_none():
    error_message = (
      f"{log_prefix} A protocol source repository with name "
      f"'{name}' already exists. Use the update function for existing repositories."
    )
    logger.error(error_message)
    raise ValueError(error_message)

  # Create new ProtocolSourceRepositoryOrm
  source_repo = ProtocolSourceRepositoryOrm(
    name=name,
    git_url=git_url,
    default_ref=default_ref,
    local_checkout_path=local_checkout_path,
    status=status,
    auto_sync_enabled=auto_sync_enabled,
  )
  db.add(source_repo)
  logger.info("%s Initialized new repository for creation.", log_prefix)

  try:
    await db.commit()
    await db.refresh(source_repo)
    logger.info("%s Successfully committed new repository.", log_prefix)
  except IntegrityError as e:
    await db.rollback()
    # Assuming a unique constraint on 'name' for ProtocolSourceRepositoryOrm
    if "uq_protocol_source_repository_name" in str(e.orig):
      error_message = (
        f"{log_prefix} A protocol source repository with name "
        f"'{name}' already exists (integrity check failed). Details: {e}"
      )
      logger.error(error_message, exc_info=True)
      raise ValueError(error_message) from e
    error_message = (
      f"{log_prefix} Database integrity error during creation. Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception("%s Unexpected error during creation. Rolling back.", log_prefix)
    raise e

  logger.info("%s Creation operation completed.", log_prefix)
  return source_repo


async def update_protocol_source_repository(
  db: AsyncSession,
  source_accession_id: uuid.UUID,  # Identifier for the repository to update
  name: Optional[str] = None,
  git_url: Optional[str] = None,
  default_ref: Optional[str] = None,
  local_checkout_path: Optional[str] = None,
  status: Optional[ProtocolSourceStatusEnum] = None,
  auto_sync_enabled: Optional[bool] = None,
) -> ProtocolSourceRepositoryOrm:
  """Update an existing protocol source repository.

  Args:
      db (AsyncSession): The database session.
      source_accession_id (uuid.UUID): The ID of the existing repository to update.
      name (Optional[str], optional): The unique name of the protocol source repository.
          Defaults to None.
      git_url (Optional[str], optional): The Git URL of the repository.
          Defaults to None.
      default_ref (Optional[str], optional): The default Git reference (branch/tag) to
          use. Defaults to None.
      local_checkout_path (Optional[str], optional): The local file system
          path where the repository is checked out. Defaults to None.
      status (Optional[ProtocolSourceStatusEnum], optional): The current status of the
          protocol source. Defaults to None.
      auto_sync_enabled (Optional[bool], optional): Whether automatic synchronization
          is enabled for this repository. Defaults to None.

  Returns:
      ProtocolSourceRepositoryOrm: The updated protocol source repository object.

  Raises:
      ValueError: If `source_accession_id` is provided but no matching repository is found,
                  or if the updated `name` conflicts with an existing one.
      Exception: For any other unexpected errors during the process.

  """
  log_prefix = f"Protocol Source Repository (ID: {source_accession_id}, updating):"
  logger.info("%s Attempting to update repository.", log_prefix)

  # Fetch the existing repository
  result = await db.execute(
    select(ProtocolSourceRepositoryOrm).filter(
      ProtocolSourceRepositoryOrm.accession_id == source_accession_id
    )
  )
  source_repo = result.scalar_one_or_none()

  if not source_repo:
    error_message = f"{log_prefix} ProtocolSourceRepositoryOrm with ID {source_accession_id} not found for update."
    logger.error(error_message)
    raise ValueError(error_message)
  logger.info("%s Found existing repository for update.", log_prefix)

  # Check for name conflict if it's being changed
  if name is not None and source_repo.name != name:
    existing_name_check = await db.execute(
      select(ProtocolSourceRepositoryOrm)
      .filter(ProtocolSourceRepositoryOrm.name == name)
      .filter(
        ProtocolSourceRepositoryOrm.accession_id != source_accession_id
      )  # Exclude the current record
    )
    if existing_name_check.scalar_one_or_none():
      error_message = (
        f"{log_prefix} Cannot update name to '{name}' as it already "
        f"exists for another protocol source repository."
      )
      logger.error(error_message)
      raise ValueError(error_message)
    source_repo.name = name

  # Update attributes if provided
  if git_url is not None:
    source_repo.git_url = git_url
  if default_ref is not None:
    source_repo.default_ref = default_ref
  if local_checkout_path is not None:
    source_repo.local_checkout_path = local_checkout_path
  if status is not None:
    source_repo.status = status
  if auto_sync_enabled is not None:
    source_repo.auto_sync_enabled = auto_sync_enabled

  try:
    await db.commit()
    await db.refresh(source_repo)
    logger.info("%s Successfully committed update.", log_prefix)
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"{log_prefix} Database integrity error during update. "
      f"This might occur if a unique constraint is violated. Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception("%s Unexpected error during update. Rolling back.", log_prefix)
    raise e

  logger.info("%s Update operation completed.", log_prefix)
  return source_repo


async def read_protocol_source_repository(
  db: AsyncSession, source_accession_id: uuid.UUID
) -> Optional[ProtocolSourceRepositoryOrm]:
  """Retrieve a protocol source repository by its ID.

  Args:
      db (AsyncSession): The database session.
      source_accession_id (uuid.UUID): The ID of the protocol source repository to retrieve.

  Returns:
      Optional[ProtocolSourceRepositoryOrm]: The protocol source repository object
      if found, otherwise None.

  """
  log_prefix = f"Protocol Source Repository (ID: {source_accession_id}):"
  logger.info("%s Attempting to read by ID.", log_prefix)
  result = await db.execute(
    select(ProtocolSourceRepositoryOrm).filter(
      ProtocolSourceRepositoryOrm.accession_id == source_accession_id
    )
  )
  repo = result.scalar_one_or_none()
  if repo:
    logger.info("%s Found repository.", log_prefix)
  else:
    logger.info("%s Repository not found.", log_prefix)
  return repo


async def read_protocol_source_repository_by_name(
  db: AsyncSession, name: str
) -> Optional[ProtocolSourceRepositoryOrm]:
  """Retrieve a protocol source repository by its unique name.

  Args:
      db (AsyncSession): The database session.
      name (str): The unique name of the protocol source repository to retrieve.

  Returns:
      Optional[ProtocolSourceRepositoryOrm]: The protocol source repository object
      if found, otherwise None.

  """
  log_prefix = f"Protocol Source Repository (Name: '{name}'):"
  logger.info("%s Attempting to read by name.", log_prefix)
  result = await db.execute(
    select(ProtocolSourceRepositoryOrm).filter(ProtocolSourceRepositoryOrm.name == name)
  )
  repo = result.scalar_one_or_none()
  if repo:
    logger.info("%s Found repository.", log_prefix)
  else:
    logger.info("%s Repository not found.", log_prefix)
  return repo


async def list_protocol_source_repositories(
  db: AsyncSession,
  status: Optional[ProtocolSourceStatusEnum] = None,
  auto_sync_enabled: Optional[bool] = None,
  limit: int = 100,
  offset: int = 0,
) -> List[ProtocolSourceRepositoryOrm]:
  """List protocol source repositories with optional filtering and pagination.

  Args:
      db (AsyncSession): The database session.
      status (Optional[ProtocolSourceStatusEnum], optional): Filter by status. Defaults to None.
      auto_sync_enabled (Optional[bool], optional): Filter by auto-sync enabled status. Defaults to None.
      limit (int): The maximum number of results to return. Defaults to 100.
      offset (int): The number of results to skip before returning. Defaults to 0.

  Returns:
      List[ProtocolSourceRepositoryOrm]: A list of protocol source repository objects
      matching the criteria.

  """
  logger.info(
    "Listing protocol source repositories with filters: status=%s, "
    "auto_sync_enabled=%s, limit=%d, offset=%d.",
    status,
    auto_sync_enabled,
    limit,
    offset,
  )
  stmt = select(ProtocolSourceRepositoryOrm)
  if status is not None:
    stmt = stmt.filter(ProtocolSourceRepositoryOrm.status == status)
    logger.debug("Filtering by status: %s.", status)
  if auto_sync_enabled is not None:
    stmt = stmt.filter(
      ProtocolSourceRepositoryOrm.auto_sync_enabled == auto_sync_enabled
    )
    logger.debug("Filtering by auto_sync_enabled: %s.", auto_sync_enabled)

  stmt = stmt.order_by(ProtocolSourceRepositoryOrm.name).limit(limit).offset(offset)
  result = await db.execute(stmt)
  repositories = list(result.scalars().all())
  logger.info("Found %d protocol source repositories.", len(repositories))
  return repositories


async def create_file_system_protocol_source(
  db: AsyncSession,
  name: str,
  base_path: str,
  is_recursive: bool = True,
  status: ProtocolSourceStatusEnum = ProtocolSourceStatusEnum.ACTIVE,
) -> FileSystemProtocolSourceOrm:
  """Add a new file system protocol source.

  Args:
      db (AsyncSession): The database session.
      name (str): The unique name of the file system protocol source.
      base_path (str): The base file system path for protocols.
      is_recursive (bool, optional): Whether to recursively scan the base path
          for protocols. Defaults to True.
      status (ProtocolSourceStatusEnum, optional): The current status of the
          file system source. Defaults to `ProtocolSourceStatusEnum.ACTIVE`.

  Returns:
      FileSystemProtocolSourceOrm: The created file system protocol
      source object.

  Raises:
      ValueError: If a file system source with the same `name` already exists.
      Exception: For any other unexpected errors during the process.

  """
  log_prefix = f"File System Protocol Source (Name: '{name}', creating new):"
  logger.info("%s Attempting to create new file system source.", log_prefix)

  # Check if a file system source with this name already exists
  result = await db.execute(
    select(FileSystemProtocolSourceOrm).filter(FileSystemProtocolSourceOrm.name == name)
  )
  if result.scalar_one_or_none():
    error_message = (
      f"{log_prefix} A file system protocol source with name "
      f"'{name}' already exists. Use the update function for existing sources."
    )
    logger.error(error_message)
    raise ValueError(error_message)

  # Create new FileSystemProtocolSourceOrm
  fs_source = FileSystemProtocolSourceOrm(
    name=name,
    base_path=base_path,
    is_recursive=is_recursive,
    status=status,
  )
  db.add(fs_source)
  logger.info("%s Initialized new file system source for creation.", log_prefix)

  try:
    await db.commit()
    await db.refresh(fs_source)
    logger.info("%s Successfully committed new file system source.", log_prefix)
  except IntegrityError as e:
    await db.rollback()
    # Assuming a unique constraint on 'name' for FileSystemProtocolSourceOrm
    if "uq_file_system_protocol_source_name" in str(e.orig):
      error_message = (
        f"{log_prefix} A file system source with name "
        f"'{name}' already exists (integrity check failed). Details: {e}"
      )
      logger.error(error_message, exc_info=True)
      raise ValueError(error_message) from e
    error_message = (
      f"{log_prefix} Database integrity error during creation. Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception("%s Unexpected error during creation. Rolling back.", log_prefix)
    raise e

  logger.info("%s Creation operation completed.", log_prefix)
  return fs_source


async def update_file_system_protocol_source(
  db: AsyncSession,
  source_accession_id: uuid.UUID,  # Identifier for the source to update
  name: Optional[str] = None,
  base_path: Optional[str] = None,
  is_recursive: Optional[bool] = None,
  status: Optional[ProtocolSourceStatusEnum] = None,
) -> FileSystemProtocolSourceOrm:
  """Update an existing file system protocol source.

  Args:
      db (AsyncSession): The database session.
      source_accession_id (uuid.UUID): The ID of an existing source to update.
      name (Optional[str], optional): The unique name of the file system protocol source.
          Defaults to None.
      base_path (Optional[str], optional): The base file system path for protocols.
          Defaults to None.
      is_recursive (Optional[bool], optional): Whether to recursively scan the base path
          for protocols. Defaults to None.
      status (Optional[ProtocolSourceStatusEnum], optional): The current status of the
          file system source. Defaults to None.

  Returns:
      FileSystemProtocolSourceOrm: The updated file system protocol
      source object.

  Raises:
      ValueError: If `source_accession_id` is provided but no matching source is found,
                  or if the updated `name` conflicts with an existing one.
      Exception: For any other unexpected errors during the process.

  """
  log_prefix = f"File System Protocol Source (ID: {source_accession_id}, updating):"
  logger.info("%s Attempting to update file system source.", log_prefix)

  # Fetch the existing source
  result = await db.execute(
    select(FileSystemProtocolSourceOrm).filter(
      FileSystemProtocolSourceOrm.accession_id == source_accession_id
    )
  )
  fs_source = result.scalar_one_or_none()

  if not fs_source:
    error_message = f"{log_prefix} FileSystemProtocolSourceOrm with ID {source_accession_id} not found for update."
    logger.error(error_message)
    raise ValueError(error_message)
  logger.info("%s Found existing file system source for update.", log_prefix)

  # Check for name conflict if it's being changed
  if name is not None and fs_source.name != name:
    existing_name_check = await db.execute(
      select(FileSystemProtocolSourceOrm)
      .filter(FileSystemProtocolSourceOrm.name == name)
      .filter(
        FileSystemProtocolSourceOrm.accession_id != source_accession_id
      )  # Exclude the current record
    )
    if existing_name_check.scalar_one_or_none():
      error_message = (
        f"{log_prefix} Cannot update name to '{name}' as it already "
        f"exists for another file system protocol source."
      )
      logger.error(error_message)
      raise ValueError(error_message)
    fs_source.name = name

  # Update attributes if provided
  if base_path is not None:
    fs_source.base_path = base_path
  if is_recursive is not None:
    fs_source.is_recursive = is_recursive
  if status is not None:
    fs_source.status = status

  try:
    await db.commit()
    await db.refresh(fs_source)
    logger.info("%s Successfully committed update.", log_prefix)
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"{log_prefix} Database integrity error during update. "
      f"This might occur if a unique constraint is violated. Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception("%s Unexpected error during update. Rolling back.", log_prefix)
    raise e

  logger.info("%s Update operation completed.", log_prefix)
  return fs_source


async def upsert_function_protocol_definition(
  db: AsyncSession,
  protocol_pydantic: FunctionProtocolDefinitionModel,
  source_repository_accession_id: Optional[uuid.UUID] = None,
  commit_hash: Optional[str] = None,
  file_system_source_accession_id: Optional[uuid.UUID] = None,
) -> FunctionProtocolDefinitionOrm:
  """Add or update a function protocol definition.

  This function creates a new `FunctionProtocolDefinitionOrm` or updates an
  existing one based on its name, version, and associated source (either Git
  repository + commit hash or file system source + file path). It handles
  the synchronization of parameters and assets.

  Args:
      db (AsyncSession): The database session.
      protocol_pydantic (FunctionProtocolDefinitionModel): The Pydantic model
          representing the function protocol definition.
      source_repository_accession_id (Optional[int], optional): The ID of the Git
          protocol source repository if applicable. Defaults to None.
      commit_hash (Optional[str], optional): The commit hash from the Git
          repository if applicable. Defaults to None.
      file_system_source_accession_id (Optional[int], optional): The ID of the file
          system protocol source if applicable. Defaults to None.

  Returns:
      FunctionProtocolDefinitionOrm: The created or updated protocol
      definition object.

  Raises:
      ValueError: If the protocol definition is not linked to a source, or
          for integrity errors during the upsert.
      Exception: For any other unexpected errors during the process.

  """
  log_prefix = (
    f"Function Protocol Definition (Name: '{protocol_pydantic.name}', "
    f"Version: '{protocol_pydantic.version}'):"
  )
  logger.info("%s Attempting to upsert.", log_prefix)

  query_filter_dict: dict[str, Union[str, uuid.UUID]] = {
    "name": protocol_pydantic.name,
    "version": protocol_pydantic.version,
  }
  if source_repository_accession_id and commit_hash:
    query_filter_dict["source_repository_accession_id"] = source_repository_accession_id
    query_filter_dict["commit_hash"] = commit_hash
    logger.debug(
      "%s Linking to Git source (ID: %s, Commit: %s).",
      log_prefix,
      source_repository_accession_id,
      commit_hash,
    )
  elif file_system_source_accession_id:
    query_filter_dict["file_system_source_accession_id"] = (
      file_system_source_accession_id
    )
    query_filter_dict["source_file_path"] = protocol_pydantic.source_file_path
    logger.debug(
      "%s Linking to File System source (ID: %s, Path: %s).",
      log_prefix,
      file_system_source_accession_id,
      protocol_pydantic.source_file_path,
    )
  else:
    error_message = (
      f"{log_prefix} Protocol definition must be linked to a source "
      "(Git repo + commit hash, or file system source)."
    )
    logger.error(error_message)
    raise ValueError(error_message)

  stmt = (
    select(FunctionProtocolDefinitionOrm)
    .options(
      selectinload(FunctionProtocolDefinitionOrm.parameters),
      selectinload(FunctionProtocolDefinitionOrm.assets),
    )
    .filter_by(**query_filter_dict)
  )
  result = await db.execute(stmt)
  def_orm = result.scalar_one_or_none()

  if not def_orm:
    def_orm = FunctionProtocolDefinitionOrm(**query_filter_dict)  # type: ignore
    db.add(def_orm)
    logger.info("%s No existing definition found, creating new.", log_prefix)
  else:
    logger.info("%s Found existing definition, updating.", log_prefix)

  def_orm.description = protocol_pydantic.description
  def_orm.source_file_path = protocol_pydantic.source_file_path
  def_orm.module_name = protocol_pydantic.module_name
  def_orm.function_name = protocol_pydantic.function_name
  def_orm.is_top_level = protocol_pydantic.is_top_level
  def_orm.solo_execution = protocol_pydantic.solo_execution
  def_orm.preconfigure_deck = protocol_pydantic.preconfigure_deck
  def_orm.deck_param_name = protocol_pydantic.deck_param_name
  def_orm.state_param_name = protocol_pydantic.state_param_name
  def_orm.category = protocol_pydantic.category
  def_orm.tags = {"values": protocol_pydantic.tags} if protocol_pydantic.tags else None
  def_orm.deprecated = (
    False  # Assuming new/updated definitions are not deprecated by default
  )
  def_orm.source_repository_accession_id = source_repository_accession_id
  def_orm.commit_hash = commit_hash
  def_orm.file_system_source_accession_id = file_system_source_accession_id
  logger.debug("%s Updated core attributes.", log_prefix)

  # Parameters
  current_params = {p.name: p for p in def_orm.parameters}
  new_params_list = []
  for param_model in protocol_pydantic.parameters:
    param_orm = current_params.pop(param_model.name, None)
    if not param_orm:
      # Ensure def_orm.accession_id is not None if it's a new protocol
      if def_orm.accession_id is None:
        await db.flush()  # Flush to get ID for new def_orm
        if def_orm.accession_id is None:
          raise ValueError(
            f"{log_prefix} Failed to get ID for new protocol definition."
          )
      param_orm = ParameterDefinitionOrm(
        protocol_definition_accession_id=def_orm.accession_id
      )
      db.add(param_orm)  # Add new parameter to session
      logger.debug("%s Adding new parameter: %s.", log_prefix, param_model.name)
    else:
      logger.debug("%s Updating existing parameter: %s.", log_prefix, param_model.name)

    param_orm.name = param_model.name
    param_orm.type_hint_str = param_model.type_hint_str
    param_orm.actual_type_str = param_model.actual_type_str
    param_orm.is_deck_param = param_model.is_deck_param
    param_orm.optional = param_model.optional
    param_orm.default_value_repr = param_model.default_value_repr
    param_orm.description = param_model.description
    param_orm.constraints_json = (
      param_model.constraints.model_dump() if param_model.constraints else None
    )
    new_params_list.append(param_orm)

  # Remove old parameters
  for old_param in current_params.values():
    logger.debug("%s Deleting old parameter: %s.", log_prefix, old_param.name)
    await db.delete(old_param)
  def_orm.parameters = new_params_list  # type: ignore
  logger.debug("%s Synchronized parameters.", log_prefix)

  # Assets
  current_assets = {p.name: p for p in def_orm.assets}
  new_assets_list = []
  for asset_model in protocol_pydantic.assets:
    asset_orm = current_assets.pop(asset_model.name, None)
    if not asset_orm:
      # Ensure def_orm.accession_id is not None if it's a new protocol
      if def_orm.accession_id is None:
        await db.flush()  # Flush to get ID for new def_orm
        if def_orm.accession_id is None:
          raise ValueError(
            f"{log_prefix} Failed to get ID for new protocol definition."
          )
      asset_orm = AssetDefinitionOrm(
        protocol_definition_accession_id=def_orm.accession_id
      )
      db.add(asset_orm)  # Add new asset to session
      logger.debug("%s Adding new asset: %s.", log_prefix, asset_model.name)
    else:
      logger.debug("%s Updating existing asset: %s.", log_prefix, asset_model.name)

    asset_orm.name = asset_model.name
    asset_orm.type_hint_str = asset_model.type_hint_str
    asset_orm.actual_type_str = asset_model.actual_type_str
    asset_orm.optional = asset_model.optional
    asset_orm.default_value_repr = asset_model.default_value_repr
    asset_orm.description = asset_model.description
    asset_orm.constraints_json = (
      asset_model.constraints.model_dump() if asset_model.constraints else None
    )
    new_assets_list.append(asset_orm)

  # Remove old assets
  for old_asset in current_assets.values():
    logger.debug("%s Deleting old asset: %s.", log_prefix, old_asset.name)
    await db.delete(old_asset)
  def_orm.assets = new_assets_list  # type: ignore
  logger.debug("%s Synchronized assets.", log_prefix)

  try:
    await db.commit()
    await db.refresh(def_orm)
    logger.info("%s Successfully upserted protocol definition.", log_prefix)
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"{log_prefix} Integrity error during upsert. This might be due to "
      f"a duplicate name/version/source combination. Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception("%s Unexpected error during upsert. Rolling back.", log_prefix)
    raise e
  logger.info("%s Operation completed.", log_prefix)
  return def_orm


async def create_protocol_run(
  db: AsyncSession,
  run_accession_id: uuid.UUID,
  top_level_protocol_definition_accession_id: uuid.UUID,
  status: ProtocolRunStatusEnum = ProtocolRunStatusEnum.PENDING,
  input_parameters_json: Optional[str] = None,
  initial_state_json: Optional[str] = None,
) -> ProtocolRunOrm:
  """Create a new protocol run instance.

  Args:
      db (AsyncSession): The database session.
      run_accession_id (uuid.UUID): A unique GUID for this protocol run.
      top_level_protocol_definition_accession_id (uuid.UUID): The ID of the top-level
          protocol definition this run is based on.
      status (ProtocolRunStatusEnum, optional): The initial status of the run.
          Defaults to `ProtocolRunStatusEnum.PENDING`.
      input_parameters_json (Optional[str], optional): A JSON string of input
          parameters for the run. Will be parsed into a dictionary. Defaults to
          None.
      initial_state_json (Optional[str], optional): A JSON string representing
          the initial state of the system for this run. Will be parsed into a
          dictionary. Defaults to None.

  Returns:
      ProtocolRunOrm: The newly created protocol run object.

  Raises:
      Exception: For any unexpected errors during the process.

  """
  logger.info(
    "Creating new protocol run with GUID '%s' for definition ID %d.",
    run_accession_id,
    top_level_protocol_definition_accession_id,
  )
  utc_now = datetime.datetime.now(datetime.timezone.utc)
  db_protocol_run = ProtocolRunOrm(
    run_accession_id=run_accession_id,
    top_level_protocol_definition_accession_id=top_level_protocol_definition_accession_id,
    status=status,
    input_parameters_json=(
      json.loads(input_parameters_json) if input_parameters_json else {}
    ),
    initial_state_json=(json.loads(initial_state_json) if initial_state_json else {}),
    start_time=utc_now if status != ProtocolRunStatusEnum.PENDING else None,
  )
  db.add(db_protocol_run)
  try:
    await db.commit()
    await db.refresh(db_protocol_run)
    logger.info(
      "Successfully created protocol run (ID: %d, GUID: %s).",
      db_protocol_run.accession_id,
      db_protocol_run.run_accession_id,
    )
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Integrity error creating protocol run '{run_accession_id}'. This might "
      f"be due to a duplicate GUID. Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error creating protocol run '%s'. Rolling back.",
      run_accession_id,
    )
    raise e
  return db_protocol_run


async def update_protocol_run_status(
  db: AsyncSession,
  protocol_run_accession_id: uuid.UUID,
  new_status: ProtocolRunStatusEnum,
  output_data_json: Optional[str] = None,
  final_state_json: Optional[str] = None,
  error_info: Optional[Dict[str, str]] = None,
) -> Optional[ProtocolRunOrm]:
  """Update the status and details of a protocol run.

  This function updates the status of a `ProtocolRunOrm`. If the new status
  is `RUNNING` and `start_time` is not set, it will be set. If the new status
  indicates completion (`COMPLETED`, `FAILED`, `CANCELLED`), `end_time` and
  `duration_ms` will be calculated, and `output_data_json` or `final_state_json`
  will be updated. For `FAILED` status, `error_info` can be stored.

  Args:
      db (AsyncSession): The database session.
      protocol_run_accession_id (int): The ID of the protocol run to update.
      new_status (ProtocolRunStatusEnum): The new status for the protocol run.
      output_data_json (Optional[str], optional): A JSON string representing
          the output data of the run. Defaults to None.
      final_state_json (Optional[str], optional): A JSON string representing
          the final state of the system after the run. Defaults to None.
      error_info (Optional[Dict[str, str]], optional): A dictionary containing
          error details if the status is `FAILED`. Defaults to None.

  Returns:
      Optional[ProtocolRunOrm]: The updated protocol run object if found,
      otherwise None.

  Raises:
      Exception: For any unexpected errors during the process.

  """
  logger.info(
    "Updating status for protocol run ID %d to '%s'.",
    protocol_run_accession_id,
    new_status.name,
  )
  stmt = select(ProtocolRunOrm).filter(
    ProtocolRunOrm.accession_id == protocol_run_accession_id
  )
  result = await db.execute(stmt)
  db_protocol_run = result.scalar_one_or_none()

  if db_protocol_run:
    db_protocol_run.status = new_status
    utc_now = datetime.datetime.now(datetime.timezone.utc)

    if new_status == ProtocolRunStatusEnum.RUNNING and not db_protocol_run.start_time:
      db_protocol_run.start_time = utc_now
      logger.debug(
        "Protocol run ID %d started at %s.", protocol_run_accession_id, utc_now
      )

    if new_status in [
      ProtocolRunStatusEnum.COMPLETED,
      ProtocolRunStatusEnum.FAILED,
      ProtocolRunStatusEnum.CANCELLED,
    ]:
      db_protocol_run.end_time = utc_now
      logger.debug(
        "Protocol run ID %d ended at %s with status %s.",
        protocol_run_accession_id,
        utc_now,
        new_status.name,
      )
      if db_protocol_run.start_time and db_protocol_run.end_time:
        duration = db_protocol_run.end_time - db_protocol_run.start_time  # type: ignore
        db_protocol_run.duration_ms = int(duration.total_seconds() * 1000)
        logger.debug(
          "Protocol run ID %d duration: %d ms.",
          protocol_run_accession_id,
          db_protocol_run.duration_ms,
        )
      if output_data_json is not None:
        db_protocol_run.output_data_json = json.loads(output_data_json)
        logger.debug(
          "Protocol run ID %d updated with output data.",
          protocol_run_accession_id,
        )
      if final_state_json is not None:
        db_protocol_run.final_state_json = json.loads(final_state_json)
        logger.debug(
          "Protocol run ID %d updated with final state.",
          protocol_run_accession_id,
        )
      if new_status == ProtocolRunStatusEnum.FAILED and error_info:
        db_protocol_run.output_data_json = error_info  # type: ignore
        logger.error(
          "Protocol run ID %d failed with error info: %s",
          protocol_run_accession_id,
          error_info,
        )
    try:
      await db.commit()
      await db.refresh(db_protocol_run)
      logger.info(
        "Successfully updated protocol run ID %d status to '%s'.",
        protocol_run_accession_id,
        new_status.name,
      )
    except Exception as e:
      await db.rollback()
      logger.exception(
        "Unexpected error updating protocol run ID %d status. Rolling back.",
        protocol_run_accession_id,
      )
      raise e
    return db_protocol_run
  logger.warning(
    "Protocol run ID %d not found for status update.",
    protocol_run_accession_id,
  )
  return None


async def log_function_call_start(
  db: AsyncSession,
  protocol_run_orm_accession_id: uuid.UUID,
  function_definition_accession_id: uuid.UUID,
  sequence_in_run: int,
  input_args_json: str,
  parent_function_call_log_accession_id: Optional[uuid.UUID] = None,
) -> FunctionCallLogOrm:
  """Log the start of a function call within a protocol run.

  Args:
      db (AsyncSession): The database session.
      protocol_run_orm_accession_id (int): The ID of the parent protocol run.
      function_definition_accession_id (int): The ID of the function protocol definition
          being called.
      sequence_in_run (int): The sequential number of this function call
          within its protocol run.
      input_args_json (str): A JSON string representing the input arguments
          to the function call. Will be parsed into a dictionary.
      parent_function_call_log_accession_id (Optional[int], optional): The ID of the
          parent function call log if this is a nested call. Defaults to None.

  Returns:
      FunctionCallLogOrm: The newly created function call log object.

  Raises:
      Exception: For any unexpected errors during the process.

  """
  logger.info(
    "Logging start of function call for protocol run ID %d, function def ID %d, "
    "sequence %d.",
    protocol_run_orm_accession_id,
    function_definition_accession_id,
    sequence_in_run,
  )
  call_log = FunctionCallLogOrm(
    protocol_run_accession_id=protocol_run_orm_accession_id,
    function_protocol_definition_accession_id=function_definition_accession_id,
    sequence_in_run=sequence_in_run,
    parent_function_call_log_accession_id=parent_function_call_log_accession_id,
    start_time=datetime.datetime.now(datetime.timezone.utc),
    input_args_json=(json.loads(input_args_json) if input_args_json else {}),
    status=FunctionCallStatusEnum.SUCCESS,  # Initial status, will be updated on end
  )
  db.add(call_log)
  try:
    await db.commit()
    await db.refresh(call_log)
    logger.info(
      "Successfully logged function call start (ID: %d).", call_log.accession_id
    )
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Integrity error logging function call start for protocol run ID "
      f"{protocol_run_orm_accession_id}, sequence {sequence_in_run}. Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception("Unexpected error logging function call start. Rolling back.")
    raise e
  return call_log


async def log_function_call_end(
  db: AsyncSession,
  function_call_log_accession_id: uuid.UUID,
  status: FunctionCallStatusEnum,
  return_value_json: Optional[str] = None,
  error_message: Optional[str] = None,
  error_traceback: Optional[str] = None,
  duration_ms: Optional[float] = None,
) -> Optional[FunctionCallLogOrm]:
  """Log the end of a function call, updating its status and results.

  Args:
      db (AsyncSession): The database session.
      function_call_log_accession_id (int): The ID of the function call log to update.
      status (FunctionCallStatusEnum): The final status of the function call
          (e.g., `SUCCESS`, `FAILED`).
      return_value_json (Optional[str], optional): A JSON string representing
          the return value of the function call. Defaults to None.
      error_message (Optional[str], optional): An error message if the
          function call failed. Defaults to None.
      error_traceback (Optional[str], optional): The traceback string if an
          error occurred. Defaults to None.
      duration_ms (Optional[float], optional): The duration of the function
          call in milliseconds. If None, it will be calculated from start/end
          times. Defaults to None.

  Returns:
      Optional[FunctionCallLogOrm]: The updated function call log object if
      found, otherwise None.

  Raises:
      Exception: For any unexpected errors during the process.

  """
  logger.info(
    "Logging end of function call ID %d with status '%s'.",
    function_call_log_accession_id,
    status.name,
  )
  stmt = select(FunctionCallLogOrm).filter(
    FunctionCallLogOrm.accession_id == function_call_log_accession_id
  )
  result = await db.execute(stmt)
  call_log = result.scalar_one_or_none()

  if call_log:
    call_log.end_time = datetime.datetime.now(datetime.timezone.utc)
    if duration_ms is not None:
      call_log.duration_ms = int(duration_ms)
    elif call_log.start_time and call_log.end_time is not None:
      call_log.duration_ms = int(
        (call_log.end_time - call_log.start_time).total_seconds() * 1000  # type: ignore
      )
    call_log.status = status
    if return_value_json is not None:
      call_log.return_value_json = json.loads(return_value_json)
    if error_message is not None:
      call_log.error_message_text = error_message
    if error_traceback is not None:
      call_log.error_traceback_text = error_traceback
    try:
      await db.commit()
      await db.refresh(call_log)
      logger.info(
        "Successfully logged function call end for ID %d.",
        function_call_log_accession_id,
      )
    except Exception as e:
      await db.rollback()
      logger.exception(
        "Unexpected error logging function call end for ID %d. Rolling back.",
        function_call_log_accession_id,
      )
      raise e
    return call_log
  logger.warning(
    "Function call log ID %d not found for end logging.",
    function_call_log_accession_id,
  )
  return None


async def read_protocol_definition(
  db: AsyncSession,
  definition_accession_id: uuid.UUID,
) -> Optional[FunctionProtocolDefinitionOrm]:
  """Retrieve a protocol definition by its ID.

  Args:
      db (AsyncSession): The database session.
      definition_accession_id (uuid.UUID): The ID of the protocol definition to retrieve.

  Returns:
      Optional[FunctionProtocolDefinitionOrm]: The protocol definition object
      if found, otherwise None.

  """
  logger.info(
    "Retrieving protocol definition with ID: %d.",
    definition_accession_id,
  )
  stmt = (
    select(FunctionProtocolDefinitionOrm)
    .options(
      selectinload(FunctionProtocolDefinitionOrm.parameters),
      selectinload(FunctionProtocolDefinitionOrm.assets),
      joinedload(FunctionProtocolDefinitionOrm.source_repository),
      joinedload(FunctionProtocolDefinitionOrm.file_system_source),
    )
    .filter(FunctionProtocolDefinitionOrm.accession_id == definition_accession_id)
  )
  result = await db.execute(stmt)
  protocol_def = result.scalar_one_or_none()
  if protocol_def:
    logger.info(
      "Found protocol definition ID %d: '%s' (Version: %s).",
      definition_accession_id,
      protocol_def.name,
      protocol_def.version,
    )
  else:
    logger.info("Protocol definition ID %d not found.", definition_accession_id)
  return protocol_def


async def read_protocol_definition_details(
  db: AsyncSession,
  name: str,
  version: Optional[str] = None,
  source_name: Optional[str] = None,
  commit_hash: Optional[str] = None,
) -> Optional[FunctionProtocolDefinitionOrm]:
  """Retrieve details of a specific protocol definition.

  This function fetches a `FunctionProtocolDefinitionOrm` by its name,
  optionally filtered by version, source name, and commit hash. It prioritizes
  the latest version if no version is specified.

  Args:
      db (AsyncSession): The database session.
      name (str): The name of the protocol definition.
      version (Optional[str], optional): The specific version of the protocol.
          If None, the latest non-deprecated version will be retrieved.
          Defaults to None.
      source_name (Optional[str], optional): The name of the protocol source
          (either Git repository or file system). Defaults to None.
      commit_hash (Optional[str], optional): The Git commit hash if the
          protocol is from a Git repository. Defaults to None.

  Returns:
      Optional[FunctionProtocolDefinitionOrm]: The protocol definition object
      if found, otherwise None.

  """
  logger.info(
    "Retrieving protocol definition details for name '%s', version '%s', "
    "source '%s', commit '%s'.",
    name,
    version,
    source_name,
    commit_hash,
  )
  stmt = (
    select(FunctionProtocolDefinitionOrm)
    .options(
      selectinload(FunctionProtocolDefinitionOrm.parameters),
      selectinload(FunctionProtocolDefinitionOrm.assets),
      joinedload(FunctionProtocolDefinitionOrm.source_repository),
      joinedload(FunctionProtocolDefinitionOrm.file_system_source),
    )
    .filter(
      FunctionProtocolDefinitionOrm.name == name,
      ~FunctionProtocolDefinitionOrm.deprecated,
    )
  )

  if version:
    stmt = stmt.filter(FunctionProtocolDefinitionOrm.version == version)

  if commit_hash:
    stmt = stmt.filter(FunctionProtocolDefinitionOrm.commit_hash == commit_hash)
    if source_name:
      stmt = stmt.join(
        ProtocolSourceRepositoryOrm,
        FunctionProtocolDefinitionOrm.source_repository_accession_id
        == ProtocolSourceRepositoryOrm.accession_id,
      ).filter(ProtocolSourceRepositoryOrm.name == source_name)
    logger.debug("Filtering by commit hash and Git source name.")
  elif source_name:
    git_source_alias = aliased(ProtocolSourceRepositoryOrm)
    fs_source_alias = aliased(FileSystemProtocolSourceOrm)
    stmt = (
      stmt.outerjoin(
        git_source_alias,
        FunctionProtocolDefinitionOrm.source_repository_accession_id
        == git_source_alias.accession_id,
      )
      .outerjoin(
        fs_source_alias,
        FunctionProtocolDefinitionOrm.file_system_source_accession_id
        == fs_source_alias.accession_id,
      )
      .filter(
        or_(
          git_source_alias.name == source_name,
          fs_source_alias.name == source_name,
        )
      )
    )
    logger.debug("Filtering by generic source name (Git or File System).")

  if not version:
    # If no version specified, order by creation date to get latest
    stmt = stmt.order_by(desc(FunctionProtocolDefinitionOrm.created_at))
    logger.debug("No version specified, ordering by creation date for latest.")

  result = await db.execute(stmt)
  protocol_def = result.scalar_one_or_none()
  if protocol_def:
    logger.info(
      "Found protocol definition '%s' (Version: %s).",
      protocol_def.name,
      protocol_def.version,
    )
  else:
    logger.info("Protocol definition '%s' not found with specified criteria.", name)
  return protocol_def


async def list_protocol_definitions(
  db: AsyncSession,
  limit: int = 100,
  offset: int = 0,
  source_name: Optional[str] = None,
  is_top_level: Optional[bool] = None,
  category: Optional[str] = None,
  tags: Optional[List[str]] = None,
  include_deprecated: bool = False,
) -> List[FunctionProtocolDefinitionOrm]:
  """List protocol definitions with various filtering and pagination options.

  Args:
      db (AsyncSession): The database session.
      limit (int, optional): The maximum number of results to return.
          Defaults to 100.
      offset (int, optional): The number of results to skip before returning.
          Defaults to 0.
      source_name (Optional[str], optional): Filter protocols by the name of
          their source repository or file system. Defaults to None.
      is_top_level (Optional[bool], optional): Filter protocols by whether
          they are considered top-level executable protocols. Defaults to None.
      category (Optional[str], optional): Filter protocols by their category.
          Defaults to None.
      tags (Optional[List[str]], optional): Filter protocols by a list of
          tags. Protocols must have all specified tags. Defaults to None.
      include_deprecated (bool, optional): Whether to include deprecated
          protocols in the results. Defaults to False.

  Returns:
      List[FunctionProtocolDefinitionOrm]: A list of protocol definition
      objects matching the criteria.

  """
  logger.info(
    "Listing protocol definitions with filters: source='%s', top_level=%s, "
    "category='%s', tags=%s, include_deprecated=%s, limit=%d, offset=%d.",
    source_name,
    is_top_level,
    category,
    tags,
    include_deprecated,
    limit,
    offset,
  )
  stmt = select(FunctionProtocolDefinitionOrm).options(
    selectinload(FunctionProtocolDefinitionOrm.parameters),
    selectinload(FunctionProtocolDefinitionOrm.assets),
    joinedload(FunctionProtocolDefinitionOrm.source_repository),
    joinedload(FunctionProtocolDefinitionOrm.file_system_source),
  )

  if not include_deprecated:
    stmt = stmt.filter(~FunctionProtocolDefinitionOrm.deprecated)
    logger.debug("Excluding deprecated protocols.")

  if source_name:
    git_source_alias = aliased(ProtocolSourceRepositoryOrm)
    fs_source_alias = aliased(FileSystemProtocolSourceOrm)
    stmt = (
      stmt.outerjoin(
        git_source_alias,
        FunctionProtocolDefinitionOrm.source_repository_accession_id
        == git_source_alias.accession_id,
      )
      .outerjoin(
        fs_source_alias,
        FunctionProtocolDefinitionOrm.file_system_source_accession_id
        == fs_source_alias.accession_id,
      )
      .filter(
        or_(
          git_source_alias.name == source_name,
          fs_source_alias.name == source_name,
        )
      )
    )
    logger.debug("Filtering by source name: '%s'.", source_name)
  if is_top_level is not None:
    stmt = stmt.filter(FunctionProtocolDefinitionOrm.is_top_level == is_top_level)
    logger.debug("Filtering by is_top_level: %s.", is_top_level)
  if category:
    stmt = stmt.filter(FunctionProtocolDefinitionOrm.category == category)
    logger.debug("Filtering by category: '%s'.", category)
  if tags:
    for tag in tags:
      stmt = stmt.filter(FunctionProtocolDefinitionOrm.tags.op("?")(tag))
    logger.debug("Filtering by tags: %s.", tags)

  stmt = (
    stmt.order_by(
      desc(FunctionProtocolDefinitionOrm.name),
      desc(FunctionProtocolDefinitionOrm.version),
    )
    .limit(limit)
    .offset(offset)
  )
  result = await db.execute(stmt)
  protocol_defs = list(result.scalars().all())
  logger.info("Found %d protocol definitions.", len(protocol_defs))
  return protocol_defs


async def read_protocol_run_by_accession_id(
  db: AsyncSession, run_accession_id: uuid.UUID
) -> Optional[ProtocolRunOrm]:
  """Retrieve a protocol run by its unique GUID.

  This function fetches a `ProtocolRunOrm` by its GUID, including its
  associated function calls and their definitions.

  Args:
      db (AsyncSession): The database session.
      run_accession_id (uuid.UUID): The unique GUID of the protocol run.

  Returns:
      Optional[ProtocolRunOrm]: The protocol run object if found, otherwise None.

  """
  logger.info("Retrieving protocol run with GUID: '%s'.", run_accession_id)
  stmt = (
    select(ProtocolRunOrm)
    .options(
      selectinload(ProtocolRunOrm.function_calls)
      .selectinload(FunctionCallLogOrm.executed_function_definition)
      .selectinload(FunctionProtocolDefinitionOrm.source_repository),
      selectinload(ProtocolRunOrm.function_calls)
      .selectinload(FunctionCallLogOrm.executed_function_definition)
      .selectinload(FunctionProtocolDefinitionOrm.file_system_source),
      joinedload(ProtocolRunOrm.top_level_protocol_definition),
    )
    .filter(ProtocolRunOrm.run_accession_id == run_accession_id)
  )
  result = await db.execute(stmt)
  protocol_run = result.scalar_one_or_none()
  if protocol_run:
    logger.info("Found protocol run with GUID '%s'.", run_accession_id)
  else:
    logger.info("Protocol run with GUID '%s' not found.", run_accession_id)
  return protocol_run


async def list_protocol_runs(
  db: AsyncSession,
  limit: int = 100,
  offset: int = 0,
  protocol_definition_accession_id: Optional[uuid.UUID] = None,
  protocol_name: Optional[str] = None,
  status: Optional[ProtocolRunStatusEnum] = None,
) -> List[ProtocolRunOrm]:
  """List protocol runs with optional filtering and pagination.

  Args:
      db (AsyncSession): The database session.
      limit (int, optional): The maximum number of results to return.
          Defaults to 100.
      offset (int, optional): The number of results to skip before returning.
          Defaults to 0.
      protocol_definition_accession_id (Optional[uuid.UUID], optional): Filter runs by the ID
          of their top-level protocol definition. Defaults to None.
      protocol_name (Optional[str], optional): Filter runs by the name of
          their top-level protocol. Defaults to None.
      status (Optional[ProtocolRunStatusEnum], optional): Filter runs by their
          current status. Defaults to None.

  Returns:
      List[ProtocolRunOrm]: A list of protocol run objects matching the criteria.

  """
  logger.info(
    "Listing protocol runs with filters: def_accession_id=%s, name='%s', status=%s, "
    "limit=%d, offset=%d.",
    protocol_definition_accession_id,
    protocol_name,
    status,
    limit,
    offset,
  )
  stmt = select(ProtocolRunOrm).options(
    joinedload(ProtocolRunOrm.top_level_protocol_definition)
  )

  if protocol_definition_accession_id is not None:
    stmt = stmt.filter(
      ProtocolRunOrm.top_level_protocol_definition_accession_id
      == protocol_definition_accession_id
    )
    logger.debug(
      "Filtering by protocol definition ID: %d.",
      protocol_definition_accession_id,
    )
  if protocol_name is not None:
    stmt = stmt.join(
      FunctionProtocolDefinitionOrm,
      ProtocolRunOrm.top_level_protocol_definition_accession_id
      == FunctionProtocolDefinitionOrm.accession_id,
    ).filter(FunctionProtocolDefinitionOrm.name == protocol_name)
    logger.debug("Filtering by protocol name: '%s'.", protocol_name)
  if status is not None:
    stmt = stmt.filter(ProtocolRunOrm.status == status)
    logger.debug("Filtering by status: '%s'.", status.name)

  stmt = (
    stmt.order_by(desc(ProtocolRunOrm.start_time), desc(ProtocolRunOrm.accession_id))
    .limit(limit)
    .offset(offset)
  )
  result = await db.execute(stmt)
  protocol_runs = list(result.scalars().all())
  logger.info("Found %d protocol runs.", len(protocol_runs))
  return protocol_runs


async def read_function_call_logs_for_run(
  db: AsyncSession,
  protocol_run_accession_id: uuid.UUID,
) -> List[FunctionCallLogOrm]:
  """Retrieve all function call logs for a specific protocol run.

  Args:
      db (AsyncSession): The database session.
      protocol_run_accession_id (uuid.UUID): The ID of the protocol run to retrieve logs for.

  Returns:
      List[FunctionCallLogOrm]: A list of function call log objects, ordered
      by their sequence in the run. Returns an empty list if no logs are found.

  """
  logger.info(
    "Retrieving function call logs for protocol run ID: %s.",
    protocol_run_accession_id,
  )
  stmt = (
    select(FunctionCallLogOrm)
    .options(selectinload(FunctionCallLogOrm.executed_function_definition))
    .filter(FunctionCallLogOrm.protocol_run_accession_id == protocol_run_accession_id)
    .order_by(FunctionCallLogOrm.sequence_in_run)
  )
  result = await db.execute(stmt)
  function_calls = list(result.scalars().all())
  logger.info(
    "Found %d function call logs for protocol run ID %s.",
    len(function_calls),
    protocol_run_accession_id,
  )
  return function_calls


async def list_active_protocol_sources(
  db: AsyncSession,
  source_type: Optional[str] = None,
) -> List[Union[ProtocolSourceRepositoryOrm, FileSystemProtocolSourceOrm]]:
  """List all active protocol sources, optionally filtered by type.

  Args:
      db (AsyncSession): The database session.
      source_type (Optional[str], optional): Filter by source type ("git" or
          "filesystem"). If None, both types will be returned. Defaults to None.

  Returns:
      List[Union[ProtocolSourceRepositoryOrm, FileSystemProtocolSourceOrm]]:
      A list of active protocol source objects.

  """
  logger.info("Listing active protocol sources with type filter: %s.", source_type)
  results: List[Union[ProtocolSourceRepositoryOrm, FileSystemProtocolSourceOrm]] = []
  if source_type is None or source_type == "git":
    stmt_git = select(ProtocolSourceRepositoryOrm).filter(
      ProtocolSourceRepositoryOrm.status == ProtocolSourceStatusEnum.ACTIVE
    )
    result_git = await db.execute(stmt_git)
    git_sources = result_git.scalars().all()
    results.extend(git_sources)
    logger.debug("Found %d active Git sources.", len(git_sources))
  if source_type is None or source_type == "filesystem":
    stmt_fs = select(FileSystemProtocolSourceOrm).filter(
      FileSystemProtocolSourceOrm.status == ProtocolSourceStatusEnum.ACTIVE
    )
    result_fs = await db.execute(stmt_fs)
    fs_sources = result_fs.scalars().all()
    results.extend(fs_sources)
    logger.debug("Found %d active File System sources.", len(fs_sources))
  logger.info("Total active protocol sources found: %d.", len(results))
  return results
