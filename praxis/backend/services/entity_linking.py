# praxis/db_services/entity_linking.py

import datetime
from functools import partial
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)

if TYPE_CHECKING:
  from praxis.backend.models import (
    MachineOrm,
    MachineStatusEnum,
    ResourceDefinitionCatalogOrm,
    ResourceInstanceOrm,
    ResourceInstanceStatusEnum,
  )

log_entity_linking_errors = partial(
  log_async_runtime_errors,
  logger_instance=logger,
  exception_type=ValueError,
  raises=True,
  raises_exception=ValueError,
)


@log_entity_linking_errors(
  prefix="Entity Linking Error: Error while retrieving resource definition for \
    linking.",
  suffix=" Please ensure the resource definition exists in the catalog.",
)
async def _get_resource_definition_for_linking(
  db: AsyncSession, name: str
) -> "ResourceDefinitionCatalogOrm":
  """Retrieve a resource definition."""
  from praxis.backend.models import ResourceDefinitionCatalogOrm

  result = await db.execute(
    select(ResourceDefinitionCatalogOrm).filter(
      ResourceDefinitionCatalogOrm.name == name
    )
  )
  definition = result.scalar_one_or_none()
  if not definition:
    raise ValueError(
      f"Resource definition '{name}' not found. Cannot create resource instance."
    )
  return definition


@log_entity_linking_errors(
  prefix="Entity Linking Error: Error while creating or linking resource counterpart \
    for machine.",
  suffix=" Please ensure the parameters are correct and the resource definition exists.\
    ",
)
async def _create_or_link_resource_counterpart_for_machine(
  db: AsyncSession,
  machine_orm: "MachineOrm",
  is_resource: bool,
  resource_counterpart_id: Optional[int],
  resource_def_name: Optional[str] = None,  # Needed if creating a new resource
  resource_properties_json: Optional[
    Dict[str, Any]
  ] = None,  # Needed if creating a new resource
  resource_initial_status: Optional[
    "ResourceInstanceStatusEnum"
  ] = None,  # Needed if creating a new resource
) -> Optional["ResourceInstanceOrm"]:
  """Create or link ResourceInstanceORm counterpart for a MachineOrm.

  This function is called by machine_data_service.py.

  Args:
    db: The database session.
    machine_orm: The MachineOrm instance to link or create a resource for.
    is_resource: Whether the machine is a resource.
    resource_counterpart_id: ID of an existing ResourceInstanceOrm to link, if any.
    resource_def_name: Name of the resource definition to use if creating a new
    resource.
    resource_properties_json: Properties for the new ResourceInstanceOrm, if creating
    one.
    resource_initial_status: Initial status for the new ResourceInstanceOrm, if creating
    one.

  Returns:
    The linked or newly created ResourceInstanceOrm, or None if not a resource.

  Raises:
    ValueError: If the resource definition is not found or if required parameters are
    missing.

  """
  from praxis.backend.models import (
    ResourceInstanceOrm,
    ResourceInstanceStatusEnum,
  )  # Runtime import

  log_prefix = (
    f"Machine (ID: {machine_orm.id}, Name: '{machine_orm.user_friendly_name}'):"
  )

  current_resource_instance: Optional[ResourceInstanceOrm] = None
  if machine_orm.resource_counterpart_id:
    # Load the existing counterpart if it exists, to manage its flags
    current_resource_instance = await db.get(
      ResourceInstanceOrm,
      machine_orm.resource_counterpart_id,
      options=[selectinload(ResourceInstanceOrm.machine_counterpart)],
    )

  if is_resource:
    if resource_counterpart_id:
      if (
        current_resource_instance
        and current_resource_instance.id == resource_counterpart_id
      ):
        logger.debug(
          "%s Already linked to ResourceInstance ID %d.",
          log_prefix,
          resource_counterpart_id,
        )
        new_resource_instance = current_resource_instance
      else:
        new_resource_instance = await db.get(
          ResourceInstanceOrm, resource_counterpart_id
        )
        if not new_resource_instance:
          raise ValueError(
            f"{log_prefix} ResourceInstanceOrm with ID {resource_counterpart_id} not \
              found for linking."
          )
        machine_orm.resource_counterpart = new_resource_instance
        logger.info(
          "%s Linked to existing ResourceInstance ID %d.",
          log_prefix,
          new_resource_instance.id,
        )

      if (
        not new_resource_instance.is_machine
        or new_resource_instance.machine_counterpart_id != machine_orm.id
      ):
        new_resource_instance.is_machine = True
        new_resource_instance.machine_counterpart = machine_orm
        db.add(new_resource_instance)  # Mark for update
        logger.debug(
          "%s Ensured reciprocal link from ResourceInstance ID %d.",
          log_prefix,
          new_resource_instance.id,
        )

      if (
        current_resource_instance
        and current_resource_instance.id != new_resource_instance.id
      ):
        if (
          current_resource_instance.is_machine
          and current_resource_instance.machine_counterpart_id == machine_orm.id
        ):
          current_resource_instance.is_machine = False
          current_resource_instance.machine_counterpart = None
          db.add(current_resource_instance)
          logger.info(
            "%s Unlinked old ResourceInstance ID %d.",
            log_prefix,
            current_resource_instance.id,
          )

      return new_resource_instance
    else:
      if (
        current_resource_instance
        and current_resource_instance.is_machine
        and current_resource_instance.machine_counterpart_id == machine_orm.id
      ):
        logger.debug(
          "%s Reusing existing linked ResourceInstance ID %d as no new ID provided.",
          log_prefix,
          current_resource_instance.id,
        )
        return current_resource_instance

      if not resource_def_name:
        raise ValueError(
          f"{log_prefix} Cannot create new ResourceInstanceOrm: 'resource_def_name' is \
            required when 'is_resource' is True and no 'resource_counterpart_id' is \
              provided."
        )

      logger.info("%s Creating new ResourceInstanceOrm as counterpart.", log_prefix)
      definition = await _get_resource_definition_for_linking(db, resource_def_name)

      new_resource_instance = ResourceInstanceOrm(
        user_assigned_name=f"Resource for {machine_orm.user_friendly_name} (Machine ID:\
          {machine_orm.id})",
        name=definition.name,
        resource_definition=definition,
        is_machine=True,
        machine_counterpart=machine_orm,
        properties_json=resource_properties_json,
        current_status=resource_initial_status
        or ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
      )
      db.add(new_resource_instance)
      await db.flush()
      machine_orm.resource_counterpart = new_resource_instance
      logger.info(
        "%s Created and linked new ResourceInstanceOrm ID %d.",
        log_prefix,
        new_resource_instance.id,
      )
      return new_resource_instance
  else:
    if current_resource_instance:
      if (
        current_resource_instance.is_machine
        and current_resource_instance.machine_counterpart_id == machine_orm.id
      ):
        logger.info(
          "%s Unlinking ResourceInstance ID %d (no longer a resource).",
          log_prefix,
          current_resource_instance.id,
        )
        current_resource_instance.is_machine = False
        current_resource_instance.machine_counterpart = None
        db.add(current_resource_instance)
      machine_orm.resource_counterpart = None
    return None


@log_entity_linking_errors(
  prefix="Entity Linking Error: Error while creating or linking machine counterpart \
    for resource instance.",
  suffix=" Please ensure the parameters are correct and the resource instance exists.",
)
async def _create_or_link_machine_counterpart_for_resource(
  db: AsyncSession,
  resource_instance_orm: "ResourceInstanceOrm",
  is_machine: bool,
  machine_counterpart_id: Optional[int],
  machine_user_friendly_name: Optional[str] = None,
  machine_python_fqn: Optional[str] = None,
  machine_properties_json: Optional[Dict[str, Any]] = None,
  machine_current_status: Optional["MachineStatusEnum"] = None,
) -> Optional["MachineOrm"]:
  """Create or link a MachineOrm counterpart for a ResourceInstanceOrm.

  Handles the creation or linking of a MachineOrm counterpart for a ResourceInstanceOrm.
  This function is called by resource_data_service.py.

  Args:
    db: The database session.
    resource_instance_orm: The ResourceInstanceOrm to link or create a machine for.
    is_machine: Whether the resource is a machine.
    machine_counterpart_id: ID of an existing MachineOrm to link, if any.
    machine_user_friendly_name: User-friendly name for the new MachineOrm, if creating
    one.
    machine_python_fqn: Python FQN for the new MachineOrm, if creating one.
    machine_properties_json: Properties for the new MachineOrm, if creating one.
    machine_current_status: Initial status for the new MachineOrm, if creating one.

  Returns:
    The linked or newly created MachineOrm, or None if not a machine.

  Raises:
    ValueError: If the machine counterpart ID is not found or if required parameters are
    missing when creating a new machine.

  """
  from praxis.backend.models import MachineOrm, MachineStatusEnum

  log_prefix = f"ResourceInstance (ID: {resource_instance_orm.id}, Name: '\
    {resource_instance_orm.user_assigned_name}'):"

  current_machine_counterpart: Optional[MachineOrm] = None
  if resource_instance_orm.machine_counterpart_id:
    current_machine_counterpart = await db.get(
      MachineOrm,
      resource_instance_orm.machine_counterpart_id,
      options=[selectinload(MachineOrm.resource_counterpart)],
    )

  if is_machine:
    if machine_counterpart_id:
      if (
        current_machine_counterpart
        and current_machine_counterpart.id == machine_counterpart_id
      ):
        logger.debug(
          "%s Already linked to Machine ID %d.", log_prefix, machine_counterpart_id
        )
        new_machine_counterpart = current_machine_counterpart
      else:
        new_machine_counterpart = await db.get(MachineOrm, machine_counterpart_id)
        if not new_machine_counterpart:
          raise ValueError(
            f"{log_prefix} MachineOrm with ID {machine_counterpart_id} not found for \
              linking."
          )
        resource_instance_orm.machine_counterpart = new_machine_counterpart
        logger.info(
          "%s Linked to existing Machine ID %d.", log_prefix, new_machine_counterpart.id
        )

      if (
        not new_machine_counterpart.is_resource
        or new_machine_counterpart.resource_counterpart_id != resource_instance_orm.id
      ):
        new_machine_counterpart.is_resource = True
        new_machine_counterpart.resource_counterpart = resource_instance_orm
        db.add(new_machine_counterpart)
        logger.debug(
          "%s Ensured reciprocal link from Machine ID %d.",
          log_prefix,
          new_machine_counterpart.id,
        )

      if (
        current_machine_counterpart
        and current_machine_counterpart.id != new_machine_counterpart.id
      ):
        if (
          current_machine_counterpart.is_resource
          and current_machine_counterpart.resource_counterpart_id
          == resource_instance_orm.id
        ):
          current_machine_counterpart.is_resource = False
          current_machine_counterpart.resource_counterpart = None
          db.add(current_machine_counterpart)
          logger.info(
            "%s Unlinked old Machine ID %d.", log_prefix, current_machine_counterpart.id
          )

      return new_machine_counterpart
    else:
      if (
        current_machine_counterpart
        and current_machine_counterpart.is_resource
        and current_machine_counterpart.resource_counterpart_id
        == resource_instance_orm.id
      ):
        logger.debug(
          "%s Reusing existing linked Machine ID %d as no new ID provided.",
          log_prefix,
          current_machine_counterpart.id,
        )
        return current_machine_counterpart

      if not machine_user_friendly_name or not machine_python_fqn:
        raise ValueError(
          f"{log_prefix} Cannot create new MachineOrm: 'machine_user_friendly_name' \
            and 'machine_python_fqn' are required when 'is_machine' is True and no \
              'machine_counterpart_id' is provided."
        )

      logger.info("%s Creating new MachineOrm as counterpart.", log_prefix)
      new_machine_counterpart = MachineOrm(
        user_friendly_name=f"Machine for {resource_instance_orm.user_assigned_name} \
          (Resource ID: {resource_instance_orm.id})",
        python_fqn=machine_python_fqn,
        is_resource=True,
        resource_counterpart=resource_instance_orm,
        properties_json=machine_properties_json,
        current_status=machine_current_status or MachineStatusEnum.OFFLINE,
      )
      db.add(new_machine_counterpart)
      await db.flush()
      resource_instance_orm.machine_counterpart = new_machine_counterpart
      logger.info(
        "%s Created and linked new MachineOrm ID %d.",
        log_prefix,
        new_machine_counterpart.id,
      )
      return new_machine_counterpart
  else:
    if current_machine_counterpart:
      if (
        current_machine_counterpart.is_resource
        and current_machine_counterpart.resource_counterpart_id
        == resource_instance_orm.id
      ):
        logger.info(
          "%s Unlinking Machine ID %d (no longer a machine).",
          log_prefix,
          current_machine_counterpart.id,
        )
        current_machine_counterpart.is_resource = False
        current_machine_counterpart.resource_counterpart = None
        db.add(current_machine_counterpart)
      resource_instance_orm.machine_counterpart = None
    return None
