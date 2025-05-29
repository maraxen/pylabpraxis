# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""
praxis/db_services/asset_data_service.py

Service layer for interacting with asset-related data in the database.
This includes Managed Devices, Labware Definitions, Labware Instances,
and Deck Configurations.
"""
import datetime
from typing import Dict, Any, Optional, List

from sqlalchemy.ext.asyncio import AsyncSession # MODIFIED
from sqlalchemy import select, update # MODIFIED
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import flag_modified


from praxis.backend.models.asset_management_orm import (
    ManagedDeviceOrm,
    LabwareDefinitionCatalogOrm,
    LabwareInstanceOrm,
    DeckConfigurationOrm,
    DeckConfigurationSlotItemOrm,
    ManagedDeviceStatusEnum,
    LabwareInstanceStatusEnum
)

# --- Managed Device Services ---

async def add_or_update_managed_device( # MODIFIED
    db: AsyncSession, # MODIFIED
    user_friendly_name: str,
    pylabrobot_class_name: str,
    backend_config_json: Optional[Dict[str, Any]] = None,
    current_status: ManagedDeviceStatusEnum = ManagedDeviceStatusEnum.OFFLINE,
    status_details: Optional[str] = None,
    workcell_id: Optional[int] = None,
    physical_location_description: Optional[str] = None,
    properties_json: Optional[Dict[str, Any]] = None,
    device_id: Optional[int] = None
) -> ManagedDeviceOrm:
    if device_id:
        result = await db.execute(select(ManagedDeviceOrm).filter(ManagedDeviceOrm.id == device_id))
        device_orm = result.scalar_one_or_none()
        if not device_orm:
            raise ValueError(f"ManagedDeviceOrm with id {device_id} not found for update.")
    else:
        result = await db.execute(select(ManagedDeviceOrm).filter(ManagedDeviceOrm.user_friendly_name == user_friendly_name))
        device_orm = result.scalar_one_or_none()
        if not device_orm:
            device_orm = ManagedDeviceOrm(user_friendly_name=user_friendly_name)
            db.add(device_orm)

    device_orm.pylabrobot_class_name = pylabrobot_class_name
    device_orm.backend_config_json = backend_config_json # type: ignore
    device_orm.current_status = current_status
    device_orm.status_details = status_details
    device_orm.workcell_id = workcell_id # type: ignore
    device_orm.physical_location_description = physical_location_description
    device_orm.properties_json = properties_json # type: ignore

    try:
        await db.commit()
        await db.refresh(device_orm)
    except IntegrityError:
        await db.rollback()
        raise ValueError(f"A device with name '{user_friendly_name}' might already exist or other integrity constraint violated.")
    except Exception as e:
        await db.rollback()
        raise e
    return device_orm

async def get_managed_device_by_id(db: AsyncSession, device_id: int) -> Optional[ManagedDeviceOrm]: # MODIFIED
    result = await db.execute(select(ManagedDeviceOrm).filter(ManagedDeviceOrm.id == device_id))
    return result.scalar_one_or_none()

async def get_managed_device_by_name(db: AsyncSession, name: str) -> Optional[ManagedDeviceOrm]: # MODIFIED
    result = await db.execute(select(ManagedDeviceOrm).filter(ManagedDeviceOrm.user_friendly_name == name))
    return result.scalar_one_or_none()

async def list_managed_devices( # MODIFIED
    db: AsyncSession, # MODIFIED
    status: Optional[ManagedDeviceStatusEnum] = None,
    pylabrobot_class_filter: Optional[str] = None,
    workcell_id: Optional[int] = None,
    limit: int = 100, offset: int = 0
) -> List[ManagedDeviceOrm]:
    stmt = select(ManagedDeviceOrm)
    if status:
        stmt = stmt.filter(ManagedDeviceOrm.current_status == status)
    if pylabrobot_class_filter:
        stmt = stmt.filter(ManagedDeviceOrm.pylabrobot_class_name.like(f"%{pylabrobot_class_filter}%"))
    if workcell_id:
        stmt = stmt.filter(ManagedDeviceOrm.workcell_id == workcell_id)
    stmt = stmt.order_by(ManagedDeviceOrm.user_friendly_name).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def update_managed_device_status( # MODIFIED
    db: AsyncSession, device_id: int, new_status: ManagedDeviceStatusEnum, # MODIFIED
    status_details: Optional[str] = None,
    current_protocol_run_guid: Optional[str] = None
) -> Optional[ManagedDeviceOrm]:
    device_orm = await get_managed_device_by_id(db, device_id)
    if device_orm:
        device_orm.current_status = new_status
        device_orm.status_details = status_details
        if new_status == ManagedDeviceStatusEnum.IN_USE:
            device_orm.current_protocol_run_guid = current_protocol_run_guid
        elif device_orm.current_protocol_run_guid == current_protocol_run_guid:
              device_orm.current_protocol_run_guid = None
        if new_status != ManagedDeviceStatusEnum.OFFLINE:
            device_orm.last_seen_online = datetime.datetime.now(datetime.timezone.utc)
        try:
            await db.commit()
            await db.refresh(device_orm)
        except Exception as e:
            await db.rollback()
            raise e
        return device_orm
    return None

async def delete_managed_device(db: AsyncSession, device_id: int) -> bool: # MODIFIED
    device_orm = await get_managed_device_by_id(db, device_id)
    if not device_orm:
        return False
    try:
        await db.delete(device_orm) #MODIFIED
        await db.commit()
        return True
    except IntegrityError as e:
        await db.rollback()
        print(f"ERROR: ADS: IntegrityError deleting managed device ID {device_id}: {e}")
        raise ValueError(f"Cannot delete device ID {device_id} due to existing references. Details: {e}")
    except Exception as e:
        await db.rollback()
        print(f"ERROR: ADS: Exception deleting managed device ID {device_id}: {e}")
        raise e


# --- Labware Definition Catalog Services ---

async def add_or_update_labware_definition( # MODIFIED
    db: AsyncSession, # MODIFIED
    pylabrobot_definition_name: str,
    python_fqn: str,
    praxis_labware_type_name: Optional[str] = None,
    description: Optional[str] = None,
    is_consumable: bool = True,
    nominal_volume_ul: Optional[float] = None,
    material: Optional[str] = None,
    manufacturer: Optional[str] = None,
    plr_definition_details_json: Optional[Dict[str, Any]] = None
) -> LabwareDefinitionCatalogOrm:
    result = await db.execute(select(LabwareDefinitionCatalogOrm).filter(
        LabwareDefinitionCatalogOrm.pylabrobot_definition_name == pylabrobot_definition_name
    ))
    def_orm = result.scalar_one_or_none()

    if not def_orm:
        def_orm = LabwareDefinitionCatalogOrm(pylabrobot_definition_name=pylabrobot_definition_name)
        db.add(def_orm)

    def_orm.python_fqn = python_fqn
    def_orm.praxis_labware_type_name = praxis_labware_type_name
    def_orm.description = description
    def_orm.is_consumable = is_consumable
    def_orm.nominal_volume_ul = nominal_volume_ul
    def_orm.material = material
    def_orm.manufacturer = manufacturer
    def_orm.plr_definition_details_json = plr_definition_details_json # type: ignore

    try:
        await db.commit()
        await db.refresh(def_orm)
    except IntegrityError:
        await db.rollback()
        raise ValueError(f"Integrity error for labware definition '{pylabrobot_definition_name}'.")
    except Exception as e:
        await db.rollback()
        raise e
    return def_orm

async def get_labware_definition(db: AsyncSession, pylabrobot_definition_name: str) -> Optional[LabwareDefinitionCatalogOrm]: # MODIFIED
    result = await db.execute(select(LabwareDefinitionCatalogOrm).filter(
        LabwareDefinitionCatalogOrm.pylabrobot_definition_name == pylabrobot_definition_name
    ))
    return result.scalar_one_or_none()

async def list_labware_definitions( # MODIFIED
    db: AsyncSession, # MODIFIED
    manufacturer: Optional[str] = None,
    is_consumable: Optional[bool] = None,
    limit: int = 100, offset: int = 0
) -> List[LabwareDefinitionCatalogOrm]:
    stmt = select(LabwareDefinitionCatalogOrm)
    if manufacturer:
        stmt = stmt.filter(LabwareDefinitionCatalogOrm.manufacturer.ilike(f"%{manufacturer}%")) # type: ignore
    if is_consumable is not None:
        stmt = stmt.filter(LabwareDefinitionCatalogOrm.is_consumable == is_consumable)
    stmt = stmt.order_by(LabwareDefinitionCatalogOrm.pylabrobot_definition_name)\
                .limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def get_labware_definition_by_name(db: AsyncSession, pylabrobot_definition_name: str) -> Optional[LabwareDefinitionCatalogOrm]: # MODIFIED
    return await get_labware_definition(db, pylabrobot_definition_name)

async def get_labware_definition_by_fqn(db: AsyncSession, python_fqn: str) -> Optional[LabwareDefinitionCatalogOrm]: # MODIFIED
    result = await db.execute(select(LabwareDefinitionCatalogOrm).filter(
        LabwareDefinitionCatalogOrm.python_fqn == python_fqn
    ))
    return result.scalar_one_or_none()

async def delete_labware_definition(db: AsyncSession, pylabrobot_definition_name: str) -> bool: # MODIFIED
    def_orm = await get_labware_definition(db, pylabrobot_definition_name)
    if not def_orm:
        return False

    try:
        await db.delete(def_orm) # MODIFIED
        await db.commit()
        return True
    except IntegrityError as e:
        await db.rollback()
        print(f"ERROR: ADS: IntegrityError deleting labware definition '{pylabrobot_definition_name}': {e}")
        return False
    except Exception as e:
        await db.rollback()
        print(f"ERROR: ADS: Exception deleting labware definition '{pylabrobot_definition_name}': {e}")
        raise e

# --- Labware Instance Services ---
async def add_labware_instance( # MODIFIED
    db: AsyncSession, # MODIFIED
    user_assigned_name: str,
    pylabrobot_definition_name: str,
    initial_status: LabwareInstanceStatusEnum = LabwareInstanceStatusEnum.AVAILABLE_IN_STORAGE,
    lot_number: Optional[str] = None,
    expiry_date: Optional[datetime.datetime] = None,
    properties_json: Optional[Dict[str, Any]] = None,
    physical_location_description: Optional[str] = None,
    is_permanent_fixture: bool = False
) -> LabwareInstanceOrm:
    definition = await get_labware_definition(db, pylabrobot_definition_name)
    if not definition:
        raise ValueError(f"Labware definition '{pylabrobot_definition_name}' not found in catalog.")

    instance_orm = LabwareInstanceOrm(
        user_assigned_name=user_assigned_name,
        pylabrobot_definition_name=pylabrobot_definition_name,
        current_status=initial_status,
        lot_number=lot_number,
        expiry_date=expiry_date,
        properties_json=properties_json, # type: ignore
        physical_location_description=physical_location_description,
        is_permanent_fixture=is_permanent_fixture
    )
    db.add(instance_orm)
    try:
        await db.commit()
        await db.refresh(instance_orm)
    except IntegrityError:
        await db.rollback()
        raise ValueError(f"A labware instance with name '{user_assigned_name}' might already exist.")
    except Exception as e:
        await db.rollback()
        raise e
    return instance_orm

async def get_labware_instance_by_id(db: AsyncSession, instance_id: int) -> Optional[LabwareInstanceOrm]: # MODIFIED
    stmt = select(LabwareInstanceOrm)\
        .options(joinedload(LabwareInstanceOrm.labware_definition),
                 joinedload(LabwareInstanceOrm.location_device))\
        .filter(LabwareInstanceOrm.id == instance_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_labware_instance_by_name(db: AsyncSession, user_assigned_name: str) -> Optional[LabwareInstanceOrm]: # MODIFIED
    stmt = select(LabwareInstanceOrm)\
        .options(joinedload(LabwareInstanceOrm.labware_definition),
                 joinedload(LabwareInstanceOrm.location_device))\
        .filter(LabwareInstanceOrm.user_assigned_name == user_assigned_name)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_labware_instances( # MODIFIED
    db: AsyncSession, # MODIFIED
    pylabrobot_definition_name: Optional[str] = None,
    status: Optional[LabwareInstanceStatusEnum] = None,
    location_device_id: Optional[int] = None,
    on_deck_slot: Optional[str] = None,
    limit: int = 100, offset: int = 0
) -> List[LabwareInstanceOrm]:
    stmt = select(LabwareInstanceOrm)\
              .options(joinedload(LabwareInstanceOrm.labware_definition),
                       joinedload(LabwareInstanceOrm.location_device))
    if pylabrobot_definition_name:
        stmt = stmt.filter(LabwareInstanceOrm.pylabrobot_definition_name == pylabrobot_definition_name)
    if status:
        stmt = stmt.filter(LabwareInstanceOrm.current_status == status)
    if location_device_id:
        stmt = stmt.filter(LabwareInstanceOrm.location_device_id == location_device_id)
    if on_deck_slot:
        stmt = stmt.filter(LabwareInstanceOrm.current_deck_slot_name == on_deck_slot)

    stmt = stmt.order_by(LabwareInstanceOrm.user_assigned_name).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def update_labware_instance_location_and_status( # MODIFIED
    db: AsyncSession, # MODIFIED
    labware_instance_id: int,
    new_status: Optional[LabwareInstanceStatusEnum] = None,
    location_device_id: Optional[int] = None,
    current_deck_slot_name: Optional[str] = None,
    physical_location_description: Optional[str] = None,
    properties_json_update: Optional[Dict[str, Any]] = None,
    current_protocol_run_guid: Optional[str] = None,
    status_details: Optional[str] = None
) -> Optional[LabwareInstanceOrm]:
    instance_orm = await get_labware_instance_by_id(db, labware_instance_id)
    if instance_orm:
        if new_status is not None:
            instance_orm.current_status = new_status

        if location_device_id is not None or \
           current_deck_slot_name is not None or \
           physical_location_description is not None:
            instance_orm.location_device_id = location_device_id # type: ignore
            instance_orm.current_deck_slot_name = current_deck_slot_name
            instance_orm.physical_location_description = physical_location_description

        if status_details is not None:
            instance_orm.status_details = status_details

        if new_status == LabwareInstanceStatusEnum.IN_USE and current_protocol_run_guid is not None:
            instance_orm.current_protocol_run_guid = current_protocol_run_guid
        elif new_status != LabwareInstanceStatusEnum.IN_USE :
            if instance_orm.current_protocol_run_guid is not None :
                 instance_orm.current_protocol_run_guid = None

        if properties_json_update is not None:
            instance_orm.properties_json = properties_json_update # type: ignore
            if instance_orm.properties_json is not None:
                 flag_modified(instance_orm, "properties_json")

        try:
            await db.commit()
            await db.refresh(instance_orm)
        except Exception as e:
            await db.rollback()
            raise e
        return instance_orm
    return None

async def delete_labware_instance(db: AsyncSession, instance_id: int) -> bool: # MODIFIED
    stmt = select(LabwareInstanceOrm).filter(LabwareInstanceOrm.id == instance_id)
    result = await db.execute(stmt)
    instance_orm = result.scalar_one_or_none()

    if not instance_orm:
        return False

    try:
        await db.delete(instance_orm) # MODIFIED
        await db.commit()
        return True
    except IntegrityError as e:
        await db.rollback()
        print(f"ERROR: ADS: IntegrityError deleting labware instance ID {instance_id}: {e}")
        raise ValueError(f"Cannot delete labware instance ID {instance_id} due to existing references (e.g., in deck layouts). Details: {e}")
    except Exception as e:
        await db.rollback()
        print(f"ERROR: ADS: Exception deleting labware instance ID {instance_id}: {e}")
        raise e


# --- Deck Configuration Services ---

async def create_deck_layout( # MODIFIED
    db: AsyncSession, # MODIFIED
    layout_name: str,
    deck_device_id: int,
    description: Optional[str] = None,
    slot_items_data: Optional[List[Dict[str, Any]]] = None
) -> DeckConfigurationOrm:
    deck_device_result = await db.execute(select(ManagedDeviceOrm).filter(ManagedDeviceOrm.id == deck_device_id))
    deck_device = deck_device_result.scalar_one_or_none()
    if not deck_device:
        raise ValueError(f"ManagedDeviceOrm (Deck Device) with id {deck_device_id} not found.")

    deck_layout_orm = DeckConfigurationOrm(
        layout_name=layout_name,
        deck_device_id=deck_device_id,
        description=description
    )
    db.add(deck_layout_orm)

    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise ValueError(f"A deck layout with name '{layout_name}' might already exist.")
    except Exception as e:
        await db.rollback()
        raise e

    if slot_items_data:
        for item_data in slot_items_data:
            labware_instance_id = item_data.get("labware_instance_id")
            if labware_instance_id:
                labware_instance_result = await db.execute(select(LabwareInstanceOrm).filter(LabwareInstanceOrm.id == labware_instance_id))
                if not labware_instance_result.scalar_one_or_none():
                    await db.rollback()
                    raise ValueError(f"LabwareInstanceOrm with id {labware_instance_id} for slot '{item_data.get('slot_name')}' not found.")

            expected_def_name = item_data.get("expected_labware_definition_name")
            if expected_def_name:
                if not await get_labware_definition(db, expected_def_name):
                    await db.rollback()
                    raise ValueError(f"LabwareDefinitionCatalogOrm with name '{expected_def_name}' for slot '{item_data.get('slot_name')}' not found.")

            slot_item = DeckConfigurationSlotItemOrm(
                deck_configuration_id=deck_layout_orm.id,
                slot_name=item_data["slot_name"],
                labware_instance_id=labware_instance_id,
                expected_labware_definition_name=expected_def_name
            )
            db.add(slot_item)
    try:
        await db.commit()
        await db.refresh(deck_layout_orm)
        if deck_layout_orm.id:
            return await get_deck_layout_by_id(db, deck_layout_orm.id) # type: ignore
    except IntegrityError as e:
        await db.rollback()
        raise ValueError(f"Error creating deck layout or its slot items: {e}")
    except Exception as e:
        await db.rollback()
        raise e
    return deck_layout_orm


async def get_deck_layout_by_id(db: AsyncSession, deck_layout_id: int) -> Optional[DeckConfigurationOrm]: # MODIFIED
    stmt = select(DeckConfigurationOrm)\
        .options(
            selectinload(DeckConfigurationOrm.slot_items)
            .selectinload(DeckConfigurationSlotItemOrm.labware_instance)
            .selectinload(LabwareInstanceOrm.labware_definition),
            selectinload(DeckConfigurationOrm.slot_items)
            .selectinload(DeckConfigurationSlotItemOrm.expected_labware_definition)
        )\
        .filter(DeckConfigurationOrm.id == deck_layout_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_deck_layout_by_name(db: AsyncSession, layout_name: str) -> Optional[DeckConfigurationOrm]: # MODIFIED
    stmt = select(DeckConfigurationOrm)\
        .options(
            selectinload(DeckConfigurationOrm.slot_items)
            .selectinload(DeckConfigurationSlotItemOrm.labware_instance)
            .selectinload(LabwareInstanceOrm.labware_definition),
            selectinload(DeckConfigurationOrm.slot_items)
            .selectinload(DeckConfigurationSlotItemOrm.expected_labware_definition)
        )\
        .filter(DeckConfigurationOrm.layout_name == layout_name)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def list_deck_layouts( # MODIFIED
    db: AsyncSession, # MODIFIED
    deck_device_id: Optional[int] = None,
    limit: int = 100, offset: int = 0
) -> List[DeckConfigurationOrm]:
    stmt = select(DeckConfigurationOrm)\
        .options(
            selectinload(DeckConfigurationOrm.slot_items)
            .selectinload(DeckConfigurationSlotItemOrm.labware_instance)
            .selectinload(LabwareInstanceOrm.labware_definition),
            selectinload(DeckConfigurationOrm.slot_items)
            .selectinload(DeckConfigurationSlotItemOrm.expected_labware_definition)
        )
    if deck_device_id is not None:
        stmt = stmt.filter(DeckConfigurationOrm.deck_device_id == deck_device_id)
    stmt = stmt.order_by(DeckConfigurationOrm.layout_name).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def update_deck_layout( # MODIFIED
    db: AsyncSession, # MODIFIED
    deck_layout_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    deck_device_id: Optional[int] = None,
    slot_items_data: Optional[List[Dict[str, Any]]] = None
) -> Optional[DeckConfigurationOrm]:
    deck_layout_orm = await get_deck_layout_by_id(db, deck_layout_id)
    if not deck_layout_orm:
        return None

    if name is not None:
        deck_layout_orm.layout_name = name
    if description is not None:
        deck_layout_orm.description = description
    if deck_device_id is not None:
        new_deck_device_result = await db.execute(select(ManagedDeviceOrm).filter(ManagedDeviceOrm.id == deck_device_id))
        if not new_deck_device_result.scalar_one_or_none():
            raise ValueError(f"New ManagedDeviceOrm (Deck Device) with id {deck_device_id} not found.")
        deck_layout_orm.deck_device_id = deck_device_id

    if slot_items_data is not None:
        if deck_layout_orm.slot_items:
            for item in deck_layout_orm.slot_items:
                await db.delete(item) # MODIFIED
        await db.flush()

        for item_data in slot_items_data:
            labware_instance_id = item_data.get("labware_instance_id")
            if labware_instance_id:
                labware_instance_result = await db.execute(select(LabwareInstanceOrm).filter(LabwareInstanceOrm.id == labware_instance_id))
                if not labware_instance_result.scalar_one_or_none():
                    await db.rollback()
                    raise ValueError(f"LabwareInstanceOrm with id {labware_instance_id} for slot '{item_data.get('slot_name')}' not found.")

            expected_def_name = item_data.get("expected_labware_definition_name")
            if expected_def_name:
                if not await get_labware_definition(db, expected_def_name):
                    await db.rollback()
                    raise ValueError(f"LabwareDefinitionCatalogOrm with name '{expected_def_name}' for slot '{item_data.get('slot_name')}' not found.")

            slot_item = DeckConfigurationSlotItemOrm(
                deck_configuration_id=deck_layout_orm.id,
                slot_name=item_data["slot_name"],
                labware_instance_id=labware_instance_id,
                expected_labware_definition_name=expected_def_name
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

async def delete_deck_layout(db: AsyncSession, deck_layout_id: int) -> bool: # MODIFIED
    deck_layout_orm = await get_deck_layout_by_id(db, deck_layout_id) # Ensures items are loaded for cascade
    if not deck_layout_orm:
        return False

    try:
        await db.delete(deck_layout_orm) # MODIFIED
        await db.commit()
        return True
    except IntegrityError as e:
        await db.rollback()
        print(f"ERROR: ADS: IntegrityError deleting deck layout ID {deck_layout_id}: {e}")
        return False
    except Exception as e:
        await db.rollback()
        raise e
