# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""Manage resource-related database interactions.

praxis/db_services/resource_data_service.py

Service layer for interacting with resource-related data in the database.
This includes Resource Definitions, Resource Instances, and their management.

"""

import datetime
from functools import partial
from typing import Any, Dict, List, Optional

import uuid
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.attributes import flag_modified

from praxis.backend.models import (
  ResourceDefinitionCatalogOrm,
  ResourceInstanceOrm,
  ResourceInstanceStatusEnum,
)
from praxis.backend.services.entity_linking import (
  _create_or_link_machine_counterpart_for_resource,
)
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)


log_resource_data_service_errors = partial(
  log_async_runtime_errors,
  logger_instance=logger,
  exception_type=ValueError,
  raises=True,
  raises_exception=ValueError,
)


@log_resource_data_service_errors(
  prefix="Resource Definition Error: Creating resource definition - ",
  suffix=" Please ensure the parameters are correct and the resource definition does "
  "not already exist.",
)
async def create_resource_definition(
  db: AsyncSession,
  name: str,
  python_fqn: str,
  resource_type: Optional[str] = None,
  description: Optional[str] = None,
  is_consumable: bool = True,
  nominal_volume_ul: Optional[float] = None,
  material: Optional[str] = None,
  manufacturer: Optional[str] = None,
  plr_definition_details_json: Optional[Dict[str, Any]] = None,
) -> ResourceDefinitionCatalogOrm:
  """Add a new resource definition to the catalog.

  This function creates a new `ResourceDefinitionCatalogOrm`.

  Args:
      db (AsyncSession): The database session.
      name (str): The unique PyLabRobot definition name
          for the resource (e.g., "tip_rack_1000ul").
      python_fqn (str): The fully qualified Python name of the resource class.
      resource_type (Optional[str], optional): A human-readable
          name for the resource type. Defaults to None.
      description (Optional[str], optional): A description of the resource.
          Defaults to None.
      is_consumable (bool, optional): Indicates if the resource is consumable.
          Defaults to True.
      nominal_volume_ul (Optional[float], optional): The nominal volume in
          microliters, if applicable. Defaults to None.
      material (Optional[str], optional): The material of the resource.
          Defaults to None.
      manufacturer (Optional[str], optional): The manufacturer of the resource.
          Defaults to None.
      plr_definition_details_json (Optional[Dict[str, Any]], optional):
          Additional PyLabRobot specific definition details as a JSON-serializable
          dictionary. Defaults to None.

  Returns:
      ResourceDefinitionCatalogOrm: The created resource definition object.

  Raises:
      ValueError: If a resource definition with the same `name` already exists.
      Exception: For any other unexpected errors during the process.

  """
  log_prefix = f"Resource Definition (Name: '{name}', creating new):"
  logger.info("%s Attempting to create new resource definition.", log_prefix)

  # Check if a resource definition with this name already exists
  result = await db.execute(
    select(ResourceDefinitionCatalogOrm).filter(
      ResourceDefinitionCatalogOrm.name == name
    )
  )
  if result.scalar_one_or_none():
    error_message = (
      f"{log_prefix} A resource definition with name "
      f"'{name}' already exists. Use the update function for existing definitions."
    )
    logger.error(error_message)
    raise ValueError(error_message)

  # Create a new ResourceDefinitionCatalogOrm
  def_orm = ResourceDefinitionCatalogOrm(
    name=name,
    python_fqn=python_fqn,
    resource_type=resource_type,
    description=description,
    is_consumable=is_consumable,
    nominal_volume_ul=nominal_volume_ul,
    material=material,
    manufacturer=manufacturer,
    plr_definition_details_json=plr_definition_details_json,
  )
  db.add(def_orm)
  logger.info("%s Initialized new resource definition for creation.", log_prefix)

  try:
    await db.commit()
    await db.refresh(def_orm)
    logger.info("%s Successfully committed new resource definition.", log_prefix)
  except IntegrityError as e:
    await db.rollback()
    if "uq_resource_definitions_name" in str(
      e.orig
    ):  # Placeholder for actual constraint name
      error_message = (
        f"{log_prefix} A resource definition with name "
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
  return def_orm


@log_resource_data_service_errors(
  prefix="Resource Definition Error: Updating resource definition - ",
  suffix=" Please ensure the parameters are correct and the resource definition exists.",
)
async def update_resource_definition(
  db: AsyncSession,
  name: str,  # Identifier for the resource definition to update
  python_fqn: Optional[str] = None,
  resource_type: Optional[str] = None,
  description: Optional[str] = None,
  is_consumable: Optional[bool] = None,
  nominal_volume_ul: Optional[float] = None,
  material: Optional[str] = None,
  manufacturer: Optional[str] = None,
  plr_definition_details_json: Optional[Dict[str, Any]] = None,
) -> ResourceDefinitionCatalogOrm:
  """Update an existing resource definition in the catalog.

  Args:
      db (AsyncSession): The database session.
      name (str): The unique PyLabRobot definition name
          for the resource to update (e.g., "tip_rack_1000ul").
      python_fqn (Optional[str], optional): The fully qualified Python name of the resource class.
          Defaults to None.
      resource_type (Optional[str], optional): A human-readable
          name for the resource type. Defaults to None.
      description (Optional[str], optional): A description of the resource.
          Defaults to None.
      is_consumable (Optional[bool], optional): Indicates if the resource is consumable.
          Defaults to None.
      nominal_volume_ul (Optional[float], optional): The nominal volume in
          microliters, if applicable. Defaults to None.
      material (Optional[str], optional): The material of the resource.
          Defaults to None.
      manufacturer (Optional[str], optional): The manufacturer of the resource.
          Defaults to None.
      plr_definition_details_json (Optional[Dict[str, Any]], optional):
          Additional PyLabRobot specific definition details as a JSON-serializable
          dictionary. Defaults to None.

  Returns:
      ResourceDefinitionCatalogOrm: The updated resource definition object.

  Raises:
      ValueError: If the resource definition with the provided `name` is not found,
                  or if an integrity error occurs (e.g., duplicate FQN if `python_fqn` is changed).
      Exception: For any other unexpected errors during the process.

  """
  log_prefix = f"Resource Definition (Name: '{name}', updating):"
  logger.info("%s Attempting to update.", log_prefix)

  # Fetch the existing resource definition
  result = await db.execute(
    select(ResourceDefinitionCatalogOrm).filter(
      ResourceDefinitionCatalogOrm.name == name
    )
  )
  def_orm = result.scalar_one_or_none()

  if not def_orm:
    error_message = f"{log_prefix} ResourceDefinitionCatalogOrm with name '{name}' not found for update."
    logger.error(error_message)
    raise ValueError(error_message)
  logger.info("%s Found existing definition for update.", log_prefix)

  # Update attributes if provided
  if python_fqn is not None:
    def_orm.python_fqn = python_fqn
  if resource_type is not None:
    def_orm.resource_type = resource_type
  if description is not None:
    def_orm.description = description
  if is_consumable is not None:
    def_orm.is_consumable = is_consumable
  if nominal_volume_ul is not None:
    def_orm.nominal_volume_ul = nominal_volume_ul
  if material is not None:
    def_orm.material = material
  if manufacturer is not None:
    def_orm.manufacturer = manufacturer
  if plr_definition_details_json is not None:
    def_orm.plr_definition_details_json = plr_definition_details_json
    flag_modified(def_orm, "plr_definition_details_json")  # Flag as modified

  try:
    await db.commit()
    await db.refresh(def_orm)
    logger.info("%s Successfully committed update.", log_prefix)
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"{log_prefix} Integrity error during update. "
      f"This might occur if a unique constraint is violated (e.g., duplicate FQN). Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception("%s Unexpected error during update. Rolling back.", log_prefix)
    raise e

  logger.info("%s Update operation completed.", log_prefix)
  return def_orm


async def read_resource_definition(
  db: AsyncSession, name: str
) -> Optional[ResourceDefinitionCatalogOrm]:
  """Retrieve a resource definition by its PyLabRobot definition name.

  Args:
      db (AsyncSession): The database session.
      name (str): The PyLabRobot definition name of the
          resource to retrieve.

  Returns:
      Optional[ResourceDefinitionCatalogOrm]: The resource definition object
      if found, otherwise None.

  """
  logger.info(
    "Retrieving resource definition by PyLabRobot name: '%s'.",
    name,
  )
  result = await db.execute(
    select(ResourceDefinitionCatalogOrm).filter(
      ResourceDefinitionCatalogOrm.name == name
    )
  )
  resource_def = result.scalar_one_or_none()
  if resource_def:
    logger.info("Found resource definition '%s'.", name)
  else:
    logger.info("Resource definition '%s' not found.", name)
  return resource_def


async def list_resource_definitions(
  db: AsyncSession,
  manufacturer: Optional[str] = None,
  is_consumable: Optional[bool] = None,
  limit: int = 100,
  offset: int = 0,
) -> List[ResourceDefinitionCatalogOrm]:
  """List resource definitions with optional filtering and pagination.

  Args:
      db (AsyncSession): The database session.
      manufacturer (Optional[str], optional): Filter definitions by manufacturer
          (case-insensitive partial match). Defaults to None.
      is_consumable (Optional[bool], optional): Filter definitions by whether
          they are consumable. Defaults to None.
      limit (int): The maximum number of results to return. Defaults to 100.
      offset (int): The number of results to skip before returning. Defaults to 0.

  Returns:
      List[ResourceDefinitionCatalogOrm]: A list of resource definition objects
      matching the criteria.

  """
  logger.info(
    "Listing resource definitions with filters: manufacturer='%s', "
    "is_consumable=%s, limit=%d, offset=%d.",
    manufacturer,
    is_consumable,
    limit,
    offset,
  )
  stmt = select(ResourceDefinitionCatalogOrm)
  if manufacturer:
    stmt = stmt.filter(
      ResourceDefinitionCatalogOrm.manufacturer.ilike(f"%{manufacturer}%")
    )
    logger.debug("Filtering by manufacturer: '%s'.", manufacturer)
  if is_consumable is not None:
    stmt = stmt.filter(ResourceDefinitionCatalogOrm.is_consumable == is_consumable)
    logger.debug("Filtering by is_consumable: %s.", is_consumable)
  stmt = stmt.order_by(ResourceDefinitionCatalogOrm.name).limit(limit).offset(offset)
  result = await db.execute(stmt)
  resource_defs = list(result.scalars().all())
  logger.info("Found %d resource definitions.", len(resource_defs))
  return resource_defs


async def read_resource_definition_by_name(
  db: AsyncSession, name: str
) -> Optional[ResourceDefinitionCatalogOrm]:
  """Retrieve a resource definition by its PyLabRobot definition name.

  This is an alias for `read_resource_definition`.

  Args:
      db (AsyncSession): The database session.
      name (str): The PyLabRobot definition name of the
          resource to retrieve.

  Returns:
      Optional[ResourceDefinitionCatalogOrm]: The resource definition object
      if found, otherwise None.

  """
  return await read_resource_definition(db, name)


async def read_resource_definition_by_fqn(
  db: AsyncSession, python_fqn: str
) -> Optional[ResourceDefinitionCatalogOrm]:
  """Retrieve a resource definition by its Python fully qualified name (FQN).

  Args:
      db (AsyncSession): The database session.
      python_fqn (str): The Python FQN of the resource to retrieve.

  Returns:
      Optional[ResourceDefinitionCatalogOrm]: The resource definition object
      if found, otherwise None.

  """
  logger.info("Retrieving resource definition by Python FQN: '%s'.", python_fqn)
  result = await db.execute(
    select(ResourceDefinitionCatalogOrm).filter(
      ResourceDefinitionCatalogOrm.python_fqn == python_fqn
    )
  )
  resource_def = result.scalar_one_or_none()
  if resource_def:
    logger.info("Found resource definition by FQN '%s'.", python_fqn)
  else:
    logger.info("Resource definition with FQN '%s' not found.", python_fqn)
  return resource_def


async def delete_resource_definition(db: AsyncSession, name: str) -> bool:
  """Delete a specific resource definition from the catalog.

  Args:
      db (AsyncSession): The database session.
      name (str): The PyLabRobot definition name of the
          resource to delete.

  Returns:
      bool: True if the deletion was successful, False if the definition was
      not found.

  Raises:
      ValueError: If the definition cannot be deleted due to existing foreign
          key references (IntegrityError).
      Exception: For any other unexpected errors during deletion.

  """
  logger.info("Attempting to delete resource definition: '%s'.", name)
  def_orm = await read_resource_definition(db, name)
  if not def_orm:
    logger.warning(
      "Resource definition '%s' not found for deletion.",
      name,
    )
    return False

  try:
    await db.delete(def_orm)
    await db.commit()
    logger.info(
      "Successfully deleted resource definition '%s'.",
      name,
    )
    return True
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Cannot delete resource definition '{name}' "
      f"due to existing references (e.g., resource instances). Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error deleting resource definition '%s'. Rolling back.",
      name,
    )
    raise e
