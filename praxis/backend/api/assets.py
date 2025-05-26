from typing import List, Optional, Dict, Any
from typing import List, Optional, Dict, Any # Ensure Any is imported
from fastapi import APIRouter, HTTPException, Depends, status # Ensure status is imported
from pydantic import BaseModel, Field # Ensure Field is imported
import datetime # For setting last_updated_at

# Assuming get_db and DbSession will be correctly imported from dependencies
# This might need adjustment based on actual project structure for db sessions
from praxis.backend.database import get_db, DbSession # Placeholder, adjust if needed

from praxis.backend.services import asset_data_service # For interacting with DB layer

from praxis.utils.db import db as old_db_api # old_db_api, keeping for existing code
from praxis.utils.plr_inspection import (
    get_resource_metadata,
    get_machine_metadata,
    get_resource_categories,
    get_all_resource_types,
    get_all_machine_types,
)

router = APIRouter()

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

class LabwareInventoryDataOut(BaseModel):
    praxis_inventory_schema_version: Optional[str] = None
    reagents: Optional[List[LabwareInventoryReagentItem]] = None
    item_count: Optional[LabwareInventoryItemCount] = None
    consumable_state: Optional[str] = None
    last_updated_by: Optional[str] = None
    inventory_notes: Optional[str] = None
    last_updated_at: Optional[str] = None # Populated from DB


# --- Original Asset Models ---
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
        return LabwareInventoryDataOut(**updated_instance.properties_json)
    except Exception as e:
        # Log the error: print(f"Error parsing updated inventory data for instance {instance_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error parsing updated inventory data: {e}")
