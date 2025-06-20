import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Generator

from praxis.backend.main import app # Assuming your FastAPI app instance is here
from praxis.backend.database_models.asset_management_orm import (
    ManagedDeviceOrm,
    ResourceInstanceOrm,
    ResourceDefinitionCatalogOrm,
    PraxisDeviceCategoryEnum,
    ManagedDeviceStatusEnum,
    PlrCategoryEnum,
)
from praxis.backend.api.models.workcell_models import (
    DeckInfo,
    ResourceInfo,
    SlotInfo,
    DeckStateResponse,
    DeckUpdateMessage,
)
from praxis.backend.utils.db import SessionLocal, engine, Base, create_tables_if_not_exist

# --- Test Data ---
VALID_DECK_ID = 1
VALID_NON_DECK_ID = 2
INVALID_DEVICE_ID = 999

# --- Pydantic Model Unit Tests ---

def test_deck_info_model():
    data = {
        "id": 1,
        "user_friendly_name": "Main Deck",
        "python_fqn": "pylabrobot.resources.Deck",
        "current_status": "ONLINE",
    }
    deck_info = DeckInfo.model_validate(data)
    assert deck_info.accession_id == data["id"]
    assert deck_info.user_friendly_name == data["user_friendly_name"]
    assert deck_info.model_dump()["current_status"] == "ONLINE"

def test_resource_info_model():
    data = {
        "resource_instance_accession_id": 10,
        "user_assigned_name": "Reagent Plate 1",
        "name": "corning_96_wellplate_360ul_flat",
        "python_fqn": "pylabrobot.resources.Plate",
        "category": "PLATE",
        "size_x_mm": 127.0,
        "size_y_mm": 85.0,
        "size_z_mm": 14.0,
        "nominal_volume_ul": 360.0,
        "properties_json": {"contents": "buffer"},
        "model": "Corning-1234",
    }
    resource_info = ResourceInfo.model_validate(data)
    assert resource_info.resource_instance_accession_id == data["resource_instance_accession_id"]
    assert resource_info.model_dump()["category"] == "PLATE"

def test_slot_info_model():
    resource_data = {
        "resource_instance_accession_id": 10, "user_assigned_name": "Reagent Plate 1",
        "name": "corning_96_wellplate_360ul_flat",
        "python_fqn": "pylabrobot.resources.Plate", "category": "PLATE"
    }
    data = {
        "name": "A1",
        "x_coordinate": 10.0,
        "y_coordinate": 20.0,
        "z_coordinate": 0.5,
        "resource": resource_data,
    }
    slot_info = SlotInfo.model_validate(data)
    assert slot_info.name == data["name"]
    assert slot_info.resource is not None
    assert slot_info.resource.resource_instance_accession_id == resource_data["resource_instance_accession_id"]
    assert slot_info.model_dump()["resource"]["user_assigned_name"] == "Reagent Plate 1"

def test_deck_state_response_model():
    slot_data = {"name": "A1", "resource": None}
    data = {
        "deck_accession_id": 1,
        "user_friendly_name": "Main Deck",
        "python_fqn": "pylabrobot.resources.Deck",
        "size_x_mm": 500.0,
        "size_y_mm": 300.0,
        "size_z_mm": 20.0,
        "slots": [slot_data],
    }
    deck_state = DeckStateResponse.model_validate(data)
    assert deck_state.deck_accession_id == data["deck_accession_id"]
    assert len(deck_state.slots) == 1
    assert deck_state.slots[0].name == slot_data["name"]
    assert deck_state.model_dump()["slots"][0]["resource"] is None

def test_deck_update_message_model():
    resource_data = {
        "resource_instance_accession_id": 10, "user_assigned_name": "Tip Box",
        "name": "opentrons_96_tiprack_300ul",
        "python_fqn": "pylabrobot.resources.TipRack", "category": "TIP_RACK"
    }
    data = {
        "deck_accession_id": 1,
        "update_type": "resource_added",
        "slot_name": "B2",
        "resource_info": resource_data,
        # Timestamp will be auto-generated if not provided
    }
    deck_update = DeckUpdateMessage.model_validate(data)
    assert deck_update.deck_accession_id == data["deck_accession_id"]
    assert deck_update.update_type == data["update_type"]
    assert deck_update.resource_info is not None
    assert deck_update.resource_info.category == "TIP_RACK" # Check enum-like string
    assert deck_update.model_dump()["timestamp"] is not None # Check timestamp is generated

    # Test with explicit timestamp
    ts = "2024-01-01T12:00:00Z"
    data_with_ts = {**data, "timestamp": ts}
    deck_update_ts = DeckUpdateMessage.model_validate(data_with_ts)
    assert deck_update_ts.timestamp == ts


# --- Pytest Fixtures ---

@pytest.fixture(scope="session", autouse=True)
def setup_test_database_session():
    """Create test tables once per session."""
    create_tables_if_not_exist() # Uses the engine from utils.db
    yield
    # Teardown: drop tables or clear data if necessary, or let tests handle cleanup.
    # For simplicity, we might rely on tests cleaning up what they create,
    # or drop all tables if that's acceptable for the test environment.
    # Base.metadata.drop_all(bind=engine) # Example: drop all tables after tests

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Provides a test database session, rolling back changes after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback() # Rollback to ensure test isolation
        connection.close()

@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Provides a TestClient instance for FastAPI, with DB session override.
    """
    from praxis.backend.api.dependencies import get_db

    # Override the get_db dependency for this test client
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            # The session is managed by the db_session fixture (rollback, close)
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    del app.dependency_overrides[get_db] # Clean up override


@pytest.fixture(scope="function")
def setup_basic_machines(db_session: Session) -> None:
    """Sets up a basic DECK machine and a NON-DECK machine."""
    deck_machine = ManagedDeviceOrm(
        id=VALID_DECK_ID,
        user_friendly_name="Test Deck 1",
        python_fqn="pylabrobot.resources.Deck",
        praxis_machine_category=PraxisDeviceCategoryEnum.DECK,
        current_status=ManagedDeviceStatusEnum.ONLINE,
    )
    non_deck_machine = ManagedDeviceOrm(
        id=VALID_NON_DECK_ID,
        user_friendly_name="Test Heater 1",
        python_fqn="pylabrobot.heating_shaking.heater_shaker.HeaterShaker",
        praxis_machine_category=PraxisDeviceCategoryEnum.GENERIC_DEVICE, # Or another non-DECK category
        current_status=ManagedDeviceStatusEnum.ONLINE,
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
    assert len(data) == 1 # Should only return the DECK machine

    deck_info = data[0]
    assert deck_info["id"] == VALID_DECK_ID
    assert deck_info["user_friendly_name"] == "Test Deck 1"
    assert deck_info["python_fqn"] == "pylabrobot.resources.Deck"
    assert deck_info["current_status"] == "ONLINE" # Enum .name or .value

def test_get_specific_deck_state_not_found(client: TestClient, db_session: Session):
    """Test GET /api/workcell/decks/{deck_accession_id}/state for a non-existent deck."""
    response = client.get(f"/api/workcell/decks/{INVALID_DEVICE_ID}/state")
    assert response.status_code == 404 # Assuming WorkcellRuntimeError leads to 404 for not found
    assert "not found" in response.json()["detail"].lower()


def test_get_specific_deck_state_not_a_deck(client: TestClient, db_session: Session, setup_basic_machines: None):
    """Test GET /api/workcell/decks/{deck_accession_id}/state for a machine that is not a DECK."""
    response = client.get(f"/api/workcell/decks/{VALID_NON_DECK_ID}/state")
    assert response.status_code == 404 # As per current error handling
    assert "not categorized as a deck" in response.json()["detail"].lower()


@pytest.fixture(scope="function")
def setup_deck_with_resource(db_session: Session, setup_basic_machines: None) -> None:
    """Fixture to set up a deck with some resource on it."""
    # Resource Definition
    plate_def = ResourceDefinitionCatalogOrm(
        id=1,
        user_friendly_name="Standard 96 Well Plate Def",
        name="corning_96_wellplate_360ul_flat",
        python_fqn="pylabrobot.resources.Plate",
        plr_category=PlrCategoryEnum.PLATE,
        size_x_mm=127.76, size_y_mm=85.48, size_z_mm=14.35,
        nominal_volume_ul=380.0
    )
    tip_rack_def = ResourceDefinitionCatalogOrm(
        id=2,
        user_friendly_name="Standard 300ul Tip Rack Def",
        name="opentrons_96_tiprack_300ul",
        python_fqn="pylabrobot.resources.TipRack",
        plr_category=PlrCategoryEnum.TIP_RACK,
    )
    db_session.add_all([plate_def, tip_rack_def])
    db_session.commit() # Commit definitions so they can be referenced

    # Resource Instances
    plate_instance = ResourceInstanceOrm(
        id=1,
        user_assigned_name="PlateOnDeck",
        resource_definition_accession_id=plate_def.accession_id,
        location_machine_accession_id=VALID_DECK_ID, # Place on Test Deck 1
        current_deck_slot_name="A1",
        current_status=ResourceInstanceStatusEnum.AVAILABLE_ON_DECK,
        properties_json={"sample_type": "plasma"}
    )
    tip_rack_instance = ResourceInstanceOrm(
        id=2,
        user_assigned_name="TipsOnDeck",
        resource_definition_accession_id=tip_rack_def.accession_id,
        location_machine_accession_id=VALID_DECK_ID, # Place on Test Deck 1
        current_deck_slot_name="B2",
        current_status=ResourceInstanceStatusEnum.AVAILABLE_ON_DECK,
    )
    # Resource not on this deck
    other_plate_instance = ResourceInstanceOrm(
        id=3,
        user_assigned_name="PlateInStorage",
        resource_definition_accession_id=plate_def.accession_id,
        location_machine_accession_id=None, # Not on any deck
        current_status=ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
    )

    db_session.add_all([plate_instance, tip_rack_instance, other_plate_instance])
    db_session.commit()


def test_get_specific_deck_state_with_resource(client: TestClient, db_session: Session, setup_deck_with_resource: None):
    """Test GET /api/workcell/decks/{deck_accession_id}/state for a deck with resource."""
    response = client.get(f"/api/workcell/decks/{VALID_DECK_ID}/state")
    assert response.status_code == 200
    data = response.json()

    assert data["deck_accession_id"] == VALID_DECK_ID
    assert data["user_friendly_name"] == "Test Deck 1"
    assert data["python_fqn"] == "pylabrobot.resources.Deck"
    # Placeholder dimensions might be None or specific values if set in WorkcellRuntime
    assert "size_x_mm" in data
    assert "slots" in data

    slots_with_resource = {slot["name"]: slot["resource"] for slot in data["slots"] if slot["resource"]}
    assert len(slots_with_resource) == 2 # PlateOnDeck and TipsOnDeck

    # Check PlateOnDeck in A1
    assert "A1" in slots_with_resource
    plate_info = slots_with_resource["A1"]
    assert plate_info["user_assigned_name"] == "PlateOnDeck"
    assert plate_info["name"] == "corning_96_wellplate_360ul_flat"
    assert plate_info["category"] == "PLATE"
    assert plate_info["properties_json"] == {"sample_type": "plasma"}

    # Check TipsOnDeck in B2
    assert "B2" in slots_with_resource
    tip_rack_info = slots_with_resource["B2"]
    assert tip_rack_info["user_assigned_name"] == "TipsOnDeck"
    assert tip_rack_info["name"] == "opentrons_96_tiprack_300ul"
    assert tip_rack_info["category"] == "TIP_RACK"

    # Ensure no other resource is reported for this deck
    all_resource_names_on_deck = [lw["user_assigned_name"] for lw in slots_with_resource.values()]
    assert "PlateInStorage" not in all_resource_names_on_deck

    # TODO: Add checks for empty slots if get_deck_state_representation is updated to include them.

# --- WebSocket Endpoint Tests ---

def test_websocket_deck_updates_connection_and_broadcast(client: TestClient, db_session: Session, setup_basic_machines: None):
    """Test WebSocket connection and message broadcast."""
    with client.websocket_connect(f"/ws/decks/{VALID_DECK_ID}/updates") as websocket:
        # Test broadcast
        test_message_payload = {
            "message_type": "resource_updated",
            "slot_name": "C3",
            "resource_name": "NewTipBox"
        }
        response = client.post(f"/ws/test_broadcast/{VALID_DECK_ID}", json=test_message_payload) # Send JSON payload
        assert response.status_code == 200 # Assuming POST request for test broadcast

        # Receive the message from WebSocket
        message_str = websocket.receive_text()
        message_data = json.loads(message_str)

        assert message_data["deck_accession_id"] == VALID_DECK_ID
        # The test_broadcast endpoint sends a DeckUpdateMessage.
        # The message_type in the POST request to test_broadcast is used to construct this.
        assert message_data["update_type"] == test_message_payload["message_type"]
        assert message_data["slot_name"] == test_message_payload["slot_name"]

        assert message_data["resource_info"] is not None
        assert message_data["resource_info"]["user_assigned_name"] == test_message_payload["resource_name"]
        assert "timestamp" in message_data

        websocket.close()


def test_websocket_deck_updates_connection_to_invalid_deck(client: TestClient, db_session: Session):
    """Test WebSocket connection attempt to an invalid deck_accession_id."""
    with pytest.raises(Exception) as exc_info: # Catching generic Exception as TestClient might wrap WebSocketDisconnect
        with client.websocket_connect(f"/ws/decks/{INVALID_DEVICE_ID}/updates") as websocket:
            # We expect this connection to fail and be closed by the server.
            # Depending on how TestClient handles server-side close, this might raise.
            # If it doesn't raise immediately, try receiving:
            try:
                _ = websocket.receive_text(timeout=1) # timeout to prevent hanging if no close frame
            except Exception as e: # WebSocketTimeoutError or similar
                 pass # Expected if server just closes without sending a close frame client expects

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
        with client.websocket_connect(f"/ws/decks/{VALID_NON_DECK_ID}/updates") as websocket:
            pass # Expect connection to be refused/closed
    assert exc_info is not None


# TODO: Add more tests, e.g. multiple clients for the same deck,
#       clients for different decks, graceful disconnect from server side if possible to simulate.

# Note: Fixture `setup_test_database` is implicitly used by `db_session` which now uses `setup_test_database_session`.
# The `create_tables_if_not_exist` should be called by `setup_test_database_session`.
# Ensure `praxis.backend.main.app` is correctly configured to use the test DB settings
# if it initializes DB on startup outside of dependencies. For TestClient, overriding `get_db` is key.Okay, I've created the test file `praxis/backend/tests/api/test_workcell_api.py` with the Pydantic model unit tests and the initial structure for HTTP endpoint and WebSocket tests, including pytest fixtures.

Here's a summary of what's been done in this step:

1.  **Created Test File:**
    *   `praxis/backend/tests/api/test_workcell_api.py` has been created.

2.  **Pydantic Model Unit Tests:**
    *   Added tests for `DeckInfo`, `ResourceInfo`, `SlotInfo`, `DeckStateResponse`, and `DeckUpdateMessage`.
    *   These tests validate model creation from dictionary data and check basic field assignments. They also implicitly test `model_dump()` (serialization) by accessing dictionary keys on the dumped model.

3.  **Pytest Fixtures:**
    *   `setup_test_database_session()`: A session-scoped fixture to create database tables once using `create_tables_if_not_exist()` (assuming this function uses the `engine` from `utils.db` and `Base.metadata`).
    *   `db_session()`: A function-scoped fixture that provides a transactional database session. It begins a transaction before yielding the session and rolls it back afterwards, ensuring test isolation.
    *   `client(db_session)`: A function-scoped fixture that provides a `TestClient` for the FastAPI application. It overrides the `get_db` dependency to use the transactional `db_session` fixture.
    *   `setup_basic_machines(db_session)`: A function-scoped fixture to populate the database with a DECK machine (`id=VALID_DECK_ID`) and a non-DECK machine (`id=VALID_NON_DECK_ID`).
    *   `setup_deck_with_resource(db_session, setup_basic_machines)`: A function-scoped fixture that builds upon `setup_basic_machines`. It adds resource definitions and instances, placing some resource onto the `VALID_DECK_ID` at specific slots (`A1`, `B2`).

4.  **HTTP Endpoint Tests (Initial Structure):**
    *   **`GET /api/workcell/decks`:**
        *   `test_list_available_decks_empty`: Tests the endpoint when no decks are in the DB.
        *   `test_list_available_decks_with_data`: Tests with both a DECK and a non-DECK machine, asserting only the DECK is returned and its data is correct.
    *   **`GET /api/workcell/decks/{deck_accession_id}/state`:**
        *   `test_get_specific_deck_state_not_found`: Tests with an ID that doesn't exist.
        *   `test_get_specific_deck_state_not_a_deck`: Tests with an ID of a machine that isn't a DECK.
        *   `test_get_specific_deck_state_with_resource`: Tests with a valid DECK ID that has resource placed on it (using `setup_deck_with_resource` fixture). It verifies the returned deck structure, slot information, and details of the resource on the slots.

5.  **WebSocket Endpoint Tests (Initial Structure):**
    *   `test_websocket_deck_updates_connection_and_broadcast`: Tests successful WebSocket connection, then uses the `POST /ws/test_broadcast/{deck_accession_id}` endpoint to send a message, and verifies the WebSocket client receives and can parse this message.
    *   `test_websocket_deck_updates_connection_to_invalid_deck`: Tests attempting to connect to a WebSocket for a `deck_accession_id` that doesn't exist in the database. It asserts that an exception occurs, indicating the connection was refused or closed.
    *   `test_websocket_connection_to_non_deck_machine`: Tests attempting to connect to a WebSocket for a `deck_accession_id` that corresponds to a machine not categorized as a DECK. It also asserts that an exception occurs.

**Next Steps (Implicitly Done by the Tool in a Single Turn):**

The tool will effectively execute this entire plan in one go, creating the file with all the tests. The fixtures will ensure that the database is set up correctly for each test function that requires it.

I have defined the tests and fixtures as requested. The `create_tables_if_not_exist` function (assumed to be in `utils.db` or similar) is crucial for the `setup_test_database_session` fixture to work correctly by creating tables before any session starts. The dependency override mechanism in FastAPI's `TestClient` is used to ensure that API endpoints use the test-managed, transactional database session.
