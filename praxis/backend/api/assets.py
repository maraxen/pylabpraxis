from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status # Ensure status is imported
from pydantic import BaseModel # Ensure Field is imported
import datetime # For setting last_updated_at

# Assuming get_db and DbSession will be correctly imported from dependencies
# This might need adjustment based on actual project structure for db sessions
from praxis.backend.database import get_db, DbSession # Placeholder, adjust if needed

from praxis.backend.services import asset_data_service # For interacting with DB layer

from praxis.backend.utils.plr_inspection import (
    get_resource_metadata,
    get_machine_metadata,
    get_resource_categories,
    get_all_resource_types,
    get_all_machine_types,
)

router = APIRouter()

# --- Pydantic Models for Labware Definitions ---
class LabwareDefinitionBase(BaseModel):
    pylabrobot_definition_name: str
    python_fqn: str
    praxis_labware_type_name: Optional[str] = None
    description: Optional[str] = None
    is_consumable: bool = True
    nominal_volume_ul: Optional[float] = None
    material: Optional[str] = None
    manufacturer: Optional[str] = None
    plr_definition_details_json: Optional[Dict[str, Any]] = None
    size_x_mm: Optional[float] = None
    size_y_mm: Optional[float] = None
    size_z_mm: Optional[float] = None
    model: Optional[str] = None
    # rotation_json: Optional[Dict[str, Any]] = None # Example if needed

    class Config:
        orm_mode = True
        use_enum_values = True # Ensure enums are serialized to values

class LabwareDefinitionCreate(LabwareDefinitionBase):
    # All fields are required or have defaults in LabwareDefinitionBase
    pass

class LabwareDefinitionUpdate(BaseModel): # All fields optional for update
    python_fqn: Optional[str] = None
    praxis_labware_type_name: Optional[str] = None
    description: Optional[str] = None
    is_consumable: Optional[bool] = None
    nominal_volume_ul: Optional[float] = None
    material: Optional[str] = None
    manufacturer: Optional[str] = None
    plr_definition_details_json: Optional[Dict[str, Any]] = None
    size_x_mm: Optional[float] = None
    size_y_mm: Optional[float] = None
    size_z_mm: Optional[float] = None
    model: Optional[str] = None

class LabwareDefinitionResponse(LabwareDefinitionBase):
    # Includes all fields from LabwareDefinitionBase due to inheritance
    # and orm_mode = True will map from the ORM object.
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None


# --- Pydantic Models for Deck Layouts ---
class DeckSlotItemBase(BaseModel):
    slot_name: str
    labware_instance_id: Optional[int] = None # Optional: a slot can be empty
    expected_labware_definition_name: Optional[str] = None

    class Config:
        orm_mode = True

class DeckSlotItemCreate(DeckSlotItemBase):
    pass

class DeckSlotItemResponse(DeckSlotItemBase):
    id: int
    deck_configuration_id: int
    # Potential to nest LabwareInstanceResponse here if needed later


class DeckLayoutBase(BaseModel):
    layout_name: str
    deck_device_id: int
    description: Optional[str] = None

    class Config:
        orm_mode = True

class DeckLayoutCreate(DeckLayoutBase):
    slot_items: Optional[List[DeckSlotItemCreate]] = []

class DeckLayoutUpdate(BaseModel): # All fields optional for update
    layout_name: Optional[str] = None
    deck_device_id: Optional[int] = None
    description: Optional[str] = None
    slot_items: Optional[List[DeckSlotItemCreate]] = None # To replace all items

class DeckLayoutResponse(DeckLayoutBase):
    id: int
    slot_items: List[DeckSlotItemResponse] = []
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None


# --- Inventory Pydantic Models ---
class LabwareInventoryReagentItem(BaseModel):
    reagent_id: str
    reagent_name: Optional[str] = None
    lot_number: Optional[str] = None
    expiry_date: Optional[str] = None # Use str for date for API, validation can be added
    supplier: Optional[str] = None
    catalog_number: Optional[str] = None
    date_received: Optional[str] = None
    date_opened: Optional[str] = None
    concentration: Optional[Dict[str, Any]] = None # e.g., {"value": 10.0, "unit": "mM"}
    initial_quantity: Dict[str, Any] # e.g., {"value": 50.0, "unit": "mL"}
    current_quantity: Dict[str, Any] # e.g., {"value": 45.5, "unit": "mL"}
    quantity_unit_is_volume: Optional[bool] = True
    custom_fields: Optional[Dict[str, Any]] = None

class LabwareInventoryItemCount(BaseModel):
    item_type: Optional[str] = None # "tip", "tube", "well_used"
    initial_max_items: Optional[int] = None
    current_available_items: Optional[int] = None
    positions_used: Optional[List[str]] = None

class LabwareInventoryDataIn(BaseModel):
    praxis_inventory_schema_version: Optional[str] = "1.0"
    reagents: Optional[List[LabwareInventoryReagentItem]] = None
    item_count: Optional[LabwareInventoryItemCount] = None
    consumable_state: Optional[str] = None # e.g., "new", "used", "partially_used", "empty", "contaminated"
    last_updated_by: Optional[str] = None # User ID or name
    inventory_notes: Optional[str] = None
    # last_updated_at is set by server on PUT

class LabwareInventoryDataOut(LabwareInventoryDataIn): # Inherits for response, last_updated_at added
    last_updated_at: Optional[str] = None # Populated from DB. Overrides if present in LabwareInventoryDataIn


# --- Original Asset Models (Kept for existing endpoints) ---
class AssetBase(BaseModel):
    name: str
    type: str
    metadata: dict = {}


class AssetResponse(AssetBase):
    is_available: bool
    description: Optional[str] = None


class ResourceTypeInfo(BaseModel):
    name: str
    parent_class: str
    can_create_directly: bool
    constructor_params: Dict[str, Dict]
    doc: str
    module: str


class MachineTypeInfo(BaseModel):
    name: str
    parent_class: str
    constructor_params: Dict[str, Dict]
    backends: List[str]
    doc: str
    module: str


class ResourceCategoriesResponse(BaseModel):
    categories: Dict[str, List[str]]


class ResourceCreationRequest(BaseModel):
    name: str
    resourceType: str
    description: Optional[str] = None
    params: Dict[str, Any] = {}


class MachineCreationRequest(BaseModel):
    name: str
    machineType: str
    backend: Optional[str] = None
    description: Optional[str] = None
    params: Dict[str, Any] = {}


@router.get("/types/{asset_type}", response_model=List[AssetResponse])
async def list_assets_by_type(asset_type: str):
    """
    Get all assets of a specific type.
    Examples of asset_type: 'labware', 'machine', 'resource'
    """
    try:
        query = """
            SELECT
                name,
                type,
                metadata,
                is_available,
                metadata->>'description' as description
            FROM assets
            WHERE type LIKE $1
            ORDER BY name
        """
        assets = await old_db_api.fetch_all(query, f"%{asset_type}%") # Using old_db_api
        return assets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch assets: {str(e)}")


@router.get("/available/{asset_type}", response_model=List[AssetResponse])
async def list_available_assets_by_type(asset_type: str):
    """
    Get all available (unlocked) assets of a specific type
    """
    try:
        query = """
            SELECT
                name,
                type,
                metadata,
                is_available,
                metadata->>'description' as description
            FROM assets
            WHERE type LIKE $1
                AND is_available = true
                AND (lock_expires_at IS NULL OR lock_expires_at < CURRENT_TIMESTAMP)
            ORDER BY name
        """
        assets = await old_db_api.fetch_all(query, f"%{asset_type}%") # Using old_db_api
        return assets
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch available assets: {str(e)}"
        )


@router.get("/{asset_name}", response_model=AssetResponse)
async def get_asset_details(asset_name: str):
    """
    Get detailed information about a specific asset
    """
    asset = await old_db_api.get_asset(asset_name) # Using old_db_api
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_name} not found")
    return asset


@router.get("/search/{query}", response_model=List[AssetResponse])
async def search_assets(query: str):
    """
    Search for assets by name or metadata
    """
    try:
        search_query = """
            SELECT
                name,
                type,
                metadata,
                is_available,
                metadata->>'description' as description
            FROM assets
            WHERE
                name ILIKE $1 OR
                type ILIKE $1 OR
                metadata::text ILIKE $1
            ORDER BY name
        """
        assets = await old_db_api.fetch_all(search_query, f"%{query}%") # Using old_db_api
        return assets
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to search assets: {str(e)}"
        )


# New endpoints for resource type metadata


@router.get("/resources/types", response_model=Dict[str, ResourceTypeInfo])
async def get_resource_types():
    """
    Get metadata about all available PyLabRobot resource types
    """
    try:
        return get_resource_metadata()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get resource types: {str(e)}"
        )


@router.get("/machines/types", response_model=Dict[str, MachineTypeInfo])
async def get_machine_types():
    """
    Get metadata about all available PyLabRobot machine types
    """
    try:
        return get_machine_metadata()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get machine types: {str(e)}"
        )


@router.get("/resources/categories", response_model=ResourceCategoriesResponse)
async def get_categorized_resources():
    """
    Get resource types organized into categories
    """
    try:
        return ResourceCategoriesResponse(categories=get_resource_categories())
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get resource categories: {str(e)}"
        )


# New endpoints for creating resources and machines


@router.post("/resource", response_model=AssetResponse)
async def create_resource(request: ResourceCreationRequest):
    """
    Create a new PyLabRobot resource
    """
    try:
        # Get resource class from type
        resource_types = get_all_resource_types()
        resource_class = resource_types.get(request.resourceType)

        if not resource_class:
            raise HTTPException(
                status_code=400, detail=f"Unknown resource type: {request.resourceType}"
            )

        # Create the resource instance
        try:
            # Extract only the parameters expected by the constructor
            valid_params = {}
            constructor_params = get_resource_metadata()[request.resourceType][
                "constructor_params"
            ]
            for param_name, param_info in constructor_params.items():
                if param_name in request.params:
                    valid_params[param_name] = request.params[param_name]
                elif param_info["required"]:
                    raise ValueError(f"Required parameter missing: {param_name}")

            # Create resource instance, passing validated parameters
            resource = resource_class(**valid_params)

            # Add metadata including description
            metadata = {
                "description": request.description
                or f"{request.resourceType} resource",
                "params": request.params,
            }

            # Serialize and save to database
            plr_serialized = resource.serialize()
            plr_serialized["type"] = request.resourceType

            # Add to database
            asset_id = await old_db_api.add_asset( # Using old_db_api
                name=request.name,
                asset_type=request.resourceType,
                metadata=metadata,
                plr_serialized=plr_serialized,
            )

            # Return the created asset
            return {
                "name": request.name,
                "type": request.resourceType,
                "metadata": metadata,
                "is_available": True,
                "description": request.description,
            }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to create resource: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create resource: {str(e)}"
        )


@router.post("/machine", response_model=AssetResponse)
async def create_machine(request: MachineCreationRequest):
    """
    Create a new PyLabRobot machine
    """
    try:
        # Get machine class from type
        machine_types = get_all_machine_types()
        machine_class = machine_types.get(request.machineType)

        if not machine_class:
            raise HTTPException(
                status_code=400, detail=f"Unknown machine type: {request.machineType}"
            )

        # Create the machine instance
        try:
            # Extract only the parameters expected by the constructor
            valid_params = {}
            constructor_params = get_machine_metadata()[request.machineType][
                "constructor_params"
            ]
            for param_name, param_info in constructor_params.items():
                if param_name in request.params:
                    valid_params[param_name] = request.params[param_name]
                elif param_info["required"]:
                    raise ValueError(f"Required parameter missing: {param_name}")

            # Add backend selection if provided
            if request.backend:
                valid_params["backend"] = request.backend

            # Create machine instance, passing validated parameters
            machine = machine_class(**valid_params)

            # Add metadata including description
            metadata = {
                "description": request.description or f"{request.machineType} machine",
                "params": request.params,
                "backend": request.backend,
            }

            # Serialize and save to database
            plr_serialized = machine.serialize()
            plr_serialized["type"] = request.machineType

            # Add to database
            asset_id = await old_db_api.add_asset( # Using old_db_api
                name=request.name,
                asset_type=request.machineType,
                metadata=metadata,
                plr_serialized=plr_serialized,
            )

            # Return the created asset
            return {
                "name": request.name,
                "type": request.machineType,
                "metadata": metadata,
                "is_available": True,
                "description": request.description,
            }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to create machine: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create machine: {str(e)}"
        )

# --- Labware Instance Inventory Endpoints ---

@router.get("/labware_instances/{instance_id}/inventory", response_model=LabwareInventoryDataOut, tags=["Labware Instances"])
async def get_labware_instance_inventory(instance_id: int, db: DbSession = Depends(get_db)) -> LabwareInventoryDataOut:
    """
    Get inventory data for a specific labware instance.
    """
    instance = asset_data_service.get_labware_instance_by_id(db, instance_id)
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Labware instance not found")

    if not instance.properties_json:
        return LabwareInventoryDataOut() # Return empty if no properties_json

    try:
        # Assuming properties_json directly stores LabwareInventoryData structure
        # The model will validate if the structure is correct.
        inventory_data = LabwareInventoryDataOut(**instance.properties_json)
        return inventory_data
    except Exception as e: # Catches Pydantic validation errors among others
        # Log the error for debugging: print(f"Error parsing inventory data for instance {instance_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error parsing inventory data from instance properties: {e}")


@router.put("/labware_instances/{instance_id}/inventory", response_model=LabwareInventoryDataOut, tags=["Labware Instances"])
async def update_labware_instance_inventory(instance_id: int, inventory_data: LabwareInventoryDataIn, db: DbSession = Depends(get_db)) -> LabwareInventoryDataOut:
    """
    Update inventory data for a specific labware instance.
    """
    instance = asset_data_service.get_labware_instance_by_id(db, instance_id)
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Labware instance not found")

    # Pydantic v2 uses model_dump, v1 uses .dict()
    if hasattr(inventory_data, 'model_dump'):
        updated_properties = inventory_data.model_dump(exclude_unset=True)
    else:
        updated_properties = inventory_data.dict(exclude_unset=True) # type: ignore

    updated_properties["last_updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    updated_instance = asset_data_service.update_labware_instance_location_and_status(
        db,
        labware_instance_id=instance_id,
        properties_json_update=updated_properties
        # new_status is not changed here, only properties_json
    )

    if not updated_instance or not updated_instance.properties_json:
        # This case should ideally not happen if the update service worked and instance was found
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update or retrieve labware instance properties")

    try:
        # Ensure that the response model correctly handles the structure from properties_json
        return LabwareInventoryDataOut(**updated_instance.properties_json)
    except Exception as e: # Catch Pydantic validation errors or others
        # Log the error: print(f"Error parsing updated inventory data for instance {instance_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error parsing updated inventory data: {e}")


# --- Labware Definition Endpoints ---
@router.post("/labware_definitions", response_model=LabwareDefinitionResponse, status_code=status.HTTP_201_CREATED, tags=["Labware Definitions"])
async def create_labware_definition_endpoint(definition: LabwareDefinitionCreate, db: DbSession = Depends(get_db)):
    """
    Creates a new labware definition in the catalog.
    The `pylabrobot_definition_name` must be unique.
    """
    try:
        # The model_dump method will correctly handle enum values if use_enum_values = True in Pydantic model Config
        created_def = asset_data_service.add_or_update_labware_definition(db=db, **definition.model_dump())
        return created_def
    except ValueError as e: # Catch errors like definition already exists or validation errors from service
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e: # pragma: no cover
        # Log the exception e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")

@router.get("/labware_definitions/{pylabrobot_definition_name}", response_model=LabwareDefinitionResponse, tags=["Labware Definitions"])
async def get_labware_definition_endpoint(pylabrobot_definition_name: str, db: DbSession = Depends(get_db)):
    """
    Retrieves a specific labware definition by its PyLabRobot definition name.
    """
    db_def = asset_data_service.get_labware_definition(db, pylabrobot_definition_name)
    if db_def is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Labware definition not found")
    return db_def

@router.get("/labware_definitions", response_model=List[LabwareDefinitionResponse], tags=["Labware Definitions"])
async def list_labware_definitions_endpoint(
    db: DbSession = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
    # TODO: Add other filter parameters like category, manufacturer etc.
    # category: Optional[LabwareCategoryEnum] = Query(None, description="Filter by labware category"),
    # manufacturer: Optional[str] = Query(None, description="Filter by manufacturer name (case-insensitive search)")
):
    """
    Lists all labware definitions in the catalog, with optional pagination.
    """
    # TODO: Pass filter parameters to service layer when implemented there
    # definitions = asset_data_service.list_labware_definitions(db, limit=limit, offset=offset, category=category, manufacturer=manufacturer)
    definitions = asset_data_service.list_labware_definitions(db, limit=limit, offset=offset)
    return definitions

@router.put("/labware_definitions/{pylabrobot_definition_name}", response_model=LabwareDefinitionResponse, tags=["Labware Definitions"])
async def update_labware_definition_endpoint(
    pylabrobot_definition_name: str,
    definition_update: LabwareDefinitionUpdate,
    db: DbSession = Depends(get_db)
):
    """
    Updates an existing labware definition.
    If `pylabrobot_definition_name` does not exist, it will not create one.
    Use POST /labware_definitions to create.
    """
    existing_def = asset_data_service.get_labware_definition(db, pylabrobot_definition_name)
    if not existing_def:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Labware definition '{pylabrobot_definition_name}' not found.")

    update_data = definition_update.model_dump(exclude_unset=True)

    # add_or_update_labware_definition expects all non-optional args from LabwareDefinitionBase if creating.
    # For update, we pass only what's in update_data.
    # The service function needs to handle partial updates gracefully.
    # We must ensure pylabrobot_definition_name and python_fqn (if not changing PK) are passed.
    # For this PUT, pylabrobot_definition_name is fixed. python_fqn is required if not in update_data.

    # The service function add_or_update_labware_definition is designed for upsert.
    # For a strict update, we might need a different service function or adapt this one.
    # Current service function requires python_fqn if creating.
    # If python_fqn is not in update_data, use existing one.
    if 'python_fqn' not in update_data and existing_def.python_fqn:
         update_data['python_fqn'] = existing_def.python_fqn
    elif 'python_fqn' not in update_data and not existing_def.python_fqn: # Should not happen if DB is consistent
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="python_fqn is required and was not found on existing definition.")


    try:
        updated_def = asset_data_service.add_or_update_labware_definition(
            db=db,
            pylabrobot_definition_name=pylabrobot_definition_name, # PK
            **update_data # Pass other fields from the update model
        )
        return updated_def
    except ValueError as e: # Catch potential errors from service layer
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/labware_definitions/{pylabrobot_definition_name}", status_code=status.HTTP_204_NO_CONTENT, tags=["Labware Definitions"])
async def delete_labware_definition_endpoint(
    pylabrobot_definition_name: str,
    db: DbSession = Depends(get_db)
):
    """Deletes a labware definition."""
    success = asset_data_service.delete_labware_definition(db, pylabrobot_definition_name)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Labware definition '{pylabrobot_definition_name}' not found or could not be deleted.")
    return None # FastAPI handles 204 No Content response

# --- Deck Layout Endpoints ---
@router.post("/deck_layouts", response_model=DeckLayoutResponse, status_code=status.HTTP_201_CREATED, tags=["Deck Layouts"])
async def create_deck_layout_endpoint(
    deck_layout_in: DeckLayoutCreate,
    db: DbSession = Depends(get_db)
):
    """Creates a new deck layout configuration."""
    try:
        slot_items_data = [item.model_dump() for item in deck_layout_in.slot_items] if deck_layout_in.slot_items else []
        created_layout = asset_data_service.create_deck_layout(
            db=db,
            layout_name=deck_layout_in.layout_name,
            deck_device_id=deck_layout_in.deck_device_id,
            description=deck_layout_in.description,
            slot_items_data=slot_items_data
        )
        return created_layout
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")


@router.get("/deck_layouts", response_model=List[DeckLayoutResponse], tags=["Deck Layouts"])
async def list_deck_layouts_endpoint(
    deck_device_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    db: DbSession = Depends(get_db)
):
    """Lists deck layout configurations."""
    layouts = asset_data_service.list_deck_layouts(db, deck_device_id=deck_device_id, limit=limit, offset=offset)
    return layouts


@router.get("/deck_layouts/{deck_layout_id}", response_model=DeckLayoutResponse, tags=["Deck Layouts"])
async def get_deck_layout_by_id_endpoint(
    deck_layout_id: int,
    db: DbSession = Depends(get_db)
):
    """Gets a specific deck layout configuration by its ID."""
    layout = asset_data_service.get_deck_layout_by_id(db, deck_layout_id)
    if not layout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Deck layout with ID {deck_layout_id} not found.")
    return layout


@router.put("/deck_layouts/{deck_layout_id}", response_model=DeckLayoutResponse, tags=["Deck Layouts"])
async def update_deck_layout_endpoint(
    deck_layout_id: int,
    deck_layout_update: DeckLayoutUpdate,
    db: DbSession = Depends(get_db)
):
    """Updates an existing deck layout configuration."""
    slot_items_data = None
    if deck_layout_update.slot_items is not None: # Distinguish between not provided (None) and empty list
        slot_items_data = [item.model_dump() for item in deck_layout_update.slot_items]

    try:
        updated_layout = asset_data_service.update_deck_layout(
            db=db,
            deck_layout_id=deck_layout_id,
            name=deck_layout_update.layout_name,
            description=deck_layout_update.description,
            deck_device_id=deck_layout_update.deck_device_id,
            slot_items_data=slot_items_data
        )
        if not updated_layout:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Deck layout with ID {deck_layout_id} not found for update.")
        return updated_layout
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")


@router.delete("/deck_layouts/{deck_layout_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Deck Layouts"])
async def delete_deck_layout_endpoint(
    deck_layout_id: int,
    db: DbSession = Depends(get_db)
):
    """Deletes a deck layout configuration."""
    success = asset_data_service.delete_deck_layout(db, deck_layout_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Deck layout with ID {deck_layout_id} not found or could not be deleted.")
    return None
