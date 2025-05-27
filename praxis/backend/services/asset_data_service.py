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

def delete_managed_device(db: DbSession, device_id: int) -> bool:
    """Deletes a managed device. Returns True if deletion was successful, False otherwise."""
    device_orm = db.query(ManagedDeviceOrm).filter(ManagedDeviceOrm.id == device_id).first()
    if not device_orm:
        return False

    # Check for related entities that might prevent deletion if not handled by cascades
    # For example, if this device is a deck_device in DeckConfigurationOrm
    # or a location_device_id in LabwareInstanceOrm.
    # The ORM definitions should ideally have cascade delete settings or ondelete="SET NULL"
    # for these relationships.
    # ManagedDeviceOrm.deck_configurations: if any, deletion might be blocked by FK if not cascaded.
    # ManagedDeviceOrm.located_labware_instances: if any, deletion might be blocked by FK if not cascaded.

    # For now, we assume that if a device is critical (e.g., a deck with layouts),
    # the user/system should handle those dependencies before deleting the device,
    # or the database schema (via cascades or SET NULL) allows it.
    # A more robust implementation might check these and raise specific errors.

    try:
        db.delete(device_orm)
        db.commit()
        return True
    except IntegrityError as e:
        db.rollback()
        print(f"ERROR: ADS: IntegrityError deleting managed device ID {device_id}: {e}")
        # This typically means there are still child records pointing to this device
        # (e.g., LabwareInstanceOrm.location_device_id or DeckConfigurationOrm.deck_device_id)
        # and the foreign key constraints are preventing deletion without ON DELETE CASCADE/SET NULL.
        raise ValueError(f"Cannot delete device ID {device_id} due to existing references. Details: {e}")
    except Exception as e:
        db.rollback()
        print(f"ERROR: ADS: Exception deleting managed device ID {device_id}: {e}")
        raise e # Re-raise other unexpected errors


# --- Labware Definition Catalog Services ---

def add_or_update_labware_definition(
    db: DbSession,
    pylabrobot_definition_name: str, # Primary Key
    python_fqn: str, # ADDED new argument
    praxis_labware_type_name: Optional[str] = None,
    category: Optional[LabwareCategoryEnum] = None,
    description: Optional[str] = None,
    is_consumable: bool = True,
    nominal_volume_ul: Optional[float] = None,
    material: Optional[str] = None,
    manufacturer: Optional[str] = None,
    plr_definition_details_json: Optional[Dict[str, Any]] = None
    # TODO: Add other fields like size_x_mm, model, etc., to this signature
    # if they are to be directly saved by AssetManager.
    # For now, only python_fqn is added based on the subtask.
) -> LabwareDefinitionCatalogOrm:
    """Adds or updates a labware definition in the catalog."""
    def_orm = db.query(LabwareDefinitionCatalogOrm).filter(
        LabwareDefinitionCatalogOrm.pylabrobot_definition_name == pylabrobot_definition_name
    ).first()

    if not def_orm:
        def_orm = LabwareDefinitionCatalogOrm(pylabrobot_definition_name=pylabrobot_definition_name)
        db.add(def_orm)
    
    def_orm.python_fqn = python_fqn # ADDED assignment
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

def get_labware_definition_by_name(db: DbSession, pylabrobot_definition_name: str) -> Optional[LabwareDefinitionCatalogOrm]:
    """Fetches a labware definition by its pylabrobot_definition_name."""
    # This is an alias for get_labware_definition for semantic clarity where "name" is the PLR definition name.
    return get_labware_definition(db, pylabrobot_definition_name)

def get_labware_definition_by_fqn(db: DbSession, python_fqn: str) -> Optional[LabwareDefinitionCatalogOrm]:
    """Fetches a labware definition by its Python Fully Qualified Name (FQN)."""
    return db.query(LabwareDefinitionCatalogOrm).filter(
        LabwareDefinitionCatalogOrm.python_fqn == python_fqn
    ).first()

def delete_labware_definition(db: DbSession, pylabrobot_definition_name: str) -> bool:
    """Deletes a labware definition from the catalog."""
    def_orm = db.query(LabwareDefinitionCatalogOrm).filter(
        LabwareDefinitionCatalogOrm.pylabrobot_definition_name == pylabrobot_definition_name
    ).first()

    if not def_orm:
        return False  # Not found

    try:
        db.delete(def_orm)
        db.commit()
        return True
    except IntegrityError as e: # Should be rare for definitions unless linked from instances directly
        db.rollback()
        print(f"ERROR: ADS: IntegrityError deleting labware definition '{pylabrobot_definition_name}': {e}")
        # Potentially re-raise or handle as a specific application error if needed
        # For now, let's say deletion failed but doesn't crash the app
        return False 
    except Exception as e:
        db.rollback()
        print(f"ERROR: ADS: Exception deleting labware definition '{pylabrobot_definition_name}': {e}")
        raise e # Re-raise other unexpected errors

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
    if properties_json is not None:
        print(f"DEBUG: ADS: Setting properties_json for new labware instance '{user_assigned_name}': {properties_json}")
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
    labware_instance_id: int, # Renamed for clarity from instance_id
    new_status: Optional[LabwareInstanceStatusEnum] = None, # MODIFIED: Made optional
    location_device_id: Optional[int] = None, 
    current_deck_slot_name: Optional[str] = None,
    physical_location_description: Optional[str] = None,
    properties_json_update: Optional[Dict[str, Any]] = None,
    current_protocol_run_guid: Optional[str] = None, # Explicitly pass None to clear
    status_details: Optional[str] = None
) -> Optional[LabwareInstanceOrm]:
    instance_orm = get_labware_instance_by_id(db, labware_instance_id)
    if instance_orm:
        if new_status is not None:
            instance_orm.current_status = new_status
        
        # Location update logic:
        # If any location field is explicitly provided, update all.
        # To clear location, pass None for location_device_id, current_deck_slot_name,
        # and potentially an empty string or specific value for physical_location_description.
        if location_device_id is not None or \
           current_deck_slot_name is not None or \
           physical_location_description is not None: # Check if any location update is intended
            instance_orm.location_device_id = location_device_id
            instance_orm.current_deck_slot_name = current_deck_slot_name
            instance_orm.physical_location_description = physical_location_description
            
        if status_details is not None:
            if hasattr(instance_orm, 'status_details'): # Should always exist now
                instance_orm.status_details = status_details
            # No else needed as status_details should exist based on ORM.

        # Simplified logic for current_protocol_run_guid:
        # - If new_status is IN_USE, set/update the GUID.
        # - If new_status is anything else, or if current_protocol_run_guid is explicitly passed as None, clear it.
        if new_status == LabwareInstanceStatusEnum.IN_USE and current_protocol_run_guid is not None:
            instance_orm.current_protocol_run_guid = current_protocol_run_guid
        elif new_status != LabwareInstanceStatusEnum.IN_USE : # If not IN_USE (or new_status is None but we are clearing GUID)
            if instance_orm.current_protocol_run_guid is not None : # Only clear if it was set
                 instance_orm.current_protocol_run_guid = None # Clears if status moves away from IN_USE
        # If current_protocol_run_guid is explicitly passed as None, it will also be cleared by direct assignment below
        # only if it's part of a broader update. For now, GUID is primarily tied to IN_USE status.
        # A more explicit clearing of current_protocol_run_guid might be needed if it can be None while IN_USE.
        # current_protocol_run_guid is passed as an argument. If it's None, it will be set to None if status is not IN_USE.
        # If status is IN_USE, and current_protocol_run_guid is None, this is an issue.
        # The logic above ensures it's set if new_status is IN_USE.
        # If current_protocol_run_guid is passed as a specific value, it will be set if status is IN_USE.
        # If current_protocol_run_guid is passed as None, it will be set to None if status is not IN_USE.

        if properties_json_update is not None: # Allow passing empty dict to clear
            print(f"DEBUG: ADS: Updating properties_json for labware instance ID {labware_instance_id}: {properties_json_update}")
            # If properties_json_update is an empty dict {}, it effectively clears existing properties.
            # If it's None, properties_json is not touched.
            instance_orm.properties_json = properties_json_update
            
            from sqlalchemy.orm.attributes import flag_modified # Ensure this import is at top level or handled
            if instance_orm.properties_json is not None: # Only flag if it's not None
                 flag_modified(instance_orm, "properties_json")

        try:
            db.commit()
            db.refresh(instance_orm)
        except Exception as e:
            db.rollback()
            raise e
        return instance_orm
    return None

def delete_labware_instance(db: DbSession, instance_id: int) -> bool:
    """Deletes a labware instance. Returns True if deletion was successful, False otherwise."""
    instance_orm = db.query(LabwareInstanceOrm).filter(LabwareInstanceOrm.id == instance_id).first()
    if not instance_orm:
        return False # Not found
    
    # Check for dependencies:
    # - DeckConfigurationSlotItemOrm.labware_instance_id
    #   The ORM definition for DeckConfigurationSlotItemOrm.labware_instance should specify ondelete behavior.
    #   If it's "SET NULL" or "CASCADE", this direct delete is fine.
    #   If it's "RESTRICT" (default for many DBs if not specified), this delete will fail if referenced.
    #   Assuming for now that if a labware instance is part of a saved deck configuration,
    #   that slot item might need to be cleared/handled first, or the schema allows SET NULL.
    #   For this function, we'll proceed with the delete and let the DB raise IntegrityError if constrained.

    try:
        db.delete(instance_orm)
        db.commit()
        return True
    except IntegrityError as e:
        db.rollback()
        print(f"ERROR: ADS: IntegrityError deleting labware instance ID {instance_id}: {e}")
        # This typically means the instance is referenced in DeckConfigurationSlotItemOrm
        # and the FK constraint is preventing deletion.
        raise ValueError(f"Cannot delete labware instance ID {instance_id} due to existing references (e.g., in deck layouts). Details: {e}")
    except Exception as e:
        db.rollback()
        print(f"ERROR: ADS: Exception deleting labware instance ID {instance_id}: {e}")
        raise e


# --- Deck Configuration Services ---

def _map_orm_to_deck_layout_response_dict(deck_orm: DeckConfigurationOrm) -> Dict: # Not currently used, Pydantic ORM mode preferred
    """Helper to convert DeckConfigurationOrm to a dictionary for Pydantic response models."""
    # This helper is conceptual for now, as Pydantic models will handle direct ORM conversion
    # if properly configured (e.g. with orm_mode=True).
    # However, if complex transformations were needed, this is where they'd go.
    # For now, we'll assume Pydantic can handle the direct ORM object.
    # This function might not be strictly necessary if Pydantic models are well-defined.
    slot_items_list = []
    if deck_orm.slot_items: # Ensure slot_items were loaded
        for item_orm in deck_orm.slot_items:
            slot_items_list.append({
                "id": item_orm.id,
                "deck_configuration_id": item_orm.deck_configuration_id,
                "slot_name": item_orm.slot_name,
                "labware_instance_id": item_orm.labware_instance_id,
                "expected_labware_definition_name": item_orm.expected_labware_definition_name,
                # Potentially include nested labware_instance details if needed by response
            })
    return {
        "id": deck_orm.id,
        "layout_name": deck_orm.layout_name,
        "deck_device_id": deck_orm.deck_device_id,
        "description": deck_orm.description,
        "created_at": deck_orm.created_at.isoformat() if deck_orm.created_at else None,
        "updated_at": deck_orm.updated_at.isoformat() if deck_orm.updated_at else None,
        "slot_items": slot_items_list,
    }

def create_deck_layout(
    db: DbSession,
    layout_name: str,
    deck_device_id: int,
    description: Optional[str] = None,
    slot_items_data: Optional[List[Dict[str, Any]]] = None
) -> DeckConfigurationOrm:
    """Creates a new deck layout configuration."""
    # Check if deck device exists
    deck_device = db.query(ManagedDeviceOrm).filter(ManagedDeviceOrm.id == deck_device_id).first()
    if not deck_device:
        raise ValueError(f"ManagedDeviceOrm (Deck Device) with id {deck_device_id} not found.")

    deck_layout_orm = DeckConfigurationOrm(
        layout_name=layout_name,
        deck_device_id=deck_device_id,
        description=description
    )
    db.add(deck_layout_orm)
    
    # Flush to get deck_layout_orm.id for slot items
    try:
        db.flush() # Get ID before full commit
    except IntegrityError:
        db.rollback()
        raise ValueError(f"A deck layout with name '{layout_name}' might already exist.")
    except Exception as e: # pragma: no cover
        db.rollback()
        raise e

    if slot_items_data:
        for item_data in slot_items_data:
            # Validate labware instance exists
            labware_instance_id = item_data.get("labware_instance_id")
            if labware_instance_id:
                labware_instance = db.query(LabwareInstanceOrm).filter(LabwareInstanceOrm.id == labware_instance_id).first()
                if not labware_instance:
                    db.rollback() # Rollback the deck_layout_orm addition
                    raise ValueError(f"LabwareInstanceOrm with id {labware_instance_id} for slot '{item_data.get('slot_name')}' not found.")
            
            # Validate expected labware definition exists, if provided
            expected_def_name = item_data.get("expected_labware_definition_name")
            if expected_def_name:
                labware_def = get_labware_definition(db, expected_def_name)
                if not labware_def:
                    db.rollback()
                    raise ValueError(f"LabwareDefinitionCatalogOrm with name '{expected_def_name}' for slot '{item_data.get('slot_name')}' not found.")

            slot_item = DeckConfigurationSlotItemOrm(
                deck_configuration_id=deck_layout_orm.id, # type: ignore
                slot_name=item_data["slot_name"],
                labware_instance_id=labware_instance_id,
                expected_labware_definition_name=expected_def_name
            )
            db.add(slot_item)
    
    try:
        db.commit()
        db.refresh(deck_layout_orm)
        # Eagerly load slot_items for the returned object
        if deck_layout_orm.id: # Ensure ID is populated
            return get_deck_layout_by_id(db, deck_layout_orm.id) # type: ignore
    except IntegrityError as e: # Catch potential issues with slot items too
        db.rollback()
        raise ValueError(f"Error creating deck layout or its slot items: {e}")
    except Exception as e: # pragma: no cover
        db.rollback()
        raise e
    return deck_layout_orm # Should ideally be the one with items loaded


def get_deck_layout_by_id(db: DbSession, deck_layout_id: int) -> Optional[DeckConfigurationOrm]:
    """Fetches a deck layout by its ID, with related slot items."""
    return db.query(DeckConfigurationOrm)\
        .options(
            selectinload(DeckConfigurationOrm.slot_items)
            .selectinload(DeckConfigurationSlotItemOrm.labware_instance)
            .selectinload(LabwareInstanceOrm.labware_definition), # Load definition of instance
            selectinload(DeckConfigurationOrm.slot_items)
            .selectinload(DeckConfigurationSlotItemOrm.expected_labware_definition) # Load expected definition directly
        )\
        .filter(DeckConfigurationOrm.id == deck_layout_id).first()

def get_deck_layout_by_name(db: DbSession, layout_name: str) -> Optional[DeckConfigurationOrm]:
    """Fetches a deck layout by its name, with related slot items."""
    return db.query(DeckConfigurationOrm)\
        .options(
            selectinload(DeckConfigurationOrm.slot_items)
            .selectinload(DeckConfigurationSlotItemOrm.labware_instance)
            .selectinload(LabwareInstanceOrm.labware_definition),
            selectinload(DeckConfigurationOrm.slot_items)
            .selectinload(DeckConfigurationSlotItemOrm.expected_labware_definition)
        )\
        .filter(DeckConfigurationOrm.layout_name == layout_name).first()

def list_deck_layouts(
    db: DbSession,
    deck_device_id: Optional[int] = None,
    limit: int = 100, offset: int = 0
) -> List[DeckConfigurationOrm]:
    """Lists deck layouts, optionally filtered by deck_device_id."""
    query = db.query(DeckConfigurationOrm)\
        .options(
            selectinload(DeckConfigurationOrm.slot_items)
            .selectinload(DeckConfigurationSlotItemOrm.labware_instance)
            .selectinload(LabwareInstanceOrm.labware_definition), # Load definition of instance
            selectinload(DeckConfigurationOrm.slot_items)
            .selectinload(DeckConfigurationSlotItemOrm.expected_labware_definition) # Load expected definition directly
        )
    if deck_device_id is not None:
        query = query.filter(DeckConfigurationOrm.deck_device_id == deck_device_id)
    return query.order_by(DeckConfigurationOrm.layout_name).limit(limit).offset(offset).all()

def update_deck_layout(
    db: DbSession,
    deck_layout_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    deck_device_id: Optional[int] = None,
    slot_items_data: Optional[List[Dict[str, Any]]] = None
) -> Optional[DeckConfigurationOrm]:
    """Updates an existing deck layout configuration."""
    deck_layout_orm = get_deck_layout_by_id(db, deck_layout_id) # Use existing getter to ensure items are loaded
    if not deck_layout_orm:
        return None

    if name is not None:
        deck_layout_orm.layout_name = name
    if description is not None: # Allow setting description to empty string
        deck_layout_orm.description = description
    if deck_device_id is not None:
        # Validate new deck device exists
        new_deck_device = db.query(ManagedDeviceOrm).filter(ManagedDeviceOrm.id == deck_device_id).first()
        if not new_deck_device:
            raise ValueError(f"New ManagedDeviceOrm (Deck Device) with id {deck_device_id} not found.")
        deck_layout_orm.deck_device_id = deck_device_id

    if slot_items_data is not None:
        # Simple approach: Delete existing items and create new ones
        # More complex merge logic could be implemented if needed (e.g., update existing, add new, remove old)
        if deck_layout_orm.slot_items:
            for item in deck_layout_orm.slot_items:
                db.delete(item)
        db.flush() # Process deletions

        for item_data in slot_items_data:
            labware_instance_id = item_data.get("labware_instance_id")
            if labware_instance_id:
                labware_instance = db.query(LabwareInstanceOrm).filter(LabwareInstanceOrm.id == labware_instance_id).first()
                if not labware_instance:
                    db.rollback()
                    raise ValueError(f"LabwareInstanceOrm with id {labware_instance_id} for slot '{item_data.get('slot_name')}' not found.")
            
            expected_def_name = item_data.get("expected_labware_definition_name")
            if expected_def_name:
                labware_def = get_labware_definition(db, expected_def_name)
                if not labware_def:
                    db.rollback()
                    raise ValueError(f"LabwareDefinitionCatalogOrm with name '{expected_def_name}' for slot '{item_data.get('slot_name')}' not found.")
            
            slot_item = DeckConfigurationSlotItemOrm(
                deck_configuration_id=deck_layout_orm.id,
                slot_name=item_data["slot_name"],
                labware_instance_id=labware_instance_id,
                expected_labware_definition_name=expected_def_name
            )
            db.add(slot_item)
    
    try:
        db.commit()
        db.refresh(deck_layout_orm)
        # Re-fetch to ensure all relationships are correctly loaded after update
        return get_deck_layout_by_id(db, deck_layout_id)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Error updating deck layout '{deck_layout_id}': {e}")
    except Exception as e: # pragma: no cover
        db.rollback()
        raise e
    
def delete_deck_layout(db: DbSession, deck_layout_id: int) -> bool:
    """Deletes a deck layout configuration."""
    deck_layout_orm = db.query(DeckConfigurationOrm).filter(DeckConfigurationOrm.id == deck_layout_id).first()
    if not deck_layout_orm:
        return False # Not found
    
    try:
        # Associated slot_items are deleted due to cascade="all, delete-orphan"
        db.delete(deck_layout_orm)
        db.commit()
        return True
    except IntegrityError as e: # Should be rare due to cascade, but as a safeguard
        db.rollback()
        print(f"ERROR: ADS: IntegrityError deleting deck layout ID {deck_layout_id}: {e}")
        return False
    except Exception as e: # pragma: no cover
        db.rollback()
        raise e
