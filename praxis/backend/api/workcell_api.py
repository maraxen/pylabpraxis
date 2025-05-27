import json
from fastapi import APIRouter, HTTPException, Depends, Path, WebSocket, WebSocketDisconnect # Added WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session 
import asyncio # Added asyncio
import datetime # Added datetime

# from ..utils.db import db 
from ..core.orchestrator import Orchestrator
# from ..configure import PraxisConfiguration 
from .dependencies import get_orchestrator, get_db, get_workcell_runtime 

# Imports for /decks and /decks/{deck_id}/state endpoints
from ..db_services import asset_data_service as ads # Corrected path based on previous tasks
from ..database_models.asset_management_orm import ManagedDeviceOrm, PraxisDeviceCategoryEnum, ManagedDeviceStatusEnum
from .models.workcell_models import DeckInfo, DeckStateResponse, DeckUpdateMessage, LabwareInfo # Added DeckUpdateMessage, LabwareInfo
from ..core.workcell_runtime import WorkcellRuntime, WorkcellRuntimeError 


router = APIRouter()

# config = PraxisConfiguration("praxis.ini") 

# --- Connection Manager for WebSockets ---
class ConnectionManager:
    def __init__(self):
        # Store connections per deck_id
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, deck_id: int, websocket: WebSocket):
        await websocket.accept()
        if deck_id not in self.active_connections:
            self.active_connections[deck_id] = []
        self.active_connections[deck_id].append(websocket)
        print(f"INFO: WebSocket connected for deck_id {deck_id}. Total clients for deck: {len(self.active_connections[deck_id])}")

    def disconnect(self, deck_id: int, websocket: WebSocket):
        if deck_id in self.active_connections:
            self.active_connections[deck_id].remove(websocket)
            if not self.active_connections[deck_id]: # Remove deck_id if no clients left
                del self.active_connections[deck_id]
            print(f"INFO: WebSocket disconnected for deck_id {deck_id}. Remaining clients for deck: {len(self.active_connections.get(deck_id, []))}")

    async def broadcast_to_deck(self, deck_id: int, message: DeckUpdateMessage):
        """
        Broadcasts a DeckUpdateMessage to all connected WebSocket clients for a specific deck.
        """
        # TODO: This method needs to be called by other services (e.g., WorkcellRuntime, AssetManager actions)
        # when actual deck state changes occur.
        # Example: When labware is assigned or cleared in WorkcellRuntime, it should prepare
        # a DeckUpdateMessage and call manager.broadcast_to_deck(deck_id, update_message).

        if deck_id in self.active_connections:
            disconnected_clients: List[WebSocket] = []
            message_json = message.model_dump_json() # Use .model_dump_json() for Pydantic v2+
            for connection in self.active_connections[deck_id]:
                try:
                    await connection.send_text(message_json)
                except Exception: # Catches various errors like broken pipe, etc.
                    # Schedule disconnection for clients that error out
                    disconnected_clients.append(connection)
            
            # Clean up disconnected clients
            for client in disconnected_clients:
                self.disconnect(deck_id, client)
            if disconnected_clients:
                print(f"INFO: Cleaned up {len(disconnected_clients)} stale connections for deck_id {deck_id} during broadcast.")


manager = ConnectionManager()
# --- End Connection Manager ---


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
        deck_state_data = workcell_runtime.get_deck_state_representation(deck_device_orm_id=deck_id)
        return deck_state_data
    except WorkcellRuntimeError as wre:
        error_detail = str(wre)
        if "not found" in error_detail.lower() or "not categorized as a deck" in error_detail.lower():
            raise HTTPException(status_code=404, detail=error_detail)
        else:
            print(f"WorkcellRuntimeError in get_specific_deck_state for deck ID {deck_id}: {wre}")
            raise HTTPException(status_code=500, detail=f"Workcell runtime error: {error_detail}")
    except Exception as e:
        print(f"Unexpected error in get_specific_deck_state for deck ID {deck_id}: {e}") 
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while fetching deck state for deck ID {deck_id}.")


@router.websocket("/ws/decks/{deck_id}/updates")
async def websocket_deck_updates(
    websocket: WebSocket,
    deck_id: int = Path(..., title="The ID of the deck device to subscribe to updates for", ge=1),
    db: Session = Depends(get_db) # Depends(get_db) will not work directly with WebSockets in this manner
                                   # We need to manage the session scope manually if DB access is needed within the WS.
                                   # For initial validation, we can use a regular dependency.
):
    """
    WebSocket endpoint for real-time updates on a specific deck's state.
    """
    # Validate deck_id first (using a regular function to get a session for this check)
    # This part needs careful handling of DB session for WebSocket.
    # A simple way is to get a session for validation only, then close it.
    # Or, if db access is needed throughout the WS lifecycle, manage it carefully.
    
    # For initial validation:
    temp_db_session_for_validation = next(get_db()) # Get a session instance
    try:
        deck_device = ads.get_managed_device_by_id(temp_db_session_for_validation, deck_id)
        if not deck_device or deck_device.praxis_device_category != PraxisDeviceCategoryEnum.DECK:
            print(f"INFO: WebSocket connection attempt to invalid deck_id {deck_id}. Closing.")
            await websocket.close(code=1008) # Policy Violation
            return
    finally:
        temp_db_session_for_validation.close() # Ensure session is closed after validation

    await manager.connect(deck_id, websocket)
    try:
        while True:
            # Keep the connection alive. In a typical use case, the server sends updates.
            # Clients might send pings or specific requests, which can be handled here.
            # For now, we just wait for messages from the client (if any) or disconnections.
            data = await websocket.receive_text()
            # Process received data if your protocol requires client-to-server messages on this WS.
            # For now, just log it.
            print(f"INFO: WebSocket for deck_id {deck_id} received text: {data}")
            # Example: if client sends a PING, server could send a PONG
            # if data.upper() == "PING":
            #     await websocket.send_text("PONG")
            
    except WebSocketDisconnect:
        print(f"INFO: WebSocket for deck_id {deck_id} disconnected by client.")
    except Exception as e: # Catch other exceptions during the receive loop
        print(f"ERROR: Exception in WebSocket for deck_id {deck_id}: {e}")
    finally:
        manager.disconnect(deck_id, websocket)
        print(f"INFO: Cleaned up WebSocket connection for deck_id {deck_id}.")


@router.post("/ws/test_broadcast/{deck_id}", tags=["Workcell API - Test"])
async def test_broadcast_deck_update(
    deck_id: int = Path(..., title="Deck ID to broadcast to", ge=1),
    message_type: str = "labware_added",
    slot_name: Optional[str] = "A1",
    labware_name: Optional[str] = "TestPlate123"
):
    """
    Test endpoint to manually trigger a broadcast of a DeckUpdateMessage
    to connected WebSocket clients for a specific deck_id.
    """
    # Create a sample LabwareInfo if the message type involves labware
    sample_labware_info = None
    if labware_name and slot_name: # Only create if relevant
        sample_labware_info = LabwareInfo(
            labware_instance_id=999, # Dummy ID
            user_assigned_name=labware_name,
            pylabrobot_definition_name="test_plate_def",
            python_fqn="pylabrobot.resources.Plate",
            category="PLATE", # Using string representation
            size_x_mm=127.0,
            size_y_mm=85.0,
            size_z_mm=14.0,
            properties_json={"contents": "test_liquid"},
            model="TestModel123"
        )

    update_message = DeckUpdateMessage(
        deck_id=deck_id,
        update_type=message_type,
        slot_name=slot_name if message_type in ["labware_added", "labware_removed", "slot_cleared", "labware_updated"] else None,
        labware_info=sample_labware_info if message_type in ["labware_added", "labware_updated"] else None,
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat() # Ensure Pydantic v2 compatibility for default_factory if used
    )
    
    await manager.broadcast_to_deck(deck_id, update_message)
    return {"status": "success", "message": f"Test broadcast initiated for deck {deck_id} with type '{message_type}'."}


# TODO: Add other new workcell endpoints here following the pattern above:
# - POST /api/workcell/decks/{deck_orm_id}/slots/{slot_name}/assign_labware
# - POST /api/workcell/decks/{deck_orm_id}/slots/{slot_name}/clear
# - POST /api/workcell/devices/{device_orm_id}/execute_action -> DeviceActionResponse
# - GET /api/workcell/devices -> List[DeviceInfo] (similar to DeckInfo but for all devices)
# - GET /api/workcell/labware_instances -> List[LabwareInstanceInfo] (more detailed than LabwareInfo)

# Ensure that the main FastAPI app includes this router.
# Example in main.py:
# from praxis.backend.api import workcell_api
# app.include_router(workcell_api.router, prefix="/api/workcell", tags=["Workcell Management"])
