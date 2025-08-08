from unittest.mock import MagicMock, patch

import pytest  # type: ignore

# Class to test
from praxis.backend.core.workcell_runtime import WorkcellRuntime

# Dependent ORM-like Mocks
ManagedDeviceOrmMock = MagicMock
ResourceOrmMock = MagicMock

# Enums
from praxis.backend.database_models.asset_management_orm import (
  ManagedDeviceStatusEnum,
  ResourceStatusEnum,
)


# Mock PLR classes
@pytest.fixture
def mock_plr_resource_class():
  klass = MagicMock()
  klass.return_value = MagicMock(name="mock_plr_resource")
  return klass


@pytest.fixture
def mock_plr_machine_backend_class(mock_plr_resource_class: MagicMock):  # So it can be a Resource
  # A PLR "machine backend" can be a machine that is also a Resource, or just a backend class
  # Let's make it behave like a machine with a setup method
  klass = MagicMock()
  instance = MagicMock(name="mock_plr_machine_instance")
  instance.setup = MagicMock()
  instance.stop = MagicMock()
  # If it's also a Deck, it needs deck methods
  instance.assign_child_resource = MagicMock()
  instance.unassign_child_resource = MagicMock()
  instance.__getitem__ = MagicMock(return_value=None)  # For deck[slot] access

  # Make it an instance of the mocked Resource class for isinstance checks if needed
  # This is a bit of a hack for isinstance(backend_instance, Deck)
  # A better way might be to have different fixtures for Deck vs non-Deck machines.
  # For now, let's assume it can be identified  if needed by checking class name.
  def_instance = klass.return_value
  def_instance.name = "mock_plr_machine_instance"
  def_instance.setup = MagicMock()
  def_instance.stop = MagicMock()
  def_instance.assign_child_resource = MagicMock()
  def_instance.unassign_child_resource = MagicMock()
  def_instance.__getitem__ = MagicMock(return_value=None)

  klass.return_value = def_instance
  return klass


@pytest.fixture
def mock_plr_deck_class(
  mock_plr_machine_backend_class: MagicMock,
):  # Inherits general machine behavior
  # Specifically for Deck. The instance from mock_plr_machine_backend_class can serve as this.
  # We ensure its type name implies it's a Deck for isinstance checks in WCR.
  # WorkcellRuntime uses isinstance(backend_instance, Deck).
  # We will patch Deck from pylabrobot.resources for this test.
  with patch("praxis.backend.core.workcell_runtime.Deck", spec=True) as MockDeckSpec:
    # Make our mock_plr_machine_backend_class's instance also an instance of this MockDeckSpec
    # This is tricky. A simpler way is to check class name if isinstance is problematic with mocks.
    # Or, the _get_class_from_fqn can return this MockDeckSpec if FQN matches a deck.
    MockDeckSpec.return_value = (
      mock_plr_machine_backend_class.return_value
    )  # Share the same instance
    yield mock_plr_machine_backend_class  # Returns the constructor mock


@pytest.fixture
def mock_ads_service_wcr():
  # Patch 'ads' where it's used inside workcell_runtime.py
  with patch("praxis.backend.core.workcell_runtime.ads") as mock_ads:
    mock_ads.update_managed_machine_status.return_value = MagicMock(spec=ManagedDeviceOrmMock)
    mock_ads.update_resource_location_and_status.return_value = MagicMock(spec=ResourceOrmMock)
    yield mock_ads


@pytest.fixture
def workcell_runtime(mock_ads_service_wcr: MagicMock):
  # db_session is not strictly used by all methods if ads is mocked, but pass a mock
  return WorkcellRuntime(db_session=MagicMock())


class TestWorkcellRuntimeDeviceHandling:
  @patch("praxis.backend.core.workcell_runtime._get_class_from_fqn")
  def test_initialize_machine_backend_success(
    self,
    mock_get_class: MagicMock,
    mock_plr_machine_backend_class: MagicMock,
    workcell_runtime: WorkcellRuntime,
    mock_ads_service_wcr: MagicMock,
  ) -> None:
    mock_get_class.return_value = mock_plr_machine_backend_class
    machine_orm = ManagedDeviceOrmMock(
      id=1, name="Device1", fqn="some.DeviceClass", properties_json={"param": "value"},
    )

    backend_instance = workcell_runtime.initialize_machine_backend(machine_orm)

    mock_get_class.assert_called_once_with("some.DeviceClass")
    # Check if constructor was called with name and params from properties_json
    # This depends on how _get_class_from_fqn and constructor inspection work.
    # For now, assume it's called. A more specific check would be on mock_plr_machine_backend_class.
    mock_plr_machine_backend_class.assert_called_with(
      name="Device1",
      param="value",
    )  # Assuming name is passed, and param from config

    assert backend_instance is not None
    assert backend_instance.setup.called  # Check if setup was called
    assert workcell_runtime._active_machine_backends[1] is backend_instance
    mock_ads_service_wcr.update_managed_machine_status.assert_called_once_with(
      workcell_runtime.db_session,
      1,
      ManagedDeviceStatusEnum.AVAILABLE,
      "Backend initialized.",
    )

  @patch("praxis.backend.core.workcell_runtime._get_class_from_fqn")
  def test_initialize_machine_backend_is_deck(
    self,
    mock_get_class: MagicMock,
    mock_plr_deck_class: MagicMock,  # Use deck-specific mock
    workcell_runtime: WorkcellRuntime,
    mock_ads_service_wcr: MagicMock,
  ) -> None:
    # For this test, we need _get_class_from_fqn to return a class that, when instantiated,
    # IS a Deck. We mock Deck itself for the isinstance check.
    with patch("praxis.backend.core.workcell_runtime.Deck", spec=True) as ActualDeckClassMocked:
      # Make our mock_plr_deck_class's instance appear as an instance of the actual (mocked) Deck
      mock_instance = (
        mock_plr_deck_class.return_value
      )  # This is the instance of MagicMock that is the "class"
      mock_instance.name = "TestDeck"  # Ensure it has a name attribute like a Resource

      # Configure _get_class_from_fqn to return our mock_plr_deck_class (which is a MagicMock itself)
      mock_get_class.return_value = mock_plr_deck_class

      # Make instances created by mock_plr_deck_class also be instances of ActualDeckClassMocked
      # This is the tricky part for isinstance checks with mocks.
      # A simpler way if this fails is to check the class_name string.
      # For now, we rely on the spec of Deck making isinstance work with its instances.
      # The worker's report on WCR v3 said "isinstance(backend_instance, Deck)" is used.
      # To make isinstance(mock_plr_deck_class.return_value, ActualDeckClassMocked) true:
      mock_plr_deck_class.return_value.__class__ = (
        ActualDeckClassMocked  # Make the instance's class the mocked Deck
      )

      machine_orm = ManagedDeviceOrmMock(
        id=2,
        name="MainDeck",
        fqn="pylabrobot.resources.deck.Deck",
        properties_json={},
      )

      backend_instance = workcell_runtime.initialize_machine_backend(machine_orm)

      assert workcell_runtime._main_deck_plr_object is backend_instance
      assert workcell_runtime._main_deck_machine_orm_accession_id == 2

  @patch("praxis.backend.core.workcell_runtime._get_class_from_fqn")
  def test_initialize_machine_backend_failure(
    self,
    mock_get_class: MagicMock,
    workcell_runtime: WorkcellRuntime,
    mock_ads_service_wcr: MagicMock,
  ) -> None:
    mock_get_class.side_effect = ImportError("Module not found")
    machine_orm = ManagedDeviceOrmMock(id=3, name="ErrorDevice", fqn="bad.fqn.Device")

    backend_instance = workcell_runtime.initialize_machine_backend(machine_orm)

    assert backend_instance is None
    assert 3 not in workcell_runtime._active_machine_backends
    mock_ads_service_wcr.update_managed_machine_status.assert_called_once_with(
      workcell_runtime.db_session,
      3,
      ManagedDeviceStatusEnum.ERROR,
      "Backend init failed: Module not found",
    )

  def test_shutdown_machine_backend(
    self, workcell_runtime: WorkcellRuntime, mock_ads_service_wcr: MagicMock,
  ) -> None:
    mock_backend_instance = MagicMock()
    mock_backend_instance.stop = MagicMock()
    workcell_runtime._active_machine_backends[1] = mock_backend_instance

    workcell_runtime.shutdown_machine_backend(1)

    assert 1 not in workcell_runtime._active_machine_backends
    mock_backend_instance.stop.assert_called_once()
    mock_ads_service_wcr.update_managed_machine_status.assert_called_once_with(
      workcell_runtime.db_session,
      1,
      ManagedDeviceStatusEnum.OFFLINE,
      "Backend shut down.",
    )


class TestWorkcellRuntimeResourceHandling:
  @patch("praxis.backend.core.workcell_runtime._get_class_from_fqn")
  def test_create_or_get_resource_plr_object_success(
    self,
    mock_get_class: MagicMock,
    mock_plr_resource_class: MagicMock,
    workcell_runtime: WorkcellRuntime,
    mock_ads_service_wcr: MagicMock,  # Added ads mock
  ) -> None:
    mock_get_class.return_value = mock_plr_resource_class
    resource_orm = ResourceOrmMock(
      id=1,
      name="Plate1",
      resource_definition_name="some.ResourceFQN",
    )  # Name used for instance

    plr_object = workcell_runtime.create_or_get_resource_plr_object(
      resource_orm, "some.ResourceFQN",
    )  # Pass FQN

    mock_get_class.assert_called_once_with("some.ResourceFQN")
    mock_plr_resource_class.assert_called_once_with(name="Plate1")
    assert plr_object is not None
    assert workcell_runtime._active_plr_resource_objects[1] is plr_object

  @patch("praxis.backend.core.workcell_runtime._get_class_from_fqn")
  def test_create_or_get_resource_plr_object_failure_sets_status_error(
    self,
    mock_get_class: MagicMock,
    workcell_runtime: WorkcellRuntime,
    mock_ads_service_wcr: MagicMock,
  ) -> None:
    mock_get_class.side_effect = ImportError("Cannot import resource class")
    resource_orm = ResourceOrmMock(
      id=2, name="BadPlate", resource_definition_name="bad.fqn.Resource",
    )

    plr_object = workcell_runtime.create_or_get_resource_plr_object(
      resource_orm, "bad.fqn.Resource",
    )

    assert plr_object is None
    assert 2 not in workcell_runtime._active_plr_resource_objects
    # Check that status was updated to ERROR
    mock_ads_service_wcr.update_resource_location_and_status.assert_called_once_with(
      db=workcell_runtime.db_session,
      resource_accession_id=2,
      new_status=ResourceStatusEnum.ERROR,
      status_details="Failed to create PLR object for 'BadPlate' using FQN 'bad.fqn.Resource': Cannot import resource class",
    )

  @patch(
    "praxis.backend.core.workcell_runtime.Deck", spec=True,
  )  # Mock the Deck class itself for isinstance checks
  def test_assign_resource_to_deck_slot(
    self,
    MockActualDeck: MagicMock,  # This is the mocked Deck class from the patch
    workcell_runtime: WorkcellRuntime,
    mock_ads_service_wcr: MagicMock,
  ) -> None:
    # Setup a mock deck object that is an instance of the (mocked) Deck
    mock_deck = MagicMock(spec=MockActualDeck)  #  that passes isinstance checks
    mock_deck.name = "TestDeck"
    mock_deck.assign_child_resource = MagicMock()

    workcell_runtime._active_machine_backends[10] = mock_deck  # Assume deck ID 10 is active

    mock_resource_plr_obj = MagicMock(
      spec=workcell_runtime.Resource,
    )  # from praxis.backend.core.workcell_runtime
    resource_accession_id = 1

    workcell_runtime.assign_resource_to_deck_slot(
      10, "A1", mock_resource_plr_obj, resource_accession_id,
    )

    mock_deck.assign_child_resource.assert_called_once_with(
      resource=mock_resource_plr_obj, slot="A1",
    )
    mock_ads_service_wcr.update_resource_location_and_status.assert_called_once_with(
      workcell_runtime.db_session,
      resource_accession_id,
      ResourceStatusEnum.AVAILABLE_ON_DECK,
      location_machine_accession_id=10,
      current_deck_slot_name="A1",
    )


# TODO: More tests:
# - get_active_machine_backend, get_active_resource_plr_object
# - clear_deck_slot
# - execute_machine_action (basic getattr call)
# - shutdown_all_backends
# - get_main_deck_plr_object (interaction with ads if deck not active)
# - Complex constructor inspection in initialize_machine_backend
