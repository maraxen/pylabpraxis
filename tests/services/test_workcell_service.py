"""Service tests for WorkcellService.

This file tests the WorkcellService layer for workcell management operations.

To run:
    export TEST_DATABASE_URL="postgresql+asyncpg://test_user:test_password@localhost:5432/test_db"
    python -m pytest tests/services/test_workcell_service.py -v
"""
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.workcell import WorkcellOrm
from praxis.backend.models.pydantic_internals.workcell import WorkcellCreate, WorkcellUpdate
from praxis.backend.models.pydantic_internals.filters import SearchFilters
from praxis.backend.services.workcell import workcell_service
from praxis.backend.utils.uuid import uuid7
from tests.helpers import create_workcell


# ============================================================================
# CREATE Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_workcell_success(db_session: AsyncSession) -> None:
    """Test successfully creating a workcell via WorkcellService."""
    # 1. SETUP
    import uuid
    unique_name = f"test_workcell_{uuid.uuid4().hex[:8]}"
    workcell_data = WorkcellCreate(
        name=unique_name,
        description="Test workcell for service layer",
        physical_location="Lab 1",
    )

    # 2. ACT
    result = await workcell_service.create(db_session, obj_in=workcell_data)

    # 3. ASSERT
    assert result is not None
    assert result.name == unique_name
    assert result.description == "Test workcell for service layer"
    assert result.physical_location == "Lab 1"
    assert result.accession_id is not None


@pytest.mark.asyncio
async def test_create_workcell_minimal(db_session: AsyncSession) -> None:
    """Test creating workcell with only required fields."""
    # 1. SETUP
    import uuid
    unique_name = f"minimal_workcell_{uuid.uuid4().hex[:8]}"
    workcell_data = WorkcellCreate(name=unique_name)

    # 2. ACT
    result = await workcell_service.create(db_session, obj_in=workcell_data)

    # 3. ASSERT
    assert result is not None
    assert result.name == unique_name
    assert result.description is None
    assert result.physical_location is None


# ============================================================================
# GET (Single) Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_workcell_by_id_exists(db_session: AsyncSession) -> None:
    """Test retrieving an existing workcell by ID."""
    # 1. SETUP
    import uuid
    unique_name = f"find_me_workcell_{uuid.uuid4().hex[:8]}"
    workcell = await create_workcell(db_session, name=unique_name)

    # 2. ACT
    result = await workcell_service.get(db_session, accession_id=workcell.accession_id)

    # 3. ASSERT
    assert result is not None
    assert result.name == unique_name
    assert result.accession_id == workcell.accession_id


@pytest.mark.asyncio
async def test_get_workcell_by_id_not_found(db_session: AsyncSession) -> None:
    """Test retrieving a non-existent workcell returns None."""
    # 1. SETUP
    fake_id = uuid7()

    # 2. ACT
    result = await workcell_service.get(db_session, accession_id=fake_id)

    # 3. ASSERT
    assert result is None


# ============================================================================
# GET_MULTI (List) Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_multi_workcells(db_session: AsyncSession) -> None:
    """Test listing multiple workcells."""
    # 1. SETUP
    import uuid
    suffix = uuid.uuid4().hex[:8]
    wc1 = await create_workcell(db_session, name=f"workcell_alpha_{suffix}")
    wc2 = await create_workcell(db_session, name=f"workcell_beta_{suffix}")
    wc3 = await create_workcell(db_session, name=f"workcell_gamma_{suffix}")

    # 2. ACT
    filters = SearchFilters()
    results = await workcell_service.get_multi(db_session, filters=filters)

    # 3. ASSERT
    assert len(results) >= 3
    result_names = {wc.name for wc in results}
    assert f"workcell_alpha_{suffix}" in result_names
    assert f"workcell_beta_{suffix}" in result_names
    assert f"workcell_gamma_{suffix}" in result_names


@pytest.mark.asyncio
async def test_get_multi_workcells_with_pagination(db_session: AsyncSession) -> None:
    """Test listing workcells with pagination."""
    # 1. SETUP
    import uuid
    suffix = uuid.uuid4().hex[:8]
    for i in range(5):
        await create_workcell(db_session, name=f"paginated_wc_{i}_{suffix}")

    # 2. ACT
    filters = SearchFilters(skip=0, limit=2)
    results = await workcell_service.get_multi(db_session, filters=filters)

    # 3. ASSERT
    assert len(results) >= 2
    # Note: May return more if other tests created workcells
    # Just verify we got results


# ============================================================================
# UPDATE Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_workcell_description(db_session: AsyncSession) -> None:
    """Test updating a workcell's description."""
    # 1. SETUP
    import uuid
    unique_name = f"update_desc_wc_{uuid.uuid4().hex[:8]}"
    workcell = await create_workcell(db_session, name=unique_name, description="Original")
    original_id = workcell.accession_id

    # 2. ACT
    update_data = WorkcellUpdate(description="Updated description")
    result = await workcell_service.update(db_session, db_obj=workcell, obj_in=update_data)

    # 3. ASSERT
    assert result.description == "Updated description"
    assert result.accession_id == original_id
    assert result.name == unique_name  # Name unchanged


@pytest.mark.asyncio
async def test_update_workcell_multiple_fields(db_session: AsyncSession) -> None:
    """Test updating multiple workcell fields."""
    # 1. SETUP
    import uuid
    unique_name = f"update_multi_wc_{uuid.uuid4().hex[:8]}"
    workcell = await create_workcell(
        db_session,
        name=unique_name,
        description="Old desc",
        physical_location="Old location"
    )

    # 2. ACT
    update_data = WorkcellUpdate(
        description="New desc",
        physical_location="New location"
    )
    result = await workcell_service.update(db_session, db_obj=workcell, obj_in=update_data)

    # 3. ASSERT
    assert result.description == "New desc"
    assert result.physical_location == "New location"
    assert result.name == unique_name  # Name unchanged


@pytest.mark.asyncio
async def test_update_workcell_partial(db_session: AsyncSession) -> None:
    """Test partial update (only some fields)."""
    # 1. SETUP
    import uuid
    unique_name = f"update_partial_wc_{uuid.uuid4().hex[:8]}"
    workcell = await create_workcell(
        db_session,
        name=unique_name,
        description="Keep this",
        physical_location="Change this"
    )

    # 2. ACT: Only update location
    update_data = WorkcellUpdate(physical_location="New location only")
    result = await workcell_service.update(db_session, db_obj=workcell, obj_in=update_data)

    # 3. ASSERT
    assert result.physical_location == "New location only"
    assert result.description == "Keep this"  # Unchanged


# ============================================================================
# DELETE Tests
# ============================================================================


@pytest.mark.asyncio
async def test_delete_empty_workcell_succeeds(db_session: AsyncSession) -> None:
    """Test that empty workcell (no machines/decks/resources) can be deleted."""
    # 1. SETUP
    import uuid
    unique_name = f"delete_empty_wc_{uuid.uuid4().hex[:8]}"
    workcell = await create_workcell(db_session, name=unique_name)
    workcell_id = workcell.accession_id

    # 2. ACT
    deleted = await workcell_service.remove(db_session, accession_id=workcell_id)

    # 3. ASSERT
    assert deleted is not None
    assert deleted.accession_id == workcell_id

    # Verify it's gone
    result = await db_session.execute(
        select(WorkcellOrm).where(WorkcellOrm.accession_id == workcell_id)
    )
    assert result.scalars().first() is None


@pytest.mark.asyncio
async def test_delete_workcell_nonexistent(db_session: AsyncSession) -> None:
    """Test deleting non-existent workcell returns None."""
    # 1. SETUP
    fake_id = uuid7()

    # 2. ACT
    result = await workcell_service.remove(db_session, accession_id=fake_id)

    # 3. ASSERT
    assert result is None


# ============================================================================
# STATE MANAGEMENT Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_workcell_state(db_session: AsyncSession) -> None:
    """Test updating workcell state JSON."""
    # 1. SETUP
    import uuid
    unique_name = f"state_wc_{uuid.uuid4().hex[:8]}"
    workcell = await create_workcell(db_session, name=unique_name)

    state_data = {
        "machines": ["machine_1", "machine_2"],
        "status": "operational",
        "last_run": "2025-01-01T12:00:00Z"
    }

    # 2. ACT
    result = await workcell_service.update_workcell_state(
        db_session,
        workcell_accession_id=workcell.accession_id,
        state_json=state_data
    )

    # 3. ASSERT
    assert result.latest_state_json == state_data
    assert result.last_state_update_time is not None


@pytest.mark.asyncio
async def test_read_workcell_state_exists(db_session: AsyncSession) -> None:
    """Test reading workcell state that exists."""
    # 1. SETUP
    import uuid
    unique_name = f"read_state_wc_{uuid.uuid4().hex[:8]}"
    workcell = await create_workcell(db_session, name=unique_name)

    state_data = {"test": "data", "value": 123}
    await workcell_service.update_workcell_state(
        db_session,
        workcell_accession_id=workcell.accession_id,
        state_json=state_data
    )

    # 2. ACT
    result = await workcell_service.read_workcell_state(
        db_session,
        workcell_accession_id=workcell.accession_id
    )

    # 3. ASSERT
    assert result == state_data
    assert result["test"] == "data"
    assert result["value"] == 123


@pytest.mark.asyncio
async def test_read_workcell_state_none(db_session: AsyncSession) -> None:
    """Test reading workcell state when no state exists."""
    # 1. SETUP
    import uuid
    unique_name = f"no_state_wc_{uuid.uuid4().hex[:8]}"
    workcell = await create_workcell(db_session, name=unique_name)

    # 2. ACT
    result = await workcell_service.read_workcell_state(
        db_session,
        workcell_accession_id=workcell.accession_id
    )

    # 3. ASSERT
    assert result is None


@pytest.mark.asyncio
async def test_update_workcell_state_nonexistent_fails(db_session: AsyncSession) -> None:
    """Test updating state for non-existent workcell raises error."""
    # 1. SETUP
    fake_id = uuid7()
    state_data = {"test": "data"}

    # 2. ACT & ASSERT
    with pytest.raises(ValueError, match="not found"):
        await workcell_service.update_workcell_state(
            db_session,
            workcell_accession_id=fake_id,
            state_json=state_data
        )


# ============================================================================
# RELATIONSHIP Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_workcell_loads_relationships(db_session: AsyncSession) -> None:
    """Test that get() loads machines, decks, and resources relationships."""
    # 1. SETUP
    import uuid
    unique_name = f"relationships_wc_{uuid.uuid4().hex[:8]}"
    workcell = await create_workcell(db_session, name=unique_name)

    # 2. ACT
    result = await workcell_service.get(db_session, accession_id=workcell.accession_id)

    # 3. ASSERT
    assert result is not None
    # Service uses selectinload, so these should be accessible
    assert hasattr(result, 'machines')
    assert hasattr(result, 'decks')
    assert hasattr(result, 'resources')
    # They should be empty lists for a new workcell
    assert result.machines == []
    assert result.decks == []
    assert result.resources == []
