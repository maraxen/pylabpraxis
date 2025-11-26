"""Unit tests for FileSystemProtocolSourceOrm model."""
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.enums import ProtocolSourceStatusEnum
from praxis.backend.models.orm.protocol import FileSystemProtocolSourceOrm


@pytest.mark.asyncio
async def test_file_system_protocol_source_orm_creation_minimal(
    db_session: AsyncSession,
) -> None:
    """Test creating FileSystemProtocolSourceOrm with minimal required fields."""
    from praxis.backend.utils.uuid import uuid7

    source_id = uuid7()
    source = FileSystemProtocolSourceOrm(
        accession_id=source_id,
        name="test_fs_source",
    )
    db_session.add(source)
    await db_session.flush()

    # Verify creation
    assert source.accession_id == source_id
    assert source.name == "test_fs_source"
    assert source.base_path == ""  # Default
    assert source.is_recursive is True  # Default
    assert source.status == ProtocolSourceStatusEnum.ACTIVE  # Default


@pytest.mark.asyncio
async def test_file_system_protocol_source_orm_creation_with_all_fields(
    db_session: AsyncSession,
) -> None:
    """Test creating FileSystemProtocolSourceOrm with all fields populated."""
    from praxis.backend.utils.uuid import uuid7

    source_id = uuid7()
    source = FileSystemProtocolSourceOrm(
        accession_id=source_id,
        name="full_fs_source",
        base_path="/opt/protocols/library",
        is_recursive=False,
        status=ProtocolSourceStatusEnum.INACTIVE,
    )
    db_session.add(source)
    await db_session.flush()

    # Verify all fields
    assert source.accession_id == source_id
    assert source.name == "full_fs_source"
    assert source.base_path == "/opt/protocols/library"
    assert source.is_recursive is False
    assert source.status == ProtocolSourceStatusEnum.INACTIVE


@pytest.mark.asyncio
async def test_file_system_protocol_source_orm_persist_to_database(
    db_session: AsyncSession,
) -> None:
    """Test full persistence cycle for FileSystemProtocolSourceOrm."""
    from praxis.backend.utils.uuid import uuid7

    source_id = uuid7()
    source = FileSystemProtocolSourceOrm(
        accession_id=source_id,
        name="persistence_test_fs",
        base_path="/var/protocols/test",
        is_recursive=True,
    )
    db_session.add(source)
    await db_session.flush()

    # Query back
    result = await db_session.execute(
        select(FileSystemProtocolSourceOrm).where(
            FileSystemProtocolSourceOrm.accession_id == source_id,
        ),
    )
    retrieved = result.scalars().first()

    # Verify persistence
    assert retrieved is not None
    assert retrieved.accession_id == source_id
    assert retrieved.name == "persistence_test_fs"
    assert retrieved.base_path == "/var/protocols/test"
    assert retrieved.is_recursive is True


@pytest.mark.asyncio
async def test_file_system_protocol_source_orm_unique_name_constraint(
    db_session: AsyncSession,
) -> None:
    """Test that name must be unique."""
    from sqlalchemy.exc import IntegrityError

    from praxis.backend.utils.uuid import uuid7

    # Create first source
    source1 = FileSystemProtocolSourceOrm(
        accession_id=uuid7(),
        name="unique_fs_name",
        base_path="/opt/protocols/source1",
    )
    db_session.add(source1)
    await db_session.flush()

    # Try to create another with same name
    source2 = FileSystemProtocolSourceOrm(
        accession_id=uuid7(),
        name="unique_fs_name",  # Duplicate name
        base_path="/opt/protocols/source2",
    )
    db_session.add(source2)

    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_file_system_protocol_source_orm_status_transitions(
    db_session: AsyncSession,
) -> None:
    """Test different status values for file system protocol source."""
    from praxis.backend.utils.uuid import uuid7

    statuses = [
        (ProtocolSourceStatusEnum.ACTIVE, "active_fs"),
        (ProtocolSourceStatusEnum.SYNCING, "syncing_fs"),
        (ProtocolSourceStatusEnum.ERROR, "error_fs"),
        (ProtocolSourceStatusEnum.INACTIVE, "inactive_fs"),
    ]

    for status, name in statuses:
        source = FileSystemProtocolSourceOrm(
            accession_id=uuid7(),
            name=name,
            base_path=f"/opt/protocols/{name}",
            status=status,
        )
        db_session.add(source)
        await db_session.flush()

        # Verify status
        assert source.status == status


@pytest.mark.asyncio
async def test_file_system_protocol_source_orm_is_recursive_flag(
    db_session: AsyncSession,
) -> None:
    """Test is_recursive flag for scanning subdirectories."""
    from praxis.backend.utils.uuid import uuid7

    # Source with recursive scanning (default)
    recursive_source = FileSystemProtocolSourceOrm(
        accession_id=uuid7(),
        name="recursive_fs",
        base_path="/opt/protocols/recursive",
        is_recursive=True,
    )
    db_session.add(recursive_source)
    await db_session.flush()
    assert recursive_source.is_recursive is True

    # Source without recursive scanning
    non_recursive_source = FileSystemProtocolSourceOrm(
        accession_id=uuid7(),
        name="non_recursive_fs",
        base_path="/opt/protocols/non_recursive",
        is_recursive=False,
    )
    db_session.add(non_recursive_source)
    await db_session.flush()
    assert non_recursive_source.is_recursive is False


@pytest.mark.asyncio
async def test_file_system_protocol_source_orm_query_by_name(
    db_session: AsyncSession,
) -> None:
    """Test querying sources by name."""
    from praxis.backend.utils.uuid import uuid7

    source = FileSystemProtocolSourceOrm(
        accession_id=uuid7(),
        name="queryable_fs",
        base_path="/opt/protocols/queryable",
    )
    db_session.add(source)
    await db_session.flush()

    # Query by name
    result = await db_session.execute(
        select(FileSystemProtocolSourceOrm).where(
            FileSystemProtocolSourceOrm.name == "queryable_fs",
        ),
    )
    retrieved = result.scalars().first()

    assert retrieved is not None
    assert retrieved.name == "queryable_fs"
    assert retrieved.base_path == "/opt/protocols/queryable"


@pytest.mark.asyncio
async def test_file_system_protocol_source_orm_update_base_path(
    db_session: AsyncSession,
) -> None:
    """Test updating base_path field."""
    from praxis.backend.utils.uuid import uuid7

    source_id = uuid7()
    source = FileSystemProtocolSourceOrm(
        accession_id=source_id,
        name="path_update_fs",
        base_path="/opt/protocols/old_path",
    )
    db_session.add(source)
    await db_session.flush()

    # Initially old path
    assert source.base_path == "/opt/protocols/old_path"

    # Update base path
    source.base_path = "/opt/protocols/new_path"
    await db_session.flush()

    # Query back and verify update
    result = await db_session.execute(
        select(FileSystemProtocolSourceOrm).where(
            FileSystemProtocolSourceOrm.accession_id == source_id,
        ),
    )
    retrieved = result.scalars().first()
    assert retrieved.base_path == "/opt/protocols/new_path"


@pytest.mark.asyncio
async def test_file_system_protocol_source_orm_repr(db_session: AsyncSession) -> None:
    """Test string representation of FileSystemProtocolSourceOrm."""
    from praxis.backend.utils.uuid import uuid7

    source_id = uuid7()
    source = FileSystemProtocolSourceOrm(
        accession_id=source_id,
        name="repr_fs",
        base_path="/opt/protocols/repr",
    )

    repr_str = repr(source)
    assert "FileSystemProtocolSourceOrm" in repr_str
    assert str(source_id) in repr_str
    assert "repr_fs" in repr_str
    assert "/opt/protocols/repr" in repr_str


@pytest.mark.asyncio
async def test_file_system_protocol_source_orm_query_by_status(
    db_session: AsyncSession,
) -> None:
    """Test querying sources by status."""
    from praxis.backend.utils.uuid import uuid7

    # Create sources with different statuses
    active_source = FileSystemProtocolSourceOrm(
        accession_id=uuid7(),
        name="active_status_fs",
        base_path="/opt/protocols/active",
        status=ProtocolSourceStatusEnum.ACTIVE,
    )
    inactive_source = FileSystemProtocolSourceOrm(
        accession_id=uuid7(),
        name="inactive_status_fs",
        base_path="/opt/protocols/inactive",
        status=ProtocolSourceStatusEnum.INACTIVE,
    )
    db_session.add(active_source)
    db_session.add(inactive_source)
    await db_session.flush()

    # Query for active sources
    result = await db_session.execute(
        select(FileSystemProtocolSourceOrm).where(
            FileSystemProtocolSourceOrm.status == ProtocolSourceStatusEnum.ACTIVE,
        ),
    )
    active_sources = result.scalars().all()

    # Should find at least our active source
    assert len(active_sources) >= 1
    assert any(s.name == "active_status_fs" for s in active_sources)
