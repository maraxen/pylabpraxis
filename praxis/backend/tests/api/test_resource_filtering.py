
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.domain.resource import ResourceDefinition

@pytest.mark.asyncio
async def test_filter_resource_definitions_by_plr_category(
    client: AsyncClient, db: AsyncSession
) -> None:
    """Test that we can filter resource definitions by plr_category."""
    # Create some test data
    # Note: Using attribute names from ResourceDefinition SQLModel
    plate_def = ResourceDefinition(
        name="Test Plate",
        fqn="pylabrobot.resources.Plate",
        plr_category="plate",
        is_consumable=True
    )
    tip_rack_def = ResourceDefinition(
        name="Test Tip Rack",
        fqn="pylabrobot.resources.TipRack",
        plr_category="tip_rack",
        is_consumable=True
    )
    db.add_all([plate_def, tip_rack_def])
    await db.commit()

    # Test filtering by plate
    # Assuming the endpoint is /api/v1/resources/definitions (based on api/resources.py)
    response = await client.get("/api/v1/resources/definitions?plr_category=plate")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Plate"

    # Test filtering by tip_rack
    response = await client.get("/api/v1/resources/definitions?plr_category=tip_rack")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Tip Rack"

    # Test with no filter
    response = await client.get("/api/v1/resources/definitions")
    assert response.status_code == 200
    data = response.json()
    # There might be existing data in the DB depending on the test setup
    # but we definitely expect at least our 2 new items.
    assert len(data) >= 2
