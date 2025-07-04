# pylint: disable=broad-except, too-many-lines
"""Service layer for Deck Type Definition Management.

praxis/db_services/deck_data_service.py

Service layer for interacting with deck-related data in the database.
This includes Deck Configurations, Deck Types, and Deck Position Definitions.

This module provides functions to create, read, update, and delete deck instances,
deck type definitions, and deck position definitions.

It also includes functions to manage position definitions for deck types.
"""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import flag_modified

from praxis.backend.models import (
  DeckDefinitionOrm,
  DeckPositionDefinitionOrm,
  PositioningConfig,
)
from praxis.backend.utils.logging import get_logger

logger = get_logger(__name__)

UUID = uuid.UUID


async def _process_position_definitions(
  db: AsyncSession,
  deck_type_orm: DeckDefinitionOrm,
  position_definitions: list[dict[str, Any]] | None,
  log_prefix: str,
):
  """Handle the deletion and creation of position definitions.

  Helper function to handle the deletion and creation of position definitions.
  This logic is common to both create and update.

  Args:
      db (AsyncSession): The database session.
      deck_type_orm (DeckTypeDefinitionOrm): The deck type ORM object to which
          position definitions will be added.
      position_definitions (Optional[list[dict[str, Any]]]): A list of
        dictionaries, each representing a position definition for this deck type.
      log_prefix (str): Prefix for logging messages to identify the operation.

  Raises:
      ValueError: If position definitions data is provided but not in the expected
        format.
      Exception: For any unexpected errors during the process.

  """
  if position_definitions is not None:
    logger.info(
      "%s Replacing existing position definitions with %s new ones.",
      log_prefix,
      len(position_definitions),
    )

    if deck_type_orm.accession_id:
      existing_positions_stmt = select(DeckPositionDefinitionOrm).filter(
        DeckPositionDefinitionOrm.deck_type_id == deck_type_orm.accession_id,
      )
      result = await db.execute(existing_positions_stmt)
      for position in result.scalars().all():
        await db.delete(position)
      await db.flush()  # Ensure deletions are processed before adding new ones
      logger.debug(
        "%s Existing position definitions for deck type ID %s deleted.",
        log_prefix,
        deck_type_orm.accession_id,
      )

    # Add new position definitions
    for position_data in position_definitions:
      position_accession_id = position_data.get("position_accession_id", "UNKNOWN_POSE")
      x_coord = position_data.get("x_coord", 0.0)
      y_coord = position_data.get("y_coord", 0.0)
      z_coord = position_data.get("z_coord", 0.0)

      logger.debug(
        "%s Adding new position definition: '%s' (%.2f, %.2f, %.2f).",
        log_prefix,
        position_accession_id,
        x_coord,
        y_coord,
        z_coord,
      )

      compatible_resource_fqns_data = position_data.get("compatible_resource_fqns")

      if compatible_resource_fqns_data is None:
        compatible_resource_fqns_data = {}
        if position_data.get("pylabrobot_position_type_name"):
          compatible_resource_fqns_data["pylabrobot_position_type_name"] = position_data[
            "pylabrobot_position_type_name"
          ]
        if position_data.get("allowed_resource_definition_names"):
          compatible_resource_fqns_data["allowed_resource_definition_names"] = position_data[
            "allowed_resource_definition_names"
          ]
        if position_data.get("accepts_tips") is not None:
          compatible_resource_fqns_data["accepts_tips"] = position_data["accepts_tips"]
        if position_data.get("accepts_plates") is not None:
          compatible_resource_fqns_data["accepts_plates"] = position_data["accepts_plates"]
        if position_data.get("accepts_tubes") is not None:
          compatible_resource_fqns_data["accepts_tubes"] = position_data["accepts_tubes"]
        if position_data.get("notes") is not None:
          compatible_resource_fqns_data["notes"] = position_data["notes"]

      # Ensure it's None if empty, to avoid storing empty JSON objects unnecessarily
      if not compatible_resource_fqns_data:
        compatible_resource_fqns_data = None

      position_orm = DeckPositionDefinitionOrm(
        deck_type_id=deck_type_orm.accession_id,
        position_accession_id=position_accession_id,
        x_coord=x_coord,
        y_coord=y_coord,
        z_coord=z_coord,
        compatible_resource_fqns=compatible_resource_fqns_data,
      )
      db.add(position_orm)


async def create_deck_type_definition(
  db: AsyncSession,
  fqn: str,
  name: str,
  description: str | None = None,
  plr_category: str | None = None,
  default_size_x_mm: float | None = None,
  default_size_y_mm: float | None = None,
  default_size_z_mm: float | None = None,
  serialized_constructor_args_json: dict[str, Any] | None = None,
  positioning_config: PositioningConfig | None = None,
  position_definitions: list[dict[str, Any]] | None = None,
) -> DeckDefinitionOrm:
  """Add a new deck type definition to the catalog.

  This function creates a new `DeckTypeDefinitionOrm` along with its associated
  position definitions.

  Args:
      db (AsyncSession): The database session.
      fqn (str): The fully qualified name of the PyLabRobot deck class.
      name (str): A human-readable name for the deck type.
      description (Optional[str], optional): A detailed description of the deck type.
          Defaults to None.
      plr_category (Optional[str], optional): The PyLabRobot category for the deck.
          Defaults to None.
      default_size_x_mm (Optional[float], optional): Default width of the deck in mm.
          Defaults to None.
      default_size_y_mm (Optional[float], optional): Default depth of the deck in mm.
          Defaults to None.
      default_size_z_mm (Optional[float], optional): Default height of the deck in mm.
          Defaults to None.
      serialized_constructor_args_json (Optional[dict[str, Any]], optional):
          Serialized constructor arguments for the PyLabRobot class. Defaults to None.
      positioning_config (Optional[PositioningConfig], optional):
          Configuration for positioning logic. Defaults to None.
      position_definitions (Optional[list[dict[str, Any]]], optional):
          A list of position definitions for this deck type. Defaults to None.

  Returns:
      DeckTypeDefinitionOrm: The created deck type definition object.

  Raises:
      ValueError: If a deck type with the same `fqn` already exists.
      Exception: For any other unexpected errors during the process.

  """
  log_prefix = f"Deck Type (FQN: '{fqn}', creating new):"
  logger.info("%s Attempting to create new deck type definition.", log_prefix)

  # Check if a deck type with this FQN already exists
  result = await db.execute(
    select(DeckDefinitionOrm).filter(DeckDefinitionOrm.fqn == fqn),
  )
  if result.scalar_one_or_none():
    error_message = (
      f"{log_prefix} A deck type definition with FQN "
      f"'{fqn}' already exists. Use the update function for existing "
      f"definitions."
    )
    logger.error(error_message)
    raise ValueError(error_message)

  deck_type_orm = DeckDefinitionOrm(
    fqn=fqn,
    name=name,
    description=description,
    plr_category=plr_category,
    default_size_x_mm=default_size_x_mm,
    default_size_y_mm=default_size_y_mm,
    default_size_z_mm=default_size_z_mm,
    serialized_constructor_args_json=serialized_constructor_args_json,
    positioning_config_json=(positioning_config.model_dump() if positioning_config else None),
  )

  db.add(deck_type_orm)

  try:
    await db.flush()  # Flush to get the accession_id for the deck type

    if position_definitions:
      await _process_position_definitions(
        db,
        deck_type_orm,
        position_definitions,
        log_prefix,
      )

    await db.commit()
    await db.refresh(deck_type_orm)
    logger.info(
      "%s Successfully created new deck type definition with ID %s.",
      log_prefix,
      deck_type_orm.accession_id,
    )
    return deck_type_orm
  except IntegrityError as e:
    await db.rollback()
    error_message = f"{log_prefix} Integrity error creating deck type. Details: {e}"
    logger.exception(error_message)
    raise ValueError(error_message) from e
  except Exception as e:  # Catch all for truly unexpected errors
    await db.rollback()
    error_message = f"{log_prefix} Unexpected error creating deck type. Rolling back."
    logger.exception(error_message)
    raise e


async def update_deck_type_definition(
  db: AsyncSession,
  deck_type_accession_id: UUID,
  fqn: str,
  name: str,
  description: str | None = None,
  manufacturer: str | None = None,
  model: str | None = None,
  notes: str | None = None,
  plr_category: str | None = "deck",
  default_size_x_mm: float | None = None,
  default_size_y_mm: float | None = None,
  default_size_z_mm: float | None = None,
  positioning_config: PositioningConfig | None = None,
  serialized_constructor_args_json: dict[str, Any] | None = None,
  serialized_assignment_methods_json: dict[str, Any] | None = None,
  serialized_constructor_hints_json: dict[str, Any] | None = None,
  additional_properties_input_json: dict[str, Any] | None = None,
  position_definitions: list[dict[str, Any]] | None = None,
) -> DeckDefinitionOrm:
  """Update an existing deck type definition."""
  log_prefix = f"Deck Type Definition (ID: {deck_type_accession_id}, updating):"
  logger.info("%s Attempting to update.", log_prefix)

  # Fetch the existing deck type definition
  result = await db.execute(
    select(DeckDefinitionOrm)
    .options(selectinload(DeckDefinitionOrm.positions))
    .filter(DeckDefinitionOrm.accession_id == deck_type_accession_id),
  )
  deck_type_orm = result.scalar_one_or_none()
  if not deck_type_orm:
    error_message = f"{log_prefix} DeckTypeDefinitionOrm with id {deck_type_accession_id} not found for update."
    logger.error(error_message)
    raise ValueError(error_message)
  logger.info("%s Found existing deck type for update.", log_prefix)

  # Check for FQN conflict if it's being changed
  if deck_type_orm.fqn != fqn:
    existing_fqn_check = await db.execute(
      select(DeckDefinitionOrm)
      .filter(DeckDefinitionOrm.fqn == fqn)
      .filter(
        DeckDefinitionOrm.accession_id != deck_type_accession_id,
      ),  # Exclude the current record
    )
    if existing_fqn_check.scalar_one_or_none():
      error_message = (
        f"{log_prefix} Cannot update FQN to '{fqn}' as it already exists for another deck type definition."
      )
      logger.error(error_message)
      raise ValueError(error_message)

  # Update attributes
  deck_type_orm.fqn = fqn
  deck_type_orm.name = name
  deck_type_orm.plr_category = plr_category
  deck_type_orm.default_size_x_mm = default_size_x_mm
  deck_type_orm.default_size_y_mm = default_size_y_mm
  deck_type_orm.default_size_z_mm = default_size_z_mm

  if positioning_config is not None:
    if not isinstance(positioning_config, PositioningConfig):
      error_message = (
        f"{log_prefix} positioning_config must be an instance of PositioningConfig. "
        f"Received: {type(positioning_config)}"
      )
      logger.error(error_message)
      raise ValueError(error_message)
    deck_type_orm.positioning_config_json = positioning_config.model_dump()
    logger.debug("%s Set positioning_config_json.", log_prefix)
  else:
    deck_type_orm.positioning_config_json = None
    logger.debug("%s Cleared positioning_config_json.", log_prefix)

  deck_type_orm.serialized_constructor_args_json = serialized_constructor_args_json
  deck_type_orm.serialized_assignment_methods_json = serialized_assignment_methods_json
  deck_type_orm.serialized_constructor_hints_json = serialized_constructor_hints_json

  # Consolidate additional properties
  current_additional_properties = deck_type_orm.additional_properties_json or {}
  if additional_properties_input_json:
    logger.debug("%s Merging additional_properties_input_json.", log_prefix)
    current_additional_properties.update(additional_properties_input_json)
  if description is not None:
    current_additional_properties["description"] = description
  if manufacturer is not None:
    current_additional_properties["manufacturer"] = manufacturer
  if model is not None:
    current_additional_properties["model"] = model
  if notes is not None:
    current_additional_properties["notes"] = notes

  if current_additional_properties:
    deck_type_orm.additional_properties_json = current_additional_properties
    flag_modified(deck_type_orm, "additional_properties_json")
    logger.debug("%s Updated additional_properties_json.", log_prefix)

  try:
    await db.flush()  # Flush to ensure deck_type_orm.accession_id is correct for position ops
    logger.debug("%s Flushed deck type definition changes.", log_prefix)

    await _process_position_definitions(
      db,
      deck_type_orm,
      position_definitions,
      log_prefix,
    )

    await db.commit()
    await db.refresh(deck_type_orm)
    logger.info("%s Successfully committed updated deck type definition.", log_prefix)

    # Reload with position definitions
    refreshed_deck_type_result = await db.execute(
      select(DeckDefinitionOrm)
      .options(selectinload(DeckDefinitionOrm.positions))
      .filter(DeckDefinitionOrm.accession_id == deck_type_orm.accession_id),
    )
    deck_type_orm = refreshed_deck_type_result.scalar_one()
    logger.debug(
      "%s Refreshed deck type and reloaded position definitions after update.",
      log_prefix,
    )

  except IntegrityError as e:
    await db.rollback()
    if "uq_deck_type_definitions_fqn" in str(e.orig):
      error_message = f"{log_prefix} A deck type definition with PyLabRobot FQN '{fqn}' already exists. Details: {e}"
      logger.exception(error_message)
      raise ValueError(error_message) from e
    if "uq_deck_position" in str(e.orig):
      error_message = f"{log_prefix} A position definition with a conflicting name was attempted. Details: {e}"
      logger.exception(error_message)
      raise ValueError(error_message) from e
    error_message = f"{log_prefix} Database integrity error during update. Details: {e}"
    logger.exception(error_message)
    raise ValueError(error_message) from e
  except Exception as e:  # Catch all for truly unexpected errors
    await db.rollback()
    logger.exception("%s Unexpected error during update. Rolling back.", log_prefix)
    raise e

  logger.info("%s Update operation completed.", log_prefix)
  return deck_type_orm


async def read_deck_type_definition(
  db: AsyncSession,
  deck_type_accession_id: uuid.UUID,
) -> DeckDefinitionOrm | None:
  """Retrieve a specific deck type definition by its ID."""
  logger.info(
    "Attempting to retrieve deck type definition with ID: %s.",
    deck_type_accession_id,
  )
  stmt = (
    select(DeckDefinitionOrm)
    .options(selectinload(DeckDefinitionOrm.positions))
    .filter(DeckDefinitionOrm.accession_id == deck_type_accession_id)
  )
  result = await db.execute(stmt)
  deck_type_def = result.scalar_one_or_none()
  if deck_type_def:
    logger.info(
      "Successfully retrieved deck type definition ID %s: '%s'.",
      deck_type_accession_id,
      deck_type_def.name,
    )
  else:
    logger.info("Deck type definition with ID %s not found.", deck_type_accession_id)
  return deck_type_def


async def read_deck_type_definition_by_name(
  db: AsyncSession,
  name: str,
) -> DeckDefinitionOrm | None:
  """Retrieve a specific deck type definition by its name.

  Args:
      db (AsyncSession): The database session.
      name (str): The name of the deck type definition to retrieve.

  Returns:
      Optional[DeckTypeDefinitionOrm]: The deck type definition object
      if found, otherwise None.

  """
  logger.info("Attempting to retrieve deck type definition with name: '%s'.", name)
  stmt = (
    select(DeckDefinitionOrm)
    .options(selectinload(DeckDefinitionOrm.positions))
    .filter(DeckDefinitionOrm.name == name)
  )
  result = await db.execute(stmt)
  deck_type_def = result.scalar_one_or_none()
  if deck_type_def:
    logger.info(
      "Successfully retrieved deck type definition '%s' (ID: %s).",
      name,
      deck_type_def.accession_id,
    )
  else:
    logger.info("Deck type definition with name '%s' not found.", name)
  return deck_type_def


async def read_deck_type_definitions(
  db: AsyncSession,
  limit: int = 100,
  offset: int = 0,
) -> list[DeckDefinitionOrm]:
  """List all deck type definitions with pagination."""
  logger.info(
    "Listing deck type definitions with limit: %s, offset: %s.",
    limit,
    offset,
  )
  stmt = (
    select(DeckDefinitionOrm)
    .options(selectinload(DeckDefinitionOrm.positions))
    .order_by(DeckDefinitionOrm.name)
    .limit(limit)
    .offset(offset)
  )
  result = await db.execute(stmt)
  deck_type_defs = list(result.scalars().all())
  logger.info("Found %s deck type definitions.", len(deck_type_defs))
  return deck_type_defs


async def delete_deck_type_definition(
  db: AsyncSession,
  deck_type_accession_id: uuid.UUID,
) -> None:
  """Delete a deck type definition by its ID."""
  log_prefix = f"Deck Type Definition (ID: {deck_type_accession_id}, deleting):"
  logger.info("%s Attempting to delete.", log_prefix)

  deck_type_orm = await read_deck_type_definition(db, deck_type_accession_id)
  if not deck_type_orm:
    error_message = f"{log_prefix} DeckTypeDefinitionOrm with id {deck_type_accession_id} not found."
    logger.error(error_message)
    raise ValueError(error_message)

  try:
    await db.delete(deck_type_orm)
    await db.commit()
    logger.info("%s Successfully deleted.", log_prefix)
  except Exception as e:  # Catch all for truly unexpected errors
    await db.rollback()
    logger.exception("%s Unexpected error during deletion. Rolling back.", log_prefix)
    raise e
