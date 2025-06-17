"""Unit tests for the WorkcellRuntime component."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import json  # For serialization tests

from sqlalchemy.ext.asyncio import async_sessionmaker

from praxis.backend.core.workcell_runtime import WorkcellRuntime
from praxis.backend.core.workcell import (
  Workcell as PraxisCoreWorkcell,
)  # Core Workcell object

# Correct Pydantic model imports
from praxis.backend.models.workcell_pydantic_models import (
  WorkcellDefinition as WorkcellDefinitionPydantic,
)
from praxis.backend.models.machine_pydantic_models import (
  MachineDefinition as MachineDefinitionPydantic,
)
# from praxis.backend.models.resource_pydantic_models import ResourceDefinition as ResourceDefinitionPydantic # If needed later

from praxis.backend.models.machine_orm import (
  MachineOrm,
)  # For mocking what Workcell core might provide


# Mock PyLabRobot objects that WorkcellRuntime might interact with
class MockLiquidHandler:
  def __init__(self, name, backend, **kwargs):
    self.name = name
    self.backend = backend
    self.is_connected = False
    self.extra_args = kwargs

  async def setup(self):
    self.is_connected = True
    # print(f"{self.name} setup called with {self.extra_args}")

  async def stop(self):
    self.is_connected = False
    # print(f"{self.name} stop called")

  def serialize_state(self):
    return {
      "name": self.name,
      "is_connected": self.is_connected,
      "type": "liquid_handler",
      "pylabrobot_fqn": "mock.MockLiquidHandler",
      "backend_name": self.backend.name
      if hasattr(self.backend, "name")
      else "mock_backend",
    }

  @classmethod
  def deserialize_state(cls, state_data, backend):
    handler = cls(name=state_data["name"], backend=backend)
    handler.is_connected = state_data.get("is_connected", False)
    return handler


class MockPlateReader:
  def __init__(self, name, backend, **kwargs):
    self.name = name
    self.backend = backend
    self.is_connected = False
    self.extra_args = kwargs

  async def setup(self):
    self.is_connected = True
    # print(f"{self.name} setup called with {self.extra_args}")

  async def stop(self):
    self.is_connected = False
    # print(f"{self.name} stop called")

  def serialize_state(self):
    return {
      "name": self.name,
      "is_connected": self.is_connected,
      "type": "plate_reader",
      "pylabrobot_fqn": "mock.MockPlateReader",
      "backend_name": self.backend.name
      if hasattr(self.backend, "name")
      else "mock_backend",
    }

  @classmethod
  def deserialize_state(cls, state_data, backend):
    reader = cls(name=state_data["name"], backend=backend)
    reader.is_connected = state_data.get("is_connected", False)
    return reader


@pytest.fixture
def mock_pylabrobot_backend():
  """Fixture for a mocked PyLabRobot backend."""
  backend = MagicMock()
  backend.name = "mock_plr_backend"  # Give backend a name for serialization if needed
  backend.setup = AsyncMock()
  backend.stop = AsyncMock()
  return backend


@pytest.fixture
def minimal_pydantic_workcell_def():
  """Provides a minimal Pydantic WorkcellDefinition for testing."""
  return WorkcellDefinitionPydantic(
    name="TestPydanticWorkcell",
    description="A test workcell definition",
    machines=[
      MachineDefinitionPydantic(
        name="Hamilton_STAR",
        machine_type="liquid_handler_STAR",
        backend_name="hamilton_backend",
        pylabrobot_fqn="mock.MockLiquidHandler",
        settings={},
      ),
      MachineDefinitionPydantic(
        name="ClarioStar",
        machine_type="plate_reader_clariostar",
        backend_name="clariostar_backend",
        pylabrobot_fqn="mock.MockPlateReader",
        settings={},
      ),
    ],
    resources=[],
  )


@pytest.fixture
@patch("praxis.backend.core.workcell_runtime.importlib.import_module")
@patch(
  "praxis.backend.core.workcell_runtime.getattr"
)  # To mock getting the PLR class from the module
def workcell_runtime_fixture(
  mock_getattr_plr_class,
  mock_import_module_plr_class,
  minimal_pydantic_workcell_def,
  mock_pylabrobot_backend,
):
  """Fixture for WorkcellRuntime with mocked dependencies."""
  mock_db_session_factory = MagicMock(spec=async_sessionmaker)
  workcell_name = "test_runtime_workcell"

  # Mock for the core PraxisCoreWorkcell object
  mock_core_workcell = MagicMock(spec=PraxisCoreWorkcell)
  mock_core_workcell.name = workcell_name

  # Setup the mock_core_workcell to return MachineOrm-like mocks
  mock_machine_definition_map = {}
  for pydantic_machine in minimal_pydantic_workcell_def.machines:
    orm_like_machine = MagicMock(spec=MachineOrm)
    orm_like_machine.name = pydantic_machine.name
    orm_like_machine.pylabrobot_fqn = pydantic_machine.pylabrobot_fqn
    orm_like_machine.backend_name = pydantic_machine.backend_name
    # Ensure backend_config and settings are dicts if accessed
    orm_like_machine.backend_config = (
      pydantic_machine.backend_config
      if hasattr(pydantic_machine, "backend_config")
      and pydantic_machine.backend_config is not None
      else {}
    )
    orm_like_machine.settings = (
      pydantic_machine.settings
      if hasattr(pydantic_machine, "settings") and pydantic_machine.settings is not None
      else {}
    )
    mock_machine_definition_map[pydantic_machine.name] = orm_like_machine

  mock_core_workcell.get_machine_definition_map.return_value = (
    mock_machine_definition_map
  )
  mock_core_workcell.get_resource_definition_map.return_value = {}  # Assuming no resources for now

  # Mocking for PyLabRobot class loading (getattr and import_module)
  def getattr_side_effect(module, class_name):
    if class_name == "MockLiquidHandler":
      return MockLiquidHandler
    if class_name == "MockPlateReader":
      return MockPlateReader
    # Fallback for any other expected classes, or raise error
    raise AttributeError(
      f"Mocked getattr doesn't know class {class_name} in module {module}"
    )

  mock_getattr_plr_class.side_effect = getattr_side_effect
  mock_import_module_plr_class.return_value = (
    MagicMock()
  )  # Represents the imported module

  runtime = WorkcellRuntime(
    db_session_factory=mock_db_session_factory,
    workcell_name=workcell_name,
    workcell_definition=mock_core_workcell,  # Pass the mocked Core Workcell
    workcell_save_file=None,
    plr_logging_level=logging.WARNING,  # Explicitly pass for clarity
  )
  return runtime


class TestWorkcellRuntime:
  """Test suite for the WorkcellRuntime."""

  @pytest.mark.asyncio
  async def test_initialize_workcell_machines_and_resources(
    self,
    workcell_runtime_fixture,
    minimal_pydantic_workcell_def,
    mock_pylabrobot_backend,
  ):
    """Test that machines and resources are initialized and setup."""
    # workcell_runtime_fixture already has the WorkcellRuntime instance
    # _get_or_create_backend_instance is an internal method, its mocking implies knowledge of internals.
    # It's often better to verify the outcome (machines initialized, setup called).

    # Patch the backend creation/lookup if it's complex and not handled by PLR object mocks
    # For now, assume PLR mock objects handle their backend interaction sufficiently.
    # If _get_or_create_backend_instance is called by WorkcellRuntime directly for each machine:
    with patch.object(
      workcell_runtime_fixture,
      "_get_or_create_backend_instance",
      return_value=mock_pylabrobot_backend,
    ) as mock_get_backend_method:
      await workcell_runtime_fixture.initialize_machines_and_resources()

      assert len(workcell_runtime_fixture.live_machines) == len(
        minimal_pydantic_workcell_def.machines
      )
      assert "Hamilton_STAR" in workcell_runtime_fixture.live_machines
      assert "ClarioStar" in workcell_runtime_fixture.live_machines

      hamilton_star = workcell_runtime_fixture.get_machine("Hamilton_STAR")
      clariostar = workcell_runtime_fixture.get_machine("ClarioStar")

      assert isinstance(hamilton_star, MockLiquidHandler)
      assert isinstance(clariostar, MockPlateReader)

      assert hamilton_star.is_connected
      assert clariostar.is_connected

      # Check if _get_or_create_backend_instance was called for each machine's backend_name
      # This depends on the internal logic of initialize_machines_and_resources
      # For example, it might be called once per unique backend_name
      # For this test, let's assume it's called for each machine if they could have different backend instances.
      assert mock_get_backend_method.call_count >= len(
        minimal_pydantic_workcell_def.machines
      )

  @pytest.mark.asyncio
  async def test_shutdown_workcell(
    self, workcell_runtime_fixture, mock_pylabrobot_backend
  ):
    """Test that machines are stopped and backends are shut down."""
    # Initialize to have some live machines
    with patch.object(
      workcell_runtime_fixture,
      "_get_or_create_backend_instance",
      return_value=mock_pylabrobot_backend,
    ):
      await workcell_runtime_fixture.initialize_machines_and_resources()

    hamilton_star = workcell_runtime_fixture.get_machine("Hamilton_STAR")
    clariostar = workcell_runtime_fixture.get_machine("ClarioStar")

    await workcell_runtime_fixture.shutdown_workcell()

    assert not hamilton_star.is_connected
    assert not clariostar.is_connected

    # Check that stop was called on each machine's backend (via the machine's stop method)
    # This is implicitly tested by `assert not machine.is_connected` if Mock PLR objects set this.
    # If WorkcellRuntime directly calls backend.stop(), that needs specific mocking and assertion.
    # Based on PLR patterns, machine.stop() should handle its backend.

  def test_get_machine_exists(self, workcell_runtime_fixture):
    """Test getting an existing machine."""
    # Populate live_machines directly for this synchronous test, or make test async and initialize.
    # For simplicity, assuming initialize_machines_and_resources was called (e.g. in an async setup method or by making this test async)
    # To keep it sync, we can manually populate live_machines if get_machine doesn't trigger async init.
    mock_lh = MockLiquidHandler("Hamilton_STAR", MagicMock())
    workcell_runtime_fixture.live_machines["Hamilton_STAR"] = mock_lh

    machine = workcell_runtime_fixture.get_machine("Hamilton_STAR")
    assert machine is not None
    assert machine.name == "Hamilton_STAR"
    assert isinstance(machine, MockLiquidHandler)

  def test_get_machine_not_exists(self, workcell_runtime_fixture):
    """Test getting a non-existent machine raises KeyError."""
    # Ensure live_machines is empty or does not contain the key
    workcell_runtime_fixture.live_machines = {}
    with pytest.raises(KeyError):
      workcell_runtime_fixture.get_machine("NonExistent_Machine")

  @patch("builtins.open", new_callable=MagicMock)  # Corrected new_callable
  @patch("json.dump")
  @pytest.mark.asyncio
  async def test_backup_workcell_state(
    self,
    mock_json_dump,
    mock_open_file,
    workcell_runtime_fixture,
    mock_pylabrobot_backend,
  ):
    """Test backing up the workcell state to a file."""
    with patch.object(
      workcell_runtime_fixture,
      "_get_or_create_backend_instance",
      return_value=mock_pylabrobot_backend,
    ):
      await workcell_runtime_fixture.initialize_machines_and_resources()

    filepath = "/path/to/backup.json"
    await workcell_runtime_fixture.backup_workcell_state(filepath)

    mock_open_file.assert_called_once_with(filepath, "w", encoding="utf-8")
    args, _ = mock_json_dump.call_args
    dumped_data = args[0]
    assert isinstance(dumped_data, dict)
    assert "machines" in dumped_data
    assert len(dumped_data["machines"]) == 2
    # Example check for one machine's data
    hamilton_state = next(
      m for m in dumped_data["machines"] if m["name"] == "Hamilton_STAR"
    )
    assert hamilton_state["pylabrobot_fqn"] == "mock.MockLiquidHandler"

  @patch("builtins.open", new_callable=MagicMock)  # Corrected new_callable
  @patch("json.load")
  # Patching for _get_class_from_fqn which uses importlib.import_module and getattr
  @patch("praxis.backend.core.workcell_runtime.importlib.import_module")
  @patch("praxis.backend.core.workcell_runtime.getattr")
  @pytest.mark.asyncio
  async def test_restore_workcell_state(
    self,
    mock_getattr_restore,
    mock_import_module_restore,
    mock_json_load,
    mock_open_file,
    workcell_runtime_fixture,
    mock_pylabrobot_backend,
  ):
    """Test restoring workcell state from a file."""
    filepath = "/path/to/backup.json"

    mock_serialized_state = {
      "machines": [
        {
          "name": "Hamilton_STAR",
          "is_connected": False,
          "type": "liquid_handler",
          "pylabrobot_fqn": "mock.MockLiquidHandler",
          "backend_name": "hamilton_backend",
          "settings": {},
        },
        {
          "name": "ClarioStar",
          "is_connected": False,
          "type": "plate_reader",
          "pylabrobot_fqn": "mock.MockPlateReader",
          "backend_name": "clariostar_backend",
          "settings": {},
        },
      ],
      "resources": [],  # Assuming resources are handled if present in serialized state
    }
    mock_json_load.return_value = mock_serialized_state

    # Configure mocks for importlib.import_module and getattr used by _get_class_from_fqn
    def getattr_side_effect_restore(module_obj, class_name_str):
      if class_name_str == "MockLiquidHandler":
        return MockLiquidHandler
      if class_name_str == "MockPlateReader":
        return MockPlateReader
      raise AttributeError(f"getattr_side_effect_restore doesn't know {class_name_str}")

    mock_getattr_restore.side_effect = getattr_side_effect_restore
    mock_import_module_restore.return_value = MagicMock()  # Mocked module object

    with patch.object(
      workcell_runtime_fixture,
      "_get_or_create_backend_instance",
      return_value=mock_pylabrobot_backend,
    ):
      await workcell_runtime_fixture.restore_workcell_state(filepath)

    mock_open_file.assert_called_once_with(filepath, "r", encoding="utf-8")
    mock_json_load.assert_called_once()

    assert "Hamilton_STAR" in workcell_runtime_fixture.live_machines
    restored_hamilton = workcell_runtime_fixture.get_machine("Hamilton_STAR")
    assert isinstance(restored_hamilton, MockLiquidHandler)
    assert (
      restored_hamilton.is_connected
    )  # deserialize_state should be called, then setup

    assert "ClarioStar" in workcell_runtime_fixture.live_machines
    restored_clariostar = workcell_runtime_fixture.get_machine("ClarioStar")
    assert isinstance(restored_clariostar, MockPlateReader)
    assert restored_clariostar.is_connected


# Add logging import for the fixture
import logging
