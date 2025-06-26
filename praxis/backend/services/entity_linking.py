# praxis/db_services/entity_linking.py

import uuid
from functools import partial
from typing import TYPE_CHECKING, Any, Optional

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


@log_entity_linking_errors(
  prefix="Entity Linking Error: Error while retrieving resource definition for linking.",
  suffix=" Please ensure the resource definition exists in the catalog.",
)
async def _read_resource_definition_for_linking(
  db: AsyncSession,
  name: str,
) -> "ResourceDefinitionCatalogOrm":
  """Retrieve a resource definition."""
  from praxis.backend.models import ResourceDefinitionCatalogOrm

  result = await db.execute(
    select(ResourceDefinitionCatalogOrm).filter(
      ResourceDefinitionCatalogOrm.name == name,
    ),
  )
  definition = result.scalar_one_or_none()
  if not definition:
    raise ValueError(
      f"Resource definition '{name}' not found. Cannot create resource instance.",
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
  resource_counterpart_accession_id: uuid.UUID | None,
  resource_def_name: str | None = None,  # Needed if creating a new resource
  resource_properties_json: dict[str, Any]
  | None = None,  # Needed if creating a new resource
  resource_initial_status: Optional[
    "ResourceStatusEnum"
  ] = None,  # Needed if creating a new resource
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
  current_resource_instance = machine_orm.resource_counterpart

  if is_resource:
    machine_orm.asset_type = AssetType.MACHINE_RESOURCE
    if resource_counterpart_accession_id:
      if (
        current_resource_instance
        and current_resource_instance.accession_id == resource_counterpart_accession_id
      ):
        logger.debug(  # type: ignore
          "%s Already linked to Resource ID %s.",
          log_prefix,
          resource_counterpart_accession_id,
        )
        new_resource_instance = current_resource_instance
      else:
        new_resource_instance = await db.get(
          ResourceOrm,
          resource_counterpart_accession_id,
        )
        if not new_resource_instance:
          raise ValueError(
            f"{log_prefix} ResourceOrm with ID {resource_counterpart_accession_id} not found for linking.",
          )
        machine_orm.resource_counterpart = new_resource_instance
        logger.info(
          "%s Linked to existing Resource ID %s.",
          log_prefix,
          new_resource_instance.accession_id,
        )

      if not new_resource_instance.machine_counterpart:
        new_resource_instance.machine_counterpart = machine_orm
        new_resource_instance.name = machine_orm.name  # Sync name
        db.add(new_resource_instance)  # type: ignore
        logger.debug(
          "%s Ensured reciprocal link from Resource ID %s.",
          log_prefix,
          new_resource_instance.accession_id,
        )

      if (
        current_resource_instance
        and current_resource_instance.accession_id != new_resource_instance.accession_id
      ):
        current_resource_instance.machine_counterpart = None
        db.add(current_resource_instance)  # type: ignore
        logger.info(
          "%s Unlinked old Resource ID %s.",
          log_prefix,
          current_resource_instance.accession_id,
        )

      return new_resource_instance
    if current_resource_instance:
      logger.debug(
        "%s Reusing existing linked Resource ID %s as no new ID provided.",  # type: ignore
        log_prefix,
        current_resource_instance.accession_id,
      )
      return current_resource_instance

    if not resource_def_name:
      raise ValueError(
        f"{log_prefix} Cannot create new ResourceOrm: 'resource_def_name' is required when 'is_resource' is True and no 'resource_counterpart_accession_id' is provided.",
      )

    logger.info("%s Creating new ResourceOrm as counterpart.", log_prefix)
    definition = await _read_resource_definition_for_linking(db, resource_def_name)

    new_resource_instance = ResourceOrm(
      name=machine_orm.name,
      asset_type=AssetType.RESOURCE,
      resource_definition_accession_id=definition.accession_id,
      machine_counterpart=machine_orm,
      properties_json=resource_properties_json,
      current_status=resource_initial_status or ResourceStatusEnum.AVAILABLE_IN_STORAGE,
    )
    db.add(new_resource_instance)
    await db.flush()
    machine_orm.resource_counterpart = new_resource_instance
    logger.info(  # type: ignore
      "%s Created and linked new ResourceOrm ID %s.",
      log_prefix,
      new_resource_instance.accession_id,
    )
    return new_resource_instance
  machine_orm.asset_type = AssetType.MACHINE
  if current_resource_instance:
    logger.info(  # type: ignore
      "%s Unlinking Resource ID %s (no longer a resource).",
      log_prefix,
      current_resource_instance.accession_id,
    )
    current_resource_instance.machine_counterpart = None
    db.add(current_resource_instance)
    machine_orm.resource_counterpart = None
  return None  # type: ignore


@log_entity_linking_errors(
  prefix="Entity Linking Error: Error while creating or linking machine counterpart for resource instance.",
  suffix=" Please ensure the parameters are correct and the resource instance exists.",
)
async def _create_or_link_machine_counterpart_for_resource(
  db: AsyncSession,
  resource_orm: "ResourceOrm",
  is_machine: bool,
  machine_counterpart_accession_id: uuid.UUID | None = None,
  machine_name: str | None = None,
  machine_fqn: str | None = None,
  machine_properties_json: dict[str, Any] | None = None,
  machine_current_status: Optional["MachineStatusEnum"] = None,
) -> Optional["MachineOrm"]:  # type: ignore
  """Create or link a MachineOrm counterpart for a ResourceOrm."""
  from praxis.backend.models import MachineOrm, MachineStatusEnum

  log_prefix = (
    f"Resource (ID: {resource_orm.accession_id}, Name: '{resource_orm.name}'):"
  )

  # Eager load the existing counterpart if the ID is present
  await db.refresh(resource_orm, attribute_names=["machine_counterpart"])
  current_machine_counterpart = resource_orm.machine_counterpart

  if is_machine:
    resource_orm.asset_type = AssetType.MACHINE_RESOURCE
    if machine_counterpart_accession_id:
      if (
        current_machine_counterpart
        and current_machine_counterpart.accession_id == machine_counterpart_accession_id
      ):
        logger.debug(  # type: ignore
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
          raise ValueError(
            f"{log_prefix} MachineOrm with ID {machine_counterpart_accession_id} not found for linking.",
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
        new_machine_counterpart.name = resource_orm.name  # type: ignore
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
        db.add(current_machine_counterpart)  # type: ignore
        logger.info(
          "%s Unlinked old Machine ID %s.",
          log_prefix,
          current_machine_counterpart.accession_id,
        )

      return new_machine_counterpart
    if current_machine_counterpart:
      logger.debug(
        "%s Reusing existing linked Machine ID %s as no new ID provided.",  # type: ignore
        log_prefix,
        current_machine_counterpart.accession_id,
      )
      return current_machine_counterpart

    if not machine_name or not machine_fqn:
      raise ValueError(
        f"{log_prefix} Cannot create new MachineOrm: 'machine_name' and 'machine_fqn' are required when 'is_machine' is True and no 'machine_counterpart_accession_id' is provided.",
      )

    logger.info("%s Creating new MachineOrm as counterpart.", log_prefix)
    new_machine_counterpart = MachineOrm(
      name=resource_orm.name,
      fqn=machine_fqn,
      asset_type=AssetType.MACHINE_RESOURCE,
      resource_counterpart=resource_orm,
      properties_json=machine_properties_json,
      status=machine_current_status or MachineStatusEnum.OFFLINE,
    )
    db.add(new_machine_counterpart)
    await db.flush()
    resource_orm.machine_counterpart = new_machine_counterpart
    logger.info(  # type: ignore
      "%s Created and linked new MachineOrm ID %s.",
      log_prefix,
      new_machine_counterpart.accession_id,
    )
    return new_machine_counterpart
  resource_orm.asset_type = AssetType.RESOURCE
  if current_machine_counterpart:  # type: ignore
    logger.info(
      "%s Unlinking Machine ID %s (no longer a machine).",
      log_prefix,
      current_machine_counterpart.accession_id,
    )
    current_machine_counterpart.asset_type = AssetType.MACHINE
    current_machine_counterpart.resource_counterpart = None
    db.add(current_machine_counterpart)
    resource_orm.machine_counterpart = None  # type: ignore
  return None


@log_entity_linking_errors(
  prefix="Entity Linking Error: Error while synchronizing names between entities.",
  suffix=" Please ensure the entities are properly linked.",
)
async def synchronize_machine_resource_names(
  db: AsyncSession,
  machine_orm: "MachineOrm",
  new_machine_name: str | None = None,
) -> None:
  """Synchronize names between a machine and its resource counterpart."""  # type: ignore
  if not machine_orm.resource_counterpart:
    return

  name_to_sync = new_machine_name or machine_orm.name
  resource_instance = machine_orm.resource_counterpart

  if resource_instance.name != name_to_sync:
    logger.info(  # type: ignore
      "Synchronizing resource name from '%s' to '%s' for Machine ID %s",
      resource_instance.name,
      name_to_sync,
      machine_orm.accession_id,
    )
    resource_instance.name = name_to_sync
    db.add(resource_instance)


# type: ignore


@log_entity_linking_errors(
  prefix="Entity Linking Error: Error while synchronizing names between entities.",
  suffix=" Please ensure the entities are properly linked.",
)
async def synchronize_resource_machine_names(
  db: AsyncSession,
  resource_orm: "ResourceOrm",
  new_resource_name: str | None = None,
) -> None:
  """Synchronize names between a resource and its machine counterpart."""  # type: ignore
  if not resource_orm.machine_counterpart:
    return

  name_to_sync = new_resource_name or resource_orm.name
  machine = resource_orm.machine_counterpart

  if machine.name != name_to_sync:
    logger.info(  # type: ignore
      "Synchronizing machine name from '%s' to '%s' for Resource ID %s",
      machine.name,
      name_to_sync,
      resource_orm.accession_id,
    )
    machine.name = name_to_sync
    db.add(machine)


# type: ignore


@log_entity_linking_errors(
  prefix="Entity Linking Error: Error while synchronizing deck-resource names.",
  suffix=" Please ensure the entities are properly linked.",
)
async def synchronize_deck_resource_names(
  db: AsyncSession,
  deck_orm: "DeckOrm",
  new_deck_name: str | None = None,
) -> None:
  """Synchronize names between a deck instance and its resource counterpart."""  # type: ignore
  if not deck_orm.resource_counterpart:
    return

  name_to_sync = new_deck_name or deck_orm.name
  resource_instance = deck_orm.resource_counterpart

  if resource_instance.name != name_to_sync:
    logger.info(
      "Synchronizing resource name from '%s' to '%s' for Deck ID %s",
      resource_instance.name,
      name_to_sync,
      deck_orm.accession_id,
    )
    resource_instance.name = name_to_sync
    db.add(resource_instance)


# type: ignore


@log_entity_linking_errors(
  prefix="Entity Linking Error: Error while synchronizing resource-deck names.",
  suffix=" Please ensure the entities are properly linked.",
)
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

  if deck.name != name_to_sync:
    logger.info(  # type: ignore
      "Synchronizing deck name from '%s' to '%s' for Resource ID %s",
      deck.name,
      name_to_sync,
      resource_orm.accession_id,
    )
    deck.name = name_to_sync
    db.add(deck)
