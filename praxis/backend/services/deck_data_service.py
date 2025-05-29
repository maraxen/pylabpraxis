# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""
praxis/db_services/deck_data_service.py

Service layer for interacting with deck-related data in the database.
This includes Deck Configurations, Deck Types, and Deck Slot Definitions.
"""

import datetime
from typing import Dict, Any, Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete  # Added delete for potential direct use
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import flag_modified

from praxis.backend.services.resource_data_service import get_resource_definition


from praxis.backend.models.asset_management_orm import (
    MachineOrm,
    ResourceInstanceOrm,
    DeckConfigurationOrm,
    DeckConfigurationSlotItemOrm,
    DeckTypeDefinitionOrm,
    DeckSlotDefinitionOrm,
)


async def create_deck_layout(  # MODIFIED
    db: AsyncSession,  # MODIFIED
    layout_name: str,
    deck_machine_id: int,
    description: Optional[str] = None,
    slot_items_data: Optional[List[Dict[str, Any]]] = None,
) -> DeckConfigurationOrm:
    deck_machine_result = await db.execute(
        select(MachineOrm).filter(MachineOrm.id == deck_machine_id)
    )
    deck_machine = deck_machine_result.scalar_one_or_none()
    if not deck_machine:
        raise ValueError(
            f"MachineOrm (Deck Device) with id {deck_machine_id} not found."
        )

    deck_layout_orm = DeckConfigurationOrm(
        layout_name=layout_name,
        deck_machine_id=deck_machine_id,
        description=description,
    )
    db.add(deck_layout_orm)

    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise ValueError(
            f"A deck layout with name '{layout_name}' might already exist."
        )
    except Exception as e:
        await db.rollback()
        raise e

    if slot_items_data:
        for item_data in slot_items_data:
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
                        f"ResourceInstanceOrm with id {resource_instance_id} for slot '{item_data.get('slot_name')}' not found."
                    )

            expected_def_name = item_data.get("expected_resource_definition_name")
            if expected_def_name:
                if not await get_resource_definition(db, expected_def_name):
                    await db.rollback()
                    raise ValueError(
                        f"ResourceDefinitionCatalogOrm with name '{expected_def_name}' for slot '{item_data.get('slot_name')}' not found."
                    )

            slot_item = DeckConfigurationSlotItemOrm(
                deck_configuration_id=deck_layout_orm.id,
                slot_name=item_data["slot_name"],
                resource_instance_id=resource_instance_id,
                expected_resource_definition_name=expected_def_name,
            )
            db.add(slot_item)
    try:
        await db.commit()
        await db.refresh(deck_layout_orm)
        if deck_layout_orm.id:
            return await get_deck_layout_by_id(db, deck_layout_orm.id)  # type: ignore
    except IntegrityError as e:
        await db.rollback()
        raise ValueError(f"Error creating deck layout or its slot items: {e}")
    except Exception as e:
        await db.rollback()
        raise e
    return deck_layout_orm


async def get_deck_layout_by_id(
    db: AsyncSession, deck_layout_id: int
) -> Optional[DeckConfigurationOrm]:  # MODIFIED
    stmt = (
        select(DeckConfigurationOrm)
        .options(
            selectinload(DeckConfigurationOrm.slot_items)
            .selectinload(DeckConfigurationSlotItemOrm.resource_instance)
            .selectinload(ResourceInstanceOrm.resource_definition),
            selectinload(DeckConfigurationOrm.slot_items).selectinload(
                DeckConfigurationSlotItemOrm.expected_resource_definition
            ),
        )
        .filter(DeckConfigurationOrm.id == deck_layout_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_deck_layout_by_name(
    db: AsyncSession, layout_name: str
) -> Optional[DeckConfigurationOrm]:  # MODIFIED
    stmt = (
        select(DeckConfigurationOrm)
        .options(
            selectinload(DeckConfigurationOrm.slot_items)
            .selectinload(DeckConfigurationSlotItemOrm.resource_instance)
            .selectinload(ResourceInstanceOrm.resource_definition),
            selectinload(DeckConfigurationOrm.slot_items).selectinload(
                DeckConfigurationSlotItemOrm.expected_resource_definition
            ),
        )
        .filter(DeckConfigurationOrm.layout_name == layout_name)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_deck_layouts(  # MODIFIED
    db: AsyncSession,  # MODIFIED
    deck_machine_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[DeckConfigurationOrm]:
    stmt = select(DeckConfigurationOrm).options(
        selectinload(DeckConfigurationOrm.slot_items)
        .selectinload(DeckConfigurationSlotItemOrm.resource_instance)
        .selectinload(ResourceInstanceOrm.resource_definition),
        selectinload(DeckConfigurationOrm.slot_items).selectinload(
            DeckConfigurationSlotItemOrm.expected_resource_definition
        ),
    )
    if deck_machine_id is not None:
        stmt = stmt.filter(DeckConfigurationOrm.deck_machine_id == deck_machine_id)
    stmt = stmt.order_by(DeckConfigurationOrm.layout_name).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_deck_layout(  # MODIFIED
    db: AsyncSession,  # MODIFIED
    deck_layout_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    deck_machine_id: Optional[int] = None,
    slot_items_data: Optional[List[Dict[str, Any]]] = None,
) -> Optional[DeckConfigurationOrm]:
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

    if slot_items_data is not None:
        if deck_layout_orm.slot_items:
            for item in deck_layout_orm.slot_items:
                await db.delete(item)  # MODIFIED
        await db.flush()

        for item_data in slot_items_data:
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
                        f"ResourceInstanceOrm with id {resource_instance_id} for slot '{item_data.get('slot_name')}' not found."
                    )

            expected_def_name = item_data.get("expected_resource_definition_name")
            if expected_def_name:
                if not await get_resource_definition(db, expected_def_name):
                    await db.rollback()
                    raise ValueError(
                        f"ResourceDefinitionCatalogOrm with name '{expected_def_name}' for slot '{item_data.get('slot_name')}' not found."
                    )

            slot_item = DeckConfigurationSlotItemOrm(
                deck_configuration_id=deck_layout_orm.id,
                slot_name=item_data["slot_name"],
                resource_instance_id=resource_instance_id,
                expected_resource_definition_name=expected_def_name,
            )
            db.add(slot_item)
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


async def delete_deck_layout(db: AsyncSession, deck_layout_id: int) -> bool:  # MODIFIED
    deck_layout_orm = await get_deck_layout_by_id(
        db, deck_layout_id
    )  # Ensures items are loaded for cascade
    if not deck_layout_orm:
        return False

    try:
        await db.delete(deck_layout_orm)  # MODIFIED
        await db.commit()
        return True
    except IntegrityError as e:
        await db.rollback()
        print(
            f"ERROR: ADS: IntegrityError deleting deck layout ID {deck_layout_id}: {e}"
        )
        return False
    except Exception as e:
        await db.rollback()
        raise e


async def add_or_update_deck_type_definition(
    db: AsyncSession,
    pylabrobot_class_name: str,  # Corresponds to DeckTypeDefinitionOrm.pylabrobot_deck_fqn
    praxis_deck_type_name: str,  # Corresponds to DeckTypeDefinitionOrm.display_name
    deck_type_id: Optional[int] = None,
    description: Optional[str] = None,
    manufacturer: Optional[str] = None,
    model: Optional[str] = None,
    notes: Optional[str] = None,  # Will be stored in additional_properties_json
    plr_category: Optional[str] = "deck",  # Default to "deck" as per ORM
    default_size_x_mm: Optional[float] = None,
    default_size_y_mm: Optional[float] = None,
    default_size_z_mm: Optional[float] = None,
    serialized_constructor_args_json: Optional[Dict[str, Any]] = None,
    serialized_assignment_methods_json: Optional[Dict[str, Any]] = None,
    serialized_constructor_layout_hints_json: Optional[Dict[str, Any]] = None,
    additional_properties_input_json: Optional[
        Dict[str, Any]
    ] = None,  # User-provided base for additional_properties_json
    slot_definitions_data: Optional[
        List[Dict[str, Any]]
    ] = None,  # List of dicts based on DeckSlotDefinitionCreate
) -> DeckTypeDefinitionOrm:
    """
    Adds a new deck type definition or updates an existing one.
    Manages associated slot definitions by replacing them if new data is provided.
    """
    deck_type_orm: Optional[DeckTypeDefinitionOrm] = None

    if deck_type_id:
        result = await db.execute(
            select(DeckTypeDefinitionOrm)
            .options(selectinload(DeckTypeDefinitionOrm.slot_definitions))
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
            .options(selectinload(DeckTypeDefinitionOrm.slot_definitions))
            .filter(DeckTypeDefinitionOrm.pylabrobot_deck_fqn == pylabrobot_class_name)
        )
        deck_type_orm = result.scalar_one_or_none()

    if not deck_type_orm:
        deck_type_orm = DeckTypeDefinitionOrm(pylabrobot_deck_fqn=pylabrobot_class_name)
        db.add(deck_type_orm)

    # Update attributes
    deck_type_orm.pylabrobot_deck_fqn = pylabrobot_class_name
    deck_type_orm.display_name = praxis_deck_type_name
    deck_type_orm.plr_category = plr_category
    deck_type_orm.default_size_x_mm = default_size_x_mm
    deck_type_orm.default_size_y_mm = default_size_y_mm
    deck_type_orm.default_size_z_mm = default_size_z_mm
    deck_type_orm.serialized_constructor_args_json = serialized_constructor_args_json
    deck_type_orm.serialized_assignment_methods_json = (
        serialized_assignment_methods_json
    )
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

        if slot_definitions_data is not None:
            # Delete existing slot definitions for this deck type
            if deck_type_orm.id:  # Ensure ID exists
                existing_slots_stmt = select(DeckSlotDefinitionOrm).filter(
                    DeckSlotDefinitionOrm.deck_type_definition_id == deck_type_orm.id
                )
                result = await db.execute(existing_slots_stmt)
                for slot in result.scalars().all():
                    await db.delete(slot)
                await db.flush()  # Process deletions

            # Add new slot definitions
            for slot_data in slot_definitions_data:
                slot_specific_details = slot_data.get(
                    "slot_specific_details_json", {}
                )  # Start with explicit if provided

                # Map Pydantic fields to slot_specific_details if not direct ORM fields
                if slot_data.get("pylabrobot_slot_type_name"):
                    slot_specific_details["pylabrobot_slot_type_name"] = slot_data[
                        "pylabrobot_slot_type_name"
                    ]
                if slot_data.get("allowed_resource_definition_names"):
                    slot_specific_details["allowed_resource_definition_names"] = (
                        slot_data["allowed_resource_definition_names"]
                    )
                if slot_data.get("accepts_tips") is not None:
                    slot_specific_details["accepts_tips"] = slot_data["accepts_tips"]
                if slot_data.get("accepts_plates") is not None:
                    slot_specific_details["accepts_plates"] = slot_data[
                        "accepts_plates"
                    ]
                if slot_data.get("accepts_tubes") is not None:
                    slot_specific_details["accepts_tubes"] = slot_data["accepts_tubes"]
                if slot_data.get("notes"):  # Slot notes
                    slot_specific_details["notes"] = slot_data["notes"]

                new_slot = DeckSlotDefinitionOrm(
                    deck_type_definition_id=deck_type_orm.id,
                    slot_name=slot_data["slot_name"],
                    nominal_x_mm=slot_data.get(
                        "location_x_mm"
                    ),  # Pydantic: location_x_mm -> ORM: nominal_x_mm
                    nominal_y_mm=slot_data.get(
                        "location_y_mm"
                    ),  # Pydantic: location_y_mm -> ORM: nominal_y_mm
                    nominal_z_mm=slot_data.get(
                        "location_z_mm"
                    ),  # Pydantic: location_z_mm -> ORM: nominal_z_mm
                    accepted_resource_categories_json=slot_data.get(
                        "allowed_resource_categories"
                    ),  # Pydantic: allowed_resource_categories
                    slot_specific_details_json=slot_specific_details
                    if slot_specific_details
                    else None,
                )
                db.add(new_slot)

        await db.commit()
        await db.refresh(deck_type_orm)
        # Eagerly load slot_definitions again after commit & refresh for the returned object
        if deck_type_orm.id:
            refreshed_deck_type_result = await db.execute(
                select(DeckTypeDefinitionOrm)
                .options(selectinload(DeckTypeDefinitionOrm.slot_definitions))
                .filter(DeckTypeDefinitionOrm.id == deck_type_orm.id)
            )
            deck_type_orm = refreshed_deck_type_result.scalar_one()

    except IntegrityError as e:
        await db.rollback()
        if "uq_deck_type_definitions_pylabrobot_deck_fqn" in str(e.orig):
            raise ValueError(
                f"A deck type definition with PyLabRobot FQN '{pylabrobot_class_name}' already exists."
            )
        elif "uq_deck_slot_definition" in str(
            e.orig
        ):  # Should be caught per slot ideally
            raise ValueError(
                f"A slot definition with the same name might already exist for this deck type. Details: {e}"
            )
        raise ValueError(
            f"Database integrity error for deck type definition '{pylabrobot_class_name}'. Details: {e}"
        )
    except Exception as e:
        await db.rollback()
        raise e

    return deck_type_orm


async def get_deck_type_definition_by_id(
    db: AsyncSession, deck_type_id: int
) -> Optional[DeckTypeDefinitionOrm]:
    """
    Retrieves a specific deck type definition by its ID, including its slot definitions.
    """
    stmt = (
        select(DeckTypeDefinitionOrm)
        .options(selectinload(DeckTypeDefinitionOrm.slot_definitions))
        .filter(DeckTypeDefinitionOrm.id == deck_type_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_deck_type_definition_by_fqn(
    db: AsyncSession, pylabrobot_deck_fqn: str
) -> Optional[DeckTypeDefinitionOrm]:
    """
    Retrieves a specific deck type definition by its PyLabRobot FQN,
    including its slot definitions.
    """
    stmt = (
        select(DeckTypeDefinitionOrm)
        .options(selectinload(DeckTypeDefinitionOrm.slot_definitions))
        .filter(DeckTypeDefinitionOrm.pylabrobot_deck_fqn == pylabrobot_deck_fqn)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_deck_type_definitions(
    db: AsyncSession, limit: int = 100, offset: int = 0
) -> List[DeckTypeDefinitionOrm]:
    """
    Lists all deck type definitions with pagination, including their slot definitions.
    """
    stmt = (
        select(DeckTypeDefinitionOrm)
        .options(selectinload(DeckTypeDefinitionOrm.slot_definitions))
        .order_by(DeckTypeDefinitionOrm.display_name)
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def add_deck_slot_definitions(
    db: AsyncSession,
    deck_type_definition_id: int,
    new_slots_data: List[
        Dict[str, Any]
    ],  # List of dicts, each based on DeckSlotDefinitionCreate
) -> List[DeckSlotDefinitionOrm]:
    """
    Adds multiple new slot definitions to an existing deck type definition.
    This function appends slots. If a slot name conflicts with an existing one
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

    created_slots: List[DeckSlotDefinitionOrm] = []
    try:
        for slot_data in new_slots_data:
            slot_specific_details = slot_data.get("slot_specific_details_json", {})

            # Map Pydantic-like fields to slot_specific_details_json
            # This logic is similar to the one in add_or_update_deck_type_definition
            if slot_data.get("pylabrobot_slot_type_name"):
                slot_specific_details["pylabrobot_slot_type_name"] = slot_data[
                    "pylabrobot_slot_type_name"
                ]
            if slot_data.get("allowed_resource_definition_names"):
                slot_specific_details["allowed_resource_definition_names"] = slot_data[
                    "allowed_resource_definition_names"
                ]
            if slot_data.get("accepts_tips") is not None:
                slot_specific_details["accepts_tips"] = slot_data["accepts_tips"]
            if slot_data.get("accepts_plates") is not None:
                slot_specific_details["accepts_plates"] = slot_data["accepts_plates"]
            if slot_data.get("accepts_tubes") is not None:
                slot_specific_details["accepts_tubes"] = slot_data["accepts_tubes"]
            if "notes" in slot_data:  # Slot-specific notes
                slot_specific_details["notes"] = slot_data["notes"]

            new_slot = DeckSlotDefinitionOrm(
                deck_type_definition_id=deck_type_definition_id,
                slot_name=slot_data["slot_name"],
                nominal_x_mm=slot_data.get("location_x_mm"),
                nominal_y_mm=slot_data.get("location_y_mm"),
                nominal_z_mm=slot_data.get("location_z_mm"),
                accepted_resource_categories_json=slot_data.get(
                    "allowed_resource_categories"
                ),
                slot_specific_details_json=slot_specific_details
                if slot_specific_details
                else None,
            )
            db.add(new_slot)
            created_slots.append(new_slot)

        await db.flush()  # Use flush to catch IntegrityErrors before commit, allowing partial operations if designed so (though here we rollback all)
        await db.commit()
        for slot in created_slots:  # Refresh each created slot
            await db.refresh(slot)

    except IntegrityError as e:
        await db.rollback()
        if "uq_deck_slot_definition" in str(e.orig):
            # Attempt to identify which slot caused the issue if possible, or give a general message.
            # For simplicity, a general message is used here.
            raise ValueError(
                f"Failed to add one or more slot definitions to deck type ID {deck_type_definition_id} "
                f"due to a slot name conflict or other integrity constraint. Details: {e}"
            )
        raise ValueError(
            f"Database integrity error while adding slot definitions. Details: {e}"
        )
    except Exception as e:
        await db.rollback()
        raise e

    return created_slots


async def get_slot_definitions_for_deck_type(
    db: AsyncSession, deck_type_definition_id: int
) -> List[DeckSlotDefinitionOrm]:
    """
    Retrieves all slot definitions associated with a specific deck type definition ID.
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
        select(DeckSlotDefinitionOrm)
        .filter(
            DeckSlotDefinitionOrm.deck_type_definition_id == deck_type_definition_id
        )
        .order_by(DeckSlotDefinitionOrm.slot_name)  # Optional: order by slot name
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
