# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""Manage resource-related database interactions.

praxis/db_services/resource_data_service.py

Service layer for interacting with resource-related data in the database.
This includes Resource Definitions, Resource Instances, and their management.

"""

import uuid
from functools import partial
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.attributes import flag_modified

from praxis.backend.models.resource_orm import (
  ResourceOrm,
  ResourceStatusEnum,
)  # Ensure correct import path and symbol names
from praxis.backend.models.resource_pydantic_models import ResourceCreate
from praxis.backend.services.entity_linking import (
  _create_or_link_machine_counterpart_for_resource,
  synchronize_resource_machine_names,
)
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors
from praxis.backend.utils.uuid import uuid7

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
  db: AsyncSession, resource_create: ResourceCreate
) -> ResourceOrm:
  """Add a new resource instance to the inventory.

  Args:
      db (AsyncSession): The database session.
      resource_create (ResourceCreate): Pydantic model with resource instance data.

  Returns:
      ResourceOrm: The newly created resource instance object.

  Raises:
      ValueError: If the `name` is not found in the
          catalog, or if a resource instance with the same
          `user_assigned_name` already exists.
      Exception: For any other unexpected errors during the process.

  """
  from praxis.backend.models import (  # pylint: disable=import-outside-toplevel
    MachineStatusEnum,
  )

  log_prefix = (
    f"Resource Instance (Name: '{resource_create.name}', FQN: '{resource_create.fqn}'):"
  )
  logger.info("%s Attempting to add new resource instance.", log_prefix)

  # The resource definition is linked by resource_definition_id in the resource_create model
  # and handled by the ORM relationships. No need to fetch it manually.

  instance_orm = ResourceOrm(
    **resource_create.model_dump(
      exclude={"machine_counterpart_id", "resource_definition_id"}
    )
  )
  instance_orm.accession_id = uuid7()
  instance_orm.resource_definition_id = resource_create.resource_definition_id

  db.add(instance_orm)
  await db.flush()

  try:
    # Since we are creating a resource that can be a machine, we might need to create
    # or link a machine counterpart.
    await _create_or_link_machine_counterpart_for_resource(
      db=db,
      resource_instance_orm=instance_orm,
      is_machine=resource_create.asset_type
      in ["MACHINE", "MACHINE_RESOURCE"],  # Simplified check
      machine_counterpart_accession_id=resource_create.machine_counterpart_id,
      # The following parameters are for creating a new machine if needed.
      # They should be part of the resource_create model if we want to support this flow.
      # For now, we assume linking to an existing machine or no machine counterpart.
      machine_user_friendly_name=resource_create.name,  # Synchronize names
      machine_python_fqn=resource_create.fqn,
      machine_properties_json=resource_create.properties_json,
      machine_current_status=MachineStatusEnum.AVAILABLE,  # Default status
    )
  except Exception as e:
    logger.error(
      f"{log_prefix} Error linking MachineOrm counterpart: {e}", exc_info=True
    )
    raise ValueError(
      "Failed to link machine counterpart for resource instance "
      f"'{resource_create.name}'."
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
      f"'{resource_create.name}' might already exist. Details: {e}"
    ) from e
  except Exception as e:
    await db.rollback()
    logger.exception("%s Unexpected error. Rolling back.", log_prefix)
    raise e
  return instance_orm


async def update_resource_instance(
  db: AsyncSession,
  instance_accession_id: uuid.UUID,
  resource_update: ResourceUpdate,
) -> Optional[ResourceOrm]:
  """Update an existing resource instance.

  Args:
      db (AsyncSession): The database session.
      instance_accession_id (uuid.UUID): The accession ID of the resource instance to update.
      resource_update (ResourceUpdate): Pydantic model with updated data.

  Returns:
      Optional[ResourceOrm]: The updated resource instance object, or None if not found.

  """
  log_prefix = f"Resource Instance (ID: {instance_accession_id}):"
  logger.info("%s Attempting to update resource instance.", log_prefix)

  instance = await get_resource_instance(db, instance_accession_id)
  if not instance:
    logger.warning("%s Resource instance not found.", log_prefix)
    return None

  update_data = resource_update.model_dump(exclude_unset=True)
  for key, value in update_data.items():
    if hasattr(instance, key):
      setattr(instance, key, value)

  # Special handling for properties_json to ensure modifications are tracked
  if "properties_json" in update_data:
    flag_modified(instance, "properties_json")

  # Synchronize names if the name is updated
  if "name" in update_data and (
    instance.machine_counterpart or instance.deck_counterpart
  ):
    await synchronize_resource_machine_names(db, instance)

  try:
    await db.commit()
    await db.refresh(instance)
    logger.info("%s Successfully updated resource instance.", log_prefix)
  except IntegrityError as e:
    await db.rollback()
    raise ValueError(f"{log_prefix} Integrity error during update. Details: {e}") from e
  except Exception as e:
    await db.rollback()
    logger.exception("%s Unexpected error during update. Rolling back.", log_prefix)
    raise e

  return instance


async def get_resource_instance(
  db: AsyncSession, instance_accession_id: uuid.UUID
) -> Optional[ResourceOrm]:
  """Retrieve a resource instance by its ID.

  Args:
      db (AsyncSession): The database session.
      instance_accession_id (uuid.UUID): The ID of the resource instance to retrieve.

  Returns:
      Optional[ResourceOrm]: The resource instance object if found,
      otherwise None.

  """
  logger.info("Retrieving resource instance with ID: %s.", instance_accession_id)
  stmt = (
    select(ResourceOrm)
    .options(
      joinedload(ResourceOrm.resource_definition),
      joinedload(ResourceOrm.machine_counterpart),
    )
    .filter(ResourceOrm.accession_id == instance_accession_id)
  )
  result = await db.execute(stmt)
  instance = result.scalar_one_or_none()
  if instance:
    logger.info(
      "Found resource instance ID %s: '%s'.",
      instance_accession_id,
      instance.name,
    )
  else:
    logger.info("Resource instance ID %d not found.", instance_accession_id)
  return instance


async def read_resource_instance_by_name(
  db: AsyncSession, name: str
) -> Optional[ResourceOrm]:
  """Retrieve a resource instance by its name.

  Args:
      db (AsyncSession): The database session.
      name (str): The name of the resource instance to retrieve.

  Returns:
      Optional[ResourceOrm]: The resource instance object if found,
      otherwise None.

  """
  logger.info("Retrieving resource instance by name: '%s'.", name)
  stmt = (
    select(ResourceOrm)
    .options(
      joinedload(ResourceOrm.resource_definition),
      joinedload(ResourceOrm.machine_counterpart),
    )
    .filter(ResourceOrm.name == name)
  )
  result = await db.execute(stmt)
  instance = result.scalar_one_or_none()
  if instance:
    logger.info("Found resource instance '%s'.", name)
  else:
    logger.info("Resource instance '%s' not found.", name)
  return instance


async def list_resource_instances(
  db: AsyncSession,
  status: Optional[ResourceStatusEnum] = None,
  property_filters: Optional[Dict[str, Any]] = None,  # Added parameter
  limit: int = 100,
  offset: int = 0,
) -> List[ResourceOrm]:
  """List resource instances with optional filtering and pagination.

  Args:
      db (AsyncSession): The database session.
      status (Optional[ResourceStatusEnum], optional): Filter instances
          by their current status. Defaults to None.
      property_filters (Optional[Dict[str, Any]], optional): Filter instances
          by properties contained within their JSONB `properties_json` field.
          Defaults to None.
      limit (int): The maximum number of results to return. Defaults to 100.
      offset (int): The number of results to skip before returning. Defaults to 0.

  Returns:
      List[ResourceOrm]: A list of resource instance objects matching
      the criteria.

  """
  logger.info(
    "Listing resource instances with filters: status=%s, property_filters=%s, "
    "limit=%d, offset=%d.",
    status,
    property_filters,
    limit,
    offset,
  )
  stmt = select(ResourceOrm).options(
    joinedload(ResourceOrm.resource_definition),
    joinedload(ResourceOrm.machine_counterpart),
  )
  if status:
    stmt = stmt.filter(ResourceOrm.current_status == status)
    logger.debug("Filtering by status: '%s'.", status.name)
  if property_filters:
    # This assumes a simple key-value equality check for top-level JSONB properties
    # For more complex queries, you'd need to use JSONB operators
    # (e.g., .op('?') or .op('@>'))
    for key, value in property_filters.items():
      stmt = stmt.filter(ResourceOrm.properties_json[key].astext == str(value))
    logger.debug("Filtering by properties: %s.", property_filters)

  stmt = stmt.order_by(ResourceOrm.name).limit(limit).offset(offset)
  result = await db.execute(stmt)
  instances = list(result.scalars().all())
  logger.info("Found %d resource instances.", len(instances))
  return instances


async def update_resource_instance_location_and_status(
  db: AsyncSession,
  resource_instance_accession_id: uuid.UUID,
  new_status: Optional[ResourceStatusEnum] = None,
  status_details: Optional[str] = None,
  properties_json_update: Optional[Dict[str, Any]] = None,
) -> Optional[ResourceOrm]:
  """Update the status and other details of a resource instance.

  Args:
      db (AsyncSession): The database session.
      resource_instance_accession_id (uuid.UUID): The ID of the resource instance to update.
      new_status (Optional[ResourceStatusEnum], optional): The new
          status for the resource instance. Defaults to None.
      status_details (Optional[str], optional): Additional details about the
          current status. Defaults to None.
      properties_json_update (Optional[Dict[str, Any]], optional): A dictionary
          of properties to merge into the existing `properties_json`.
          Defaults to None.

  Returns:
      Optional[ResourceOrm]: The updated resource instance object if
      found, otherwise None.

  Raises:
      Exception: For any unexpected errors during the process.

  """
  logger.info(
    "Updating resource instance ID %d: new_status=%s.",
    resource_instance_accession_id,
    new_status,
  )
  instance_orm = await read_resource_instance_by_name(
    db, resource_instance_accession_id
  )
  if instance_orm:
    if new_status is not None:
      logger.debug(
        "Instance ID %d status changing from '%s' to '%s'.",
        resource_instance_accession_id,
        instance_orm.current_status.name,
        new_status.name,
      )
      instance_orm.current_status = new_status

    if status_details is not None:
      logger.debug(
        "Instance ID %d status details updated.", resource_instance_accession_id
      )
      instance_orm.status_details = status_details

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
  stmt = select(ResourceOrm).filter(ResourceOrm.accession_id == instance_accession_id)
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
    logger.error(error_message)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error deleting resource instance ID %d. Rolling back.",
      instance_accession_id,
    )
    raise e


async def delete_resource_instance_by_name(db: AsyncSession, name: str) -> bool:
  """Delete a resource instance by its unique name.

  Args:
      db (AsyncSession): The database session.
      name (str): The unique name of the resource
          instance to delete.

  Returns:
      bool: True if the deletion was successful, False if the instance was
      not found.

  """
  logger.info("Attempting to delete resource instance with name: '%s'.", name)
  instance_orm = await read_resource_instance_by_name(db, name=name)
  if not instance_orm:
    logger.warning(
      "Resource instance with name '%s' not found for deletion.",
      name,
    )
    return False
  try:
    await db.delete(instance_orm)
    await db.commit()
    logger.info(
      "Successfully deleted resource instance with name '%s'.",
      name,
    )
    return True
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Cannot delete resource instance '{name}' due to existing "
      f"references (e.g., in deck layouts). Details: {e}"
    )
    logger.error(error_message)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error deleting resource instance with name '%s'. Rolling back.",
      name,
    )
    raise e
