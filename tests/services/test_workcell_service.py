# pylint: disable=unused-argument, duplicate-code
"""Tests for the WorkcellService."""

import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.enums import AssetType
from praxis.backend.models.pydantic_internals.filters import SearchFilters
from praxis.backend.models.pydantic_internals.machine import MachineCreate
from praxis.backend.models.pydantic_internals.workcell import WorkcellCreate, WorkcellUpdate
from praxis.backend.services.machine import machine_service
from praxis.backend.services.workcell import workcell_service

# All tests in this module should be marked as asyncio
pytestmark = pytest.mark.asyncio


async def test_create_workcell_success(db_session: AsyncSession) -> None:
    """Test creating a workcell successfully."""
    workcell_in = WorkcellCreate(name="Test Workcell", fqn="test.workcell")
    workcell = await workcell_service.create(db_session, obj_in=workcell_in)
    assert workcell is not None
    assert workcell.name == "Test Workcell"
    assert workcell.fqn == "test.workcell"


async def test_get_workcell_by_id_exists(db_session: AsyncSession) -> None:
    """Test retrieving a workcell by its ID."""
    workcell_in = WorkcellCreate(name="Test Workcell", fqn="test.workcell")
    workcell = await workcell_service.create(db_session, obj_in=workcell_in)

    retrieved_workcell = await workcell_service.get(db_session, accession_id=workcell.accession_id)
    assert retrieved_workcell is not None
    assert retrieved_workcell.accession_id == workcell.accession_id


async def test_get_workcell_by_id_not_found(db_session: AsyncSession) -> None:
    """Test retrieving a workcell by a non-existent ID."""
    retrieved_workcell = await workcell_service.get(db_session, accession_id=uuid.uuid4())
    assert retrieved_workcell is None


async def test_get_multi_workcells_all(db_session: AsyncSession) -> None:
    """Test retrieving multiple workcells."""
    for i in range(5):
        workcell_in = WorkcellCreate(name=f"Test Workcell {i}", fqn=f"test.workcell.{i}")
        await workcell_service.create(db_session, obj_in=workcell_in)

    filters = SearchFilters(skip=0, limit=10)
    retrieved_workcells = await workcell_service.get_multi(db_session, filters=filters)
    assert len(retrieved_workcells) == 5


async def test_update_workcell_name(db_session: AsyncSession) -> None:
    """Test updating a workcell's name."""
    workcell_in = WorkcellCreate(name="Test Workcell", fqn="test.workcell")
    workcell = await workcell_service.create(db_session, obj_in=workcell_in)

    workcell_update = WorkcellUpdate(name="New Workcell Name")
    updated_workcell = await workcell_service.update(db_session, db_obj=workcell, obj_in=workcell_update)
    assert updated_workcell.name == "New Workcell Name"


async def test_delete_empty_workcell_succeeds(db_session: AsyncSession) -> None:
    """Test that empty workcell (no machines) can be deleted."""
    from sqlalchemy import select
    from praxis.backend.models.orm.workcell import WorkcellOrm

    workcell_in = WorkcellCreate(name="Test Workcell", fqn="test.workcell")
    workcell = await workcell_service.create(db_session, obj_in=workcell_in)
    workcell_id = workcell.accession_id

    result = await workcell_service.remove(db_session, accession_id=workcell_id)

    assert result is not None
    assert result.accession_id == workcell_id

    query_result = await db_session.execute(
        select(WorkcellOrm).where(WorkcellOrm.accession_id == workcell_id)
    )
    assert query_result.scalars().first() is None


async def test_create_workcell_duplicate_name(db_session: AsyncSession) -> None:
    """Test creating a workcell with a duplicate name."""
    workcell_in1 = WorkcellCreate(name="Test Workcell", fqn="test.workcell1")
    await workcell_service.create(db_session, obj_in=workcell_in1)

    workcell_in2 = WorkcellCreate(name="Test Workcell", fqn="test.workcell2")
    with pytest.raises(IntegrityError):
        await workcell_service.create(db_session, obj_in=workcell_in2)


async def test_read_workcell_state(db_session: AsyncSession) -> None:
    """Test reading a workcell's state."""
    workcell_in = WorkcellCreate(
        name="Test Workcell",
        fqn="test.workcell",
        latest_state_json={"setting": "value"},
    )
    workcell = await workcell_service.create(db_session, obj_in=workcell_in)

    state = await workcell_service.read_workcell_state(
        db_session,
        workcell_accession_id=workcell.accession_id,
    )
    assert state == {"setting": "value"}


async def test_read_workcell_state_not_found(db_session: AsyncSession) -> None:
    """Test reading a workcell's state when none is set."""
    workcell_in = WorkcellCreate(name="Test Workcell", fqn="test.workcell")
    workcell = await workcell_service.create(db_session, obj_in=workcell_in)

    state = await workcell_service.read_workcell_state(
        db_session,
        workcell_accession_id=workcell.accession_id,
    )
    assert state is None


async def test_workcell_configuration_updates(db_session: AsyncSession) -> None:
    """Test updating a workcell's configuration."""
    workcell_in = WorkcellCreate(name="Test Workcell", fqn="test.workcell")
    workcell = await workcell_service.create(db_session, obj_in=workcell_in)

    configuration = {"setting": "value"}
    updated_workcell = await workcell_service.update_workcell_state(
        db_session,
        workcell_accession_id=workcell.accession_id,
        state_json=configuration,
    )
    assert updated_workcell.latest_state_json == configuration


@pytest.mark.skip(
    reason=(
        "Blocked by known ORM issue: workcell_accession_id FK not persisting on MachineOrm. "
        "See test_machine_orm.py:142-187 for details. "
    )
)
async def test_delete_workcell_is_blocked_by_machine(db_session: AsyncSession) -> None:
    """Test that deleting a workcell with machines is blocked."""
    workcell_in = WorkcellCreate(name="Test Workcell", fqn="test.workcell")
    workcell = await workcell_service.create(db_session, obj_in=workcell_in)

    machine_in = MachineCreate(
        name="Test Machine",
        fqn="test.machine",
        workcell_accession_id=workcell.accession_id,
        asset_type=AssetType.MACHINE,
    )
    await machine_service.create(db_session, obj_in=machine_in)

    with pytest.raises(ValueError, match="has associated machines"):
        await workcell_service.remove(db_session, accession_id=workcell.accession_id)
