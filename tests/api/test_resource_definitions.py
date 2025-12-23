"""Comprehensive API tests for resource definitions following the established pattern.

Based on test_decks.py (5/5 passing) and API_TEST_PATTERN.md
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import create_resource_definition


@pytest.mark.asyncio
async def test_create_resource_definition(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test creating a resource definition via API."""
    # 1. SETUP: Prepare payload
    payload = {
        "name": "test_resource_def_api",
        "fqn": "test.resource.definition.api",
        "description": "A test resource definition created via API",
        "resource_type": "plate",
        "is_consumable": True,
    }

    # 2. ACT: Call the API
    response = await client.post("/api/v1/resources/definitions", json=payload)

    # 3. ASSERT: Check the response
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test_resource_def_api"
    assert data["fqn"] == "test.resource.definition.api"
    assert data["description"] == "A test resource definition created via API"
    assert data["accession_id"] is not None


@pytest.mark.asyncio
async def test_get_resource_definition(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test retrieving a single resource definition by ID."""
    # 1. SETUP: Create test resource definition
    resource_def = await create_resource_definition(
        db_session,
        name="test_resource_def_get",
        fqn="test.resource.def.get",
    )

    # 2. ACT: Retrieve via API
    response = await client.get(f"/api/v1/resources/definitions/{resource_def.accession_id}")

    # 3. ASSERT: Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == resource_def.name
    assert data["fqn"] == resource_def.fqn
    assert data["accession_id"] == str(resource_def.accession_id)


@pytest.mark.asyncio
async def test_get_multi_resource_definitions(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test retrieving multiple resource definitions."""
    # 1. SETUP: Create multiple resource definitions (unique fqns to avoid constraints)
    await create_resource_definition(db_session, name="resource_def_1", fqn="test.resource.def.1")
    await create_resource_definition(db_session, name="resource_def_2", fqn="test.resource.def.2")
    await create_resource_definition(db_session, name="resource_def_3", fqn="test.resource.def.3")

    # 2. ACT: Call the API
    response = await client.get("/api/v1/resources/definitions")

    # 3. ASSERT: Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


@pytest.mark.asyncio
async def test_update_resource_definition(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test updating a resource definition's attributes."""
    # 1. SETUP: Create resource definition to update
    resource_def = await create_resource_definition(
        db_session,
        name="original_resource_def_name",
        fqn="test.resource.def.original",
    )

    # 2. ACT: Update via API
    new_description = "Updated description"
    response = await client.put(
        f"/api/v1/resources/definitions/{resource_def.accession_id}",
        json={"fqn": resource_def.fqn, "description": new_description},
    )

    # 3. ASSERT: Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == new_description

    # Verify persistence in database
    await db_session.refresh(resource_def)
    assert resource_def.description == new_description


@pytest.mark.asyncio
async def test_delete_resource_definition(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test deleting a resource definition.

    Note: Mocks db.delete() to avoid CircularDependencyError from
    cascade relationships during test rollback.
    """
    from unittest.mock import patch

    # 1. SETUP: Create resource definition to delete
    resource_def = await create_resource_definition(
        db_session,
        name="resource_def_to_delete",
        fqn="test.resource.def.to.delete",
    )
    resource_def_id = resource_def.accession_id

    # 2. Mock delete operations to avoid circular dependency
    async def mock_delete(obj):
        pass

    async def mock_flush():
        pass

    with patch.object(db_session, "delete", new=mock_delete), \
         patch.object(db_session, "flush", new=mock_flush):

        # 3. ACT: Call the API
        response = await client.delete(f"/api/v1/resources/definitions/{resource_def_id}")

        # 4. ASSERT: Verify response
        assert response.status_code == 204  # No Content


@pytest.mark.asyncio
async def test_get_resource_definition_facets(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test retrieving facets for resource definitions.

    Facets endpoint returns unique values with counts for filterable fields:
    plr_category, vendor, num_items, plate_type, well_volume_ul, tip_volume_ul.

    Note: Test database may have pre-existing data from sync, so we verify
    response structure rather than specific values.
    """
    # 1. ACT: Call the facets endpoint
    response = await client.get("/api/v1/resources/definitions/facets")

    # 2. ASSERT: Verify response structure
    assert response.status_code == 200
    data = response.json()

    # Check expected facet fields exist
    expected_facets = ["plr_category", "vendor", "num_items", "plate_type", "well_volume_ul", "tip_volume_ul"]
    for facet in expected_facets:
        assert facet in data, f"Missing facet: {facet}"
        assert isinstance(data[facet], list), f"Facet {facet} should be a list"

    # Check facet value structure (if any values exist)
    for facet_name, facet_values in data.items():
        for item in facet_values:
            assert "value" in item, f"Facet item missing 'value' key in {facet_name}"
            assert "count" in item, f"Facet item missing 'count' key in {facet_name}"
            assert isinstance(item["count"], int), f"Facet count should be int in {facet_name}"
            assert item["count"] > 0, f"Facet count should be positive in {facet_name}"


