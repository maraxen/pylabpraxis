# pylint: disable=redefined-outer-name, protected-access, unused-argument, too-many-arguments, invalid-name
"""Unit tests for the WorkcellRuntime component."""

import asyncio
import uuid
from unittest.mock import ANY, AsyncMock, MagicMock, call, patch

import pytest
from pylabrobot.resources import Coordinate, Deck

from praxis.backend.core.workcell import Workcell
from praxis.backend.core.workcell_runtime import WorkcellRuntime, _get_class_from_fqn
from praxis.backend.models import (
  DeckTypeDefinitionOrm,
  MachineOrm,
  MachineStatusEnum,
  PositioningConfig,
  ResourceInstanceOrm,
  ResourceInstanceStatusEnum,
)
from praxis.backend.utils.errors import WorkcellRuntimeError

# Correctly import the distinct mock classes
from .test_workcell import MockBackend, MockMachineResource, MockPureResource

# --- Fixtures ---


@pytest.fixture
def mock_db_session_factory():
  """Fixture for a mock SQLAlchemy async session factory."""
  mock_session = AsyncMock()
  mock_factory = MagicMock(return_value=mock_session)
  # To make it usable in "async with"
  mock_session.__aenter__.return_value = mock_session
  return mock_factory


@pytest.fixture
def mock_main_workcell():
  """Fixture for a mock core Workcell object."""
  return MagicMock(spec=Workcell)


@pytest.fixture
@patch("praxis.backend.core.workcell_runtime.Workcell")
def workcell_runtime(mock_workcell_cls, mock_db_session_factory) -> WorkcellRuntime:
  """Fixture for a WorkcellRuntime instance with mocked dependencies."""
  mock_workcell_instance = mock_workcell_cls.return_value
  runtime = WorkcellRuntime(
    db_session_factory=mock_db_session_factory,
    workcell_name="test_runtime",
    workcell_save_file="/tmp/test_runtime.json",
  )
  runtime._main_workcell = mock_workcell_instance
  return runtime


# --- Tests for Helper Functions ---


def test_get_class_from_fqn_success():
  """Test that _get_class_from_fqn successfully imports and returns a class."""
  cls = _get_class_from_fqn("unittest.mock.MagicMock")
  assert cls is MagicMock


def test_get_class_from_fqn_failure():
  """Test that _get_class_from_fqn raises ValueError for an invalid FQN."""
  with pytest.raises(ValueError):
    _get_class_from_fqn("invalid_fqn")
  with pytest.raises(ImportError):
    _get_class_from_fqn("non.existent.module.ClassName")
  with pytest.raises(AttributeError):
    _get_class_from_fqn("unittest.mock.NonExistentClass")


# --- Test Classes ---


@pytest.mark.asyncio
class TestWorkcellRuntimeLifecycle:
  """Tests for the startup and shutdown of the WorkcellRuntime."""

  @patch("praxis.backend.services.create_workcell")
  @patch("praxis.backend.services.read_workcell_state", new_callable=AsyncMock)
  async def test_link_workcell_to_db_creates_new(
    self, mock_read_state, mock_create_workcell, workcell_runtime
  ):
    """Test that a new workcell is created in the DB if one doesn't exist."""
    mock_read_state.return_value = None  # No prior state
    mock_created_orm = MagicMock(accession_id=uuid.uuid4())
    mock_create_workcell.return_value = mock_created_orm

    await workcell_runtime._link_workcell_to_db()

    mock_create_workcell.assert_awaited_once()
    assert workcell_runtime._workcell_db_accession_id == mock_created_orm.accession_id
    workcell_runtime._main_workcell.load_all_state.assert_not_called()

  @patch("praxis.backend.services.create_workcell")
  @patch("praxis.backend.services.read_workcell_state", new_callable=AsyncMock)
  async def test_link_workcell_to_db_loads_existing(
    self, mock_read_state, mock_create_workcell, workcell_runtime
  ):
    """Test that existing state is loaded from the DB."""
    existing_state = {"some_state": "value"}
    mock_read_state.return_value = existing_state
    mock_created_orm = MagicMock(accession_id=uuid.uuid4())
    mock_create_workcell.return_value = mock_created_orm

    await workcell_runtime._link_workcell_to_db()

    mock_create_workcell.assert_awaited_once()  # Still links
    workcell_runtime._main_workcell.load_all_state.assert_called_once_with(
      existing_state
    )

  @patch("asyncio.create_task")
  async def test_start_and_stop_state_sync(self, mock_create_task, workcell_runtime):
    """Test the starting and stopping of the state sync task."""
    workcell_runtime._link_workcell_to_db = AsyncMock()
    mock_task = MagicMock()
    mock_task.done.return_value = False
    mock_create_task.return_value = mock_task

    await workcell_runtime.start_workcell_state_sync()
    workcell_runtime._link_workcell_to_db.assert_awaited_once()
    mock_create_task.assert_called_once()
    assert workcell_runtime._state_sync_task is mock_task

    await workcell_runtime.stop_workcell_state_sync()
    mock_task.cancel.assert_called_once()


@pytest.mark.asyncio
@patch("praxis.backend.core.workcell_runtime._get_class_from_fqn")
class TestAssetLifecycle:
  """Tests for initializing, getting, and shutting down assets."""

  @patch("praxis.backend.services.update_machine_status")
  async def test_initialize_machine_resource_success(
    self, mock_update_status, mock_get_fqn, workcell_runtime, mock_main_workcell
  ):
    """Test the successful initialization of a machine that is also a resource."""
    machine_id = uuid.uuid4()
    mock_machine_orm = MagicMock(
      spec=MachineOrm,
      accession_id=machine_id,
      user_friendly_name="TestBot",
      python_fqn="my_module.MockMachineResource",
      backend_config_json={},
      is_resource=True,  # This machine is also a resource
    )
    # Use the mock that has both machine and resource properties
    mock_get_fqn.return_value = MockMachineResource

    initialized_machine = await workcell_runtime.initialize_machine(mock_machine_orm)

    assert isinstance(initialized_machine, MockMachineResource)
    mock_get_fqn.assert_called_with("my_module.MockMachineResource")
    # initialize_machine calls setup(), which is mocked in MockPlrMachine
    assert hasattr(initialized_machine, "setup")
    assert workcell_runtime._active_machines[machine_id] is initialized_machine
    mock_main_workcell.add_asset.assert_called_once_with(initialized_machine)
    mock_update_status.assert_awaited_with(
      ANY, machine_id, MachineStatusEnum.AVAILABLE, ANY
    )

  @patch("praxis.backend.services.update_machine_status")
  async def test_initialize_machine_fails_on_setup(
    self, mock_update_status, mock_get_fqn, workcell_runtime
  ):
    """Test that initialization fails if the machine's setup method fails."""
    machine_id = uuid.uuid4()
    mock_machine_orm = MagicMock(
      spec=MachineOrm,
      accession_id=machine_id,
      user_friendly_name="FailyBot",
      python_fqn="my_module.FailyMachine",
    )
    # This mock will be returned by the patched _get_class_from_fqn
    mock_failing_machine_cls = MagicMock()
    mock_failing_machine_cls.return_value.setup.side_effect = ConnectionError(
      "Failed to connect"
    )
    mock_get_fqn.return_value = mock_failing_machine_cls

    with pytest.raises(WorkcellRuntimeError, match="Failed to call setup()"):
      await workcell_runtime.initialize_machine(mock_machine_orm)

    mock_update_status.assert_awaited_with(
      ANY, machine_id, MachineStatusEnum.ERROR, ANY
    )

  @patch("praxis.backend.services.update_resource_instance_location_and_status")
  async def test_create_or_get_resource_success(
    self, mock_update_status, mock_get_fqn, workcell_runtime, mock_main_workcell
  ):
    """Test successful creation of a new pure resource."""
    resource_id = uuid.uuid4()
    mock_resource_orm = MagicMock(
      spec=ResourceInstanceOrm,
      accession_id=resource_id,
      user_assigned_name="TestPlate",
      is_machine=False,
    )
    # Use the pure resource mock
    mock_get_fqn.return_value = MockPureResource

    initialized_resource = await workcell_runtime.create_or_get_resource(
      mock_resource_orm, "pylabrobot.resources.Plate"
    )

    assert isinstance(initialized_resource, MockPureResource)
    assert workcell_runtime._active_resources[resource_id] is initialized_resource
    mock_main_workcell.add_asset.assert_called_once_with(initialized_resource)
    mock_update_status.assert_not_called()

  async def test_get_active_machine_failure(self, workcell_runtime):
    """Test that getting a non-existent active machine raises an error."""
    with pytest.raises(WorkcellRuntimeError, match="not found in active machines"):
      workcell_runtime.get_active_machine(uuid.uuid4())

  @patch("praxis.backend.services.update_machine_status")
  async def test_shutdown_machine(
    self, mock_update_status, mock_get_fqn, workcell_runtime
  ):
    """Test successfully shutting down a machine."""
    machine_id = uuid.uuid4()
    mock_plr_machine = MockMachineResource(name="TestBot", backend=MockBackend())
    workcell_runtime._active_machines[machine_id] = mock_plr_machine

    await workcell_runtime.shutdown_machine(machine_id)

    # stop() is mocked in the base MockPlrMachine class
    assert hasattr(mock_plr_machine, "stop")
    assert machine_id not in workcell_runtime._active_machines
    mock_update_status.assert_awaited_with(
      ANY, machine_id, MachineStatusEnum.OFFLINE, "Machine shut down."
    )


@pytest.mark.asyncio
class TestDeckOperations:
  """Tests for operations involving decks and resources on them."""

  @pytest.fixture
  def mock_deck(self):
    """Fixture for a mock PyLabRobot Deck."""
    deck = MagicMock(spec=Deck)
    deck.assign_child_resource = MagicMock()
    return deck

  @pytest.fixture
  def setup_assets(self, workcell_runtime, mock_deck):
    """Helper fixture to populate runtime with a deck and a resource."""
    deck_id = uuid.uuid4()
    resource_id = uuid.uuid4()
    workcell_runtime._active_decks[deck_id] = mock_deck
    workcell_runtime._active_resources[resource_id] = MockPureResource(
      name="plate_to_assign"
    )
    return deck_id, resource_id, mock_deck

  @patch("praxis.backend.services.read_deck_instance")
  @patch("praxis.backend.services.read_deck_type_definition")
  @patch("praxis.backend.services.update_resource_instance_location_and_status")
  async def test_assign_resource_to_deck_by_position(
    self,
    mock_update_status,
    mock_read_deck_type,
    mock_read_deck,
    workcell_runtime,
    setup_assets,
  ):
    """Test assigning a resource to a deck using a position identifier."""
    deck_id, resource_id, mock_deck = setup_assets
    position_id = "A1"

    mock_read_deck.return_value = MagicMock(
      accession_id=deck_id, deck_type_definition_accession_id=uuid.uuid4()
    )
    mock_deck_type_orm = MagicMock(
      spec=DeckTypeDefinitionOrm,
      accession_id=uuid.uuid4(),
      positioning_config_json=PositioningConfig(
        method_name="get_item", arg_name="identifier", arg_type="str", params={}
      ).model_dump(),
    )
    mock_read_deck_type.return_value = mock_deck_type_orm
    mock_deck.get_item.return_value = Coordinate(10, 20, 30)

    await workcell_runtime.assign_resource_to_deck(
      resource_instance_orm_accession_id=resource_id,
      target=deck_id,
      position_accession_id=position_id,
    )

    mock_deck.get_item.assert_called_once_with(identifier=position_id)
    mock_deck.assign_child_resource.assert_called_once()
    args, kwargs = mock_deck.assign_child_resource.call_args
    assert isinstance(kwargs["resource"], MockPureResource)
    assert kwargs["location"] == Coordinate(10, 20, 30)
    mock_update_status.assert_awaited_once_with(
      ANY,
      resource_id,
      ResourceInstanceStatusEnum.AVAILABLE_ON_DECK,
      location_machine_accession_id=deck_id,
      current_deck_position_name="A1",
    )

  @patch("praxis.backend.services.update_resource_instance_location_and_status")
  async def test_clear_deck_position(
    self, mock_update_status, workcell_runtime, setup_assets
  ):
    """Test clearing a resource from a deck position."""
    deck_id, resource_id, mock_deck = setup_assets
    position_name = "A1"
    resource_in_pos = workcell_runtime.get_active_resource(resource_id)
    mock_deck.get_resource.return_value = resource_in_pos

    await workcell_runtime.clear_deck_position(
      deck_id, position_name, resource_instance_orm_accession_id=resource_id
    )

    mock_deck.unassign_child_resource.assert_called_once_with(resource_in_pos)
    mock_update_status.assert_awaited_with(
      ANY,
      resource_id,
      ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
      location_machine_accession_id=None,
      current_deck_position_name=None,
    )
