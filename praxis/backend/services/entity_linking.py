# praxis/db_services/entity_linking.py

import uuid
from functools import partial
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.enums import AssetType
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)

if TYPE_CHECKING:
  from praxis.backend.models import (
    DeckOrm,
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
  prefix="Entity Linking Error: Error while retrieving resource definition for linking.",
  suffix=" Please ensure the resource definition exists in the catalog.",
)
async def _read_resource_definition_for_linking(
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
  prefix="Entity Linking Error: Error while creating or linking resource counterpart for machine.",
  suffix=" Please ensure the parameters are correct and the resource definition exists.",
)
async def _create_or_link_resource_counterpart_for_machine(
  db: AsyncSession,
  machine_orm: "MachineOrm",
  is_resource: bool,
  resource_counterpart_accession_id: Optional[uuid.UUID],
  resource_def_name: Optional[str] = None,  # Needed if creating a new resource
  resource_properties_json: Optional[
    Dict[str, Any]
  ] = None,  # Needed if creating a new resource
  resource_initial_status: Optional[
    "ResourceInstanceStatusEnum"
  ] = None,  # Needed if creating a new resource
) -> Optional["ResourceInstanceOrm"]:
  """Create or link ResourceInstanceOrm counterpart for a MachineOrm."""
  from praxis.backend.models import (
    ResourceInstanceOrm,
    ResourceInstanceStatusEnum,
  )  # Runtime import

  log_prefix = f"Machine (ID: {machine_orm.accession_id}, Name: '{machine_orm.name}'):"

  # Eager load the existing counterpart if the ID is present
  if machine_orm.resource_counterpart_accession_id:
    await db.refresh(machine_orm, attribute_names=["resource_counterpart"])
  current_resource_instance = machine_orm.resource_counterpart

  if is_resource:
    machine_orm.asset_type = AssetType.MACHINE_RESOURCE
    if resource_counterpart_accession_id:
      if (
        current_resource_instance
        and current_resource_instance.accession_id == resource_counterpart_accession_id
      ):
        logger.debug(
          "%s Already linked to ResourceInstance ID %s.",
          log_prefix,
          resource_counterpart_accession_id,
        )
        new_resource_instance = current_resource_instance
      else:
        new_resource_instance = await db.get(
          ResourceInstanceOrm, resource_counterpart_accession_id
        )
        if not new_resource_instance:
          raise ValueError(
            f"{log_prefix} ResourceInstanceOrm with ID {resource_counterpart_accession_id} not found for linking."
          )
        machine_orm.resource_counterpart = new_resource_instance
        logger.info(
          "%s Linked to existing ResourceInstance ID %s.",
          log_prefix,
          new_resource_instance.accession_id,
        )

      if not new_resource_instance.machine_counterpart:
        new_resource_instance.machine_counterpart = machine_orm
        new_resource_instance.name = machine_orm.name  # Sync name
        db.add(new_resource_instance)
        logger.debug(
          "%s Ensured reciprocal link from ResourceInstance ID %s.",
          log_prefix,
          new_resource_instance.accession_id,
        )

      if (
        current_resource_instance
        and current_resource_instance.accession_id != new_resource_instance.accession_id
      ):
        current_resource_instance.machine_counterpart = None
        db.add(current_resource_instance)
        logger.info(
          "%s Unlinked old ResourceInstance ID %s.",
          log_prefix,
          current_resource_instance.accession_id,
        )

      return new_resource_instance
    else:
      if current_resource_instance:
        logger.debug(
          "%s Reusing existing linked ResourceInstance ID %s as no new ID provided.",
          log_prefix,
          current_resource_instance.accession_id,
        )
        return current_resource_instance

      if not resource_def_name:
        raise ValueError(
          f"{log_prefix} Cannot create new ResourceInstanceOrm: 'resource_def_name' is required when 'is_resource' is True and no 'resource_counterpart_accession_id' is provided."
        )

      logger.info("%s Creating new ResourceInstanceOrm as counterpart.", log_prefix)
      definition = await _read_resource_definition_for_linking(db, resource_def_name)

      new_resource_instance = ResourceInstanceOrm(
        name=machine_orm.name,
        asset_type=AssetType.RESOURCE,
        resource_definition_accession_id=definition.accession_id,
        machine_counterpart=machine_orm,
        properties_json=resource_properties_json,
        current_status=resource_initial_status
        or ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
      )
      db.add(new_resource_instance)
      await db.flush()
      machine_orm.resource_counterpart = new_resource_instance
      logger.info(
        "%s Created and linked new ResourceInstanceOrm ID %s.",
        log_prefix,
        new_resource_instance.accession_id,
      )
      return new_resource_instance
  else:
    machine_orm.asset_type = AssetType.MACHINE
    if current_resource_instance:
      logger.info(
        "%s Unlinking ResourceInstance ID %s (no longer a resource).",
        log_prefix,
        current_resource_instance.accession_id,
      )
      current_resource_instance.machine_counterpart = None
      db.add(current_resource_instance)
      machine_orm.resource_counterpart = None
    return None


@log_entity_linking_errors(
  prefix="Entity Linking Error: Error while creating or linking machine counterpart for resource instance.",
  suffix=" Please ensure the parameters are correct and the resource instance exists.",
)
async def _create_or_link_machine_counterpart_for_resource(
  db: AsyncSession,
  resource_instance_orm: "ResourceInstanceOrm",
  is_machine: bool,
  machine_counterpart_accession_id: Optional[uuid.UUID] = None,
  machine_name: Optional[str] = None,
  machine_fqn: Optional[str] = None,
  machine_properties_json: Optional[Dict[str, Any]] = None,
  machine_current_status: Optional["MachineStatusEnum"] = None,
) -> Optional["MachineOrm"]:
  """Create or link a MachineOrm counterpart for a ResourceInstanceOrm."""
  from praxis.backend.models import MachineOrm, MachineStatusEnum

  log_prefix = (
    f"ResourceInstance (ID: {resource_instance_orm.accession_id}, "
    f"Name: '{resource_instance_orm.name}'):"
  )

  # Eager load the existing counterpart if the ID is present
  await db.refresh(resource_instance_orm, attribute_names=["machine_counterpart"])
  current_machine_counterpart = resource_instance_orm.machine_counterpart

  if is_machine:
    resource_instance_orm.asset_type = AssetType.MACHINE_RESOURCE
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
          MachineOrm, machine_counterpart_accession_id
        )
        if not new_machine_counterpart:
          raise ValueError(
            f"{log_prefix} MachineOrm with ID {machine_counterpart_accession_id} not found for linking."
          )
        resource_instance_orm.machine_counterpart = new_machine_counterpart
        logger.info(
          "%s Linked to existing Machine ID %s.",
          log_prefix,
          new_machine_counterpart.accession_id,
        )

      if not new_machine_counterpart.resource_counterpart:
        new_machine_counterpart.asset_type = AssetType.MACHINE_RESOURCE
        new_machine_counterpart.resource_counterpart = resource_instance_orm
        new_machine_counterpart.name = resource_instance_orm.name
        db.add(new_machine_counterpart)
        logger.debug(
          "%s Ensured reciprocal link from Machine ID %s.",
          log_prefix,
          new_machine_counterpart.accession_id,
        )

      if (
        current_machine_counterpart
        and current_machine_counterpart.accession_id
        != new_machine_counterpart.accession_id
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
    else:
      if current_machine_counterpart:
        logger.debug(
          "%s Reusing existing linked Machine ID %s as no new ID provided.",
          log_prefix,
          current_machine_counterpart.accession_id,
        )
        return current_machine_counterpart

      if not machine_name or not machine_fqn:
        raise ValueError(
          f"{log_prefix} Cannot create new MachineOrm: 'machine_name' and 'machine_fqn' are required when 'is_machine' is True and no 'machine_counterpart_accession_id' is provided."
        )

      logger.info("%s Creating new MachineOrm as counterpart.", log_prefix)
      new_machine_counterpart = MachineOrm(
        name=resource_instance_orm.name,
        fqn=machine_fqn,
        asset_type=AssetType.MACHINE_RESOURCE,
        resource_counterpart=resource_instance_orm,
        properties_json=machine_properties_json,
        status=machine_current_status or MachineStatusEnum.OFFLINE,
      )
      db.add(new_machine_counterpart)
      await db.flush()
      resource_instance_orm.machine_counterpart = new_machine_counterpart
      logger.info(
        "%s Created and linked new MachineOrm ID %s.",
        log_prefix,
        new_machine_counterpart.accession_id,
      )
      return new_machine_counterpart
  else:
    resource_instance_orm.asset_type = AssetType.RESOURCE
    if current_machine_counterpart:
      logger.info(
        "%s Unlinking Machine ID %s (no longer a machine).",
        log_prefix,
        current_machine_counterpart.accession_id,
      )
      current_machine_counterpart.asset_type = AssetType.MACHINE
      current_machine_counterpart.resource_counterpart = None
      db.add(current_machine_counterpart)
      resource_instance_orm.machine_counterpart = None
    return None


@log_entity_linking_errors(
  prefix="Entity Linking Error: Error while synchronizing names between entities.",
  suffix=" Please ensure the entities are properly linked.",
)
async def synchronize_machine_resource_names(
  db: AsyncSession,
  machine_orm: "MachineOrm",
  new_machine_name: Optional[str] = None,
) -> None:
  """Synchronize names between a machine and its resource counterpart."""
  if not machine_orm.resource_counterpart:
    return

  name_to_sync = new_machine_name or machine_orm.name
  resource_instance = machine_orm.resource_counterpart

  if resource_instance.name != name_to_sync:
    logger.info(
      "Synchronizing resource name from '%s' to '%s' for Machine ID %s",
      resource_instance.name,
      name_to_sync,
      machine_orm.accession_id,
    )
    resource_instance.name = name_to_sync
    db.add(resource_instance)


@log_entity_linking_errors(
  prefix="Entity Linking Error: Error while synchronizing names between entities.",
  suffix=" Please ensure the entities are properly linked.",
)
async def synchronize_resource_machine_names(
  db: AsyncSession,
  resource_instance_orm: "ResourceInstanceOrm",
  new_resource_name: Optional[str] = None,
) -> None:
  """Synchronize names between a resource and its machine counterpart."""
  if not resource_instance_orm.machine_counterpart:
    return

  name_to_sync = new_resource_name or resource_instance_orm.name
  machine = resource_instance_orm.machine_counterpart

  if machine.name != name_to_sync:
    logger.info(
      "Synchronizing machine name from '%s' to '%s' for Resource ID %s",
      machine.name,
      name_to_sync,
      resource_instance_orm.accession_id,
    )
    machine.name = name_to_sync
    db.add(machine)


@log_entity_linking_errors(
  prefix="Entity Linking Error: Error while synchronizing deck-resource names.",
  suffix=" Please ensure the entities are properly linked.",
)
async def synchronize_deck_resource_names(
  db: AsyncSession,
  deck_instance_orm: "DeckOrm",
  new_deck_name: Optional[str] = None,
) -> None:
  """Synchronize names between a deck instance and its resource counterpart."""
  if not deck_instance_orm.resource_counterpart:
    return

  name_to_sync = new_deck_name or deck_instance_orm.name
  resource_instance = deck_instance_orm.resource_counterpart

  if resource_instance.name != name_to_sync:
    logger.info(
      "Synchronizing resource name from '%s' to '%s' for Deck ID %s",
      resource_instance.name,
      name_to_sync,
      deck_instance_orm.accession_id,
    )
    resource_instance.name = name_to_sync
    db.add(resource_instance)


@log_entity_linking_errors(
  prefix="Entity Linking Error: Error while synchronizing resource-deck names.",
  suffix=" Please ensure the entities are properly linked.",
)
async def synchronize_resource_deck_names(
  db: AsyncSession,
  resource_instance_orm: "ResourceInstanceOrm",
  new_resource_name: Optional[str] = None,
) -> None:
  """Synchronize names between a resource and its deck counterpart."""
  if not resource_instance_orm.deck_counterpart:
    return

  name_to_sync = new_resource_name or resource_instance_orm.name
  deck = resource_instance_orm.deck_counterpart

  if deck.name != name_to_sync:
    logger.info(
      "Synchronizing deck name from '%s' to '%s' for Resource ID %s",
      deck.name,
      name_to_sync,
      resource_instance_orm.accession_id,
    )
    deck.name = name_to_sync
    db.add(deck)
