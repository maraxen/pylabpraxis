# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""Service layer for Deck Data Management.

praxis/db_services/deck_data_service.py

Service layer for interacting with deck-related data in the database.
This includes Deck Configurations, Deck Types, and Deck Pose Definitions.

This module provides functions to create, read, update, and delete deck layouts,
deck type definitions, and deck pose definitions.

It also includes functions to manage pose definitions for deck types.
"""

import datetime
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.attributes import flag_modified

from praxis.backend.models import (
  DeckConfigurationOrm,
  DeckConfigurationPoseItemOrm,
  DeckPoseDefinitionOrm,
  DeckTypeDefinitionOrm,
  MachineOrm,
  ResourceInstanceOrm,
)
from praxis.backend.services.resource_data_service import get_resource_definition

logger = logging.getLogger(__name__)


async def create_deck_layout(
  db: AsyncSession,
  layout_name: str,
  deck_machine_id: int,
  description: Optional[str] = None,
  pose_items_data: Optional[List[Dict[str, Any]]] = None,
) -> DeckConfigurationOrm:
  """Create a new deck layout configuration with optional posed items.

  This function creates a deck layout configuration and associates it with a deck
  machine. It can also create posed items for the deck layout if `pose_items_data`
  is provided.

  Args:
    db (AsyncSession): The database session.
    layout_name (str): The name of the deck layout.
    deck_machine_id (int): The ID of the deck machine to associate with this layout.
    description (Optional[str], optional): Description of the deck layout.
      Defaults to None.
    pose_items_data (Optional[List[Dict[str, Any]]], optional): List of pose items
      data. Each dictionary in the list should contain:
      - 'pose_name' (str): The name of the pose.
      - 'resource_instance_id' (Optional[int]): The ID of the resource instance
        associated with this pose (optional).
      - 'expected_resource_definition_name' (Optional[str]): The name of the
        expected resource definition for this pose (optional).
      Defaults to None.

  Returns:
    DeckConfigurationOrm: The created deck layout configuration object.

  Raises:
    ValueError: If:
      - The specified deck machine ID doesn't exist.
      - A deck layout with the same name already exists.
      - A specified resource instance ID doesn't exist.
      - A specified resource definition name doesn't exist.
    Exception: For any other unexpected errors during the process.

  """
  logger.info(
    "Attempting to create deck layout '%s' for machine ID %d.",
    layout_name,
    deck_machine_id,
  )

  deck_machine_result = await db.execute(
    select(MachineOrm).filter(MachineOrm.id == deck_machine_id)
  )
  deck_machine = deck_machine_result.scalar_one_or_none()
  if not deck_machine:
    error_message = (
      f"MachineOrm (Deck Device) with id {deck_machine_id} not found. "
      "Cannot create deck layout."
    )
    logger.error(error_message)
    raise ValueError(error_message)

  deck_layout_orm = DeckConfigurationOrm(
    layout_name=layout_name,
    deck_machine_id=deck_machine_id,
    description=description,
  )
  db.add(deck_layout_orm)

  try:
    await db.flush()
    logger.info("Successfully flushed new deck layout with name '%s'.", layout_name)
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"DeckConfigurationOrm with layout name '{layout_name}' "
      f"already exists. Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    logger.exception("Error flushing new deck layout '%s'. Rolling back.", layout_name)
    await db.rollback()
    raise e

  if pose_items_data:
    logger.info(
      "Processing %d pose items for deck layout '%s'.",
      len(pose_items_data),
      layout_name,
    )
    for item_data in pose_items_data:
      pose_name = item_data.get("pose_name", "N/A")
      resource_instance_id = item_data.get("resource_instance_id")
      expected_def_name = item_data.get("expected_resource_definition_name")

      if resource_instance_id:
        resource_instance_result = await db.execute(
          select(ResourceInstanceOrm).filter(
            ResourceInstanceOrm.id == resource_instance_id
          )
        )
        if not resource_instance_result.scalar_one_or_none():
          await db.rollback()
          error_message = (
            f"ResourceInstanceOrm with id {resource_instance_id} for pose "
            f"'{pose_name}' not found. Rolling back."
          )
          logger.error(error_message)
          raise ValueError(error_message)

      if expected_def_name:
        if not await get_resource_definition(db, expected_def_name):
          await db.rollback()
          error_message = (
            f"ResourceDefinitionCatalogOrm with name '{expected_def_name}' for pose "
            f"'{pose_name}' not found. Rolling back."
          )
          logger.error(error_message)
          raise ValueError(error_message)

      pose_item = DeckConfigurationPoseItemOrm(
        deck_configuration_id=deck_layout_orm.id,
        pose_name=pose_name,
        resource_instance_id=resource_instance_id,
        expected_resource_definition_name=expected_def_name,
      )
      db.add(pose_item)
      logger.debug("Added pose item '%s' to deck layout '%s'.", pose_name, layout_name)

  try:
    await db.commit()
    await db.refresh(deck_layout_orm)
    logger.info(
      "Successfully committed deck layout '%s' and its pose items.", layout_name
    )
    # Eagerly load pose_items for the returned object
    if deck_layout_orm.id:
      return await get_deck_layout_by_id(db, deck_layout_orm.id)  # type: ignore
    return deck_layout_orm  # Should not be reached if ID is None after flush/commit
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Integrity error while creating deck layout '{layout_name}' or its pose items. "
      f"Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error creating deck layout '%s' or its pose items. Rolling back.",
      layout_name,
    )
    raise e


async def get_deck_layout_by_id(
  db: AsyncSession, deck_layout_id: int
) -> Optional[DeckConfigurationOrm]:
  """Retrieve a specific deck layout configuration by its ID.

  This function retrieves a deck layout configuration along with its pose items,
  including the associated resource instances and their definitions.

  Args:
    db (AsyncSession): The database session.
    deck_layout_id (int): The ID of the deck layout to retrieve.

  Returns:
    Optional[DeckConfigurationOrm]: The deck layout configuration object if found,
    otherwise None.

  """
  logger.info("Attempting to retrieve deck layout with ID: %d.", deck_layout_id)
  stmt = (
    select(DeckConfigurationOrm)
    .options(
      selectinload(DeckConfigurationOrm.pose_items)
      .selectinload(DeckConfigurationPoseItemOrm.resource_instance)
      .selectinload(ResourceInstanceOrm.resource_definition),
      selectinload(DeckConfigurationOrm.pose_items).selectinload(
        DeckConfigurationPoseItemOrm.expected_resource_definition
      ),
    )
    .filter(DeckConfigurationOrm.id == deck_layout_id)
  )
  result = await db.execute(stmt)
  deck_layout = result.scalar_one_or_none()
  if deck_layout:
    logger.info(
      "Successfully retrieved deck layout ID %d: '%s'.",
      deck_layout_id,
      deck_layout.layout_name,
    )
  else:
    logger.info("Deck layout with ID %d not found.", deck_layout_id)
  return deck_layout


async def get_deck_layout_by_name(
  db: AsyncSession, layout_name: str
) -> Optional[DeckConfigurationOrm]:
  """Retrieve a specific deck layout configuration by its name.

  This function retrieves a deck layout configuration along with its pose items,
  including the associated resource instances and their definitions.

  Args:
    db (AsyncSession): The database session.
    layout_name (str): The name of the deck layout to retrieve.

  Returns:
    Optional[DeckConfigurationOrm]: The deck layout configuration object if found,
    otherwise None.

  """
  logger.info("Attempting to retrieve deck layout with name: '%s'.", layout_name)
  stmt = (
    select(DeckConfigurationOrm)
    .options(
      selectinload(DeckConfigurationOrm.pose_items)
      .selectinload(DeckConfigurationPoseItemOrm.resource_instance)
      .selectinload(ResourceInstanceOrm.resource_definition),
      selectinload(DeckConfigurationOrm.pose_items).selectinload(
        DeckConfigurationPoseItemOrm.expected_resource_definition
      ),
    )
    .filter(DeckConfigurationOrm.layout_name == layout_name)
  )
  result = await db.execute(stmt)
  deck_layout = result.scalar_one_or_none()
  if deck_layout:
    logger.info("Successfully retrieved deck layout by name '%s'.", layout_name)
  else:
    logger.info("Deck layout with name '%s' not found.", layout_name)
  return deck_layout


async def list_deck_layouts(
  db: AsyncSession,
  deck_machine_id: Optional[int] = None,
  limit: int = 100,
  offset: int = 0,
) -> List[DeckConfigurationOrm]:
  """List all deck layouts with optional filtering by deck machine ID.

  This function retrieves a list of deck layout configurations, including their pose
  items, associated resource instances, and their definitions.

  Args:
    db (AsyncSession): The database session.
    deck_machine_id (Optional[int]): The ID of the deck machine to filter by.
      Defaults to None, meaning no filtering by machine ID.
    limit (int): The maximum number of results to return. Defaults to 100.
    offset (int): The number of results to skip before returning. Defaults to 0.

  Returns:
    List[DeckConfigurationOrm]: A list of deck layout configuration objects.

  """
  logger.info(
    "Listing deck layouts with machine ID filter: %s, limit: %d, offset: %d.",
    deck_machine_id,
    limit,
    offset,
  )
  stmt = select(DeckConfigurationOrm).options(
    selectinload(DeckConfigurationOrm.pose_items)
    .selectinload(DeckConfigurationPoseItemOrm.resource_instance)
    .selectinload(ResourceInstanceOrm.resource_definition),
    selectinload(DeckConfigurationOrm.pose_items).selectinload(
      DeckConfigurationPoseItemOrm.expected_resource_definition
    ),
  )
  if deck_machine_id is not None:
    stmt = stmt.filter(DeckConfigurationOrm.deck_machine_id == deck_machine_id)
  stmt = stmt.order_by(DeckConfigurationOrm.layout_name).limit(limit).offset(offset)
  result = await db.execute(stmt)
  deck_layouts = list(result.scalars().all())
  logger.info("Found %d deck layouts.", len(deck_layouts))
  return deck_layouts


async def update_deck_layout(
  db: AsyncSession,
  deck_layout_id: int,
  name: Optional[str] = None,
  description: Optional[str] = None,
  deck_machine_id: Optional[int] = None,
  pose_items_data: Optional[List[Dict[str, Any]]] = None,
) -> Optional[DeckConfigurationOrm]:
  """Update an existing deck layout configuration.

  Updates the specified deck layout with new values for its name, description,
  associated deck machine, and pose items. If `pose_items_data` is provided,
  it will replace the existing pose items for the deck layout.

  Args:
    db (AsyncSession): The database session.
    deck_layout_id (int): The ID of the deck layout to update.
    name (Optional[str], optional): The new name for the deck layout. Defaults to None.
    description (Optional[str], optional): The new description for the deck layout.
      Defaults to None.
    deck_machine_id (Optional[int], optional): The ID of the new deck machine to
      associate with this layout. Defaults to None.
    pose_items_data (Optional[List[Dict[str, Any]]], optional): A list of new pose
      items data. Each dictionary in the list should contain:
      - 'pose_name' (str): The name of the pose.
      - 'resource_instance_id' (Optional[int]): The ID of the resource instance
        associated with this pose (optional).
      - 'expected_resource_definition_name' (Optional[str]): The name of the
        expected resource definition for this pose (optional).
      If provided, existing pose items for this layout will be deleted and
      replaced with these. Defaults to None.

  Returns:
    Optional[DeckConfigurationOrm]: The updated deck layout configuration object
    if successful, otherwise None if the layout was not found.

  Raises:
    ValueError: If:
      - The new deck machine ID does not exist.
      - A specified resource instance ID does not exist.
      - A specified resource definition name does not exist.
    Exception: For any other unexpected errors during the process.

  """
  logger.info("Attempting to update deck layout with ID: %d.", deck_layout_id)
  deck_layout_orm = await get_deck_layout_by_id(db, deck_layout_id)
  if not deck_layout_orm:
    logger.warning("Deck layout with ID %d not found for update.", deck_layout_id)
    return None

  original_layout_name = deck_layout_orm.layout_name
  updates_made = False

  if name is not None and deck_layout_orm.layout_name != name:
    logger.debug(
      "Updating layout name from '%s' to '%s'.", deck_layout_orm.layout_name, name
    )
    deck_layout_orm.layout_name = name
    updates_made = True
  if description is not None and deck_layout_orm.description != description:
    logger.debug("Updating description for layout '%s'.", original_layout_name)
    deck_layout_orm.description = description
    updates_made = True
  if deck_machine_id is not None and deck_layout_orm.deck_machine_id != deck_machine_id:
    logger.debug(
      "Updating deck machine ID from %d to %d for layout '%s'.",
      deck_layout_orm.deck_machine_id,
      deck_machine_id,
      original_layout_name,
    )
    new_deck_machine_result = await db.execute(
      select(MachineOrm).filter(MachineOrm.id == deck_machine_id)
    )
    if not new_deck_machine_result.scalar_one_or_none():
      error_message = (
        f"New MachineOrm (Deck Device) with id {deck_machine_id} not found. "
        f"Cannot update deck layout '{original_layout_name}'."
      )
      logger.error(error_message)
      raise ValueError(error_message)
    deck_layout_orm.deck_machine_id = deck_machine_id
    updates_made = True

  if pose_items_data is not None:
    logger.info("Replacing pose items for deck layout '%s'.", original_layout_name)
    # Delete existing pose items
    if deck_layout_orm.pose_items:
      for item in deck_layout_orm.pose_items:
        logger.debug(
          "Deleting existing pose item '%s' for layout '%s'.",
          item.pose_name,
          original_layout_name,
        )
        await db.delete(item)
    await db.flush()  # Process deletions before adding new ones
    updates_made = True

    # Add new pose items
    for item_data in pose_items_data:
      pose_name = item_data.get("pose_name", "N/A")
      resource_instance_id = item_data.get("resource_instance_id")
      expected_def_name = item_data.get("expected_resource_definition_name")

      if resource_instance_id:
        resource_instance_result = await db.execute(
          select(ResourceInstanceOrm).filter(
            ResourceInstanceOrm.id == resource_instance_id
          )
        )
        if not resource_instance_result.scalar_one_or_none():
          await db.rollback()
          error_message = (
            f"ResourceInstanceOrm with id {resource_instance_id} for pose "
            f"'{pose_name}' not found. Rolling back update for layout "
            f"'{original_layout_name}'."
          )
          logger.error(error_message)
          raise ValueError(error_message)

      if expected_def_name:
        if not await get_resource_definition(db, expected_def_name):
          await db.rollback()
          error_message = (
            f"ResourceDefinitionCatalogOrm with name '{expected_def_name}' for pose "
            f"'{pose_name}' not found. Rolling back update for layout "
            f"'{original_layout_name}'."
          )
          logger.error(error_message)
          raise ValueError(error_message)

      pose_item = DeckConfigurationPoseItemOrm(
        deck_configuration_id=deck_layout_orm.id,
        pose_name=pose_name,
        resource_instance_id=resource_instance_id,
        expected_resource_definition_name=expected_def_name,
      )
      db.add(pose_item)
      logger.debug(
        "Added new pose item '%s' to layout '%s'.", pose_name, original_layout_name
      )

  if not updates_made:
    logger.info(
      "No changes detected for deck layout ID %d. No update performed.", deck_layout_id
    )
    return deck_layout_orm  # Return the original object if no changes were applied

  try:
    await db.commit()
    await db.refresh(deck_layout_orm)
    logger.info(
      "Successfully updated deck layout ID %d: '%s'.",
      deck_layout_id,
      deck_layout_orm.layout_name,
    )
    return await get_deck_layout_by_id(db, deck_layout_id)  # Reload with all relations
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Integrity error while updating deck layout '{original_layout_name}' (ID: {deck_layout_id}). "
      f"Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error updating deck layout '%s' (ID: %d). Rolling back.",
      original_layout_name,
      deck_layout_id,
    )
    raise e


async def delete_deck_layout(db: AsyncSession, deck_layout_id: int) -> bool:
  """Delete a specific deck layout configuration by its ID.

  This function deletes a deck layout configuration and all its associated pose items.

  Args:
    db (AsyncSession): The database session.
    deck_layout_id (int): The ID of the deck layout to delete.

  Returns:
    bool: True if the deletion was successful, False if the layout was not found.

  Raises:
    Exception: For any unexpected errors during deletion.

  """
  logger.info("Attempting to delete deck layout with ID: %d.", deck_layout_id)
  deck_layout_orm = await get_deck_layout_by_id(db, deck_layout_id)
  if not deck_layout_orm:
    logger.warning("Deck layout with ID %d not found for deletion.", deck_layout_id)
    return False

  try:
    await db.delete(deck_layout_orm)
    await db.commit()
    logger.info(
      "Successfully deleted deck layout ID %d: '%s'.",
      deck_layout_id,
      deck_layout_orm.layout_name,
    )
    return True
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Integrity error deleting deck layout ID {deck_layout_id}. "
      f"This might be due to foreign key constraints. Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    return False  # Return False as deletion failed due to integrity
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error deleting deck layout ID %d. Rolling back.", deck_layout_id
    )
    raise e


async def add_or_update_deck_type_definition(
  db: AsyncSession,
  pylabrobot_class_name: str,
  praxis_deck_type_name: str,
  deck_type_id: Optional[int] = None,
  description: Optional[str] = None,
  manufacturer: Optional[str] = None,
  model: Optional[str] = None,
  notes: Optional[str] = None,
  plr_category: Optional[str] = "deck",
  default_size_x_mm: Optional[float] = None,
  default_size_y_mm: Optional[float] = None,
  default_size_z_mm: Optional[float] = None,
  serialized_constructor_args_json: Optional[Dict[str, Any]] = None,
  serialized_assignment_methods_json: Optional[Dict[str, Any]] = None,
  serialized_constructor_layout_hints_json: Optional[Dict[str, Any]] = None,
  additional_properties_input_json: Optional[Dict[str, Any]] = None,
  pose_definitions_data: Optional[List[Dict[str, Any]]] = None,
) -> DeckTypeDefinitionOrm:
  """Add a new deck type definition or updates an existing one.

  This function creates a new `DeckTypeDefinitionOrm` if `deck_type_id` is not
  provided and no existing definition matches `pylabrobot_class_name`. If
  `deck_type_id` is provided, it attempts to update the existing definition.
  If `pose_definitions_data` is provided, all existing pose definitions for this
  deck type will be deleted and replaced with the new ones.

  Args:
    db (AsyncSession): The database session.
    pylabrobot_class_name (str): The fully qualified name of the PyLabRobot deck
      class (e.g., "pylabrobot.resources.Deck").
    praxis_deck_type_name (str): A human-readable display name for the deck type.
    deck_type_id (Optional[int], optional): The ID of an existing deck type definition
      to update. If None, a new definition will be created or an existing one
      looked up by `pylabrobot_class_name`. Defaults to None.
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
    serialized_constructor_args_json (Optional[Dict[str, Any]], optional): JSON
      string of constructor arguments for PyLabRobot instantiation. Defaults to None.
    serialized_assignment_methods_json (Optional[Dict[str, Any]], optional): JSON
      string of assignment methods for PyLabRobot instantiation. Defaults to None.
    serialized_constructor_layout_hints_json (Optional[Dict[str, Any]], optional):
      JSON string of layout hints for PyLabRobot instantiation. Defaults to None.
    additional_properties_input_json (Optional[Dict[str, Any]], optional): A dictionary
      of additional properties to store as JSON. Keys in this dictionary will
      override `description`, `manufacturer`, `model`, `notes` if also provided.
      Defaults to None.
    pose_definitions_data (Optional[List[Dict[str, Any]]], optional): A list of
      dictionaries, each representing a pose definition for this deck type. Each
      dictionary should contain:
      - 'pose_name' (str): The unique name of the pose.
      - 'location_x_mm' (Optional[float]): Nominal X coordinate of the pose.
      - 'location_y_mm' (Optional[float]): Nominal Y coordinate of the pose.
      - 'location_z_mm' (Optional[float]): Nominal Z coordinate of the pose.
      - 'allowed_resource_categories' (Optional[List[str]]): List of resource
        categories allowed at this pose.
      - 'pylabrobot_pose_type_name' (Optional[str]): PyLabRobot specific pose type.
      - 'allowed_resource_definition_names' (Optional[List[str]]): Specific
        resource definition names allowed.
      - 'accepts_tips' (Optional[bool]): If the pose accepts tips.
      - 'accepts_plates' (Optional[bool]): If the pose accepts plates.
      - 'accepts_tubes' (Optional[bool]): If the pose accepts tubes.
      - 'notes' (Optional[str]): Any specific notes for the pose.
      If provided, existing pose definitions for this deck type will be deleted
      and replaced with these. Defaults to None.

  Returns:
    DeckTypeDefinitionOrm: The created or updated deck type definition object.

  Raises:
    ValueError: If:
      - `deck_type_id` is provided but no matching deck type is found.
      - A deck type definition with the same `pylabrobot_class_name` already exists
        during creation.
      - A pose definition with a conflicting name is attempted to be added.
    Exception: For any other unexpected errors during the process.

  """
  log_prefix = f"Deck Type Definition (FQN: '{pylabrobot_class_name}', ID: {deck_type_id or 'new'}):"
  logger.info("%s Attempting to add or update.", log_prefix)

  deck_type_orm: Optional[DeckTypeDefinitionOrm] = None

  if deck_type_id:
    result = await db.execute(
      select(DeckTypeDefinitionOrm)
      .options(selectinload(DeckTypeDefinitionOrm.pose_definitions))
      .filter(DeckTypeDefinitionOrm.id == deck_type_id)
    )
    deck_type_orm = result.scalar_one_or_none()
    if not deck_type_orm:
      error_message = f"{log_prefix} DeckTypeDefinitionOrm with id {deck_type_id} not found for update."
      logger.error(error_message)
      raise ValueError(error_message)
    logger.info("%s Found existing deck type for update.", log_prefix)
  else:
    result = await db.execute(
      select(DeckTypeDefinitionOrm)
      .options(selectinload(DeckTypeDefinitionOrm.pose_definitions))
      .filter(DeckTypeDefinitionOrm.pylabrobot_deck_fqn == pylabrobot_class_name)
    )
    deck_type_orm = result.scalar_one_or_none()
    if deck_type_orm:
      logger.info(
        "%s Found existing deck type by FQN, updating instead of creating.",
        log_prefix,
      )
    else:
      logger.info("%s No existing deck type found, creating new.", log_prefix)
      deck_type_orm = DeckTypeDefinitionOrm(pylabrobot_deck_fqn=pylabrobot_class_name)
      db.add(deck_type_orm)

  # This check should ideally not be needed if logic above is sound, but kept as a safeguard
  if deck_type_orm is None:
    error_message = f"{log_prefix} Failed to initialize DeckTypeDefinitionOrm. This indicates a logic error."
    logger.critical(error_message)
    raise ValueError(error_message)

  # Update attributes
  deck_type_orm.pylabrobot_deck_fqn = pylabrobot_class_name  # Ensure FQN is consistent
  deck_type_orm.display_name = praxis_deck_type_name
  deck_type_orm.plr_category = plr_category
  deck_type_orm.default_size_x_mm = default_size_x_mm
  deck_type_orm.default_size_y_mm = default_size_y_mm
  deck_type_orm.default_size_z_mm = default_size_z_mm
  deck_type_orm.serialized_constructor_args_json = serialized_constructor_args_json
  deck_type_orm.serialized_assignment_methods_json = serialized_assignment_methods_json
  deck_type_orm.serialized_constructor_layout_hints_json = (
    serialized_constructor_layout_hints_json
  )

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
    await db.flush()  # Flush to get deck_type_orm.id if it's new
    logger.debug("%s Flushed deck type definition.", log_prefix)

    if pose_definitions_data is not None:
      logger.info(
        "%s Replacing existing pose definitions with %d new ones.",
        log_prefix,
        len(pose_definitions_data),
      )
      # Delete existing pose definitions for this deck type
      if deck_type_orm.id:
        existing_poses_stmt = select(DeckPoseDefinitionOrm).filter(
          DeckPoseDefinitionOrm.deck_type_definition_id == deck_type_orm.id
        )
        result = await db.execute(existing_poses_stmt)
        for pose in result.scalars().all():
          logger.debug("%s Deleting existing pose '%s'.", log_prefix, pose.pose_id)
          await db.delete(pose)
        await db.flush()  # Process deletions
        logger.debug("%s Existing pose definitions deleted.", log_prefix)

      # Add new pose definitions
      for pose_data in pose_definitions_data:
        pose_name = pose_data.get("pose_id", "UNKNOWN_POSE")
        logger.debug("%s Adding new pose definition: '%s'.", log_prefix, pose_name)
        pose_specific_details = pose_data.get("pose_specific_details_json", {})

        # Map Pydantic fields to pose_specific_details if not direct ORM fields
        if pose_data.get("pylabrobot_pose_type_name"):
          pose_specific_details["pylabrobot_pose_type_name"] = pose_data[
            "pylabrobot_pose_type_name"
          ]
        if pose_data.get("allowed_resource_definition_names"):
          pose_specific_details["allowed_resource_definition_names"] = pose_data[
            "allowed_resource_definition_names"
          ]
        if pose_data.get("accepts_tips") is not None:
          pose_specific_details["accepts_tips"] = pose_data["accepts_tips"]
        if pose_data.get("accepts_plates") is not None:
          pose_specific_details["accepts_plates"] = pose_data["accepts_plates"]
        if pose_data.get("accepts_tubes") is not None:
          pose_specific_details["accepts_tubes"] = pose_data["accepts_tubes"]
        if "notes" in pose_data:
          pose_specific_details["notes"] = pose_data["notes"]

        new_pose = DeckPoseDefinitionOrm(
          deck_type_definition_id=deck_type_orm.id,  # type: ignore
          pose_name=pose_name,
          nominal_x_mm=pose_data.get("location_x_mm"),
          nominal_y_mm=pose_data.get("location_y_mm"),
          nominal_z_mm=pose_data.get("location_z_mm"),
          accepted_resource_categories_json=pose_data.get(
            "allowed_resource_categories"
          ),
          pose_specific_details_json=pose_specific_details
          if pose_specific_details
          else None,
        )
        db.add(new_pose)

    await db.commit()
    await db.refresh(deck_type_orm)
    logger.info("%s Successfully committed changes.", log_prefix)

    # Eagerly load pose_definitions again after commit & refresh for the returned object
    if deck_type_orm.id:
      refreshed_deck_type_result = await db.execute(
        select(DeckTypeDefinitionOrm)
        .options(selectinload(DeckTypeDefinitionOrm.pose_definitions))
        .filter(DeckTypeDefinitionOrm.id == deck_type_orm.id)
      )
      deck_type_orm = refreshed_deck_type_result.scalar_one()
      logger.debug("%s Refreshed deck type and reloaded pose definitions.", log_prefix)

  except IntegrityError as e:
    await db.rollback()
    if "uq_deck_type_definitions_pylabrobot_deck_fqn" in str(e.orig):
      error_message = (
        f"{log_prefix} A deck type definition with PyLabRobot FQN "
        f"'{pylabrobot_class_name}' already exists. Details: {e}"
      )
      logger.error(error_message, exc_info=True)
      raise ValueError(error_message) from e
    if "uq_deck_pose_definition" in str(e.orig):
      error_message = (
        f"{log_prefix} A pose definition with a conflicting name might already "
        f"exist for this deck type. Details: {e}"
      )
      logger.error(error_message, exc_info=True)
      raise ValueError(error_message) from e
    error_message = f"{log_prefix} Database integrity error. Details: {e}"
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception("%s Unexpected error. Rolling back.", log_prefix)
    raise e

  logger.info("%s Operation completed.", log_prefix)
  return deck_type_orm


async def get_deck_type_definition_by_id(
  db: AsyncSession, deck_type_id: int
) -> Optional[DeckTypeDefinitionOrm]:
  """Retrieve a specific deck type definition by its ID.

  Args:
    db (AsyncSession): The database session.
    deck_type_id (int): The ID of the deck type definition to retrieve.

  Returns:
    Optional[DeckTypeDefinitionOrm]: The deck type definition object if found,
    otherwise None.

  """
  logger.info("Attempting to retrieve deck type definition with ID: %d.", deck_type_id)
  stmt = (
    select(DeckTypeDefinitionOrm)
    .options(selectinload(DeckTypeDefinitionOrm.pose_definitions))
    .filter(DeckTypeDefinitionOrm.id == deck_type_id)
  )
  result = await db.execute(stmt)
  deck_type_def = result.scalar_one_or_none()
  if deck_type_def:
    logger.info(
      "Successfully retrieved deck type definition ID %d: '%s'.",
      deck_type_id,
      deck_type_def.display_name,
    )
  else:
    logger.info("Deck type definition with ID %d not found.", deck_type_id)
  return deck_type_def


async def get_deck_type_definition_by_fqn(
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
    .options(selectinload(DeckTypeDefinitionOrm.pose_definitions))
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
  """List all deck type definitions with pagination, including their pose definitions.

  Args:
    db (AsyncSession): The database session.
    limit (int): The maximum number of results to return. Defaults to 100.
    offset (int): The number of results to skip before returning. Defaults to 0.

  Returns:
    List[DeckTypeDefinitionOrm]: A list of deck type definition objects.

  """
  logger.info(
    "Listing deck type definitions with limit: %d, offset: %d.", limit, offset
  )
  stmt = (
    select(DeckTypeDefinitionOrm)
    .options(selectinload(DeckTypeDefinitionOrm.pose_definitions))
    .order_by(DeckTypeDefinitionOrm.display_name)
    .limit(limit)
    .offset(offset)
  )
  result = await db.execute(stmt)
  deck_type_defs = list(result.scalars().all())
  logger.info("Found %d deck type definitions.", len(deck_type_defs))
  return deck_type_defs


async def add_deck_pose_definitions(
  db: AsyncSession,
  deck_type_definition_id: int,
  new_poses_data: List[Dict[str, Any]],
) -> List[DeckPoseDefinitionOrm]:
  """Add multiple new pose definitions to an existing deck type definition.

  This function appends poses. If a pose name conflicts with an existing one
  for this deck type, an `IntegrityError` will be raised by the database.

  Args:
    db (AsyncSession): The database session.
    deck_type_definition_id (int): The ID of the deck type definition to which
      to add the poses.
    new_poses_data (List[Dict[str, Any]]): A list of dictionaries, each
      representing a new pose definition. Each dictionary should contain:
      - 'pose_name' (str): The unique name of the pose.
      - 'location_x_mm' (Optional[float]): Nominal X coordinate of the pose.
      - 'location_y_mm' (Optional[float]): Nominal Y coordinate of the pose.
      - 'location_z_mm' (Optional[float]): Nominal Z coordinate of the pose.
      - 'allowed_resource_categories' (Optional[List[str]]): List of resource
        categories allowed at this pose.
      - 'pylabrobot_pose_type_name' (Optional[str]): PyLabRobot specific pose type.
      - 'allowed_resource_definition_names' (Optional[List[str]]): Specific
        resource definition names allowed.
      - 'accepts_tips' (Optional[bool]): If the pose accepts tips.
      - 'accepts_plates' (Optional[bool]): If the pose accepts plates.
      - 'accepts_tubes' (Optional[bool]): If the pose accepts tubes.
      - 'notes' (Optional[str]): Any specific notes for the pose.

  Returns:
    List[DeckPoseDefinitionOrm]: A list of the newly created deck pose definition
    objects.

  Raises:
    ValueError: If the `deck_type_definition_id` does not exist, or if a pose
      name conflict occurs during addition.
    Exception: For any other unexpected errors during the process.
  """
  log_prefix = f"Deck Pose Definitions (Deck Type ID: {deck_type_definition_id}):"
  logger.info(
    "%s Attempting to add %d new pose definitions.", log_prefix, len(new_poses_data)
  )

  # First, check if the parent DeckTypeDefinitionOrm exists
  deck_type_result = await db.execute(
    select(DeckTypeDefinitionOrm).filter(
      DeckTypeDefinitionOrm.id == deck_type_definition_id
    )
  )
  deck_type_orm = deck_type_result.scalar_one_or_none()

  if not deck_type_orm:
    error_message = (
      f"{log_prefix} DeckTypeDefinitionOrm with id {deck_type_definition_id} not found. "
      "Cannot add pose definitions."
    )
    logger.error(error_message)
    raise ValueError(error_message)
  logger.debug("%s Parent deck type definition found.", log_prefix)

  created_poses: List[DeckPoseDefinitionOrm] = []
  try:
    for pose_data in new_poses_data:
      pose_name = pose_data.get("pose_name", "UNKNOWN_POSE")
      logger.debug("%s Preparing to add pose '%s'.", log_prefix, pose_name)

      pose_specific_details = pose_data.get("pose_specific_details_json", {})

      # Map Pydantic-like fields to pose_specific_details_json
      if pose_data.get("pylabrobot_pose_type_name"):
        pose_specific_details["pylabrobot_pose_type_name"] = pose_data[
          "pylabrobot_pose_type_name"
        ]
      if pose_data.get("allowed_resource_definition_names"):
        pose_specific_details["allowed_resource_definition_names"] = pose_data[
          "allowed_resource_definition_names"
        ]
      if pose_data.get("accepts_tips") is not None:
        pose_specific_details["accepts_tips"] = pose_data["accepts_tips"]
      if pose_data.get("accepts_plates") is not None:
        pose_specific_details["accepts_plates"] = pose_data["accepts_plates"]
      if pose_data.get("accepts_tubes") is not None:
        pose_specific_details["accepts_tubes"] = pose_data["accepts_tubes"]
      if "notes" in pose_data:
        pose_specific_details["notes"] = pose_data["notes"]

      new_pose = DeckPoseDefinitionOrm(
        deck_type_definition_id=deck_type_definition_id,
        pose_name=pose_name,
        nominal_x_mm=pose_data.get("location_x_mm"),
        nominal_y_mm=pose_data.get("location_y_mm"),
        nominal_z_mm=pose_data.get("location_z_mm"),
        accepted_resource_categories_json=pose_data.get("allowed_resource_categories"),
        pose_specific_details_json=pose_specific_details
        if pose_specific_details
        else None,
      )
      db.add(new_pose)
      created_poses.append(new_pose)
      logger.debug("%s Added pose '%s' to session.", log_prefix, pose_name)

    await db.flush()
    await db.commit()
    for pose in created_poses:
      await db.refresh(pose)
    logger.info(
      "%s Successfully added and committed %d pose definitions.",
      log_prefix,
      len(created_poses),
    )

  except IntegrityError as e:
    await db.rollback()
    if "uq_deck_pose_definition" in str(e.orig):
      error_message = (
        f"{log_prefix} Failed to add one or more pose definitions due to a pose name "
        f"conflict or other integrity constraint. Details: {e}"
      )
      logger.error(error_message, exc_info=True)
      raise ValueError(error_message) from e
    error_message = f"{log_prefix} Database integrity error while adding pose "
    f"definitions. Details: {e}"
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception(
      "%s Unexpected error while adding pose definitions. Rolling back.", log_prefix
    )
    raise e

  return created_poses


async def get_pose_definitions_for_deck_type(
  db: AsyncSession, deck_type_definition_id: int
) -> List[DeckPoseDefinitionOrm]:
  """Retrieve all pose definitions associated with a specific deck type definition ID.

  Args:
    db (AsyncSession): The database session.
    deck_type_definition_id (int): The ID of the deck type definition.

  Returns:
    List[DeckPoseDefinitionOrm]: A list of pose definitions for the specified
    deck type. Returns an empty list if no poses are found or if the deck type
    does not exist.

  Raises:
    ValueError: If the `deck_type_definition_id` does not exist.

  """
  logger.info(
    "Attempting to retrieve pose definitions for deck type ID: %d.",
    deck_type_definition_id,
  )
  deck_type_exists_result = await db.execute(
    select(DeckTypeDefinitionOrm.id).filter(
      DeckTypeDefinitionOrm.id == deck_type_definition_id
    )
  )
  if not deck_type_exists_result.scalar_one_or_none():
    error_message = (
      f"DeckTypeDefinitionOrm with id {deck_type_definition_id} not found. "
      "Cannot retrieve pose definitions."
    )
    logger.error(error_message)
    raise ValueError(error_message)

  stmt = (
    select(DeckPoseDefinitionOrm)
    .filter(DeckPoseDefinitionOrm.deck_type_definition_id == deck_type_definition_id)
    .order_by(DeckPoseDefinitionOrm.pose_id)
  )
  result = await db.execute(stmt)
  poses = list(result.scalars().all())
  logger.info(
    "Found %d pose definitions for deck type ID %d.",
    len(poses),
    deck_type_definition_id,
  )
  return poses
