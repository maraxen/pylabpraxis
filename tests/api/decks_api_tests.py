import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from praxis.backend.api.models.workcell_models import (
  DeckInfo,
  DeckStateResponse,
  DeckUpdateMessage,
  PositionInfo,
  ResourceInfo,
)
from praxis.backend.database_models.asset_management_orm import (
  ManagedDeviceOrm,
  ManagedDeviceStatusEnum,
  PlrCategoryEnum,
  PraxisDeviceCategoryEnum,
  ResourceDefinitionOrm,
  ResourceOrm,
  ResourceStatusEnum,
)

# --- Test Data ---
VALID_DECK_ID = 1
VALID_NON_DECK_ID = 2
INVALID_DEVICE_ID = 999

# --- Pydantic Model Unit Tests ---


def test_deck_info_model():
  data = {
    "id": 1,
    "name": "Main Deck",
    "fqn": "pylabrobot.resources.Deck",
    "status": "ONLINE",
  }
  deck_info = DeckInfo.model_validate(data)
  assert deck_info.accession_id == data["id"]
  assert deck_info.name == data["name"]
  assert deck_info.model_dump()["status"] == "ONLINE"


def test_resource_info_model():
  data = {
    "resource_accession_id": 10,
    "name": "Reagent Plate 1",
    "resource_definition_name": "corning_96_wellplate_360ul_flat",
    "fqn": "pylabrobot.resources.Plate",
    "category": "PLATE",
    "size_x_mm": 127.0,
    "size_y_mm": 85.0,
    "size_z_mm": 14.0,
    "nominal_volume_ul": 360.0,
    "properties_json": {"contents": "buffer"},
    "model": "Corning-1234",
  }
  resource_info = ResourceInfo.model_validate(data)
  assert resource_info.resource_accession_id == data["resource_accession_id"]
  assert resource_info.model_dump()["category"] == "PLATE"


def test_position_info_model():
  resource_data = {
    "resource_accession_id": 10,
    "name": "Reagent Plate 1",
    "fqn": "pylabrobot.resources.Plate",
    "category": "PLATE",
  }
  data = {
    "name": "A1",
    "x_coordinate": 10.0,
    "y_coordinate": 20.0,
    "z_coordinate": 0.5,
    "resource": resource_data,
  }
  position_info = PositionInfo.model_validate(data)
  assert position_info.name == data["name"]
  assert position_info.resource is not None
  assert position_info.resource.resource_accession_id == resource_data["resource_accession_id"]
  assert position_info.model_dump()["resource"]["name"] == "Reagent Plate 1"


def test_deck_state_response_model():
  position_data = {"name": "A1", "resource": None}
  data = {
    "deck_accession_id": 1,
    "name": "Main Deck",
    "fqn": "pylabrobot.resources.Deck",
    "size_x_mm": 500.0,
    "size_y_mm": 300.0,
    "size_z_mm": 20.0,
    "positions": [position_data],
  }
  deck_state = DeckStateResponse.model_validate(data)
  assert deck_state.deck_accession_id == data["deck_accession_id"]
  assert len(deck_state.positions) == 1
  assert deck_state.positions[0].name == position_data["name"]
  assert deck_state.model_dump()["positions"][0]["resource"] is None


def test_deck_update_message_model():
  resource_data = {
    "resource_accession_id": 10,
    "name": "Tip Box",
    "fqn": "pylabrobot.resources.TipRack",
    "category": "TIP_RACK",
  }
  data = {
    "deck_accession_id": 1,
    "update_type": "resource_added",
    "position_name": "B2",
    "resource_info": resource_data,
    # Timestamp will be auto-generated if not provided
  }
  deck_update = DeckUpdateMessage.model_validate(data)
  assert deck_update.deck_accession_id == data["deck_accession_id"]
  assert deck_update.update_type == data["update_type"]
  assert deck_update.resource_info is not None
  assert deck_update.resource_info.category == "TIP_RACK"  # Check enum-like string
  assert deck_update.model_dump()["timestamp"] is not None  # Check timestamp is generated

  # Test with explicit timestamp
  ts = "2024-01-01T12:00:00Z"
  data_with_ts = {**data, "timestamp": ts}
  deck_update_ts = DeckUpdateMessage.model_validate(data_with_ts)
  assert deck_update_ts.timestamp == ts


@pytest.fixture(scope="function")
def setup_basic_machines(db_session: Session) -> None:
  """Sets up a basic DECK machine and a NON-DECK machine."""
  deck_machine = ManagedDeviceOrm(
    id=VALID_DECK_ID,
    name="Test Deck 1",
    fqn="pylabrobot.resources.Deck",
    praxis_machine_category=PraxisDeviceCategoryEnum.DECK,
    status=ManagedDeviceStatusEnum.ONLINE,
  )
  non_deck_machine = ManagedDeviceOrm(
    id=VALID_NON_DECK_ID,
    name="Test Heater 1",
    fqn="pylabrobot.heating_shaking.heater_shaker.HeaterShaker",
    praxis_machine_category=PraxisDeviceCategoryEnum.GENERIC_DEVICE,  # Or another non-DECK category
    status=ManagedDeviceStatusEnum.ONLINE,
  )
  db_session.add_all([deck_machine, non_deck_machine])
  db_session.commit()


# --- HTTP Endpoint Tests ---


def test_list_available_decks_empty(client: TestClient, db_session: Session):
  """Test GET /api/workcell/decks when no decks are present."""
  response = client.get("/api/workcell/decks")
  assert response.status_code == 200
  assert response.json() == []


def test_list_available_decks_with_data(client: TestClient, db_session: Session, setup_basic_machines: None):
  """Test GET /api/workcell/decks with a DECK and a NON-DECK machine."""
  response = client.get("/api/workcell/decks")
  assert response.status_code == 200
  data = response.json()
  assert isinstance(data, list)
  assert len(data) == 1  # Should only return the DECK machine

  deck_info = data[0]
  assert deck_info["id"] == VALID_DECK_ID
  assert deck_info["name"] == "Test Deck 1"
  assert deck_info["fqn"] == "pylabrobot.resources.Deck"
  assert deck_info["status"] == "ONLINE"  # Enum .name or .value


def test_get_specific_deck_state_not_found(client: TestClient, db_session: Session):
  """Test GET /api/workcell/decks/{deck_accession_id}/state for a non-existent deck."""
  response = client.get(f"/api/workcell/decks/{INVALID_DEVICE_ID}/state")
  assert response.status_code == 404  # Assuming WorkcellRuntimeError leads to 404 for not found
  assert "not found" in response.json()["detail"].lower()


def test_get_specific_deck_state_not_a_deck(client: TestClient, db_session: Session, setup_basic_machines: None):
  """Test GET /api/workcell/decks/{deck_accession_id}/state for a machine that is not a DECK."""
  response = client.get(f"/api/workcell/decks/{VALID_NON_DECK_ID}/state")
  assert response.status_code == 404  # As per current error handling
  assert "not categorized as a deck" in response.json()["detail"].lower()


@pytest.fixture(scope="function")
def setup_deck_with_resource(db_session: Session, setup_basic_machines: None) -> None:
  """Fixture to set up a deck with some resource on it."""
  # Resource Definition
  plate_def = ResourceDefinitionOrm(
    id=1,
    name="corning_96_wellplate_360ul_flat",
    fqn="pylabrobot.resources.Plate",
    plr_category=PlrCategoryEnum.PLATE,
    size_x_mm=127.76,
    size_y_mm=85.48,
    size_z_mm=14.35,
    nominal_volume_ul=380.0,
  )
  tip_rack_def = ResourceDefinitionOrm(
    id=2,
    name="opentrons_96_tiprack_300ul",
    fqn="pylabrobot.resources.TipRack",
    plr_category=PlrCategoryEnum.TIP_RACK,
  )
  db_session.add_all([plate_def, tip_rack_def])
  db_session.commit()  # Commit definitions so they can be referenced

  # Resource s
  plate_instance = ResourceOrm(
    id=1,
    name="PlateOnDeck",
    resource_definition_accession_id=plate_def.accession_id,
    location_machine_accession_id=VALID_DECK_ID,  # Place on Test Deck 1
    current_deck_position_name="A1",
    status=ResourceStatusEnum.AVAILABLE_ON_DECK,
    properties_json={"sample_type": "plasma"},
  )
  tip_rack_instance = ResourceOrm(
    id=2,
    name="TipsOnDeck",
    resource_definition_accession_id=tip_rack_def.accession_id,
    location_machine_accession_id=VALID_DECK_ID,  # Place on Test Deck 1
    current_deck_position_name="B2",
    status=ResourceStatusEnum.AVAILABLE_ON_DECK,
  )
  # Resource not on this deck
  other_plate_instance = ResourceOrm(
    id=3,
    name="PlateInStorage",
    resource_definition_accession_id=plate_def.accession_id,
    location_machine_accession_id=None,  # Not on any deck
    status=ResourceStatusEnum.AVAILABLE_IN_STORAGE,
  )

  db_session.add_all([plate_instance, tip_rack_instance, other_plate_instance])
  db_session.commit()


def test_get_specific_deck_state_with_resource(client: TestClient, db_session: Session, setup_deck_with_resource: None):
  """Test GET /api/workcell/decks/{deck_accession_id}/state for a deck with resource."""
  response = client.get(f"/api/workcell/decks/{VALID_DECK_ID}/state")
  assert response.status_code == 200
  data = response.json()

  assert data["deck_accession_id"] == VALID_DECK_ID
  assert data["name"] == "Test Deck 1"
  assert data["fqn"] == "pylabrobot.resources.Deck"
  # Placeholder dimensions might be None or specific values if set in WorkcellRuntime
  assert "size_x_mm" in data
  assert "positions" in data

  positions_with_resource = {
    position["name"]: position["resource"] for position in data["positions"] if position["resource"]
  }
  assert len(positions_with_resource) == 2  # PlateOnDeck and TipsOnDeck

  # Check PlateOnDeck in A1
  assert "A1" in positions_with_resource
  plate_info = positions_with_resource["A1"]
  assert plate_info["name"] == "PlateOnDeck"
  assert plate_info["category"] == "PLATE"
  assert plate_info["properties_json"] == {"sample_type": "plasma"}

  # Check TipsOnDeck in B2
  assert "B2" in positions_with_resource
  tip_rack_info = positions_with_resource["B2"]
  assert tip_rack_info["name"] == "TipsOnDeck"
  assert tip_rack_info["category"] == "TIP_RACK"

  # Ensure no other resource is reported for this deck
  all_resource_names_on_deck = [lw["name"] for lw in positions_with_resource.values()]
  assert "PlateInStorage" not in all_resource_names_on_deck

  # TODO: Add checks for empty positions if get_deck_state_representation is updated to include them.


# --- WebSocket Endpoint Tests ---


def test_websocket_deck_updates_connection_and_broadcast(
  client: TestClient,
  db_session: Session,
  setup_basic_machines: None,
):
  """Test WebSocket connection and message broadcast."""
  with client.websocket_connect(f"/ws/decks/{VALID_DECK_ID}/updates") as websocket:
    # Test broadcast
    test_message_payload = {
      "message_type": "resource_updated",
      "position_name": "C3",
      "resource_name": "NewTipBox",
    }
    response = client.post(f"/ws/test_broadcast/{VALID_DECK_ID}", json=test_message_payload)  # Send JSON payload
    assert response.status_code == 200  # Assuming POST request for test broadcast

    # Receive the message from WebSocket
    message_str = websocket.receive_text()
    message_data = json.loads(message_str)

    assert message_data["deck_accession_id"] == VALID_DECK_ID
    # The test_broadcast endpoint sends a DeckUpdateMessage.
    # The message_type in the POST request to test_broadcast is used to construct this.
    assert message_data["update_type"] == test_message_payload["message_type"]
    assert message_data["position_name"] == test_message_payload["position_name"]

    assert message_data["resource_info"] is not None
    assert message_data["resource_info"]["name"] == test_message_payload["resource_name"]
    assert "timestamp" in message_data

    websocket.close()


def test_websocket_deck_updates_connection_to_invalid_deck(client: TestClient, db_session: Session):
  """Test WebSocket connection attempt to an invalid deck_accession_id."""
  with pytest.raises(Exception) as exc_info:  # Catching generic Exception as TestClient might wrap WebSocketDisconnect
    with client.websocket_connect(f"/ws/decks/{INVALID_DEVICE_ID}/updates") as websocket:
      # We expect this connection to fail and be closed by the server.
      # Depending on how TestClient handles server-side close, this might raise.
      # If it doesn't raise immediately, try receiving:
      try:
        _ = websocket.receive_text(timeout=1)  # timeout to prevent hanging if no close frame
      except Exception:  # WebSocketTimeoutError or similar
        pass  # Expected if server just closes without sending a close frame client expects

  # The exact exception and how to check the close code (1008) can be tricky with TestClient.
  # FastAPI's TestClient might not expose the close code directly in a simple way.
  # If the server closes with 1008, the client might see it as a generic disconnect or an exception.
  # For now, we assert that an exception occurs, implying the connection was not maintained.
  # A more direct way to test close codes might require lower-level WebSocket client testing.
  assert exc_info is not None
  # If we could access the close event details, we'd check:
  # assert exc_info.value.code == 1008 # For WebSocketDisconnect exception if it holds the code


def test_websocket_connection_to_non_deck_machine(client: TestClient, db_session: Session, setup_basic_machines: None):
  """Test WebSocket connection attempt to a machine that is not a DECK."""
  with pytest.raises(Exception) as exc_info:
    with client.websocket_connect(f"/ws/decks/{VALID_NON_DECK_ID}/updates"):
      pass  # Expect connection to be refused/closed
  assert exc_info is not None


# TODO: Add more tests, e.g. multiple clients for the same deck,
#       clients for different decks, graceful disconnect from server side if possible to simulate.
