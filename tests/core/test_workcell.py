# pylint: disable=redefined-outer-name, protected-access
"""Unit tests for the Workcell and WorkcellView classes."""

import pytest
from pylabrobot.machines import Machine
from pylabrobot.machines.backends import MachineBackend
from pylabrobot.resources import Resource

from praxis.backend.core.workcell import Workcell
from praxis.backend.models import (
  ResourceCategoryEnum,
)


class MockBackend(MachineBackend):
  """A mock backend for testing."""

  def __init__(self):
    """Initialize the mock backend."""
    super().__init__()

  async def setup(self):
    """Set up the mock backend (no-op)."""
    pass

  async def stop(self):
    """Stop the mock backend (no-op)."""
    pass


@pytest.fixture
def mock_backend() -> MockBackend:
  """Fixture for a mock backend instance."""
  return MockBackend()


class MockPureMachine(Machine):
  """A mock machine that is not a resource."""

  def __init__(self, backend: MockBackend):
    """Initialize the mock pure machine with a backend."""
    super().__init__(backend=backend)


class MockPureResource(Resource):
  """A mock resource that is not a machine."""

  def __init__(self, name: str, category: str = "plates", **kwargs):
    """Initialize the mock pure resource with a name and category."""
    super().__init__(
      name=name, size_x=10, size_y=10, size_z=10, category=category, **kwargs
    )


class MockMachineResource(Resource, Machine):
  """A mock asset that is both a machine and a resource."""

  def __init__(
    self, name: str, backend: MockBackend, category: str = "robot_arms", **kwargs
  ):
    """Initialize the mock machine resource with a name, backend, and category."""
    Resource.__init__(
      self, name=name, size_x=1, size_y=1, size_z=1, category=category, **kwargs
    )
    Machine.__init__(self, backend=backend)
    self.state = "default"

  def serialize_state(self) -> dict:
    """Serialize the state of the mock machine resource."""
    return {"name": self.name, "state": self.state}

  def load_state(self, state: dict):
    """Load the state into the mock machine resource."""
    self.state = state.get("state", "loaded_default")


@pytest.fixture
def workcell() -> Workcell:
  """Fixture for a Workcell instance with a temporary save file."""
  return Workcell(name="test_cell", save_file="/tmp/test_cell.json")


class TestWorkcell:
  """Tests for the Workcell container class."""

  def test_add_pure_machine_asset(self, workcell: Workcell, mock_backend: MockBackend):
    """Test adding a machine that is NOT a resource."""
    machine = MockPureMachine(backend=mock_backend)
    workcell.add_asset(machine)
    # Pure machine has no '.name', so it's identified by its hash in the workcell
    asset_key = str(machine.__hash__())
    assert machine in workcell.children
    assert asset_key in workcell
    assert workcell[asset_key] == machine

  def test_add_pure_resource_asset(self, workcell: Workcell):
    """Test adding a resource-only asset to the workcell."""
    resource = MockPureResource(
      name="test_plate", category=ResourceCategoryEnum.PLATE.value
    )
    workcell.add_asset(resource)
    assert resource in workcell.children
    assert "test_plate" in workcell.plates  # type: ignore
    assert workcell.plates["test_plate"] == resource  # type: ignore

  def test_add_machine_resource_asset(
    self, workcell: Workcell, mock_backend: MockBackend
  ):
    """Test adding an asset that is both a Machine and a Resource."""
    machine_resource = MockMachineResource(
      name="robot_arm", backend=mock_backend, category="robot_arms"
    )
    workcell.add_asset(machine_resource)
    assert machine_resource in workcell.children
    assert "robot_arm" in workcell.robot_arms  # type: ignore
    assert workcell.robot_arms["robot_arm"] == machine_resource  # type: ignore
    assert "robot_arm" in workcell.all_machines
