# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""Service layer for Deck Data Management.

praxis/db_services/deck_data_service.py

Service layer for interacting with deck-related data in the database.
This includes Deck Configurations, Deck Types, and Deck Position Definitions.

This module provides functions to create, read, update, and delete deck instances,
deck type definitions, and deck position definitions.

It also includes functions to manage position definitions for deck types.
"""

import datetime
import logging
from typing import Any, Dict, List, Optional

import uuid_utils as uuid
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.attributes import flag_modified

from praxis.backend.models import (
  DeckInstanceOrm,
  DeckInstancePositionResourceOrm,
  DeckPositionDefinitionOrm,
  DeckTypeDefinitionOrm,
  MachineOrm,
  PositioningConfig,
  ResourceInstanceOrm,
)
from praxis.backend.utils.logging import get_logger

from .resource_type_definition import read_resource_definition

logger = get_logger(__name__)

UUID = uuid.UUID


async def _process_position_definitions(
  db: AsyncSession,
  deck_type_orm: DeckTypeDefinitionOrm,
  position_definitions_data: Optional[List[Dict[str, Any]]],
  log_prefix: str,
):
  """Handle the deletion and creation of position definitions.

  Helper function to handle the deletion and creation of position definitions.
  This logic is common to both create and update.

  Args:
    db (AsyncSession): The database session.
    deck_type_orm (DeckTypeDefinitionOrm): The deck type ORM object to which
      position definitions will be added.
    position_definitions_data (Optional[List[Dict[str, Any]]]): A list of dictionaries,
      each representing a position definition for this deck type.
    log_prefix (str): Prefix for logging messages to identify the operation.

  Raises:
    ValueError: If position definitions data is provided but not in the expected format.
    Exception: For any unexpected errors during the process.

  """
  if position_definitions_data is not None:
    logger.info(
      "%s Replacing existing position definitions with %s new ones.",
      log_prefix,
      len(position_definitions_data),
    )
    # Delete existing position definitions for this deck type
    if deck_type_orm.id:  # Ensure we have an ID to link positions
      existing_positions_stmt = select(DeckPositionDefinitionOrm).filter(
        DeckPositionDefinitionOrm.deck_type_definition_id == deck_type_orm.id
      )
      result = await db.execute(existing_positions_stmt)
      for position in result.scalars().all():
        logger.debug("%s Deleting existing position '%s'.", log_prefix, position.name)
        await db.delete(position)
      await db.flush()  # Process deletions to avoid conflicts with new additions
      logger.debug("%s Existing position definitions deleted.", log_prefix)

    # Add new position definitions
    for position_data in position_definitions_data:
      position_name = position_data.get(
        "position_name", "UNKNOWN_POSE"
      )  # Use position_name
      logger.debug(
        "%s Adding new position definition: '%s'.", log_prefix, position_name
      )
      position_specific_details = position_data.get(
        "position_specific_details_json", {}
      )

      # Map Pydantic fields to position_specific_details if not direct ORM fields
      if position_data.get("pylabrobot_position_type_name"):
        position_specific_details["pylabrobot_position_type_name"] = position_data[
          "pylabrobot_position_type_name"
        ]
      if position_data.get("allowed_resource_definition_names"):
        position_specific_details["allowed_resource_definition_names"] = position_data[
          "allowed_resource_definition_names"
        ]
      if position_data.get("accepts_tips") is not None:
        position_specific_details["accepts_tips"] = position_data["accepts_tips"]
      if position_data.get("accepts_plates") is not None:
        position_specific_details["accepts_plates"] = position_data["accepts_plates"]
      if position_data.get("accepts_tubes") is not None:
        position_specific_details["accepts_tubes"] = position_data["accepts_tubes"]
      if "notes" in position_data:
        position_specific_details["notes"] = position_data["notes"]

      new_position = DeckPositionDefinitionOrm(
        deck_type_definition_id=deck_type_orm.id,  # type: ignore
        position_name=position_name,
        nominal_x_mm=position_data.get("location_x_mm"),
        nominal_y_mm=position_data.get("location_y_mm"),
        nominal_z_mm=position_data.get("location_z_mm"),
        accepted_resource_categories_json=position_data.get(
          "allowed_resource_categories"
        ),
        position_specific_details_json=position_specific_details
        if position_specific_details
        else None,
      )
      db.add(new_position)


async def create_deck_type_definition(
  db: AsyncSession,
  python_fqn: str,
  deck_type: str,
  description: Optional[str] = None,
  manufacturer: Optional[str] = None,
  model: Optional[str] = None,
  notes: Optional[str] = None,
  plr_category: Optional[str] = "deck",
  default_size_x_mm: Optional[float] = None,
  default_size_y_mm: Optional[float] = None,
  default_size_z_mm: Optional[float] = None,
  positioning_config: Optional[PositioningConfig] = None,
  serialized_constructor_args_json: Optional[Dict[str, Any]] = None,
  serialized_assignment_methods_json: Optional[Dict[str, Any]] = None,
  serialized_constructor_hints_json: Optional[Dict[str, Any]] = None,
  additional_properties_input_json: Optional[Dict[str, Any]] = None,
  position_definitions_data: Optional[List[Dict[str, Any]]] = None,
) -> DeckTypeDefinitionOrm:
  """Create a new deck type definition.

  Args:
    db (AsyncSession): The database session.
    python_fqn (str): The fully qualified name of the PyLabRobot deck
      class (e.g., "pylabrobot.resources.Deck").
    deck_type (str): A human-readable display name for the deck type.
    description (Optional[str], optional): A description of the deck type.
      This will be stored in `additional_properties_json`. Defaults to None.
    manufacturer (Optional[str], optional): The manufacturer of the deck type.
      This will be stored in `additional_properties_json`. Defaults to None.
    model (Optional[str], optional): The model name of the deck type.
      This will be stored in `additional_properties_json`. Defaults to None.
    notes (Optional[str], optional): Any additional notes about the deck type.
      This will be stored in `additional_properties_json`. Defaults to None.
    plr_category (Optional[str], optional): The PyLabRobot category for the deck
      (e.g., "deck", "plate"). Defaults to "deck".
    default_size_x_mm (Optional[float], optional): The default X dimension in mm.
      Defaults to None.
    default_size_y_mm (Optional[float], optional): The default Y dimension in mm.
      Defaults to None.
    default_size_z_mm (Optional[float], optional): The default Z dimension in mm.
      Defaults to None.
    positioning_config (Optional[PositioningConfig], optional): Configuration for
      positioning of the deck. Specifies how positions are encoded for the particular
      deck sublcass.
    serialized_constructor_args_json (Optional[Dict[str, Any]], optional): JSON
      string of constructor arguments for PyLabRobot instantiation. Defaults to None.
    serialized_assignment_methods_json (Optional[Dict[str, Any]], optional): JSON
      string of assignment methods for PyLabRobot instantiation. Defaults to None.
    serialized_constructor_hints_json (Optional[Dict[str, Any]], optional):
      JSON string of config hints for PyLabRobot instantiation. Defaults to None.
    additional_properties_input_json (Optional[Dict[str, Any]], optional): A dictionary
      of additional properties to store as JSON. Keys in this dictionary will
      override `description`, `manufacturer`, `model`, `notes` if also provided.
      Defaults to None.
    position_definitions_data (Optional[List[Dict[str, Any]]], optional): A list of
      dictionaries, each representing a position definition for this deck type. Each
      dictionary should contain:
      - 'position_name' (str): The unique name of the position.
      - 'location_x_mm' (Optional[float]): Nominal X coordinate of the position.
      - 'location_y_mm' (Optional[float]): Nominal Y coordinate of the position.
      - 'location_z_mm' (Optional[float]): Nominal Z coordinate of the position.
      - 'allowed_resource_categories' (Optional[List[str]]): List of resource
        categories allowed at this position.
      - 'pylabrobot_position_type_name' (Optional[str]): PyLabRobot specific position
      type.
      - 'allowed_resource_definition_names' (Optional[List[str]]): Specific
        resource definition names allowed.
      - 'accepts_tips' (Optional[bool]): If the position accepts tips.
      - 'accepts_plates' (Optional[bool]): If the position accepts plates.
      - 'accepts_tubes' (Optional[bool]): If the position accepts tubes.
      - 'notes' (Optional[str]): Any specific notes for the position.
      If provided, existing position definitions for this deck type will be deleted
      and replaced with these. Defaults to None.

  Returns:
    DeckTypeDefinitionOrm: The created deck type definition object.

  Raises:
    ValueError: If a deck type definition with the same `python_fqn` already exists.
    Exception: For any other unexpected errors during the process.

  """
  log_prefix = f"Deck Type Definition (FQN: '{python_fqn}', creating new):"
  logger.info("%s Attempting to create.", log_prefix)

  # Check if a deck type with this FQN already exists
  result = await db.execute(
    select(DeckTypeDefinitionOrm).filter(
      DeckTypeDefinitionOrm.pylabrobot_deck_fqn == python_fqn
    )
  )
  if result.scalar_one_or_none():
    error_message = (
      f"{log_prefix} A deck type definition with PyLabRobot FQN "
      f"'{python_fqn}' already exists. Use the update function for existing definitions."
    )
    logger.error(error_message)
    raise ValueError(error_message)

  # Create a new deck type definition
  deck_type_orm = DeckTypeDefinitionOrm(pylabrobot_deck_fqn=python_fqn)
  db.add(deck_type_orm)
  logger.info("%s Initialized new deck type for creation.", log_prefix)

  # Update attributes
  deck_type_orm.display_name = deck_type
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
    await db.flush()  # Flush to get the new deck_type_orm.id for position definitions
    logger.debug("%s Flushed new deck type definition to get ID.", log_prefix)

    await _process_position_definitions(
      db, deck_type_orm, position_definitions_data, log_prefix
    )

    await db.commit()
    await db.refresh(deck_type_orm)  # Refresh to load newly added positions
    logger.info("%s Successfully committed new deck type definition.", log_prefix)

    # Reload with position definitions
    refreshed_deck_type_result = await db.execute(
      select(DeckTypeDefinitionOrm)
      .options(selectinload(DeckTypeDefinitionOrm.position_definitions))
      .filter(DeckTypeDefinitionOrm.id == deck_type_orm.id)
    )
    deck_type_orm = refreshed_deck_type_result.scalar_one()
    logger.debug(
      "%s Refreshed deck type and loaded position definitions after creation.",
      log_prefix,
    )

  except IntegrityError as e:
    await db.rollback()
    if "uq_deck_type_definitions_pylabrobot_deck_fqn" in str(e.orig):
      error_message = (
        f"{log_prefix} A deck type definition with PyLabRobot FQN "
        f"'{python_fqn}' already exists (integrity check failed). Details: {e}"
      )
      logger.error(error_message, exc_info=True)
      raise ValueError(error_message) from e
    if "uq_deck_position_definition" in str(e.orig):
      error_message = f"{log_prefix} A position definition with a conflicting name was \
        attempted. Details: {e}"
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
  return deck_type_orm


async def update_deck_type_definition(
  db: AsyncSession,
  deck_type_id: int,
  python_fqn: str,
  deck_type: str,
  description: Optional[str] = None,
  manufacturer: Optional[str] = None,
  model: Optional[str] = None,
  notes: Optional[str] = None,
  plr_category: Optional[str] = "deck",
  default_size_x_mm: Optional[float] = None,
  default_size_y_mm: Optional[float] = None,
  default_size_z_mm: Optional[float] = None,
  positioning_config: Optional[PositioningConfig] = None,
  serialized_constructor_args_json: Optional[Dict[str, Any]] = None,
  serialized_assignment_methods_json: Optional[Dict[str, Any]] = None,
  serialized_constructor_hints_json: Optional[Dict[str, Any]] = None,
  additional_properties_input_json: Optional[Dict[str, Any]] = None,
  position_definitions_data: Optional[List[Dict[str, Any]]] = None,
) -> DeckTypeDefinitionOrm:
  """Update an existing deck type definition.

  Args:
    db (AsyncSession): The database session.
    deck_type_id (int): The ID of the existing deck type definition to update.
    python_fqn (str): The fully qualified name of the PyLabRobot deck
      class. This will update the existing FQN.
    deck_type (str): A human-readable display name for the deck type.
    description (Optional[str], optional): A description of the deck type.
      This will be stored in `additional_properties_json`. Defaults to None.
    manufacturer (Optional[str], optional): The manufacturer of the deck type.
      This will be stored in `additional_properties_json`. Defaults to None.
    model (Optional[str], optional): The model name of the deck type.
      This will be stored in `additional_properties_json`. Defaults to None.
    notes (Optional[str], optional): Any additional notes about the deck type.
      This will be stored in `additional_properties_json`. Defaults to None.
    plr_category (Optional[str], optional): The PyLabRobot category for the deck
      (e.g., "deck", "plate"). Defaults to "deck".
    default_size_x_mm (Optional[float], optional): The default X dimension in mm.
      Defaults to None.
    default_size_y_mm (Optional[float], optional): The default Y dimension in mm.
      Defaults to None.
    default_size_z_mm (Optional[float], optional): The default Z dimension in mm.
      Defaults to None.
    positioning_config (Optional[PositioningConfig], optional): Configuration for
      positioning of the deck. Specifies how positions are encoded for the particular
      deck sublcass.
    serialized_constructor_args_json (Optional[Dict[str, Any]], optional): JSON
      string of constructor arguments for PyLabRobot instantiation. Defaults to None.
    serialized_assignment_methods_json (Optional[Dict[str, Any]], optional): JSON
      string of assignment methods for PyLabRobot instantiation. Defaults to None.
    serialized_constructor_hints_json (Optional[Dict[str, Any]], optional):
      JSON string of config hints for PyLabRobot instantiation. Defaults to None.
    additional_properties_input_json (Optional[Dict[str, Any]], optional): A dictionary
      of additional properties to store as JSON. Keys in this dictionary will
      override `description`, `manufacturer`, `model`, `notes` if also provided.
      Defaults to None.
    position_definitions_data (Optional[List[Dict[str, Any]]], optional): A list of
      dictionaries, each representing a position definition for this deck type. Each
      dictionary should contain:
      - 'position_name' (str): The unique name of the position.
      - 'location_x_mm' (Optional[float]): Nominal X coordinate of the position.
      - 'location_y_mm' (Optional[float]): Nominal Y coordinate of the position.
      - 'location_z_mm' (Optional[float]): Nominal Z coordinate of the position.
      - 'allowed_resource_categories' (Optional[List[str]]): List of resource
        categories allowed at this position.
      - 'pylabrobot_position_type_name' (Optional[str]): PyLabRobot specific position
      type.
      - 'allowed_resource_definition_names' (Optional[List[str]]): Specific
        resource definition names allowed.
      - 'accepts_tips' (Optional[bool]): If the position accepts tips.
      - 'accepts_plates' (Optional[bool]): If the position accepts plates.
      - 'accepts_tubes' (Optional[bool]): If the position accepts tubes.
      - 'notes' (Optional[str]): Any specific notes for the position.
      If provided, existing position definitions for this deck type will be deleted
      and replaced with these. Defaults to None.

  Returns:
    DeckTypeDefinitionOrm: The updated deck type definition object.

  Raises:
    ValueError: If `deck_type_id` is provided but no matching deck type is found,
                or if the updated `python_fqn` conflicts with an existing one.
    Exception: For any other unexpected errors during the process.

  """
  log_prefix = f"Deck Type Definition (ID: {deck_type_id}, updating):"
  logger.info("%s Attempting to update.", log_prefix)

  # Fetch the existing deck type definition
  result = await db.execute(
    select(DeckTypeDefinitionOrm)
    .options(selectinload(DeckTypeDefinitionOrm.position_definitions))
    .filter(DeckTypeDefinitionOrm.id == deck_type_id)
  )
  deck_type_orm = result.scalar_one_or_none()
  if not deck_type_orm:
    error_message = (
      f"{log_prefix} DeckTypeDefinitionOrm with id {deck_type_id} not found for update."
    )
    logger.error(error_message)
    raise ValueError(error_message)
  logger.info("%s Found existing deck type for update.", log_prefix)

  # Check for FQN conflict if it's being changed
  if deck_type_orm.pylabrobot_deck_fqn != python_fqn:
    existing_fqn_check = await db.execute(
      select(DeckTypeDefinitionOrm)
      .filter(DeckTypeDefinitionOrm.pylabrobot_deck_fqn == python_fqn)
      .filter(DeckTypeDefinitionOrm.id != deck_type_id)  # Exclude the current record
    )
    if existing_fqn_check.scalar_one_or_none():
      error_message = (
        f"{log_prefix} Cannot update FQN to '{python_fqn}' as it already "
        f"exists for another deck type definition."
      )
      logger.error(error_message)
      raise ValueError(error_message)

  # Update attributes
  deck_type_orm.pylabrobot_deck_fqn = python_fqn
  deck_type_orm.display_name = deck_type
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
    await db.flush()  # Flush to ensure deck_type_orm.id is correct for position ops
    logger.debug("%s Flushed deck type definition changes.", log_prefix)

    await _process_position_definitions(
      db, deck_type_orm, position_definitions_data, log_prefix
    )

    await db.commit()
    await db.refresh(deck_type_orm)
    logger.info("%s Successfully committed updated deck type definition.", log_prefix)

    # Reload with position definitions
    refreshed_deck_type_result = await db.execute(
      select(DeckTypeDefinitionOrm)
      .options(selectinload(DeckTypeDefinitionOrm.position_definitions))
      .filter(DeckTypeDefinitionOrm.id == deck_type_orm.id)
    )
    deck_type_orm = refreshed_deck_type_result.scalar_one()
    logger.debug(
      "%s Refreshed deck type and reloaded position definitions after update.",
      log_prefix,
    )

  except IntegrityError as e:
    await db.rollback()
    if "uq_deck_type_definitions_pylabrobot_deck_fqn" in str(e.orig):
      error_message = (
        f"{log_prefix} A deck type definition with PyLabRobot FQN "
        f"'{python_fqn}' already exists. Details: {e}"
      )
      logger.error(error_message, exc_info=True)
      raise ValueError(error_message) from e
    if "uq_deck_position_definition" in str(e.orig):
      error_message = f"{log_prefix} A position definition with a conflicting name was\
        attempted. Details: {e}"
      logger.error(error_message, exc_info=True)
      raise ValueError(error_message) from e
    error_message = f"{log_prefix} Database integrity error during update. Details: {e}"
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception("%s Unexpected error during update. Rolling back.", log_prefix)
    raise e

  logger.info("%s Update operation completed.", log_prefix)
  return deck_type_orm


async def read_deck_type_definition(
  db: AsyncSession, deck_type_id: uuid.UUID
) -> Optional[DeckTypeDefinitionOrm]:
  """Retrieve a specific deck type definition by its ID.

  Args:
    db (AsyncSession): The database session.
    deck_type_id (uuid.UUID): The ID of the deck type definition to retrieve.

  Returns:
    Optional[DeckTypeDefinitionOrm]: The deck type definition object if found,
    otherwise None.

  """
  logger.info("Attempting to retrieve deck type definition with ID: %s.", deck_type_id)
  stmt = (
    select(DeckTypeDefinitionOrm)
    .options(selectinload(DeckTypeDefinitionOrm.position_definitions))
    .filter(DeckTypeDefinitionOrm.id == deck_type_id)
  )
  result = await db.execute(stmt)
  deck_type_def = result.scalar_one_or_none()
  if deck_type_def:
    logger.info(
      "Successfully retrieved deck type definition ID %s: '%s'.",
      deck_type_id,
      deck_type_def.display_name,
    )
  else:
    logger.info("Deck type definition with ID %s not found.", deck_type_id)
  return deck_type_def


async def read_deck_type_definition_by_fqn(
  db: AsyncSession, pylabrobot_deck_fqn: str
) -> Optional[DeckTypeDefinitionOrm]:
  """Retrieve a specific deck type definition by its PyLabRobot FQN.

  Args:
    db (AsyncSession): The database session.
    pylabrobot_deck_fqn (str): The fully qualified name of the PyLabRobot deck class.

  Returns:
    Optional[DeckTypeDefinitionOrm]: The deck type definition object if found,
    otherwise None.

  """
  logger.info(
    "Attempting to retrieve deck type definition by FQN: '%s'.", pylabrobot_deck_fqn
  )
  stmt = (
    select(DeckTypeDefinitionOrm)
    .options(selectinload(DeckTypeDefinitionOrm.position_definitions))
    .filter(DeckTypeDefinitionOrm.pylabrobot_deck_fqn == pylabrobot_deck_fqn)
  )
  result = await db.execute(stmt)
  deck_type_def = result.scalar_one_or_none()
  if deck_type_def:
    logger.info(
      "Successfully retrieved deck type definition by FQN '%s'.", pylabrobot_deck_fqn
    )
  else:
    logger.info("Deck type definition with FQN '%s' not found.", pylabrobot_deck_fqn)
  return deck_type_def


async def list_deck_type_definitions(
  db: AsyncSession, limit: int = 100, offset: int = 0
) -> List[DeckTypeDefinitionOrm]:
  """List all deck type definitions with pagination, including their position definitions.

  Args:
    db (AsyncSession): The database session.
    limit (int): The maximum number of results to return. Defaults to 100.
    offset (int): The number of results to skip before returning. Defaults to 0.

  Returns:
    List[DeckTypeDefinitionOrm]: A list of deck type definition objects.

  """
  logger.info(
    "Listing deck type definitions with limit: %s, offset: %s.", limit, offset
  )
  stmt = (
    select(DeckTypeDefinitionOrm)
    .options(selectinload(DeckTypeDefinitionOrm.position_definitions))
    .order_by(DeckTypeDefinitionOrm.display_name)
    .limit(limit)
    .offset(offset)
  )
  result = await db.execute(stmt)
  deck_type_defs = list(result.scalars().all())
  logger.info("Found %s deck type definitions.", len(deck_type_defs))
  return deck_type_defs


async def delete_deck_type_definition(
  db: AsyncSession, deck_type_id: uuid.UUID
) -> None:
  """Delete a deck type definition by its ID.

  Args:
    db (AsyncSession): The database session.
    deck_type_id (uuid.UUID): The ID of the deck type definition to delete.

  Raises:
    ValueError: If the deck type definition does not exist.
    Exception: For any other unexpected errors during the deletion process.

  """
  log_prefix = f"Deck Type Definition (ID: {deck_type_id}, deleting):"
  logger.info("%s Attempting to delete.", log_prefix)

  stmt = select(DeckTypeDefinitionOrm).filter(DeckTypeDefinitionOrm.id == deck_type_id)
  result = await db.execute(stmt)
  deck_type_orm = result.scalar_one_or_none()
  if not deck_type_orm:
    error_message = (
      f"{log_prefix} DeckTypeDefinitionOrm with id {deck_type_id} not found."
    )
    logger.error(error_message)
    raise ValueError(error_message)

  try:
    await db.delete(deck_type_orm)
    await db.commit()
    logger.info("%s Successfully deleted.", log_prefix)
  except Exception as e:
    await db.rollback()
    logger.exception("%s Unexpected error during deletion. Rolling back.", log_prefix)
    raise e
