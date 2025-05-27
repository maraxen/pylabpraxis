import json
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session # Added for DB session

# from ..utils.db import db # Not directly used, get_db is preferred for endpoints
# from ..core.workcell import Workcell, WorkcellView # Keep if used by other endpoints
# from ..protocol import WorkcellAssets # Keep if used by other endpoints
from ..core.orchestrator import Orchestrator
# from ..configure import PraxisConfiguration # Keep if used by other endpoints
from .dependencies import get_orchestrator, get_db # Added get_db

# New imports for /decks endpoint
from ..db_services import asset_data_service as ads
from ..database_models.asset_management_orm import ManagedDeviceOrm, PraxisDeviceCategoryEnum, ManagedDeviceStatusEnum
from .models.workcell_models import DeckInfo


router = APIRouter()

# config = PraxisConfiguration("praxis.ini") # Keep if used by other endpoints


# Asset request/response models (Keep existing models)
class WorkcellAssetRequest(BaseModel):
    """Request model for matching assets to requirements."""
    protocol_name: str
    required_assets: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)


class AssetMatchResponse(BaseModel):
    """Response model for matched assets."""
    asset_name: str
    asset_type: str
    compatibility_score: float
    metadata: Dict[str, Any]


class WorkcellStateResponse(BaseModel):
    """Response model for workcell state."""
    assets: Dict[str, Dict[str, Any]]
    running_protocols: List[str]
    available_resources: List[str]


@router.get("/state", response_model=WorkcellStateResponse, tags=["Workcell API - Legacy"]) # Added tag
async def get_workcell_state(orchestrator: Orchestrator = Depends(get_orchestrator)):
    """Get current workcell state including assets and protocols."""
    if not orchestrator._main_workcell: # type: ignore
        raise HTTPException(status_code=503, detail="Workcell not initialized")

    try:
        return WorkcellStateResponse(
            assets=orchestrator._main_workcell._asset_states, # type: ignore
            running_protocols=orchestrator.get_running_protocols(), # type: ignore
            available_resources=[
                asset
                for asset in orchestrator._main_workcell.asset_ids # type: ignore
                if not orchestrator._main_workcell.is_asset_in_use(asset) # type: ignore
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/match_assets", tags=["Workcell API - Legacy"]) # Added tag
async def match_assets_to_requirements(
    requirements: WorkcellAssetRequest,
    orchestrator: Orchestrator = Depends(get_orchestrator),
) -> Dict[str, List[AssetMatchResponse]]:
    """Match required assets to available assets in database."""
    try:
        matches = await orchestrator.match_assets_to_requirements(requirements.dict()) # type: ignore
        return {
            asset_name: [AssetMatchResponse(**match) for match in asset_matches]
            for asset_name, asset_matches in matches.items()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to match assets: {str(e)}")


@router.post("/validate_configuration", tags=["Workcell API - Legacy"]) # Added tag
async def validate_configuration(
    config: Dict[str, Any], orchestrator: Orchestrator = Depends(get_orchestrator)
) -> Dict[str, Any]:
    """Validate a complete protocol configuration."""
    try:
        result = await orchestrator.validate_configuration(config) # type: ignore
        if not result["valid"]:
            return {"valid": False, "errors": result["errors"], "config": config}
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Configuration validation failed: {str(e)}"
        )


@router.post("/release/{protocol_name}", tags=["Workcell API - Legacy"]) # Added tag
async def release_workcell_view(
    protocol_name: str, orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Release a protocol's workcell view."""
    try:
        await orchestrator.release_workcell_view(protocol_name) # type: ignore
        return {
            "status": "success",
            "message": f"Released workcell view for {protocol_name}",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to release workcell view: {str(e)}"
        )

# New endpoint implementation
@router.get("/decks", response_model=List[DeckInfo], tags=["Workcell API"])
async def list_available_decks(db: Session = Depends(get_db)):
    """
    Lists all available deck devices registered in the system.
    A deck device is a ManagedDeviceOrm with praxis_device_category set to DECK.
    """
    try:
        # Assuming asset_data_service.list_managed_devices can take a category filter
        # If not, we would fetch all and filter in Python, but a DB filter is preferred.
        # The example snippet implies such a filter exists.
        deck_devices_orm = ads.list_managed_devices(
            db_session=db,
            praxis_category_filter=PraxisDeviceCategoryEnum.DECK
        )
        
        available_decks = []
        for device_orm in deck_devices_orm:
            # Ensure all required fields for DeckInfo are present in device_orm
            # and handle potential None values if the Pydantic model doesn't allow them.
            # The DeckInfo model fields are: id, user_friendly_name, pylabrobot_class_name, current_status
            
            status_name = "UNKNOWN" # Default status if not set or not an enum
            if device_orm.current_status:
                if isinstance(device_orm.current_status, ManagedDeviceStatusEnum):
                    status_name = device_orm.current_status.name
                elif isinstance(device_orm.current_status, str): # If it's already a string
                    status_name = device_orm.current_status
                else: # Fallback for other types, though ideally it's always the enum
                    status_name = str(device_orm.current_status)


            deck_info = DeckInfo(
                id=device_orm.id,
                user_friendly_name=device_orm.user_friendly_name or f"Deck_{device_orm.id}", # Provide a default if None
                pylabrobot_class_name=device_orm.pylabrobot_class_name or "UnknownType", # Provide a default
                current_status=status_name
            )
            available_decks.append(deck_info)
        return available_decks
    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        # TODO: Add proper logging of the exception 'e' here
        print(f"Error in list_available_decks: {e}") # Basic print for now
        raise HTTPException(status_code=500, detail=f"Failed to list available decks: {str(e)}")

# TODO: Add other new workcell endpoints here following the pattern above:
# - GET /api/workcell/decks/{deck_orm_id}/state -> DeckStateResponse
# - WebSocket /ws/workcell/decks/{deck_orm_id}/subscribe -> Stream of DeckUpdateMessage
# - POST /api/workcell/decks/{deck_orm_id}/slots/{slot_name}/assign_labware
# - POST /api/workcell/decks/{deck_orm_id}/slots/{slot_name}/clear
# - POST /api/workcell/devices/{device_orm_id}/execute_action -> DeviceActionResponse
# - GET /api/workcell/devices -> List[DeviceInfo] (similar to DeckInfo but for all devices)
# - GET /api/workcell/labware_instances -> List[LabwareInstanceInfo] (more detailed than LabwareInfo)

# Ensure that the main FastAPI app includes this router.
# Example in main.py:
# from praxis.backend.api import workcell_api
# app.include_router(workcell_api.router, prefix="/api/workcell", tags=["Workcell Management"])
