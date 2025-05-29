import pytest # type: ignore
from unittest.mock import MagicMock, patch, call
from typing import Dict, Any, Optional

# Class to test
from praxis.backend.core.workcell_runtime import WorkcellRuntime, _get_class_from_fqn

# Dependent ORM-like Mocks
ManagedDeviceOrmMock = MagicMock
LabwareInstanceOrmMock = MagicMock

# Enums
from praxis.backend.database_models.asset_management_orm import (
    ManagedDeviceStatusEnum, LabwareInstanceStatusEnum
)

# Mock PLR classes
@pytest.fixture
def mock_plr_resource_class():
    klass = MagicMock()
    klass.return_value = MagicMock(name="mock_plr_resource_instance") # Instance
    return klass

@pytest.fixture
def mock_plr_device_backend_class(mock_plr_resource_class: MagicMock): # So it can be a PlrResource
    # A PLR "device backend" can be a machine that is also a Resource, or just a backend class
    # Let's make it behave like a machine with a setup method
    klass = MagicMock()
    instance = MagicMock(name="mock_plr_device_instance")
    instance.setup = MagicMock()
    instance.stop = MagicMock()
    # If it's also a PlrDeck, it needs deck methods
    instance.assign_child_resource = MagicMock()
    instance.unassign_child_resource = MagicMock()
    instance.__getitem__ = MagicMock(return_value=None) # For deck[slot] access
    
    # Make it an instance of the mocked PlrResource class for isinstance checks if needed
    # This is a bit of a hack for isinstance(backend_instance, PlrDeck)
    # A better way might be to have different fixtures for Deck vs non-Deck devices.
    # For now, let's assume it can be identified as PlrDeck if needed by checking class name.
    def_instance = klass.return_value 
    def_instance.name = "mock_plr_device_instance"
    def_instance.setup = MagicMock()
    def_instance.stop = MagicMock()
    def_instance.assign_child_resource = MagicMock()
    def_instance.unassign_child_resource = MagicMock()
    def_instance.__getitem__ = MagicMock(return_value=None)
    
    klass.return_value = def_instance
    return klass


@pytest.fixture
def mock_plr_deck_class(mock_plr_device_backend_class: MagicMock): # Inherits general device behavior
    # Specifically for PlrDeck. The instance from mock_plr_device_backend_class can serve as this.
    # We ensure its type name implies it's a Deck for isinstance checks in WCR.
    # WorkcellRuntime uses isinstance(backend_instance, PlrDeck).
    # We will patch PlrDeck from pylabrobot.resources for this test.
    with patch('praxis.backend.core.workcell_runtime.PlrDeck', spec=True) as MockPlrDeckSpec:
        # Make our mock_plr_device_backend_class's instance also an instance of this MockPlrDeckSpec
        # This is tricky. A simpler way is to check class name if isinstance is problematic with mocks.
        # Or, the _get_class_from_fqn can return this MockPlrDeckSpec if FQN matches a deck.
        MockPlrDeckSpec.return_value = mock_plr_device_backend_class.return_value # Share the same instance
        yield mock_plr_device_backend_class # Returns the constructor mock

@pytest.fixture
def mock_ads_service_wcr():
    # Patch 'ads' where it's used inside workcell_runtime.py
    with patch('praxis.backend.core.workcell_runtime.ads') as mock_ads:
        mock_ads.update_managed_device_status.return_value = MagicMock(spec=ManagedDeviceOrmMock)
        mock_ads.update_labware_instance_location_and_status.return_value = MagicMock(spec=LabwareInstanceOrmMock)
        yield mock_ads

@pytest.fixture
def workcell_runtime(mock_ads_service_wcr: MagicMock):
    # db_session is not strictly used by all methods if ads is mocked, but pass a mock
    return WorkcellRuntime(db_session=MagicMock())

class TestWorkcellRuntimeDeviceHandling:

    @patch('praxis.backend.core.workcell_runtime._get_class_from_fqn')
    def test_initialize_device_backend_success(
        self, mock_get_class: MagicMock, mock_plr_device_backend_class: MagicMock,
        workcell_runtime: WorkcellRuntime, mock_ads_service_wcr: MagicMock
    ):
        mock_get_class.return_value = mock_plr_device_backend_class
        device_orm = ManagedDeviceOrmMock(id=1, user_friendly_name="Device1", pylabrobot_class_name="some.DeviceClass", backend_config_json={"param": "value"})

        backend_instance = workcell_runtime.initialize_device_backend(device_orm)

        mock_get_class.assert_called_once_with("some.DeviceClass")
        # Check if constructor was called with name and params from backend_config_json
        # This depends on how _get_class_from_fqn and constructor inspection work.
        # For now, assume it's called. A more specific check would be on mock_plr_device_backend_class.
        mock_plr_device_backend_class.assert_called_with(name="Device1", param="value") # Assuming name is passed, and param from config
        
        assert backend_instance is not None
        assert backend_instance.setup.called # Check if setup was called
        assert workcell_runtime._active_device_backends[1] is backend_instance
        mock_ads_service_wcr.update_managed_device_status.assert_called_once_with(
            workcell_runtime.db_session, 1, ManagedDeviceStatusEnum.AVAILABLE, "Backend initialized."
        )

    @patch('praxis.backend.core.workcell_runtime._get_class_from_fqn')
    def test_initialize_device_backend_is_deck(
        self, mock_get_class: MagicMock, mock_plr_deck_class: MagicMock, # Use deck-specific mock
        workcell_runtime: WorkcellRuntime, mock_ads_service_wcr: MagicMock
    ):
        # For this test, we need _get_class_from_fqn to return a class that, when instantiated,
        # IS a PlrDeck. We mock PlrDeck itself for the isinstance check.
        with patch('praxis.backend.core.workcell_runtime.PlrDeck', spec=True) as ActualPlrDeckClassMocked:
            # Make our mock_plr_deck_class's instance appear as an instance of the actual (mocked) PlrDeck
            mock_instance = mock_plr_deck_class.return_value # This is the instance of MagicMock that is the "class"
            mock_instance.name = "TestDeckInstance" # Ensure it has a name attribute like a PlrResource
            
            # Configure _get_class_from_fqn to return our mock_plr_deck_class (which is a MagicMock itself)
            mock_get_class.return_value = mock_plr_deck_class 
            
            # Make instances created by mock_plr_deck_class also be instances of ActualPlrDeckClassMocked
            # This is the tricky part for isinstance checks with mocks.
            # A simpler way if this fails is to check the class_name string.
            # For now, we rely on the spec of PlrDeck making isinstance work with its instances.
            # The worker's report on WCR v3 said "isinstance(backend_instance, PlrDeck)" is used.
            # To make isinstance(mock_plr_deck_class.return_value, ActualPlrDeckClassMocked) true:
            mock_plr_deck_class.return_value.__class__ = ActualPlrDeckClassMocked # Make the instance's class the mocked PlrDeck

            device_orm = ManagedDeviceOrmMock(id=2, user_friendly_name="MainDeck", pylabrobot_class_name="pylabrobot.resources.deck.Deck", backend_config_json={})
            
            backend_instance = workcell_runtime.initialize_device_backend(device_orm)

            assert workcell_runtime._main_deck_plr_object is backend_instance
            assert workcell_runtime._main_deck_device_orm_id == 2


    @patch('praxis.backend.core.workcell_runtime._get_class_from_fqn')
    def test_initialize_device_backend_failure(
        self, mock_get_class: MagicMock, workcell_runtime: WorkcellRuntime, mock_ads_service_wcr: MagicMock
    ):
        mock_get_class.side_effect = ImportError("Module not found")
        device_orm = ManagedDeviceOrmMock(id=3, user_friendly_name="ErrorDevice", pylabrobot_class_name="bad.fqn.Device")

        backend_instance = workcell_runtime.initialize_device_backend(device_orm)

        assert backend_instance is None
        assert 3 not in workcell_runtime._active_device_backends
        mock_ads_service_wcr.update_managed_device_status.assert_called_once_with(
            workcell_runtime.db_session, 3, ManagedDeviceStatusEnum.ERROR, "Backend init failed: Module not found"
        )

    def test_shutdown_device_backend(self, workcell_runtime: WorkcellRuntime, mock_ads_service_wcr: MagicMock):
        mock_backend_instance = MagicMock()
        mock_backend_instance.stop = MagicMock()
        workcell_runtime._active_device_backends[1] = mock_backend_instance

        workcell_runtime.shutdown_device_backend(1)

        assert 1 not in workcell_runtime._active_device_backends
        mock_backend_instance.stop.assert_called_once()
        mock_ads_service_wcr.update_managed_device_status.assert_called_once_with(
            workcell_runtime.db_session, 1, ManagedDeviceStatusEnum.OFFLINE, "Backend shut down."
        )

class TestWorkcellRuntimeLabwareHandling:

    @patch('praxis.backend.core.workcell_runtime._get_class_from_fqn')
    def test_create_or_get_labware_plr_object_success(
        self, mock_get_class: MagicMock, mock_plr_resource_class: MagicMock,
        workcell_runtime: WorkcellRuntime, mock_ads_service_wcr: MagicMock # Added ads mock
    ):
        mock_get_class.return_value = mock_plr_resource_class
        labware_orm = LabwareInstanceOrmMock(id=1, user_assigned_name="Plate1", pylabrobot_definition_name="some.LabwareFQN") # Name used for instance

        plr_object = workcell_runtime.create_or_get_labware_plr_object(labware_orm, "some.LabwareFQN") # Pass FQN

        mock_get_class.assert_called_once_with("some.LabwareFQN")
        mock_plr_resource_class.assert_called_once_with(name="Plate1")
        assert plr_object is not None
        assert workcell_runtime._active_plr_labware_objects[1] is plr_object

    @patch('praxis.backend.core.workcell_runtime._get_class_from_fqn')
    def test_create_or_get_labware_plr_object_failure_sets_status_error(
        self, mock_get_class: MagicMock, workcell_runtime: WorkcellRuntime, mock_ads_service_wcr: MagicMock
    ):
        mock_get_class.side_effect = ImportError("Cannot import labware class")
        labware_orm = LabwareInstanceOrmMock(id=2, user_assigned_name="BadPlate", pylabrobot_definition_name="bad.fqn.Labware")

        plr_object = workcell_runtime.create_or_get_labware_plr_object(labware_orm, "bad.fqn.Labware")

        assert plr_object is None
        assert 2 not in workcell_runtime._active_plr_labware_objects
        # Check that status was updated to ERROR
        mock_ads_service_wcr.update_labware_instance_location_and_status.assert_called_once_with(
            db=workcell_runtime.db_session,
            labware_instance_id=2,
            new_status=LabwareInstanceStatusEnum.ERROR,
            status_details="Failed to create PLR object for 'BadPlate' using FQN 'bad.fqn.Labware': Cannot import labware class"
        )


    @patch('praxis.backend.core.workcell_runtime.PlrDeck', spec=True) # Mock the PlrDeck class itself for isinstance checks
    def test_assign_labware_to_deck_slot(
        self, MockActualPlrDeck: MagicMock, # This is the mocked PlrDeck class from the patch
        workcell_runtime: WorkcellRuntime, mock_ads_service_wcr: MagicMock
    ):
        # Setup a mock deck object that is an instance of the (mocked) PlrDeck
        mock_deck_instance = MagicMock(spec=MockActualPlrDeck) # Instance that passes isinstance checks
        mock_deck_instance.name = "TestDeck"
        mock_deck_instance.assign_child_resource = MagicMock()
        
        workcell_runtime._active_device_backends[10] = mock_deck_instance # Assume deck device ID 10 is active

        mock_labware_plr_obj = MagicMock(spec=workcell_runtime.PlrResource) # from praxis.backend.core.workcell_runtime
        labware_instance_id = 1

        workcell_runtime.assign_labware_to_deck_slot(10, "A1", mock_labware_plr_obj, labware_instance_id)

        mock_deck_instance.assign_child_resource.assert_called_once_with(resource=mock_labware_plr_obj, slot="A1")
        mock_ads_service_wcr.update_labware_instance_location_and_status.assert_called_once_with(
            workcell_runtime.db_session, labware_instance_id, LabwareInstanceStatusEnum.AVAILABLE_ON_DECK,
            location_device_id=10, current_deck_slot_name="A1"
        )

# TODO: More tests:
# - get_active_device_backend, get_active_labware_plr_object
# - clear_deck_slot
# - execute_device_action (basic getattr call)
# - shutdown_all_backends
# - get_main_deck_plr_object (interaction with ads if deck not active)
# - Complex constructor inspection in initialize_device_backend
```
