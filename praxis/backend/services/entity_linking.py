"""Entity linking services for synchronizing and managing relationships.

This module provides asynchronous functions to create, link, and synchronize ORM entities such as
MachineOrm, ResourceOrm, and DeckOrm, ensuring consistency and proper bidirectional relationships in
the database.
"""

import uuid
from functools import partial
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.enums import AssetType
from praxis.backend.utils.db_decorator import handle_db_transaction
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)

if TYPE_CHECKING:
  from praxis.backend.models import (
    DeckOrm,
    MachineOrm,
    MachineStatusEnum,
    ResourceDefinitionOrm,
    ResourceOrm,
    ResourceStatusEnum,
  )

log_entity_linking_errors = partial(
  log_async_runtime_errors,
  logger_instance=logger,
  exception_type=ValueError,
  raises=True,
  raises_exception=ValueError,
)


@handle_db_transaction
async def _read_resource_definition_for_linking(
  db: AsyncSession,
  name: str,
) -> "ResourceDefinitionOrm":
  """Retrieve a resource definition."""
  from praxis.backend.models import ResourceDefinitionOrm

  result = await db.execute(
    select(ResourceDefinitionOrm).filter(
      ResourceDefinitionOrm.name == name,
    ),
  )
  definition = result.scalar_one_or_none()
  if not definition:
    msg = f"Resource definition '{name}' not found. Cannot create resource instance."
    raise ValueError(
      msg,
    )
  return definition


@handle_db_transaction
async def _create_or_link_resource_counterpart_for_machine(
  db: AsyncSession,
  machine_orm: "MachineOrm",
  resource_counterpart_accession_id: uuid.UUID | None,
  resource_definition_name: str | None = None,  # Needed if creating a new resource
  resource_properties_json: dict[str, Any] | None = None,  # Needed if creating a new resource
  resource_status: Optional["ResourceStatusEnum"] = None,  # Needed if
  # creating a new resource
) -> Optional["ResourceOrm"]:
  """Create or link ResourceOrm counterpart for a MachineOrm."""
  from praxis.backend.models import (
    ResourceOrm,
    ResourceStatusEnum,
  )  # Runtime import

  log_prefix = f"Machine (ID: {machine_orm.accession_id}, Name: '{machine_orm.name}'):"

  # Eager load the existing counterpart if the ID is present
  if machine_orm.resource_counterpart_accession_id:
    await db.refresh(machine_orm, attribute_names=["resource_counterpart"])
  current_resource = machine_orm.resource_counterpart

  if resource_counterpart_accession_id is not None:
    machine_orm.asset_type = AssetType.MACHINE_RESOURCE
    if current_resource and current_resource.accession_id == resource_counterpart_accession_id:
      logger.debug(
        "%s Already linked to Resource ID %s.",
        log_prefix,
        resource_counterpart_accession_id,
      )
      new_resource = current_resource
    else:
      new_resource = await db.get(
        ResourceOrm,
        resource_counterpart_accession_id,
      )
      if not new_resource:
        msg = (
          f"{log_prefix} ResourceOrm with ID {resource_counterpart_accession_id} "
          "not found for linking."
        )
        raise ValueError(
          msg,
        )
      machine_orm.resource_counterpart = new_resource
      logger.info(
        "%s Linked to existing Resource ID %s.",
        log_prefix,
        new_resource.accession_id,
      )

    if not new_resource.machine_counterpart:
      new_resource.machine_counterpart = machine_orm
      new_resource.name = machine_orm.name  # Sync name
      db.add(new_resource)
      logger.debug(
        "%s Ensured reciprocal link from Resource ID %s.",
        log_prefix,
        new_resource.accession_id,
      )

    if current_resource and current_resource.accession_id != new_resource.accession_id:
      current_resource.machine_counterpart = None
      db.add(current_resource)
      logger.info(
        "%s Unlinked old Resource ID %s.",
        log_prefix,
        current_resource.accession_id,
      )

    return new_resource
  if current_resource:
    logger.debug(
      "%s Reusing existing linked Resource ID %s as no new ID provided.",
      log_prefix,
      current_resource.accession_id,
    )
    return current_resource

  if not resource_definition_name:
    msg = (
      f"{log_prefix} Cannot create new ResourceOrm: 'resource_definition_name' is "
      "required when 'is_resource' is True and no "
      "'resource_counterpart_accession_id' is provided."
    )
    raise ValueError(msg)

  logger.info("%s Creating new ResourceOrm as counterpart.", log_prefix)
  definition = await _read_resource_definition_for_linking(db, resource_definition_name)

  new_resource = ResourceOrm(
    fqn=machine_orm.fqn,
    name=f"{machine_orm.name}_resource",
    asset_type=AssetType.RESOURCE,
    resource_definition_accession_id=definition.accession_id,
    properties_json=resource_properties_json or {},
    status=resource_status or ResourceStatusEnum.AVAILABLE_IN_STORAGE,
  )
  db.add(new_resource)
  await db.flush()
  machine_orm.resource_counterpart_accession_id = new_resource.accession_id
  logger.info(
    "%s Created and linked new ResourceOrm ID %s.",
    log_prefix,
    new_resource.accession_id,
  )
  return new_resource
  machine_orm.asset_type = AssetType.MACHINE
  if current_resource:
    logger.info(
      "%s Unlinking Resource ID %s (no longer a resource).",
      log_prefix,
      current_resource.accession_id,
    )
    current_resource.machine_counterpart = None
    db.add(current_resource)
    machine_orm.resource_counterpart = None
  return None


@handle_db_transaction
async def _create_or_link_machine_counterpart_for_resource(
  db: AsyncSession,
  resource_orm: "ResourceOrm",
  machine_counterpart_accession_id: uuid.UUID | None = None,
  machine_name: str | None = None,
  machine_fqn: str | None = None,
  machine_properties_json: dict[str, Any] | None = None,
  machine_status: Optional["MachineStatusEnum"] = None,
) -> Optional["MachineOrm"]:
  """Create or link a MachineOrm counterpart for a ResourceOrm."""
  from praxis.backend.models import MachineOrm, MachineStatusEnum

  log_prefix = f"Resource (ID: {resource_orm.accession_id}, Name: '{resource_orm.name}'):"

  # Eager load the existing counterpart if the ID is present
  await db.refresh(resource_orm, attribute_names=["machine_counterpart"])
  current_machine_counterpart = resource_orm.machine_counterpart

  resource_orm.asset_type = AssetType.MACHINE_RESOURCE
  if machine_counterpart_accession_id:
    if (
      current_machine_counterpart
      and current_machine_counterpart.accession_id == machine_counterpart_accession_id
    ):
      logger.debug(
        "%s Already linked to Machine ID %s.",
        log_prefix,
        machine_counterpart_accession_id,
      )
      new_machine_counterpart = current_machine_counterpart
    else:
      new_machine_counterpart = await db.get(
        MachineOrm,
        machine_counterpart_accession_id,
      )
      if not new_machine_counterpart:
        msg = (
          f"{log_prefix} MachineOrm with ID {machine_counterpart_accession_id} "
          "not found for linking."
        )
        raise ValueError(
          msg,
        )
      resource_orm.machine_counterpart = new_machine_counterpart
      logger.info(
        "%s Linked to existing Machine ID %s.",
        log_prefix,
        new_machine_counterpart.accession_id,
      )

    if not new_machine_counterpart.resource_counterpart:
      new_machine_counterpart.asset_type = AssetType.MACHINE_RESOURCE
      new_machine_counterpart.resource_counterpart = resource_orm
      new_machine_counterpart.name = resource_orm.name
      db.add(new_machine_counterpart)
      logger.debug(
        "%s Ensured reciprocal link from Machine ID %s.",
        log_prefix,
        new_machine_counterpart.accession_id,
      )

    if (
      current_machine_counterpart
      and current_machine_counterpart.accession_id != new_machine_counterpart.accession_id
    ):
      current_machine_counterpart.asset_type = AssetType.MACHINE
      current_machine_counterpart.resource_counterpart = None
      db.add(current_machine_counterpart)
      logger.info(
        "%s Unlinked old Machine ID %s.",
        log_prefix,
        current_machine_counterpart.accession_id,
      )

    return new_machine_counterpart
  if current_machine_counterpart:
    logger.debug(
      "%s Reusing existing linked Machine ID %s as no new ID provided.",
      log_prefix,
      current_machine_counterpart.accession_id,
    )
    return current_machine_counterpart

  if not machine_name or not machine_fqn:
    msg = (
      f"{log_prefix} Cannot create new MachineOrm: 'machine_name' and "
      "'machine_fqn' are required when 'is_machine' is True and no "
      "'machine_counterpart_accession_id' is provided."
    )
    raise ValueError(
      msg,
    )

  logger.info("%s Creating new MachineOrm as counterpart.", log_prefix)
  new_machine_counterpart = MachineOrm(
    name=f"{resource_orm.name}_machine",
    fqn=machine_fqn,
    asset_type=AssetType.MACHINE_RESOURCE,
    properties_json=machine_properties_json or {},
    status=machine_status or MachineStatusEnum.OFFLINE,
  )
  db.add(new_machine_counterpart)
  await db.flush()
  resource_orm.machine_counterpart = new_machine_counterpart
  logger.info(
    "%s Created and linked new MachineOrm ID %s.",
    log_prefix,
    new_machine_counterpart.accession_id,
  )
  return new_machine_counterpart


@handle_db_transaction
async def synchronize_machine_resource_names(
  db: AsyncSession,
  machine_orm: "MachineOrm",
  new_machine_name: str | None = None,
) -> None:
  """Synchronize names between a machine and its resource counterpart."""
  if not machine_orm.resource_counterpart:
    return

  name_to_sync = new_machine_name or machine_orm.name
  resource = machine_orm.resource_counterpart
  target_name = f"{name_to_sync}_resource"

  if resource.name != target_name:
    logger.info(
      "Synchronizing resource name from '%s' to '%s' for Machine ID %s",
      resource.name,
      target_name,
      machine_orm.accession_id,
    )
    resource.name = target_name
    db.add(resource)


# type: ignore


@handle_db_transaction
async def synchronize_resource_machine_names(
  db: AsyncSession,
  resource_orm: "ResourceOrm",
  new_resource_name: str | None = None,
) -> None:
  """Synchronize names between a resource and its machine counterpart."""
  if not resource_orm.machine_counterpart:
    return

  name_to_sync = new_resource_name or resource_orm.name
  machine = resource_orm.machine_counterpart
  target_name = f"{name_to_sync}_machine"

  if machine.name != target_name:
    logger.info(
      "Synchronizing machine name from '%s' to '%s' for Resource ID %s",
      machine.name,
      target_name,
      resource_orm.accession_id,
    )
    machine.name = target_name
    db.add(machine)


# type: ignore


@handle_db_transaction
async def synchronize_deck_resource_names(
  db: AsyncSession,
  deck_orm: "DeckOrm",
  new_deck_name: str | None = None,
) -> None:
  """Synchronize names between a deck instance and its resource counterpart."""
  if not deck_orm.resource_counterpart:
    return

  name_to_sync = new_deck_name or deck_orm.name
  resource = deck_orm.resource_counterpart
  target_name = f"{name_to_sync}_resource"

  if resource.name != target_name:
    logger.info(
      "Synchronizing resource name from '%s' to '%s' for Deck ID %s",
      resource.name,
      target_name,
      deck_orm.accession_id,
    )
    resource.name = target_name
    db.add(resource)


# type: ignore


@handle_db_transaction
async def synchronize_resource_deck_names(
  db: AsyncSession,
  resource_orm: "ResourceOrm",
  new_resource_name: str | None = None,
) -> None:
  """Synchronize names between a resource and its deck counterpart.

  Args:
      db (AsyncSession): The database session.
      resource_orm (ResourceOrm): The resource instance ORM object.
      new_resource_name (str | None, optional): The new name for the resource.

  If not provided, the current name will be used.

  Raises:
      ValueError: If the resource does not have a deck counterpart.

  """
  if not resource_orm.deck_counterpart:
    return

  name_to_sync = new_resource_name or resource_orm.name
  deck = resource_orm.deck_counterpart
  target_name = f"{name_to_sync}_deck"

  if deck.name != target_name:
    logger.info(
      "Synchronizing deck name from '%s' to '%s' for Resource ID %s",
      deck.name,
      target_name,
      resource_orm.accession_id,
    )
    deck.name = target_name
    db.add(deck)
