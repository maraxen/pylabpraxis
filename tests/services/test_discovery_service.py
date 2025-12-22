"""Tests for the DiscoveryService."""

import uuid
from pathlib import Path
from textwrap import dedent
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.services.discovery_service import DiscoveryService
from praxis.backend.services.machine_type_definition import MachineTypeDefinitionService
from praxis.backend.services.protocol_definition import ProtocolDefinitionCRUDService
from praxis.backend.services.resource_type_definition import ResourceTypeDefinitionService


@pytest.fixture
def mock_db_session_factory():
    """Mock database session factory."""
    session = AsyncMock(spec=AsyncSession)
    # The factory returns an async context manager that yields the session
    factory = MagicMock(return_value=AsyncMock(__aenter__=AsyncMock(return_value=session), __aexit__=AsyncMock()))
    return factory


@pytest.fixture
def mock_protocol_service():
    """Mock protocol definition service."""
    service = AsyncMock(spec=ProtocolDefinitionCRUDService)
    # Explicitly set return values for common methods to avoid await issues if auto-mocking fails
    service.get_by_fqn.return_value = None
    service.create.return_value = MagicMock(accession_id=uuid.uuid4(), id=1)
    service.update.return_value = MagicMock(accession_id=uuid.uuid4(), id=1)
    return service


@pytest.fixture
def mock_resource_service():
    """Mock resource type definition service."""
    service = AsyncMock(spec=ResourceTypeDefinitionService)
    return service


@pytest.fixture
def mock_machine_service():
    """Mock machine type definition service."""
    service = AsyncMock(spec=MachineTypeDefinitionService)
    return service


@pytest.fixture
def discovery_service(
    mock_db_session_factory,
    mock_protocol_service,
    mock_resource_service,
    mock_machine_service,
):
    """Return a DiscoveryService instance with mocked dependencies."""
    return DiscoveryService(
        db_session_factory=mock_db_session_factory,
        protocol_definition_service=mock_protocol_service,
        resource_type_definition_service=mock_resource_service,
        machine_type_definition_service=mock_machine_service,
    )


def test_extract_protocol_definitions_from_paths(discovery_service, tmp_path):
    """Test that protocol definitions are extracted from paths."""
    protocol_dir = tmp_path / "my_protocols"
    protocol_dir.mkdir()
    (protocol_dir / "__init__.py").touch()

    protocol_file = protocol_dir / "proto.py"
    protocol_content = dedent("""
        def my_protocol(volume: float):
            '''A test protocol.'''
            pass
    """)
    protocol_file.write_text(protocol_content)

    definitions = discovery_service._extract_protocol_definitions_from_paths([protocol_dir])
    assert len(definitions) == 1
    assert definitions[0]["name"] == "my_protocol"
    assert definitions[0]["description"] == "A test protocol."
    assert len(definitions[0]["parameters"]) == 1
    assert definitions[0]["parameters"][0]["name"] == "volume"
    assert definitions[0]["parameters"][0]["type_hint"] == "float"


def test_extract_protocol_definitions_with_complex_signature(discovery_service, tmp_path):
    """Test that protocol definitions are extracted from a complex signature."""
    protocol_dir = tmp_path / "my_protocols"
    protocol_dir.mkdir()
    (protocol_dir / "__init__.py").touch()

    protocol_file = protocol_dir / "proto.py"
    protocol_content = dedent("""
        from typing import Optional
        def my_protocol(
            a: int,
            b: str = "hello",
            c: Optional[float] = None,
        ):
            pass
    """)
    protocol_file.write_text(protocol_content)

    definitions = discovery_service._extract_protocol_definitions_from_paths([protocol_dir])
    assert len(definitions) == 1
    assert definitions[0]["name"] == "my_protocol"
    parameters = definitions[0]["parameters"]
    assert len(parameters) == 3
    assert parameters[0]["name"] == "a"
    assert parameters[0]["type_hint"] == "int"
    assert not parameters[0]["optional"]
    assert parameters[1]["name"] == "b"
    assert parameters[1]["type_hint"] == "str"
    assert parameters[1]["optional"]
    assert parameters[1]["default_value_repr"] == "'hello'"
    assert parameters[2]["name"] == "c"
    assert parameters[2]["type_hint"] == "Optional[float]"
    assert parameters[2]["optional"]
    assert parameters[2]["default_value_repr"] == "None"


def test_extract_protocol_definitions_with_pylabrobot_resource(discovery_service, tmp_path):
    """Test that pylabrobot resources are correctly identified as assets."""
    protocol_dir = tmp_path / "my_protocols"
    protocol_dir.mkdir()
    (protocol_dir / "__init__.py").touch()

    protocol_file = protocol_dir / "proto.py"
    protocol_content = dedent("""
        from pylabrobot.resources import Plate
        def my_protocol(plate: Plate):
            pass
    """)
    protocol_file.write_text(protocol_content)

    definitions = discovery_service._extract_protocol_definitions_from_paths([protocol_dir])
    assert len(definitions) == 1
    assert definitions[0]["name"] == "my_protocol"
    assets = definitions[0]["assets"]
    assert len(assets) == 1
    assert assets[0]["name"] == "plate"
    assert assets[0]["type_hint"] == "Plate"


def test_extract_protocol_definitions_with_invalid_syntax(discovery_service, tmp_path):
    """Test that protocol definitions are not extracted from a file with invalid syntax."""
    protocol_dir = tmp_path / "my_protocols"
    protocol_dir.mkdir()
    (protocol_dir / "__init__.py").touch()

    protocol_file = protocol_dir / "proto.py"
    protocol_content = dedent("""
        def my_protocol()
            pass
    """)
    protocol_file.write_text(protocol_content)

    definitions = discovery_service._extract_protocol_definitions_from_paths([protocol_dir])
    assert len(definitions) == 0


@pytest.mark.asyncio
@patch("praxis.backend.utils.uuid.uuid7")
async def test_discover_and_upsert_protocols_successfully(
  mock_uuid7: MagicMock,
  discovery_service: DiscoveryService,
  tmp_path: Path,
  mock_protocol_service: MagicMock,
):
  """Test that protocols are discovered and upserted successfully."""
  mock_uuid7.return_value = uuid.UUID("00000000-0000-0000-0000-000000000001")
  protocol_dir = tmp_path / "protocols"
  protocol_dir.mkdir()
  protocol_file = protocol_dir / "protocol.py"
  protocol_file.write_text(dedent("""
        from praxis.backend.models.pydantic_internals.protocol import FunctionProtocolDefinitionCreate

        def mock_protocol_func():
            pass

        protocol_def = FunctionProtocolDefinitionCreate(
            name="mock_protocol_func",
            version="1.0",
            description="A mock protocol function.",
            source_file_path=__file__,
            module_name="protocol",
            function_name="mock_protocol_func",
            parameters=[],
            assets=[],
            is_top_level=True,
        )
        setattr(mock_protocol_func, "_protocol_definition", protocol_def)
    """).strip())

  result = await discovery_service.discover_and_upsert_protocols([str(protocol_dir)])

  assert len(result) == 1
  mock_protocol_service.create.assert_called_once()


@pytest.mark.asyncio
@patch("praxis.backend.utils.uuid.uuid7")
async def test_discover_and_upsert_protocols_inferred(
  mock_uuid7: MagicMock,
  discovery_service: DiscoveryService,
  tmp_path: Path,
  mock_protocol_service: MagicMock,
):
  """Test that a protocol definition is inferred and upserted."""
  mock_uuid7.return_value = uuid.UUID("00000000-0000-0000-0000-000000000002")
  protocol_dir = tmp_path / "protocols"
  protocol_dir.mkdir()
  protocol_file = protocol_dir / "inferred_protocol.py"
  protocol_file.write_text(dedent("""
        def another_mock_func(param1: int, param2: str = "default"):
            \"\"\"A docstring for description.\"\"\"
            pass
    """).strip())

  # Mock return for create
  mock_protocol_service.create.return_value = MagicMock(accession_id=uuid.uuid4(), id=2)

  result = await discovery_service.discover_and_upsert_protocols([str(protocol_dir)])

  assert len(result) == 1
  mock_protocol_service.create.assert_called_once()
  created_def = mock_protocol_service.create.call_args[1]["obj_in"]
  assert created_def.name == "another_mock_func"


@pytest.mark.asyncio
async def test_discover_and_upsert_protocols_no_protocols_found(
  discovery_service: DiscoveryService, tmp_path: Path,
):
  """Test that nothing is upserted when no protocols are found."""
  protocol_dir = tmp_path / "protocols"
  protocol_dir.mkdir()
  (protocol_dir / "empty.txt").touch()

  result = await discovery_service.discover_and_upsert_protocols([str(protocol_dir)])
  assert len(result) == 0


@pytest.mark.asyncio
async def test_discover_and_upsert_protocols_directory_not_exist(
  discovery_service: DiscoveryService,
):
  """Test that nothing is upserted for a non-existent directory."""
  result = await discovery_service.discover_and_upsert_protocols(["/non_existent_dir"])
  assert len(result) == 0


@pytest.mark.asyncio
@patch("praxis.backend.utils.uuid.uuid7")
async def test_discover_and_upsert_protocols_import_error(
  mock_uuid7: MagicMock,
  discovery_service: DiscoveryService,
  tmp_path: Path,
  mock_protocol_service: MagicMock,
):
  """Test that an import error is handled gracefully."""
  mock_uuid7.return_value = uuid.UUID("00000000-0000-0000-0000-000000000003")
  protocol_dir = tmp_path / "protocols"
  protocol_dir.mkdir()
  protocol_file = protocol_dir / "importerror_protocol.py"
  protocol_file.write_text("import non_existent_module")

  result = await discovery_service.discover_and_upsert_protocols([str(protocol_dir)])
  assert len(result) == 0
  mock_protocol_service.create.assert_not_called()


@pytest.mark.asyncio
async def test_discover_and_sync_all_definitions(
    discovery_service: DiscoveryService,
    mock_resource_service: MagicMock,
    mock_machine_service: MagicMock,
):
    """Test that all definitions are discovered and synced."""
    # Mock discover_and_upsert_protocols since it's called internally
    # and we don't want to actually run file scanning in this unit test
    with patch.object(
        discovery_service, "discover_and_upsert_protocols", new_callable=AsyncMock
    ) as mock_upsert:
        await discovery_service.discover_and_sync_all_definitions(
            protocol_search_paths=["/tmp/protocols"],
            source_repository_accession_id=uuid.uuid4(),
            commit_hash="abc1234",
            file_system_source_accession_id=uuid.uuid4(),
        )

        mock_resource_service.discover_and_synchronize_type_definitions.assert_called_once()
        mock_machine_service.discover_and_synchronize_type_definitions.assert_called_once()
        mock_upsert.assert_called_once()
        call_kwargs = mock_upsert.call_args[1]
        assert call_kwargs["search_paths"] == ["/tmp/protocols"]
        assert call_kwargs["commit_hash"] == "abc1234"
