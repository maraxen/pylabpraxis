# <filename>praxis/backend/api/assets.py</filename>
from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, Depends, status
import datetime
import json  # For serializing metadata if needed for DB

from praxis.backend.api.dependencies import get_db  # MODIFIED: Use local dependencies
from sqlalchemy.ext.asyncio import AsyncSession  # MODIFIED: For type hinting

from praxis.backend.models import (
    AssetResponse,
    ResourceTypeInfo,
    MachineTypeInfo,
    ResourceCategoriesResponse,
    ResourceCreationRequest,
    MachineCreationRequest,
    LabwareInventoryDataIn,
    LabwareInventoryDataOut,
    LabwareDefinitionCreate,
    LabwareDefinitionUpdate,
    LabwareDefinitionResponse,
    DeckLayoutCreate,
    DeckLayoutUpdate,
    DeckLayoutResponse,
    LabwareInventoryReagentItem,
    LabwareInventoryItemCount,
)
from praxis.backend.services import asset_data_service
from praxis.backend.services.praxis_orm_service import PraxisDBService

from praxis.backend.utils.plr_inspection import (
    get_resource_metadata,
    get_machine_metadata,
    get_resource_categories,
    get_all_resource_types,
    get_all_machine_types,
)

router = APIRouter()


async def get_praxis_db_service() -> PraxisDBService:
    keycloak_dsn = None  # Or get from config if needed by initialize logic
    return await PraxisDBService.initialize(keycloak_dsn=keycloak_dsn)


@router.get("/types/{asset_type}", response_model=List[AssetResponse])
async def list_assets_by_type(
    asset_type: str, db_service: PraxisDBService = Depends(get_praxis_db_service)
):
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
        # Parameter format for asyncpg (used by PraxisDBService for direct SQL) is $1, $2, etc.
        # The fetch_all_sql in PraxisDBService handles this.
        assets_data = await db_service.fetch_all_sql(
            query, params={"1": f"%{asset_type}%"}
        )
        return [AssetResponse(**asset) for asset in assets_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch assets: {str(e)}")


@router.get("/available/{asset_type}", response_model=List[AssetResponse])
async def list_available_assets_by_type(
    asset_type: str, db_service: PraxisDBService = Depends(get_praxis_db_service)
):
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
        assets_data = await db_service.fetch_all_sql(
            query, params={"1": f"%{asset_type}%"}
        )
        return [AssetResponse(**asset) for asset in assets_data]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch available assets: {str(e)}"
        )


@router.get("/{asset_name}", response_model=AssetResponse)
async def get_asset_details(
    asset_name: str, db_service: PraxisDBService = Depends(get_praxis_db_service)
):
    """
    Get detailed information about a specific asset
    """
    query = """
        SELECT name, type, metadata, is_available, metadata->>'description' as description
        FROM assets
        WHERE name = $1
    """
    asset_data = await db_service.fetch_one_sql(query, params={"1": asset_name})
    if not asset_data:
        raise HTTPException(status_code=404, detail=f"Asset {asset_name} not found")
    return AssetResponse(**asset_data)


@router.get(
    "/search/{query_str}", response_model=List[AssetResponse]
)  # Renamed query to query_str to avoid conflict
async def search_assets(
    query_str: str, db_service: PraxisDBService = Depends(get_praxis_db_service)
):
    """
    Search for assets by name or metadata
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
            WHERE
                name ILIKE $1 OR
                type ILIKE $1 OR
                metadata::text ILIKE $1
            ORDER BY name
        """
        assets_data = await db_service.fetch_all_sql(
            query, params={"1": f"%{query_str}%"}
        )
        return [AssetResponse(**asset) for asset in assets_data]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to search assets: {str(e)}"
        )


# New endpoints for resource type metadata (No DB interaction, no change needed)
@router.get("/resources/types", response_model=Dict[str, ResourceTypeInfo])
async def get_resource_types():
    try:
        return get_resource_metadata()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get resource types: {str(e)}"
        )


@router.get("/machines/types", response_model=Dict[str, MachineTypeInfo])
async def get_machine_types():
    try:
        return get_machine_metadata()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get machine types: {str(e)}"
        )


@router.get("/resources/categories", response_model=ResourceCategoriesResponse)
async def get_categorized_resources():
    try:
        return ResourceCategoriesResponse(categories=get_resource_categories())
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get resource categories: {str(e)}"
        )


# New endpoints for creating resources and machines
@router.post("/resource", response_model=AssetResponse)
async def create_resource(
    request: ResourceCreationRequest,
    db_service: PraxisDBService = Depends(get_praxis_db_service),
):
    try:
        resource_types = get_all_resource_types()
        resource_class = resource_types.get(request.resourceType)
        if not resource_class:
            raise HTTPException(
                status_code=400, detail=f"Unknown resource type: {request.resourceType}"
            )

        valid_params = {}
        constructor_params_meta = (
            get_resource_metadata()
            .get(request.resourceType, {})
            .get("constructor_params", {})
        )
        for param_name, param_info in constructor_params_meta.items():
            if param_name in request.params:
                valid_params[param_name] = request.params[param_name]
            elif param_info.get(
                "required"
            ):  # Pydantic models might not have "required" field, check .get
                raise ValueError(f"Required parameter missing: {param_name}")

        resource = resource_class(**valid_params)  # PyLabRobot resource instance

        metadata_dict = {
            "description": request.description or f"{request.resourceType} resource",
            "params": request.params,
            # Add other relevant info from resource object if needed
        }

        plr_serialized_dict = resource.serialize()
        plr_serialized_dict["type"] = (
            request.resourceType
        )  # Ensure type is part of serialized data for consistency

        # INSERT into generic 'assets' table
        # Assuming 'assets' table columns: name, type, metadata (jsonb), plr_serialized_data (jsonb), is_available (boolean)
        # Adjust SQL and params based on actual table structure
        sql_insert = """
            INSERT INTO assets (name, type, metadata, plr_serialized_data, is_available)
            VALUES ($1, $2, $3, $4, true)
            RETURNING id;
        """  # RETURNING id is optional unless needed

        params_insert = {
            "1": request.name,
            "2": request.resourceType,
            "3": json.dumps(metadata_dict),
            "4": json.dumps(plr_serialized_dict),
        }
        await db_service.execute_sql(sql_insert, params_insert)

        return AssetResponse(
            name=request.name,
            type=request.resourceType,
            metadata=metadata_dict,
            is_available=True,  # Assuming new assets are available
            description=request.description,
        )
    except ValueError as e:  # Catch specific errors like missing params
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:  # Catch all other errors
        # Consider logging the full error e for debugging
        raise HTTPException(
            status_code=500, detail=f"Failed to create resource: {str(e)}"
        )


@router.post("/machine", response_model=AssetResponse)
async def create_machine(
    request: MachineCreationRequest,
    db_service: PraxisDBService = Depends(get_praxis_db_service),
):
    try:
        machine_types = get_all_machine_types()
        machine_class = machine_types.get(request.machineType)
        if not machine_class:
            raise HTTPException(
                status_code=400, detail=f"Unknown machine type: {request.machineType}"
            )

        valid_params = {}
        constructor_params_meta = (
            get_machine_metadata()
            .get(request.machineType, {})
            .get("constructor_params", {})
        )
        for param_name, param_info in constructor_params_meta.items():
            if param_name in request.params:
                valid_params[param_name] = request.params[param_name]
            elif param_info.get("required"):
                raise ValueError(f"Required parameter missing: {param_name}")

        if request.backend:
            valid_params["backend"] = request.backend

        machine = machine_class(**valid_params)  # PyLabRobot machine instance

        metadata_dict = {
            "description": request.description or f"{request.machineType} machine",
            "params": request.params,
            "backend": request.backend,
        }
        plr_serialized_dict = machine.serialize()
        plr_serialized_dict["type"] = (
            request.machineType
        )  # Ensure type is part of serialized data

        sql_insert = """
            INSERT INTO assets (name, type, metadata, plr_serialized_data, is_available)
            VALUES ($1, $2, $3, $4, true)
            RETURNING id;
        """
        params_insert = {
            "1": request.name,
            "2": request.machineType,
            "3": json.dumps(metadata_dict),
            "4": json.dumps(plr_serialized_dict),
        }
        await db_service.execute_sql(sql_insert, params_insert)

        return AssetResponse(
            name=request.name,
            type=request.machineType,
            metadata=metadata_dict,
            is_available=True,
            description=request.description,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create machine: {str(e)}"
        )


# --- Labware Instance Inventory Endpoints ---
# These already use asset_data_service and get_db, ensure get_db is from .dependencies
@router.get(
    "/labware_instances/{instance_id}/inventory",
    response_model=LabwareInventoryDataOut,
    tags=["Labware Instances"],
)
async def get_labware_instance_inventory(
    instance_id: int, db: AsyncSession = Depends(get_db)
) -> LabwareInventoryDataOut:
    instance = await asset_data_service.get_labware_instance_by_id(db, instance_id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Labware instance not found"
        )
    if not instance.properties_json:
        return LabwareInventoryDataOut()
    try:
        inventory_data = LabwareInventoryDataOut(**instance.properties_json)
        return inventory_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing inventory data: {e}",
        )


@router.put(
    "/labware_instances/{instance_id}/inventory",
    response_model=LabwareInventoryDataOut,
    tags=["Labware Instances"],
)
async def update_labware_instance_inventory(
    instance_id: int,
    inventory_data: LabwareInventoryDataIn,
    db: AsyncSession = Depends(get_db),
) -> LabwareInventoryDataOut:
    instance = await asset_data_service.get_labware_instance_by_id(db, instance_id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Labware instance not found"
        )

    if hasattr(inventory_data, "model_dump"):
        updated_properties = inventory_data.model_dump(exclude_unset=True)
    else:
        updated_properties = inventory_data.dict(exclude_unset=True)  # type: ignore

    updated_properties["last_updated_at"] = datetime.datetime.now(
        datetime.timezone.utc
    ).isoformat()

    updated_instance = (
        await asset_data_service.update_labware_instance_location_and_status(
            db,
            labware_instance_id=instance_id,
            properties_json_update=updated_properties,
        )
    )
    if not updated_instance or not updated_instance.properties_json:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update or retrieve labware instance properties",
        )
    try:
        return LabwareInventoryDataOut(**updated_instance.properties_json)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing updated inventory data: {e}",
        )


# --- Labware Definition Endpoints ---
# These already use asset_data_service and get_db
@router.post(
    "/labware_definitions",
    response_model=LabwareDefinitionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Labware Definitions"],
)
async def create_labware_definition_endpoint(
    definition: LabwareDefinitionCreate, db: AsyncSession = Depends(get_db)
):
    try:
        created_def = await asset_data_service.add_or_update_labware_definition(
            db=db, **definition.model_dump()
        )
        return created_def
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}",
        )


@router.get(
    "/labware_definitions/{pylabrobot_definition_name}",
    response_model=LabwareDefinitionResponse,
    tags=["Labware Definitions"],
)
async def get_labware_definition_endpoint(
    pylabrobot_definition_name: str, db: AsyncSession = Depends(get_db)
):
    db_def = await asset_data_service.get_labware_definition(
        db, pylabrobot_definition_name
    )
    if db_def is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Labware definition not found"
        )
    return db_def


@router.get(
    "/labware_definitions",
    response_model=List[LabwareDefinitionResponse],
    tags=["Labware Definitions"],
)
async def list_labware_definitions_endpoint(
    db: AsyncSession = Depends(get_db), limit: int = 100, offset: int = 0
):
    definitions = await asset_data_service.list_labware_definitions(
        db, limit=limit, offset=offset
    )
    return definitions


@router.put(
    "/labware_definitions/{pylabrobot_definition_name}",
    response_model=LabwareDefinitionResponse,
    tags=["Labware Definitions"],
)
async def update_labware_definition_endpoint(
    pylabrobot_definition_name: str,
    definition_update: LabwareDefinitionUpdate,
    db: AsyncSession = Depends(get_db),
):
    existing_def = await asset_data_service.get_labware_definition(
        db, pylabrobot_definition_name
    )
    if not existing_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Labware definition '{pylabrobot_definition_name}' not found.",
        )

    update_data = definition_update.model_dump(exclude_unset=True)
    if "python_fqn" not in update_data and existing_def.python_fqn:
        update_data["python_fqn"] = existing_def.python_fqn
    elif "python_fqn" not in update_data and not existing_def.python_fqn:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="python_fqn is required."
        )

    try:
        updated_def = await asset_data_service.add_or_update_labware_definition(
            db=db, pylabrobot_definition_name=pylabrobot_definition_name, **update_data
        )
        return updated_def
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/labware_definitions/{pylabrobot_definition_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Labware Definitions"],
)
async def delete_labware_definition_endpoint(
    pylabrobot_definition_name: str, db: AsyncSession = Depends(get_db)
):
    success = await asset_data_service.delete_labware_definition(
        db, pylabrobot_definition_name
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Labware definition '{pylabrobot_definition_name}' not found or could not be deleted.",
        )
    return None


# --- Deck Layout Endpoints ---
# These already use asset_data_service and get_db
@router.post(
    "/deck_layouts",
    response_model=DeckLayoutResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Deck Layouts"],
)
async def create_deck_layout_endpoint(
    deck_layout_in: DeckLayoutCreate, db: AsyncSession = Depends(get_db)
):
    try:
        slot_items_data = (
            [item.model_dump() for item in deck_layout_in.slot_items]
            if deck_layout_in.slot_items
            else []
        )
        created_layout = await asset_data_service.create_deck_layout(
            db=db,
            layout_name=deck_layout_in.layout_name,
            deck_device_id=deck_layout_in.deck_device_id,
            description=deck_layout_in.description,
            slot_items_data=slot_items_data,
        )
        return created_layout
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}",
        )


@router.get(
    "/deck_layouts", response_model=List[DeckLayoutResponse], tags=["Deck Layouts"]
)
async def list_deck_layouts_endpoint(
    deck_device_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    layouts = await asset_data_service.list_deck_layouts(
        db, deck_device_id=deck_device_id, limit=limit, offset=offset
    )
    return layouts


@router.get(
    "/deck_layouts/{deck_layout_id}",
    response_model=DeckLayoutResponse,
    tags=["Deck Layouts"],
)
async def get_deck_layout_by_id_endpoint(
    deck_layout_id: int, db: AsyncSession = Depends(get_db)
):
    layout = await asset_data_service.get_deck_layout_by_id(db, deck_layout_id)
    if not layout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck layout with ID {deck_layout_id} not found.",
        )
    return layout


@router.put(
    "/deck_layouts/{deck_layout_id}",
    response_model=DeckLayoutResponse,
    tags=["Deck Layouts"],
)
async def update_deck_layout_endpoint(
    deck_layout_id: int,
    deck_layout_update: DeckLayoutUpdate,
    db: AsyncSession = Depends(get_db),
):
    slot_items_data = None
    if deck_layout_update.slot_items is not None:
        slot_items_data = [item.model_dump() for item in deck_layout_update.slot_items]
    try:
        updated_layout = await asset_data_service.update_deck_layout(
            db=db,
            deck_layout_id=deck_layout_id,
            name=deck_layout_update.layout_name,
            description=deck_layout_update.description,
            deck_device_id=deck_layout_update.deck_device_id,
            slot_items_data=slot_items_data,
        )
        if not updated_layout:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deck layout with ID {deck_layout_id} not found.",
            )
        return updated_layout
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}",
        )


@router.delete(
    "/deck_layouts/{deck_layout_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Deck Layouts"],
)
async def delete_deck_layout_endpoint(
    deck_layout_id: int, db: AsyncSession = Depends(get_db)
):
    success = await asset_data_service.delete_deck_layout(db, deck_layout_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck layout with ID {deck_layout_id} not found or could not be deleted.",
        )
    return None
