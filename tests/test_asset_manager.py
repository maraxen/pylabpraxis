import pytest # type: ignore
from unittest.mock import MagicMock, patch, call
from typing import List, Optional, Any, Dict

# Classes to test
from praxis.backend.core.asset_manager import AssetManager, AssetAcquisitionError

# Dependent ORM-like Mocks (can be simple MagicMocks or classes)
# We'll use MagicMock for flexibility in these tests
ManagedDeviceOrmMock = MagicMock
LabwareInstanceOrmMock = MagicMock
LabwareDefinitionCatalogOrmMock = MagicMock
AssetRequirementModelMock = MagicMock # from praxis.backend.protocol_core.protocol_definition_models

# Enums (assuming they are importable or defined simply for test if needed)
from praxis.backend.database_models.asset_management_orm import (
    ManagedDeviceStatusEnum, LabwareInstanceStatusEnum, PraxisDeviceCategoryEnum
)


@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def mock_workcell_runtime():
    m = MagicMock()
    m.initialize_device_backend.return_value = MagicMock(name="live_mock_device")
    m.create_or_get_labware_plr_object.return_value = MagicMock(name="live_mock_labware")
    return m

@pytest.fixture
def mock_ads_service():
    with patch('praxis.backend.core.asset_manager.ads') as mock_ads: # Patch where it's used
        # Configure default return values for ads functions
        mock_ads.list_managed_devices.return_value = []
        mock_ads.get_managed_device_by_id.return_value = None
        mock_ads.update_managed_device_status.return_value = MagicMock(spec=ManagedDeviceOrmMock)
        
        mock_ads.list_labware_instances.return_value = []
        mock_ads.get_labware_instance_by_id.return_value = None
        mock_ads.get_labware_definition_by_name.return_value = None # Changed from get_labware_definition
        mock_ads.update_labware_instance_location_and_status.return_value = MagicMock(spec=LabwareInstanceOrmMock)
        yield mock_ads


@pytest.fixture
def asset_manager(mock_db_session: MagicMock, mock_workcell_runtime: MagicMock, mock_ads_service: MagicMock):
    # mock_ads_service fixture ensures that 'ads' within asset_manager module is patched
    return AssetManager(db_session=mock_db_session, workcell_runtime=mock_workcell_runtime)

class TestAssetManagerAcquireDevice:

    def test_acquire_device_success(self, asset_manager: AssetManager, mock_ads_service: MagicMock, mock_workcell_runtime: MagicMock):
        mock_device_orm = ManagedDeviceOrmMock(id=1, user_friendly_name="Device1", pylabrobot_class_name="SomeDeviceClass")
        mock_ads_service.list_managed_devices.return_value = [mock_device_orm]
        # Simulate successful update by returning the same mock_device_orm or a new one with updated fields
        updated_mock_device_orm = ManagedDeviceOrmMock(id=1, user_friendly_name="Device1", current_status=ManagedDeviceStatusEnum.IN_USE)
        mock_ads_service.update_managed_device_status.return_value = updated_mock_device_orm


        live_device, orm_id, dev_type = asset_manager.acquire_device(
            protocol_run_guid="run123",
            requested_asset_name_in_protocol="dev_in_proto",
            pylabrobot_class_name_constraint="SomeDeviceClass"
        )

        mock_ads_service.list_managed_devices.assert_called_once_with(
            asset_manager.db, # db session
            status=ManagedDeviceStatusEnum.AVAILABLE,
            pylabrobot_class_filter="SomeDeviceClass"
        )
        mock_workcell_runtime.initialize_device_backend.assert_called_once_with(mock_device_orm)
        mock_ads_service.update_managed_device_status.assert_called_once_with(
            asset_manager.db, 1, ManagedDeviceStatusEnum.IN_USE,
            current_protocol_run_guid="run123",
            status_details="In use by run run123"
        )
        assert live_device is mock_workcell_runtime.initialize_device_backend.return_value
        assert orm_id == 1
        assert dev_type == "device"

    def test_acquire_device_no_device_found(self, asset_manager: AssetManager, mock_ads_service: MagicMock):
        mock_ads_service.list_managed_devices.return_value = [] # No devices available
        with pytest.raises(AssetAcquisitionError, match="No device found matching type constraint 'SomeDeviceClass' and status AVAILABLE."):
            asset_manager.acquire_device("run123", "dev", "SomeDeviceClass")

    def test_acquire_device_backend_init_fails(self, asset_manager: AssetManager, mock_ads_service: MagicMock, mock_workcell_runtime: MagicMock):
        mock_device_orm = ManagedDeviceOrmMock(id=1, user_friendly_name="Device1")
        mock_ads_service.list_managed_devices.return_value = [mock_device_orm]
        mock_workcell_runtime.initialize_device_backend.return_value = None # Simulate failure

        with pytest.raises(AssetAcquisitionError, match="Failed to initialize backend for device 'Device1'"):
            asset_manager.acquire_device("run123", "dev", "SomeDeviceClass")
        
        # WorkcellRuntime is expected to have set status to ERROR
        # No call to update_managed_device_status(..., ManagedDeviceStatusEnum.IN_USE, ...) should occur from AssetManager

    def test_acquire_device_db_status_update_fails_after_init(self, asset_manager: AssetManager, mock_ads_service: MagicMock, mock_workcell_runtime: MagicMock):
        mock_device_orm = ManagedDeviceOrmMock(id=1, user_friendly_name="Device1")
        mock_ads_service.list_managed_devices.return_value = [mock_device_orm]
        mock_ads_service.update_managed_device_status.return_value = None # Simulate DB update failure

        with pytest.raises(AssetAcquisitionError, match="CRITICAL: Device 'Device1' backend is live, but FAILED to update its DB status to IN_USE"):
            asset_manager.acquire_device("run123", "dev", "SomeDeviceClass")


class TestAssetManagerAcquireLabware:

    @pytest.fixture
    def mock_labware_def(self):
        mock_def = LabwareDefinitionCatalogOrmMock()
        mock_def.python_fqn = "pylabrobot.resources.plate.Plate"
        return mock_def

    def test_acquire_labware_success_from_storage(
        self, asset_manager: AssetManager, mock_ads_service: MagicMock, 
        mock_workcell_runtime: MagicMock, mock_labware_def: MagicMock
    ):
        mock_lw_instance_orm = LabwareInstanceOrmMock(id=1, user_assigned_name="Plate1", pylabrobot_definition_name="some_plate_def_name")
        mock_ads_service.list_labware_instances.side_effect = [
            [], # First call for AVAILABLE_ON_DECK returns empty
            [mock_lw_instance_orm] # Second call for AVAILABLE_IN_STORAGE returns one
        ]
        mock_ads_service.get_labware_definition_by_name.return_value = mock_labware_def
        # Simulate successful update
        updated_mock_lw_instance_orm = LabwareInstanceOrmMock(id=1, user_assigned_name="Plate1", current_status=LabwareInstanceStatusEnum.IN_USE)
        mock_ads_service.update_labware_instance_location_and_status.return_value = updated_mock_lw_instance_orm


        live_labware, orm_id, lw_type = asset_manager.acquire_labware(
            protocol_run_guid="run123",
            requested_asset_name_in_protocol="lw_in_proto",
            pylabrobot_definition_name_constraint="some_plate_def_name"
        )

        mock_ads_service.get_labware_definition_by_name.assert_called_once_with(asset_manager.db, "some_plate_def_name")
        mock_workcell_runtime.create_or_get_labware_plr_object.assert_called_once_with(
            labware_instance_orm=mock_lw_instance_orm,
            labware_definition_fqn="pylabrobot.resources.plate.Plate"
        )
        # Final status update to IN_USE
        mock_ads_service.update_labware_instance_location_and_status.assert_called_with(
            asset_manager.db, mock_lw_instance_orm.id,
            new_status=LabwareInstanceStatusEnum.IN_USE,
            current_protocol_run_guid="run123",
            status_details="In use by run run123"
        )
        assert live_labware is mock_workcell_runtime.create_or_get_labware_plr_object.return_value
        assert orm_id == 1
        assert lw_type == "labware"

    def test_acquire_labware_with_deck_assignment(
        self, asset_manager: AssetManager, mock_ads_service: MagicMock,
        mock_workcell_runtime: MagicMock, mock_labware_def: MagicMock
    ):
        mock_lw_instance_orm = LabwareInstanceOrmMock(id=1, user_assigned_name="Plate1", pylabrobot_definition_name="some_plate_def_name")
        mock_deck_orm = ManagedDeviceOrmMock(id=10, user_friendly_name="MainDeck")

        mock_ads_service.list_labware_instances.return_value = [mock_lw_instance_orm] # Found directly
        mock_ads_service.get_labware_definition_by_name.return_value = mock_labware_def
        mock_ads_service.list_managed_devices.return_value = [mock_deck_orm] # For deck lookup
        mock_ads_service.update_labware_instance_location_and_status.return_value = mock_lw_instance_orm


        location_constraints = {"deck_name": "MainDeck", "slot_name": "A1"}
        live_labware, _, _ = asset_manager.acquire_labware(
            protocol_run_guid="run123",
            requested_asset_name_in_protocol="plate_on_deck",
            pylabrobot_definition_name_constraint="some_plate_def_name",
            location_constraints=location_constraints
        )
        
        mock_ads_service.list_managed_devices.assert_called_once_with(
            asset_manager.db, user_friendly_name_filter="MainDeck", praxis_category_filter=PraxisDeviceCategoryEnum.DECK
        )
        mock_workcell_runtime.assign_labware_to_deck_slot.assert_called_once_with(
            deck_device_orm_id=mock_deck_orm.id,
            slot_name="A1",
            labware_plr_object=mock_workcell_runtime.create_or_get_labware_plr_object.return_value,
            labware_instance_orm_id=mock_lw_instance_orm.id
        )
        # Check final status update to IN_USE
        mock_ads_service.update_labware_instance_location_and_status.assert_called_with(
            asset_manager.db, mock_lw_instance_orm.id,
            new_status=LabwareInstanceStatusEnum.IN_USE,
            current_protocol_run_guid="run123",
            status_details="In use by run run123"
        )


    def test_acquire_labware_fqn_not_found(self, asset_manager: AssetManager, mock_ads_service: MagicMock):
        mock_lw_instance_orm = LabwareInstanceOrmMock(id=1, pylabrobot_definition_name="unknown_def_name")
        mock_ads_service.list_labware_instances.return_value = [mock_lw_instance_orm]
        mock_ads_service.get_labware_definition_by_name.return_value = None # FQN not found

        with pytest.raises(AssetAcquisitionError, match="Python FQN not found for labware definition 'unknown_def_name'"):
            asset_manager.acquire_labware("run123", "lw", "unknown_def_name")
        
        # Verify status update to ERROR
        mock_ads_service.update_labware_instance_location_and_status.assert_called_once_with(
            db=asset_manager.db, labware_instance_id=mock_lw_instance_orm.id,
            new_status=LabwareInstanceStatusEnum.ERROR,
            status_details=ANY # Check that some details are passed
        )


    def test_acquire_labware_plr_object_creation_fails(
        self, asset_manager: AssetManager, mock_ads_service: MagicMock,
        mock_workcell_runtime: MagicMock, mock_labware_def: MagicMock
    ):
        mock_lw_instance_orm = LabwareInstanceOrmMock(id=1, user_assigned_name="Plate1", pylabrobot_definition_name="def")
        mock_ads_service.list_labware_instances.return_value = [mock_lw_instance_orm]
        mock_ads_service.get_labware_definition_by_name.return_value = mock_labware_def
        mock_workcell_runtime.create_or_get_labware_plr_object.return_value = None # Simulate failure

        with pytest.raises(AssetAcquisitionError, match="Failed to create PLR object for labware 'Plate1'"):
            asset_manager.acquire_labware("run123", "lw", "def")
        # WorkcellRuntime is expected to have set status to ERROR via its ads call.

class TestAssetManagerRelease:

    def test_release_device(self, asset_manager: AssetManager, mock_ads_service: MagicMock, mock_workcell_runtime: MagicMock):
        # Mock the return of get_managed_device_by_id for the logic inside release_device
        mock_device_after_shutdown = ManagedDeviceOrmMock(id=1, current_status=ManagedDeviceStatusEnum.OFFLINE)
        mock_ads_service.get_managed_device_by_id.return_value = mock_device_after_shutdown

        asset_manager.release_device(device_orm_id=1, final_status=ManagedDeviceStatusEnum.AVAILABLE)
        
        mock_workcell_runtime.shutdown_device_backend.assert_called_once_with(1)
        mock_ads_service.get_managed_device_by_id.assert_called_once_with(asset_manager.db, 1)
        # This assertion checks the final call to set the desired status if different from what WCR set
        mock_ads_service.update_managed_device_status.assert_called_with(
            asset_manager.db, 1, ManagedDeviceStatusEnum.AVAILABLE,
            status_details="Released from run", current_protocol_run_guid=None
        )

    def test_release_labware_no_deck_clear(
        self, asset_manager: AssetManager, mock_ads_service: MagicMock, mock_workcell_runtime: MagicMock
    ):
        asset_manager.release_labware(
            labware_instance_orm_id=1,
            final_status=LabwareInstanceStatusEnum.AVAILABLE_IN_STORAGE,
            status_details="Stored after run"
        )
        mock_workcell_runtime.clear_deck_slot.assert_not_called()
        mock_ads_service.update_labware_instance_location_and_status.assert_called_once_with(
            asset_manager.db, 1,
            new_status=LabwareInstanceStatusEnum.AVAILABLE_IN_STORAGE,
            properties_json_update=None,
            location_device_id=None, 
            current_deck_slot_name=None, 
            current_protocol_run_guid=None,
            status_details="Stored after run"
        )

    def test_release_labware_with_deck_clear(
        self, asset_manager: AssetManager, mock_ads_service: MagicMock, mock_workcell_runtime: MagicMock
    ):
        asset_manager.release_labware(
            labware_instance_orm_id=1,
            final_status=LabwareInstanceStatusEnum.AVAILABLE_IN_STORAGE,
            clear_from_deck_device_id=10, # Deck ID
            clear_from_slot_name="A1",
            status_details="Cleared from deck and stored"
        )
        mock_workcell_runtime.clear_deck_slot.assert_called_once_with(
            deck_device_orm_id=10, slot_name="A1", labware_instance_orm_id=1
        )
        # This call sets the final status after WCR might have set it to AVAILABLE_IN_STORAGE
        mock_ads_service.update_labware_instance_location_and_status.assert_called_once_with(
            asset_manager.db, 1,
            new_status=LabwareInstanceStatusEnum.AVAILABLE_IN_STORAGE,
            properties_json_update=None,
            location_device_id=None,
            current_deck_slot_name=None,
            current_protocol_run_guid=None,
            status_details="Cleared from deck and stored"
        )

# TODO: Tests for acquire_asset dispatcher method (verify it calls correct acquire_device/labware)
# TODO: Basic test for sync_pylabrobot_definitions (highly complex to fully unit test, needs extensive mocking of import machinery)

```
