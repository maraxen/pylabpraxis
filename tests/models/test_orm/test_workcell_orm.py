"""Unit tests for WorkcellOrm model."""
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.workcell import WorkcellOrm
from praxis.backend.models.enums.workcell import WorkcellStatusEnum


@pytest.mark.asyncio
async def test_workcell_orm_creation_with_defaults(db_session: AsyncSession) -> None:
    """Test creating a WorkcellOrm with default values."""
    from praxis.backend.utils.uuid import uuid7

    # Create a workcell with only required fields
    workcell_id = uuid7()
    workcell = WorkcellOrm(
        accession_id=workcell_id,
        name="test_workcell"
    )

    # Verify defaults are set
    assert workcell.accession_id == workcell_id
    assert workcell.name == "test_workcell"
    assert workcell.status == WorkcellStatusEnum.AVAILABLE.value
    assert workcell.description is None
    assert workcell.physical_location is None
    assert workcell.latest_state_json is None


@pytest.mark.asyncio
async def test_workcell_orm_persist_to_database(db_session: AsyncSession) -> None:
    """Test that a WorkcellOrm can be persisted to the database."""
    from praxis.backend.utils.uuid import uuid7

    workcell_id = uuid7()
    workcell = WorkcellOrm(
        accession_id=workcell_id,
        name="test_persistence",
        description="A test workcell",
        physical_location="Lab 1"
    )

    # Add to session and flush
    db_session.add(workcell)
    await db_session.flush()

    # Query back from database
    result = await db_session.execute(
        select(WorkcellOrm).where(WorkcellOrm.accession_id == workcell_id)
    )
    retrieved = result.scalars().first()

    # Verify persistence
    assert retrieved is not None
    assert retrieved.accession_id == workcell_id
    assert retrieved.name == "test_persistence"
    assert retrieved.description == "A test workcell"
    assert retrieved.physical_location == "Lab 1"


@pytest.mark.asyncio
async def test_workcell_orm_unique_name_constraint(db_session: AsyncSession) -> None:
    """Test that workcell names must be unique."""
    from praxis.backend.utils.uuid import uuid7
    from sqlalchemy.exc import IntegrityError

    # Create first workcell
    workcell1 = WorkcellOrm(
        accession_id=uuid7(),
        name="unique_workcell"
    )
    db_session.add(workcell1)
    await db_session.flush()

    # Try to create another with same name
    workcell2 = WorkcellOrm(
        accession_id=uuid7(),
        name="unique_workcell"  # Duplicate name
    )
    db_session.add(workcell2)

    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_workcell_orm_relationships_empty_by_default(db_session: AsyncSession) -> None:
    """Test that relationship collections are empty by default."""
    from praxis.backend.utils.uuid import uuid7

    workcell = WorkcellOrm(
        accession_id=uuid7(),
        name="test_relationships"
    )

    # Relationships should be empty lists
    assert workcell.machines == []
    assert workcell.decks == []
    assert workcell.resources == []


@pytest.mark.asyncio
async def test_workcell_orm_with_custom_status(db_session: AsyncSession) -> None:
    """Test creating a workcell with a custom status."""
    from praxis.backend.utils.uuid import uuid7

    workcell = WorkcellOrm(
        accession_id=uuid7(),
        name="test_status",
        status=WorkcellStatusEnum.MAINTENANCE.value
    )

    db_session.add(workcell)
    await db_session.flush()

    # Verify status was set
    assert workcell.status == WorkcellStatusEnum.MAINTENANCE.value
