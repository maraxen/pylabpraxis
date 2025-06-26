# pylint: disable=redefined-outer-name, protected-access
"""Shared fixtures for core component tests."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from pylabrobot.resources import Deck, STARLetDeck

from praxis.backend.core.asset_manager import AssetManager
from praxis.backend.models import (
  MachineOrm,
  MachineStatusEnum,
  ResourceDefinitionCatalogOrm,
  ResourceOrm,
  ResourceStatusEnum,
)

# --- Static Test UUIDs (version 7) ---
TEST_PROTOCOL_RUN_ID = uuid.UUID("018f4a3b-3c48-7c87-8c4c-35e6a172c74d", version=7)
TEST_MACHINE_ID = uuid.UUID("018f4a3c-b034-7548-b4e8-87d464cb3f92", version=7)
TEST_RESOURCE_ID = uuid.UUID("018f4a3d-3b4f-7b1e-913a-a1c1d858348c", version=7)
TEST_DECK_RESOURCE_ID = uuid.UUID("018f4a3d-a3e1-75f2-9831-27f329d443e2", version=7)


@pytest.fixture
def mock_db_session() -> AsyncMock:
  """Provide a mock SQLAlchemy AsyncSession."""
  return AsyncMock()


@pytest.fixture
def mock_workcell_runtime() -> AsyncMock:
  """Provide a mock WorkcellRuntime with mocked async methods."""
  runtime = AsyncMock()
  runtime.initialize_machine = AsyncMock()
  runtime.shutdown_machine = AsyncMock()
  runtime.create_or_get_resource = AsyncMock()
  runtime.assign_resource_to_deck = AsyncMock()
  runtime.clear_resource_instance = AsyncMock()
  runtime.clear_deck_position = AsyncMock()
  return runtime


@pytest.fixture
def asset_manager(mock_db_session, mock_workcell_runtime) -> AssetManager:
  """Provide an AssetManager instance with mocked dependencies."""
  return AssetManager(
    db_session=mock_db_session,
    workcell_runtime=mock_workcell_runtime,
  )


@pytest.fixture
def machine_orm_factory():
  """Create MachineOrm instances for testing."""

  def _factory(**kwargs):
    defaults = {
      "accession_id": TEST_MACHINE_ID,
      "user_friendly_name": "Test OT-2",
      "python_fqn": "pylabrobot.liquid_handling.ot_2.OT_2",
      "current_status": MachineStatusEnum.AVAILABLE,
      "current_protocol_run_accession_id": None,
    }
    defaults.update(kwargs)
    return MachineOrm(**defaults)

  return _factory


@pytest.fixture
def resource_definition_factory():
  """Create ResourceDefinitionCatalogOrm instances."""

  def _factory(**kwargs):
    defaults = {
      "name": "cos_96_wellplate_100ul",
      "python_fqn": "pylabrobot.resources.corning_costar.plates.cos_96_wellplate_100ul",
      "resource_type": "Plate",
      "is_consumable": True,
      "plr_definition_details_json": {"size_x": 127.0, "size_y": 86.0},
    }
    defaults.update(kwargs)
    # Using a MagicMock allows attribute access without a full ORM model
    mock_orm = MagicMock(spec=ResourceDefinitionCatalogOrm)
    for key, value in defaults.items():
      setattr(mock_orm, key, value)
    return mock_orm

  return _factory


@pytest.fixture
def resource_instance_factory():
  """Create ResourceOrm instances."""

  def _factory(**kwargs):
    defaults = {
      "accession_id": TEST_RESOURCE_ID,
      "user_assigned_name": "Test Plate 1",
      "python_fqn": "cos_96_wellplate_100ul",
      "current_status": ResourceStatusEnum.AVAILABLE_IN_STORAGE,
      "current_protocol_run_accession_id": None,
      "location_machine_accession_id": None,
      "current_deck_position_name": None,
    }
    defaults.update(kwargs)
    return ResourceOrm(**defaults)

  return _factory


@pytest.fixture
def mock_plr_deck_object() -> Deck:
  """Provide a mock PyLabRobot Deck object."""
  deck = MagicMock(spec=STARLetDeck)
  deck.name = "mock_deck_resource_instance"
  deck.assign_child_resource = MagicMock()
  return deck


@pytest.fixture
def mock_plr_resource_object() -> MagicMock:
  """Provide a generic mock PyLabRobot Resource object."""
  resource = MagicMock(spec=Deck)  # Use a real class for isinstance checks
  resource.name = "mock_plate_resource_instance"
  return resource
