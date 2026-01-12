"""Unit tests for FunctionProtocolDefinitionmodel."""
import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.domain.protocol import (
    FunctionProtocolDefinition,
)
from praxis.backend.models.domain.protocol_source import (
    FileSystemProtocolSource,
    ProtocolSourceRepository,
)


@pytest_asyncio.fixture
async def git_source(db_session: AsyncSession) -> ProtocolSourceRepository:
    """Create a ProtocolSourceRepositoryfor testing."""
    source = ProtocolSourceRepository(
        name="test_git_source",
        git_url="https://github.com/example/protocols.git",
        default_ref="main",
    )
    db_session.add(source)
    await db_session.flush()
    return source


@pytest_asyncio.fixture
async def fs_source(db_session: AsyncSession) -> FileSystemProtocolSource:
    """Create a FileSystemProtocolSourcefor testing."""
    source = FileSystemProtocolSource(
        name="test_fs_source",
        base_path="/opt/protocols",
    )
    db_session.add(source)
    await db_session.flush()
    return source


@pytest.mark.asyncio
async def test_function_protocol_definition_orm_creation_minimal(
    db_session: AsyncSession,
) -> None:
    """Test creating FunctionProtocolDefinitionwith minimal required fields."""
    from praxis.backend.utils.uuid import uuid7

    protocol_id = uuid7()
    protocol = FunctionProtocolDefinition(
        name="test_protocol",
        fqn="test.protocols.test_protocol",
    )
    protocol.accession_id = protocol_id
    db_session.add(protocol)
    await db_session.flush()

    # Verify creation with defaults
    assert protocol.accession_id == protocol_id
    assert protocol.name == "test_protocol"
    assert protocol.fqn == "test.protocols.test_protocol"
    assert protocol.version == "0.1.0"  # Default
    assert protocol.description is None
    assert protocol.source_file_path == ""  # Default
    assert protocol.module_name == ""  # Default
    assert protocol.function_name == ""  # Default
    assert protocol.is_top_level is False  # Default
    assert protocol.solo_execution is False  # Default
    assert protocol.preconfigure_deck is False  # Default
    assert protocol.deprecated is False  # Default


@pytest.mark.asyncio
async def test_function_protocol_definition_orm_with_git_source(
    db_session: AsyncSession,
    git_source: ProtocolSourceRepository,
) -> None:
    """Test creating protocol definition linked to Git repository source."""
    from praxis.backend.utils.uuid import uuid7

    protocol_id = uuid7()
    protocol = FunctionProtocolDefinition(
        name="git_protocol",
        fqn="protocols.git_protocol",
        version="1.0.0",
        source_file_path="protocols/git_protocol.py",
        module_name="protocols",
        function_name="git_protocol",
        source_repository_accession_id=git_source.accession_id,
        commit_hash="abc123def456",
    )
    protocol.accession_id = protocol_id
    protocol.source_repository = git_source
    db_session.add(protocol)
    await db_session.flush()

    # Verify Git source linkage
    assert protocol.source_repository_accession_id == git_source.accession_id
    assert protocol.commit_hash == "abc123def456"
    assert protocol.file_system_source_accession_id is None


@pytest.mark.asyncio
async def test_function_protocol_definition_orm_with_fs_source(
    db_session: AsyncSession,
    fs_source: FileSystemProtocolSource,
) -> None:
    """Test creating protocol definition linked to file system source."""
    from praxis.backend.utils.uuid import uuid7

    protocol_id = uuid7()
    protocol = FunctionProtocolDefinition(
        name="fs_protocol",
        fqn="protocols.fs_protocol",
        version="2.0.0",
        source_file_path="library/fs_protocol.py",
        module_name="library",
        function_name="fs_protocol",
        file_system_source_accession_id=fs_source.accession_id,
    )
    protocol.accession_id = protocol_id
    protocol.file_system_source = fs_source
    db_session.add(protocol)
    await db_session.flush()

    # Verify file system source linkage
    assert protocol.file_system_source_accession_id == fs_source.accession_id
    assert protocol.source_repository_accession_id is None
    assert protocol.commit_hash is None


@pytest.mark.asyncio
async def test_function_protocol_definition_orm_persist_to_database(
    db_session: AsyncSession,
) -> None:
    """Test full persistence cycle for FunctionProtocolDefinition."""
    from praxis.backend.utils.uuid import uuid7

    protocol_id = uuid7()
    protocol = FunctionProtocolDefinition(
        name="persistence_protocol",
        fqn="test.protocols.persistence_protocol",
        version="1.0.0",
        description="Test protocol for persistence",
        source_file_path="test/persistence_protocol.py",
        module_name="test.protocols",
        function_name="persistence_protocol",
        is_top_level=True,
    )
    protocol.accession_id = protocol_id
    db_session.add(protocol)
    await db_session.flush()

    # Query back
    result = await db_session.execute(
        select(FunctionProtocolDefinition).where(
            FunctionProtocolDefinition.accession_id == protocol_id,
        ),
    )
    retrieved = result.scalars().first()

    # Verify persistence
    assert retrieved is not None
    assert retrieved.accession_id == protocol_id
    assert retrieved.name == "persistence_protocol"
    assert retrieved.fqn == "test.protocols.persistence_protocol"
    assert retrieved.version == "1.0.0"
    assert retrieved.description == "Test protocol for persistence"
    assert retrieved.is_top_level is True


@pytest.mark.asyncio
async def test_function_protocol_definition_orm_unique_constraint_git(
    db_session: AsyncSession,
    git_source: ProtocolSourceRepository,
) -> None:
    """Test unique constraint (name, version, source_repository, commit_hash)."""
    from praxis.backend.utils.uuid import uuid7

    # Create first protocol
    protocol1 = FunctionProtocolDefinition(
        name="unique_protocol",
        fqn="protocols.unique_protocol",
        version="1.0.0",
        source_repository_accession_id=git_source.accession_id,
        commit_hash="commit123",
    )
    protocol1.accession_id = uuid7()
    protocol1.source_repository = git_source
    db_session.add(protocol1)
    await db_session.flush()

    # Try to create another with same name, version, source, commit
    protocol2 = FunctionProtocolDefinition(
        name="unique_protocol",  # Same name
        fqn="protocols.unique_protocol_2",
        version="1.0.0",  # Same version
        source_repository_accession_id=git_source.accession_id,  # Same source
        commit_hash="commit123",  # Same commit
    )
    protocol2.accession_id = uuid7()
    protocol2.source_repository = git_source
    db_session.add(protocol2)

    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_function_protocol_definition_orm_unique_constraint_fs(
    db_session: AsyncSession,
    fs_source: FileSystemProtocolSource,
) -> None:
    """Test unique constraint (name, version, file_system_source, source_file_path)."""
    from praxis.backend.utils.uuid import uuid7

    # Create first protocol
    protocol1 = FunctionProtocolDefinition(
        name="unique_fs_protocol",
        fqn="protocols.unique_fs_protocol",
        version="1.0.0",
        file_system_source_accession_id=fs_source.accession_id,
        source_file_path="lib/unique.py",
    )
    protocol1.accession_id = uuid7()
    protocol1.file_system_source = fs_source
    db_session.add(protocol1)
    await db_session.flush()

    # Try to create another with same name, version, source, file path
    protocol2 = FunctionProtocolDefinition(
        name="unique_fs_protocol",  # Same name
        fqn="protocols.unique_fs_protocol_2",
        version="1.0.0",  # Same version
        file_system_source_accession_id=fs_source.accession_id,  # Same source
        source_file_path="lib/unique.py",  # Same file path
    )
    protocol2.accession_id = uuid7()
    protocol2.file_system_source = fs_source
    db_session.add(protocol2)

    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_function_protocol_definition_orm_is_top_level_flag(
    db_session: AsyncSession,
) -> None:
    """Test is_top_level flag for protocol execution."""
    from praxis.backend.utils.uuid import uuid7

    # Top-level protocol (can be executed directly)
    top_level = FunctionProtocolDefinition(
        name="top_level_protocol",
        fqn="protocols.top_level_protocol",
        is_top_level=True,
    )
    top_level.accession_id = uuid7()
    db_session.add(top_level)
    await db_session.flush()
    assert top_level.is_top_level is True

    # Helper protocol (not top-level)
    helper = FunctionProtocolDefinition(
        name="helper_protocol",
        fqn="protocols.helper_protocol",
        is_top_level=False,
    )
    helper.accession_id = uuid7()
    db_session.add(helper)
    await db_session.flush()
    assert helper.is_top_level is False


@pytest.mark.asyncio
async def test_function_protocol_definition_orm_solo_execution_flag(
    db_session: AsyncSession,
) -> None:
    """Test solo_execution flag for exclusive machine access."""
    from praxis.backend.utils.uuid import uuid7

    # Protocol requiring solo execution
    solo = FunctionProtocolDefinition(
        name="solo_protocol",
        fqn="protocols.solo_protocol",
        solo_execution=True,
    )
    solo.accession_id = uuid7()
    db_session.add(solo)
    await db_session.flush()
    assert solo.solo_execution is True

    # Protocol allowing concurrent execution
    concurrent = FunctionProtocolDefinition(
        name="concurrent_protocol",
        fqn="protocols.concurrent_protocol",
        solo_execution=False,
    )
    concurrent.accession_id = uuid7()
    db_session.add(concurrent)
    await db_session.flush()
    assert concurrent.solo_execution is False


@pytest.mark.asyncio
async def test_function_protocol_definition_orm_preconfigure_deck_flag(
    db_session: AsyncSession,
) -> None:
    """Test preconfigure_deck flag for deck setup."""
    from praxis.backend.utils.uuid import uuid7

    # Protocol with deck preconfiguration
    with_deck = FunctionProtocolDefinition(
        name="deck_protocol",
        fqn="protocols.deck_protocol",
        preconfigure_deck=True,
        deck_param_name="deck",
        deck_construction_function_fqn="protocols.setup_deck",
    )
    with_deck.accession_id = uuid7()
    db_session.add(with_deck)
    await db_session.flush()
    assert with_deck.preconfigure_deck is True
    assert with_deck.deck_param_name == "deck"
    assert with_deck.deck_construction_function_fqn == "protocols.setup_deck"


@pytest.mark.asyncio
async def test_function_protocol_definition_orm_deprecated_flag(
    db_session: AsyncSession,
) -> None:
    """Test deprecated flag for protocol versioning."""
    from praxis.backend.utils.uuid import uuid7

    # Deprecated protocol
    deprecated = FunctionProtocolDefinition(
        name="old_protocol",
        fqn="protocols.old_protocol",
        version="0.9.0",
        deprecated=True,
    )
    deprecated.accession_id = uuid7()
    db_session.add(deprecated)
    await db_session.flush()
    assert deprecated.deprecated is True

    # Active protocol
    active = FunctionProtocolDefinition(
        name="new_protocol",
        fqn="protocols.new_protocol",
        version="2.0.0",
        deprecated=False,
    )
    active.accession_id = uuid7()
    db_session.add(active)
    await db_session.flush()
    assert active.deprecated is False


@pytest.mark.asyncio
async def test_function_protocol_definition_orm_jsonb_tags(
    db_session: AsyncSession,
) -> None:
    """Test JSONB tags field for categorization."""
    from praxis.backend.utils.uuid import uuid7

    tags = {
        "category": "liquid_handling",
        "complexity": "advanced",
        "requires_calibration": True,
        "hardware": ["pipette", "plate_reader"],
    }

    protocol = FunctionProtocolDefinition(
        name="tagged_protocol",
        fqn="protocols.tagged_protocol",
        tags=tags,
        category="liquid_handling",
    )
    protocol.accession_id = uuid7()
    db_session.add(protocol)
    await db_session.flush()

    # Verify JSONB storage and retrieval
    assert protocol.tags == tags
    assert protocol.tags["category"] == "liquid_handling"
    assert protocol.tags["hardware"] == ["pipette", "plate_reader"]
    assert protocol.category == "liquid_handling"


@pytest.mark.asyncio
async def test_function_protocol_definition_orm_state_param(
    db_session: AsyncSession,
) -> None:
    """Test state_param_name for stateful protocols."""
    from praxis.backend.utils.uuid import uuid7

    protocol = FunctionProtocolDefinition(
        name="stateful_protocol",
        fqn="protocols.stateful_protocol",
        state_param_name="state",
    )
    protocol.accession_id = uuid7()
    db_session.add(protocol)
    await db_session.flush()
    assert protocol.state_param_name == "state"


@pytest.mark.asyncio
async def test_function_protocol_definition_orm_query_by_fqn(
    db_session: AsyncSession,
) -> None:
    """Test querying protocols by fully qualified name."""
    from praxis.backend.utils.uuid import uuid7

    protocol = FunctionProtocolDefinition(
        name="queryable_protocol",
        fqn="protocols.queryable.test_protocol",
    )
    protocol.accession_id = uuid7()
    db_session.add(protocol)
    await db_session.flush()

    # Query by FQN
    result = await db_session.execute(
        select(FunctionProtocolDefinition).where(
            FunctionProtocolDefinition.fqn == "protocols.queryable.test_protocol",
        ),
    )
    retrieved = result.scalars().first()

    assert retrieved is not None
    assert retrieved.name == "queryable_protocol"
    assert retrieved.fqn == "protocols.queryable.test_protocol"


@pytest.mark.asyncio
async def test_function_protocol_definition_orm_query_top_level(
    db_session: AsyncSession,
) -> None:
    """Test querying only top-level protocols."""
    from praxis.backend.utils.uuid import uuid7

    # Create top-level and helper protocols
    top_level1 = FunctionProtocolDefinition(
        name="top_level_1",
        fqn="protocols.top_level_1",
        is_top_level=True,
    )
    top_level1.accession_id = uuid7()
    top_level2 = FunctionProtocolDefinition(
        name="top_level_2",
        fqn="protocols.top_level_2",
        is_top_level=True,
    )
    top_level2.accession_id = uuid7()
    helper = FunctionProtocolDefinition(
        name="helper",
        fqn="protocols.helper",
        is_top_level=False,
    )
    helper.accession_id = uuid7()
    db_session.add(top_level1)
    db_session.add(top_level2)
    db_session.add(helper)
    await db_session.flush()

    # Query only top-level protocols
    result = await db_session.execute(
        select(FunctionProtocolDefinition).where(
            FunctionProtocolDefinition.is_top_level == True,  # noqa: E712
        ),
    )
    top_level_protocols = result.scalars().all()

    # Should find at least our 2 top-level protocols
    assert len(top_level_protocols) >= 2
    names = [p.name for p in top_level_protocols]
    assert "top_level_1" in names
    assert "top_level_2" in names


@pytest.mark.asyncio
async def test_function_protocol_definition_orm_repr(
    db_session: AsyncSession,
) -> None:
    """Test string representation of FunctionProtocolDefinition."""
    from praxis.backend.utils.uuid import uuid7

    protocol_id = uuid7()
    protocol = FunctionProtocolDefinition(
        name="repr_protocol",
        fqn="protocols.repr_protocol",
        version="1.5.0",
    )
    protocol.accession_id = protocol_id

    repr_str = repr(protocol)
    assert "FunctionProtocolDefinition" in repr_str
    assert str(protocol_id) in repr_str
    assert "repr_protocol" in repr_str
    assert "1.5.0" in repr_str
