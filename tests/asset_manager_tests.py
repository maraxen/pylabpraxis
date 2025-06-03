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
ResourceInstanceOrmMock = MagicMock
ResourceDefinitionCatalogOrmMock = MagicMock
AssetRequirementModelMock = MagicMock

# Enums
from praxis.backend.database_models.asset_management_orm import (
    ManagedDeviceStatusEnum, ResourceInstanceStatusEnum, PraxisDeviceCategoryEnum, ResourceCategoryEnum,
    DeckLayoutOrm, DeckSlotOrm # ADDED for DeckLoading tests
)
from praxis.protocol_core.definitions import PlrDeck as ProtocolPlrDeck # ADDED for DeckLoading tests

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

# --- New/Simpler Mock PyLabRobot Base Classes for specific sync tests ---
class SomeNonSimpleType: # For complex constructor testing
    pass

class MockBasePlrResource: # Simplified base for these tests
    # Class attributes to be potentially used if instantiation fails or is skipped
    model: Optional[str] = "BaseClassModel"
    resource_type: Optional[str] = "base_class_resource"
    # For _get_category_from_class_name
    __name__ = "MockBasePlrResource"

    def __init__(self, name: str, **kwargs: Any):
        self.name = name
        # Instance attributes override class attributes if instance is created
        self.model = kwargs.get("model", self.model)
        self.resource_type = kwargs.get("resource_type", self.resource_type)
        self.__class__.__module__ = kwargs.get("module_name", "pylabrobot.resources.mock_sync_tests")
        # Ensure __name__ is set on the instance's class for inspect.getdoc
        self.__class__.__name__ = self.__class__.__name__


    def serialize(self) -> Dict[str, Any]:
        # Basic serialization, subclasses should extend
        return {"name": self.name, "model": self.model, "resource_type": self.resource_type}

class MockBaseItemizedResource(MockBasePlrResource):
    # Class attributes
    __name__ = "MockBaseItemizedResource"

    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.items: List[Any] = kwargs.get("items", [])
        self.wells: List[Any] = kwargs.get("wells", [])
        # Ensure __name__ is set on the instance's class
        self.__class__.__name__ = self.__class__.__name__


# Test-specific mock classes
class MockResourceSimple(MockBasePlrResource):
    # Override class attributes if needed, or rely on MockBasePlrResource
    model = "SimpleModel" # Class attribute
    resource_type = "simple_resource" # Class attribute
    __name__ = "MockResourceSimple"

    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name, **kwargs)
        # Instance attributes
        self.size_x: float = 10.0
        self.size_y: float = 20.0
        self.size_z: float = 30.0
        self.capacity: float = 100.0
        self.__class__.__module__ = "pylabrobot.resources.mock_simple"
        self.__class__.__name__ = "MockResourceSimple"


    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            "size_x": self.size_x, "size_y": self.size_y, "size_z": self.size_z,
            "capacity": self.capacity
        })
        return data

class MockResourceItemized(MockBaseItemizedResource):
    model = "ItemizedModel"
    resource_type = "itemized_resource"
    __name__ = "MockResourceItemized"

    def __init__(self, name: str, num_items_init: int = 5, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.num_items = num_items_init # Direct attribute for num_items extraction
        self.wells = [MagicMock(name=f"W{i+1}") for i in range(num_items_init)]
        self.__class__.__module__ = "pylabrobot.resources.mock_itemized"
        self.__class__.__name__ = "MockResourceItemized"


    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            "num_items": self.num_items,
            "wells_data": [{"name": w.name} for w in self.wells] # Simulate serialized well data
        })
        return data

class MockResourceComplexConstructor(MockBasePlrResource):
    model = "ComplexModel" # Class attribute
    resource_type = "complex_resource" # Class attribute
    class_volume = 50.0 # Class attribute for testing fallback
    __name__ = "MockResourceComplexConstructor"


    def __init__(self, name: str, required_object: SomeNonSimpleType, optional_int: int = 0, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.required_object = required_object
        self.optional_int = optional_int
        self.__class__.__module__ = "pylabrobot.resources.mock_complex"
        self.__class__.__name__ = "MockResourceComplexConstructor"
        # No serialize method, as it shouldn't be called if instantiation is skipped.

class MockResourceInstantiationFails(MockBasePlrResource):
    model = "FailModel" # Class attribute
    resource_type = "fail_resource" # Class attribute
    class_size_x = 5.0 # Class attribute for testing fallback
    __name__ = "MockResourceInstantiationFails"

    def __init__(self, name: str, **kwargs: Any):
        # super().__init__(name, **kwargs) # Don't call super if init itself fails
        self.__class__.__module__ = "pylabrobot.resources.mock_fails"
        self.__class__.__name__ = "MockResourceInstantiationFails"
        raise ValueError("Cannot instantiate this")

    # No serialize method as it won't be instantiated.

# --- End New/Simpler Mock PyLabRobot Base Classes ---
# --- End Mock PyLabRobot Base Classes ---

# Helper function for mocking module discovery
def setup_mock_modules(mock_walk_packages_target, mock_import_module_target, mock_getmembers_target, resource_classes_to_discover):
    """
    Configures mocks for pkgutil.walk_packages, importlib.import_module, and inspect.getmembers
    to simulate the discovery of specified resource_classes.
    """
    discovered_modules_info = {} # Stores {module_name: (mock_module_obj, list_of_members)}

    for r_class in resource_classes_to_discover:
        module_name = r_class.__module__
        class_name = r_class.__name__

        if module_name not in discovered_modules_info:
            mock_module = MagicMock()
            mock_module.__name__ = module_name
            # Attach the class to the mock module object directly
            setattr(mock_module, class_name, r_class)
            discovered_modules_info[module_name] = (mock_module, [])

        # Ensure the class is also in the list of members for getmembers
        # and re-set it on the module object in case the module was already created
        current_module_obj, members_list = discovered_modules_info[module_name]
        if not hasattr(current_module_obj, class_name): # Avoid duplicate setattr if module processed multiple times
             setattr(current_module_obj, class_name, r_class)

        # Avoid adding duplicate (name, class) tuples to members_list
        if not any(m[0] == class_name for m in members_list):
            members_list.append((class_name, r_class))


    mock_walk_packages_target.return_value = [
        (None, name, False) for name in discovered_modules_info.keys()
    ]

    def import_module_side_effect(name_import):
        if name_import in discovered_modules_info:
            return discovered_modules_info[name_import][0]
        # Fallback for other imports if AssetManager tries to import something else from pylabrobot.resources
        if name_import.startswith("pylabrobot.resources"):
            # print(f"DEBUG_IMPORT_HELPER: Mock importing {name_import} as new MagicMock")
            return MagicMock(__name__=name_import) # Return a generic mock for other PLR modules
        raise ImportError(f"No mock for module {name_import} in setup_mock_modules")
    mock_import_module_target.side_effect = import_module_side_effect

    def getmembers_side_effect(module_obj, predicate=None): # Added predicate
        # predicate is often inspect.isclass, ensure it works with our mocks
        module_name_lookup = getattr(module_obj, '__name__', None)
        if module_name_lookup in discovered_modules_info:
            # print(f"DEBUG_GETMEMBERS_HELPER: Returning members for {module_name_lookup}: {discovered_modules_info[module_name_lookup][1]}")
            # Filter by predicate if provided, as inspect.getmembers does
            if predicate:
                return [(name, member) for name, member in discovered_modules_info[module_name_lookup][1] if predicate(member)]
            return discovered_modules_info[module_name_lookup][1]
        # print(f"DEBUG_GETMEMBERS_HELPER: No members for {module_name_lookup}")
        return []
    mock_getmembers_target.side_effect = getmembers_side_effect


@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def mock_workcell_runtime():
    m = MagicMock()
    m.initialize_device_backend.return_value = MagicMock(name="live_mock_device")
    m.create_or_get_resource_plr_object.return_value = MagicMock(name="live_mock_resource")
    return m

@pytest.fixture
def mock_ads_service():
    with patch('praxis.backend.core.asset_manager.ads') as mock_ads:
        mock_ads.list_managed_devices.return_value = []
        mock_ads.get_managed_device_by_id.return_value = None
        mock_ads.update_managed_device_status.return_value = MagicMock(spec=ManagedDeviceOrmMock)

        mock_ads.list_resource_instances.return_value = []
        mock_ads.get_resource_instance_by_id.return_value = None
        mock_ads.get_resource_definition.return_value = None
        mock_ads.add_or_update_resource_definition.return_value = MagicMock(spec=ResourceDefinitionCatalogOrmMock)
        mock_ads.update_resource_instance_location_and_status.return_value = MagicMock(spec=ResourceInstanceOrmMock)
        yield mock_ads


@pytest.fixture
def asset_manager(mock_db_session: MagicMock, mock_workcell_runtime: MagicMock, mock_ads_service: MagicMock):
    return AssetManager(db_session=mock_db_session, workcell_runtime=mock_workcell_runtime)

class TestAssetManagerAcquireDevice:

    def test_acquire_device_success(self, asset_manager: AssetManager, mock_ads_service: MagicMock, mock_workcell_runtime: MagicMock):
        mock_device_orm = ManagedDeviceOrmMock(id=1, user_friendly_name="Device1", python_fqn="SomeDeviceClass")
        mock_ads_service.list_managed_devices.return_value = [mock_device_orm]
        updated_mock_device_orm = ManagedDeviceOrmMock(id=1, user_friendly_name="Device1", current_status=ManagedDeviceStatusEnum.IN_USE)
        mock_ads_service.update_managed_device_status.return_value = updated_mock_device_orm

        live_device, orm_id, dev_type = asset_manager.acquire_device(
            protocol_run_guid="run123",
            requested_asset_name_in_protocol="dev_in_proto",
            python_fqn_constraint="SomeDeviceClass"
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


class TestAssetManagerAcquireResource:

    @pytest.fixture
    def mock_resource_def(self):
        mock_def = ResourceDefinitionCatalogOrmMock()
        mock_def.python_fqn = "pylabrobot.resources.plate.Plate"
        return mock_def

    def test_acquire_resource_success_from_storage(
        self, asset_manager: AssetManager, mock_ads_service: MagicMock,
        mock_workcell_runtime: MagicMock, mock_resource_def: MagicMock
    ):
        mock_lw_instance_orm = ResourceInstanceOrmMock(id=1, user_assigned_name="Plate1", name="some_plate_def_name")
        mock_ads_service.list_resource_instances.side_effect = [
            [],
            [mock_lw_instance_orm]
        ]
        mock_ads_service.get_resource_definition.return_value = mock_resource_def
        updated_mock_lw_instance_orm = ResourceInstanceOrmMock(id=1, user_assigned_name="Plate1", current_status=ResourceInstanceStatusEnum.IN_USE)
        mock_ads_service.update_resource_instance_location_and_status.return_value = updated_mock_lw_instance_orm

        live_resource, orm_id, lw_type = asset_manager.acquire_resource(
            protocol_run_guid="run123",
            requested_asset_name_in_protocol="lw_in_proto",
            name_constraint="some_plate_def_name"
        )

        mock_ads_service.get_resource_definition.assert_called_once_with(asset_manager.db, "some_plate_def_name")
        mock_workcell_runtime.create_or_get_resource_plr_object.assert_called_once_with(
            resource_instance_orm=mock_lw_instance_orm,
            resource_definition_fqn="pylabrobot.resources.plate.Plate"
        )
        mock_ads_service.update_resource_instance_location_and_status.assert_called_with(
            asset_manager.db, mock_lw_instance_orm.id,
            new_status=ResourceInstanceStatusEnum.IN_USE,
            current_protocol_run_guid="run123",
            status_details="In use by run run123"
        )
        assert live_resource is mock_workcell_runtime.create_or_get_resource_plr_object.return_value
        assert orm_id == 1
        assert lw_type == "resource"

    def test_acquire_resource_with_deck_assignment(
        self, asset_manager: AssetManager, mock_ads_service: MagicMock,
        mock_workcell_runtime: MagicMock, mock_resource_def: MagicMock
    ):
        mock_lw_instance_orm = ResourceInstanceOrmMock(id=1, user_assigned_name="Plate1", name="some_plate_def_name")
        mock_deck_orm = ManagedDeviceOrmMock(id=10, user_friendly_name="MainDeck")

        mock_ads_service.list_resource_instances.return_value = [mock_lw_instance_orm]
        mock_ads_service.get_resource_definition.return_value = mock_resource_def
        mock_ads_service.list_managed_devices.return_value = [mock_deck_orm]
        mock_ads_service.update_resource_instance_location_and_status.return_value = mock_lw_instance_orm

        location_constraints = {"deck_name": "MainDeck", "slot_name": "A1"}
        asset_manager.acquire_resource(
            protocol_run_guid="run123",
            requested_asset_name_in_protocol="plate_on_deck",
            name_constraint="some_plate_def_name",
            location_constraints=location_constraints
        )

        mock_ads_service.list_managed_devices.assert_called_once_with(
            asset_manager.db, user_friendly_name_filter="MainDeck", praxis_category_filter=PraxisDeviceCategoryEnum.DECK
        )
        mock_workcell_runtime.assign_resource_to_deck_slot.assert_called_once_with(
            deck_device_orm_id=mock_deck_orm.id,
            slot_name="A1",
            resource_plr_object=mock_workcell_runtime.create_or_get_resource_plr_object.return_value,
            resource_instance_orm_id=mock_lw_instance_orm.id
        )
        mock_ads_service.update_resource_instance_location_and_status.assert_called_with(
            asset_manager.db, mock_lw_instance_orm.id,
            new_status=ResourceInstanceStatusEnum.IN_USE,
            current_protocol_run_guid="run123",
            status_details="In use by run run123"
        )

    def test_acquire_resource_fqn_not_found(self, asset_manager: AssetManager, mock_ads_service: MagicMock):
        mock_lw_instance_orm = ResourceInstanceOrmMock(id=1, name="unknown_def_name")
        mock_ads_service.list_resource_instances.return_value = [mock_lw_instance_orm]
        mock_ads_service.get_resource_definition.return_value = None

        with pytest.raises(AssetAcquisitionError, match="Python FQN not found for resource definition 'unknown_def_name'"):
            asset_manager.acquire_resource("run123", "lw", "unknown_def_name")

        mock_ads_service.update_resource_instance_location_and_status.assert_called_once_with(
            db=asset_manager.db, resource_instance_id=mock_lw_instance_orm.id,
            new_status=ResourceInstanceStatusEnum.ERROR,
            status_details=ANY
        )

    def test_acquire_resource_plr_object_creation_fails(
        self, asset_manager: AssetManager, mock_ads_service: MagicMock,
        mock_workcell_runtime: MagicMock, mock_resource_def: MagicMock
    ):
        mock_lw_instance_orm = ResourceInstanceOrmMock(id=1, user_assigned_name="Plate1", name="def")
        mock_ads_service.list_resource_instances.return_value = [mock_lw_instance_orm]
        mock_ads_service.get_resource_definition.return_value = mock_resource_def
        mock_workcell_runtime.create_or_get_resource_plr_object.return_value = None

        with pytest.raises(AssetAcquisitionError, match="Failed to create PLR object for resource 'Plate1'"):
            asset_manager.acquire_resource("run123", "lw", "def")

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

    def test_release_resource_no_deck_clear(
        self, asset_manager: AssetManager, mock_ads_service: MagicMock, mock_workcell_runtime: MagicMock
    ):
        asset_manager.release_resource(
            resource_instance_orm_id=1,
            final_status=ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
            status_details="Stored after run"
        )
        mock_workcell_runtime.clear_deck_slot.assert_not_called()
        mock_ads_service.update_resource_instance_location_and_status.assert_called_once_with(
            asset_manager.db, 1,
            new_status=ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
            properties_json_update=None,
            location_device_id=None,
            current_deck_slot_name=None,
            current_protocol_run_guid=None,
            status_details="Stored after run"
        )

    def test_release_resource_with_deck_clear(
        self, asset_manager: AssetManager, mock_ads_service: MagicMock, mock_workcell_runtime: MagicMock
    ):
        asset_manager.release_resource(
            resource_instance_orm_id=1,
            final_status=ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
            clear_from_deck_device_id=10,
            clear_from_slot_name="A1",
            status_details="Cleared from deck and stored"
        )
        mock_workcell_runtime.clear_deck_slot.assert_called_once_with(
            deck_device_orm_id=10, slot_name="A1", resource_instance_orm_id=1
        )
        mock_ads_service.update_resource_instance_location_and_status.assert_called_once_with(
            asset_manager.db, 1,
            new_status=ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
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
        self.mock_get_constructor_params = MagicMock() # Mock for get_resource_constructor_params

        # Patch targets for the helper function
        self.mock_walk_packages_target = MagicMock(name="walk_packages_target_in_fixture")
        self.mock_import_module_target = MagicMock(name="import_module_target_in_fixture")
        self.mock_getmembers_target = MagicMock(name="getmembers_target_in_fixture")


        monkeypatch.setattr("praxis.backend.core.asset_manager.pkgutil.walk_packages", self.mock_walk_packages_target)
        monkeypatch.setattr("praxis.backend.core.asset_manager.importlib.import_module", self.mock_import_module_target)
        monkeypatch.setattr("praxis.backend.core.asset_manager.inspect.getmembers", self.mock_getmembers_target) # Patched here

        monkeypatch.setattr("praxis.backend.core.asset_manager.inspect.isabstract", self.mock_isabstract_inspect)
        monkeypatch.setattr("praxis.backend.core.asset_manager.inspect.isclass", self.mock_isclass_inspect)
        monkeypatch.setattr("praxis.backend.core.asset_manager.issubclass", self.mock_issubclass_inspect)
        # Patch for the constructor param utility
        monkeypatch.setattr("praxis.backend.core.asset_manager.get_resource_constructor_params", self.mock_get_constructor_params)


        # Keep existing PLR base class mocks as they might be used by other tests
        # The new simple mocks are additive for the new tests.
        monkeypatch.setattr("praxis.backend.core.asset_manager.PlrResource", MockPlrResource) # Original detailed mock
        monkeypatch.setattr("praxis.backend.core.asset_manager.Container", MockPlrContainer) # Original detailed mock
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
        self.mock_ads_service.get_resource_definition.return_value = None

        added, updated = asset_manager.sync_pylabrobot_definitions(plr_resources_package=MagicMock(__path__=['dummy'], __name__='mock_plr_pkg'))

        assert added == 1
        assert updated == 0
        self.mock_ads_service.add_or_update_resource_definition.assert_called_once()
        call_args = self.mock_ads_service.add_or_update_resource_definition.call_args[1]

        assert call_args['python_fqn'] == 'mock_pylabrobot_module.plates.MockSimplePlateToSync'
        assert call_args['name'] == "simple_plate_type_inst"
        assert call_args['resource_type'] == "TestModel123"
        assert call_args['category'] == ResourceCategoryEnum.PLATE
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
        self.mock_ads_service.get_resource_definition.return_value = None

        added, updated = asset_manager.sync_pylabrobot_definitions(plr_resources_package=MagicMock(__path__=['dummy'], __name__='mock_plr_pkg'))

        assert added == 1
        assert updated == 0
        self.mock_ads_service.add_or_update_resource_definition.assert_called_once()
        call_args = self.mock_ads_service.add_or_update_resource_definition.call_args[1]

        assert call_args['python_fqn'] == 'mock_module.complex.MockComplexResource'
        assert call_args['name'] == "complex_static_type"
        assert call_args['description'] == "Description for complex resource"
        assert call_args['category'] == ResourceCategoryEnum.OTHER
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
        self.mock_ads_service.get_resource_definition.return_value = None

        added, updated = asset_manager.sync_pylabrobot_definitions(plr_resources_package=MagicMock(__path__=['dummy'], __name__='mock_plr_pkg'))

        assert added == 1
        assert updated == 0
        self.mock_ads_service.add_or_update_resource_definition.assert_called_once()
        call_args = self.mock_ads_service.add_or_update_resource_definition.call_args[1]

        assert call_args['python_fqn'] == 'mock_module.failing.MockFailingResource'
        assert call_args['name'] == "failing_static_type"
        assert call_args['description'] == "Description for failing resource"
        assert call_args['category'] == ResourceCategoryEnum.OTHER
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

        self.mock_ads_service.get_resource_definition.return_value = None

        added, updated = asset_manager.sync_pylabrobot_definitions(plr_resources_package=MagicMock(__path__=['dummy'], __name__='mock_plr_pkg'))

        asset_manager.EXCLUDED_CLASS_NAMES = original_excluded_names

        assert added == 1
        assert updated == 0
        self.mock_ads_service.add_or_update_resource_definition.assert_called_once()
        call_args = self.mock_ads_service.add_or_update_resource_definition.call_args[1]
        assert call_args['python_fqn'] == 'mock_module.kept.KeptResource'
        assert call_args['name'] == "kept_resource_type"

    # This test replaces the old test_sync_property_extraction_from_details_json
    # and incorporates checks for the new fields praxis_extracted_num_items and praxis_extracted_ordering
    def test_sync_extracts_basic_properties_and_new_fields(self, asset_manager: AssetManager, caplog):
        # Use the setup_mock_modules helper
        setup_mock_modules(
            self.mock_walk_packages_target,
            self.mock_import_module_target,
            self.mock_getmembers_target,
            [MockResourceSimple, MockResourceItemized]
        )

        # Mock get_resource_constructor_params for each class
        # For MockResourceSimple
        simple_params = {'name': {'type': 'str', 'required': True, 'default': inspect.Parameter.empty}}
        # For MockResourceItemized
        itemized_params = {
            'name': {'type': 'str', 'required': True, 'default': inspect.Parameter.empty},
            'num_items_init': {'type': 'int', 'required': False, 'default': 5}
        }

        def get_constructor_params_side_effect(cls):
            if cls == MockResourceSimple: return simple_params
            if cls == MockResourceItemized: return itemized_params
            return {}
        self.mock_get_constructor_params.side_effect = get_constructor_params_side_effect

        self.mock_ads_service.get_resource_definition.return_value = None # New definitions

        added, updated = asset_manager.sync_pylabrobot_definitions()

        assert added == 2
        assert updated == 0
        assert self.mock_ads_service.add_or_update_resource_definition.call_count == 2

        calls_args_list = self.mock_ads_service.add_or_update_resource_definition.call_args_list

        # Call 1: MockResourceSimple
        args_simple = calls_args_list[0][1]
        assert args_simple['python_fqn'] == 'pylabrobot.resources.mock_simple.MockResourceSimple'
        assert args_simple['name'] == 'simple_resource' # From class attribute
        assert args_simple['resource_type'] == 'SimpleModel' # From class attribute, instance uses it
        assert args_simple['category'] == ResourceCategoryEnum.OTHER # Default from MockBasePlrResource via _get_category_from_plr_object
        assert args_simple['model'] == 'SimpleModel'
        assert args_simple['size_x_mm'] == 10.0
        assert args_simple['size_y_mm'] == 20.0
        assert args_simple['size_z_mm'] == 30.0
        assert args_simple['nominal_volume_ul'] == 100.0
        details_simple = args_simple['plr_definition_details_json']
        assert "praxis_extracted_num_items" not in details_simple # Or assert it's None
        assert "praxis_extracted_ordering" not in details_simple # Or assert it's None

        # Call 2: MockResourceItemized
        args_itemized = calls_args_list[1][1]
        assert args_itemized['python_fqn'] == 'pylabrobot.resources.mock_itemized.MockResourceItemized'
        assert args_itemized['name'] == 'itemized_resource'
        assert args_itemized['resource_type'] == 'ItemizedModel'
        assert args_itemized['category'] == ResourceCategoryEnum.OTHER # Default
        assert args_itemized['model'] == 'ItemizedModel'
        details_itemized = args_itemized['plr_definition_details_json']
        assert details_itemized.get('praxis_extracted_num_items') == 5
        assert details_itemized.get('praxis_extracted_ordering') == "W1,W2,W3,W4,W5"

    def test_sync_handles_complex_constructor_gracefully(self, asset_manager: AssetManager, caplog):
        setup_mock_modules(
            self.mock_walk_packages_target,
            self.mock_import_module_target,
            self.mock_getmembers_target,
            [MockResourceComplexConstructor]
        )

        self.mock_get_constructor_params.return_value = {
            'name': {'type': 'str', 'required': True, 'default': inspect.Parameter.empty},
            'required_object': {'type': 'SomeNonSimpleType', 'required': True, 'default': inspect.Parameter.empty},
            'optional_int': {'type': 'int', 'required': False, 'default': 0}
        }
        self.mock_ads_service.get_resource_definition.return_value = None

        added, updated = asset_manager.sync_pylabrobot_definitions()

        assert added == 1
        assert self.mock_ads_service.add_or_update_resource_definition.call_count == 1
        args_complex = self.mock_ads_service.add_or_update_resource_definition.call_args[1]

        assert args_complex['python_fqn'] == 'pylabrobot.resources.mock_complex.MockResourceComplexConstructor'
        assert args_complex['name'] == 'complex_resource' # From class
        assert args_complex['resource_type'] == 'ComplexModel' # From class
        assert args_complex['model'] == 'ComplexModel' # From class attribute, as instance not created
        assert args_complex['nominal_volume_ul'] is None # class_volume not automatically picked up by _extract_volume from class
        # Ensure details_json does not contain instance-specific data if temp_instance was None
        details_complex = args_complex['plr_definition_details_json']
        # If temp_instance is None, details_json will be {} (after initialization) or None if not touched.
        # If it's {}, then these praxis_extracted keys won't be there.
        assert "praxis_extracted_num_items" not in details_complex
        assert "praxis_extracted_ordering" not in details_complex

        assert "INFO: AM_SYNC: Skipping instantiation for pylabrobot.resources.mock_complex.MockResourceComplexConstructor due to complex required parameter 'required_object' of type 'SomeNonSimpleType'" in caplog.text
        assert "INFO: AM_SYNC: Proceeding to extract data for pylabrobot.resources.mock_complex.MockResourceComplexConstructor without a temporary instance" in caplog.text


    def test_sync_handles_instantiation_failure_gracefully(self, asset_manager: AssetManager, caplog):
        setup_mock_modules(
            self.mock_walk_packages_target,
            self.mock_import_module_target,
            self.mock_getmembers_target,
            [MockResourceInstantiationFails]
        )

        self.mock_get_constructor_params.return_value = {
            'name': {'type': 'str', 'required': True, 'default': inspect.Parameter.empty}
        }
        self.mock_ads_service.get_resource_definition.return_value = None

        added, updated = asset_manager.sync_pylabrobot_definitions()

        assert added == 1
        assert self.mock_ads_service.add_or_update_resource_definition.call_count == 1
        args_fail = self.mock_ads_service.add_or_update_resource_definition.call_args[1]

        assert args_fail['python_fqn'] == 'pylabrobot.resources.mock_fails.MockResourceInstantiationFails'
        assert args_fail['name'] == 'fail_resource' # From class
        assert args_fail['resource_type'] == 'FailModel' # From class
        assert args_fail['model'] == 'FailModel' # From class attribute
        # class_size_x is not automatically picked up by _extract_dimensions from class.
        assert args_fail['size_x_mm'] is None

        assert "WARNING: AM_SYNC: Instantiation of pylabrobot.resources.mock_fails.MockResourceInstantiationFails failed even with smart defaults: ValueError('Cannot instantiate this')" in caplog.text
        assert "INFO: AM_SYNC: Proceeding to extract data for pylabrobot.resources.mock_fails.MockResourceInstantiationFails without a temporary instance" in caplog.text


class TestAssetManagerDeckLoading:

    @pytest.fixture
    def mock_deck_layout_orm(self):
        deck_layout = MagicMock(spec=DeckLayoutOrm)
        deck_layout.id = 1
        deck_layout.name = "TestDeckLayout"
        # deck_layout.managing_device_id = 50 # Assuming a link if needed, or handled by name+category
        return deck_layout

    @pytest.fixture
    def mock_deck_device_orm(self):
        deck_device = MagicMock(spec=ManagedDeviceOrm)
        deck_device.id = 50
        deck_device.user_friendly_name = "TestDeckLayout" # Matching layout name
        deck_device.praxis_device_category = PraxisDeviceCategoryEnum.DECK
        deck_device.current_status = ManagedDeviceStatusEnum.AVAILABLE
        deck_device.current_protocol_run_guid = None
        return deck_device

    @pytest.fixture
    def mock_slot_orm(self, mock_resource_instance_orm):
        slot = MagicMock(spec=DeckSlotOrm)
        slot.id = 101
        slot.slot_name = "A1"
        slot.pre_assigned_resource_instance_id = mock_resource_instance_orm.id
        slot.default_resource_definition_id = None
        return slot

    @pytest.fixture
    def mock_resource_instance_orm(self):
        lw_instance = MagicMock(spec=ResourceInstanceOrm)
        lw_instance.id = 201
        lw_instance.user_assigned_name = "TestPlateOnDeck"
        lw_instance.name = "test_plate_def_name"
        lw_instance.current_status = ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE
        lw_instance.current_protocol_run_guid = None
        lw_instance.location_device_id = None
        lw_instance.current_deck_slot_name = None
        return lw_instance

    @pytest.fixture
    def mock_resource_def_catalog_orm(self):
        lw_def = MagicMock(spec=ResourceDefinitionCatalogOrm)
        lw_def.name = "test_plate_def_name"
        lw_def.python_fqn = "pylabrobot.resources.plate.Plate"
        return lw_def

    def test_deck_layout_not_found(self, asset_manager: AssetManager, mock_ads_service: MagicMock):
        mock_ads_service.get_deck_layout_by_name.return_value = None
        with pytest.raises(AssetAcquisitionError, match="Deck layout 'NonExistentLayout' not found"):
            asset_manager.apply_deck_configuration("NonExistentLayout", "run123")

    def test_deck_device_not_found(self, asset_manager: AssetManager, mock_ads_service: MagicMock, mock_deck_layout_orm):
        mock_ads_service.get_deck_layout_by_name.return_value = mock_deck_layout_orm
        mock_ads_service.list_managed_devices.return_value = [] # No deck device found
        with pytest.raises(AssetAcquisitionError, match="No ManagedDevice found for deck 'TestDeckLayout' with category DECK"):
            asset_manager.apply_deck_configuration("TestDeckLayout", "run123")
        mock_ads_service.list_managed_devices.assert_called_once_with(
            asset_manager.db,
            user_friendly_name_filter="TestDeckLayout",
            praxis_category_filter=PraxisDeviceCategoryEnum.DECK
        )

    def test_deck_device_init_fails(
        self, asset_manager: AssetManager, mock_ads_service: MagicMock,
        mock_deck_layout_orm, mock_deck_device_orm, mock_workcell_runtime: MagicMock
    ):
        mock_ads_service.get_deck_layout_by_name.return_value = mock_deck_layout_orm
        mock_ads_service.list_managed_devices.return_value = [mock_deck_device_orm]
        mock_workcell_runtime.initialize_device_backend.return_value = None # Deck init fails

        with pytest.raises(AssetAcquisitionError, match="Failed to initialize backend for deck device 'TestDeckLayout'"):
            asset_manager.apply_deck_configuration("TestDeckLayout", "run123")
        mock_workcell_runtime.initialize_device_backend.assert_called_once_with(mock_deck_device_orm)

    def test_successful_deck_config_no_resource(
        self, asset_manager: AssetManager, mock_ads_service: MagicMock,
        mock_deck_layout_orm, mock_deck_device_orm, mock_workcell_runtime: MagicMock
    ):
        mock_ads_service.get_deck_layout_by_name.return_value = mock_deck_layout_orm
        mock_ads_service.list_managed_devices.return_value = [mock_deck_device_orm]
        live_plr_deck_obj = MagicMock(name="LivePlrDeck")
        mock_workcell_runtime.initialize_device_backend.return_value = live_plr_deck_obj
        mock_ads_service.get_deck_slots_for_layout.return_value = [] # No slots with resource

        returned_deck = asset_manager.apply_deck_configuration("TestDeckLayout", "run123")

        assert returned_deck == live_plr_deck_obj
        mock_ads_service.update_managed_device_status.assert_called_once_with(
            asset_manager.db, mock_deck_device_orm.id, ManagedDeviceStatusEnum.IN_USE,
            current_protocol_run_guid="run123",
            status_details="Deck 'TestDeckLayout' in use by run run123"
        )
        mock_workcell_runtime.assign_resource_to_deck_slot.assert_not_called()

    def test_successful_deck_config_with_one_resource(
        self, asset_manager: AssetManager, mock_ads_service: MagicMock,
        mock_deck_layout_orm, mock_deck_device_orm, mock_slot_orm,
        mock_resource_instance_orm, mock_resource_def_catalog_orm, mock_workcell_runtime: MagicMock
    ):
        mock_ads_service.get_deck_layout_by_name.return_value = mock_deck_layout_orm
        mock_ads_service.list_managed_devices.return_value = [mock_deck_device_orm]
        live_plr_deck_obj = MagicMock(name="LivePlrDeck")
        mock_workcell_runtime.initialize_device_backend.return_value = live_plr_deck_obj
        mock_ads_service.get_deck_slots_for_layout.return_value = [mock_slot_orm]
        mock_ads_service.get_resource_instance_by_id.return_value = mock_resource_instance_orm
        mock_ads_service.get_resource_definition.return_value = mock_resource_def_catalog_orm

        live_plr_resource_obj = MagicMock(name="LiveTestPlate")
        mock_workcell_runtime.create_or_get_resource_plr_object.return_value = live_plr_resource_obj

        asset_manager.apply_deck_configuration(ProtocolPlrDeck(name="TestDeckLayout"), "run123") # Test with PlrDeck input

        mock_ads_service.get_resource_instance_by_id.assert_called_once_with(asset_manager.db, mock_resource_instance_orm.id)
        mock_ads_service.get_resource_definition.assert_called_once_with(asset_manager.db, mock_resource_instance_orm.name)
        mock_workcell_runtime.create_or_get_resource_plr_object.assert_called_once_with(
            resource_instance_orm=mock_resource_instance_orm,
            resource_definition_fqn=mock_resource_def_catalog_orm.python_fqn
        )
        mock_workcell_runtime.assign_resource_to_deck_slot.assert_called_once_with(
            deck_device_orm_id=mock_deck_device_orm.id,
            slot_name=mock_slot_orm.slot_name,
            resource_plr_object=live_plr_resource_obj,
            resource_instance_orm_id=mock_resource_instance_orm.id
        )
        mock_ads_service.update_resource_instance_location_and_status.assert_called_once_with(
            db=asset_manager.db,
            resource_instance_id=mock_resource_instance_orm.id,
            new_status=ResourceInstanceStatusEnum.IN_USE,
            current_protocol_run_guid="run123",
            location_device_id=mock_deck_device_orm.id,
            current_deck_slot_name=mock_slot_orm.slot_name,
            deck_slot_orm_id=mock_slot_orm.id,
            status_details=f"On deck '{mock_deck_layout_orm.name}' slot '{mock_slot_orm.slot_name}' for run run123"
        )

    def test_resource_instance_not_available_for_slot(
        self, asset_manager: AssetManager, mock_ads_service: MagicMock,
        mock_deck_layout_orm, mock_deck_device_orm, mock_slot_orm,
        mock_resource_instance_orm, mock_workcell_runtime: MagicMock
    ):
        mock_resource_instance_orm.current_status = ResourceInstanceStatusEnum.IN_USE # Not available
        mock_resource_instance_orm.current_protocol_run_guid = "another_run"

        mock_ads_service.get_deck_layout_by_name.return_value = mock_deck_layout_orm
        mock_ads_service.list_managed_devices.return_value = [mock_deck_device_orm]
        mock_workcell_runtime.initialize_device_backend.return_value = MagicMock()
        mock_ads_service.get_deck_slots_for_layout.return_value = [mock_slot_orm]
        mock_ads_service.get_resource_instance_by_id.return_value = mock_resource_instance_orm

        with pytest.raises(AssetAcquisitionError, match="is not available"):
            asset_manager.apply_deck_configuration("TestDeckLayout", "run123")

    def test_resource_def_fqn_not_found_for_slot_resource(
        self, asset_manager: AssetManager, mock_ads_service: MagicMock,
        mock_deck_layout_orm, mock_deck_device_orm, mock_slot_orm,
        mock_resource_instance_orm, mock_resource_def_catalog_orm, mock_workcell_runtime: MagicMock
    ):
        mock_resource_def_catalog_orm.python_fqn = None # FQN missing

        mock_ads_service.get_deck_layout_by_name.return_value = mock_deck_layout_orm
        mock_ads_service.list_managed_devices.return_value = [mock_deck_device_orm]
        mock_workcell_runtime.initialize_device_backend.return_value = MagicMock()
        mock_ads_service.get_deck_slots_for_layout.return_value = [mock_slot_orm]
        mock_ads_service.get_resource_instance_by_id.return_value = mock_resource_instance_orm
        mock_ads_service.get_resource_definition.return_value = mock_resource_def_catalog_orm

        with pytest.raises(AssetAcquisitionError, match="Python FQN not found for resource definition"):
            asset_manager.apply_deck_configuration("TestDeckLayout", "run123")

# --- Tests for AssetManager Logging (New Class) ---
class TestAssetManagerLogging:

    def test_acquire_resource_logs_property_constraints(self, asset_manager: AssetManager, mock_ads_service: MagicMock, mock_workcell_runtime: MagicMock, caplog):
        # Setup for a successful resource acquisition to reach the logging point
        mock_lw_instance_orm = ResourceInstanceOrmMock(id=1, user_assigned_name="PlateLogTest", name="log_plate_def")
        mock_resource_def = ResourceDefinitionCatalogOrmMock()
        mock_resource_def.python_fqn = "pylabrobot.resources.plate.Plate" # Valid FQN

        mock_ads_service.list_resource_instances.return_value = [mock_lw_instance_orm]
        mock_ads_service.get_resource_definition.return_value = mock_resource_def
        mock_ads_service.update_resource_instance_location_and_status.return_value = mock_lw_instance_orm
        mock_workcell_runtime.create_or_get_resource_plr_object.return_value = MagicMock(name="live_logging_plate")

        property_constraints_payload = {"min_volume_ul": 10, "is_sterile": True}

        # This is the AssetRequirementModel that Orchestrator would build and pass
        asset_req = AssetRequirementModelMock()
        asset_req.name = "test_plate_for_log"
        asset_req.actual_type_str = "log_plate_def" # Matches name_constraint
        asset_req.constraints_json = property_constraints_payload # This is what we want to log

        # Call acquire_asset, which dispatches to acquire_resource
        try:
            asset_manager.acquire_asset(
                protocol_run_guid="log_run_123",
                asset_requirement=asset_req
            )
        except AssetAcquisitionError: # Catch if something else fails, to still check logs
            pass

        assert f"INFO: AM_ACQUIRE: Resource acquisition for 'test_plate_for_log' includes property_constraints: {property_constraints_payload}" in caplog.text

    def test_release_resource_logs_properties_update(self, asset_manager: AssetManager, mock_ads_service: MagicMock, caplog):
        # Setup for release_resource
        final_props_update = {"content_state": "empty", "cleaned": True}

        # Mock the get_resource_instance_by_id call that might happen if workcell_runtime is None or other logic paths
        # For this test, we are primarily interested in the log message generated by release_resource itself.
        # The actual update logic is tested elsewhere.
        mock_ads_service.update_resource_instance_location_and_status.return_value = MagicMock(spec=ResourceInstanceOrm)


        asset_manager.release_resource(
            resource_instance_orm_id=555,
            final_status=ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
            final_properties_json_update=final_props_update,
            status_details="Logging properties update on release"
        )

        assert f"INFO: AM_RELEASE: Resource release for instance ID 555 includes final_properties_json_update: {final_props_update}" in caplog.text
```
