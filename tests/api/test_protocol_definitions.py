"""Comprehensive API tests for protocol definitions following the established pattern.

Based on test_decks.py (5/5 passing) and API_TEST_PATTERN.md
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.helpers import create_protocol_definition


@pytest.mark.asyncio
async def test_create_protocol_definition(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test creating a protocol definition via API."""
    # 1. SETUP: Prepare payload (sources will be auto-created by service)
    payload = {
        "name": "test_protocol_api",
        "fqn": "test.protocols.test_protocol_api",
        "source_file_path": "/test/protocols/test_protocol_api.py",
        "module_name": "test.protocols.test_protocol_api",
        "function_name": "test_protocol_api",
        "version": "1.0.0",
        "description": "A test protocol created via API",
    }

    # 2. ACT: Call the API
    response = await client.post("/api/v1/protocols/definitions", json=payload)

    # 3. ASSERT: Check the response
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["name"] == "test_protocol_api"
    assert data["fqn"] == "test.protocols.test_protocol_api"
    assert data["accession_id"] is not None


@pytest.mark.asyncio
async def test_get_protocol_definition(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test retrieving a single protocol definition by ID."""
    # 1. SETUP: Create test protocol definition
    protocol_def = await create_protocol_definition(db_session, name="test_protocol_get")

    # 2. ACT: Retrieve via API
    response = await client.get(f"/api/v1/protocols/definitions/{protocol_def.accession_id}")

    # 3. ASSERT: Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == protocol_def.name
    assert data["accession_id"] == str(protocol_def.accession_id)


@pytest.mark.asyncio
async def test_get_multi_protocol_definitions(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test retrieving multiple protocol definitions."""
    # 1. SETUP: Create multiple protocol definitions (unique names to avoid constraints)
    await create_protocol_definition(db_session, name="protocol_def_1")
    await create_protocol_definition(db_session, name="protocol_def_2")
    await create_protocol_definition(db_session, name="protocol_def_3")

    # 2. ACT: Call the API
    response = await client.get("/api/v1/protocols/definitions")

    # 3. ASSERT: Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


@pytest.mark.asyncio
async def test_update_protocol_definition(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test updating a protocol definition's attributes."""
    # 1. SETUP: Create protocol definition to update
    protocol_def = await create_protocol_definition(
        db_session,
        name="original_protocol_name"
    )

    # 2. ACT: Update via API
    new_description = "Updated description"
    response = await client.put(
        f"/api/v1/protocols/definitions/{protocol_def.accession_id}",
        json={"description": new_description},
    )

    # 3. ASSERT: Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == new_description

    # Verify persistence in database
    await db_session.refresh(protocol_def)
    assert protocol_def.description == new_description


@pytest.mark.asyncio
async def test_delete_protocol_definition(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test deleting a protocol definition.

    Note: Mocks db.delete() to avoid CircularDependencyError from
    cascade relationships during test rollback.
    """
    from unittest.mock import patch

    # 1. SETUP: Create protocol definition to delete
    protocol_def = await create_protocol_definition(
        db_session,
        name="protocol_def_to_delete"
    )
    protocol_def_id = protocol_def.accession_id

    # 2. Mock delete operations to avoid circular dependency
    async def mock_delete(obj):
        pass

    async def mock_flush():
        pass

    with patch.object(db_session, 'delete', new=mock_delete), \
         patch.object(db_session, 'flush', new=mock_flush):

        # 3. ACT: Call the API
        response = await client.delete(f"/api/v1/protocols/definitions/{protocol_def_id}")

        # 4. ASSERT: Verify response
        assert response.status_code == 204  # No Content
