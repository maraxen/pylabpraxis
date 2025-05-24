import pytest # type: ignore
from unittest.mock import MagicMock, patch, call, ANY # Added ANY
from typing import List, Optional, Any, Dict, Type # Added Type
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED
import inspect # ADDED
import pkgutil # ADDED
import importlib # ADDED

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
    ManagedDeviceStatusEnum, LabwareInstanceStatusEnum, PraxisDeviceCategoryEnum, LabwareCategoryEnum
)

# --- Mock PyLabRobot Base Classes for sync_pylabrobot_definitions tests ---
class MockPlrResource:
    resource_type: Optional[str] = None # Class level
    
    def __init__(self, name: str, **kwargs: Any):
        self.name = name
        self.model: Optional[str] = kwargs.get("model")
        self.category: Optional[str] = kwargs.get("category") # For serialize
        self.size_x: Optional[float] = kwargs.get("size_x")
        self.size_y: Optional[float] = kwargs.get("size_y")
        self.size_z: Optional[float] = kwargs.get("size_z")
        self.capacity: Optional[float] = kwargs.get("capacity")
        self._dimensions: Optional[Any] = kwargs.get("dimensions") 
        self._wells: List[Any] = [] 
        self.__class__.__module__ = "pylabrobot.resources.mocked" 


    def serialize(self) -> Dict[str, Any]:
        return {"name": self.name, "model": self.model, "category": self.category or "mock_resource_category"}

    def get_size_x(self) -> Optional[float]: return self.size_x
    def get_size_y(self) -> Optional[float]: return self.size_y
    def get_size_z(self) -> Optional[float]: return self.size_z
    
    @property
    def dimensions(self) -> Optional[Any]:
        return self._dimensions

    def get_well(self, index: int) -> Any:
        if not self._wells or index >= len(self._wells):
            mock_well = MagicMock()
            mock_well.max_volume = self.capacity / len(self.wells) if self.wells and self.capacity else 0 
            return mock_well
        return self._wells[index]
    
    @property
    def wells(self) -> List[Any]:
        return self._wells

class MockPlrContainer(MockPlrResource):
    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.__class__.__module__ = "pylabrobot.resources.container"

class MockPlrPlate(MockPlrContainer): 
    resource_type = "plate_type_class_level" 
    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.__class__.__module__ = "pylabrobot.resources.plate" 

class MockPlrTipRack(MockPlrResource):
    resource_type = "tip_rack_type_class_level"
    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.__class__.__module__ = "pylabrobot.resources.tip_rack"

class MockPlrWell(MockPlrResource): 
    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.__class__.__module__ = "pylabrobot.resources.well"

class MockPlrDeck(MockPlrResource): 
     def __init__(self, name: str, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.__class__.__module__ = "pylabrobot.resources.deck"

class MockPlrLid(MockPlrResource):
    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.__class__.__module__ = "pylabrobot.resources.lid"

class MockPlrReservoir(MockPlrContainer):
    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.__class__.__module__ = "pylabrobot.resources.reservoir"

class MockPlrTubeRack(MockPlrResource):
    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.__class__.__module__ = "pylabrobot.resources.tube_rack"

class MockPlrTube(MockPlrContainer):
    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.__class__.__module__ = "pylabrobot.resources.tube"
        
class MockPlrPetriDish(MockPlrContainer):
    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.__class__.__module__ = "pylabrobot.resources.petri_dish"

class MockTrash(MockPlrResource):
    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.__class__.__module__ = "pylabrobot.resources.trash"

class MockCarrier(MockPlrResource):
    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.__class__.__module__ = "pylabrobot.resources.carrier"

class MockPlateCarrier(MockCarrier):
    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.__class__.__module__ = "pylabrobot.resources.plate_carrier"

class MockTipCarrier(MockCarrier):
    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.__class__.__module__ = "pylabrobot.resources.tip_carrier"
        
class MockPlateAdapter(MockCarrier):
    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.__class__.__module__ = "pylabrobot.resources.plate_adapter"

class MockItemizedResource(MockPlrResource):
     def __init__(self, name: str, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.__class__.__module__ = "pylabrobot.resources.itemized_resource"

class MockPlrTip(MockPlrResource):
     def __init__(self, name: str, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.__class__.__module__ = "pylabrobot.resources.tip"

class MockCoordinate(MagicMock): # Not a resource, just needs to be mockable
    pass
# --- End Mock PyLabRobot Base Classes ---


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

# --- Mock PyLabRobot Base Classes for sync_pylabrobot_definitions tests ---
class MockPlrResource:
    resource_type: Optional[str] = None # Class level
    
    def __init__(self, name: str, **kwargs: Any):
        self.name = name
        self.model: Optional[str] = kwargs.get("model")
        # Simulate other common attributes that might be checked by helper methods
        self.size_x: Optional[float] = kwargs.get("size_x")
        self.size_y: Optional[float] = kwargs.get("size_y")
        self.size_z: Optional[float] = kwargs.get("size_z")
        self.capacity: Optional[float] = kwargs.get("capacity")
        self._dimensions: Optional[Any] = kwargs.get("dimensions") # For Coordinate like objects
        self._wells: List[Any] = [] # For things that have wells

    def serialize(self) -> Dict[str, Any]:
        return {"name": self.name, "model": self.model, "category": "mock_resource"}

    def get_size_x(self) -> Optional[float]: return self.size_x
    def get_size_y(self) -> Optional[float]: return self.size_y
    def get_size_z(self) -> Optional[float]: return self.size_z
    
    # For things like Plate that have dimensions attribute
    @property
    def dimensions(self) -> Optional[Any]:
        return self._dimensions

    # For things that have wells and capacity might be inferred from a well
    def get_well(self, index: int) -> Any:
        return self._wells[index]
    
    @property
    def wells(self) -> List[Any]:
        return self._wells


class MockPlrContainer(MockPlrResource):
    pass

class MockPlrPlate(MockPlrContainer): # Inherits from MockPlrContainer -> MockPlrResource
    resource_type = "plate_type_class_level" # Example class-level resource_type
    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.custom_plate_attr = "plate_specific"

class MockPlrTipRack(MockPlrResource):
    resource_type = "tip_rack_type_class_level"
    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.custom_tip_rack_attr = "tip_rack_specific"

class MockPlrWell(MockPlrResource): # Example of an excluded base class
    pass

class MockPlrDeck(MockPlrResource): # Example of an excluded base class
    pass

# --- End Mock PyLabRobot Base Classes ---


class TestAssetManagerSyncPylabrobotDefinitions:
    @pytest.fixture(autouse=True)
    def patch_dependencies(self, mock_ads_service: MagicMock):
        self.mock_ads_service = mock_ads_service
        
        # Patch external dependencies for sync_pylabrobot_definitions
        with patch('praxis.backend.core.asset_manager.pkgutil.walk_packages') as self.mock_walk_packages, \
             patch('praxis.backend.core.asset_manager.importlib.import_module') as self.mock_import_module, \
             patch('praxis.backend.core.asset_manager.inspect.getmembers') as self.mock_getmembers, \
             patch('praxis.backend.core.asset_manager.inspect.isabstract') as self.mock_isabstract, \
             patch('praxis.backend.core.asset_manager.get_resource_constructor_params') as self.mock_get_constructor_params, \
             patch('praxis.backend.core.asset_manager.PlrResource', MockPlrResource), \
             patch('praxis.backend.core.asset_manager.Container', MockPlrContainer), \
             patch('praxis.backend.core.asset_manager.PlrPlate', MockPlrPlate), \
             patch('praxis.backend.core.asset_manager.PlrTipRack', MockPlrTipRack), \
             patch('praxis.backend.core.asset_manager.Well', MockPlrWell), \
             patch('praxis.backend.core.asset_manager.PlrDeck', MockPlrDeck):
            yield

    def test_sync_simple_instantiable_resource(self, asset_manager: AssetManager):
        # 1. Setup Mocks
        class MockSimplePlate(MockPlrPlate):
            resource_type = "simple_plate_type" # Class level
            
            def __init__(self, name: str, model: Optional[str] = None, size_x: Optional[float] = None, capacity: Optional[float] = None):
                super().__init__(name, model=model, size_x=size_x, capacity=capacity)
                if model is None: self.model = "TestModel123" # Default instance model
                if size_x is None: self.size_x = 120.0 # Default instance size_x
                if capacity is None: self.capacity = 100.0 # Default instance capacity (assume uL for test)

            def serialize(self) -> Dict[str, Any]:
                return {"custom_field": "value", "name": self.name, "model": self.model, "category": "plate"}

        mock_module = MagicMock()
        mock_module.MockSimplePlate = MockSimplePlate
        
        self.mock_walk_packages.return_value = [(None, 'mock_pylabrobot_module.plates', False)]
        self.mock_import_module.return_value = mock_module
        self.mock_getmembers.return_value = [('MockSimplePlate', MockSimplePlate)]
        self.mock_isabstract.return_value = False
        self.mock_get_constructor_params.return_value = {
            'name': {'type': 'str', 'required': True, 'default': None},
            'model': {'type': 'Optional[str]', 'required': False, 'default': None},
            'size_x': {'type': 'Optional[float]', 'required': False, 'default': None},
            'capacity': {'type': 'Optional[float]', 'required': False, 'default': None},
        }
        self.mock_ads_service.get_labware_definition.return_value = None # New definition

        # 2. Call sync_pylabrobot_definitions
        added, updated = asset_manager.sync_pylabrobot_definitions()

        # 3. Assertions
        assert added == 1
        assert updated == 0
        self.mock_ads_service.add_or_update_labware_definition.assert_called_once()
        call_args = self.mock_ads_service.add_or_update_labware_definition.call_args[1]
        
        assert call_args['python_fqn'] == 'mock_pylabrobot_module.plates.MockSimplePlate'
        assert call_args['pylabrobot_definition_name'] == "simple_plate_type" # From class level
        assert call_args['praxis_labware_type_name'] == "TestModel123" # From instance model
        assert call_args['category'].name == 'PLATE' # Inferred from MockPlrPlate inheritance
        assert call_args['model'] == "TestModel123"
        assert call_args['size_x_mm'] == 120.0
        assert call_args['nominal_volume_ul'] == 100.0 # Directly from capacity
        assert call_args['plr_definition_details_json'] == {"custom_field": "value", "model": "TestModel123", "category": "plate"}
        assert call_args['is_consumable'] is True
        assert "MockSimplePlate" in call_args['description'] # Basic check for docstring or name

    # More tests will be added here

```
