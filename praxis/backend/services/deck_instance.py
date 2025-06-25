# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""Service layer for Deck Data Management.

praxis/db_services/deck_data_service.py

Service layer for interacting with deck-related data in the database.
This includes Deck Configurations, Deck Types, and Deck Position Definitions.

This module provides functions to create, read, update, and delete deck instances,
deck type definitions, and deck position definitions.

It also includes functions to manage position definitions for deck types.
"""

import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from praxis.backend.models import (
  DeckInstanceOrm,
  DeckInstancePositionResourceOrm,
  MachineOrm,
  ResourceInstanceOrm,
)
from praxis.backend.utils.logging import get_logger

from .resource_type_definition import read_resource_definition

logger = get_logger(__name__)

UUID = uuid.UUID

# TODO: add resource counterpart operations


async def create_deck_instance(
  db: AsyncSession,
  name: str,
  deck_accession_id: UUID,
  python_fqn: str,
  description: Optional[str] = None,
  position_items_data: Optional[List[Dict[str, Any]]] = None,
) -> DeckInstanceOrm:
  """Create a new deck instance configuration with optional positioned items.

  This function creates a deck instance configuration and associates it with a deck
  machine. It can also position items for the deck instance if `position_items_data`
  is provided.

  Args:
    db (AsyncSession): The database session.
    name (str): The name of the deck instance.
    deck_accession_id (UUID): The ID of the deck to associate with this config.
    python_fqn (str): The fully qualified name of the Python class representing the
    deck.
    description (Optional[str], optional): Description of the deck instance.
      Defaults to None.
    position_items_data (Optional[List[Dict[str, Any]]], optional): List of position
    items data. Each dictionary in the list should contain:
      - 'position_name' (str): The name of the position.
      - 'resource_instance_accession_id' (Optional[UUID]): The ID of the resource instance
        associated with this position (optional).
      - 'expected_resource_definition_name' (Optional[UUID]): The name of the
        expected resource definition for this position (optional).
      Defaults to None.

  Returns:
    DeckInstanceOrm: The created deck instance configuration object.

  Raises:
    ValueError: If:
      - The specified deck ID doesn't exist.
      - A deck instance with the same name already exists.
      - A specified resource instance ID doesn't exist.
      - A specified resource definition name doesn't exist.
    Exception: For any other unexpected errors during the process.

  """
  logger.info(
    "Attempting to create deck instance '%s' for machine ID %s.",
    name,
    deck_accession_id,
  )

  deck_resource_result = await db.execute(
    select(ResourceInstanceOrm).filter(
      ResourceInstanceOrm.accession_id == deck_accession_id
    )
  )
  deck_resource = deck_resource_result.scalar_one_or_none()
  if not deck_resource:
    error_message = (
      f"ResourceInstanceOrm (Deck Device) with id {deck_accession_id} not found. "
      "Cannot create deck instance."
    )
    logger.error(error_message)
    raise ValueError(error_message)

  deck_orm = DeckInstanceOrm(
    name=name,
    deck_accession_id=deck_accession_id,
    description=description,
    python_fqn=python_fqn,
  )
  db.add(deck_orm)

  try:
    await db.flush()
    logger.info("Successfully flushed new deck instance with name '%s'.", name)
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"DeckInstanceOrm with config name '{name}' already exists. Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    logger.exception("Error flushing new deck instance '%s'. Rolling back.", name)
    await db.rollback()
    raise e

  if position_items_data:
    logger.info(
      "Processing %s position items for deck instance '%s'.",
      len(position_items_data),
      name,
    )
    for item_data in position_items_data:
      position_name = item_data.get("position_name", "N/A")
      resource_instance_accession_id = item_data.get("resource_instance_accession_id")
      expected_def_name = item_data.get("expected_resource_definition_name")

      if resource_instance_accession_id:
        resource_instance_result = await db.execute(
          select(ResourceInstanceOrm).filter(
            ResourceInstanceOrm.accession_id == resource_instance_accession_id
          )
        )
        if not resource_instance_result.scalar_one_or_none():
          await db.rollback()
          error_message = (
            f"ResourceInstanceOrm with id {resource_instance_accession_id} for position "
            f"'{position_name}' not found. Rolling back."
          )
          logger.error(error_message)
          raise ValueError(error_message)

      if expected_def_name:
        if not await read_resource_definition(db, expected_def_name):
          await db.rollback()
          error_message = (
            f"ResourceDefinitionCatalogOrm with name '{expected_def_name}' for position "
            f"'{position_name}' not found. Rolling back."
          )
          logger.error(error_message)
          raise ValueError(error_message)

      position_item = DeckInstancePositionResourceOrm(
        deck_accession_id=deck_orm.accession_id,
        position_name=position_name,
        resource_instance_accession_id=resource_instance_accession_id,
        expected_resource_definition_name=expected_def_name,
      )
      db.add(position_item)
      logger.debug(
        "Added position item '%s' to deck instance '%s'.", position_name, name
      )

  try:
    await db.commit()
    await db.refresh(deck_orm)
    logger.info(
      "Successfully committed deck instance '%s' and its position items.", name
    )
    # Eagerly load position_items for the returned object
    if deck_orm.accession_id:
      return await read_deck_instance(db, deck_orm.accession_id)  # type: ignore
    return deck_orm  # Should not be reached if ID is None after flush/commit
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Integrity error while creating deck instance '{name}' or its position items. "
      f"Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error creating deck instance '%s' or its position items. Rolling back.",
      name,
    )
    raise e


async def read_deck_instance_by_parent_machine_accession_id(
  db: AsyncSession, parent_machine_accession_id: UUID
) -> Optional[DeckInstanceOrm]:
  """Retrieve a specific deck instanceuration by its parent machine ID.

  Args:
    db (AsyncSession): The database session.
    parent_machine_accession_id (UUID): The ID of the parent machine.

  Returns:
    Optional[DeckInstanceOrm]: The deck instanceuration object if found,
    otherwise None.

  """
  logger.info(
    "Attempting to retrieve deck instanceuration with parent machine ID: %s.",
    parent_machine_accession_id,
  )
  stmt = select(DeckInstanceOrm).filter(
    DeckInstanceOrm.deck_accession_id == parent_machine_accession_id
  )
  result = await db.execute(stmt)
  deck = result.scalar_one_or_none()
  if deck:
    logger.info(
      "Successfully retrieved deck instanceuration with parent machine ID %s: '%s'.",
      parent_machine_accession_id,
      deck.name,
    )
  else:
    logger.info(
      "Deck configuration with parent machine ID %s not found.",
      parent_machine_accession_id,
    )
  return deck


async def read_deck_instance(
  db: AsyncSession, deck_accession_id: UUID
) -> Optional[DeckInstanceOrm]:
  """Retrieve a specific deck instance configuration by its ID.

  This function retrieves a deck instance configuration along with its position items,
  including the associated resource instances and their definitions.

  Args:
    db (AsyncSession): The database session.
    deck_accession_id (UUID): The ID of the deck instance to retrieve.

  Returns:
    Optional[DeckInstanceOrm]: The deck instance configuration object if found,
    otherwise None.

  """
  logger.info("Attempting to retrieve deck instance with ID: %s.", deck_accession_id)
  stmt = (
    select(DeckInstanceOrm)
    .options(
      selectinload(DeckInstanceOrm.position_items)
      .selectinload(DeckInstancePositionResourceOrm.resource_instance)
      .selectinload(ResourceInstanceOrm.resource_definition),
      selectinload(DeckInstanceOrm.position_items).selectinload(
        DeckInstancePositionResourceOrm.expected_resource_definition
      ),
    )
    .filter(DeckInstanceOrm.accession_id == deck_accession_id)
  )
  result = await db.execute(stmt)
  deck = result.scalar_one_or_none()
  if deck:
    logger.info(
      "Successfully retrieved deck instance ID %s: '%s'.",
      deck_accession_id,
      deck.name,
    )
  else:
    logger.info("Deck config with ID %s not found.", deck_accession_id)
  return deck


async def read_deck_instance_by_name(
  db: AsyncSession, name: str
) -> Optional[DeckInstanceOrm]:
  """Retrieve a specific deck instance configuration by its name.

  This function retrieves a deck instance configuration along with its position items,
  including the associated resource instances and their definitions.

  Args:
    db (AsyncSession): The database session.
    name (str): The name of the deck instance to retrieve.

  Returns:
    Optional[DeckInstanceOrm]: The deck instance configuration object if found,
    otherwise None.

  """
  logger.info("Attempting to retrieve deck instance with name: '%s'.", name)
  stmt = (
    select(DeckInstanceOrm)
    .options(
      selectinload(DeckInstanceOrm.position_items)
      .selectinload(DeckInstancePositionResourceOrm.resource_instance)
      .selectinload(ResourceInstanceOrm.resource_definition),
      selectinload(DeckInstanceOrm.position_items).selectinload(
        DeckInstancePositionResourceOrm.expected_resource_definition
      ),
    )
    .filter(DeckInstanceOrm.name == name)
  )
  result = await db.execute(stmt)
  deck = result.scalar_one_or_none()
  if deck:
    logger.info("Successfully retrieved deck instance by name '%s'.", name)
  else:
    logger.info("Deck config with name '%s' not found.", name)
  return deck


async def list_deck_instances(
  db: AsyncSession,
  deck_accession_id: Optional[int] = None,
  limit: int = 100,
  offset: int = 0,
) -> List[DeckInstanceOrm]:
  """List all deck instances with optional filtering by deck ID.

  This function retrieves a list of deck instance configurations, including their position
  items, associated resource instances, and their definitions.

  Args:
    db (AsyncSession): The database session.
    deck_accession_id (Optional[int]): The ID of the deck to filter by.
      Defaults to None, meaning no filtering by deck ID.
    limit (int): The maximum number of results to return. Defaults to 100.
    offset (int): The number of results to skip before returning. Defaults to 0.

  Returns:
    List[DeckInstanceOrm]: A list of deck instance configuration objects.

  """
  logger.info(
    "Listing deck instances with deck ID filter: %s, limit: %s, offset: %s.",
    deck_accession_id,
    limit,
    offset,
  )
  stmt = select(DeckInstanceOrm).options(
    selectinload(DeckInstanceOrm.position_items)
    .selectinload(DeckInstancePositionResourceOrm.resource_instance)
    .selectinload(ResourceInstanceOrm.resource_definition),
    selectinload(DeckInstanceOrm.position_items).selectinload(
      DeckInstancePositionResourceOrm.expected_resource_definition
    ),
  )
  if deck_accession_id is not None:
    stmt = stmt.filter(DeckInstanceOrm.deck_accession_id == deck_accession_id)
  stmt = stmt.order_by(DeckInstanceOrm.name).limit(limit).offset(offset)
  result = await db.execute(stmt)
  decks = list(result.scalars().all())
  logger.info("Found %s deck instances.", len(decks))
  return decks


async def update_deck_instance(
  db: AsyncSession,
  deck_accession_id: UUID,
  name: Optional[str] = None,
  description: Optional[str] = None,
  position_items_data: Optional[List[Dict[str, Any]]] = None,
) -> Optional[DeckInstanceOrm]:
  """Update an existing deck instance configuration.

  Updates the specified deck instance with new values for its name, description,
  associated deck, and position items. If `position_items_data` is provided,
  it will replace the existing position items for the deck instance.

  Args:
    db (AsyncSession): The database session.
    deck_accession_id (int): The ID of the deck instance to update.
    name (Optional[str], optional): The new name for the deck instance. Defaults to None.
    description (Optional[str], optional): The new description for the deck instance.
      Defaults to None.
    deck_accession_id (int): The ID of the new deck  to
      associate with this config.
    position_items_data (Optional[List[Dict[str, Any]]], optional): A list of new
      position items data. Each dictionary in the list should contain:
      - 'position_name' (str): The name of the position.
      - 'resource_instance_accession_id' (Optional[int]): The ID of the resource instance
        associated with this position (optional).
      - 'expected_resource_definition_name' (Optional[str]): The name of the
        expected resource definition for this position (optional).
      If provided, existing position items for this config will be deleted and
      replaced with these. Defaults to None.

  Returns:
    Optional[DeckInstanceOrm]: The updated deck instance configuration object
    if successful, otherwise None if the config was not found.

  Raises:
    ValueError: If:
      - The new deck ID does not exist.
      - A specified resource instance ID does not exist.
      - A specified resource definition name does not exist.
    Exception: For any other unexpected errors during the process.

  """
  logger.info("Attempting to update deck instance with ID: %s.", deck_accession_id)
  deck_orm = await read_deck_instance(db, deck_accession_id)
  if not deck_orm:
    logger.warning("Deck config with ID %s not found for update.", deck_accession_id)
    return None

  original_name = deck_orm.name
  updates_made = False

  if name is not None and deck_orm.name != name:
    logger.debug("Updating config name from '%s' to '%s'.", deck_orm.name, name)
    deck_orm.name = name
    updates_made = True
  if description is not None and deck_orm.description != description:
    logger.debug("Updating description for config '%s'.", original_name)
    deck_orm.description = description
    updates_made = True
  if deck_accession_id is not None and deck_orm.deck_accession_id != deck_accession_id:
    logger.debug(
      "Updating deck ID from %s to %s for config '%s'.",
      deck_orm.deck_accession_id,
      deck_accession_id,
      original_name,
    )
    new_deck_machine_result = await db.execute(
      select(MachineOrm).filter(MachineOrm.accession_id == deck_accession_id)
    )
    if not new_deck_machine_result.scalar_one_or_none():
      error_message = (
        f"New MachineOrm (Deck Device) with id {deck_accession_id} not found. "
        f"Cannot update deck instance '{original_name}'."
      )
      logger.error(error_message)
      raise ValueError(error_message)
    deck_orm.deck_accession_id = deck_accession_id
    updates_made = True

  if position_items_data is not None:
    logger.info("Replacing position items for deck instance '%s'.", original_name)
    # Delete existing position items
    if deck_orm.position_items:
      for item in deck_orm.position_items:
        logger.debug(
          "Deleting existing position item '%s' for config '%s'.",
          item.position_name,
          original_name,
        )
        await db.delete(item)
    await db.flush()
    updates_made = True

    # Add new position items
    for item_data in position_items_data:
      position_name = item_data.get("position_name", "N/A")
      resource_instance_accession_id = item_data.get("resource_instance_accession_id")
      expected_def_name = item_data.get("expected_resource_definition_name")

      if resource_instance_accession_id:
        resource_instance_result = await db.execute(
          select(ResourceInstanceOrm).filter(
            ResourceInstanceOrm.accession_id == resource_instance_accession_id
          )
        )
        if not resource_instance_result.scalar_one_or_none():
          await db.rollback()
          error_message = (
            f"ResourceInstanceOrm with id {resource_instance_accession_id} for position "
            f"'{position_name}' not found. Rolling back update for config "
            f"'{original_name}'."
          )
          logger.error(error_message)
          raise ValueError(error_message)

      if expected_def_name:
        if not await read_resource_definition(db, expected_def_name):
          await db.rollback()
          error_message = (
            f"ResourceDefinitionCatalogOrm with name '{expected_def_name}' for position"
            f" '{position_name}' not found. Rolling back update for config "
            f"'{original_name}'."
          )
          logger.error(error_message)
          raise ValueError(error_message)

      position_item = DeckInstancePositionResourceOrm(
        deck_accession_id=deck_orm.accession_id,
        position_name=position_name,
        resource_instance_accession_id=resource_instance_accession_id,
        expected_resource_definition_name=expected_def_name,
      )
      db.add(position_item)
      logger.debug(
        "Added new position item '%s' to config '%s'.",
        position_name,
        original_name,
      )

  if not updates_made:
    logger.info(
      "No changes detected for deck instance ID %s. No update performed.",
      deck_accession_id,
    )
    return deck_orm

  try:
    await db.commit()
    await db.refresh(deck_orm)
    logger.info(
      "Successfully updated deck instance ID %s: '%s'.",
      deck_accession_id,
      deck_orm.name,
    )
    return await read_deck_instance(db, deck_accession_id)  # Reload with all relations
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Integrity error while updating deck instance '{original_name}' (ID: {deck_accession_id}). "
      f"Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error updating deck instance '%s' (ID: %s). Rolling back.",
      original_name,
      deck_accession_id,
    )
    raise e


async def delete_deck_instance(db: AsyncSession, deck_accession_id: UUID) -> bool:
  """Delete a specific deck instance by its ID.

  This function deletes a deck instance and all its associated position
  items.

  Args:
    db (AsyncSession): The database session.
    deck_accession_id (int): The ID of the deck instance to delete.

  Returns:
    bool: True if the deletion was successful, False if the config was not found.

  Raises:
    Exception: For any unexpected errors during deletion.

  """
  logger.info("Attempting to delete deck instance with ID: %s.", deck_accession_id)
  deck_orm = await read_deck_instance(db, deck_accession_id)
  if not deck_orm:
    logger.warning(
      "Deck instance with ID %s not found for deletion.", deck_accession_id
    )
    return False

  try:
    await db.delete(deck_orm)
    await db.commit()
    logger.info(
      "Successfully deleted deck instance ID %s: '%s'.",
      deck_accession_id,
      deck_orm.name,
    )
    return True
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Integrity error deleting deck instance ID {deck_accession_id}. "
      f"This might be due to foreign key constraints. Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    return False  # Return False as deletion failed due to integrity
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error deleting deck instance ID %s. Rolling back.", deck_accession_id
    )
    raise e
