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

from sqlalchemy import delete, select, update  # Added delete for potential direct use
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
  machine.
  It can also create posed items for the deck layout if pose_items_data is provided.

  Args:
    db (AsyncSession): The database session.
    layout_name (str): The name of the deck layout.
    deck_machine_id (int): The ID of the deck machine to associate with this layout.
    description (Optional[str], optional): Description of the deck layout. Defaults to
      None.
    pose_items_data (Optional[List[Dict[str, Any]]], optional): List of pose items
    data. Each item should be a dict containing 'pose_name' and optionally
    'resource_instance_id' and 'expected_resource_definition_name'. Defaults to None.

  Returns:
    DeckConfigurationOrm: The created deck layout configuration object.

  Raises:
    ValueError: If:
      - The specified deck machine ID doesn't exist
      - A deck layout with the same name already exists
      - A specified resource instance ID doesn't exist
      - A specified resource definition name doesn't exist
      - There's an integrity error while creating the deck layout or pose items

  """
  deck_machine_result = await db.execute(
    select(MachineOrm).filter(MachineOrm.id == deck_machine_id)
  )
  deck_machine = deck_machine_result.scalar_one_or_none()
  if not deck_machine:
    raise ValueError(f"MachineOrm (Deck Device) with id {deck_machine_id} not found.")

  deck_layout_orm = DeckConfigurationOrm(
    layout_name=layout_name,
    deck_machine_id=deck_machine_id,
    description=description,
  )
  db.add(deck_layout_orm)

  try:
    await db.flush()
    logger.info("Deck Data Service: Successfully flushed new deck layout.")
  except IntegrityError:
    await db.rollback()
    error_message = (
      f"Deck Data Service: DeckConfigurationOrm with layout name '{layout_name}' "
      f"already exists."
    )
    logger.error(error_message)
    raise ValueError(error_message)
  except Exception as e:
    logger.error(f"Deck Data Service: Error flushing new deck layout: {e}")
    logger.info("Deck Data Service: Rolling back transaction.")
    await db.rollback()
    raise e

  if pose_items_data:
    for item_data in pose_items_data:
      resource_instance_id = item_data.get("resource_instance_id")
      if resource_instance_id:
        resource_instance_result = await db.execute(
          select(ResourceInstanceOrm).filter(
            ResourceInstanceOrm.id == resource_instance_id
          )
        )
        if not resource_instance_result.scalar_one_or_none():
          await db.rollback()
          raise ValueError(
            f"ResourceInstanceOrm with id {resource_instance_id} for pose \
                          '{item_data.get('pose_name')}' not found."
          )

      expected_def_name = item_data.get("expected_resource_definition_name")
      if expected_def_name:
        if not await get_resource_definition(db, expected_def_name):
          await db.rollback()
          raise ValueError(
            f"ResourceDefinitionCatalogOrm with name '{expected_def_name}' for pose \
                          '{item_data.get('pose_name')}' not found."
          )

      pose_item = DeckConfigurationPoseItemOrm(
        deck_configuration_id=deck_layout_orm.id,
        pose_name=item_data["pose_name"],
        resource_instance_id=resource_instance_id,
        expected_resource_definition_name=expected_def_name,
      )
      db.add(pose_item)
  try:
    await db.commit()
    await db.refresh(deck_layout_orm)
    if deck_layout_orm.id:
      return await get_deck_layout_by_id(db, deck_layout_orm.id)  # type: ignore
  except IntegrityError as e:
    await db.rollback()
    raise ValueError(f"Error creating deck layout or its pose items: {e}")
  except Exception as e:
    await db.rollback()
    raise e
  return deck_layout_orm


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
  return result.scalar_one_or_none()


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
  return result.scalar_one_or_none()


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
    deck_machine_id (Optional[int]): The ID of the deck machine to filter by (optional).
    limit (int): The maximum number of results to return (default: 100).
    offset (int): The number of results to skip before returning (default: 0).

  Returns:
    List[DeckConfigurationOrm]: A list of deck layout configuration objects.

  """
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
  return list(result.scalars().all())


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
  associated deck machine, and pose items. If pose items are provided, they will
  replace the existing pose items for the deck layout.

  Args:
    db (AsyncSession): The database session.
    deck_layout_id (int): The ID of the deck layout to update.
    name (Optional[str]): The new name for the deck layout (optional).
    description (Optional[str]): The new description for the deck layout (optional).
    deck_machine_id (Optional[int]): The ID of the new deck machine (optional).
    pose_items_data (Optional[List[Dict[str, Any]]]): The new pose items data
    (optional).

  Returns:
    Optional[DeckConfigurationOrm]: The updated deck layout configuration object if
    successful, otherwise None.

  Raises:
    ValueError: If:
      - The specified deck layout ID does not exist
      - The new deck machine ID does not exist
      - A specified resource instance ID does not exist
      - A specified resource definition name does not exist
      - There is an integrity error while updating the deck layout or pose items

  """
  deck_layout_orm = await get_deck_layout_by_id(db, deck_layout_id)
  if not deck_layout_orm:
    return None

  if name is not None:
    deck_layout_orm.layout_name = name
  if description is not None:
    deck_layout_orm.description = description
  if deck_machine_id is not None:
    new_deck_machine_result = await db.execute(
      select(MachineOrm).filter(MachineOrm.id == deck_machine_id)
    )
    if not new_deck_machine_result.scalar_one_or_none():
      raise ValueError(
        f"New MachineOrm (Deck Device) with id {deck_machine_id} not found."
      )
    deck_layout_orm.deck_machine_id = deck_machine_id

  if pose_items_data is not None:
    if deck_layout_orm.pose_items:
      for item in deck_layout_orm.pose_items:
        await db.delete(item)
    await db.flush()

    for item_data in pose_items_data:
      resource_instance_id = item_data.get("resource_instance_id")
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
            f"'{item_data.get('pose_name')}' not found."
          )
          logger.error(error_message)
          raise ValueError(error_message)

      expected_def_name = item_data.get("expected_resource_definition_name")
      if expected_def_name:
        if not await get_resource_definition(db, expected_def_name):
          await db.rollback()
          error_message = (
            f"ResourceDefinitionCatalogOrm with name '{expected_def_name}' for pose \
                          '{item_data.get('pose_name')}' not found."
          )
          logger.error(error_message)
          raise ValueError(error_message)


      pose_item = DeckConfigurationPoseItemOrm(
        deck_configuration_id=deck_layout_orm.id,
        pose_name=item_data["pose_name"],
        resource_instance_id=resource_instance_id,
        expected_resource_definition_name=expected_def_name,
      )
      db.add(pose_item)
  try:
    await db.commit()
    await db.refresh(deck_layout_orm)
    return await get_deck_layout_by_id(db, deck_layout_id)
  except IntegrityError as e:
    await db.rollback()
    raise ValueError(f"Error updating deck layout '{deck_layout_id}': {e}")
  except Exception as e:
    await db.rollback()
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
    Exception: For any other errors besides IntegrityError that occur during deletion.

  """
  deck_layout_orm = await get_deck_layout_by_id(db, deck_layout_id)
  if not deck_layout_orm:
    return False

  try:
    await db.delete(deck_layout_orm)
    await db.commit()
    return True
  except IntegrityError as e:
    await db.rollback()
    print(f"ERROR: ADS: IntegrityError deleting deck layout ID {deck_layout_id}: {e}")
    return False
  except Exception as e:
    await db.rollback()
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
  """
  Adds a new deck type definition or updates an existing one.
  Manages associated pose definitions by replacing them if new data is provided.
  """
  deck_type_orm: Optional[DeckTypeDefinitionOrm] = None

  if deck_type_id:
    result = await db.execute(
      select(DeckTypeDefinitionOrm)
      .options(selectinload(DeckTypeDefinitionOrm.pose_definitions))
      .filter(DeckTypeDefinitionOrm.id == deck_type_id)
    )
    deck_type_orm = result.scalar_one_or_none()
    if not deck_type_orm:
      raise ValueError(
        f"DeckTypeDefinitionOrm with id {deck_type_id} not found for update."
      )
  else:
    result = await db.execute(
      select(DeckTypeDefinitionOrm)
      .options(selectinload(DeckTypeDefinitionOrm.pose_definitions))
      .filter(DeckTypeDefinitionOrm.pylabrobot_deck_fqn == pylabrobot_class_name)
    )
    deck_type_orm = result.scalar_one_or_none()

  if not deck_type_orm:
    deck_type_orm = DeckTypeDefinitionOrm(pylabrobot_deck_fqn=pylabrobot_class_name)
    db.add(deck_type_orm)

  if deck_type_orm is None:
    raise ValueError(
      f"DeckTypeDefinitionOrm with FQN '{pylabrobot_class_name}' \
            not found and no ID provided for creation."
    )

  # Update attributes
  deck_type_orm.pylabrobot_deck_fqn = pylabrobot_class_name
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
  if (
    additional_properties_input_json
  ):  # Explicitly passed JSON takes precedence for its keys
    current_additional_properties.update(additional_properties_input_json)
  if description is not None:
    current_additional_properties["description"] = description
  if manufacturer is not None:
    current_additional_properties["manufacturer"] = manufacturer
  if model is not None:
    current_additional_properties["model"] = model
  if notes is not None:
    current_additional_properties["notes"] = notes

  if current_additional_properties:  # Only assign if there's something to store
    deck_type_orm.additional_properties_json = current_additional_properties
    flag_modified(deck_type_orm, "additional_properties_json")

  try:
    await db.flush()  # Flush to get deck_type_orm.id if it's new

    if pose_definitions_data is not None:
      # Delete existing pose definitions for this deck type
      if deck_type_orm.id:  # Ensure ID exists
        existing_poses_stmt = select(DeckPoseDefinitionOrm).filter(
          DeckPoseDefinitionOrm.deck_type_definition_id == deck_type_orm.id
        )
        result = await db.execute(existing_poses_stmt)
        for pose in result.scalars().all():
          await db.delete(pose)
        await db.flush()  # Process deletions

      # Add new pose definitions
      for pose_data in pose_definitions_data:
        pose_specific_details = pose_data.get(
          "pose_specific_details_json", {}
        )  # Start with explicit if provided

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
        if pose_data.get("notes"):  # Pose notes
          pose_specific_details["notes"] = pose_data["notes"]

        new_pose = DeckPoseDefinitionOrm(
          deck_type_definition_id=deck_type_orm.id,
          pose_name=pose_data["pose_name"],
          nominal_x_mm=pose_data.get(
            "location_x_mm"
          ),  # Pydantic: location_x_mm -> ORM: nominal_x_mm
          nominal_y_mm=pose_data.get(
            "location_y_mm"
          ),  # Pydantic: location_y_mm -> ORM: nominal_y_mm
          nominal_z_mm=pose_data.get(
            "location_z_mm"
          ),  # Pydantic: location_z_mm -> ORM: nominal_z_mm
          accepted_resource_categories_json=pose_data.get(
            "allowed_resource_categories"
          ),  # Pydantic: allowed_resource_categories
          pose_specific_details_json=pose_specific_details
          if pose_specific_details
          else None,
        )
        db.add(new_pose)

    await db.commit()
    await db.refresh(deck_type_orm)
    # Eagerly load pose_definitions again after commit & refresh for the returned object
    if deck_type_orm.id:
      refreshed_deck_type_result = await db.execute(
        select(DeckTypeDefinitionOrm)
        .options(selectinload(DeckTypeDefinitionOrm.pose_definitions))
        .filter(DeckTypeDefinitionOrm.id == deck_type_orm.id)
      )
      deck_type_orm = refreshed_deck_type_result.scalar_one()

  except IntegrityError as e:
    await db.rollback()
    if "uq_deck_type_definitions_pylabrobot_deck_fqn" in str(e.orig):
      raise ValueError(
        f"A deck type definition with PyLabRobot FQN '{pylabrobot_class_name}' \
                  already exists."
      )
    elif "uq_deck_pose_definition" in str(e.orig):  # Should be caught per pose ideally
      raise ValueError(
        f"A pose definition with the same name might already exist for this deck type. \
                  Details: {e}"
      )
    raise ValueError(
      f"Database integrity error for deck type definition '{pylabrobot_class_name}'. \
              Details: {e}"
    )
  except Exception as e:
    await db.rollback()
    raise e

  return deck_type_orm


async def get_deck_type_definition_by_id(
  db: AsyncSession, deck_type_id: int
) -> Optional[DeckTypeDefinitionOrm]:
  """
  Retrieves a specific deck type definition by its ID, including its pose definitions.
  """
  stmt = (
    select(DeckTypeDefinitionOrm)
    .options(selectinload(DeckTypeDefinitionOrm.pose_definitions))
    .filter(DeckTypeDefinitionOrm.id == deck_type_id)
  )
  result = await db.execute(stmt)
  return result.scalar_one_or_none()


async def get_deck_type_definition_by_fqn(
  db: AsyncSession, pylabrobot_deck_fqn: str
) -> Optional[DeckTypeDefinitionOrm]:
  """
  Retrieves a specific deck type definition by its PyLabRobot FQN,
  including its pose definitions.
  """
  stmt = (
    select(DeckTypeDefinitionOrm)
    .options(selectinload(DeckTypeDefinitionOrm.pose_definitions))
    .filter(DeckTypeDefinitionOrm.pylabrobot_deck_fqn == pylabrobot_deck_fqn)
  )
  result = await db.execute(stmt)
  return result.scalar_one_or_none()


async def list_deck_type_definitions(
  db: AsyncSession, limit: int = 100, offset: int = 0
) -> List[DeckTypeDefinitionOrm]:
  """
  Lists all deck type definitions with pagination, including their pose definitions.
  """
  stmt = (
    select(DeckTypeDefinitionOrm)
    .options(selectinload(DeckTypeDefinitionOrm.pose_definitions))
    .order_by(DeckTypeDefinitionOrm.display_name)
    .limit(limit)
    .offset(offset)
  )
  result = await db.execute(stmt)
  return list(result.scalars().all())


async def add_deck_pose_definitions(
  db: AsyncSession,
  deck_type_definition_id: int,
  new_poses_data: List[
    Dict[str, Any]
  ],  # List of dicts, each based on DeckPoseDefinitionCreate
) -> List[DeckPoseDefinitionOrm]:
  """
  Adds multiple new pose definitions to an existing deck type definition.
  This function appends poses. If a pose name conflicts with an existing one
  for this deck type, an IntegrityError will be raised by the database.
  """
  # First, check if the parent DeckTypeDefinitionOrm exists
  deck_type_result = await db.execute(
    select(DeckTypeDefinitionOrm).filter(
      DeckTypeDefinitionOrm.id == deck_type_definition_id
    )
  )
  deck_type_orm = deck_type_result.scalar_one_or_none()

  if not deck_type_orm:
    raise ValueError(
      f"DeckTypeDefinitionOrm with id {deck_type_definition_id} not found."
    )

  created_poses: List[DeckPoseDefinitionOrm] = []
  try:
    for pose_data in new_poses_data:
      pose_specific_details = pose_data.get("pose_specific_details_json", {})

      # Map Pydantic-like fields to pose_specific_details_json
      # This logic is similar to the one in add_or_update_deck_type_definition
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
      if "notes" in pose_data:  # Pose-specific notes
        pose_specific_details["notes"] = pose_data["notes"]

      new_pose = DeckPoseDefinitionOrm(
        deck_type_definition_id=deck_type_definition_id,
        pose_name=pose_data["pose_name"],
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

    await db.flush()
    await db.commit()
    for pose in created_poses:  # Refresh each created pose
      await db.refresh(pose)

  except IntegrityError as e:
    await db.rollback()
    if "uq_deck_pose_definition" in str(e.orig):
      raise ValueError(
        f"Failed to add one or more pose definitions to deck type ID \
                  {deck_type_definition_id} "
        f"due to a pose name conflict or other integrity constraint. Details: {e}"
      )
    raise ValueError(
      f"Database integrity error while adding pose definitions. Details: {e}"
    )
  except Exception as e:
    await db.rollback()
    raise e

  return created_poses


async def get_pose_definitions_for_deck_type(
  db: AsyncSession, deck_type_definition_id: int
) -> List[DeckPoseDefinitionOrm]:
  """
  Retrieves all pose definitions associated with a specific deck type definition ID.
  """
  # Check if the parent DeckTypeDefinitionOrm exists to provide a better error if it doesn't
  deck_type_exists_result = await db.execute(
    select(DeckTypeDefinitionOrm.id).filter(
      DeckTypeDefinitionOrm.id == deck_type_definition_id
    )
  )
  if not deck_type_exists_result.scalar_one_or_none():
    # Or, depending on desired behavior, this could return an empty list instead of raising.
    # For now, let's assume the caller expects the deck type to exist.
    raise ValueError(
      f"DeckTypeDefinitionOrm with id {deck_type_definition_id} not found."
    )

  stmt = (
    select(DeckPoseDefinitionOrm)
    .filter(DeckPoseDefinitionOrm.deck_type_definition_id == deck_type_definition_id)
    .order_by(DeckPoseDefinitionOrm.pose_name)  # Optional: order by pose name
  )
  result = await db.execute(stmt)
  return list(result.scalars().all())
