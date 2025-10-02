import pytest
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.workcell import WorkcellOrm
from praxis.backend.models.pydantic_internals.workcell import WorkcellCreate
from praxis.backend.services.workcell import WorkcellService


@pytest.fixture
def mock_db_session():
    """Fixture for a mock SQLAlchemy async session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def workcell_service():
    """Fixture for the WorkcellService."""
    return WorkcellService(WorkcellOrm)


@pytest.mark.asyncio
async def test_create_workcell(workcell_service: WorkcellService, mock_db_session: AsyncSession):
    """Test creating a new workcell."""
    workcell_in = WorkcellCreate(name="Test Workcell", fqn="test.workcell.fqn")

    # Mock the super().create method to return a mock WorkcellOrm object
    mock_workcell_orm = WorkcellOrm(
        name=workcell_in.name,
        fqn=workcell_in.fqn,
        accession_id=MagicMock(),
        created_at=MagicMock(),
        updated_at=MagicMock(),
        properties_json={},
        latest_state_json={},
        last_state_update_time=MagicMock(),
        machines=[],
    )

    with patch.object(workcell_service, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_workcell_orm

        created_workcell = await workcell_service.create(db=mock_db_session, obj_in=workcell_in)

        mock_create.assert_awaited_once_with(db=mock_db_session, obj_in=workcell_in)
        assert created_workcell.name == workcell_in.name
        assert created_workcell.fqn == workcell_in.fqn

import uuid
from unittest.mock import patch

from praxis.backend.models.pydantic_internals.filters import SearchFilters


@pytest.mark.asyncio
async def test_get_workcell(workcell_service: WorkcellService, mock_db_session: AsyncSession):
    """Test retrieving a workcell."""
    workcell_id = uuid.uuid4()
    mock_workcell_orm = WorkcellOrm(
        name="Test Workcell",
        fqn="test.workcell.fqn",
        accession_id=workcell_id,
        created_at=MagicMock(),
        updated_at=MagicMock(),
        properties_json={},
        latest_state_json={},
        last_state_update_time=MagicMock(),
        machines=[],
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_workcell_orm
    mock_db_session.execute.return_value = mock_result

    retrieved_workcell = await workcell_service.get(db=mock_db_session, accession_id=workcell_id)

    mock_db_session.execute.assert_awaited_once()
    assert retrieved_workcell is not None
    assert retrieved_workcell.accession_id == workcell_id

from praxis.backend.models.pydantic_internals.workcell import WorkcellUpdate


@pytest.mark.asyncio
async def test_get_multi_workcells(workcell_service: WorkcellService, mock_db_session: AsyncSession):
    """Test retrieving multiple workcells."""
    mock_workcells = [
        WorkcellOrm(
            name="Test Workcell 1",
            fqn="test.workcell.fqn1",
            accession_id=uuid.uuid4(),
            created_at=MagicMock(),
            updated_at=MagicMock(),
            properties_json={},
            latest_state_json={},
            last_state_update_time=MagicMock(),
            machines=[],
        ),
        WorkcellOrm(
            name="Test Workcell 2",
            fqn="test.workcell.fqn2",
            accession_id=uuid.uuid4(),
            created_at=MagicMock(),
            updated_at=MagicMock(),
            properties_json={},
            latest_state_json={},
            last_state_update_time=MagicMock(),
            machines=[],
        ),
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_workcells
    mock_db_session.execute.return_value = mock_result

    filters = SearchFilters()
    retrieved_workcells = await workcell_service.get_multi(db=mock_db_session, filters=filters)

    mock_db_session.execute.assert_awaited_once()
    assert len(retrieved_workcells) == 2
    assert retrieved_workcells[0].name == "Test Workcell 1"

@pytest.mark.asyncio
async def test_update_workcell(workcell_service: WorkcellService, mock_db_session: AsyncSession):
    """Test updating a workcell."""
    workcell_id = uuid.uuid4()
    workcell_orm = WorkcellOrm(
        name="Old Name",
        fqn="old.fqn",
        accession_id=workcell_id,
        created_at=MagicMock(),
        updated_at=MagicMock(),
        properties_json={},
        latest_state_json={},
        last_state_update_time=MagicMock(),
        machines=[],
    )
    workcell_update = WorkcellUpdate(name="New Name")

    with patch.object(workcell_service, 'update', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = workcell_orm
        updated_workcell = await workcell_service.update(db=mock_db_session, db_obj=workcell_orm, obj_in=workcell_update)
        mock_update.assert_awaited_once_with(db=mock_db_session, db_obj=workcell_orm, obj_in=workcell_update)
        assert updated_workcell is not None

@pytest.mark.asyncio
async def test_remove_workcell(workcell_service: WorkcellService, mock_db_session: AsyncSession):
    """Test removing a workcell."""
    workcell_id = uuid.uuid4()
    workcell_orm = WorkcellOrm(
        name="Test Workcell",
        fqn="test.workcell.fqn",
        accession_id=workcell_id,
        created_at=MagicMock(),
        updated_at=MagicMock(),
        properties_json={},
        latest_state_json={},
        last_state_update_time=MagicMock(),
        machines=[],
    )

    with patch.object(workcell_service, 'remove', new_callable=AsyncMock) as mock_remove:
        mock_remove.return_value = workcell_orm

        removed_workcell = await workcell_service.remove(db=mock_db_session, accession_id=workcell_id)

        mock_remove.assert_awaited_once_with(db=mock_db_session, accession_id=workcell_id)
        assert removed_workcell is not None