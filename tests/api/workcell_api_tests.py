import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

# --- Test Data ---
VALID_WORKCELL_ID = "test_workcell_id"
VALID_WORKCELL_NAME = "Test Workcell"
UPDATED_WORKCELL_NAME = "Updated Test Workcell"
INVALID_WORKCELL_ID = "invalid_workcell_id"

# --- CRUD Endpoint Tests ---

@pytest.mark.asyncio
async def test_create_workcell(api_client: AsyncClient, db_session: AsyncSession) -> None:
    workcell_data = {"name": VALID_WORKCELL_NAME, "description": "A test workcell"}
    response = await api_client.post("/api/v1/workcell/", json=workcell_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == VALID_WORKCELL_NAME
    assert "accession_id" in data

    # Test creating with existing name (should fail)
    response = await api_client.post("/api/v1/workcell/", json=workcell_data)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_get_workcell_by_id(api_client: AsyncClient, db_session: AsyncSession) -> None:
    # Create a workcell first
    workcell_data = {"name": "get_by_id_test", "description": "A test workcell"}
    create_response = await api_client.post("/api/v1/workcell/", json=workcell_data)
    created_workcell_id = create_response.json()["accession_id"]

    response = await api_client.get(f"/api/v1/workcell/{created_workcell_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "get_by_id_test"
    assert data["accession_id"] == created_workcell_id

@pytest.mark.asyncio
async def test_get_workcell_by_name(api_client: AsyncClient, db_session: AsyncSession) -> None:
    # Create a workcell first
    workcell_data = {"name": "get_by_name_test", "description": "A test workcell"}
    await api_client.post("/api/v1/workcell/", json=workcell_data)

    response = await api_client.get(f"/api/v1/workcell/{'get_by_name_test'}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "get_by_name_test"

@pytest.mark.asyncio
async def test_get_non_existent_workcell(api_client: AsyncClient, db_session: AsyncSession) -> None:
    response = await api_client.get(f"/api/v1/workcell/{INVALID_WORKCELL_ID}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_list_workcells(api_client: AsyncClient, db_session: AsyncSession) -> None:
    # Create a few workcells
    await api_client.post("/api/v1/workcell/", json={"name": "Workcell 1"})
    await api_client.post("/api/v1/workcell/", json={"name": "Workcell 2"})

    response = await api_client.get("/api/v1/workcell/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

@pytest.mark.asyncio
async def test_update_workcell(api_client: AsyncClient, db_session: AsyncSession) -> None:
    # Create a workcell first
    workcell_data = {"name": "update_test", "description": "A test workcell"}
    create_response = await api_client.post("/api/v1/workcell/", json=workcell_data)
    created_workcell_id = create_response.json()["accession_id"]

    update_data = {"name": UPDATED_WORKCELL_NAME, "description": "Updated description"}
    response = await api_client.put(f"/api/v1/workcell/{created_workcell_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == UPDATED_WORKCELL_NAME
    assert data["description"] == "Updated description"

@pytest.mark.asyncio
async def test_update_non_existent_workcell(api_client: AsyncClient, db_session: AsyncSession) -> None:
    update_data = {"name": UPDATED_WORKCELL_NAME}
    response = await api_client.put(f"/api/v1/workcell/{INVALID_WORKCELL_ID}", json=update_data)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_workcell(api_client: AsyncClient, db_session: AsyncSession) -> None:
    # Create a workcell first
    workcell_data = {"name": "delete_test", "description": "A test workcell"}
    create_response = await api_client.post("/api/v1/workcell/", json=workcell_data)
    created_workcell_id = create_response.json()["accession_id"]

    response = await api_client.delete(f"/api/v1/workcell/{created_workcell_id}")
    assert response.status_code == 204

    # Verify it's deleted
    response = await api_client.get(f"/api/v1/workcell/{created_workcell_id}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_non_existent_workcell(api_client: AsyncClient, db_session: AsyncSession) -> None:
    response = await api_client.delete(f"/api/v1/workcell/{INVALID_WORKCELL_ID}")
    assert response.status_code == 404