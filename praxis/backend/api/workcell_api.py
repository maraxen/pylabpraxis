import json
from fastapi import APIRouter, HTTPException, Depends, Path # Added Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session 

# from ..utils.db import db 
from ..core.orchestrator import Orchestrator
# from ..configure import PraxisConfiguration 
from .dependencies import get_orchestrator, get_db, get_workcell_runtime # Added get_workcell_runtime

# Imports for /decks and /decks/{deck_id}/state endpoints
from ..db_services import asset_data_service as ads
from ..database_models.asset_management_orm import ManagedDeviceOrm, PraxisDeviceCategoryEnum, ManagedDeviceStatusEnum
from .models.workcell_models import DeckInfo, DeckStateResponse # Added DeckStateResponse
from ..core.workcell_runtime import WorkcellRuntime, WorkcellRuntimeError # Added WorkcellRuntime, WorkcellRuntimeError


router = APIRouter()

# config = PraxisConfiguration("praxis.ini") 


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


@router.get("/state", response_model=WorkcellStateResponse, tags=["Workcell API - Legacy"]) 
async def get_workcell_state(orchestrator: Orchestrator = Depends(get_orchestrator)):
    """Get current workcell state including assets and protocols."""
    if not orchestrator._main_workcell: 
        raise HTTPException(status_code=503, detail="Workcell not initialized")

    try:
        return WorkcellStateResponse(
            assets=orchestrator._main_workcell._asset_states, 
            running_protocols=orchestrator.get_running_protocols(), 
            available_resources=[
                asset
                for asset in orchestrator._main_workcell.asset_ids 
                if not orchestrator._main_workcell.is_asset_in_use(asset) 
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/match_assets", tags=["Workcell API - Legacy"]) 
async def match_assets_to_requirements(
    requirements: WorkcellAssetRequest,
    orchestrator: Orchestrator = Depends(get_orchestrator),
) -> Dict[str, List[AssetMatchResponse]]:
    """Match required assets to available assets in database."""
    try:
        matches = await orchestrator.match_assets_to_requirements(requirements.dict()) 
        return {
            asset_name: [AssetMatchResponse(**match) for match in asset_matches]
            for asset_name, asset_matches in matches.items()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to match assets: {str(e)}")


@router.post("/validate_configuration", tags=["Workcell API - Legacy"]) 
async def validate_configuration(
    config: Dict[str, Any], orchestrator: Orchestrator = Depends(get_orchestrator)
) -> Dict[str, Any]:
    """Validate a complete protocol configuration."""
    try:
        result = await orchestrator.validate_configuration(config) 
        if not result["valid"]:
            return {"valid": False, "errors": result["errors"], "config": config}
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Configuration validation failed: {str(e)}"
        )


@router.post("/release/{protocol_name}", tags=["Workcell API - Legacy"]) 
async def release_workcell_view(
    protocol_name: str, orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Release a protocol's workcell view."""
    try:
        await orchestrator.release_workcell_view(protocol_name) 
        return {
            "status": "success",
            "message": f"Released workcell view for {protocol_name}",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to release workcell view: {str(e)}"
        )


@router.get("/decks", response_model=List[DeckInfo], tags=["Workcell API"])
async def list_available_decks(db: Session = Depends(get_db)):
    """
    Lists all available deck devices registered in the system.
    A deck device is a ManagedDeviceOrm with praxis_device_category set to DECK.
    """
    try:
        deck_devices_orm = ads.list_managed_devices(
            db_session=db,
            praxis_category_filter=PraxisDeviceCategoryEnum.DECK
        )
        
        available_decks = []
        for device_orm in deck_devices_orm:
            status_name = "UNKNOWN" 
            if device_orm.current_status:
                if isinstance(device_orm.current_status, ManagedDeviceStatusEnum):
                    status_name = device_orm.current_status.name
                elif isinstance(device_orm.current_status, str): 
                    status_name = device_orm.current_status
                else: 
                    status_name = str(device_orm.current_status)

            deck_info = DeckInfo(
                id=device_orm.id,
                user_friendly_name=device_orm.user_friendly_name or f"Deck_{device_orm.id}", 
                pylabrobot_class_name=device_orm.pylabrobot_class_name or "UnknownType", 
                current_status=status_name
            )
            available_decks.append(deck_info)
        return available_decks
    except HTTPException: 
        raise
    except Exception as e:
        print(f"Error in list_available_decks: {e}") 
        raise HTTPException(status_code=500, detail=f"Failed to list available decks: {str(e)}")


@router.get("/decks/{deck_id}/state", response_model=DeckStateResponse, tags=["Workcell API"])
async def get_specific_deck_state(
    deck_id: int = Path(..., title="The ID of the deck device to get state for", ge=1),
    workcell_runtime: WorkcellRuntime = Depends(get_workcell_runtime)
):
    """
    Retrieves the current state of a specific deck, including its layout and any labware present.
    """
    try:
        # The get_deck_state_representation method in WorkcellRuntime is expected to
        # fetch all necessary data (deck details, slots, labware on slots) from the database
        # and return it in a dictionary structure that matches DeckStateResponse.
        deck_state_data = workcell_runtime.get_deck_state_representation(deck_device_orm_id=deck_id)
        
        # FastAPI will automatically validate deck_state_data against DeckStateResponse.
        # If deck_state_data is already a Pydantic model (e.g. DeckStateResponse instance),
        # FastAPI handles it directly. If it's a dict, it tries to parse it.
        return deck_state_data
    except WorkcellRuntimeError as wre:
        # Specific errors from WorkcellRuntime can be mapped to appropriate HTTP status codes.
        # For example, if WorkcellRuntimeError has a 'deck_not_found' or 'not_a_deck' type/attribute.
        # For now, using a generic approach: if the error message suggests "not found" or "not a DECK".
        error_detail = str(wre)
        if "not found" in error_detail.lower() or "not categorized as a deck" in error_detail.lower():
            raise HTTPException(status_code=404, detail=error_detail)
        else:
            # Other WorkcellRuntimeErrors might indicate a server-side issue with runtime logic
            print(f"WorkcellRuntimeError in get_specific_deck_state for deck ID {deck_id}: {wre}")
            raise HTTPException(status_code=500, detail=f"Workcell runtime error: {error_detail}")
    except Exception as e:
        # TODO: Add proper logging of the exception 'e' here
        print(f"Unexpected error in get_specific_deck_state for deck ID {deck_id}: {e}") # Basic print for now
        # Consider logging the full traceback for unexpected errors
        # import traceback
        # traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while fetching deck state for deck ID {deck_id}.")


# TODO: Add other new workcell endpoints here following the pattern above:
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
