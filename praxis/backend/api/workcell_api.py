# <filename>praxis/backend/api/workcell_api.py</filename>
from fastapi import (
  APIRouter,
  HTTPException,
  Depends,
  Path,
  WebSocket,
  WebSocketDisconnect,
)
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import (
  Session as SQLAlchemyClassicSession,
)  # For type hint if needed, but we use AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession  # For actual use
import datetime

# MODIFIED: Import get_db from local dependencies
from praxis.backend.api.dependencies import (
  get_orchestrator,
  get_db,
  get_workcell_runtime,
)
from praxis.backend.core.orchestrator import Orchestrator
from praxis.backend.core.workcell_runtime import WorkcellRuntime, WorkcellRuntimeError

from praxis.backend.services import asset_data_service as ads
from praxis.backend.models.asset_management_orm import (
  PraxisDeviceCategoryEnum,
  ManagedDeviceStatusEnum,
)
from praxis.backend.models import (
  DeckInfo,
  DeckStateResponse,
  DeckUpdateMessage,
  ResourceInfo,
)

router = APIRouter()


class ConnectionManager:
  def __init__(self):
    self.active_connections: Dict[int, List[WebSocket]] = {}

  async def connect(self, deck_id: int, websocket: WebSocket):
    await websocket.accept()
    if deck_id not in self.active_connections:
      self.active_connections[deck_id] = []
    self.active_connections[deck_id].append(websocket)
    print(
      f"INFO: WebSocket connected for deck_id {deck_id}. Total: {len(self.active_connections[deck_id])}"
    )

  def disconnect(self, deck_id: int, websocket: WebSocket):
    if deck_id in self.active_connections:
      self.active_connections[deck_id].remove(websocket)
      if not self.active_connections[deck_id]:
        del self.active_connections[deck_id]
      print(
        f"INFO: WebSocket disconnected for deck_id {deck_id}. Remaining: {len(self.active_connections.get(deck_id, []))}"
      )

  async def broadcast_to_deck(self, deck_id: int, message: DeckUpdateMessage):
    if deck_id in self.active_connections:
      disconnected_clients: List[WebSocket] = []
      message_json = message.model_dump_json()
      for connection in self.active_connections[deck_id]:
        try:
          await connection.send_text(message_json)
        except Exception:
          disconnected_clients.append(connection)
      for client in disconnected_clients:
        self.disconnect(deck_id, client)


manager = ConnectionManager()


class WorkcellAssetRequest(BaseModel):
  protocol_name: str
  required_assets: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
  parameters: Dict[str, Any] = Field(default_factory=dict)


class AssetMatchResponse(BaseModel):
  asset_name: str
  asset_type: str
  compatibility_score: float
  metadata: Dict[str, Any]


class WorkcellStateResponse(BaseModel):
  assets: Dict[str, Dict[str, Any]]
  running_protocols: List[str]
  available_resources: List[str]


@router.get(
  "/state", response_model=WorkcellStateResponse, tags=["Workcell API - Legacy"]
)
async def get_workcell_state(orchestrator: Orchestrator = Depends(get_orchestrator)):
  if (
    not orchestrator._main_workcell
  ):  # Accessing private member, consider public API if possible
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
  try:
    # .dict() is for Pydantic v1. For v2+, use .model_dump()
    matches = await orchestrator.match_assets_to_requirements(requirements.model_dump())
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
  try:
    result = await orchestrator.validate_configuration(config)
    if not result["valid"]:
      return {"valid": False, "errors": result["errors"], "config": config}
    return result
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Config validation failed: {str(e)}")


@router.post("/release/{protocol_name}", tags=["Workcell API - Legacy"])
async def release_workcell_view(
  protocol_name: str, orchestrator: Orchestrator = Depends(get_orchestrator)
):
  try:
    await orchestrator.release_workcell_view(protocol_name)
    return {"status": "success", "message": f"Released view for {protocol_name}"}
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to release view: {str(e)}")


@router.get("/decks", response_model=List[DeckInfo], tags=["Workcell API"])
async def list_available_decks(
  db: AsyncSession = Depends(get_db),
):  # MODIFIED: AsyncSession
  try:
    deck_machines_orm = await ads.list_managed_machines(  # MODIFIED: await
      db_session=db,  # db is already AsyncSession
      praxis_category_filter=PraxisDeviceCategoryEnum.DECK,  # Ensure enum value is passed if service expects it
    )
    available_decks = []
    for machine_orm in deck_machines_orm:
      status_name = "UNKNOWN"
      if machine_orm.current_status:  # current_status is already Enum
        status_name = machine_orm.current_status.name
      deck_info = DeckInfo(
        id=machine_orm.id,
        user_friendly_name=machine_orm.user_friendly_name or f"Deck_{machine_orm.id}",
        python_fqn=machine_orm.python_fqn or "UnknownType",
        current_status=status_name,
      )
      available_decks.append(deck_info)
    return available_decks
  except Exception as e:
    print(f"Error in list_available_decks: {e}")
    raise HTTPException(status_code=500, detail=f"Failed to list decks: {str(e)}")


@router.get(
  "/decks/{deck_id}/state", response_model=DeckStateResponse, tags=["Workcell API"]
)
async def get_specific_deck_state(
  deck_id: int = Path(..., title="The ID of the deck", ge=1),
  workcell_runtime: WorkcellRuntime = Depends(
    get_workcell_runtime
  ),  # workcell_runtime already injected
):
  try:
    # Assuming get_deck_state_representation is async or can be called from async
    # If it needs db session, WorkcellRuntime should get it via its own dependencies or initialization
    deck_state_data = workcell_runtime.get_deck_state_representation(
      deck_machine_orm_id=deck_id
    )
    return deck_state_data
  except WorkcellRuntimeError as wre:
    error_detail = str(wre)
    if (
      "not found" in error_detail.lower()
      or "not categorized as a deck" in error_detail.lower()
    ):
      raise HTTPException(status_code=404, detail=error_detail)
    else:
      raise HTTPException(
        status_code=500, detail=f"Workcell runtime error: {error_detail}"
      )
  except Exception as e:
    raise HTTPException(
      status_code=500, detail=f"Unexpected error fetching deck state: {str(e)}"
    )


@router.websocket("/ws/decks/{deck_id}/updates")
async def websocket_deck_updates(
  websocket: WebSocket,
  deck_id: int = Path(..., title="Deck ID for updates", ge=1),
  # db: AsyncSession = Depends(get_db) # Cannot use Depends directly in WebSocket path operation func signature
  # We need to manage session manually or pass it if manager methods need it.
):
  # For initial validation, we'd manually acquire a session if needed.
  # However, ads.get_managed_machine_by_id is async and needs an AsyncSession.
  # The simplest is to acquire one for the validation check.
  db_session_for_validation: Optional[AsyncSession] = None
  try:
    async with AsyncSessionLocal() as db_session_for_validation:  # Manually create session for validation
      deck_machine = await ads.get_managed_machine_by_id(
        db_session_for_validation, deck_id
      )
      if (
        not deck_machine
        or deck_machine.praxis_machine_category != PraxisDeviceCategoryEnum.DECK
      ):
        print(f"INFO: WebSocket attempt to invalid deck_id {deck_id}. Closing.")
        await websocket.close(code=1008)
        return
  except Exception as e:  # Catch DB connection errors or other issues during validation
    print(f"ERROR: WebSocket validation for deck_id {deck_id} failed: {e}")
    await websocket.close(code=1011)  # Internal Error
    return
  # finally: # Session is closed by 'async with'

  await manager.connect(deck_id, websocket)
  try:
    while True:
      data = await websocket.receive_text()
      print(f"INFO: WebSocket for deck_id {deck_id} received: {data}")
  except WebSocketDisconnect:
    print(f"INFO: WebSocket for deck_id {deck_id} disconnected by client.")
  except Exception as e:
    print(f"ERROR: Exception in WebSocket for deck_id {deck_id}: {e}")
  finally:
    manager.disconnect(deck_id, websocket)
    print(f"INFO: Cleaned up WebSocket for deck_id {deck_id}.")


@router.post("/ws/test_broadcast/{deck_id}", tags=["Workcell API - Test"])
async def test_broadcast_deck_update(
  deck_id: int = Path(..., title="Deck ID to broadcast to", ge=1),
  message_type: str = "resource_added",
  slot_name: Optional[str] = "A1",
  resource_name: Optional[str] = "TestPlate123",
):
  sample_resource_info = None
  if resource_name and slot_name:
    sample_resource_info = ResourceInfo(
      resource_instance_id=999,
      user_assigned_name=resource_name,
      name="test_plate_def",
      python_fqn="pylabrobot.resources.Plate",
      category="PLATE",
      size_x_mm=127.0,
      size_y_mm=85.0,
      size_z_mm=14.0,
      properties_json={"contents": "test_liquid"},
      model="TestModel123",
    )
  update_message = DeckUpdateMessage(
    deck_id=deck_id,
    update_type=message_type,
    slot_name=slot_name
    if message_type
    in ["resource_added", "resource_removed", "slot_cleared", "resource_updated"]
    else None,
    resource_info=sample_resource_info
    if message_type in ["resource_added", "resource_updated"]
    else None,
    timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
  )
  await manager.broadcast_to_deck(deck_id, update_message)
  return {
    "status": "success",
    "message": f"Test broadcast for deck {deck_id}, type '{message_type}'.",
  }
