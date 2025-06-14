# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""Manage resource-related database interactions.

praxis/db_services/resource_data_service.py

Service layer for interacting with resource-related data in the database.
This includes Resource Definitions, Resource Instances, and their management.

"""

import datetime
import uuid
from functools import partial
from typing import Any, Dict, List, Optional


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
  synchronize_resource_machine_names,
)
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors
from praxis.backend.utils.uuid import uuid7

from .resource_type_definition import read_resource_definition

logger = get_logger(__name__)


log_resource_data_service_errors = partial(
  log_async_runtime_errors,
  logger_instance=logger,
  exception_type=ValueError,
  raises=True,
  raises_exception=ValueError,
)


@log_resource_data_service_errors(
  prefix="Resource Instance Error: Error while adding resource instance.",
  suffix=" Please ensure the parameters are correct and the resource definition exists.\
    ",
)
async def create_resource_instance(
  db: AsyncSession,
  user_assigned_name: str,
  python_fqn: str,
  resource_definition_accession_id: uuid.UUID,
  initial_status: ResourceInstanceStatusEnum = ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,  # noqa: E501
  lot_number: Optional[str] = None,
  expiry_date: Optional[datetime.datetime] = None,
  properties_json: Optional[Dict[str, Any]] = None,
  physical_location_description: Optional[str] = None,
  is_permanent_fixture: bool = False,
  is_machine: bool = False,
  machine_counterpart_accession_id: Optional[uuid.UUID] = None,
  # Parameters for creating a new Machine if machine_counterpart_accession_id is None
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
      python_fqn (str): The PyLabRobot definition name
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
      machine_counterpart_accession_id (Optional[int]): ID of the associated MachineOrm if this
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
    f"Resource Instance (Name: '{user_assigned_name}', " f"Definition: '{python_fqn}'):"
  )
  logger.info("%s Attempting to add new resource instance.", log_prefix)

  definition = await read_resource_definition(db, python_fqn)
  if not definition:
    error_message = (
      f"{log_prefix} Resource definition '{python_fqn}' "
      "not found in catalog. Cannot add instance."
    )
    logger.error(error_message)
    raise ValueError(error_message)

  instance_orm = ResourceInstanceOrm(
    accession_id=uuid7(),
    user_assigned_name=user_assigned_name,
    python_fqn=python_fqn,
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
      machine_counterpart_accession_id=machine_counterpart_accession_id,
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
      instance_orm.accession_id,
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


async def update_resource_instance(
  db: AsyncSession,
  instance_accession_id: uuid.UUID,
  user_assigned_name: Optional[str] = None,
  python_fqn: Optional[str] = None,
  lot_number: Optional[str] = None,
  expiry_date: Optional[datetime.datetime] = None,
  properties_json: Optional[Dict[str, Any]] = None,
  physical_location_description: Optional[str] = None,
  is_permanent_fixture: Optional[bool] = None,
  is_machine: Optional[bool] = None,
  machine_counterpart_accession_id: Optional[uuid.UUID] = None,
) -> Optional[ResourceInstanceOrm]:
  """Update an existing resource instance.

  Args:
    db (AsyncSession): The database session.
    instance_accession_id (uuid.UUID): The ID of the resource instance to update.
    user_assigned_name (Optional[str], optional): New user-assigned name for the
      resource instance. Defaults to None.
    python_fqn (Optional[str], optional): New PyLabRobot definition name for the
      resource instance. Defaults to None.
    lot_number (Optional[str], optional): New lot number for the resource.
      Defaults to None.
    expiry_date (Optional[datetime.datetime], optional): New expiry date
      for the resource. Defaults to None.
    properties_json (Optional[Dict[str, Any]], optional): New properties
      for the resource instance as a JSON-serializable dictionary. Defaults to None.
    physical_location_description (Optional[str], optional): New description
      of the physical location of the resource. Defaults to None.
    is_permanent_fixture (Optional[bool], optional): Indicates if this resource
      instance is a permanent fixture. Defaults to None.
    is_machine (Optional[bool]): True if this instance is a machine, False otherwise.
    machine_counterpart_accession_id (Optional[uuid.UUID]): ID of the associated MachineOrm if this
        resource is a machine.

  Returns:
    Optional[ResourceInstanceOrm]: The updated resource instance object if
    the update was successful, otherwise None.

  Raises:
    ValueError: If the resource instance with the given ID does not exist,
      or if an error occurs while updating the instance.
    Exception: For any other unexpected errors during the update process.

  """
  logger.info("Updating resource instance with ID: %s.", instance_accession_id)
  instance_orm = await read_resource_instance(db, instance_accession_id)
  if not instance_orm:
    logger.warning(
      "Resource instance with ID %s not found for update.", instance_accession_id
    )
    return None
  log_prefix = f"Resource Instance (ID: {instance_orm.accession_id}, Name: \
    {instance_orm.user_assigned_name}):"
  logger.info("%s Attempting to update resource instance.", log_prefix)
  # Update the fields of the resource instance as needed
  if user_assigned_name:
    instance_orm.user_assigned_name = user_assigned_name
    # Synchronize name with linked machine counterpart if it exists
    await synchronize_resource_machine_names(db, instance_orm, user_assigned_name)
  if python_fqn:
    instance_orm.python_fqn = python_fqn
  if lot_number:
    instance_orm.lot_number = lot_number
  if expiry_date:
    instance_orm.expiry_date = expiry_date
  if properties_json:
    instance_orm.properties_json = properties_json
  if physical_location_description:
    instance_orm.physical_location_description = physical_location_description
  if is_permanent_fixture:
    instance_orm.is_permanent_fixture = is_permanent_fixture
  if is_machine:
    instance_orm.is_machine = is_machine
  if machine_counterpart_accession_id:
    instance_orm.machine_counterpart_accession_id = machine_counterpart_accession_id
    # If the machine counterpart ID is provided, we assume it is being updated
    # and we need to ensure the machine counterpart is linked correctly.
  if machine_counterpart_accession_id is not None:
    try:
      logger.info(
        "%s Linking MachineOrm counterpart (ID: %s).",
        log_prefix,
        machine_counterpart_accession_id,
      )
      if not is_machine:
        logger.warning(
          "%s Machine counterpart ID provided but is_machine is False. "
          "This may lead to inconsistencies.",
          log_prefix,
        )
        is_machine = (
          True  # Ensure is_machine is True if a machine counterpart ID is provided
        )
      await _create_or_link_machine_counterpart_for_resource(
        db=db,
        resource_instance_orm=instance_orm,
        is_machine=is_machine,
        machine_counterpart_accession_id=machine_counterpart_accession_id,
      )
    except Exception as e:
      logger.error(
        f"{log_prefix} Error linking MachineOrm counterpart: {e}", exc_info=True
      )
      raise ValueError(
        f"Failed to link machine counterpart for resource instance "
        f"'{instance_orm.user_assigned_name}'."
      ) from e

  try:
    await db.commit()
    await db.refresh(instance_orm)
    logger.info("%s Successfully updated resource instance.", log_prefix)
  except Exception as e:
    await db.rollback()
    logger.error("%s Error updating resource instance: %s", log_prefix, e)
    raise

  return instance_orm


async def read_resource_instance(
  db: AsyncSession, instance_accession_id: uuid.UUID
) -> Optional[ResourceInstanceOrm]:
  """Retrieve a resource instance by its ID.

  Args:
      db (AsyncSession): The database session.
      instance_accession_id (uuid.UUID): The ID of the resource instance to retrieve.

  Returns:
      Optional[ResourceInstanceOrm]: The resource instance object if found,
      otherwise None.

  """
  logger.info("Retrieving resource instance with ID: %s.", instance_accession_id)
  stmt = (
    select(ResourceInstanceOrm)
    .options(
      joinedload(ResourceInstanceOrm.resource_definition),
      joinedload(ResourceInstanceOrm.location_machine),
      joinedload(ResourceInstanceOrm.machine_counterpart),
    )
    .filter(ResourceInstanceOrm.accession_id == instance_accession_id)
  )
  result = await db.execute(stmt)
  instance = result.scalar_one_or_none()
  if instance:
    logger.info(
      "Found resource instance ID %s: '%s'.",
      instance_accession_id,
      instance.user_assigned_name,
    )
  else:
    logger.info("Resource instance ID %d not found.", instance_accession_id)
  return instance


async def read_resource_instance_by_name(
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
  python_fqn: Optional[str] = None,
  status: Optional[ResourceInstanceStatusEnum] = None,
  location_machine_accession_id: Optional[uuid.UUID] = None,
  on_deck_position: Optional[str] = None,
  property_filters: Optional[Dict[str, Any]] = None,  # Added parameter
  current_protocol_run_accession_id_filter: Optional[str] = None,  # Added parameter
  limit: int = 100,
  offset: int = 0,
) -> List[ResourceInstanceOrm]:
  """List resource instances with optional filtering and pagination.

  Args:
      db (AsyncSession): The database session.
      python_fqn (Optional[str], optional): Filter instances
          by their PyLabRobot definition FQN. Defaults to None.
      status (Optional[ResourceInstanceStatusEnum], optional): Filter instances
          by their current status. Defaults to None.
      location_machine_accession_id (Optional[uuid.UUID], optional): Filter instances by the
          ID of the machine they are currently located on. Defaults to None.
      on_deck_position (Optional[str], optional): Filter instances by the name of
          the deck position they are currently in. Defaults to None.
      property_filters (Optional[Dict[str, Any]], optional): Filter instances
          by properties contained within their JSONB `properties_json` field.
          Defaults to None.
      current_protocol_run_accession_id_filter (Optional[str], optional): Filter instances
          by the GUID of the protocol run they are currently associated with.
          Defaults to None.
      limit (int): The maximum number of results to return. Defaults to 100.
      offset (int): The number of results to skip before returning. Defaults to 0.

  Returns:
      List[ResourceInstanceOrm]: A list of resource instance objects matching
      the criteria.

  """
  logger.info(
    "Listing resource instances with filters: python_fqn='%s', status=%s, "
    "machine_accession_id=%s, deck_position='%s', property_filters=%s, run_accession_id_filter=%s, "
    "limit=%d, offset=%d.",
    python_fqn,
    status,
    location_machine_accession_id,
    on_deck_position,
    property_filters,
    current_protocol_run_accession_id_filter,
    limit,
    offset,
  )
  stmt = select(ResourceInstanceOrm).options(
    joinedload(ResourceInstanceOrm.resource_definition),
    joinedload(ResourceInstanceOrm.location_machine),
    joinedload(ResourceInstanceOrm.machine_counterpart),
  )
  if python_fqn:
    stmt = stmt.filter(ResourceInstanceOrm.python_fqn == python_fqn)
    logger.debug("Filtering by definition FQN: '%s'.", python_fqn)
  if status:
    stmt = stmt.filter(ResourceInstanceOrm.current_status == status)
    logger.debug("Filtering by status: '%s'.", status.name)
  if location_machine_accession_id:
    stmt = stmt.filter(
      ResourceInstanceOrm.location_machine_accession_id == location_machine_accession_id
    )
    logger.debug("Filtering by location machine ID: %d.", location_machine_accession_id)
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
  if current_protocol_run_accession_id_filter:
    stmt = stmt.filter(
      ResourceInstanceOrm.current_protocol_run_accession_id
      == current_protocol_run_accession_id_filter
    )
    logger.debug(
      "Filtering by current_protocol_run_accession_id: %s.",
      current_protocol_run_accession_id_filter,
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
  resource_instance_accession_id: uuid.UUID,
  new_status: Optional[ResourceInstanceStatusEnum] = None,
  location_machine_accession_id: Optional[uuid.UUID] = None,
  current_deck_position_name: Optional[str] = None,  # TODO: perhaps change to uuid
  physical_location_description: Optional[str] = None,
  properties_json_update: Optional[Dict[str, Any]] = None,
  current_protocol_run_accession_id: Optional[uuid.UUID] = None,
  status_details: Optional[str] = None,
) -> Optional[ResourceInstanceOrm]:
  """Update the location, status, and other details of a resource instance.

  Args:
      db (AsyncSession): The database session.
      resource_instance_accession_id (uuid.UUID): The ID of the resource instance to update.
      new_status (Optional[ResourceInstanceStatusEnum], optional): The new
          status for the resource instance. Defaults to None.
      location_machine_accession_id (Optional[uuid.UUID], optional): The ID of the machine
          where the resource is now located. Defaults to None.
      current_deck_position_name (Optional[str], optional): The name of the deck
          position where the resource is now located. Defaults to None.
      current_deck_position_accession_id (Optional[uuid.UUID], optional): The ID of the deck
          position where the resource is now located. Defaults to None.
      physical_location_description (Optional[str], optional): An updated
          description of the physical location. Defaults to None.
      properties_json_update (Optional[Dict[str, Any]], optional): A dictionary
          of properties to merge into the existing `properties_json`.
          Defaults to None.
      current_protocol_run_accession_id (Optional[uuid.UUID], optional): The GUID of the
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
    "Updating resource instance ID %d: new_status=%s, machine_accession_id=%s, "
    "deck_position='%s'.",
    resource_instance_accession_id,
    new_status,
    location_machine_accession_id,
    current_deck_position_name,
  )
  instance_orm = await read_resource_instance(db, resource_instance_accession_id)
  if instance_orm:
    if new_status is not None:
      logger.debug(
        "Instance ID %d status changing from '%s' to '%s'.",
        resource_instance_accession_id,
        instance_orm.current_status.name,
        new_status.name,
      )
      instance_orm.current_status = new_status

    # Update location fields if any are provided
    if (
      location_machine_accession_id is not None
      or current_deck_position_name is not None
      or physical_location_description is not None
    ):
      logger.debug(
        "Instance ID %d location update: machine_accession_id=%s, deck_position='%s', "
        "physical_desc='%s'.",
        resource_instance_accession_id,
        location_machine_accession_id,
        current_deck_position_name,
        physical_location_description,
      )

      instance_orm.location_machine_accession_id = location_machine_accession_id
      instance_orm.current_deck_position_name = current_deck_position_name
      instance_orm.physical_location_description = physical_location_description

    if status_details is not None:
      logger.debug(
        "Instance ID %d status details updated.", resource_instance_accession_id
      )
      instance_orm.status_details = status_details

    if (
      new_status == ResourceInstanceStatusEnum.IN_USE
      and current_protocol_run_accession_id is not None
    ):
      logger.debug(
        "Instance ID %d set to IN_USE with protocol run GUID: %s.",
        resource_instance_accession_id,
        current_protocol_run_accession_id,
      )
      instance_orm.current_protocol_run_accession_id = current_protocol_run_accession_id
    elif new_status != ResourceInstanceStatusEnum.IN_USE:
      if instance_orm.current_protocol_run_accession_id is not None:
        logger.debug(
          "Instance ID %d protocol run GUID cleared.", resource_instance_accession_id
        )
        instance_orm.current_protocol_run_accession_id = None

    if properties_json_update is not None:
      logger.debug("Instance ID %d properties updated.", resource_instance_accession_id)
      # Merge existing properties with new ones
      existing_properties = instance_orm.properties_json or {}
      existing_properties.update(properties_json_update)
      instance_orm.properties_json = existing_properties
      # Mark as modified for SQLAlchemy to detect changes in JSONB
      flag_modified(instance_orm, "properties_json")

    try:
      await db.commit()
      await db.refresh(instance_orm)
      logger.info(
        "Successfully updated resource instance ID %d.", resource_instance_accession_id
      )
    except Exception as e:
      await db.rollback()
      logger.exception(
        "Unexpected error updating resource instance ID %d. Rolling back.",
        resource_instance_accession_id,
      )
      raise e
    return instance_orm
  logger.warning(
    "Resource instance ID %d not found for update.", resource_instance_accession_id
  )
  return None


async def delete_resource_instance(
  db: AsyncSession, instance_accession_id: uuid.UUID
) -> bool:
  """Delete a specific resource instance.

  Args:
      db (AsyncSession): The database session.
      instance_accession_id (uuid.UUID): The ID of the resource instance to delete.

  Returns:
      bool: True if the deletion was successful, False if the instance was
      not found.

  Raises:
      ValueError: If the instance cannot be deleted due to existing foreign
          key references (IntegrityError).
      Exception: For any other unexpected errors during deletion.

  """
  logger.info(
    "Attempting to delete resource instance with ID: %s.", instance_accession_id
  )
  stmt = select(ResourceInstanceOrm).filter(
    ResourceInstanceOrm.accession_id == instance_accession_id
  )
  result = await db.execute(stmt)
  instance_orm = result.scalar_one_or_none()

  if not instance_orm:
    logger.warning(
      "Resource instance ID %s not found for deletion.", instance_accession_id
    )
    return False

  try:
    await db.delete(instance_orm)
    await db.commit()
    logger.info("Successfully deleted resource instance ID %s.", instance_accession_id)
    return True
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Cannot delete resource instance ID {instance_accession_id} due to existing "
      f"references (e.g., in deck layouts). Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error deleting resource instance ID %d. Rolling back.",
      instance_accession_id,
    )
    raise e


async def delete_resource_instance_by_name(
  db: AsyncSession, user_assigned_name: str
) -> bool:
  """Delete a resource instance by its unique name.

  Args:
      db (AsyncSession): The database session.
      user_assigned_name (str): The unique name of the resource
          instance to delete.

  Returns:
      bool: True if the deletion was successful, False if the instance was
      not found.

  """
  logger.info(
    "Attempting to delete resource instance with name: '%s'.", user_assigned_name
  )
  instance_orm = await read_resource_instance_by_name(
    db, user_assigned_name=user_assigned_name
  )
  if not instance_orm:
    logger.warning(
      "Resource instance with name '%s' not found for deletion.",
      user_assigned_name,
    )
    return False
  try:
    await db.delete(instance_orm)
    await db.commit()
    logger.info(
      "Successfully deleted resource instance with name '%s'.",
      user_assigned_name,
    )
    return True
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Cannot delete resource instance '{user_assigned_name}' due to existing "
      f"references (e.g., in deck layouts). Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error deleting resource instance with name '%s'. Rolling back.",
      user_assigned_name,
    )
    raise e
