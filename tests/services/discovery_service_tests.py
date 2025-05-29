# tests/services/test_discovery_service.py
import asyncio
import pytest
import pytest_asyncio
import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, Tuple # Added for type hints
from unittest.mock import AsyncMock, patch, MagicMock, call # Added call

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncpg # For mock_asyncpg_pool

from praxis.backend.utils.db import Base as PraxisBase
from praxis.backend.services.discovery_service import ProtocolDiscoveryService
from praxis.backend.services.praxis_orm_service import PraxisDBService # Keep for mock_praxis_db_service
from praxis.backend.database_models import (
    ProtocolSourceRepositoryOrm,
    FileSystemProtocolSourceOrm,
    FunctionProtocolDefinitionOrm, # ORM model for DB
    UserOrm
)
# Using the Pydantic models for definitions as used in DiscoveryService
from praxis.backend.protocol_core.protocol_definition_models import (
    UIHint,
    ParameterMetadataModel,
    AssetRequirementModel,
    FunctionProtocolDefinitionModel
)
# Import decorators and other core definitions if needed for creating test content
from praxis.backend.protocol_core.decorators import protocol_function
from praxis.backend.protocol_core.definitions import PraxisState, PlrDeck, PlrResource


ASYNC_SQLITE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="function")
async def async_engine():
    engine = create_async_engine(ASYNC_SQLITE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(PraxisBase.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(PraxisBase.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session(async_engine):
    async_session_local = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_local() as session: # type: ignore
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def mock_asyncpg_pool():
    """Mocks the asyncpg connection pool and its connections."""
    mock_pool = AsyncMock(spec=asyncpg.Pool)
    mock_conn = AsyncMock(spec=asyncpg.Connection)

    acquire_cm = AsyncMock()
    acquire_cm.__aenter__.return_value = mock_conn
    acquire_cm.__aexit__.return_value = None
    mock_pool.acquire.return_value = acquire_cm

    mock_pool.release = AsyncMock()
    mock_conn.execute = AsyncMock()
    mock_conn.fetch = AsyncMock(return_value=[])
    mock_pool._closed = False
    return mock_pool


@pytest_asyncio.fixture
async def mock_praxis_db_service(db_session, mock_asyncpg_pool):
    """Mocks PraxisDBService for testing DiscoveryService."""
    with patch("praxis.backend.services.praxis_orm_service.PraxisDBService.initialize", new_callable=AsyncMock) as mock_init, \
         patch("praxis.backend.services.praxis_orm_service.PraxisDBService.get_praxis_session") as mock_get_session:

        mock_session_cm = AsyncMock()
        mock_session_cm.__aenter__.return_value = db_session
        mock_session_cm.__aexit__.return_value = None
        mock_get_session.return_value = mock_session_cm

        # If DiscoveryService instantiates PraxisDBService or calls its class methods:
        # Patch the class itself or its relevant methods if necessary.
        # For now, assuming DiscoveryService primarily uses get_praxis_session from an instance.

        # Create a mock instance that will be implicitly used if DiscoveryService creates one
        # or explicitly if we inject it.
        # The key is that `get_praxis_session` is patched.
        # We can also mock the `initialize` if DiscoveryService calls it.

        # To ensure that if DiscoveryService creates its own instance, it's properly managed:
        # We can patch the __new__ or __init__ of PraxisDBService if it's complex,
        # but patching `get_praxis_session` globally for the service class might be enough.

        # Let's assume DiscoveryService might create an instance of PraxisDBService.
        # The patched methods will apply to any instance created during the patch scope.

        # If DiscoveryService gets PraxisDBService injected or as a singleton,
        # this mock setup needs to align with that.
        # For now, the patch on `PraxisDBService.get_praxis_session` should cover
        # cases where DiscoveryService obtains a session through an instance of PraxisDBService.

        # We yield None because the patches are the important part for how DiscoveryService
        # will interact with a (mocked) PraxisDBService session.
        # If DiscoveryService takes a `db_service` instance in its constructor, then we'd yield a mock instance.
        yield None # The patches are active


@pytest_asyncio.fixture
async def discovery_service(db_session: AsyncSession, mock_praxis_db_service): # mock_praxis_db_service ensures patches are active
    """
    Provides an instance of ProtocolDiscoveryService.
    Relies on mock_praxis_db_service to ensure that if ProtocolDiscoveryService
    uses PraxisDBService for sessions, it gets the mocked session.
    """
    # The ProtocolDiscoveryService constructor in the actual code seems to take `db_session=None`
    # and then potentially uses a global or internal PraxisDBService instance.
    # The patches in `mock_praxis_db_service` should cover `PraxisDBService.get_praxis_session`.
    service = ProtocolDiscoveryService(db_session=db_session) # Pass the actual test session

    # If ProtocolDiscoveryService has an `initialize_discovery` method that sets up DB connections
    # or interacts with PraxisDBService, ensure it's compatible with the mocks.
    # For example, if it calls PraxisDBService.initialize(), that's mocked by mock_praxis_db_service.
    if hasattr(service, 'initialize_discovery') and asyncio.iscoroutinefunction(service.initialize_discovery):
        await service.initialize_discovery()
    elif hasattr(service, 'initialize_discovery'):
        service.initialize_discovery()

    return service

# Helper to create a mock ORM object similar to what upsert might return
def create_mock_protocol_orm_obj(id_val,
                                  pydantic_def: FunctionProtocolDefinitionModel, source_repo_id=None, fs_source_id=None):
    return MagicMock(
        spec=FunctionProtocolDefinitionOrm,
        id=id_val,
        name=pydantic_def.name,
        version=pydantic_def.version,
        module_name=pydantic_def.module_name,
        function_name=pydantic_def.function_name,
        description=pydantic_def.description,
        is_top_level=pydantic_def.is_top_level,
        source_file_path=pydantic_def.source_file_path,
        source_repository_id=source_repo_id,
        file_system_source_id=fs_source_id,
        commit_hash=pydantic_def.commit_hash,
        # parameters=[ParameterDefinitionOrm(...)], # If deep mocking is needed
        # assets=[AssetDefinitionOrm(...)]
    )


@pytest.mark.asyncio
class TestProtocolDiscoveryService:

    async def test_discover_and_register_protocols_from_repo(self, discovery_service: ProtocolDiscoveryService, db_session: AsyncSession):
        """Test discovery from a mock Git repository source, reflecting decorated protocols."""
        repo_orm = ProtocolSourceRepositoryOrm(
            id=1, # Explicitly set ID for predictability in mocks
            name="TestGitRepoDecorated",
            git_url="https://example.com/test_decorated_repo.git",
            default_ref="main",
            local_checkout_path="/tmp/fake_decorated_repo_path"
        )
        db_session.add(repo_orm)
        await db_session.commit()
        await db_session.refresh(repo_orm)

        # Define Pydantic models for the two protocols from PROTOCOL_CONTENT_DECORATED
        protocol_def_1 = FunctionProtocolDefinition(
            name="MyDecoratedProtocol", version="1.0.0", description="A test protocol.",
            module_name="temp_protocols_test_pkg.decorated_protos", function_name="decorated_protocol_func",
            parameters=[
                ParameterDefinition(name="state", type_hint_str="PraxisState", actual_type_str="PraxisState", optional=False, is_deck_param=False),
                ParameterDefinition(name="deck", type_hint_str="PlrDeck", actual_type_str="PlrDeck", optional=False, is_deck_param=True),
                ParameterDefinition(name="samples", type_hint_str="int", actual_type_str="int", optional=False, default_value_repr="8"),
                ParameterDefinition(name="comment", type_hint_str="Optional[str]", actual_type_str="str", optional=True, default_value_repr="None")
            ],
            assets=[], is_top_level=True, source_file_path="decorated_protos.py",
            docstring="This is a docstring for decorated_protocol_func."
        )
        protocol_def_2 = FunctionProtocolDefinition(
            name="AnotherProtocol", version="0.1.0", description=None, # No explicit description in decorator
            module_name="temp_protocols_test_pkg.decorated_protos", function_name="another_func",
            parameters=[
                ParameterDefinition(name="state", type_hint_str="PraxisState", actual_type_str="PraxisState", optional=False),
            ],
            assets=[
                AssetDefinition(name="tip_box", type_hint_str="PlrResource", actual_type_str="PlrResource", optional=False)
            ],
            is_top_level=False, # Default for @protocol_function if not specified
            source_file_path="decorated_protos.py"
        )

        mock_discovered_protos_list: List[DiscoveredFunctionProtocol] = [
            DiscoveredFunctionProtocol(
                source_info=ProtocolSourceInfo(
                    source_type=ProtocolSourceType.GIT_REPOSITORY,
                    path="decorated_protos.py", # Relative path within repo
                    repo_url=repo_orm.git_url,
                    commit_hash="abcdef123"
                ),
                definition=protocol_def_1.model_copy(update={"commit_hash": "abcdef123", "source_repository_name": str(repo_orm.id)})
            ),
            DiscoveredFunctionProtocol(
                source_info=ProtocolSourceInfo(
                    source_type=ProtocolSourceType.GIT_REPOSITORY,
                    path="decorated_protos.py",
                    repo_url=repo_orm.git_url,
                    commit_hash="abcdef123"
                ),
                definition=protocol_def_2.model_copy(update={"commit_hash": "abcdef123", "source_repository_name": str(repo_orm.id)})
            )
        ]

        # Simulate that _register_discovered_protocols sets the db_id on the returned DiscoveredFunctionProtocol objects
        # and returns the ORM objects (or their IDs) as part of its result.
        # For this test, we care about the DiscoveredFunctionProtocol having db_id.

        # Mock return value for _register_discovered_protocols
        # It should return (new_defs_with_db_id, updated_defs_with_db_id, failed_defs)
        # Let's assume both are new and get db_ids 1 and 2
        registered_proto_1 = mock_discovered_protos_list[0].model_copy()
        registered_proto_1.db_id = 1
        registered_proto_1.definition.db_id = 1


        registered_proto_2 = mock_discovered_protos_list[1].model_copy()
        registered_proto_2.db_id = 2
        registered_proto_2.definition.db_id = 2

        discovery_service._sync_git_repository = AsyncMock(return_value=repo_orm.local_checkout_path) # Must return Path object or string
        discovery_service._scan_directory_for_protocols = MagicMock(return_value=mock_discovered_protos_list)
        # _register_discovered_protocols is what eventually calls the DB upsert logic.
        # Its return value should be a tuple: (new_defs, updated_defs, failed_defs)
        # where new_defs and updated_defs are lists of DiscoveredFunctionProtocol with db_id set.
        discovery_service._register_discovered_protocols = AsyncMock(return_value=([registered_proto_1, registered_proto_2], [], []))

        new_defs, updated_defs, failed_defs = await discovery_service.discover_and_register_protocols_from_repo(repo_orm.id)

        assert len(new_defs) == 2
        assert len(updated_defs) == 0
        assert len(failed_defs) == 0

        # Protocol 1: MyDecoratedProtocol
        found_protocol_1 = next((p for p in new_defs if p.definition.name == "MyDecoratedProtocol"), None)
        assert found_protocol_1 is not None
        if found_protocol_1:
            assert found_protocol_1.definition.name == "MyDecoratedProtocol"
            assert found_protocol_1.definition.version == "1.0.0"
            assert found_protocol_1.db_id == 1
            assert found_protocol_1.definition.db_id == 1
            assert len(found_protocol_1.definition.parameters) == 4 # state, deck, samples, comment
            assert any(p.name == "samples" and p.default_value_repr == "8" for p in found_protocol_1.definition.parameters)
            assert any(p.name == "deck" and p.is_deck_param for p in found_protocol_1.definition.parameters)
            assert found_protocol_1.source_info.commit_hash == "abcdef123"
            assert found_protocol_1.definition.source_repository_name == str(repo_orm.id)


        # Protocol 2: AnotherProtocol
        found_protocol_2 = next((p for p in new_defs if p.definition.name == "AnotherProtocol"), None)
        assert found_protocol_2 is not None
        if found_protocol_2:
            assert found_protocol_2.definition.name == "AnotherProtocol"
            assert found_protocol_2.definition.version == "0.1.0"
            assert found_protocol_2.db_id == 2
            assert found_protocol_2.definition.db_id == 2
            assert len(found_protocol_2.definition.parameters) == 1
            assert len(found_protocol_2.definition.assets) == 1
            assert found_protocol_2.definition.assets[0].name == "tip_box"
            assert found_protocol_2.definition.source_repository_name == str(repo_orm.id)


        discovery_service._sync_git_repository.assert_called_once_with(repo_orm)
        discovery_service._scan_directory_for_protocols.assert_called_once_with(
            Path(str(repo_orm.local_checkout_path)), # Ensure Path object if that's what _scan expects
            ProtocolSourceInfo(
                source_type=ProtocolSourceType.GIT_REPOSITORY,
                path=str(repo_orm.local_checkout_path),
                repo_url=repo_orm.git_url,
                # commit_hash is usually determined during/after sync, not passed into scan this way.
                # The source_info for scan is more about the root being scanned.
            )
        )
        discovery_service._register_discovered_protocols.assert_called_once_with(
            mock_discovered_protos_list,
            repo_orm,
            None
        )

    async def test_discover_from_decorated_module_via_fs_source(self, discovery_service: ProtocolDiscoveryService, db_session: AsyncSession, temp_protocol_dir: Path):
        """
        Test discovering a protocol from a Python module within a FileSystemSource,
        simulating the structure of the original 'test_discover_from_decorated_module'.
        """
        # 1. Create a dummy protocol file in the temp_protocol_dir (which is 'temp_protocols_test_pkg')
        module_name = "decorated_module_for_fs_test"
        create_dummy_protocol_file(temp_protocol_dir, module_name, PROTOCOL_CONTENT_DECORATED)

        # 2. Setup FileSystemProtocolSourceOrm to point to the parent of temp_protocol_dir
        #    The discovery service typically scans paths relative to the FS source's base_path.
        #    If temp_protocol_dir is '.../temp_protocols_test_pkg', and base_path is '...',
        #    then the module path will be 'temp_protocols_test_pkg.decorated_module_for_fs_test'
        fs_source_orm = FileSystemProtocolSourceOrm(
            id=10, # Predictable ID
            name="TestFileSystemSource",
            base_path=str(temp_protocol_dir.parent) # The directory *containing* 'temp_protocols_test_pkg'
        )
        db_session.add(fs_source_orm)
        await db_session.commit()
        await db_session.refresh(fs_source_orm)

        # 3. Define the expected discovered protocols (similar to the repo test)
        protocol_def_1 = FunctionProtocolDefinition(
            name="MyDecoratedProtocol", version="1.0.0", description="A test protocol.",
            module_name=f"temp_protocols_test_pkg.{module_name}", function_name="decorated_protocol_func",
            parameters=[
                ParameterDefinition(name="state", type_hint_str="PraxisState", actual_type_str="PraxisState", optional=False),
                ParameterDefinition(name="deck", type_hint_str="PlrDeck", actual_type_str="PlrDeck", optional=False, is_deck_param=True),
                ParameterDefinition(name="samples", type_hint_str="int", actual_type_str="int", optional=False, default_value_repr="8"),
                ParameterDefinition(name="comment", type_hint_str="Optional[str]", actual_type_str="str", optional=True, default_value_repr="None")
            ],
            assets=[], is_top_level=True, source_file_path=f"{module_name}.py", # Relative to package
            docstring="This is a docstring for decorated_protocol_func."
        )
        protocol_def_2 = FunctionProtocolDefinition(
            name="AnotherProtocol", version="0.1.0",
            module_name=f"temp_protocols_test_pkg.{module_name}", function_name="another_func",
            parameters=[ParameterDefinition(name="state", type_hint_str="PraxisState", actual_type_str="PraxisState", optional=False)],
            assets=[AssetDefinition(name="tip_box", type_hint_str="PlrResource", actual_type_str="PlrResource", optional=False)],
            is_top_level=False, source_file_path=f"{module_name}.py"
        )

        # These are what _scan_directory_for_protocols would produce
        mock_scanned_protos: List[DiscoveredFunctionProtocol] = [
            DiscoveredFunctionProtocol(
                source_info=ProtocolSourceInfo(
                    source_type=ProtocolSourceType.FILE_SYSTEM,
                    # Path here is relative to the FileSystemProtocolSourceOrm.base_path
                    path=f"temp_protocols_test_pkg/{module_name}.py",
                ),
                definition=protocol_def_1.model_copy(update={"file_system_source_name": str(fs_source_orm.id)})
            ),
            DiscoveredFunctionProtocol(
                source_info=ProtocolSourceInfo(
                    source_type=ProtocolSourceType.FILE_SYSTEM,
                    path=f"temp_protocols_test_pkg/{module_name}.py",
                ),
                definition=protocol_def_2.model_copy(update={"file_system_source_name": str(fs_source_orm.id)})
            )
        ]

        # Mock _scan_directory_for_protocols because it involves actual file system ops and imports
        discovery_service._scan_directory_for_protocols = MagicMock(return_value=mock_scanned_protos)

        # Mock _register_discovered_protocols to simulate DB interaction and db_id assignment
        registered_proto_1 = mock_scanned_protos[0].model_copy()
        registered_proto_1.db_id = 3
        registered_proto_1.definition.db_id = 3

        registered_proto_2 = mock_scanned_protos[1].model_copy()
        registered_proto_2.db_id = 4
        registered_proto_2.definition.db_id = 4

        discovery_service._register_discovered_protocols = AsyncMock(
            return_value=([registered_proto_1, registered_proto_2], [], [])
        )

        # 4. Act
        # Call the method that handles discovery from a FileSystemSource
        new_defs, updated_defs, failed_defs = await discovery_service.discover_and_register_protocols_from_fs(fs_source_orm.id)

        # 5. Assert
        assert len(new_defs) == 2
        assert len(updated_defs) == 0
        assert len(failed_defs) == 0

        found_protocol_1 = next((p for p in new_defs if p.definition.name == "MyDecoratedProtocol"), None)
        assert found_protocol_1 is not None
        if found_protocol_1:
            assert found_protocol_1.definition.name == "MyDecoratedProtocol"
            assert found_protocol_1.db_id == 3
            assert found_protocol_1.definition.db_id == 3
            assert found_protocol_1.definition.module_name == f"temp_protocols_test_pkg.{module_name}"
            assert found_protocol_1.definition.file_system_source_name == str(fs_source_orm.id)


        found_protocol_2 = next((p for p in new_defs if p.definition.name == "AnotherProtocol"), None)
        assert found_protocol_2 is not None
        if found_protocol_2:
            assert found_protocol_2.definition.name == "AnotherProtocol"
            assert found_protocol_2.db_id == 4
            assert found_protocol_2.definition.db_id == 4
            assert found_protocol_2.definition.file_system_source_name == str(fs_source_orm.id)


        # Verify mock calls
        # _scan_directory_for_protocols is called with the base_path of the fs_source_orm
        # and source_info reflecting that file system source.
        discovery_service._scan_directory_for_protocols.assert_called_once()
        call_args_scan = discovery_service._scan_directory_for_protocols.call_args[0]
        assert call_args_scan[0] == Path(fs_source_orm.base_path)
        assert call_args_scan[1].source_type == ProtocolSourceType.FILE_SYSTEM
        assert call_args_scan[1].path == fs_source_orm.base_path

        discovery_service._register_discovered_protocols.assert_called_once_with(
            mock_scanned_protos,
            None, # No repo_source_orm
            fs_source_orm
        )
