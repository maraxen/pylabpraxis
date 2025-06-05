# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""Manage resource-related database interactions.

praxis/db_services/resource_data_service.py

Service layer for interacting with resource-related data in the database.
This includes Resource Definitions, Resource Instances, and their management.

"""

import datetime
from functools import partial
from typing import Any, Dict, List, Optional

import uuid_utils as uuid
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
  prefix="Resource Definition Error: Error while adding or updating resource definition\
    .",
  suffix=" Please ensure the parameters are correct and the resource definition exists\
    .",
)
async def add_or_update_resource_definition(
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
  """Add a new resource definition to the catalog or update an existing one.

  This function creates a new `ResourceDefinitionCatalogOrm` if no existing
  definition matches `name`. If a match is found, it
  updates the existing definition.

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
      ResourceDefinitionCatalogOrm: The created or updated resource definition
      object.

  Raises:
      ValueError: If an integrity error occurs (e.g., duplicate name).
      Exception: For any other unexpected errors during the process.

  """
  log_prefix = f"Resource Definition (Name: '{name}'):"
  logger.info("%s Attempting to add or update.", log_prefix)

  result = await db.execute(
    select(ResourceDefinitionCatalogOrm).filter(
      ResourceDefinitionCatalogOrm.name == name
    )
  )
  def_orm = result.scalar_one_or_none()

  if not def_orm:
    def_orm = ResourceDefinitionCatalogOrm(name=name)
    db.add(def_orm)
    logger.info("%s No existing definition found, creating new.", log_prefix)
  else:
    logger.info("%s Found existing definition, updating.", log_prefix)

  def_orm.python_fqn = python_fqn
  def_orm.resource_type = resource_type
  def_orm.description = description
  def_orm.is_consumable = is_consumable
  def_orm.nominal_volume_ul = nominal_volume_ul
  def_orm.material = material
  def_orm.manufacturer = manufacturer
  def_orm.plr_definition_details_json = plr_definition_details_json

  try:
    await db.commit()
    await db.refresh(def_orm)
    logger.info("%s Successfully committed changes.", log_prefix)
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"{log_prefix} Integrity error. A resource definition with this "
      f"name might already exist. Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception("%s Unexpected error. Rolling back.", log_prefix)
    raise e
  logger.info("%s Operation completed.", log_prefix)
  return def_orm


async def get_resource_definition(
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


async def get_resource_definition_by_name(
  db: AsyncSession, name: str
) -> Optional[ResourceDefinitionCatalogOrm]:
  """Retrieve a resource definition by its PyLabRobot definition name.

  This is an alias for `get_resource_definition`.

  Args:
      db (AsyncSession): The database session.
      name (str): The PyLabRobot definition name of the
          resource to retrieve.

  Returns:
      Optional[ResourceDefinitionCatalogOrm]: The resource definition object
      if found, otherwise None.

  """
  return await get_resource_definition(db, name)


async def get_resource_definition_by_fqn(
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
  def_orm = await get_resource_definition(db, name)
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


@log_resource_data_service_errors(
  prefix="Resource Instance Error: Error while adding resource instance.",
  suffix=" Please ensure the parameters are correct and the resource definition exists.\
    ",
)
async def add_resource_instance(
  db: AsyncSession,
  user_assigned_name: str,
  name: str,
  initial_status: ResourceInstanceStatusEnum = ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,  # noqa: E501
  lot_number: Optional[str] = None,
  expiry_date: Optional[datetime.datetime] = None,
  properties_json: Optional[Dict[str, Any]] = None,
  physical_location_description: Optional[str] = None,
  is_permanent_fixture: bool = False,
  is_machine: bool = False,
  machine_counterpart_id: Optional[uuid.UUID] = None,
  # Parameters for creating a new Machine if machine_counterpart_id is None
  machine_user_friendly_name: Optional[str] = None,
  machine_python_fqn: Optional[str] = None,
  machine_properties_json: Optional[Dict[str, Any]] = None,
  machine_current_status: Optional["MachineStatusEnum"] = None,  # type: ignore # noqa: F821
) -> ResourceInstanceOrm:
  """Add a new resource instance to the inventory.

  Args:
      db (AsyncSession): The database session.
      user_assigned_name (str): A unique, user-friendly name for the
          resource instance.
      name (str): The PyLabRobot definition name
          associated with this instance. This definition must exist in the
          catalog.
      initial_status (ResourceInstanceStatusEnum, optional): The initial
          status of the resource instance. Defaults to
          `ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE`.
      lot_number (Optional[str], optional): The lot number of the resource.
          Defaults to None.
      expiry_date (Optional[datetime.datetime], optional): The expiry date
          of the resource. Defaults to None.
      properties_json (Optional[Dict[str, Any]], optional): Additional
          properties for the resource instance as a JSON-serializable
          dictionary. Defaults to None.
      physical_location_description (Optional[str], optional): A description
          of the physical location of the resource. Defaults to None.
      is_permanent_fixture (bool, optional): Indicates if this resource
          instance is a permanent fixture (e.g., a deck). Defaults to False.
      is_machine (bool): True if this instance is a machine.
      machine_counterpart_id (Optional[int]): ID of the associated MachineOrm if this
      resource is a machine.
          If `is_machine` is True and this is None, a new MachineOrm will be created.
      machine_user_friendly_name (Optional[str]): Required if creating a new MachineOrm.
      machine_python_fqn (Optional[str]): Required if creating a new MachineOrm.
      machine_properties_json (Optional[Dict[str, Any]]): Optional properties for a new
      MachineOrm.
      machine_current_status (Optional[MachineStatusEnum]): Initial status for a new
      MachineOrm.


  Returns:
      ResourceInstanceOrm: The newly created resource instance object.

  Raises:
      ValueError: If the `name` is not found in the
          catalog, or if a resource instance with the same
          `user_assigned_name` already exists.
      Exception: For any other unexpected errors during the process.

  """
  from praxis.backend.models import MachineStatusEnum  # noqa: F401

  log_prefix = (
    f"Resource Instance (Name: '{user_assigned_name}', " f"Definition: '{name}'):"
  )
  logger.info("%s Attempting to add new resource instance.", log_prefix)

  definition = await get_resource_definition(db, name)
  if not definition:
    error_message = (
      f"{log_prefix} Resource definition '{name}' "
      "not found in catalog. Cannot add instance."
    )
    logger.error(error_message)
    raise ValueError(error_message)

  instance_orm = ResourceInstanceOrm(
    id=uuid.uuid7(),
    user_assigned_name=user_assigned_name,
    name=name,
    resource_definition=definition,
    current_status=initial_status,
    lot_number=lot_number,
    expiry_date=expiry_date,
    properties_json=properties_json,
    physical_location_description=physical_location_description,
    is_permanent_fixture=is_permanent_fixture,
  )
  db.add(instance_orm)
  await db.flush()

  try:
    await _create_or_link_machine_counterpart_for_resource(
      db=db,
      resource_instance_orm=instance_orm,
      is_machine=is_machine,
      machine_counterpart_id=machine_counterpart_id,
      machine_user_friendly_name=machine_user_friendly_name,
      machine_python_fqn=machine_python_fqn,
      machine_properties_json=machine_properties_json,
      machine_current_status=machine_current_status,
    )
  except Exception as e:
    logger.error(
      f"{log_prefix} Error linking MachineOrm counterpart: {e}", exc_info=True
    )
    raise ValueError(
      f"Failed to link machine counterpart for resource instance '{user_assigned_name}'."
    ) from e

  try:
    await db.commit()
    await db.refresh(instance_orm)
    if instance_orm.machine_counterpart:
      await db.refresh(instance_orm.machine_counterpart)
    logger.info(
      "%s Successfully added resource instance (ID: %s).",
      log_prefix,
      instance_orm.id,
    )
  except IntegrityError as e:
    await db.rollback()
    raise ValueError(
      f"{log_prefix} Integrity error. A resource instance with name "
      f"'{user_assigned_name}' might already exist. Details: {e}"
    ) from e
  except Exception as e:
    await db.rollback()
    logger.exception("%s Unexpected error. Rolling back.", log_prefix)
    raise e
  return instance_orm


async def get_resource_instance_by_id(
  db: AsyncSession, instance_id: uuid.UUID
) -> Optional[ResourceInstanceOrm]:
  """Retrieve a resource instance by its ID.

  Args:
      db (AsyncSession): The database session.
      instance_id (uuid.UUID): The ID of the resource instance to retrieve.

  Returns:
      Optional[ResourceInstanceOrm]: The resource instance object if found,
      otherwise None.

  """
  logger.info("Retrieving resource instance with ID: %s.", instance_id)
  stmt = (
    select(ResourceInstanceOrm)
    .options(
      joinedload(ResourceInstanceOrm.resource_definition),
      joinedload(ResourceInstanceOrm.location_machine),
      joinedload(ResourceInstanceOrm.machine_counterpart),
    )
    .filter(ResourceInstanceOrm.id == instance_id)
  )
  result = await db.execute(stmt)
  instance = result.scalar_one_or_none()
  if instance:
    logger.info(
      "Found resource instance ID %s: '%s'.",
      instance_id,
      instance.user_assigned_name,
    )
  else:
    logger.info("Resource instance ID %d not found.", instance_id)
  return instance


async def get_resource_instance_by_name(
  db: AsyncSession, user_assigned_name: str
) -> Optional[ResourceInstanceOrm]:
  """Retrieve a resource instance by its user-assigned name.

  Args:
      db (AsyncSession): The database session.
      user_assigned_name (str): The user-assigned name of the resource
          instance to retrieve.

  Returns:
      Optional[ResourceInstanceOrm]: The resource instance object if found,
      otherwise None.

  """
  logger.info(
    "Retrieving resource instance by user-assigned name: '%s'.",
    user_assigned_name,
  )
  stmt = (
    select(ResourceInstanceOrm)
    .options(
      joinedload(ResourceInstanceOrm.resource_definition),
      joinedload(ResourceInstanceOrm.location_machine),
      joinedload(ResourceInstanceOrm.machine_counterpart),
    )
    .filter(ResourceInstanceOrm.user_assigned_name == user_assigned_name)
  )
  result = await db.execute(stmt)
  instance = result.scalar_one_or_none()
  if instance:
    logger.info("Found resource instance '%s'.", user_assigned_name)
  else:
    logger.info("Resource instance '%s' not found.", user_assigned_name)
  return instance


async def list_resource_instances(
  db: AsyncSession,
  name: Optional[str] = None,
  status: Optional[ResourceInstanceStatusEnum] = None,
  location_machine_id: Optional[uuid.UUID] = None,
  on_deck_position: Optional[str] = None,
  property_filters: Optional[Dict[str, Any]] = None,  # Added parameter
  current_protocol_run_guid_filter: Optional[str] = None,  # Added parameter
  limit: int = 100,
  offset: int = 0,
) -> List[ResourceInstanceOrm]:
  """List resource instances with optional filtering and pagination.

  Args:
      db (AsyncSession): The database session.
      name (Optional[str], optional): Filter instances
          by their PyLabRobot definition name. Defaults to None.
      status (Optional[ResourceInstanceStatusEnum], optional): Filter instances
          by their current status. Defaults to None.
      location_machine_id (Optional[uuid.UUID], optional): Filter instances by the
          ID of the machine they are currently located on. Defaults to None.
      on_deck_position (Optional[str], optional): Filter instances by the name of
          the deck position they are currently in. Defaults to None.
      property_filters (Optional[Dict[str, Any]], optional): Filter instances
          by properties contained within their JSONB `properties_json` field.
          Defaults to None.
      current_protocol_run_guid_filter (Optional[str], optional): Filter instances
          by the GUID of the protocol run they are currently associated with.
          Defaults to None.
      limit (int): The maximum number of results to return. Defaults to 100.
      offset (int): The number of results to skip before returning. Defaults to 0.

  Returns:
      List[ResourceInstanceOrm]: A list of resource instance objects matching
      the criteria.

  """
  logger.info(
    "Listing resource instances with filters: def_name='%s', status=%s, "
    "machine_id=%s, deck_position='%s', property_filters=%s, run_guid_filter=%s, "
    "limit=%d, offset=%d.",
    name,
    status,
    location_machine_id,
    on_deck_position,
    property_filters,
    current_protocol_run_guid_filter,
    limit,
    offset,
  )
  stmt = select(ResourceInstanceOrm).options(
    joinedload(ResourceInstanceOrm.resource_definition),
    joinedload(ResourceInstanceOrm.location_machine),
    joinedload(ResourceInstanceOrm.machine_counterpart),
  )
  if name:
    stmt = stmt.filter(ResourceInstanceOrm.name == name)
    logger.debug("Filtering by definition name: '%s'.", name)
  if status:
    stmt = stmt.filter(ResourceInstanceOrm.current_status == status)
    logger.debug("Filtering by status: '%s'.", status.name)
  if location_machine_id:
    stmt = stmt.filter(ResourceInstanceOrm.location_machine_id == location_machine_id)
    logger.debug("Filtering by location machine ID: %d.", location_machine_id)
  if on_deck_position:
    stmt = stmt.filter(
      ResourceInstanceOrm.current_deck_position_name == on_deck_position
    )
    logger.debug("Filtering by deck position: '%s'.", on_deck_position)
  if property_filters:
    # This assumes a simple key-value equality check for top-level JSONB properties
    # For more complex queries, you'd need to use JSONB operators
    # (e.g., .op('?') or .op('@>'))
    for key, value in property_filters.items():
      stmt = stmt.filter(ResourceInstanceOrm.properties_json[key].astext == str(value))
    logger.debug("Filtering by properties: %s.", property_filters)
  if current_protocol_run_guid_filter:
    stmt = stmt.filter(
      ResourceInstanceOrm.current_protocol_run_guid == current_protocol_run_guid_filter
    )
    logger.debug(
      "Filtering by current_protocol_run_guid: %s.", current_protocol_run_guid_filter
    )

  stmt = (
    stmt.order_by(ResourceInstanceOrm.user_assigned_name).limit(limit).offset(offset)
  )
  result = await db.execute(stmt)
  instances = list(result.scalars().all())
  logger.info("Found %d resource instances.", len(instances))
  return instances


async def update_resource_instance_location_and_status(
  db: AsyncSession,
  resource_instance_id: uuid.UUID,
  new_status: Optional[ResourceInstanceStatusEnum] = None,
  location_machine_id: Optional[uuid.UUID] = None,
  current_deck_position_name: Optional[str] = None,
  physical_location_description: Optional[str] = None,
  properties_json_update: Optional[Dict[str, Any]] = None,
  current_protocol_run_guid: Optional[uuid.UUID] = None,
  status_details: Optional[str] = None,
) -> Optional[ResourceInstanceOrm]:
  """Update the location, status, and other details of a resource instance.

  Args:
      db (AsyncSession): The database session.
      resource_instance_id (uuid.UUID): The ID of the resource instance to update.
      new_status (Optional[ResourceInstanceStatusEnum], optional): The new
          status for the resource instance. Defaults to None.
      location_machine_id (Optional[uuid.UUID], optional): The ID of the machine
          where the resource is now located. Defaults to None.
      current_deck_position_name (Optional[str], optional): The name of the deck
          position where the resource is now located. Defaults to None.
      physical_location_description (Optional[str], optional): An updated
          description of the physical location. Defaults to None.
      properties_json_update (Optional[Dict[str, Any]], optional): A dictionary
          of properties to merge into the existing `properties_json`.
          Defaults to None.
      current_protocol_run_guid (Optional[uuid.UUID], optional): The GUID of the
          protocol run currently using this resource. If the status is changing
          to `IN_USE`, this should be provided. If the status is changing
          from `IN_USE`, this will be cleared. Defaults to None.
      status_details (Optional[str], optional): Additional details about the
          current status. Defaults to None.

  Returns:
      Optional[ResourceInstanceOrm]: The updated resource instance object if
      found, otherwise None.

  Raises:
      Exception: For any unexpected errors during the process.

  """
  logger.info(
    "Updating resource instance ID %d: new_status=%s, machine_id=%s, "
    "deck_position='%s'.",
    resource_instance_id,
    new_status,
    location_machine_id,
    current_deck_position_name,
  )
  instance_orm = await get_resource_instance_by_id(db, resource_instance_id)
  if instance_orm:
    if new_status is not None:
      logger.debug(
        "Instance ID %d status changing from '%s' to '%s'.",
        resource_instance_id,
        instance_orm.current_status.name,
        new_status.name,
      )
      instance_orm.current_status = new_status

    # Update location fields if any are provided
    if (
      location_machine_id is not None
      or current_deck_position_name is not None
      or physical_location_description is not None
    ):
      logger.debug(
        "Instance ID %d location update: machine_id=%s, deck_position='%s', "
        "physical_desc='%s'.",
        resource_instance_id,
        location_machine_id,
        current_deck_position_name,
        physical_location_description,
      )

      instance_orm.location_machine_id = location_machine_id
      instance_orm.current_deck_position_name = current_deck_position_name
      instance_orm.physical_location_description = physical_location_description

    if status_details is not None:
      logger.debug("Instance ID %d status details updated.", resource_instance_id)
      instance_orm.status_details = status_details

    if (
      new_status == ResourceInstanceStatusEnum.IN_USE
      and current_protocol_run_guid is not None
    ):
      logger.debug(
        "Instance ID %d set to IN_USE with protocol run GUID: %s.",
        resource_instance_id,
        current_protocol_run_guid,
      )
      instance_orm.current_protocol_run_guid = current_protocol_run_guid
    elif new_status != ResourceInstanceStatusEnum.IN_USE:
      if instance_orm.current_protocol_run_guid is not None:
        logger.debug("Instance ID %d protocol run GUID cleared.", resource_instance_id)
        instance_orm.current_protocol_run_guid = None

    if properties_json_update is not None:
      logger.debug("Instance ID %d properties updated.", resource_instance_id)
      # Merge existing properties with new ones
      existing_properties = instance_orm.properties_json or {}
      existing_properties.update(properties_json_update)
      instance_orm.properties_json = existing_properties
      # Mark as modified for SQLAlchemy to detect changes in JSONB
      flag_modified(instance_orm, "properties_json")

    try:
      await db.commit()
      await db.refresh(instance_orm)
      logger.info("Successfully updated resource instance ID %d.", resource_instance_id)
    except Exception as e:
      await db.rollback()
      logger.exception(
        "Unexpected error updating resource instance ID %d. Rolling back.",
        resource_instance_id,
      )
      raise e
    return instance_orm
  logger.warning("Resource instance ID %d not found for update.", resource_instance_id)
  return None


async def delete_resource_instance(db: AsyncSession, instance_id: int) -> bool:
  """Delete a specific resource instance.

  Args:
      db (AsyncSession): The database session.
      instance_id (int): The ID of the resource instance to delete.

  Returns:
      bool: True if the deletion was successful, False if the instance was
      not found.

  Raises:
      ValueError: If the instance cannot be deleted due to existing foreign
          key references (IntegrityError).
      Exception: For any other unexpected errors during deletion.

  """
  logger.info("Attempting to delete resource instance with ID: %d.", instance_id)
  stmt = select(ResourceInstanceOrm).filter(ResourceInstanceOrm.id == instance_id)
  result = await db.execute(stmt)
  instance_orm = result.scalar_one_or_none()

  if not instance_orm:
    logger.warning("Resource instance ID %d not found for deletion.", instance_id)
    return False

  try:
    await db.delete(instance_orm)
    await db.commit()
    logger.info("Successfully deleted resource instance ID %d.", instance_id)
    return True
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Cannot delete resource instance ID {instance_id} due to existing "
      f"references (e.g., in deck layouts). Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error deleting resource instance ID %d. Rolling back.",
      instance_id,
    )
    raise e
