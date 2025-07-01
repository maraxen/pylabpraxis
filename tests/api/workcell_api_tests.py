from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# --- Test Data ---
VALID_WORKCELL_ID = "test_workcell_id"
VALID_WORKCELL_NAME = "Test Workcell"
UPDATED_WORKCELL_NAME = "Updated Test Workcell"
INVALID_WORKCELL_ID = "invalid_workcell_id"

# --- CRUD Endpoint Tests ---

def test_create_workcell(client: TestClient, db_session: Session):
    workcell_data = {"name": VALID_WORKCELL_NAME, "description": "A test workcell"}
    response = client.post("/api/workcell/", json=workcell_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == VALID_WORKCELL_NAME
    assert "accession_id" in data

    # Test creating with existing name (should fail)
    response = client.post("/api/workcell/", json=workcell_data)
    assert response.status_code == 400

def test_get_workcell_by_id(client: TestClient, db_session: Session):
    # Create a workcell first
    workcell_data = {"name": VALID_WORKCELL_NAME, "description": "A test workcell"}
    create_response = client.post("/api/workcell/", json=workcell_data)
    created_workcell_id = create_response.json()["accession_id"]

    response = client.get(f"/api/workcell/{created_workcell_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == VALID_WORKCELL_NAME
    assert data["accession_id"] == created_workcell_id

def test_get_workcell_by_name(client: TestClient, db_session: Session):
    # Create a workcell first
    workcell_data = {"name": VALID_WORKCELL_NAME, "description": "A test workcell"}
    client.post("/api/workcell/", json=workcell_data)

    response = client.get(f"/api/workcell/{VALID_WORKCELL_NAME}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == VALID_WORKCELL_NAME

def test_get_non_existent_workcell(client: TestClient, db_session: Session):
    response = client.get(f"/api/workcell/{INVALID_WORKCELL_ID}")
    assert response.status_code == 404

def test_list_workcells(client: TestClient, db_session: Session):
    # Create a few workcells
    client.post("/api/workcell/", json={"name": "Workcell 1"})
    client.post("/api/workcell/", json={"name": "Workcell 2"})

    response = client.get("/api/workcell/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2 # May have other workcells from other tests if not properly isolated

def test_update_workcell(client: TestClient, db_session: Session):
    # Create a workcell first
    workcell_data = {"name": VALID_WORKCELL_NAME, "description": "A test workcell"}
    create_response = client.post("/api/workcell/", json=workcell_data)
    created_workcell_id = create_response.json()["accession_id"]

    update_data = {"name": UPDATED_WORKCELL_NAME, "description": "Updated description"}
    response = client.put(f"/api/workcell/{created_workcell_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == UPDATED_WORKCELL_NAME
    assert data["description"] == "Updated description"

def test_update_non_existent_workcell(client: TestClient, db_session: Session):
    update_data = {"name": UPDATED_WORKCELL_NAME}
    response = client.put(f"/api/workcell/{INVALID_WORKCELL_ID}", json=update_data)
    assert response.status_code == 404

def test_delete_workcell(client: TestClient, db_session: Session):
    # Create a workcell first
    workcell_data = {"name": VALID_WORKCELL_NAME, "description": "A test workcell"}
    create_response = client.post("/api/workcell/", json=workcell_data)
    created_workcell_id = create_response.json()["accession_id"]

    response = client.delete(f"/api/workcell/{created_workcell_id}")
    assert response.status_code == 204

    # Verify it's deleted
    response = client.get(f"/api/workcell/{created_workcell_id}")
    assert response.status_code == 404

def test_delete_non_existent_workcell(client: TestClient, db_session: Session):
    response = client.delete(f"/api/workcell/{INVALID_WORKCELL_ID}")
    assert response.status_code == 404
