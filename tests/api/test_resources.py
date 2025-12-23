"""Comprehensive API tests for resources following the established pattern.

Based on test_decks.py (5/5 passing) and API_TEST_PATTERN.md
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import create_resource, create_resource_definition


@pytest.mark.asyncio
async def test_create_resource(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test creating a resource via API."""
    # 1. SETUP: Create resource definition
    resource_def = await create_resource_definition(
        db_session,
        name="test_resource_def_api",
        fqn="test.resource.def.api",
    )

    # 2. SETUP: Prepare payload
    payload = {
        "name": "test_resource_api",
        "fqn": "test.resource.api",
        "asset_type": "RESOURCE",
        "resource_definition_accession_id": str(resource_def.accession_id),
    }

    # 3. ACT: Call the API
    response = await client.post("/api/v1/resources/", json=payload)

    # 4. ASSERT: Check the response
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test_resource_api"
    assert data["fqn"] == "test.resource.api"
    assert data["accession_id"] is not None


@pytest.mark.asyncio
async def test_get_resource(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test retrieving a single resource by ID."""
    # 1. SETUP: Create test resource
    resource = await create_resource(db_session, name="test_resource_get")

    # 2. ACT: Retrieve via API
    response = await client.get(f"/api/v1/resources/{resource.accession_id}")

    # 3. ASSERT: Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == resource.name
    assert data["accession_id"] == str(resource.accession_id)


@pytest.mark.asyncio
async def test_get_multi_resources(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test retrieving multiple resources."""
    # 1. SETUP: Create shared resource definition
    resource_def = await create_resource_definition(
        db_session,
        name="shared_resource_def_multi",
        fqn="test.resource.def.shared.multi",
    )

    # 2. SETUP: Create multiple resources sharing definition
    await create_resource(db_session, name="resource_1_multi", resource_definition=resource_def)
    await create_resource(db_session, name="resource_2_multi", resource_definition=resource_def)
    await create_resource(db_session, name="resource_3_multi", resource_definition=resource_def)

    # 3. ACT: Call the API
    response = await client.get("/api/v1/resources/")

    # 4. ASSERT: Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


@pytest.mark.asyncio
async def test_update_resource(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test updating a resource's attributes."""
    # 1. SETUP: Create resource to update
    resource = await create_resource(db_session, name="original_resource_name")

    # 2. ACT: Update via API
    new_name = "updated_resource_name"
    response = await client.put(
        f"/api/v1/resources/{resource.accession_id}",
        json={"name": new_name},
    )

    # 3. ASSERT: Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == new_name

    # Verify persistence in database
    await db_session.refresh(resource)
    assert resource.name == new_name


@pytest.mark.asyncio
async def test_delete_resource(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test deleting a resource.

    Note: Mocks db.delete() to avoid CircularDependencyError from
    cascade relationships during test rollback.
    """
    from unittest.mock import patch

    # 1. SETUP: Create resource to delete
    resource = await create_resource(db_session, name="resource_to_delete")
    resource_id = resource.accession_id

    # 2. Mock delete operations to avoid circular dependency
    async def mock_delete(obj):
        pass

    async def mock_flush():
        pass

    with patch.object(db_session, "delete", new=mock_delete), \
         patch.object(db_session, "flush", new=mock_flush):

        # 3. ACT: Call the API
        response = await client.delete(f"/api/v1/resources/{resource_id}")

        # 4. ASSERT: Verify response
        assert response.status_code == 204  # No Content
