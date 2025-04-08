from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from praxis.utils.db import db
from praxis.utils.plr_inspection import (
    get_resource_metadata,
    get_machine_metadata,
    get_resource_categories,
    get_all_resource_types,
    get_all_machine_types,
)

router = APIRouter()


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
        assets = await db.fetch_all(query, f"%{asset_type}%")
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
        assets = await db.fetch_all(query, f"%{asset_type}%")
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
    asset = await db.get_asset(asset_name)
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
        assets = await db.fetch_all(search_query, f"%{query}%")
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
            asset_id = await db.add_asset(
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
            asset_id = await db.add_asset(
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
