import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.services.workcell import workcell_service
from praxis.backend.models.pydantic_internals.workcell import WorkcellCreate, WorkcellUpdate
from praxis.backend.models.pydantic_internals.filters import SearchFilters
from praxis.backend.models.enums.workcell import WorkcellStatusEnum

@pytest.mark.asyncio
async def test_create_workcell(db_session: AsyncSession):
    """Test creating a new workcell."""
    workcell_in = WorkcellCreate(
        name="Test Workcell",
        description="A test workcell",
        physical_location="Lab 1",
        status=WorkcellStatusEnum.AVAILABLE
    )
    workcell = await workcell_service.create(db=db_session, obj_in=workcell_in)

    assert workcell.name == "Test Workcell"
    assert workcell.accession_id is not None
    assert workcell.created_at is not None

@pytest.mark.asyncio
async def test_get_workcell(db_session: AsyncSession):
    """Test retrieving a workcell by ID."""
    workcell_in = WorkcellCreate(name="Get Workcell")
    created_workcell = await workcell_service.create(db=db_session, obj_in=workcell_in)

    retrieved_workcell = await workcell_service.get(db=db_session, accession_id=created_workcell.accession_id)
    assert retrieved_workcell is not None
    assert retrieved_workcell.accession_id == created_workcell.accession_id
    assert retrieved_workcell.name == "Get Workcell"

@pytest.mark.asyncio
async def test_get_multi_workcells(db_session: AsyncSession):
    """Test listing workcells."""
    # Create two workcells
    await workcell_service.create(db=db_session, obj_in=WorkcellCreate(name="Workcell A"))
    await workcell_service.create(db=db_session, obj_in=WorkcellCreate(name="Workcell B"))

    filters = SearchFilters()
    workcells = await workcell_service.get_multi(db=db_session, filters=filters)

    assert len(workcells) >= 2
    names = [w.name for w in workcells]
    assert "Workcell A" in names
    assert "Workcell B" in names

@pytest.mark.asyncio
async def test_update_workcell(db_session: AsyncSession):
    """Test updating a workcell."""
    workcell_in = WorkcellCreate(name="Update Workcell", status=WorkcellStatusEnum.AVAILABLE)
    created_workcell = await workcell_service.create(db=db_session, obj_in=workcell_in)

    update_data = WorkcellUpdate(name="Updated Name", status=WorkcellStatusEnum.ERROR)
    updated_workcell = await workcell_service.update(
        db=db_session,
        db_obj=created_workcell,
        obj_in=update_data
    )

    assert updated_workcell.name == "Updated Name"
    assert updated_workcell.status == WorkcellStatusEnum.ERROR.value

    # Verify persistence
    refetched = await workcell_service.get(db=db_session, accession_id=created_workcell.accession_id)
    assert refetched.name == "Updated Name"
    assert refetched.status == WorkcellStatusEnum.ERROR.value

@pytest.mark.asyncio
async def test_remove_workcell(db_session: AsyncSession):
    """Test removing a workcell."""
    workcell_in = WorkcellCreate(name="Remove Workcell")
    created_workcell = await workcell_service.create(db=db_session, obj_in=workcell_in)

    removed = await workcell_service.remove(db=db_session, accession_id=created_workcell.accession_id)
    assert removed is not None
    assert removed.accession_id == created_workcell.accession_id

    # Verify it's gone
    retrieved = await workcell_service.get(db=db_session, accession_id=created_workcell.accession_id)
    assert retrieved is None

@pytest.mark.asyncio
async def test_remove_non_existent_workcell(db_session: AsyncSession):
    """Test removing a non-existent workcell."""
    non_existent_id = uuid.uuid4()
    result = await workcell_service.remove(db=db_session, accession_id=non_existent_id)
    assert result is None

@pytest.mark.asyncio
async def test_workcell_state_operations(db_session: AsyncSession):
    """Test reading and updating workcell state."""
    workcell_in = WorkcellCreate(name="State Workcell")
    created_workcell = await workcell_service.create(db=db_session, obj_in=workcell_in)

    # Initial state should be None or empty depending on model default,
    # but let's check read_workcell_state behavior
    initial_state = await workcell_service.read_workcell_state(
        db=db_session,
        workcell_accession_id=created_workcell.accession_id
    )
    assert initial_state is None

    # Update state
    new_state = {"key": "value", "status": "ok"}
    updated = await workcell_service.update_workcell_state(
        db=db_session,
        workcell_accession_id=created_workcell.accession_id,
        state_json=new_state
    )
    assert updated.latest_state_json == new_state
    assert updated.last_state_update_time is not None

    # Read state again
    read_state = await workcell_service.read_workcell_state(
        db=db_session,
        workcell_accession_id=created_workcell.accession_id
    )
    assert read_state == new_state

@pytest.mark.asyncio
async def test_update_workcell_state_not_found(db_session: AsyncSession):
    """Test updating state for non-existent workcell raises ValueError."""
    non_existent_id = uuid.uuid4()
    with pytest.raises(ValueError, match=f"WorkcellOrm with ID {non_existent_id} not found"):
        await workcell_service.update_workcell_state(
            db=db_session,
            workcell_accession_id=non_existent_id,
            state_json={"a": 1}
        )
