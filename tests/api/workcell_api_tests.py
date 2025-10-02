import pytest
from fastapi.testclient import TestClient
import uuid

# --- Test Data ---
VALID_WORKCELL_NAME = "Test Workcell"
UPDATED_WORKCELL_NAME = "Updated Test Workcell"
INVALID_WORKCELL_ID = str(uuid.uuid4())

# --- CRUD Endpoint Tests ---

@pytest.mark.asyncio
async def test_create_workcell(client: TestClient) -> None:
    workcell_data = {"name": VALID_WORKCELL_NAME, "fqn": "test.workcell.fqn"}
    response = client.post("/api/v1/workcell/", json=workcell_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == VALID_WORKCELL_NAME
    assert "accession_id" in data

@pytest.mark.asyncio
async def test_get_workcell_by_id(client: TestClient) -> None:
    # Create a workcell first
    workcell_data = {"name": "Another Test Workcell", "fqn": "test.workcell.fqn2"}
    create_response = client.post("/api/v1/workcell/", json=workcell_data)
    assert create_response.status_code == 200
    created_workcell_id = create_response.json()["accession_id"]

    response = client.get(f"/api/v1/workcell/{created_workcell_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Another Test Workcell"
    assert data["accession_id"] == created_workcell_id

@pytest.mark.asyncio
async def test_get_non_existent_workcell(client: TestClient) -> None:
    response = client.get(f"/api/v1/workcell/{INVALID_WORKCELL_ID}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_list_workcells(client: TestClient) -> None:
    # Create a few workcells
    client.post("/api/v1/workcell/", json={"name": "Workcell 1", "fqn": "test.workcell.list1"})
    client.post("/api/v1/workcell/", json={"name": "Workcell 2", "fqn": "test.workcell.list2"})

    response = client.get("/api/v1/workcell/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2 # May have other workcells from other tests if not properly isolated

@pytest.mark.asyncio
async def test_update_workcell(client: TestClient) -> None:
    # Create a workcell first
    workcell_data = {"name": "Updatable Workcell", "fqn": "test.workcell.update"}
    create_response = client.post("/api/v1/workcell/", json=workcell_data)
    created_workcell_id = create_response.json()["accession_id"]

    update_data = {"name": UPDATED_WORKCELL_NAME}
    response = client.put(f"/api/v1/workcell/{created_workcell_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == UPDATED_WORKCELL_NAME

@pytest.mark.asyncio
async def test_update_non_existent_workcell(client: TestClient) -> None:
    update_data = {"name": UPDATED_WORKCELL_NAME}
    response = client.put(f"/api/v1/workcell/{INVALID_WORKCELL_ID}", json=update_data)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_workcell(client: TestClient) -> None:
    # Create a workcell first
    workcell_data = {"name": "Deletable Workcell", "fqn": "test.workcell.delete"}
    create_response = client.post("/api/v1/workcell/", json=workcell_data)
    created_workcell_id = create_response.json()["accession_id"]

    response = client.delete(f"/api/v1/workcell/{created_workcell_id}")
    assert response.status_code == 200

    # Verify it's deleted
    response = client.get(f"/api/v1/workcell/{created_workcell_id}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_non_existent_workcell(client: TestClient) -> None:
    response = client.delete(f"/api/v1/workcell/{INVALID_WORKCELL_ID}")
    assert response.status_code == 404