# pylint: disable=redefined-outer-name, protected-access, unused-argument, too-many-arguments, invalid-name
"""Unit tests for the WorkcellRuntime component."""

import uuid
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest
from pylabrobot.resources import Coordinate, Deck

from praxis.backend.core.protocols.workcell import IWorkcell
from praxis.backend.core.workcell_runtime import WorkcellRuntime, _get_class_from_fqn
from praxis.backend.models.orm.deck import DeckDefinitionOrm
from praxis.backend.models.orm.machine import MachineOrm, MachineStatusEnum
from praxis.backend.models.orm.resource import ResourceOrm, ResourceStatusEnum
from praxis.backend.models.pydantic_internals.deck import PositioningConfig
from praxis.backend.services.deck import DeckService
from praxis.backend.services.deck_type_definition import DeckTypeDefinitionCRUDService
from praxis.backend.services.machine import MachineService
from praxis.backend.services.resource import ResourceService
from praxis.backend.services.workcell import WorkcellService
from praxis.backend.utils.errors import WorkcellRuntimeError

# Correctly import the distinct mock classes
from tests.core.workcell_tests import MockBackend, MockMachineResource, MockPureResource


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
def mock_main_workcell() -> MagicMock:
    """Fixture for a mock core Workcell object."""
    return MagicMock(spec=IWorkcell)


@pytest.fixture
def mock_deck_service() -> MagicMock:
    """Fixture for a mock DeckService."""
    return MagicMock(spec=DeckService)


@pytest.fixture
def mock_machine_service() -> MagicMock:
    """Fixture for a mock MachineService."""
    return MagicMock(spec=MachineService)


@pytest.fixture
def mock_resource_service() -> MagicMock:
    """Fixture for a mock ResourceService."""
    return MagicMock(spec=ResourceService)


@pytest.fixture
def mock_deck_type_definition_service() -> MagicMock:
    """Fixture for a mock DeckTypeDefinitionCRUDService."""
    return MagicMock(spec=DeckTypeDefinitionCRUDService)


@pytest.fixture
def mock_workcell_service() -> MagicMock:
    """Fixture for a mock WorkcellService."""
    return MagicMock(spec=WorkcellService)


@pytest.fixture
def workcell_runtime(
    mock_db_session_factory,
    mock_main_workcell,
    mock_deck_service,
    mock_machine_service,
    mock_resource_service,
    mock_deck_type_definition_service,
    mock_workcell_service,
) -> WorkcellRuntime:
    """Fixture for a WorkcellRuntime instance with mocked dependencies."""
    return WorkcellRuntime(
        db_session_factory=mock_db_session_factory,
        workcell=mock_main_workcell,
        deck_service=mock_deck_service,
        machine_service=mock_machine_service,
        resource_service=mock_resource_service,
        deck_type_definition_service=mock_deck_type_definition_service,
        workcell_service=mock_workcell_service,
    )


# --- Tests for Helper Functions ---


def test_get_class_from_fqn_success() -> None:
    """Test that _get_class_from_fqn successfully imports and returns a class."""
    cls = _get_class_from_fqn("unittest.mock.MagicMock")
    assert cls is MagicMock


def test_get_class_from_fqn_failure() -> None:
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

    async def test_link_workcell_to_db_creates_new(
        self, workcell_runtime: WorkcellRuntime
    ) -> None:
        """Test that a new workcell is created in the DB if one doesn't exist."""
        workcell_runtime.workcell_svc.read_state.return_value = None  # No prior state
        mock_created_orm = MagicMock(accession_id=uuid.uuid4())
        workcell_runtime.workcell_svc.create.return_value = mock_created_orm

        await workcell_runtime._link_workcell_to_db()

        workcell_runtime.workcell_svc.create.assert_awaited_once()
        assert workcell_runtime._workcell_db_accession_id == mock_created_orm.accession_id
        workcell_runtime._main_workcell.load_all_state.assert_not_called()

    async def test_link_workcell_to_db_loads_existing(
        self, workcell_runtime: WorkcellRuntime
    ) -> None:
        """Test that existing state is loaded from the DB."""
        existing_state = {"some_state": "value"}
        workcell_runtime.workcell_svc.read_state.return_value = existing_state
        mock_created_orm = MagicMock(accession_id=uuid.uuid4())
        workcell_runtime.workcell_svc.create.return_value = mock_created_orm

        await workcell_runtime._link_workcell_to_db()

        workcell_runtime.workcell_svc.create.assert_awaited_once()  # Still links
        workcell_runtime._main_workcell.load_all_state.assert_called_once_with(
            existing_state
        )

    @patch("asyncio.create_task")
    async def test_start_and_stop_state_sync(
        self, mock_create_task, workcell_runtime: WorkcellRuntime
    ) -> None:
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

    async def test_initialize_machine_resource_success(
        self, mock_get_fqn, workcell_runtime: WorkcellRuntime, mock_main_workcell
    ) -> None:
        """Test the successful initialization of a machine that is also a resource."""
        machine_id = uuid.uuid4()
        mock_machine_orm = MagicMock(
            spec=MachineOrm,
            accession_id=machine_id,
            name="TestBot",
            fqn="my_module.MockMachineResource",
            properties_json={},
            is_resource=True,  # This machine is also a resource
        )
        mock_get_fqn.return_value = MockMachineResource

        initialized_machine = await workcell_runtime.initialize_machine(mock_machine_orm)

        assert isinstance(initialized_machine, MockMachineResource)
        mock_get_fqn.assert_called_with("my_module.MockMachineResource")
        assert hasattr(initialized_machine, "setup")
        assert workcell_runtime._active_machines[machine_id] is initialized_machine
        mock_main_workcell.add_asset.assert_called_once_with(initialized_machine)
        workcell_runtime.machine_svc.update_machine_status.assert_awaited_with(
            ANY, machine_id, MachineStatusEnum.AVAILABLE, ANY
        )

    async def test_initialize_machine_fails_on_setup(
        self, mock_get_fqn, workcell_runtime: WorkcellRuntime
    ) -> None:
        """Test that initialization fails if the machine's setup method fails."""
        machine_id = uuid.uuid4()
        mock_machine_orm = MagicMock(
            spec=MachineOrm,
            accession_id=machine_id,
            name="FailyBot",
            fqn="my_module.FailyMachine",
        )
        mock_failing_machine_cls = MagicMock()
        mock_failing_machine_cls.return_value.setup.side_effect = ConnectionError(
            "Failed to connect"
        )
        mock_get_fqn.return_value = mock_failing_machine_cls

        with pytest.raises(WorkcellRuntimeError, match="Failed to call setup()"):
            await workcell_runtime.initialize_machine(mock_machine_orm)

        workcell_runtime.machine_svc.update_machine_status.assert_awaited_with(
            ANY, machine_id, MachineStatusEnum.ERROR, ANY
        )

    async def test_create_or_get_resource_success(
        self, mock_get_fqn, workcell_runtime: WorkcellRuntime, mock_main_workcell
    ) -> None:
        """Test successful creation of a new pure resource."""
        resource_id = uuid.uuid4()
        mock_resource_orm = MagicMock(
            spec=ResourceOrm, accession_id=resource_id, name="TestPlate", is_machine=False
        )
        mock_get_fqn.return_value = MockPureResource

        initialized_resource = await workcell_runtime.create_or_get_resource(
            mock_resource_orm, "pylabrobot.resources.Plate"
        )

        assert isinstance(initialized_resource, MockPureResource)
        assert workcell_runtime._active_resources[resource_id] is initialized_resource
        mock_main_workcell.add_asset.assert_called_once_with(initialized_resource)
        workcell_runtime.resource_svc.update.assert_not_called()

    async def test_get_active_machine_failure(
        self, workcell_runtime: WorkcellRuntime
    ) -> None:
        """Test that getting a non-existent active machine raises an error."""
        with pytest.raises(WorkcellRuntimeError, match="not found in active machines"):
            workcell_runtime.get_active_machine(uuid.uuid4())

    async def test_shutdown_machine(self, mock_get_fqn, workcell_runtime: WorkcellRuntime) -> None:
        """Test successfully shutting down a machine."""
        machine_id = uuid.uuid4()
        mock_plr_machine = MockMachineResource(name="TestBot", backend=MockBackend())
        workcell_runtime._active_machines[machine_id] = mock_plr_machine

        await workcell_runtime.shutdown_machine(machine_id)

        assert hasattr(mock_plr_machine, "stop")
        assert machine_id not in workcell_runtime._active_machines
        workcell_runtime.machine_svc.update_machine_status.assert_awaited_with(
            ANY, machine_id, MachineStatusEnum.OFFLINE, "Machine shut down."
        )