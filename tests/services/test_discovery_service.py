"""Tests for the DiscoveryService."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch

from praxis.backend.services.discovery_service import DiscoveryService
from praxis.backend.services.resource_type_definition import ResourceTypeDefinitionService
from praxis.backend.services.machine_type_definition import MachineTypeDefinitionService
from praxis.backend.services.deck_type_definition import DeckTypeDefinitionService
from praxis.backend.models.orm.resource import ResourceDefinitionOrm
from sqlalchemy.ext.asyncio import create_async_engine
from praxis.backend.utils.db import Base


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
@patch('praxis.backend.services.resource_type_definition.ResourceTypeDefinitionService.discover_and_synchronize_type_definitions')
@patch('praxis.backend.services.machine_type_definition.MachineTypeDefinitionService.discover_and_synchronize_type_definitions')
@patch('praxis.backend.services.deck_type_definition.DeckTypeDefinitionService.discover_and_synchronize_type_definitions')
async def test_discover_and_sync_resources(mock_deck_discover_and_sync, mock_machine_discover_and_sync, mock_resource_discover_and_sync, db: AsyncSession):
    """Test that the DiscoveryService can discover and sync resources."""
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

    mock_resource_discover_and_sync.assert_called_once()
    mock_machine_discover_and_sync.assert_called_once()
    mock_deck_discover_and_sync.assert_called_once()


@pytest.mark.asyncio
async def test_table_exists():
    """Test that the resource_definition_catalog table exists."""
    from sqlalchemy import text
    from sqlalchemy.orm import sessionmaker

    ASYNC_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5433/test_db"
    engine = create_async_engine(ASYNC_DATABASE_URL)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    session = SessionLocal()

    try:
        await session.execute(text("SELECT 1 FROM resource_definition_catalog LIMIT 1"))
        assert True, "resource_definition_catalog table exists"
    except Exception as e:
        assert False, f"resource_definition_catalog table does not exist: {e}"
    finally:
        await session.close()
        await engine.dispose()
