import pytest # type: ignore
from unittest.mock import MagicMock, patch, call, ANY 
from typing import List, Optional, Any, Dict, Type 
import inspect 
import pkgutil 
import importlib 

# Classes to test
from praxis.backend.core.asset_manager import AssetManager, AssetAcquisitionError

# Dependent ORM-like Mocks
ManagedDeviceOrmMock = MagicMock
LabwareInstanceOrmMock = MagicMock
LabwareDefinitionCatalogOrmMock = MagicMock
AssetRequirementModelMock = MagicMock 

# Enums
from praxis.backend.database_models.asset_management_orm import (
    ManagedDeviceStatusEnum, LabwareInstanceStatusEnum, PraxisDeviceCategoryEnum, LabwareCategoryEnum
)

# --- Mock PyLabRobot Base Classes for sync_pylabrobot_definitions tests ---
class MockPlrResource:
    resource_type: Optional[str] = None 
    
    def __init__(self, name: str, **kwargs: Any):
        self.name = name
        self.model: Optional[str] = kwargs.get("model")
        self.category_str: Optional[str] = kwargs.get("category_str") 
        self.size_x: Optional[float] = kwargs.get("size_x")
        self.size_y: Optional[float] = kwargs.get("size_y")
        self.size_z: Optional[float] = kwargs.get("size_z")
        self.capacity: Optional[float] = kwargs.get("capacity")
        self._dimensions: Optional[Any] = kwargs.get("dimensions_obj") 
        self._wells_data: List[Any] = kwargs.get("wells_data", []) 
        self.__class__.__module__ = "pylabrobot.resources.mocked" 


    def serialize(self) -> Dict[str, Any]:
        return {"name": self.name, "model": self.model, "category": self.category_str or "mock_resource_category"}

    def get_size_x(self) -> Optional[float]: return self.size_x
    def get_size_y(self) -> Optional[float]: return self.size_y
    def get_size_z(self) -> Optional[float]: return self.size_z
    
    @property
    def dimensions(self) -> Optional[Any]: 
        return self._dimensions

    def get_well(self, index: int) -> Any:
        if not self._wells_data or index >= len(self._wells_data):
            mock_well = MagicMock(spec=MockPlrWell) 
            mock_well.max_volume = (self.capacity / len(self._wells_data)) if self._wells_data and self.capacity else 0 
            return mock_well
        return self._wells_data[index]
    
    @property
    def wells(self) -> List[Any]: 
        return self._wells_data

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

class MockCoordinate(MagicMock): 
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
    with patch('praxis.backend.core.asset_manager.ads') as mock_ads:
        mock_ads.list_managed_devices.return_value = []
        mock_ads.get_managed_device_by_id.return_value = None
        mock_ads.update_managed_device_status.return_value = MagicMock(spec=ManagedDeviceOrmMock)
        
        mock_ads.list_labware_instances.return_value = []
        mock_ads.get_labware_instance_by_id.return_value = None
        mock_ads.get_labware_definition.return_value = None 
        mock_ads.add_or_update_labware_definition.return_value = MagicMock(spec=LabwareDefinitionCatalogOrmMock)
        mock_ads.update_labware_instance_location_and_status.return_value = MagicMock(spec=LabwareInstanceOrmMock)
        yield mock_ads


@pytest.fixture
def asset_manager(mock_db_session: MagicMock, mock_workcell_runtime: MagicMock, mock_ads_service: MagicMock):
    return AssetManager(db_session=mock_db_session, workcell_runtime=mock_workcell_runtime)

class TestAssetManagerAcquireDevice: 

    def test_acquire_device_success(self, asset_manager: AssetManager, mock_ads_service: MagicMock, mock_workcell_runtime: MagicMock):
        mock_device_orm = ManagedDeviceOrmMock(id=1, user_friendly_name="Device1", pylabrobot_class_name="SomeDeviceClass")
        mock_ads_service.list_managed_devices.return_value = [mock_device_orm]
        updated_mock_device_orm = ManagedDeviceOrmMock(id=1, user_friendly_name="Device1", current_status=ManagedDeviceStatusEnum.IN_USE)
        mock_ads_service.update_managed_device_status.return_value = updated_mock_device_orm

        live_device, orm_id, dev_type = asset_manager.acquire_device(
            protocol_run_guid="run123",
            requested_asset_name_in_protocol="dev_in_proto",
            pylabrobot_class_name_constraint="SomeDeviceClass"
        )

        mock_ads_service.list_managed_devices.assert_called_once_with(
            asset_manager.db, 
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
        mock_ads_service.list_managed_devices.return_value = [] 
        with pytest.raises(AssetAcquisitionError, match="No device found matching type constraint 'SomeDeviceClass' and status AVAILABLE."):
            asset_manager.acquire_device("run123", "dev", "SomeDeviceClass")

    def test_acquire_device_backend_init_fails(self, asset_manager: AssetManager, mock_ads_service: MagicMock, mock_workcell_runtime: MagicMock):
        mock_device_orm = ManagedDeviceOrmMock(id=1, user_friendly_name="Device1")
        mock_ads_service.list_managed_devices.return_value = [mock_device_orm]
        mock_workcell_runtime.initialize_device_backend.return_value = None 

        with pytest.raises(AssetAcquisitionError, match="Failed to initialize backend for device 'Device1'"):
            asset_manager.acquire_device("run123", "dev", "SomeDeviceClass")
        
    def test_acquire_device_db_status_update_fails_after_init(self, asset_manager: AssetManager, mock_ads_service: MagicMock, mock_workcell_runtime: MagicMock):
        mock_device_orm = ManagedDeviceOrmMock(id=1, user_friendly_name="Device1")
        mock_ads_service.list_managed_devices.return_value = [mock_device_orm]
        mock_ads_service.update_managed_device_status.return_value = None 

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
            [], 
            [mock_lw_instance_orm] 
        ]
        mock_ads_service.get_labware_definition.return_value = mock_labware_def 
        updated_mock_lw_instance_orm = LabwareInstanceOrmMock(id=1, user_assigned_name="Plate1", current_status=LabwareInstanceStatusEnum.IN_USE)
        mock_ads_service.update_labware_instance_location_and_status.return_value = updated_mock_lw_instance_orm

        live_labware, orm_id, lw_type = asset_manager.acquire_labware(
            protocol_run_guid="run123",
            requested_asset_name_in_protocol="lw_in_proto",
            pylabrobot_definition_name_constraint="some_plate_def_name"
        )

        mock_ads_service.get_labware_definition.assert_called_once_with(asset_manager.db, "some_plate_def_name")
        mock_workcell_runtime.create_or_get_labware_plr_object.assert_called_once_with(
            labware_instance_orm=mock_lw_instance_orm,
            labware_definition_fqn="pylabrobot.resources.plate.Plate"
        )
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

        mock_ads_service.list_labware_instances.return_value = [mock_lw_instance_orm] 
        mock_ads_service.get_labware_definition.return_value = mock_labware_def 
        mock_ads_service.list_managed_devices.return_value = [mock_deck_orm] 
        mock_ads_service.update_labware_instance_location_and_status.return_value = mock_lw_instance_orm

        location_constraints = {"deck_name": "MainDeck", "slot_name": "A1"}
        asset_manager.acquire_labware(
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
        mock_ads_service.update_labware_instance_location_and_status.assert_called_with(
            asset_manager.db, mock_lw_instance_orm.id,
            new_status=LabwareInstanceStatusEnum.IN_USE,
            current_protocol_run_guid="run123",
            status_details="In use by run run123"
        )

    def test_acquire_labware_fqn_not_found(self, asset_manager: AssetManager, mock_ads_service: MagicMock):
        mock_lw_instance_orm = LabwareInstanceOrmMock(id=1, pylabrobot_definition_name="unknown_def_name")
        mock_ads_service.list_labware_instances.return_value = [mock_lw_instance_orm]
        mock_ads_service.get_labware_definition.return_value = None 

        with pytest.raises(AssetAcquisitionError, match="Python FQN not found for labware definition 'unknown_def_name'"):
            asset_manager.acquire_labware("run123", "lw", "unknown_def_name")
        
        mock_ads_service.update_labware_instance_location_and_status.assert_called_once_with(
            db=asset_manager.db, labware_instance_id=mock_lw_instance_orm.id,
            new_status=LabwareInstanceStatusEnum.ERROR,
            status_details=ANY 
        )

    def test_acquire_labware_plr_object_creation_fails(
        self, asset_manager: AssetManager, mock_ads_service: MagicMock,
        mock_workcell_runtime: MagicMock, mock_labware_def: MagicMock
    ):
        mock_lw_instance_orm = LabwareInstanceOrmMock(id=1, user_assigned_name="Plate1", pylabrobot_definition_name="def")
        mock_ads_service.list_labware_instances.return_value = [mock_lw_instance_orm]
        mock_ads_service.get_labware_definition.return_value = mock_labware_def 
        mock_workcell_runtime.create_or_get_labware_plr_object.return_value = None 

        with pytest.raises(AssetAcquisitionError, match="Failed to create PLR object for labware 'Plate1'"):
            asset_manager.acquire_labware("run123", "lw", "def")

class TestAssetManagerRelease: 

    def test_release_device(self, asset_manager: AssetManager, mock_ads_service: MagicMock, mock_workcell_runtime: MagicMock):
        mock_device_after_shutdown = ManagedDeviceOrmMock(id=1, current_status=ManagedDeviceStatusEnum.OFFLINE)
        mock_ads_service.get_managed_device_by_id.return_value = mock_device_after_shutdown

        asset_manager.release_device(device_orm_id=1, final_status=ManagedDeviceStatusEnum.AVAILABLE)
        
        mock_workcell_runtime.shutdown_device_backend.assert_called_once_with(1)
        mock_ads_service.get_managed_device_by_id.assert_called_once_with(asset_manager.db, 1)
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
            clear_from_deck_device_id=10, 
            clear_from_slot_name="A1",
            status_details="Cleared from deck and stored"
        )
        mock_workcell_runtime.clear_deck_slot.assert_called_once_with(
            deck_device_orm_id=10, slot_name="A1", labware_instance_orm_id=1
        )
        mock_ads_service.update_labware_instance_location_and_status.assert_called_once_with(
            asset_manager.db, 1,
            new_status=LabwareInstanceStatusEnum.AVAILABLE_IN_STORAGE,
            properties_json_update=None,
            location_device_id=None,
            current_deck_slot_name=None,
            current_protocol_run_guid=None,
            status_details="Cleared from deck and stored"
        )

class TestAssetManagerSyncPylabrobotDefinitions:
    @pytest.fixture(autouse=True)
    def patch_dependencies(self, mock_ads_service: MagicMock, monkeypatch: pytest.MonkeyPatch): 
        self.mock_ads_service = mock_ads_service
        
        self.mock_walk_packages = MagicMock()
        self.mock_import_module = MagicMock()
        self.mock_getmembers = MagicMock()
        self.mock_isabstract_inspect = MagicMock() 
        self.mock_isclass_inspect = MagicMock()   
        self.mock_issubclass_inspect = MagicMock()
        self.mock_get_constructor_params = MagicMock()

        monkeypatch.setattr("praxis.backend.core.asset_manager.pkgutil.walk_packages", self.mock_walk_packages)
        monkeypatch.setattr("praxis.backend.core.asset_manager.importlib.import_module", self.mock_import_module)
        monkeypatch.setattr("praxis.backend.core.asset_manager.inspect.getmembers", self.mock_getmembers)
        monkeypatch.setattr("praxis.backend.core.asset_manager.inspect.isabstract", self.mock_isabstract_inspect)
        monkeypatch.setattr("praxis.backend.core.asset_manager.inspect.isclass", self.mock_isclass_inspect)
        monkeypatch.setattr("praxis.backend.core.asset_manager.issubclass", self.mock_issubclass_inspect) 
        monkeypatch.setattr("praxis.backend.core.asset_manager.get_resource_constructor_params", self.mock_get_constructor_params)

        monkeypatch.setattr("praxis.backend.core.asset_manager.PlrResource", MockPlrResource)
        monkeypatch.setattr("praxis.backend.core.asset_manager.Container", MockPlrContainer)
        monkeypatch.setattr("praxis.backend.core.asset_manager.PlrPlate", MockPlrPlate)
        monkeypatch.setattr("praxis.backend.core.asset_manager.PlrTipRack", MockPlrTipRack)
        monkeypatch.setattr("praxis.backend.core.asset_manager.Well", MockPlrWell) 
        monkeypatch.setattr("praxis.backend.core.asset_manager.PlrDeck", MockPlrDeck) 
        monkeypatch.setattr("praxis.backend.core.asset_manager.Lid", MockPlrLid)
        monkeypatch.setattr("praxis.backend.core.asset_manager.PlrReservoir", MockPlrReservoir)
        monkeypatch.setattr("praxis.backend.core.asset_manager.PlrTubeRack", MockPlrTubeRack)
        monkeypatch.setattr("praxis.backend.core.asset_manager.PlrTube", MockPlrTube)
        monkeypatch.setattr("praxis.backend.core.asset_manager.PlrPetriDish", MockPlrPetriDish)
        monkeypatch.setattr("praxis.backend.core.asset_manager.Trash", MockTrash)
        monkeypatch.setattr("praxis.backend.core.asset_manager.PlateCarrier", MockPlateCarrier)
        monkeypatch.setattr("praxis.backend.core.asset_manager.TipCarrier", MockTipCarrier)
        monkeypatch.setattr("praxis.backend.core.asset_manager.PlateAdapter", MockPlateAdapter)
        monkeypatch.setattr("praxis.backend.core.asset_manager.Carrier", MockCarrier)
        monkeypatch.setattr("praxis.backend.core.asset_manager.ItemizedResource", MockItemizedResource)
        monkeypatch.setattr("praxis.backend.core.asset_manager.PlrTip", MockPlrTip)
        monkeypatch.setattr("praxis.backend.core.asset_manager.Coordinate", MockCoordinate)

        self.mock_isclass_inspect.side_effect = lambda obj: isinstance(obj, type)
        
        def _mock_issubclass(obj, base):
            if not isinstance(obj, type): return False
            if not inspect.isclass(base): return False 
            return issubclass(obj, base)
        self.mock_issubclass_inspect.side_effect = _mock_issubclass

    def test_sync_simple_instantiable_resource(self, asset_manager: AssetManager, caplog):
        class MockSimplePlateDef(MockPlrPlate):
            resource_type = "simple_plate_type_inst"
            def __init__(self, name: str, model: Optional[str] = "TestModel123", size_x: Optional[float] = 120.0, capacity: Optional[float] = 100.0):
                super().__init__(name, model=model, size_x=size_x, capacity=capacity)
                self.model = model 
                self.size_x = size_x
                self.capacity = capacity
                self.__class__.__module__ = "mock_pylabrobot_module.plates"

            def serialize(self) -> Dict[str, Any]:
                return {"custom_field": "value", "name": self.name, "model": self.model, "category_str": "plate"}

        mock_module = MagicMock()
        mock_module.MockSimplePlateToSync = MockSimplePlateDef 
        
        self.mock_walk_packages.return_value = [(None, 'mock_pylabrobot_module.plates', False)]
        self.mock_import_module.return_value = mock_module
        self.mock_getmembers.return_value = [('MockSimplePlateToSync', MockSimplePlateDef)]
        self.mock_isabstract_inspect.return_value = False
        self.mock_get_constructor_params.return_value = {
            'name': {'type': 'str', 'required': True, 'default': inspect.Parameter.empty},
            'model': {'type': 'Optional[str]', 'required': False, 'default': "TestModel123"},
            'size_x': {'type': 'Optional[float]', 'required': False, 'default': 120.0},
            'capacity': {'type': 'Optional[float]', 'required': False, 'default': 100.0},
        }
        self.mock_ads_service.get_labware_definition.return_value = None 

        added, updated = asset_manager.sync_pylabrobot_definitions(plr_resources_package=MagicMock(__path__=['dummy'], __name__='mock_plr_pkg'))
        
        assert added == 1
        assert updated == 0
        self.mock_ads_service.add_or_update_labware_definition.assert_called_once()
        call_args = self.mock_ads_service.add_or_update_labware_definition.call_args[1]
        
        assert call_args['python_fqn'] == 'mock_pylabrobot_module.plates.MockSimplePlateToSync'
        assert call_args['pylabrobot_definition_name'] == "simple_plate_type_inst" 
        assert call_args['praxis_labware_type_name'] == "TestModel123" 
        assert call_args['category'] == LabwareCategoryEnum.PLATE 
        assert call_args['model'] == "TestModel123"
        assert call_args['size_x_mm'] == 120.0
        assert call_args['nominal_volume_ul'] == 100.0 
        assert call_args['plr_definition_details_json'] == {"custom_field": "value", "name": ANY, "model": "TestModel123", "category_str": "plate"} 
        assert call_args['is_consumable'] is True
        assert "MockSimplePlateToSync" in call_args['description'] 

    def test_sync_complex_constructor_fallback_to_class_data(self, asset_manager: AssetManager, caplog):
        class MockComplexResource(MockPlrResource):
            """Description for complex resource"""
            resource_type = "complex_static_type"
            model = "ClassLevelModel" 
            
            def __init__(self, name: str, backend: Any, another_required: int): 
                super().__init__(name)
                self.backend = backend
                self.another_required = another_required
                self.__class__.__module__ = "mock_module.complex"

        mock_module = MagicMock()
        mock_module.MockComplexResource = MockComplexResource

        self.mock_walk_packages.return_value = [(None, 'mock_module.complex', False)]
        self.mock_import_module.return_value = mock_module
        self.mock_getmembers.return_value = [('MockComplexResource', MockComplexResource)]
        self.mock_isabstract_inspect.return_value = False
        self.mock_get_constructor_params.return_value = {
            'name': {'type': 'str', 'required': True, 'default': inspect.Parameter.empty},
            'backend': {'type': 'SomeBackendClass', 'required': True, 'default': inspect.Parameter.empty},
            'another_required': {'type': 'int', 'required': True, 'default': inspect.Parameter.empty}
        }
        self.mock_ads_service.get_labware_definition.return_value = None

        added, updated = asset_manager.sync_pylabrobot_definitions(plr_resources_package=MagicMock(__path__=['dummy'], __name__='mock_plr_pkg'))

        assert added == 1
        assert updated == 0
        self.mock_ads_service.add_or_update_labware_definition.assert_called_once()
        call_args = self.mock_ads_service.add_or_update_labware_definition.call_args[1]

        assert call_args['python_fqn'] == 'mock_module.complex.MockComplexResource'
        assert call_args['pylabrobot_definition_name'] == "complex_static_type"
        assert call_args['description'] == "Description for complex resource"
        assert call_args['category'] == LabwareCategoryEnum.OTHER 
        assert call_args['model'] is None 
        assert call_args['size_x_mm'] is None
        assert call_args['nominal_volume_ul'] is None
        assert call_args['plr_definition_details_json'] is None 
        assert "Skipping instantiation for mock_module.complex.MockComplexResource due to complex required parameter 'backend'" in caplog.text

    def test_sync_instantiation_failure_fallback_to_class_data(self, asset_manager: AssetManager, caplog):
        class MockFailingResource(MockPlrResource):
            """Description for failing resource"""
            resource_type = "failing_static_type"
            model = "FailingClassModel" 
            
            def __init__(self, name: str):
                super().__init__(name)
                self.__class__.__module__ = "mock_module.failing"
                raise TypeError("Test instantiation failure")

        mock_module = MagicMock()
        mock_module.MockFailingResource = MockFailingResource

        self.mock_walk_packages.return_value = [(None, 'mock_module.failing', False)]
        self.mock_import_module.return_value = mock_module
        self.mock_getmembers.return_value = [('MockFailingResource', MockFailingResource)]
        self.mock_isabstract_inspect.return_value = False
        self.mock_get_constructor_params.return_value = {
            'name': {'type': 'str', 'required': True, 'default': inspect.Parameter.empty}
        } 
        self.mock_ads_service.get_labware_definition.return_value = None

        added, updated = asset_manager.sync_pylabrobot_definitions(plr_resources_package=MagicMock(__path__=['dummy'], __name__='mock_plr_pkg'))

        assert added == 1
        assert updated == 0
        self.mock_ads_service.add_or_update_labware_definition.assert_called_once()
        call_args = self.mock_ads_service.add_or_update_labware_definition.call_args[1]

        assert call_args['python_fqn'] == 'mock_module.failing.MockFailingResource'
        assert call_args['pylabrobot_definition_name'] == "failing_static_type"
        assert call_args['description'] == "Description for failing resource"
        assert call_args['category'] == LabwareCategoryEnum.OTHER
        assert call_args['model'] is None 
        assert call_args['size_x_mm'] is None
        assert call_args['nominal_volume_ul'] is None
        assert call_args['plr_definition_details_json'] is None
        assert "WARNING: Instantiation of mock_module.failing.MockFailingResource failed even with smart defaults: Test instantiation failure" in caplog.text

    def test_sync_filters_excluded_classes(self, asset_manager: AssetManager, monkeypatch):
        class MockExcludedByName(MockPlrResource):
            resource_type = "excluded_by_name_type"
            __module__ = "mock_module.excluded"
        
        class MockExcludedByBase(MockPlrDeck): 
            resource_type = "excluded_by_base_type"
            __module__ = "mock_module.excluded"

        class MockAbstractResource(MockPlrPlate): 
            resource_type = "abstract_type"
            __module__ = "mock_module.excluded"
        
        class NonPlrResource: 
            __module__ = "mock_module.excluded"
            
        class KeptResource(MockPlrPlate): 
            resource_type = "kept_resource_type"
            model = "KeptModel"
            __module__ = "mock_module.kept"
            def __init__(self, name, model="KeptModel"): 
                super().__init__(name, model=model)

        original_excluded_names = asset_manager.EXCLUDED_CLASS_NAMES.copy()
        monkeypatch.setattr(asset_manager, 'EXCLUDED_CLASS_NAMES', original_excluded_names | {'MockExcludedByName'})

        mock_module_excluded = MagicMock()
        mock_module_excluded.MockExcludedByName = MockExcludedByName
        mock_module_excluded.MockExcludedByBase = MockExcludedByBase
        mock_module_excluded.MockAbstractResource = MockAbstractResource
        mock_module_excluded.NonPlrResource = NonPlrResource
        
        mock_module_kept = MagicMock()
        mock_module_kept.KeptResource = KeptResource

        self.mock_walk_packages.return_value = [
            (None, 'mock_module.excluded', False),
            (None, 'mock_module.kept', False)
        ]
        
        def import_module_side_effect(name):
            if name == 'mock_module.excluded': return mock_module_excluded
            if name == 'mock_module.kept': return mock_module_kept
            raise ImportError
        self.mock_import_module.side_effect = import_module_side_effect
        
        def getmembers_side_effect(module_obj, pred):
            # Make sure the predicate is also called with the mock objects
            # This is essential for issubclass and isclass to work correctly with our mocks
            if module_obj == mock_module_excluded:
                return [
                    ('MockExcludedByName', MockExcludedByName),
                    ('MockExcludedByBase', MockExcludedByBase),
                    ('MockAbstractResource', MockAbstractResource),
                    ('NonPlrResource', NonPlrResource)
                ]
            if module_obj == mock_module_kept:
                 return [('KeptResource', KeptResource)]
            return []

        self.mock_getmembers.side_effect = getmembers_side_effect
        self.mock_isabstract_inspect.side_effect = lambda cls: cls == MockAbstractResource
        
        self.mock_get_constructor_params.side_effect = lambda cls: \
            {'name': {'type': 'str', 'required': True, 'default': inspect.Parameter.empty}} if cls == KeptResource else {}

        self.mock_ads_service.get_labware_definition.return_value = None

        added, updated = asset_manager.sync_pylabrobot_definitions(plr_resources_package=MagicMock(__path__=['dummy'], __name__='mock_plr_pkg'))
        
        asset_manager.EXCLUDED_CLASS_NAMES = original_excluded_names

        assert added == 1  
        assert updated == 0
        self.mock_ads_service.add_or_update_labware_definition.assert_called_once()
        call_args = self.mock_ads_service.add_or_update_labware_definition.call_args[1]
        assert call_args['python_fqn'] == 'mock_module.kept.KeptResource'
        assert call_args['pylabrobot_definition_name'] == "kept_resource_type"

    def test_sync_property_extraction_from_details_json(self, asset_manager: AssetManager, caplog):
        class MockResourceWithJsonProps(MockPlrPlate): 
            resource_type = "json_props_type"
            model = "InstanceModelShouldBeOverridden" 
            size_x = 1.0 
            capacity = 10.0 

            def __init__(self, name: str, model: Optional[str] = None, size_x: Optional[float]=None, capacity: Optional[float]=None, category_str: Optional[str] = None): # Added category_str
                super().__init__(name=name, model=model or self.model, size_x=size_x or self.size_x, capacity=capacity or self.capacity, category_str=category_str)
                self.__class__.__module__ = "mock_module.json_props"

            def serialize(self) -> Dict[str, Any]:
                return {
                    "name": self.name, 
                    "model": "JSONModel", 
                    "category": "plate", # Explicitly set category here
                    "size_x": 90.0, 
                    "size_y": 70.0,
                    "size_z": 15.0,
                    "capacity": 250.0, 
                }

        mock_module = MagicMock()
        mock_module.MockResourceWithJsonProps = MockResourceWithJsonProps
        
        self.mock_walk_packages.return_value = [(None, 'mock_module.json_props', False)]
        self.mock_import_module.return_value = mock_module
        self.mock_getmembers.return_value = [('MockResourceWithJsonProps', MockResourceWithJsonProps)]
        self.mock_isabstract_inspect.return_value = False 
        self.mock_get_constructor_params.return_value = {
            'name': {'type': 'str', 'required': True, 'default': inspect.Parameter.empty},
            # Ensure constructor allows these to be None or take defaults so instance values don't override JSON
            'model': {'type': 'Optional[str]', 'required': False, 'default': None},
            'size_x': {'type': 'Optional[float]', 'required': False, 'default': None},
            'capacity': {'type': 'Optional[float]', 'required': False, 'default': None}
        }
        self.mock_ads_service.get_labware_definition.return_value = None

        added, updated = asset_manager.sync_pylabrobot_definitions(plr_resources_package=MagicMock(__path__=['dummy'], __name__='mock_plr_pkg'))

        assert added == 1
        assert updated == 0
        self.mock_ads_service.add_or_update_labware_definition.assert_called_once()
        call_args = self.mock_ads_service.add_or_update_labware_definition.call_args[1]

        assert call_args['python_fqn'] == 'mock_module.json_props.MockResourceWithJsonProps'
        assert call_args['pylabrobot_definition_name'] == "json_props_type"
        assert call_args['praxis_labware_type_name'] == "JSONModel" 
        assert call_args['category'] == LabwareCategoryEnum.PLATE 
        assert call_args['model'] == "JSONModel" 
        assert call_args['size_x_mm'] == 90.0 
        assert call_args['size_y_mm'] == 70.0 
        assert call_args['size_z_mm'] == 15.0 
        assert call_args['nominal_volume_ul'] == 250.0 
        expected_details = {"model": "JSONModel", "category": "plate", "size_x": 90.0, "size_y": 70.0, "size_z": 15.0, "capacity": 250.0}
        
        actual_details = call_args['plr_definition_details_json'].copy()
        if 'name' in actual_details: # name is temporary and not part of the stored details
            del actual_details['name']
        assert actual_details == expected_details
        assert call_args['is_consumable'] is True 

```
