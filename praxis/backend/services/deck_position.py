import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from praxis.backend.models import (
  DeckOrm,
  DeckPositionDefinitionOrm,
  DeckPositionResourceOrm,
  DeckTypeDefinitionOrm,
  ResourceOrm,
)
from praxis.backend.utils.logging import get_logger

from .resource_type_definition import read_resource_definition

logger = get_logger(__name__)

UUID = uuid.UUID


async def create_deck_position_item(
  db: AsyncSession,
  deck_accession_id: UUID,
  name: str,
  resource_instance_accession_id: UUID | None = None,
  expected_resource_definition_name: str | None = None,
) -> DeckPositionResourceOrm | None:
  """Add a new position item to a deck instance.

  Args:
    db (AsyncSession): The database session.
    deck_accession_id (int): The ID of the deck instance to which
      to create the position item.
    name (str): The name of the position for this item.
    resource_instance_accession_id (Optional[int], optional): The ID of the resource instance
      associated with this position item. Defaults to None.
    expected_resource_definition_name (Optional[str], optional): The name of the
      expected resource definition for this position item. Defaults to None.

  Returns:
    DeckPositionResourceOrm: The newly created position item object.

  Raises:
    ValueError: If the `deck_accession_id` does not exist, or if a specified
      resource instance ID or resource definition name does not exist.
    Exception: For any other unexpected errors during the process.

  """
  logger.info(
    "Attempting to create position item '%s' to deck instance ID %s.",
    name,
    deck_accession_id,
  )

  # Check if the parent DeckOrm exists
  deck_result = await db.execute(
    select(DeckOrm).filter(DeckOrm.accession_id == deck_accession_id),
  )
  deck_orm = deck_result.scalar_one_or_none()

  if not deck_orm:
    error_message = f"DeckOrm with id {deck_accession_id} not found. " "Cannot create position item."
    logger.error(error_message)
    raise ValueError(error_message)

  # Validate resource instance if provided
  if resource_instance_accession_id is not None:
    resource_instance_result = await db.execute(
      select(ResourceOrm).filter(
        ResourceOrm.accession_id == resource_instance_accession_id,
      ),
    )
    if not resource_instance_result.scalar_one_or_none():
      error_message = f"ResourceOrm with id {resource_instance_accession_id} not found. " "Cannot create position item."
      logger.error(error_message)
      raise ValueError(error_message)

  # Validate expected resource definition if provided
  if expected_resource_definition_name is not None:
    if not await read_resource_definition(db, expected_resource_definition_name):
      error_message = (
        f"ResourceDefinitionOrm with name '{expected_resource_definition_name}' "
        "not found. Cannot create position item."
      )
      logger.error(error_message)
      raise ValueError(error_message)
  # Create the new position item
  position_item = DeckPositionResourceOrm(
    deck_accession_id=deck_accession_id,
    name=name,
    resource_instance_accession_id=resource_instance_accession_id,
    expected_resource_definition_name=expected_resource_definition_name,
  )
  db.add(position_item)
  await db.flush()  # Ensure the item is created before commit

  try:
    await db.commit()
    await db.refresh(position_item)  # Refresh to get the latest state
    logger.info(
      "Successfully created position item '%s' to deck instance ID %s.",
      name,
      deck_accession_id,
    )
    return position_item
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Integrity error creating position item '{name}' to deck instance ID" f" {deck_accession_id}. Details: {e}"
    )
    logger.error(error_message)
    return None


async def read_deck_position_item(
  db: AsyncSession,
  position_item_accession_id: UUID,
) -> DeckPositionResourceOrm | None:
  """Retrieve a specific position item by its ID.

  Args:
    db (AsyncSession): The database session.
    position_item_accession_id (UUID): The ID of the position item to retrieve.

  Returns:
    Optional[DeckPositionResourceOrm]: The position item object if found,
    otherwise None.

  """
  logger.info(
    "Attempting to retrieve position item with ID: %s.",
    position_item_accession_id,
  )
  result = await db.execute(
    select(DeckPositionResourceOrm).filter(
      DeckPositionResourceOrm.accession_id == position_item_accession_id,
    ),
  )
  position_item = result.scalar_one_or_none()
  if position_item:
    logger.info(
      "Successfully retrieved position item ID %s: '%s'.",
      position_item_accession_id,
      position_item.position_name,
    )
  else:
    logger.info("Position item with ID %s not found.", position_item_accession_id)
  return position_item


async def update_deck_position_item(
  db: AsyncSession,
  position_item_accession_id: UUID,
  position_accession_id: str | None = None,
  resource_instance_accession_id: UUID | None = None,
  expected_resource_definition_name: str | None = None,
) -> DeckPositionResourceOrm | None:
  """Update an existing position item in a deck instance.

  Args:
    db (AsyncSession): The database session.
    position_item_accession_id (UUID): The ID of the position item to update.
    position_accession_id (Optional[str], optional): The new position ID for the position item.
      Defaults to None.
    resource_instance_accession_id (Optional[UUID], optional): The new resource instance ID
      associated with this position item. Defaults to None.
    expected_resource_definition_name (Optional[str], optional): The new expected
      resource definition name for this position item. Defaults to None.

  Returns:
    Optional[DeckPositionResourceOrm]: The updated position item object if
    successful, otherwise None if the item was not found.

  Raises:
    ValueError: If the specified position item ID does not exist, or if a specified
      resource instance ID or resource definition name does not exist.
    Exception: For any other unexpected errors during the process.

  """
  logger.info("Attempting to update position item ID %s.", position_item_accession_id)
  result = await db.execute(
    select(DeckPositionResourceOrm).filter(
      DeckPositionResourceOrm.accession_id == position_item_accession_id,
    ),
  )
  position_item = result.scalar_one_or_none()

  if not position_item:
    logger.warning(
      "Position item with ID %s not found for update.",
      position_item_accession_id,
    )
    return None

  original_position_accession_id = position_item.position_accession_id

  if position_accession_id is not None and position_item.position_accession_id != position_accession_id:
    logger.debug(
      "Updating position ID from '%s' to '%s'.",
      original_position_accession_id,
      position_accession_id,
    )
    position_item.position_accession_id = position_accession_id

  if resource_instance_accession_id is not None and (
    not position_item.resource_instance_accession_id
    or position_item.resource_instance_accession_id != resource_instance_accession_id
  ):
    resource_instance_result = await db.execute(
      select(ResourceOrm).filter(
        ResourceOrm.accession_id == resource_instance_accession_id,
      ),
    )
    if not resource_instance_result.scalar_one_or_none():
      error_message = f"ResourceOrm with id {resource_instance_accession_id} not found. " "Cannot update position item."
      logger.error(error_message)
      raise ValueError(error_message)
    logger.debug(
      "Updating resource instance ID from %s to %s.",
      position_item.resource_instance_accession_id,
      resource_instance_accession_id,
    )
    position_item.resource_instance_accession_id = resource_instance_accession_id
  if expected_resource_definition_name is not None and (
    not position_item.expected_resource_definition_name
    or position_item.expected_resource_definition_name != expected_resource_definition_name
  ):
    if not await read_resource_definition(db, expected_resource_definition_name):
      error_message = (
        f"ResourceDefinitionOrm with name '{expected_resource_definition_name}' "
        "not found. Cannot update position item."
      )
      logger.error(error_message)
      raise ValueError(error_message)
    logger.debug(
      "Updating expected resource definition name from '%s' to '%s'.",
      position_item.expected_resource_definition_name,
      expected_resource_definition_name,
    )
    position_item.expected_resource_definition_name = expected_resource_definition_name
  try:
    await db.commit()
    await db.refresh(position_item)  # Refresh to get the latest state
    logger.info("Successfully updated position item ID %s.", position_item_accession_id)
    return position_item
  except IntegrityError as e:
    await db.rollback()
    error_message = f"Integrity error updating position item ID {position_item_accession_id}. " f"Details: {e}"
    logger.error(error_message, exc_info=True)
    return None


async def delete_deck_position_item(
  db: AsyncSession,
  position_item_accession_id: UUID,
) -> bool:
  """Delete a specific position item by its ID.

  This function deletes a position item from a deck instance.

  Args:
    db (AsyncSession): The database session.
    position_item_accession_id (UUID): The ID of the position item to delete.

  Returns:
    bool: True if the deletion was successful, False if the item was not found.

  Raises:
    Exception: For any unexpected errors during deletion.

  """
  logger.info(
    "Attempting to delete position item with ID: %s.",
    position_item_accession_id,
  )
  position_item = await read_deck_position_item(db, position_item_accession_id)
  if not position_item:
    logger.warning(
      "Position item with ID %s not found for deletion.",
      position_item_accession_id,
    )
    return False

  try:
    await db.delete(position_item)
    await db.commit()
    logger.info("Successfully deleted position item ID %s.", position_item_accession_id)
    return True
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Integrity error deleting position item ID {position_item_accession_id}. "
      f"This might be due to foreign key constraints. Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    return False  # Return False as deletion failed due to integrity
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error deleting position item ID %s. Rolling back.",
      position_item_accession_id,
    )
    raise e


async def _process_position_definitions(
  db: AsyncSession,
  deck_type_orm: DeckTypeDefinitionOrm,
  position_definitions_data: list[dict[str, Any]] | None,
  log_prefix: str,
):
  """Helper function to handle the deletion and creation of position definitions.
  This logic is common to both create and update.
  """
  if position_definitions_data is not None:
    logger.info(
      "%s Replacing existing position definitions with %s new ones.",
      log_prefix,
      len(position_definitions_data),
    )
    # Delete existing position definitions for this deck type
    if deck_type_orm.accession_id:  # Ensure we have an ID to link positions
      existing_positions_stmt = select(DeckPositionDefinitionOrm).filter(
        DeckPositionDefinitionOrm.deck_type_id == deck_type_orm.accession_id,
      )
      result = await db.execute(existing_positions_stmt)
      for position in result.scalars().all():
        logger.debug("%s Deleting existing position '%s'.", log_prefix, position.name)
        await db.delete(position)
      await db.flush()  # Process deletions to avoid conflicts with new additions
      logger.debug("%s Existing position definitions deleted.", log_prefix)

    # Add new position definitions
    for position_data in position_definitions_data:
      name = position_data.get("name", "UNKNOWN_POSE")  # Use name
      logger.debug("%s Adding new position definition: '%s'.", log_prefix, name)
      position_specific_details = position_data.get(
        "position_specific_details_json",
        {},
      )

      # Map Pydantic fields to position_specific_details if not direct ORM fields
      if position_data.get("pylabrobot_position_type_name"):
        position_specific_details["pylabrobot_position_type_name"] = position_data["pylabrobot_position_type_name"]
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
        deck_type_id=deck_type_orm.accession_id,  # type: ignore
        name=name,
        nominal_x_mm=position_data.get("location_x_mm"),
        nominal_y_mm=position_data.get("location_y_mm"),
        nominal_z_mm=position_data.get("location_z_mm"),
        accepted_resource_categories_json=position_data.get(
          "allowed_resource_categories",
        ),
        position_specific_details_json=position_specific_details if position_specific_details else None,
      )
      db.add(new_position)


async def create_deck_position_definitions(
  db: AsyncSession,
  deck_type_id: uuid.UUID,
  new_positions_data: list[dict[str, Any]],
) -> list[DeckPositionDefinitionOrm]:
  """Add multiple new position definitions to an existing deck type definition.

  This function appends positions. If a position name conflicts with an existing one
  for this deck type, an `IntegrityError` will be raised by the database.

  Args:
    db (AsyncSession): The database session.
    deck_type_id (int): The ID of the deck type definition to which
      to create the positions.
    new_positions_data (list[dict[str, Any]]): A list of dictionaries, each
      representing a new position definition. Each dictionary should contain:
      - 'name' (str): The unique name of the position.
      - 'location_x_mm' (Optional[float]): Nominal X coordinate of the position.
      - 'location_y_mm' (Optional[float]): Nominal Y coordinate of the position.
      - 'location_z_mm' (Optional[float]): Nominal Z coordinate of the position.
      - 'allowed_resource_categories' (Optional[list[str]]): List of resource
        categories allowed at this position.
      - 'pylabrobot_position_type_name' (Optional[str]): PyLabRobot specific position
      type.
      - 'allowed_resource_definition_names' (Optional[list[str]]): Specific
        resource definition names allowed.
      - 'accepts_tips' (Optional[bool]): If the position accepts tips.
      - 'accepts_plates' (Optional[bool]): If the position accepts plates.
      - 'accepts_tubes' (Optional[bool]): If the position accepts tubes.
      - 'notes' (Optional[str]): Any specific notes for the position.

  Returns:
    list[DeckPositionDefinitionOrm]: A list of the newly created deck position definition
    objects.

  Raises:
    ValueError: If the `deck_type_id` does not exist, or if a position
      name conflict occurs during creation.
    Exception: For any other unexpected errors during the process.

  """
  log_prefix = f"Deck Position Definitions (Deck Type ID: {deck_type_id}):"
  logger.info(
    "%s Attempting to create %s new position definitions.",
    log_prefix,
    len(new_positions_data),
  )

  # First, check if the parent DeckTypeDefinitionOrm exists
  deck_type_result = await db.execute(
    select(DeckTypeDefinitionOrm).filter(
      DeckTypeDefinitionOrm.accession_id == deck_type_id,
    ),
  )
  deck_type_orm = deck_type_result.scalar_one_or_none()

  if not deck_type_orm:
    error_message = (
      f"{log_prefix} DeckTypeDefinitionOrm with id {deck_type_id} not found." " Cannot create position definitions."
    )
    logger.error(error_message)
    raise ValueError(error_message)
  logger.debug("%s Parent deck type definition found.", log_prefix)

  created_positions: list[DeckPositionDefinitionOrm] = []
  try:
    for position_data in new_positions_data:
      name = position_data.get("name", "UNKNOWN_POSE")
      logger.debug("%s Preparing to create position '%s'.", log_prefix, name)

      position_specific_details = position_data.get(
        "position_specific_details_json",
        {},
      )

      # Map Pydantic-like fields to position_specific_details_json
      if position_data.get("pylabrobot_position_type_name"):
        position_specific_details["pylabrobot_position_type_name"] = position_data["pylabrobot_position_type_name"]
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
        deck_type_id=deck_type_id,
        name=name,
        nominal_x_mm=position_data.get("location_x_mm"),
        nominal_y_mm=position_data.get("location_y_mm"),
        nominal_z_mm=position_data.get("location_z_mm"),
        accepted_resource_categories_json=position_data.get(
          "allowed_resource_categories",
        ),
        position_specific_details_json=position_specific_details if position_specific_details else None,
      )
      db.add(new_position)
      created_positions.append(new_position)
      logger.debug("%s Added position '%s' to session.", log_prefix, name)

    await db.flush()
    await db.commit()
    for position in created_positions:
      await db.refresh(position)
    logger.info(
      "%s Successfully created and committed %s position definitions.",
      log_prefix,
      len(created_positions),
    )

  except IntegrityError as e:
    await db.rollback()
    if "uq_deck_position_definition" in str(e.orig):
      error_message = (
        f"{log_prefix} Failed to create one or more position definitions due to a "
        f"position name conflict or other integrity constraint. Details: {e}"
      )
      logger.error(error_message, exc_info=True)
      raise ValueError(error_message) from e
    error_message = f"{log_prefix} Database integrity error while creating position "
    f"definitions. Details: {e}"
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception(
      "%s Unexpected error while creating position definitions. Rolling back.",
      log_prefix,
    )
    raise e

  return created_positions


async def update_deck_position_definition(
  db: AsyncSession,
  deck_type_id: uuid.UUID,
  name: str,
  location_x_mm: float | None = None,
  location_y_mm: float | None = None,
  location_z_mm: float | None = None,
  allowed_resource_categories: list[str] | None = None,
  pylabrobot_position_type_name: str | None = None,
  allowed_resource_definition_names: list[str] | None = None,
  accepts_tips: bool | None = None,
  accepts_plates: bool | None = None,
  accepts_tubes: bool | None = None,
  notes: str | None = None,
) -> DeckPositionDefinitionOrm:
  """Update an existing position definition for a specific deck type definition.

  Args:
    db (AsyncSession): The database session.
    deck_type_id (int): The ID of the parent deck type definition.
    name (str): The unique name of the position to update.
    location_x_mm (Optional[float], optional): Nominal X coordinate of the position.
    location_y_mm (Optional[float], optional): Nominal Y coordinate of the position.
    location_z_mm (Optional[float], optional): Nominal Z coordinate of the position.
    allowed_resource_categories (Optional[list[str]]): List of resource
      categories allowed at this position.
    pylabrobot_position_type_name (Optional[str]): PyLabRobot specific position
      type.
    allowed_resource_definition_names (Optional[list[str]]): Specific
      resource definition names allowed.
    accepts_tips (Optional[bool]): If the position accepts tips.
    accepts_plates (Optional[bool]): If the position accepts plates.
    accepts_tubes (Optional[bool]): If the position accepts tubes.
    notes (Optional[str]): Any specific notes for the position.

  Returns:
    DeckPositionDefinitionOrm: The updated deck position definition object.

  Raises:
    ValueError: If the deck type definition or the position definition is not found.
    Exception: For any other unexpected errors during the process.

  """
  log_prefix = f"Deck Position Definition (Deck Type ID: {deck_type_id}, Position: '{name}'):"
  logger.info("%s Attempting to update.", log_prefix)

  # First, fetch the specific position definition
  result = await db.execute(
    select(DeckPositionDefinitionOrm)
    .filter(
      DeckPositionDefinitionOrm.deck_type_id == deck_type_id,
    )
    .filter(DeckPositionDefinitionOrm.name == name),
  )
  position_orm = result.scalar_one_or_none()

  if not position_orm:
    error_message = (
      f"{log_prefix} Position definition not found for update. "
      "Please ensure both deck type ID and position name are correct."
    )
    logger.error(error_message)
    raise ValueError(error_message)
  logger.debug("%s Found existing position definition for update.", log_prefix)

  # Update core attributes
  if location_x_mm is not None:
    position_orm.nominal_x_mm = location_x_mm
  if location_y_mm is not None:
    position_orm.nominal_y_mm = location_y_mm
  if location_z_mm is not None:
    position_orm.nominal_z_mm = location_z_mm
  if allowed_resource_categories is not None:
    position_orm.accepted_resource_categories_json = allowed_resource_categories
    flag_modified(position_orm, "accepted_resource_categories_json")  # Flag as modified
  logger.debug("%s Updated nominal dimensions and allowed categories.", log_prefix)

  # Update position_specific_details_json
  current_position_details = position_orm.position_specific_details_json or {}

  if pylabrobot_position_type_name is not None:
    current_position_details["pylabrobot_position_type_name"] = pylabrobot_position_type_name
  if allowed_resource_definition_names is not None:
    current_position_details["allowed_resource_definition_names"] = allowed_resource_definition_names
  if accepts_tips is not None:
    current_position_details["accepts_tips"] = accepts_tips
  if accepts_plates is not None:
    current_position_details["accepts_plates"] = accepts_plates
  if accepts_tubes is not None:
    current_position_details["accepts_tubes"] = accepts_tubes
  if notes is not None:
    current_position_details["notes"] = notes

  if current_position_details:
    position_orm.position_specific_details_json = current_position_details
    flag_modified(position_orm, "position_specific_details_json")  # Flag as modified
    logger.debug("%s Updated position_specific_details_json.", log_prefix)

  try:
    await db.commit()
    await db.refresh(position_orm)
    logger.info("%s Successfully committed update.", log_prefix)
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"{log_prefix} Database integrity error during update. "
      f"This might occur if a unique constraint is violated. Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception("%s Unexpected error during update. Rolling back.", log_prefix)
    raise e

  logger.info("%s Update operation completed.", log_prefix)
  return position_orm


async def delete_deck_position_definition(
  db: AsyncSession,
  deck_type_id: uuid.UUID,
  name: str,
) -> None:
  """Delete a specific position definition from a deck type definition.

  Args:
    db (AsyncSession): The database session.
    deck_type_id (int): The ID of the parent deck type definition.
    name (str): The unique name of the position to delete.

  Returns:
    None

  Raises:
    ValueError: If the deck type definition or the position definition is not found.
    Exception: For any other unexpected errors during the process.

  """
  log_prefix = f"Deck Position Definition (Deck Type ID: {deck_type_id}, \
    Position: '{name}'):"
  logger.info("%s Attempting to delete.", log_prefix)

  # First, fetch the specific position definition
  result = await db.execute(
    select(DeckPositionDefinitionOrm)
    .filter(
      DeckPositionDefinitionOrm.deck_type_id == deck_type_id,
    )
    .filter(DeckPositionDefinitionOrm.name == name),
  )
  position_orm = result.scalar_one_or_none()

  if not position_orm:
    error_message = (
      f"{log_prefix} Position definition not found for deletion. "
      "Please ensure both deck type ID and position name are correct."
    )
    logger.error(error_message)
    raise ValueError(error_message)
  logger.debug("%s Found existing position definition for deletion.", log_prefix)

  try:
    await db.delete(position_orm)
    await db.commit()
    logger.info("%s Successfully deleted position definition.", log_prefix)
  except Exception as e:
    await db.rollback()
    logger.exception("%s Unexpected error during deletion. Rolling back.", log_prefix)
    raise e


async def read_position_definitions_for_deck_type(
  db: AsyncSession,
  deck_type_id: uuid.UUID,
) -> list[DeckPositionDefinitionOrm]:
  """Retrieve all position definitions associated with a specific deck type definition ID.

  Args:
    db (AsyncSession): The database session.
    deck_type_id (uuid.UUID): The ID of the deck type definition.

  Returns:
    list[DeckPositionDefinitionOrm]: A list of position definitions for the specified
    deck type. Returns an empty list if no positions are found or if the deck type
    does not exist.

  Raises:
    ValueError: If the `deck_type_id` does not exist.

  """
  logger.info(
    "Attempting to retrieve position definitions for deck type ID: %s.",
    deck_type_id,
  )
  deck_type_exists_result = await db.execute(
    select(DeckTypeDefinitionOrm.accession_id).filter(
      DeckTypeDefinitionOrm.accession_id == deck_type_id,
    ),
  )
  if not deck_type_exists_result.scalar_one_or_none():
    error_message = f"DeckTypeDefinitionOrm with id {deck_type_id} not found. " "Cannot retrieve position definitions."
    logger.error(error_message)
    raise ValueError(error_message)

  stmt = (
    select(DeckPositionDefinitionOrm)
    .filter(
      DeckPositionDefinitionOrm.deck_type_id == deck_type_id,
    )
    .order_by(
      DeckPositionDefinitionOrm.name,
    )  # Changed from position_accession_id to name
  )
  result = await db.execute(stmt)
  positions = list(result.scalars().all())
  logger.info(
    "Found %s position definitions for deck type ID %s.",
    len(positions),
    deck_type_id,
  )
  return positions
