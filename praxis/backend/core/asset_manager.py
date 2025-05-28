# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-locals, too-many-branches, too-many-statements, E501
"""
praxis/core/asset_manager.py

The AssetManager is responsible for managing the lifecycle and allocation
of physical laboratory assets (devices and labware instances). It interacts
with the AssetDataService for persistence and the WorkcellRuntime for
live PyLabRobot object interactions.

Version 8: Replaces WorkcellRuntimePlaceholder with actual WorkcellRuntime import.
           Integrates Python's logging module, replacing print statements.
"""
from typing import Dict, Any, Optional, List, Type, Tuple, Set, Union
import importlib
import inspect
import pkgutil
import logging # ADDED for logging

from sqlalchemy.orm import Session as DbSession

from praxis.backend.services import asset_data_service as ads

from praxis.backend.database_models.asset_management_orm import (
    ManagedDeviceOrm, LabwareInstanceOrm, LabwareDefinitionCatalogOrm,
    ManagedDeviceStatusEnum, LabwareInstanceStatusEnum,
    PraxisDeviceCategoryEnum
)

# Praxis Protocol Core Models
from praxis.backend.protocol_core.protocol_definition_models import AssetRequirementModel

# Import actual WorkcellRuntime
from praxis.backend.core.workcell_runtime import WorkcellRuntime # ADDED

import pylabrobot.resources
from pylabrobot.resources import (
    Resource as PlrResource, Lid, Carrier, Deck as PlrDeck, Well, Container, Coordinate,
    PlateCarrier, TipCarrier, Trash, ItemizedResource, PlateAdapter,
    TipRack, Plate, Trough as PlrTrough
)
from pylabrobot.resources.plate import Plate as PlrPlate
from pylabrobot.resources.tip_rack import TipRack as PlrTipRack
from pylabrobot.resources.tube_rack import TubeRack as PlrTubeRack
from pylabrobot.resources.tube import Tube as PlrTube
from pylabrobot.resources.tip import Tip as PlrTip
from pylabrobot.resources.petri_dish import PetriDish as PlrPetriDish
from pylabrobot.liquid_handling.backends.backend import LiquidHandlerBackend
from praxis.backend.utils.plr_inspection import get_resource_constructor_params
from praxis.backend.protocol_core.definitions import PlrDeck as ProtocolPlrDeck


# Setup logger for this module
logger = logging.getLogger(__name__) # ADDED

class AssetAcquisitionError(RuntimeError): pass

# Define string constants for categories (as in previous version)
CATEGORY_PLATE = "PLATE"
CATEGORY_TIP_RACK = "TIP_RACK"
CATEGORY_LID = "LID"
CATEGORY_TROUGH = "TROUGH"
CATEGORY_TUBE_RACK = "TUBE_RACK"
CATEGORY_PETRI_DISH = "PETRI_DISH"
CATEGORY_TUBE = "TUBE"
CATEGORY_WASTE = "WASTE"
CATEGORY_CARRIER = "CARRIER"
CATEGORY_OTHER = "OTHER"

CONSUMABLE_CATEGORIES = {
    CATEGORY_PLATE,
    CATEGORY_TIP_RACK,
    CATEGORY_TROUGH,
    CATEGORY_LID,
    CATEGORY_TUBE,
    CATEGORY_PETRI_DISH
}


class AssetManager:
    def __init__(self, db_session: DbSession, workcell_runtime: WorkcellRuntime): # UPDATED type hint
        self.db: DbSession = db_session
        self.workcell_runtime = workcell_runtime # UPDATED: No more placeholder

        self.EXCLUDED_BASE_CLASSES: List[Type[PlrResource]] = [
            PlrResource, Container, ItemizedResource, Well, PlrDeck
        ]
        self.EXCLUDED_CLASS_NAMES: Set[str] = {"WellCreator", "TipCreator", "CarrierSite", "ResourceStack"}

    def _extract_dimensions(self,
                            resource_class: Type[PlrResource],
                            resource: Optional[PlrResource] = None,
                            details: Optional[Dict[str, Any]] = None) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Extracts dimensions (x, y, z) in mm."""
        x, y, z = None, None, None
        try:
            if resource:
                if hasattr(resource, 'get_size_x') and callable(resource.get_size_x): # type: ignore
                    logger.debug(f"AM_EXTRACT_DIM: Extracted from get_size_x/y/z for {resource_class.__name__}")
                    return resource.get_size_x(), resource.get_size_y(), resource.get_size_z() # type: ignore
                if hasattr(resource, 'dimensions') and isinstance(resource.dimensions, Coordinate): # type: ignore
                    logger.debug(f"AM_EXTRACT_DIM: Extracted from 'dimensions' (Coordinate) for {resource_class.__name__}")
                    return resource.dimensions.x, resource.dimensions.y, resource.dimensions.z # type: ignore

                size_x, size_y, size_z = None, None, None
                if hasattr(resource, 'depth'): size_x = getattr(resource, 'depth', None)
                if hasattr(resource, 'width'): size_y = getattr(resource, 'width', None)
                if hasattr(resource, 'height'): size_z = getattr(resource, 'height', None)

                if size_x is not None and size_y is not None and size_z is not None:
                    try:
                        logger.debug(f"AM_EXTRACT_DIM: Extracted from direct attributes (depth, width, height) for {resource_class.__name__}")
                        return float(size_x), float(size_y), float(size_z)
                    except (ValueError, TypeError) as ve:
                        logger.debug(f"AM_EXTRACT_DIM: Conversion error for depth/width/height for {resource_class.__name__}: {ve}")

            if details:
                if "dimensions" in details and isinstance(details["dimensions"], dict):
                    dx_d, dy_d, dz_d = details["dimensions"].get("x"), details["dimensions"].get("y"), details["dimensions"].get("z")
                    if dx_d is not None and dy_d is not None and dz_d is not None:
                        logger.debug(f"AM_EXTRACT_DIM: Extracted from details['dimensions'] for {resource_class.__name__}")
                        return dx_d, dy_d, dz_d
                if "size_x" in details and "size_y" in details and "size_z" in details:
                    sx_d, sy_d, sz_d = details.get("size_x"), details.get("size_y"), details.get("size_z")
                    if sx_d is not None and sy_d is not None and sz_d is not None:
                        logger.debug(f"AM_EXTRACT_DIM: Extracted from details['size_x/y/z'] for {resource_class.__name__}")
                        return sx_d, sy_d, sz_d

            if x is None and y is None and z is None:
                logger.debug(f"AM_EXTRACT_DIM: Dimensions not found through any known attributes or details for {resource_class.__name__}.")

        except Exception as e:
            logger.exception(f"AM_EXTRACT_DIM: Error extracting dimensions for {resource_class.__name__}: {e}")
        return x, y, z

    def _extract_volume(self, resource: Optional[PlrResource], resource_class: Type[PlrResource], details: Optional[Dict[str, Any]]) -> Optional[float]:
        """Extracts nominal volume in uL."""
        volume_value = None
        try:
            if resource:
                vol_attrs = ['capacity', 'max_volume', 'total_liquid_volume']
                for attr in vol_attrs:
                    if hasattr(resource, attr):
                        val = getattr(resource, attr)
                        if isinstance(val, (int, float)):
                            logger.debug(f"AM_EXTRACT_VOL: Extracted from '{attr}' for {resource_class.__name__}")
                            volume_value = float(val)
                            return volume_value
                if hasattr(resource, 'wells') and resource.wells and hasattr(resource.get_well(0), 'max_volume'): # type: ignore
                    well_vol = getattr(resource.get_well(0), 'max_volume', None) # type: ignore
                    if isinstance(well_vol, (int, float)):
                        logger.debug(f"AM_EXTRACT_VOL: Extracted from 'well.max_volume' for {resource_class.__name__}")
                        volume_value = float(well_vol)
                        return volume_value
            if details:
                detail_vol_attrs = ['capacity', 'max_volume', 'total_liquid_volume', 'nominal_volume_ul']
                for attr in detail_vol_attrs:
                    if attr in details and isinstance(details[attr], (int, float)):
                        logger.debug(f"AM_EXTRACT_VOL: Extracted from details['{attr}'] for {resource_class.__name__}")
                        volume_value = float(details[attr])
                        return volume_value

            if volume_value is None:
                logger.debug(f"AM_EXTRACT_VOL: Volume not found through any known attributes or details for {resource_class.__name__}.")

        except Exception as e:
            logger.exception(f"AM_EXTRACT_VOL: Error extracting volume for {resource_class.__name__}: {e}")
        return volume_value

    def _extract_model_name(self, resource: Optional[PlrResource], resource_class: Type[PlrResource], details: Optional[Dict[str, Any]]) -> Optional[str]:
        """Extracts model name."""
        model_value = None
        try:
            if resource and hasattr(resource, 'model') and resource.model:
                logger.debug(f"AM_EXTRACT_MODEL: Extracted from 'resource.model' for {resource_class.__name__}")
                model_value = str(resource.model)
                return model_value
            if details and "model" in details and details["model"]:
                logger.debug(f"AM_EXTRACT_MODEL: Extracted from details['model'] for {resource_class.__name__}")
                model_value = str(details["model"])
                return model_value

            if model_value is None:
                  logger.debug(f"AM_EXTRACT_MODEL: Model name not found through any known attributes or details for {resource_class.__name__}.")

        except Exception as e:
            logger.exception(f"AM_EXTRACT_MODEL: Error extracting model for {resource_class.__name__}: {e}")
        return model_value

    def _extract_num_items(self, resource: Optional[PlrResource], resource_class: Type[PlrResource], details: Optional[Dict[str, Any]]) -> Optional[int]:
        """Extracts the number of items (e.g., tips, wells, tubes)."""
        num_items_value = None
        try:
            if resource:
                if hasattr(resource, 'num_items') and isinstance(getattr(resource, 'num_items'), int):
                    logger.debug(f"AM_EXTRACT_NUM: Extracted from 'num_items' for {resource_class.__name__}")
                    num_items_value = int(getattr(resource, 'num_items'))
                    return num_items_value

            if details:
                if "num_items" in details and isinstance(details["num_items"], int):
                    logger.debug(f"AM_EXTRACT_NUM: Extracted from details['num_items'] for {resource_class.__name__}")
                    num_items_value = int(details["num_items"])
                    return num_items_value
                if "items" in details and isinstance(details["items"], list):
                    logger.debug(f"AM_EXTRACT_NUM: Extracted from len(details['items']) for {resource_class.__name__}")
                    num_items_value = len(details["items"])
                    return num_items_value
                if "wells" in details and isinstance(details["wells"], list):
                    logger.debug(f"AM_EXTRACT_NUM: Extracted from len(details['wells']) for {resource_class.__name__}")
                    num_items_value = len(details["wells"])
                    return num_items_value

            if num_items_value is None:
                logger.debug(f"AM_EXTRACT_NUM: Number of items not found through any known attributes or details for {resource_class.__name__}.")

        except Exception as e:
            logger.exception(f"AM_EXTRACT_NUM: Error extracting num_items for {resource_class.__name__}: {e}")
        return num_items_value

    def _extract_ordering(self, resource: Optional[PlrResource], resource_class: Type[PlrResource], details: Optional[Dict[str, Any]]) -> Optional[str]:
        """Extracts a comma-separated string of item names if ordered (e.g., wells in a plate)."""
        ordering_value = None
        try:
            if resource and isinstance(resource, ItemizedResource):
                if hasattr(resource, 'wells') and isinstance(getattr(resource, 'wells'), list):
                    wells_list = getattr(resource, 'wells')
                    well_names = [getattr(well, 'name', str(i)) for i, well in enumerate(wells_list)]
                    if well_names:
                        logger.debug(f"AM_EXTRACT_ORDER: Extracted from 'resource.wells' for {resource_class.__name__}")
                        ordering_value = ",".join(well_names)
                        return ordering_value
            if details:
                if "ordering" in details and isinstance(details["ordering"], str):
                    logger.debug(f"AM_EXTRACT_ORDER: Extracted from details['ordering'] for {resource_class.__name__}")
                    ordering_value = details["ordering"]
                    return ordering_value
                if "wells" in details and isinstance(details["wells"], list):
                    if all(isinstance(w, dict) and "name" in w for w in details["wells"]):
                        logger.debug(f"AM_EXTRACT_ORDER: Extracted from names in details['wells'] for {resource_class.__name__}")
                        ordering_value = ",".join([w["name"] for w in details["wells"]])
                        return ordering_value

            if ordering_value is None:
                logger.debug(f"AM_EXTRACT_ORDER: Ordering not found through any known attributes or details for {resource_class.__name__}.")

        except Exception as e:
            logger.exception(f"AM_EXTRACT_ORDER: Error extracting ordering for {resource_class.__name__}: {e}")
        return ordering_value

    def _get_category_from_plr_object(self, plr_object: PlrResource) -> str: # TODO: have it use resource.category
        """Determines string category from a PyLabRobot resource object."""
        match plr_object:
          case PlrPlate():
            return CATEGORY_PLATE
          case PlrTipRack():
            return CATEGORY_TIP_RACK
          case Lid():
            return CATEGORY_LID
          case PlrTrough():
            return CATEGORY_TROUGH
          case PlrTubeRack():
            return CATEGORY_TUBE_RACK
          case PlrPetriDish():
            return CATEGORY_PETRI_DISH
          case PlrTube():
            return CATEGORY_TUBE
          case Trash():
            return CATEGORY_WASTE
          case PlateCarrier() | TipCarrier() | PlateAdapter() | Carrier():
            return CATEGORY_CARRIER
          case PlrResource():
            return CATEGORY_OTHER
          case _:
            return CATEGORY_OTHER # TODO: decide how to handle exceptions
        return CATEGORY_OTHER

    def _get_category_from_class_name(self, class_name: str) -> str:
        """Infers string category from a class name string if object instance not available."""
        name_lower = class_name.lower()
        match name_lower.split('_'):
          case [*_, "carrier"]:
            return CATEGORY_CARRIER
          case [*_, "plate"]:
            return CATEGORY_PLATE
          case [*_, "tiprack"] | [*_, "tip", "rack"]:
            return CATEGORY_TIP_RACK
          case [*_, "lid"]:
            return CATEGORY_LID
          case [*_, "trough"]:
            return CATEGORY_TROUGH
          case [*_, "tuberack"] | [*_, "tube", "rack"]:
            return CATEGORY_TUBE_RACK
          case [*_, "trash"]:
            return CATEGORY_WASTE
          case [*_, "tube"]:
            return CATEGORY_TUBE
          case [*_, "petridish"] | [*_, "petri", "dish"]:
            return CATEGORY_PETRI_DISH
        return CATEGORY_OTHER

    def _is_catalogable_labware_class(self, plr_class: Type[Any]) -> bool:
        """
        Determines if a PyLabRobot class should be a primary, catalogable labware definition.
        """
        if not inspect.isclass(plr_class) or not issubclass(plr_class, PlrResource):
            return False
        if inspect.isabstract(plr_class):
            return False
        if plr_class in self.EXCLUDED_BASE_CLASSES:
            return False
        if plr_class.__name__ in self.EXCLUDED_CLASS_NAMES:
            return False
        if not plr_class.__module__.startswith("pylabrobot.resources"):
            return False
        return True

    def sync_pylabrobot_definitions(self, plr_resources_package=pylabrobot.resources) -> Tuple[int, int]:
        """
        Scans PyLabRobot's resources by introspecting modules and classes,
        then populates/updates the LabwareDefinitionCatalogOrm.
        """
        logger.info(f"AM_SYNC: Starting PyLabRobot labware definition sync from package: {plr_resources_package.__name__}")
        added_count = 0; updated_count = 0
        processed_fqns: Set[str] = set()

        for importer, modname, ispkg in pkgutil.walk_packages(
            path=plr_resources_package.__path__, # type: ignore
            prefix=plr_resources_package.__name__ + '.',
            onerror=lambda x: logger.error(f"AM_SYNC: Error walking package {x}")
        ):
            try:
                module = importlib.import_module(modname)
            except Exception as e:
                logger.warning(f"AM_SYNC: Could not import module {modname} during sync: {e}")
                continue

            for class_name, plr_class_obj in inspect.getmembers(module, inspect.isclass):
                fqn = f"{modname}.{class_name}"
                if fqn in processed_fqns: continue
                processed_fqns.add(fqn)

                logger.debug(f"AM_SYNC: Found class {fqn}. Checking if catalogable...")

                if not self._is_catalogable_labware_class(plr_class_obj):
                    logger.debug(f"AM_SYNC: Skipping {fqn} - not a catalogable labware class.")
                    continue

                logger.debug(f"AM_SYNC: Processing potential labware class: {fqn}")
                temp_instance: Optional[PlrResource] = None
                can_instantiate = True
                kwargs_for_instantiation: Dict[str, Any] = {"name": f"praxis_sync_temp_{class_name}"}

                try:
                    constructor_params = get_resource_constructor_params(plr_class_obj)
                    for param_name, param_info in constructor_params.items():
                        if param_name in ["self", "name"]: continue
                        if param_info["required"] and param_info["default"] is None:
                            param_type_str = param_info["type"].lower()
                            if "optional[" in param_type_str:
                              kwargs_for_instantiation[param_name] = None
                            elif "str" in param_type_str:
                              kwargs_for_instantiation[param_name] = ""
                            elif "int" in param_type_str:
                              kwargs_for_instantiation[param_name] = 0
                            elif "float" in param_type_str:
                              kwargs_for_instantiation[param_name] = 0.0
                            elif "bool" in param_type_str:
                              kwargs_for_instantiation[param_name] = False
                            elif "list" in param_type_str:
                              kwargs_for_instantiation[param_name] = []
                            elif "dict" in param_type_str:
                              kwargs_for_instantiation[param_name] = {}
                            else:
                                logger.info(f"AM_SYNC: Skipping instantiation for {fqn} due to complex required parameter '{param_name}' of type '{param_info['type']}'. Will rely on class-level data.")
                                can_instantiate = False
                                break
                    if can_instantiate:
                        logger.debug(f"AM_SYNC: Attempting instantiation of {fqn} with kwargs: {kwargs_for_instantiation}")
                        temp_instance = plr_class_obj(**kwargs_for_instantiation)
                except Exception as inst_err:
                    logger.warning(f"AM_SYNC: Instantiation of {fqn} failed even with smart defaults: {inst_err}. Proceeding with class-level data extraction.", exc_info=True)
                    temp_instance = None

                if not can_instantiate and temp_instance is None:
                      logger.info(f"AM_SYNC: Proceeding to extract data for {fqn} without a temporary instance (either skipped or failed instantiation).")

                details_json: Optional[Dict[str, Any]] = None
                if temp_instance and hasattr(temp_instance, 'serialize') and callable(temp_instance.serialize):
                    try:
                        details_json = temp_instance.serialize()
                        if 'name' in details_json: del details_json['name']
                    except Exception as ser_err: logger.warning(f"AM_SYNC: Serialize failed for {fqn}: {ser_err}")

                size_x, size_y, size_z = self._extract_dimensions(plr_class_obj, temp_instance, details_json)
                nominal_volume_ul = self._extract_volume(temp_instance, plr_class_obj, details_json)
                model_name = self._extract_model_name(temp_instance, plr_class_obj, details_json)
                num_items = self._extract_num_items(temp_instance, plr_class_obj, details_json)
                ordering_str = self._extract_ordering(temp_instance, plr_class_obj, details_json)

                if details_json is None:
                  details_json = {}
                if num_items is not None:
                  details_json["praxis_extracted_num_items"] = num_items
                if ordering_str is not None:
                  details_json["praxis_extracted_ordering"] = ordering_str

                try:
                    pylabrobot_def_name: Optional[str] = None
                    category: str
                    description: Optional[str]
                    is_consumable: bool = False
                    praxis_type_name: Optional[str] = model_name

                    if temp_instance:
                        if hasattr(temp_instance, 'category') and isinstance(temp_instance.category, str) and temp_instance.category:
                            pylabrobot_def_name = temp_instance.category
                        if not pylabrobot_def_name and model_name:
                          pylabrobot_def_name = model_name
                        if not praxis_type_name:
                          praxis_type_name = getattr(temp_instance, 'model', None) or plr_class_obj.__name__
                        category = self._get_category_from_plr_object(temp_instance)
                        description = inspect.getdoc(plr_class_obj) or temp_instance.name
                        is_consumable = category in CONSUMABLE_CATEGORIES
                    else:
                        if hasattr(plr_class_obj, 'resource_type') and isinstance(plr_class_obj.resource_type, str) and plr_class_obj.resource_type: # type: ignore
                            pylabrobot_def_name = plr_class_obj.resource_type # type: ignore
                        if not praxis_type_name: praxis_type_name = plr_class_obj.__name__
                        category = self._get_category_from_class_name(plr_class_obj.__name__)
                        description = inspect.getdoc(plr_class_obj)
                        is_consumable = category in CONSUMABLE_CATEGORIES

                    if not pylabrobot_def_name: pylabrobot_def_name = fqn
                    if not description: description = fqn

                    logger.debug(f"AM_SYNC: Syncing {pylabrobot_def_name} (FQN: {fqn}): Category={category}, Model={model_name}, Vol={nominal_volume_ul}, X={size_x}, Y={size_y}, Z={size_z}, NumItems={num_items}, Ordering={ordering_str[:50] if ordering_str else 'N/A'}...")

                    existing_def_orm = ads.get_labware_definition(self.db, pylabrobot_def_name)
                    ads.add_or_update_labware_definition(
                        db=self.db,
                        pylabrobot_definition_name=pylabrobot_def_name,
                        python_fqn=fqn,
                        praxis_labware_type_name=praxis_type_name,
                        description=description,
                        is_consumable=is_consumable,
                        nominal_volume_ul=nominal_volume_ul, # TODO: add material and manufacturer
                        plr_definition_details_json=details_json
                    )
                    if not existing_def_orm:
                      added_count += 1
                    else:
                      updated_count += 1
                except Exception as e_proc:
                    logger.exception(f"AM_SYNC: Could not process or save PLR class '{fqn}': {e_proc}")
                finally:
                    if temp_instance: del temp_instance

        logger.info(f"AM_SYNC: Labware definition sync complete. Added: {added_count}, Updated: {updated_count}")
        return added_count, updated_count

    def apply_deck_configuration(self, deck_identifier: Union[str, ProtocolPlrDeck], protocol_run_guid: str) -> PlrDeck:
        deck_name: str
        if isinstance(deck_identifier, ProtocolPlrDeck):
            deck_name = deck_identifier.name
        elif isinstance(deck_identifier, str):
            deck_name = deck_identifier
        else:
            raise TypeError(f"Unsupported deck_identifier type: {type(deck_identifier)}. Expected str or PlrDeck (protocol definition).")

        logger.info(f"AM_DECK_CONFIG: Applying deck configuration for '{deck_name}', run_guid: {protocol_run_guid}")

        deck_layout_orm = ads.get_deck_layout_by_name(self.db, deck_name)
        if not deck_layout_orm:
            raise AssetAcquisitionError(f"Deck layout '{deck_name}' not found in database.")

        deck_devices_orm = ads.list_managed_devices(
            self.db,
            pylabrobot_class_filter=PlrDeck.__name__,
        )
        if not deck_devices_orm:
            raise AssetAcquisitionError(f"No ManagedDevice found for deck '{deck_name}' with category DECK.")
        if len(deck_devices_orm) > 1: # pragma: no cover
            raise AssetAcquisitionError(f"Multiple ManagedDevices found for deck '{deck_name}' with category DECK. Ambiguous.")

        deck_device_orm = deck_devices_orm[0]

        if deck_device_orm.current_status == ManagedDeviceStatusEnum.IN_USE and \
          deck_device_orm.current_protocol_run_guid != protocol_run_guid:
            raise AssetAcquisitionError(f"Deck device '{deck_name}' (ID: {deck_device_orm.id}) is already in use by another run '{deck_device_orm.current_protocol_run_guid}'.")

        live_plr_deck_object = self.workcell_runtime.initialize_device_backend(deck_device_orm)
        if not live_plr_deck_object:
            raise AssetAcquisitionError(f"Failed to initialize backend for deck device '{deck_name}' (ID: {deck_device_orm.id}). Check WorkcellRuntime.")

        ads.update_managed_device_status(
            self.db,
            deck_device_orm.id,
            ManagedDeviceStatusEnum.IN_USE,
            current_protocol_run_guid=protocol_run_guid,
            status_details=f"Deck '{deck_name}' in use by run {protocol_run_guid}"
        )
        logger.info(f"AM_DECK_CONFIG: Deck device '{deck_name}' (ID: {deck_device_orm.id}) backend initialized and marked IN_USE.")

        deck_slots_orm = [] # ads.get_deck_slots_for_layout(self.db, deck_layout_orm.id) # TODO: implement this
        logger.info(f"AM_DECK_CONFIG: Found {len(deck_slots_orm)} slots for deck layout '{deck_name}'.")

        for slot_orm in deck_slots_orm:
            if slot_orm.pre_assigned_labware_instance_id:
                labware_instance_id = slot_orm.pre_assigned_labware_instance_id
                logger.info(f"AM_DECK_CONFIG: Slot '{slot_orm.slot_name}' has pre-assigned labware instance ID: {labware_instance_id}.")

                labware_instance_orm = ads.get_labware_instance_by_id(self.db, labware_instance_id)
                if not labware_instance_orm:
                    raise AssetAcquisitionError(f"Labware instance ID {labware_instance_id} for slot '{slot_orm.slot_name}' not found.")

                if labware_instance_orm.current_status not in [LabwareInstanceStatusEnum.AVAILABLE_IN_STORAGE, LabwareInstanceStatusEnum.AVAILABLE_ON_DECK]:
                    if labware_instance_orm.current_protocol_run_guid == protocol_run_guid and \
                      labware_instance_orm.location_device_id == deck_device_orm.id and \
                      labware_instance_orm.current_deck_slot_name == slot_orm.slot_name:
                        logger.warning(f"AM_DECK_CONFIG: Labware instance {labware_instance_id} in slot '{slot_orm.slot_name}' is already IN_USE by this run. Assuming already configured.")
                        continue
                    raise AssetAcquisitionError(
                      f"Labware instance ID {labware_instance_id} for slot '{slot_orm.slot_name}' is not available "
                      f"(status: {labware_instance_orm.current_status}, run: {labware_instance_orm.current_protocol_run_guid})."
                    )

                labware_def_orm = ads.get_labware_definition(self.db, labware_instance_orm.pylabrobot_definition_name)
                if not labware_def_orm or not labware_def_orm.python_fqn:
                    raise AssetAcquisitionError(f"Python FQN not found for labware definition '{labware_instance_orm.pylabrobot_definition_name}' (instance ID {labware_instance_id}).")

                live_plr_labware = self.workcell_runtime.create_or_get_labware_plr_object(
                    labware_instance_orm=labware_instance_orm,
                    labware_definition_fqn=labware_def_orm.python_fqn
                )
                if not live_plr_labware:
                    raise AssetAcquisitionError(f"Failed to create PLR object for labware instance ID {labware_instance_id} in slot '{slot_orm.slot_name}'.")

                logger.info(f"AM_DECK_CONFIG: Assigning labware '{live_plr_labware.name}' (Instance ID: {labware_instance_id}) to deck '{deck_name}' slot '{slot_orm.slot_name}'.")
                self.workcell_runtime.assign_labware_to_deck_slot(
                    deck_device_orm_id=deck_device_orm.id,
                    slot_name=slot_orm.slot_name,
                    labware_plr_object=live_plr_labware,
                    labware_instance_orm_id=labware_instance_id
                )
                ads.update_labware_instance_location_and_status(
                    db=self.db,
                    labware_instance_id=labware_instance_id,
                    new_status=LabwareInstanceStatusEnum.IN_USE,
                    current_protocol_run_guid=protocol_run_guid,
                    location_device_id=deck_device_orm.id,
                    current_deck_slot_name=slot_orm.slot_name,
                    #deck_slot_orm_id=slot_orm.id, # TODO: implement this or deprecate
                    status_details=f"On deck '{deck_name}' slot '{slot_orm.slot_name}' for run {protocol_run_guid}"
                )
                logger.info(f"AM_DECK_CONFIG: Labware instance ID {labware_instance_id} marked IN_USE on slot '{slot_orm.slot_name}'.")

        logger.info(f"AM_DECK_CONFIG: Deck configuration for '{deck_name}' applied successfully.")
        if not isinstance(live_plr_deck_object, PlrDeck):
            logger.warning(f"AM_DECK_CONFIG: WorkcellRuntime returned an object of type '{type(live_plr_deck_object)}' for deck, not PlrDeck. Ensure compatibility.")
        return live_plr_deck_object # type: ignore

    def acquire_device(self, protocol_run_guid: str, requested_asset_name_in_protocol: str, pylabrobot_class_name_constraint: str, constraints: Optional[Dict[str, Any]] = None) -> Tuple[Any, int, str]:
        logger.info(f"Acquiring device '{requested_asset_name_in_protocol}' (type constraint: '{pylabrobot_class_name_constraint}') for run '{protocol_run_guid}'. Constraints: {constraints}")
        device_orm_list = ads.list_managed_devices(
            self.db,
            status=ManagedDeviceStatusEnum.AVAILABLE,
            pylabrobot_class_filter=pylabrobot_class_name_constraint
        )
        selected_device_orm: Optional[ManagedDeviceOrm] = None
        if device_orm_list:
            selected_device_orm = device_orm_list[0]
        else:
            in_use_by_this_run_list = ads.list_managed_devices(
                self.db,
                pylabrobot_class_filter=pylabrobot_class_name_constraint,
                status=ManagedDeviceStatusEnum.IN_USE
            )
            if in_use_by_this_run_list:
                selected_device_orm = in_use_by_this_run_list[0]
                logger.info(f"Device '{selected_device_orm.user_friendly_name}' (ID: {selected_device_orm.id}) is already IN_USE by this run '{protocol_run_guid}'. Re-acquiring.")
            else:
                raise AssetAcquisitionError(f"No device found matching type constraint '{pylabrobot_class_name_constraint}' and status AVAILABLE, nor already in use by this run.")
        if not selected_device_orm:
              raise AssetAcquisitionError(f"Device selection failed for '{requested_asset_name_in_protocol}'.")
        logger.info(f"Attempting to initialize backend for selected device '{selected_device_orm.user_friendly_name}' (ID: {selected_device_orm.id}) via WorkcellRuntime.")
        live_plr_device = self.workcell_runtime.initialize_device_backend(selected_device_orm)
        if not live_plr_device:
            error_msg = f"Failed to initialize backend for device '{selected_device_orm.user_friendly_name}' (ID: {selected_device_orm.id}). Check WorkcellRuntime logs and device status in DB."
            logger.error(error_msg)
            raise AssetAcquisitionError(error_msg)
        logger.info(f"Backend for device '{selected_device_orm.user_friendly_name}' initialized. Marking as IN_USE for run '{protocol_run_guid}'.")
        updated_device_orm = ads.update_managed_device_status(
            self.db,
            selected_device_orm.id,
            ManagedDeviceStatusEnum.IN_USE,
            current_protocol_run_guid=protocol_run_guid,
            status_details=f"In use by run {protocol_run_guid}"
        )
        if not updated_device_orm:
            critical_error_msg = f"CRITICAL: Device '{selected_device_orm.user_friendly_name}' backend is live, but FAILED to update its DB status to IN_USE for run '{protocol_run_guid}'."
            logger.error(critical_error_msg)
            raise AssetAcquisitionError(critical_error_msg)
        logger.info(f"Device '{updated_device_orm.user_friendly_name}' (ID: {updated_device_orm.id}) successfully acquired and backend initialized for run '{protocol_run_guid}'.")
        return live_plr_device, selected_device_orm.id, "device"

    def acquire_labware(
        self,
        protocol_run_guid: str,
        requested_asset_name_in_protocol: str,
        pylabrobot_definition_name_constraint: str,
        user_choice_instance_id: Optional[int] = None,
        location_constraints: Optional[Dict[str, Any]] = None,
        property_constraints: Optional[Dict[str, Any]] = None
    ) -> Tuple[Any, int, str]:
        logger.info(f"AM_ACQUIRE: Acquiring labware '{requested_asset_name_in_protocol}' (definition name constraint: '{pylabrobot_definition_name_constraint}') for run '{protocol_run_guid}'.")
        if property_constraints:
            logger.info(f"AM_ACQUIRE: Labware acquisition for '{requested_asset_name_in_protocol}' includes property_constraints: {property_constraints}")

        labware_instance_to_acquire: Optional[LabwareInstanceOrm] = None
        if user_choice_instance_id:
            labware_instance_to_acquire = ads.get_labware_instance_by_id(self.db, user_choice_instance_id)
            if not labware_instance_to_acquire:
                 raise AssetAcquisitionError(f"Specified labware instance ID {user_choice_instance_id} not found.")
            if labware_instance_to_acquire.pylabrobot_definition_name != pylabrobot_definition_name_constraint:
                raise AssetAcquisitionError(f"Chosen labware instance ID {user_choice_instance_id} (Definition: '{labware_instance_to_acquire.pylabrobot_definition_name}') does not match definition constraint '{pylabrobot_definition_name_constraint}'.")
            if labware_instance_to_acquire.current_status == LabwareInstanceStatusEnum.IN_USE:
                if labware_instance_to_acquire.current_protocol_run_guid != protocol_run_guid:
                    raise AssetAcquisitionError(f"Chosen labware instance ID {user_choice_instance_id} is IN_USE by another run ('{labware_instance_to_acquire.current_protocol_run_guid}').")
                else:
                    logger.info(f"AM_ACQUIRE: Labware instance ID {user_choice_instance_id} is already IN_USE by this run '{protocol_run_guid}'. Re-acquiring.")
            elif labware_instance_to_acquire.current_status not in [LabwareInstanceStatusEnum.AVAILABLE_IN_STORAGE, LabwareInstanceStatusEnum.AVAILABLE_ON_DECK]:
                 raise AssetAcquisitionError(f"Chosen labware instance ID {user_choice_instance_id} is not available (status: {labware_instance_to_acquire.current_status.name if labware_instance_to_acquire.current_status else 'N/A'}).")
        else:
            in_use_by_this_run_list = ads.list_labware_instances(
                self.db,
                pylabrobot_definition_name=pylabrobot_definition_name_constraint,                status=LabwareInstanceStatusEnum.IN_USE
            )
            if in_use_by_this_run_list:
                labware_instance_to_acquire = in_use_by_this_run_list[0]
                logger.info(f"AM_ACQUIRE: Labware instance '{labware_instance_to_acquire.user_assigned_name}' (ID: {labware_instance_to_acquire.id}) is already IN_USE by this run '{protocol_run_guid}'. Re-acquiring.")
            else:
                lws_on_deck = ads.list_labware_instances(self.db, pylabrobot_definition_name=pylabrobot_definition_name_constraint, status=LabwareInstanceStatusEnum.AVAILABLE_ON_DECK)
                if lws_on_deck: labware_instance_to_acquire = lws_on_deck[0]
                else:
                    lws_in_storage = ads.list_labware_instances(self.db, pylabrobot_definition_name=pylabrobot_definition_name_constraint, status=LabwareInstanceStatusEnum.AVAILABLE_IN_STORAGE)
                    if lws_in_storage: labware_instance_to_acquire = lws_in_storage[0]
            if not labware_instance_to_acquire:
                raise AssetAcquisitionError(f"No labware found matching definition '{pylabrobot_definition_name_constraint}' that is available or already in use by this run.")
        if not labware_instance_to_acquire: # pragma: no cover
            raise AssetAcquisitionError(f"Labware matching criteria for '{requested_asset_name_in_protocol}' (Def: '{pylabrobot_definition_name_constraint}') not found or not available for run '{protocol_run_guid}'.")

        labware_def_orm = ads.get_labware_definition(self.db, labware_instance_to_acquire.pylabrobot_definition_name) # type: ignore
        if not labware_def_orm or not hasattr(labware_def_orm, 'python_fqn') or not labware_def_orm.python_fqn: # type: ignore
            error_msg = f"Python FQN not found for labware definition '{labware_instance_to_acquire.pylabrobot_definition_name}' for instance ID {labware_instance_to_acquire.id}." # type: ignore
            logger.error(error_msg)
            if ads:
                ads.update_labware_instance_location_and_status(
                    db=self.db, labware_instance_id=labware_instance_to_acquire.id, # type: ignore
                    new_status=LabwareInstanceStatusEnum.ERROR,
                    status_details=error_msg
                )
            raise AssetAcquisitionError(error_msg)
        labware_fqn = labware_def_orm.python_fqn # type: ignore

        logger.info(f"Attempting to create PLR object for labware instance '{labware_instance_to_acquire.user_assigned_name}' (ID: {labware_instance_to_acquire.id}) using FQN '{labware_fqn}'.") # type: ignore
        live_plr_labware = self.workcell_runtime.create_or_get_labware_plr_object(
            labware_instance_orm=labware_instance_to_acquire, # type: ignore
            labware_definition_fqn=labware_fqn
        )
        if not live_plr_labware:
            error_msg = f"Failed to create PLR object for labware '{labware_instance_to_acquire.user_assigned_name}' (ID: {labware_instance_to_acquire.id}). Check WorkcellRuntime logs." # type: ignore
            logger.error(error_msg)
            raise AssetAcquisitionError(error_msg)
        logger.info(f"PLR object for labware '{labware_instance_to_acquire.user_assigned_name}' created. Updating status to IN_USE.") # type: ignore

        target_deck_orm_id: Optional[int] = None
        target_slot_name: Optional[str] = None
        if location_constraints and isinstance(location_constraints, dict):
            deck_name = location_constraints.get("deck_name")
            slot_name = location_constraints.get("slot_name")
            if deck_name and slot_name:
                logger.info(f"Location constraint: place '{live_plr_labware.name}' on deck '{deck_name}' slot '{slot_name}'.")
                deck_device_list = ads.list_managed_devices(self.db, user_friendly_name_filter=deck_name, praxis_category_filter=PraxisDeviceCategoryEnum.DECK) # type: ignore
                if not deck_device_list:
                    raise AssetAcquisitionError(f"Deck '{deck_name}' specified in location_constraints not found.")
                deck_device_orm = deck_device_list[0]
                target_deck_orm_id = deck_device_orm.id
                target_slot_name = slot_name
                logger.debug(f"Assigning to Deck ID {target_deck_orm_id}, Slot {target_slot_name}")
                self.workcell_runtime.assign_labware_to_deck_slot(
                    deck_device_orm_id=target_deck_orm_id, # type: ignore
                    slot_name=target_slot_name, # type: ignore
                    labware_plr_object=live_plr_labware,
                    labware_instance_orm_id=labware_instance_to_acquire.id # type: ignore
                )
            elif deck_name or slot_name:
                raise AssetAcquisitionError(f"Partial location constraint for '{requested_asset_name_in_protocol}'. Both 'deck_name' and 'slot_name' required if placing on deck.")

        updated_labware_instance_orm = ads.update_labware_instance_location_and_status(
            self.db,
            labware_instance_id=labware_instance_to_acquire.id, # type: ignore
            new_status=LabwareInstanceStatusEnum.IN_USE,
            current_protocol_run_guid=protocol_run_guid,
            status_details=f"In use by run {protocol_run_guid}",
        )
        if not updated_labware_instance_orm:
            critical_error_msg = f"CRITICAL: Labware '{labware_instance_to_acquire.user_assigned_name}' PLR object created/assigned, but FAILED to update its DB status to IN_USE for run '{protocol_run_guid}'." # type: ignore
            logger.error(critical_error_msg)
            raise AssetAcquisitionError(critical_error_msg)
        logger.info(f"Labware '{updated_labware_instance_orm.user_assigned_name}' (ID: {updated_labware_instance_orm.id}) successfully acquired for run '{protocol_run_guid}'.") # type: ignore
        return live_plr_labware, labware_instance_to_acquire.id, "labware" # type: ignore

    def release_device(
        self,
        device_orm_id: int,
        final_status: ManagedDeviceStatusEnum = ManagedDeviceStatusEnum.AVAILABLE,
        status_details: Optional[str] = "Released from run"
    ):
        logger.info(f"Releasing device ID {device_orm_id}. Target status: {final_status.name if final_status else 'N/A'}.")
        if self.workcell_runtime:
            logger.info(f"Calling WorkcellRuntime to shut down backend for device ID {device_orm_id}.")
            self.workcell_runtime.shutdown_device_backend(device_orm_id)
            if ads:
                device_after_wcr_shutdown = ads.get_managed_device_by_id(self.db, device_orm_id)
                if device_after_wcr_shutdown and device_after_wcr_shutdown.current_status != final_status:
                     logger.info(f"WorkcellRuntime set device {device_orm_id} to {device_after_wcr_shutdown.current_status}, but final desired status is {final_status}. Updating.")
                     ads.update_managed_device_status(
                        self.db,
                        device_orm_id,
                        final_status,
                        status_details=status_details,
                        current_protocol_run_guid=None
                    )
                elif not device_after_wcr_shutdown:
                     logger.error(f"Device ID {device_orm_id} not found after WorkcellRuntime shutdown attempt.")
        else:
            logger.warning(f"WorkcellRuntime not available. Attempting direct DB status update for device ID {device_orm_id}.")
            if ads:
                updated_device = ads.update_managed_device_status(
                    self.db,
                    device_orm_id,
                    final_status,
                    status_details=status_details,
                    current_protocol_run_guid=None
                )
                if not updated_device:
                    logger.error(f"Failed to update status for device ID {device_orm_id} directly in DB.")
        logger.info(f"Device ID {device_orm_id} release process initiated.")

    def release_labware(
        self,
        labware_instance_orm_id: int,
        final_status: LabwareInstanceStatusEnum,
        final_properties_json_update: Optional[Dict[str, Any]] = None,
        clear_from_deck_device_id: Optional[int] = None,
        clear_from_slot_name: Optional[str] = None,
        status_details: Optional[str] = "Released from run"
    ):
        logger.info(f"AM_RELEASE: Releasing labware ID {labware_instance_orm_id}. Target status: {final_status.name}. Details: {status_details}")
        if final_properties_json_update is not None:
            logger.info(f"AM_RELEASE: Labware release for instance ID {labware_instance_orm_id} includes final_properties_json_update: {final_properties_json_update}")

        final_location_device_id_for_ads: Optional[int] = None
        final_deck_slot_name_for_ads: Optional[str] = None
        if clear_from_deck_device_id is not None and clear_from_slot_name is not None:
            if self.workcell_runtime:
                logger.info(f"Calling WorkcellRuntime to clear labware ID {labware_instance_orm_id} from deck ID {clear_from_deck_device_id}, slot '{clear_from_slot_name}'.")
                self.workcell_runtime.clear_deck_slot(
                    deck_device_orm_id=clear_from_deck_device_id,
                    slot_name=clear_from_slot_name,
                    labware_instance_orm_id=labware_instance_orm_id
                )
            else: # pragma: no cover
                logger.warning(f"WorkcellRuntime not available. Cannot clear labware ID {labware_instance_orm_id} from deck. Manual DB update for status only.")
        logger.info(f"Updating final status and details for labware ID {labware_instance_orm_id} in DB.")
        if ads:
            updated_labware = ads.update_labware_instance_location_and_status(
                self.db,
                labware_instance_id=labware_instance_orm_id,
                new_status=final_status,
                properties_json_update=final_properties_json_update,
                location_device_id=final_location_device_id_for_ads,
                current_deck_slot_name=final_deck_slot_name_for_ads,
                current_protocol_run_guid=None,
                status_details=status_details
            )
            if not updated_labware:
                logger.error(f"Failed to update final status for labware ID {labware_instance_orm_id} in DB.")
        logger.info(f"Labware ID {labware_instance_orm_id} release process initiated.")

    def acquire_asset(self, protocol_run_guid: str, asset_requirement: AssetRequirementModel) -> Tuple[Any, int, str]:
        logger.info(f"AM_ACQUIRE_DISPATCH: AssetManager attempting to acquire asset '{asset_requirement.name}' "
              f"of type '{asset_requirement.actual_type_str}' for run '{protocol_run_guid}'. "
              f"Constraints: {asset_requirement.constraints_json}")
        constraints_for_device = asset_requirement.constraints_json if asset_requirement.constraints_json else {}
        properties_for_labware = asset_requirement.constraints_json if asset_requirement.constraints_json else {}
        labware_def_check = ads.get_labware_definition(self.db, asset_requirement.actual_type_str)
        if labware_def_check:
            logger.debug(f"AM_ACQUIRE_DISPATCH: Identified '{asset_requirement.actual_type_str}' as LABWARE. Dispatching to acquire_labware for {asset_requirement.name}")
            return self.acquire_labware(
                protocol_run_guid=protocol_run_guid,
                requested_asset_name_in_protocol=asset_requirement.name,
                pylabrobot_definition_name_constraint=asset_requirement.actual_type_str,
                property_constraints=properties_for_labware
            )
        else:
            logger.debug(f"AM_ACQUIRE_DISPATCH: Identified '{asset_requirement.actual_type_str}' as DEVICE (FQN). Dispatching to acquire_device for {asset_requirement.name}")
            return self.acquire_device(
                protocol_run_guid=protocol_run_guid,
                requested_asset_name_in_protocol=asset_requirement.name,
                pylabrobot_class_name_constraint=asset_requirement.actual_type_str,
                constraints=constraints_for_device
            )
