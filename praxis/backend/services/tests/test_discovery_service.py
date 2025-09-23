"""Tests for the DiscoveryService."""

import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from praxis.backend.services.discovery_service import DiscoveryService


@pytest.fixture
def mock_db_session_factory() -> MagicMock:
  """Mock database session factory."""
  return MagicMock()


@pytest.fixture
def mock_protocol_definition_service() -> MagicMock:
  """Mock protocol definition service."""
  service = MagicMock()
  service.get_by_fqn = AsyncMock(return_value=None)
  service.create = AsyncMock(return_value="orm_object")
  service.update = AsyncMock(return_value="updated_orm_object")
  return service


@pytest.fixture
def discovery_service(
  mock_db_session_factory: MagicMock,
  mock_protocol_definition_service: MagicMock,
) -> DiscoveryService:
  """Return a DiscoveryService instance with mocked dependencies."""
  return DiscoveryService(
    db_session_factory=mock_db_session_factory,
    protocol_definition_service=mock_protocol_definition_service,
  )


@pytest.mark.asyncio
@patch("uuid_utils.uuid7")
async def test_discover_and_upsert_protocols_successfully(
  mock_uuid7: MagicMock,
  discovery_service: DiscoveryService,
  tmp_path: Path,
  mock_protocol_definition_service: MagicMock,
  mock_db_session_factory: MagicMock,
) -> None:
  """Test that protocols are discovered and upserted successfully."""
  mock_uuid7.return_value = uuid.UUID("00000000-0000-0000-0000-000000000001")
  protocol_dir = tmp_path / "protocols"
  protocol_dir.mkdir()
  protocol_file = protocol_dir / "protocol.py"
  protocol_file.write_text(
    """
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
""",
  )
  mock_db_session_factory.return_value.__aenter__.return_value = AsyncMock()

  result = await discovery_service.discover_and_upsert_protocols([str(protocol_dir)])

  assert len(result) == 1
  assert result[0] == "orm_object"
  mock_protocol_definition_service.create.assert_called_once()


@pytest.mark.asyncio
@patch("uuid_utils.uuid7")
async def test_discover_and_upsert_protocols_inferred(
  mock_uuid7: MagicMock,
  discovery_service: DiscoveryService,
  tmp_path: Path,
  mock_protocol_definition_service: MagicMock,
  mock_db_session_factory: MagicMock,
) -> None:
  """Test that a protocol definition is inferred and upserted."""
  mock_uuid7.return_value = uuid.UUID("00000000-0000-0000-0000-000000000002")
  protocol_dir = tmp_path / "protocols"
  protocol_dir.mkdir()
  protocol_file = protocol_dir / "inferred_protocol.py"
  protocol_file.write_text(
    """
def another_mock_func(param1: int, param2: str = "default"):
    \"\"\"A docstring for description.\"\"\"
    pass
""",
  )

  mock_db_session_factory.return_value.__aenter__.return_value = AsyncMock()
  mock_protocol_definition_service.create.return_value = "inferred_orm_object"

  result = await discovery_service.discover_and_upsert_protocols([str(protocol_dir)])

  assert len(result) == 1
  assert result[0] == "inferred_orm_object"
  mock_protocol_definition_service.create.assert_called_once()
  created_def = mock_protocol_definition_service.create.call_args[1]["obj_in"]
  assert created_def.name == "another_mock_func"


@pytest.mark.asyncio
async def test_discover_and_upsert_protocols_no_protocols_found(
  discovery_service: DiscoveryService, tmp_path: Path,
) -> None:
  """Test that nothing is upserted when no protocols are found."""
  protocol_dir = tmp_path / "protocols"
  protocol_dir.mkdir()
  (protocol_dir / "empty.txt").touch()

  result = await discovery_service.discover_and_upsert_protocols([str(protocol_dir)])
  assert len(result) == 0


@pytest.mark.asyncio
async def test_discover_and_upsert_protocols_directory_not_exist(
  discovery_service: DiscoveryService,
) -> None:
  """Test that nothing is upserted for a non-existent directory."""
  result = await discovery_service.discover_and_upsert_protocols(["/non_existent_dir"])
  assert len(result) == 0


@pytest.mark.asyncio
@patch("uuid_utils.uuid7")
async def test_discover_and_upsert_protocols_import_error(
  mock_uuid7: MagicMock,
  discovery_service: DiscoveryService,
  tmp_path: Path,
  mock_protocol_definition_service: MagicMock,
  mock_db_session_factory: MagicMock,
) -> None:
  """Test that an import error is handled gracefully."""
  mock_uuid7.return_value = uuid.UUID("00000000-0000-0000-0000-000000000003")
  protocol_dir = tmp_path / "protocols"
  protocol_dir.mkdir()
  protocol_file = protocol_dir / "importerror_protocol.py"
  protocol_file.write_text("import non_existent_module")

  mock_db_session_factory.return_value.__aenter__.return_value = AsyncMock()

  result = await discovery_service.discover_and_upsert_protocols([str(protocol_dir)])
  assert len(result) == 0
  mock_protocol_definition_service.create.assert_not_called()
