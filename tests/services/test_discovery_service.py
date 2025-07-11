# pylint: disable=redefined-outer-name, protected-access, unused-argument, no-member
"""Unit tests for the ProtocolDiscoveryService."""

import sys
import uuid
from collections.abc import Generator
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from praxis.backend.core.run_context import PROTOCOL_REGISTRY
from praxis.backend.models.protocol_pydantic_models import (
  FunctionProtocolDefinitionModel,
)
from praxis.backend.services.discovery_service import ProtocolDiscoveryService

# --- Fixtures ---


@pytest.fixture
def discovery_service() -> ProtocolDiscoveryService:
  """Provides a ProtocolDiscoveryService instance with a mocked DB session factory."""
  mock_session_factory = MagicMock()
  # The session factory itself returns an async context manager
  mock_session_factory.return_value.__aenter__.return_value = AsyncMock()
  mock_session_factory.return_value.__aexit__.return_value = None
  return ProtocolDiscoveryService(db_session_factory=mock_session_factory)


@pytest.fixture(autouse=True)
def clear_protocol_registry():
  """Fixture to clear the global PROTOCOL_REGISTRY before and after each test."""
  PROTOCOL_REGISTRY.clear()
  yield
  PROTOCOL_REGISTRY.clear()


@pytest.fixture
def protocol_files(tmp_path: Path) -> Generator[Path, None, None]:
  """Creates a temporary directory with dummy protocol files for discovery."""
  protocols_dir = tmp_path / "protocols"
  protocols_dir.mkdir()

  sys.path.insert(0, str(tmp_path))

  # File 1: A protocol defined with the @protocol decorator
  (protocols_dir / "decorated_protocol.py").write_text(
    """
from praxis.backend.protocol_core.decorators import protocol
from praxis.backend.models.protocol_pydantic_models import AssetRequirementModel
from pylabrobot.resources import Plate, TipRack
from typing import Optional

@protocol(
    name="decorated_transfer",
    version="1.1.0",
    description="A test protocol using a decorator.",
    is_top_level=True,
    assets=[
        AssetRequirementModel(
            name="tips",
            fqn="pylabrobot.resources.TipRack",
            optional=False
        )
    ]
)
def my_decorated_protocol(
    source_plate: Plate,
    dest_plate: Optional[Plate] = None,
    volume: float = 50.0
):
    '''Docstring for decorated protocol.'''
    pass
""",
  )

  # File 2: A protocol to be discovered via inference
  (protocols_dir / "inferred_protocol.py").write_text(
    """
from pylabrobot.resources import Plate
from typing import Optional

def my_inferred_protocol(p: Plate, num_transfers: int, speed: Optional[float] = 1.0):
    '''Docstring for inferred protocol.'''
    pass

def not_a_protocol():
    return "hello"
""",
  )

  (protocols_dir / "_ignored_file.py").write_text("def ignored_func(): pass")

  yield protocols_dir

  sys.path.pop(0)
  for mod in ["protocols.decorated_protocol", "protocols.inferred_protocol"]:
    if mod in sys.modules:
      del sys.modules[mod]


# --- Tests ---


@pytest.mark.asyncio
class TestProtocolDiscoveryService:
  """Test suite for the ProtocolDiscoveryService."""

  def test_extract_from_paths_finds_protocols(self, discovery_service, protocol_files) -> None:
    """Test that _extract_protocol_definitions_from_paths finds all valid protocols."""
    definitions = discovery_service._extract_protocol_definitions_from_paths(
      str(protocol_files),
    )
    assert len(definitions) == 2
    names = {model.name for model, func in definitions}
    assert "decorated_transfer" in names
    assert "my_inferred_protocol" in names

  def test_decorated_protocol_is_parsed_correctly(
    self, discovery_service, protocol_files,
  ) -> None:
    """Verify the content of a protocol definition from a decorator."""
    definitions = discovery_service._extract_protocol_definitions_from_paths(
      str(protocol_files),
    )
    decorated_def, func = next(
      d for d in definitions if d[0].name == "decorated_transfer"
    )
    assert isinstance(decorated_def, FunctionProtocolDefinitionModel)
    assert decorated_def.name == "decorated_transfer"
    assert decorated_def.version == "1.1.0"
    param_names = {p.name for p in decorated_def.parameters}
    assert param_names == {"source_plate", "dest_plate", "volume"}
    asset_names = {a.name for a in decorated_def.assets}
    assert "tips" in asset_names

  def test_inferred_protocol_is_parsed_correctly(
    self, discovery_service, protocol_files,
  ) -> None:
    """Verify the content of an inferred protocol definition."""
    definitions = discovery_service._extract_protocol_definitions_from_paths(
      str(protocol_files),
    )
    inferred_def, func = next(
      d for d in definitions if d[0].name == "my_inferred_protocol"
    )
    assert isinstance(inferred_def, FunctionProtocolDefinitionModel)
    params = {p.name: p for p in inferred_def.parameters}
    assert "num_transfers" in params
    assets = {a.name: a for a in inferred_def.assets}
    assert "p" in assets
    # FIX: Check the 'fqn' attribute instead of 'actual_type_str'
    assert assets["p"].fqn == "pylabrobot.resources.Plate"
    assert assets["p"].optional is False

  async def test_discover_and_upsert_happy_path(
    self, discovery_service, protocol_files,
  ) -> None:
    """Test the full discover and upsert flow, including registry updates."""
    # Manually populate the registry as the decorator would
    decorated_def = FunctionProtocolDefinitionModel(
      accession_id=uuid.uuid4(),
      name="decorated_transfer",
      version="1.1.0",
      source_file_path="protocols/decorated_protocol.py",
      module_name="protocols.decorated_protocol",
      function_name="my_decorated_protocol",
    )
    PROTOCOL_REGISTRY["decorated_transfer_v1.1.0"] = {
      "pydantic_definition": decorated_def,
    }
    mock_orm = MagicMock()
    mock_orm.accession_id = uuid.uuid4()

    with patch(
      "praxis.backend.services.protocols.upsert_function_protocol_definition",
      new_callable=AsyncMock,
    ) as mock_upsert:
      mock_upsert.return_value = mock_orm
      result_orms = await discovery_service.discover_and_upsert_protocols(
        str(protocol_files),
      )
      assert len(result_orms) == 2
      registry_entry = PROTOCOL_REGISTRY.get("decorated_transfer_v1.1.0")
      assert registry_entry is not None
      assert registry_entry["db_accession_id"] == mock_orm.accession_id
