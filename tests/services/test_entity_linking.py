"""Tests for entity linking service."""

import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models import (
    DeckOrm,
    MachineOrm,
    MachineStatusEnum,
    ResourceDefinitionOrm,
    ResourceOrm,
    ResourceStatusEnum,
)
from praxis.backend.models.enums import AssetType
from praxis.backend.services.entity_linking import (
    _create_or_link_machine_counterpart_for_resource,
    _create_or_link_resource_counterpart_for_machine,
    _read_resource_definition_for_linking,
    synchronize_deck_resource_names,
    synchronize_machine_resource_names,
    synchronize_resource_deck_names,
    synchronize_resource_machine_names,
)


@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Mock database session."""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def resource_definition() -> ResourceDefinitionOrm:
    obj = ResourceDefinitionOrm(
        name="test_resource_def",
        fqn="test.fqn",
    )
    # Set ID manually for testing stability if needed, though usually auto-generated
    return obj


@pytest.mark.asyncio
async def test_read_resource_definition_for_linking(
    mock_db_session: AsyncMock,
    resource_definition: ResourceDefinitionOrm,
) -> None:
    """Test reading a resource definition."""
    # Mock result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = resource_definition
    mock_db_session.execute.return_value = mock_result

    result = await _read_resource_definition_for_linking(
        mock_db_session, "test_resource_def"
    )
    assert result == resource_definition
    mock_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_read_resource_definition_for_linking_not_found(
    mock_db_session: AsyncMock,
) -> None:
    """Test reading a resource definition that doesn't exist."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    with pytest.raises(ValueError, match="Resource definition 'test' not found"):
        await _read_resource_definition_for_linking(mock_db_session, "test")


@pytest.mark.asyncio
@patch("praxis.backend.services.entity_linking.uuid7")
@patch("praxis.backend.services.entity_linking._read_resource_definition_for_linking")
async def test_create_or_link_resource_counterpart_new(
    mock_read_def: AsyncMock,
    mock_uuid7: MagicMock,
    mock_db_session: AsyncMock,
    resource_definition: ResourceDefinitionOrm,
) -> None:
    """Test creating a new resource counterpart for a machine."""
    mock_uuid7.return_value = uuid.UUID("00000000-0000-0000-0000-000000000001")
    mock_read_def.return_value = resource_definition

    machine = MachineOrm(
        name="test_machine",
        fqn="test.machine",
        asset_type=AssetType.MACHINE,
        status=MachineStatusEnum.OFFLINE,
    )

    result = await _create_or_link_resource_counterpart_for_machine(
        db=mock_db_session,
        machine_orm=machine,
        resource_counterpart_accession_id=None,
        resource_definition_name="test_resource_def",
        resource_properties_json={},
    )

    assert result is not None
    assert isinstance(result, ResourceOrm)
    assert result.name == "test_machine_resource"
    assert machine.resource_counterpart_accession_id == result.accession_id
    mock_db_session.add.assert_called()
    mock_db_session.flush.assert_called()


@pytest.mark.asyncio
async def test_create_or_link_resource_counterpart_existing_link(
    mock_db_session: AsyncMock,
) -> None:
    """Test linking to an existing resource counterpart via ID."""
    machine = MachineOrm(
        name="test_machine",
        fqn="test.machine",
        asset_type=AssetType.MACHINE,
        status=MachineStatusEnum.OFFLINE,
    )

    # Need a definition ID to create resource
    def_id = uuid.uuid4()

    existing_resource = ResourceOrm(
        name="existing_resource",
        fqn="resource.fqn",
        asset_type=AssetType.RESOURCE,
        resource_definition_accession_id=def_id,
        status=ResourceStatusEnum.AVAILABLE_IN_STORAGE,
    )

    mock_db_session.get.return_value = existing_resource

    result = await _create_or_link_resource_counterpart_for_machine(
        db=mock_db_session,
        machine_orm=machine,
        resource_counterpart_accession_id=existing_resource.accession_id,
    )

    assert result == existing_resource
    assert machine.resource_counterpart == existing_resource
    assert existing_resource.machine_counterpart == machine
    assert existing_resource.name == "test_machine"  # Synced name
    assert machine.asset_type == AssetType.MACHINE_RESOURCE


@pytest.mark.asyncio
@patch("praxis.backend.services.entity_linking.uuid7")
async def test_create_or_link_machine_counterpart_new(
    mock_uuid7: MagicMock,
    mock_db_session: AsyncMock,
) -> None:
    """Test creating a new machine counterpart for a resource."""
    mock_uuid7.return_value = uuid.UUID("00000000-0000-0000-0000-000000000002")

    resource = ResourceOrm(
        name="test_resource",
        fqn="resource.fqn",
        asset_type=AssetType.RESOURCE,
        resource_definition_accession_id=uuid.uuid4(),
        status=ResourceStatusEnum.AVAILABLE_IN_STORAGE,
    )

    result = await _create_or_link_machine_counterpart_for_resource(
        db=mock_db_session,
        resource_orm=resource,
        machine_counterpart_accession_id=None,
        machine_name="new_machine",
        machine_fqn="new.machine.fqn",
    )

    assert result is not None
    assert isinstance(result, MachineOrm)
    assert result.name == "test_resource_machine"
    assert resource.machine_counterpart == result
    mock_db_session.add.assert_called()
    mock_db_session.flush.assert_called()


@pytest.mark.asyncio
async def test_synchronize_machine_resource_names(
    mock_db_session: AsyncMock,
) -> None:
    """Test synchronizing names between machine and resource."""
    machine = MachineOrm(
        name="machine",
        fqn="machine.fqn",
        asset_type=AssetType.MACHINE_RESOURCE,
        status=MachineStatusEnum.OFFLINE,
    )
    resource = ResourceOrm(
        name="old_resource_name",
        fqn="resource.fqn",
        asset_type=AssetType.MACHINE_RESOURCE,
        resource_definition_accession_id=uuid.uuid4(),
        status=ResourceStatusEnum.AVAILABLE_IN_STORAGE,
    )
    machine.resource_counterpart = resource
    resource.machine_counterpart = machine

    await synchronize_machine_resource_names(mock_db_session, machine, new_machine_name="new_name")

    assert resource.name == "new_name_resource"
    mock_db_session.add.assert_called_with(resource)
