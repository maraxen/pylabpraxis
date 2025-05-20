# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""
praxis/db_services/asset_data_service.py

Service layer for interacting with asset-related data in the database.
This includes Managed Devices, Labware Definitions, Labware Instances,
and Deck Configurations.
"""
import datetime
import json
from typing import Dict, Any, Optional, List, Union

from sqlalchemy.orm import Session as DbSession, joinedload, selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc, or_ # For querying

# Import Asset Management ORM Models
# TODO: ADS-1: Ensure praxis.database_models.asset_management_orm is correctly structured and importable
try:
    from praxis.database_models.asset_management_orm import (
        ManagedDeviceOrm,
        LabwareDefinitionCatalogOrm,
        LabwareInstanceOrm,
        DeckConfigurationOrm,
        DeckConfigurationSlotItemOrm,
        ManagedDeviceStatusEnum,
        LabwareInstanceStatusEnum,
        LabwareCategoryEnum
    )
except ImportError:
    print("WARNING: ADS-1: Could not import Asset ORM models. AssetDataService will have placeholder types.")
    # Define placeholders if models not found (for linting/testing this file in isolation)
    class ManagedDeviceOrm: pass # type: ignore
    class LabwareDefinitionCatalogOrm: pass # type: ignore
    class LabwareInstanceOrm: pass # type: ignore
    class DeckConfigurationOrm: pass # type: ignore
    class DeckConfigurationSlotItemOrm: pass # type: ignore
    class ManagedDeviceStatusEnum(enum.Enum): OFFLINE="offline"; AVAILABLE="available"; IN_USE="in_use" # type: ignore
    class LabwareInstanceStatusEnum(enum.Enum): UNKNOWN="unknown"; AVAILABLE_IN_STORAGE="available_in_storage" # type: ignore
    class LabwareCategoryEnum(enum.Enum): PLATE="plate"; TIP_RACK="tip_rack" # type: ignore


# --- Managed Device Services ---

def add_or_update_managed_device(
    db: DbSession,
    user_friendly_name: str,
    pylabrobot_class_name: str,
    backend_config_json: Optional[Dict[str, Any]] = None,
    current_status: ManagedDeviceStatusEnum = ManagedDeviceStatusEnum.OFFLINE,
    status_details: Optional[str] = None,
    workcell_id: Optional[int] = None,
    physical_location_description: Optional[str] = None,
    properties_json: Optional[Dict[str, Any]] = None,
    device_id: Optional[int] = None # Provide for update
) -> ManagedDeviceOrm:
    """Adds a new managed device or updates an existing one."""
    if device_id:
        device_orm = db.query(ManagedDeviceOrm).filter(ManagedDeviceOrm.id == device_id).first()
        if not device_orm:
            raise ValueError(f"ManagedDeviceOrm with id {device_id} not found for update.")
    else: # Try to find by name for upsert-like behavior or create new
        device_orm = db.query(ManagedDeviceOrm).filter(ManagedDeviceOrm.user_friendly_name == user_friendly_name).first()
        if not device_orm:
            device_orm = ManagedDeviceOrm(user_friendly_name=user_friendly_name)
            db.add(device_orm)

    device_orm.pylabrobot_class_name = pylabrobot_class_name
    device_orm.backend_config_json = backend_config_json
    device_orm.current_status = current_status
    device_orm.status_details = status_details
    device_orm.workcell_id = workcell_id
    device_orm.physical_location_description = physical_location_description
    device_orm.properties_json = properties_json
    # last_seen_online would be updated by a monitoring process

    try:
        db.commit()
        db.refresh(device_orm)
    except IntegrityError:
        db.rollback()
        raise ValueError(f"A device with name '{user_friendly_name}' might already exist or other integrity constraint violated.")
    except Exception as e:
        db.rollback()
        raise e
    return device_orm

def get_managed_device_by_id(db: DbSession, device_id: int) -> Optional[ManagedDeviceOrm]:
    return db.query(ManagedDeviceOrm).filter(ManagedDeviceOrm.id == device_id).first()

def get_managed_device_by_name(db: DbSession, name: str) -> Optional[ManagedDeviceOrm]:
    return db.query(ManagedDeviceOrm).filter(ManagedDeviceOrm.user_friendly_name == name).first()

def list_managed_devices(
    db: DbSession,
    status: Optional[ManagedDeviceStatusEnum] = None,
    pylabrobot_class_filter: Optional[str] = None, # e.g., "Deck", "HeaterShaker"
    workcell_id: Optional[int] = None,
    limit: int = 100, offset: int = 0
) -> List[ManagedDeviceOrm]:
    query = db.query(ManagedDeviceOrm)
    if status:
        query = query.filter(ManagedDeviceOrm.current_status == status)
    if pylabrobot_class_filter:
        # Allows filtering for base classes or specific classes
        query = query.filter(ManagedDeviceOrm.pylabrobot_class_name.like(f"%{pylabrobot_class_filter}%"))
    if workcell_id:
        query = query.filter(ManagedDeviceOrm.workcell_id == workcell_id)
    return query.order_by(ManagedDeviceOrm.user_friendly_name).limit(limit).offset(offset).all()

def update_managed_device_status(
    db: DbSession, device_id: int, new_status: ManagedDeviceStatusEnum,
    status_details: Optional[str] = None,
    current_protocol_run_guid: Optional[str] = None # Set if IN_USE
) -> Optional[ManagedDeviceOrm]:
    device_orm = get_managed_device_by_id(db, device_id)
    if device_orm:
        device_orm.current_status = new_status
        device_orm.status_details = status_details
        if new_status == ManagedDeviceStatusEnum.IN_USE:
            device_orm.current_protocol_run_guid = current_protocol_run_guid
        elif device_orm.current_protocol_run_guid == current_protocol_run_guid: # Clear if no longer in use by this run
             device_orm.current_protocol_run_guid = None
        if new_status != ManagedDeviceStatusEnum.OFFLINE: # Assuming any other status means it was seen
            device_orm.last_seen_online = datetime.datetime.now(datetime.timezone.utc)
        try:
            db.commit()
            db.refresh(device_orm)
        except Exception as e:
            db.rollback()
            raise e
        return device_orm
    return None

# --- Labware Definition Catalog Services ---

def add_or_update_labware_definition(
    db: DbSession,
    pylabrobot_definition_name: str, # Primary Key
    praxis_labware_type_name: Optional[str] = None,
    category: Optional[LabwareCategoryEnum] = None,
    description: Optional[str] = None,
    is_consumable: bool = True,
    nominal_volume_ul: Optional[float] = None,
    material: Optional[str] = None,
    manufacturer: Optional[str] = None,
    plr_definition_details_json: Optional[Dict[str, Any]] = None
) -> LabwareDefinitionCatalogOrm:
    """Adds or updates a labware definition in the catalog."""
    def_orm = db.query(LabwareDefinitionCatalogOrm).filter(
        LabwareDefinitionCatalogOrm.pylabrobot_definition_name == pylabrobot_definition_name
    ).first()

    if not def_orm:
        def_orm = LabwareDefinitionCatalogOrm(pylabrobot_definition_name=pylabrobot_definition_name)
        db.add(def_orm)

    def_orm.praxis_labware_type_name = praxis_labware_type_name
    def_orm.category = category
    def_orm.description = description
    def_orm.is_consumable = is_consumable
    def_orm.nominal_volume_ul = nominal_volume_ul
    def_orm.material = material
    def_orm.manufacturer = manufacturer
    def_orm.plr_definition_details_json = plr_definition_details_json

    try:
        db.commit()
        db.refresh(def_orm)
    except IntegrityError: # Should not happen if PK is pylabrobot_definition_name and we query first
        db.rollback()
        raise ValueError(f"Integrity error for labware definition '{pylabrobot_definition_name}'.")
    except Exception as e:
        db.rollback()
        raise e
    return def_orm

def get_labware_definition(db: DbSession, pylabrobot_definition_name: str) -> Optional[LabwareDefinitionCatalogOrm]:
    return db.query(LabwareDefinitionCatalogOrm).filter(
        LabwareDefinitionCatalogOrm.pylabrobot_definition_name == pylabrobot_definition_name
    ).first()

def list_labware_definitions(
    db: DbSession,
    category: Optional[LabwareCategoryEnum] = None,
    manufacturer: Optional[str] = None,
    is_consumable: Optional[bool] = None,
    limit: int = 100, offset: int = 0
) -> List[LabwareDefinitionCatalogOrm]:
    query = db.query(LabwareDefinitionCatalogOrm)
    if category:
        query = query.filter(LabwareDefinitionCatalogOrm.category == category)
    if manufacturer:
        query = query.filter(LabwareDefinitionCatalogOrm.manufacturer.ilike(f"%{manufacturer}%")) # type: ignore
    if is_consumable is not None:
        query = query.filter(LabwareDefinitionCatalogOrm.is_consumable == is_consumable)
    return query.order_by(LabwareDefinitionCatalogOrm.pylabrobot_definition_name)\
                .limit(limit).offset(offset).all()


# --- Labware Instance Services ---
# TODO: ADS-2: Implement full CRUD for LabwareInstanceOrm, DeckConfigurationOrm, DeckConfigurationSlotItemOrm
# Placeholder for add_labware_instance
def add_labware_instance(
    db: DbSession,
    user_assigned_name: str,
    pylabrobot_definition_name: str,
    initial_status: LabwareInstanceStatusEnum = LabwareInstanceStatusEnum.AVAILABLE_IN_STORAGE,
    lot_number: Optional[str] = None,
    expiry_date: Optional[datetime.datetime] = None,
    properties_json: Optional[Dict[str, Any]] = None,
    physical_location_description: Optional[str] = None,
    is_permanent_fixture: bool = False
) -> LabwareInstanceOrm:
    # Check if definition exists
    definition = get_labware_definition(db, pylabrobot_definition_name)
    if not definition:
        raise ValueError(f"Labware definition '{pylabrobot_definition_name}' not found in catalog.")

    instance_orm = LabwareInstanceOrm(
        user_assigned_name=user_assigned_name,
        pylabrobot_definition_name=pylabrobot_definition_name,
        current_status=initial_status,
        lot_number=lot_number,
        expiry_date=expiry_date,
        properties_json=properties_json,
        physical_location_description=physical_location_description,
        is_permanent_fixture=is_permanent_fixture
    )
    db.add(instance_orm)
    try:
        db.commit()
        db.refresh(instance_orm)
    except IntegrityError:
        db.rollback()
        raise ValueError(f"A labware instance with name '{user_assigned_name}' might already exist.")
    except Exception as e:
        db.rollback()
        raise e
    return instance_orm

def get_labware_instance_by_id(db: DbSession, instance_id: int) -> Optional[LabwareInstanceOrm]:
    return db.query(LabwareInstanceOrm)\
        .options(joinedload(LabwareInstanceOrm.labware_definition),
                 joinedload(LabwareInstanceOrm.location_device))\
        .filter(LabwareInstanceOrm.id == instance_id).first()

def get_labware_instance_by_name(db: DbSession, user_assigned_name: str) -> Optional[LabwareInstanceOrm]:
    return db.query(LabwareInstanceOrm)\
        .options(joinedload(LabwareInstanceOrm.labware_definition),
                 joinedload(LabwareInstanceOrm.location_device))\
        .filter(LabwareInstanceOrm.user_assigned_name == user_assigned_name).first()


def list_labware_instances(
    db: DbSession,
    pylabrobot_definition_name: Optional[str] = None,
    status: Optional[LabwareInstanceStatusEnum] = None,
    location_device_id: Optional[int] = None,
    on_deck_slot: Optional[str] = None, # To find labware in a specific slot on any deck or a specific deck
    limit: int = 100, offset: int = 0
) -> List[LabwareInstanceOrm]:
    query = db.query(LabwareInstanceOrm)\
              .options(joinedload(LabwareInstanceOrm.labware_definition),
                       joinedload(LabwareInstanceOrm.location_device))
    if pylabrobot_definition_name:
        query = query.filter(LabwareInstanceOrm.pylabrobot_definition_name == pylabrobot_definition_name)
    if status:
        query = query.filter(LabwareInstanceOrm.current_status == status)
    if location_device_id: # Labware is on or in this specific device (could be a deck or instrument)
        query = query.filter(LabwareInstanceOrm.location_device_id == location_device_id)
    if on_deck_slot: # Labware is in this specific slot name (implies location_device_id is a deck)
        query = query.filter(LabwareInstanceOrm.current_deck_slot_name == on_deck_slot)
        # Optionally, could combine with location_device_id if you want slot on specific deck

    return query.order_by(LabwareInstanceOrm.user_assigned_name).limit(limit).offset(offset).all()

def update_labware_instance_location_and_status(
    db: DbSession,
    instance_id: int,
    new_status: LabwareInstanceStatusEnum,
    location_device_id: Optional[int] = None, # ID of the ManagedDevice (e.g., a deck)
    current_deck_slot_name: Optional[str] = None,
    physical_location_description: Optional[str] = None,
    properties_json_update: Optional[Dict[str, Any]] = None, # For partial updates to properties
    current_protocol_run_guid: Optional[str] = None # If status is IN_USE
) -> Optional[LabwareInstanceOrm]:
    instance_orm = get_labware_instance_by_id(db, instance_id)
    if instance_orm:
        instance_orm.current_status = new_status
        instance_orm.location_device_id = location_device_id
        instance_orm.current_deck_slot_name = current_deck_slot_name
        instance_orm.physical_location_description = physical_location_description

        if new_status == LabwareInstanceStatusEnum.IN_USE:
            instance_orm.current_protocol_run_guid = current_protocol_run_guid
        elif instance_orm.current_protocol_run_guid == current_protocol_run_guid: # Clear if no longer in use by this run
            instance_orm.current_protocol_run_guid = None

        if properties_json_update:
            if instance_orm.properties_json is None:
                instance_orm.properties_json = {}
            # TODO: ADS-3: Implement a more robust JSON merge for properties_json
            for key, value in properties_json_update.items():
                instance_orm.properties_json[key] = value # Simple top-level merge/overwrite
            # Flag the ORM object as modified if JSON is mutable, to ensure SQLAlchemy picks up change
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(instance_orm, "properties_json")

        try:
            db.commit()
            db.refresh(instance_orm)
        except Exception as e:
            db.rollback()
            raise e
        return instance_orm
    return None


# --- Deck Configuration Services ---
# TODO: ADS-4: Implement services for DeckConfigurationOrm and DeckConfigurationSlotItemOrm
# - create_deck_configuration(db, layout_name, deck_device_id)
# - add_labware_to_deck_configuration_slot(db, deck_config_id, slot_name, labware_instance_id, expected_def_name=None)
# - get_deck_configuration_details(db, deck_config_id or layout_name) -> Optional[DeckConfigurationOrm] (with eager loaded items)
# - list_deck_configurations(db, deck_device_id=None)

