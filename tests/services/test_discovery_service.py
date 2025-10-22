"""Tests for the DiscoveryService."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch

from praxis.backend.services.discovery_service import DiscoveryService
from praxis.backend.services.resource_type_definition import ResourceTypeDefinitionService
from praxis.backend.services.machine_type_definition import MachineTypeDefinitionService
from praxis.backend.services.deck_type_definition import DeckTypeDefinitionService
from praxis.backend.models.orm.resource import ResourceDefinitionOrm


@pytest.mark.asyncio
async def test_create_discovery_service(db: AsyncSession):
    """Test that the DiscoveryService can be created."""
    resource_type_service = ResourceTypeDefinitionService(db)
    machine_type_service = MachineTypeDefinitionService(db)
    deck_type_service = DeckTypeDefinitionService(db)

    discovery_service = DiscoveryService(
        db_session_factory=lambda: db,
        resource_type_definition_service=resource_type_service,
        machine_type_definition_service=machine_type_service,
        deck_type_definition_service=deck_type_service,
    )

    assert discovery_service is not None

@pytest.mark.asyncio
@patch('praxis.backend.utils.plr_inspection.get_resource_classes')
async def test_discover_and_sync_resources(mock_get_resource_classes, db: AsyncSession):
    """Test that the DiscoveryService can discover and sync resources."""
    # Mock the pylabrobot library to return a known set of resources
    mock_get_resource_classes.return_value = {
        'pylabrobot.resources.Plate': object,
        'pylabrobot.resources.TipRack': object,
    }

    resource_type_service = ResourceTypeDefinitionService(db)
    machine_type_service = MachineTypeDefinitionService(db)
    deck_type_service = DeckTypeDefinitionService(db)

    discovery_service = DiscoveryService(
        db_session_factory=lambda: db,
        resource_type_definition_service=resource_type_service,
        machine_type_definition_service=machine_type_service,
        deck_type_definition_service=deck_type_service,
    )

    await discovery_service.discover_and_sync_all_definitions(protocol_search_paths=[])

    # Check that the resources were correctly added to the database
    from sqlalchemy import select
    result = await db.execute(select(ResourceDefinitionOrm))
    definitions = result.scalars().all()
    assert len(definitions) == 2
    assert {d.fqn for d in definitions} == {'pylabrobot.resources.Plate', 'pylabrobot.resources.TipRack'}

@pytest.mark.asyncio
async def test_table_exists(db: AsyncSession):
    """Test that the resource_definition_catalog table exists."""
    from sqlalchemy import text
    try:
        await db.execute(text("SELECT 1 FROM resource_definition_catalog LIMIT 1"))
        assert True, "resource_definition_catalog table exists"
    except Exception as e:
        assert False, f"resource_definition_catalog table does not exist: {e}"
