import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.machine import MachineOrm
from praxis.backend.models.orm.resource import ResourceOrm, ResourceDefinitionOrm
from praxis.backend.models.orm.deck import DeckOrm
from praxis.backend.services import entity_linking


@pytest.fixture
def mock_db_session():
    """Fixture for a mocked async database session."""
    session = AsyncMock(spec=AsyncSession)
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.get = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def mock_machine_orm():
    """Fixture for a mocked MachineOrm."""
    machine = MagicMock(spec=MachineOrm)
    machine.accession_id = uuid.uuid4()
    machine.name = "Test Machine"
    machine.resource_counterpart = None
    machine.resource_counterpart_accession_id = None
    return machine


@pytest.fixture
def mock_resource_orm():
    """Fixture for a mocked ResourceOrm."""
    resource = MagicMock(spec=ResourceOrm)
    resource.accession_id = uuid.uuid4()
    resource.name = "Test Resource"
    resource.machine_counterpart = None
    return resource


@pytest.fixture
def mock_deck_orm():
    """Fixture for a mocked DeckOrm."""
    deck = MagicMock(spec=DeckOrm)
    deck.accession_id = uuid.uuid4()
    deck.name = "Test Deck"
    deck.resource_counterpart = None
    return deck


@pytest.fixture
def mock_resource_definition_orm():
    """Fixture for a mocked ResourceDefinitionOrm."""
    definition = MagicMock(spec=ResourceDefinitionOrm)
    definition.accession_id = uuid.uuid4()
    definition.name = "Test Definition"
    return definition


@pytest.mark.asyncio
@patch("praxis.backend.services.entity_linking._read_resource_definition_for_linking")
@patch("praxis.backend.models.ResourceOrm")
async def test_create_resource_counterpart_for_machine_success(
    mock_resource_orm_constructor,
    mock_read_def,
    mock_db_session,
    mock_machine_orm,
    mock_resource_definition_orm,
):
    """Test creating a new resource counterpart for a machine successfully."""
    mock_read_def.return_value = mock_resource_definition_orm
    mock_resource_instance = MagicMock()
    mock_resource_instance.accession_id = uuid.uuid4()
    mock_resource_orm_constructor.return_value = mock_resource_instance

    result = await entity_linking._create_or_link_resource_counterpart_for_machine(
        db=mock_db_session,
        machine_orm=mock_machine_orm,
        resource_counterpart_accession_id=None,
        resource_definition_name="Test Definition",
    )

    assert result is not None
    mock_db_session.add.assert_called()
    mock_db_session.flush.assert_awaited_once()
    assert mock_machine_orm.resource_counterpart_accession_id == result.accession_id


@pytest.mark.asyncio
async def test_link_resource_counterpart_for_machine_success(
    mock_db_session, mock_machine_orm, mock_resource_orm
):
    """Test linking an existing resource counterpart to a machine successfully."""
    mock_db_session.get.return_value = mock_resource_orm

    result = await entity_linking._create_or_link_resource_counterpart_for_machine(
        db=mock_db_session,
        machine_orm=mock_machine_orm,
        resource_counterpart_accession_id=mock_resource_orm.accession_id,
    )

    assert result == mock_resource_orm
    assert mock_machine_orm.resource_counterpart == mock_resource_orm


@pytest.mark.asyncio
async def test_create_resource_counterpart_no_definition_name_raises_error(
    mock_db_session, mock_machine_orm
):
    """Test that ValueError is raised if resource_definition_name is not provided."""
    with pytest.raises(
        ValueError, match="Cannot create new ResourceOrm: 'resource_definition_name' is required"
    ):
        await entity_linking._create_or_link_resource_counterpart_for_machine(
            db=mock_db_session,
            machine_orm=mock_machine_orm,
            resource_counterpart_accession_id=None,
        )


@pytest.mark.asyncio
async def test_link_resource_counterpart_not_found_raises_error(
    mock_db_session, mock_machine_orm
):
    """Test that ValueError is raised if the resource to link is not found."""
    mock_db_session.get.return_value = None
    with pytest.raises(ValueError, match="not found for linking"):
        await entity_linking._create_or_link_resource_counterpart_for_machine(
            db=mock_db_session,
            machine_orm=mock_machine_orm,
            resource_counterpart_accession_id=uuid.uuid4(),
        )


@pytest.mark.asyncio
@patch("praxis.backend.models.MachineOrm")
async def test_create_machine_counterpart_for_resource_success(
    mock_machine_orm_constructor, mock_db_session, mock_resource_orm
):
    """Test creating a new machine counterpart for a resource successfully."""
    mock_machine_instance = MagicMock()
    mock_machine_instance.accession_id = uuid.uuid4()
    mock_machine_orm_constructor.return_value = mock_machine_instance

    result = await entity_linking._create_or_link_machine_counterpart_for_resource(
        db=mock_db_session,
        resource_orm=mock_resource_orm,
        machine_name="New Machine",
        machine_fqn="new.machine.fqn",
    )

    assert result is not None
    mock_db_session.add.assert_called()
    mock_db_session.flush.assert_awaited_once()
    assert mock_resource_orm.machine_counterpart is not None


@pytest.mark.asyncio
async def test_link_machine_counterpart_for_resource_success(
    mock_db_session, mock_resource_orm, mock_machine_orm
):
    """Test linking an existing machine counterpart to a resource successfully."""
    mock_db_session.get.return_value = mock_machine_orm

    result = await entity_linking._create_or_link_machine_counterpart_for_resource(
        db=mock_db_session,
        resource_orm=mock_resource_orm,
        machine_counterpart_accession_id=mock_machine_orm.accession_id,
    )

    assert result == mock_machine_orm
    assert mock_resource_orm.machine_counterpart == mock_machine_orm


@pytest.mark.asyncio
async def test_create_machine_counterpart_no_name_or_fqn_raises_error(
    mock_db_session, mock_resource_orm
):
    """Test that ValueError is raised if machine_name or machine_fqn is not provided."""
    with pytest.raises(
        ValueError, match="Cannot create new MachineOrm: 'machine_name' and 'machine_fqn' are required"
    ):
        await entity_linking._create_or_link_machine_counterpart_for_resource(
            db=mock_db_session, resource_orm=mock_resource_orm
        )


@pytest.mark.asyncio
async def test_link_machine_counterpart_not_found_raises_error(
    mock_db_session, mock_resource_orm
):
    """Test that ValueError is raised if the machine to link is not found."""
    mock_db_session.get.return_value = None
    with pytest.raises(ValueError, match="not found for linking"):
        await entity_linking._create_or_link_machine_counterpart_for_resource(
            db=mock_db_session,
            resource_orm=mock_resource_orm,
            machine_counterpart_accession_id=uuid.uuid4(),
        )


@pytest.mark.asyncio
async def test_synchronize_machine_resource_names(mock_db_session, mock_machine_orm):
    """Test synchronizing names between a machine and its resource counterpart."""
    mock_resource = MagicMock(spec=ResourceOrm)
    mock_resource.name = "Old Name"
    mock_machine_orm.resource_counterpart = mock_resource
    mock_machine_orm.name = "New Name"

    await entity_linking.synchronize_machine_resource_names(
        db=mock_db_session, machine_orm=mock_machine_orm
    )

    assert mock_resource.name == "New Name"
    mock_db_session.add.assert_called_with(mock_resource)


@pytest.mark.asyncio
async def test_synchronize_resource_machine_names(mock_db_session, mock_resource_orm):
    """Test synchronizing names between a resource and its machine counterpart."""
    mock_machine = MagicMock(spec=MachineOrm)
    mock_machine.name = "Old Name"
    mock_resource_orm.machine_counterpart = mock_machine
    mock_resource_orm.name = "New Name"

    await entity_linking.synchronize_resource_machine_names(
        db=mock_db_session, resource_orm=mock_resource_orm
    )

    assert mock_machine.name == "New Name"
    mock_db_session.add.assert_called_with(mock_machine)


@pytest.mark.asyncio
async def test_synchronize_deck_resource_names(mock_db_session, mock_deck_orm):
    """Test synchronizing names between a deck and its resource counterpart."""
    mock_resource = MagicMock(spec=ResourceOrm)
    mock_resource.name = "Old Name"
    mock_deck_orm.resource_counterpart = mock_resource
    mock_deck_orm.name = "New Name"

    await entity_linking.synchronize_deck_resource_names(
        db=mock_db_session, deck_orm=mock_deck_orm
    )

    assert mock_resource.name == "New Name"
    mock_db_session.add.assert_called_with(mock_resource)


@pytest.mark.asyncio
async def test_synchronize_resource_deck_names(mock_db_session, mock_resource_orm):
    """Test synchronizing names between a resource and its deck counterpart."""
    mock_deck = MagicMock(spec=DeckOrm)
    mock_deck.name = "Old Name"
    mock_resource_orm.deck_counterpart = mock_deck
    mock_resource_orm.name = "New Name"

    await entity_linking.synchronize_resource_deck_names(
        db=mock_db_session, resource_orm=mock_resource_orm
    )

    assert mock_deck.name == "New Name"
    mock_db_session.add.assert_called_with(mock_deck)
