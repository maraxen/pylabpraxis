# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-locals, too-many-branches, too-many-statements
"""
praxis/core/asset_manager.py

The AssetManager is responsible for managing the lifecycle and allocation
of physical laboratory assets (devices and labware instances). It interacts
with the AssetDataService for persistence and the WorkcellRuntime for
live PyLabRobot object interactions.

Version 6: Further refines sync_pylabrobot_definitions based on detailed
           PLR structure and "PLR Inspection Utility" document.
           Removes ResourceLoader, correctly handles Deck, Coordinate, Well, Tip.
"""
from typing import Dict, Any, Optional, List, Type, Tuple, Set
import importlib
import inspect
import traceback
import os
import pkgutil
import sys # ADDED

from sqlalchemy.orm import Session as DbSession

# Data services
try:
    from praxis.backend.services import asset_data_service as ads # CORRECTED PATH
except ImportError:
    print("WARNING: AM-1: Could not import asset_data_service. AssetManager DB ops placeholder.")
    class PlaceholderAssetDataService: # Copied from file for completeness
        def get_labware_definition(self, db, name): return None
        def add_or_update_labware_definition(self, db, **kw): class D: pass; return D() # type: ignore
        def list_managed_devices(self, *args, **kwargs): return [] # type: ignore
        def update_managed_device_status(self, *args, **kwargs): return None # type: ignore
        def list_labware_instances(self, *args, **kwargs): return [] # type: ignore
        def get_labware_instance_by_id(self, *args, **kwargs): return None # type: ignore
        def update_labware_instance_location_and_status(self, *args, **kwargs): return None # type: ignore
    ads = PlaceholderAssetDataService() # type: ignore

# ORM Models
try:
    from praxis.database_models.asset_management_orm import (
        ManagedDeviceOrm, LabwareInstanceOrm, LabwareDefinitionCatalogOrm,
        ManagedDeviceStatusEnum, LabwareInstanceStatusEnum, LabwareCategoryEnum, # Keep LabwareCategoryEnum if still used by _get_category_from_plr_object
        PraxisDeviceCategoryEnum # ADDED for deck filtering
    )
except ImportError:
    print("WARNING: AM-2: Could not import Asset ORM models.")
    class ManagedDeviceOrm: id: int; user_friendly_name: str; pylabrobot_class_name: str; current_status: Any; current_protocol_run_guid: Optional[str] # type: ignore
    class LabwareInstanceOrm: id: int; user_assigned_name: str; pylabrobot_definition_name: str; current_status: Any; current_protocol_run_guid: Optional[str]; location_device_id: Optional[int]; current_deck_slot_name: Optional[str] # type: ignore
    class LabwareDefinitionCatalogOrm: pylabrobot_definition_name: str; python_fqn: str # Added python_fqn for type hint
    class ManagedDeviceStatusEnum(enum.Enum): AVAILABLE="available"; IN_USE="in_use"; ERROR="error"; OFFLINE="offline" # type: ignore # type: ignore
    class LabwareInstanceStatusEnum(enum.Enum): AVAILABLE_ON_DECK="available_on_DECK"; AVAILABLE_IN_STORAGE="available_in_storage"; IN_USE="in_use"; EMPTY="empty"; UNKNOWN="unknown" # type: ignore # type: ignore
    class LabwareCategoryEnum(enum.Enum): PLATE="plate"; TIP_RACK="tip_rack"; RESERVOIR="reservoir"; TUBE_RACK="tube_rack"; CARRIER="carrier"; LID="lid"; WASTE="waste"; TUBE="tube"; OTHER="other"; DECK="deck" # type: ignore # type: ignore
    class PraxisDeviceCategoryEnum(enum.Enum): DECK="Deck" # ADDED for deck filtering
    import enum # Make sure enum is imported if placeholders are used

# Praxis Protocol Core Models
from praxis.backend.protocol_core.protocol_definition_models import AssetRequirementModel

# PyLabRobot imports
try:
    import pylabrobot.resources
    from pylabrobot.resources import (
        Resource as PlrResource, Lid, Carrier, Deck as PlrDeck, Well, Container, Coordinate,
        PlateCarrier, TipCarrier, Trash, ItemizedResource, PlateAdapter,
        TIP_RACK_RESOURCE_TYPE, PLATE_RESOURCE_TYPE, LID_RESOURCE_TYPE,
    )
    from pylabrobot.resources.plate import Plate as PlrPlate
    from pylabrobot.resources.tip_rack import TipRack as PlrTipRack
    from pylabrobot.resources.tube_rack import TubeRack as PlrTubeRack
    from pylabrobot.resources.tube import Tube as PlrTube
    from pylabrobot.resources.tip import Tip as PlrTip
    from pylabrobot.resources.petri_dish import PetriDish as PlrPetriDish
    # from pylabrobot.resources.opentrons.load import load_labware as ot_load_labware # AM-5E
    from pylabrobot.liquid_handling.backends.backend import LiquidHandlerBackend
    from praxis.backend.utils.plr_inspection import get_resource_constructor_params # ADDED
except ImportError:
    print("WARNING: AM-3: PyLabRobot not found/fully importable.")
    def get_resource_constructor_params(resource_class: Type[Any]) -> Dict[str, Dict]: return {} # Placeholder if import fails
    # Define placeholders (condensed)
    class PlrResource: name: str; resource_type: Optional[str]; parent: Any; children: List[Any]; model: Optional[str]; def serialize(self): return {}; def __init__(self, name, **kwargs): self.name=name # type: ignore
    class PlrPlate(PlrResource): pass; class PlrTipRack(PlrResource): pass; class PlrTubeRack(PlrResource): pass
    class PlrReservoir(PlrResource): pass; class Lid(PlrResource): pass; class Carrier(PlrResource): pass
    class PlrDeck(PlrResource): pass; class Well(PlrResource): pass; class Container(PlrResource): pass
    class Coordinate: pass; class PlateCarrier(Carrier): pass; class TipCarrier(Carrier): pass
    class Trash(PlrResource): pass; class ItemizedResource(PlrResource): pass; class PlateAdapter(Carrier): pass
    class PlrTube(Container): pass; class PlrTip(Container): pass; class PlrPetriDish(Container): pass
    TIP_RACK_RESOURCE_TYPE = "tip_rack"; PLATE_RESOURCE_TYPE = "plate"; LID_RESOURCE_TYPE = "lid"
    class LiquidHandlerBackend: pass # type: ignore


# Placeholder for WorkcellRuntime
class WorkcellRuntimePlaceholder: # (Same as v1)
    def get_plr_device_backend(self, device_orm: ManagedDeviceOrm) -> Optional[Any]: return None
    def get_plr_labware_object(self, labware_instance_orm: LabwareInstanceOrm) -> Optional[PlrResource]: return None
    def assign_labware_to_deck_slot(self, deck_plr_obj: Any, slot_name: str, labware_plr_obj: PlrResource): pass
    def clear_deck_slot(self, deck_plr_obj: Any, slot_name: str): pass

class AssetAcquisitionError(RuntimeError): pass

class AssetManager:
    def __init__(self, db_session: DbSession, workcell_runtime: Optional[WorkcellRuntimePlaceholder] = None):
        self.db: DbSession = db_session
        self.workcell_runtime = workcell_runtime if workcell_runtime else WorkcellRuntimePlaceholder()

        # Classes to explicitly exclude from labware catalog (bases, utilities, components)
        # Based on "PLR Inspection Utility" document and common sense.
        self.EXCLUDED_BASE_CLASSES: List[Type[PlrResource]] = [
            PlrResource, Container, ItemizedResource, Well, PlrTip, Coordinate,
            PlrDeck # Decks are ManagedDevices, not labware definitions for placement.
        ]
        # Names of classes that are known to be utility/creators
        self.EXCLUDED_CLASS_NAMES: Set[str] = {"WellCreator", "TipCreator", "CarrierSite", "ResourceStack"}

    def _extract_dimensions(self, resource: Optional[PlrResource], resource_class: Type[PlrResource], details: Optional[Dict[str, Any]]) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Extracts dimensions (x, y, z) in mm."""
        try:
            if resource:
                if hasattr(resource, 'get_size_x') and callable(resource.get_size_x): # type: ignore
                    return resource.get_size_x(), resource.get_size_y(), resource.get_size_z() # type: ignore
                if hasattr(resource, 'dimensions') and isinstance(resource.dimensions, Coordinate): # type: ignore
                    return resource.dimensions.x, resource.dimensions.y, resource.dimensions.z # type: ignore
            if details:
                if "dimensions" in details and isinstance(details["dimensions"], dict):
                    return details["dimensions"].get("x"), details["dimensions"].get("y"), details["dimensions"].get("z")
                if "size_x" in details and "size_y" in details and "size_z" in details:
                    return details.get("size_x"), details.get("size_y"), details.get("size_z")
        except Exception as e:
            print(f"DEBUG: AM_EXTRACT_DIM_ERR: Error extracting dimensions for {resource_class.__name__}: {e}")
        return None, None, None

    def _extract_volume(self, resource: Optional[PlrResource], resource_class: Type[PlrResource], details: Optional[Dict[str, Any]]) -> Optional[float]:
        """Extracts nominal volume in uL."""
        try:
            if resource:
                if hasattr(resource, 'capacity') and resource.capacity is not None: return float(resource.capacity) # type: ignore
                if hasattr(resource, 'max_volume') and resource.max_volume is not None: return float(resource.max_volume) # type: ignore
                if hasattr(resource, 'wells') and resource.wells and hasattr(resource.get_well(0), 'max_volume'): # type: ignore
                    return float(resource.get_well(0).max_volume) # type: ignore
            if details:
                if "capacity" in details and details["capacity"] is not None: return float(details["capacity"])
                if "max_volume" in details and details["max_volume"] is not None: return float(details["max_volume"])
                if "nominal_volume_ul" in details and details["nominal_volume_ul"] is not None: return float(details["nominal_volume_ul"])
        except Exception as e:
            print(f"DEBUG: AM_EXTRACT_VOL_ERR: Error extracting volume for {resource_class.__name__}: {e}")
        return None

    def _extract_model_name(self, resource: Optional[PlrResource], resource_class: Type[PlrResource], details: Optional[Dict[str, Any]]) -> Optional[str]:
        """Extracts model name."""
        try:
            if resource and hasattr(resource, 'model') and resource.model: return str(resource.model) # type: ignore
            if details and "model" in details and details["model"]: return str(details["model"])
        except Exception as e:
            print(f"DEBUG: AM_EXTRACT_MODEL_ERR: Error extracting model for {resource_class.__name__}: {e}")
        return None

    def _get_category_from_plr_object(self, plr_object: PlrResource) -> LabwareCategoryEnum:
        """Determines LabwareCategoryEnum from a PyLabRobot resource object."""
        # Order matters: more specific types first
        if isinstance(plr_object, PlrPlate): return LabwareCategoryEnum.PLATE
        if isinstance(plr_object, PlrTipRack): return LabwareCategoryEnum.TIP_RACK
        if isinstance(plr_object, Lid): return LabwareCategoryEnum.LID
        if isinstance(plr_object, PlrReservoir): return LabwareCategoryEnum.RESERVOIR
        if isinstance(plr_object, PlrTubeRack): return LabwareCategoryEnum.TUBE_RACK
        if isinstance(plr_object, PlrPetriDish): return LabwareCategoryEnum.PLATE # Often treated like plates
        if isinstance(plr_object, PlrTube): return LabwareCategoryEnum.TUBE # Standalone tube or tube in rack
        if isinstance(plr_object, Trash): return LabwareCategoryEnum.WASTE
        if isinstance(plr_object, (PlateCarrier, TipCarrier, PlateAdapter, Carrier)): return LabwareCategoryEnum.CARRIER
        # If it's a Container but not caught above, it's likely a generic or custom one
        if isinstance(plr_object, Container): return LabwareCategoryEnum.OTHER # Or RESERVOIR if appropriate
        return LabwareCategoryEnum.OTHER

    def _get_category_from_class_name(self, class_name: str) -> LabwareCategoryEnum:
        """Infers LabwareCategoryEnum from a class name string if object instance not available."""
        name_lower = class_name.lower()
        if "plate" in name_lower: return LabwareCategoryEnum.PLATE
        if "tiprack" in name_lower or "tip_rack" in name_lower: return LabwareCategoryEnum.TIP_RACK
        if "lid" in name_lower: return LabwareCategoryEnum.LID
        if "reservoir" in name_lower: return LabwareCategoryEnum.RESERVOIR
        if "tuberack" in name_lower or "tube_rack" in name_lower: return LabwareCategoryEnum.TUBE_RACK
        if "trash" in name_lower: return LabwareCategoryEnum.WASTE
        if "carrier" in name_lower: return LabwareCategoryEnum.CARRIER
        if "tube" in name_lower: return LabwareCategoryEnum.TUBE # Must be after tuberack
        return LabwareCategoryEnum.OTHER

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

        # Module check: ensure it's from a 'resources' submodule, not e.g. 'backends'
        # This is a heuristic; PLR's structure is generally good but could have exceptions.
        if not plr_class.__module__.startswith("pylabrobot.resources"):
            # Allow exceptions for known community/extension paths if configured
            # TODO: AM-5C: Make additional scan paths/module prefixes configurable.
            # print(f"DEBUG: Skipping {plr_class.__module__}.{plr_class.__name__} due to module path.")
            return False # For now, strict to pylabrobot.resources

        return True

    def sync_pylabrobot_definitions(self, plr_resources_package=pylabrobot.resources) -> Tuple[int, int]:
        """
        Scans PyLabRobot's resources by introspecting modules and classes,
        then populates/updates the LabwareDefinitionCatalogOrm.
        """
        print(f"INFO: Starting PyLabRobot labware definition sync from package: {plr_resources_package.__name__}")
        added_count = 0; updated_count = 0
        processed_fqns: Set[str] = set()

        for importer, modname, ispkg in pkgutil.walk_packages(
            path=plr_resources_package.__path__, # type: ignore
            prefix=plr_resources_package.__name__ + '.',
            onerror=lambda x: print(f"Error walking package: {x}") # Log errors during walk
        ):
            try:
                module = importlib.import_module(modname)
            except Exception as e:
                print(f"WARNING: Could not import module {modname} during sync: {e}")
                continue

            for class_name, plr_class_obj in inspect.getmembers(module, inspect.isclass):
                fqn = f"{modname}.{class_name}"
                if fqn in processed_fqns: continue
                processed_fqns.add(fqn)

                if not self._is_catalogable_labware_class(plr_class_obj):
                    continue

                # print(f"DEBUG: Processing potential labware class: {fqn}")
                temp_instance: Optional[PlrResource] = None
                can_instantiate = True
                kwargs_for_instantiation: Dict[str, Any] = {"name": f"praxis_sync_temp_{class_name}"}

                try:
                    constructor_params = get_resource_constructor_params(plr_class_obj)
                    for param_name, param_info in constructor_params.items():
                        if param_name in ["self", "name"]: continue
                        if param_info["required"] and param_info["default"] is None: # Simplified check for no default
                            param_type_str = param_info["type"].lower()
                            if "optional[" in param_type_str: # Handle Optional[type]
                                kwargs_for_instantiation[param_name] = None
                            elif "str" in param_type_str: kwargs_for_instantiation[param_name] = ""
                            elif "int" in param_type_str: kwargs_for_instantiation[param_name] = 0
                            elif "float" in param_type_str: kwargs_for_instantiation[param_name] = 0.0
                            elif "bool" in param_type_str: kwargs_for_instantiation[param_name] = False
                            elif "list" in param_type_str: kwargs_for_instantiation[param_name] = []
                            elif "dict" in param_type_str: kwargs_for_instantiation[param_name] = {}
                            else: # Complex/unknown type
                                print(f"INFO: Skipping instantiation for {fqn} due to complex required parameter '{param_name}' of type '{param_info['type']}'. Will rely on class-level data.")
                                can_instantiate = False
                                break
                    
                    if can_instantiate:
                        print(f"DEBUG: Attempting instantiation of {fqn} with kwargs: {kwargs_for_instantiation}")
                        temp_instance = plr_class_obj(**kwargs_for_instantiation)
                except Exception as inst_err:
                    print(f"WARNING: Instantiation of {fqn} failed even with smart defaults: {inst_err}. Proceeding with class-level data extraction.")
                    temp_instance = None
                
                if not can_instantiate and temp_instance is None: # Double check if loop was broken
                     print(f"INFO: Skipped instantiation for {fqn} due to complex/missing required parameters. Relying on class-level data.")
                     # temp_instance is already None

                # Property Extraction
                details_json: Optional[Dict[str, Any]] = None
                if temp_instance and hasattr(temp_instance, 'serialize') and callable(temp_instance.serialize):
                    try:
                        details_json = temp_instance.serialize()
                        if 'name' in details_json: del details_json['name'] 
                    except Exception as ser_err: print(f"WARN: Serialize failed for {fqn}: {ser_err}")

                size_x, size_y, size_z = self._extract_dimensions(temp_instance, plr_class_obj, details_json)
                nominal_volume_ul = self._extract_volume(temp_instance, plr_class_obj, details_json)
                model_name = self._extract_model_name(temp_instance, plr_class_obj, details_json)

                try:
                    pylabrobot_def_name: Optional[str] = None
                    category: LabwareCategoryEnum
                    description: Optional[str]
                    is_consumable: bool = False # Default
                    praxis_type_name: Optional[str] = model_name # Use extracted model name first

                    if temp_instance:
                        if hasattr(temp_instance, 'resource_type') and isinstance(temp_instance.resource_type, str) and temp_instance.resource_type:
                            pylabrobot_def_name = temp_instance.resource_type
                        
                        if not pylabrobot_def_name and model_name:
                             pylabrobot_def_name = model_name

                        if not praxis_type_name: # Fallback if model_name was None
                            praxis_type_name = getattr(temp_instance, 'model', None) or plr_class_obj.__name__

                        category = self._get_category_from_plr_object(temp_instance)
                        description = inspect.getdoc(plr_class_obj) or temp_instance.name
                        is_consumable = category in [LabwareCategoryEnum.PLATE, LabwareCategoryEnum.TIP_RACK, LabwareCategoryEnum.RESERVOIR, LabwareCategoryEnum.LID, LabwareCategoryEnum.TUBE]
                    else: # Class-level data fallback
                        if hasattr(plr_class_obj, 'resource_type') and isinstance(plr_class_obj.resource_type, str) and plr_class_obj.resource_type: # type: ignore
                            pylabrobot_def_name = plr_class_obj.resource_type # type: ignore
                        
                        if not praxis_type_name: # Fallback if model_name was None (likely for class-level)
                             praxis_type_name = plr_class_obj.__name__

                        category = self._get_category_from_class_name(plr_class_obj.__name__)
                        description = inspect.getdoc(plr_class_obj)
                        is_consumable = category in [LabwareCategoryEnum.PLATE, LabwareCategoryEnum.TIP_RACK, LabwareCategoryEnum.RESERVOIR, LabwareCategoryEnum.LID, LabwareCategoryEnum.TUBE]
                    
                    if not pylabrobot_def_name: # Final fallback for def_name
                        pylabrobot_def_name = fqn
                    if not description: description = fqn # Ensure description is not empty

                    print(f"DEBUG: Syncing {pylabrobot_def_name} (FQN: {fqn}): Category={category.name}, Model={model_name}, Vol={nominal_volume_ul}, X={size_x}, Y={size_y}, Z={size_z}")

                    existing_def_orm = ads.get_labware_definition(self.db, pylabrobot_def_name)
                    ads.add_or_update_labware_definition(
                        db=self.db, 
                        pylabrobot_definition_name=pylabrobot_def_name,
                        python_fqn=fqn,
                        praxis_labware_type_name=praxis_type_name, 
                        category=category,
                        description=description,
                        is_consumable=is_consumable, 
                        nominal_volume_ul=nominal_volume_ul,
                        size_x_mm=size_x, 
                        size_y_mm=size_y, 
                        size_z_mm=size_z,
                        model=model_name,
                        plr_definition_details_json=details_json
                    )
                    if not existing_def_orm: added_count += 1
                    else: updated_count += 1
                except Exception as e_proc:
                    print(f"ERROR: Could not process or save PLR class '{fqn}': {e_proc}\n{traceback.format_exc()}")
                finally:
                    if temp_instance: del temp_instance

        # TODO: AM-5E: Add step for loading definitions from external files (e.g., Opentrons JSON).
        print(f"Labware definition sync complete. Added: {added_count}, Updated: {updated_count}")
        return added_count, updated_count

    # --- acquire/release methods (structurally same as v4, with existing TODOs) ---
    # (Condensed for brevity, full logic from v4 should be retained)
    def acquire_device(self, protocol_run_guid: str, requested_asset_name_in_protocol: str, pylabrobot_class_name_constraint: str, constraints: Optional[Dict[str, Any]] = None) -> Tuple[Any, int, str]: # MODIFIED return type
        print(f"INFO: Acquiring device '{requested_asset_name_in_protocol}' (type constraint: '{pylabrobot_class_name_constraint}') for run '{protocol_run_guid}'. Constraints: {constraints}")
        
        # TODO: AM-6: Implement more sophisticated constraint-based selection from device_orm_list.
        # TODO: AM-7: Consider locking mechanism for selection if multiple orchestrators/threads.
        device_orm_list = ads.list_managed_devices(
            self.db, 
            status=ManagedDeviceStatusEnum.AVAILABLE, 
            pylabrobot_class_filter=pylabrobot_class_name_constraint
        )

        if not device_orm_list:
            raise AssetAcquisitionError(f"No device found matching type constraint '{pylabrobot_class_name_constraint}' and status AVAILABLE.")

        selected_device_orm = device_orm_list[0] # Basic selection: first available

        print(f"INFO: Attempting to initialize backend for selected device '{selected_device_orm.user_friendly_name}' (ID: {selected_device_orm.id}) via WorkcellRuntime.")
        # TODO: AM-4: Ensure workcell_runtime is the actual WorkcellRuntime, not placeholder.
        live_plr_device = self.workcell_runtime.initialize_device_backend(selected_device_orm)

        if not live_plr_device:
            # initialize_device_backend in WorkcellRuntime should have set the device status to ERROR in DB.
            error_msg = f"Failed to initialize backend for device '{selected_device_orm.user_friendly_name}' (ID: {selected_device_orm.id}). Check WorkcellRuntime logs and device status in DB."
            print(f"ERROR: {error_msg}")
            raise AssetAcquisitionError(error_msg)

        # Backend initialized successfully, now mark as IN_USE for this run
        print(f"INFO: Backend for device '{selected_device_orm.user_friendly_name}' initialized. Marking as IN_USE for run '{protocol_run_guid}'.")
        updated_device_orm = ads.update_managed_device_status(
            self.db, 
            selected_device_orm.id, 
            ManagedDeviceStatusEnum.IN_USE, 
            current_protocol_run_guid=protocol_run_guid,
            status_details=f"In use by run {protocol_run_guid}" # Optional detail
        )

        if not updated_device_orm: # Should ideally not happen if selected_device_orm.id is valid
            # This is a problematic state: backend is live, but DB status update failed.
            # Attempt to revert by shutting down the backend? Or just raise a critical error.
            critical_error_msg = f"CRITICAL: Device '{selected_device_orm.user_friendly_name}' backend is live, but FAILED to update its DB status to IN_USE for run '{protocol_run_guid}'."
            print(f"ERROR: {critical_error_msg}")
            # Consider trying to shut down the backend to prevent orphaned live asset
            # self.workcell_runtime.shutdown_device_backend(selected_device_orm.id)
            raise AssetAcquisitionError(critical_error_msg) # Let caller know something is wrong

        print(f"INFO: Device '{updated_device_orm.user_friendly_name}' (ID: {updated_device_orm.id}) successfully acquired and backend initialized for run '{protocol_run_guid}'.")
        return live_plr_device, selected_device_orm.id, "device" # MODIFIED return value

    def acquire_labware(
        self, 
        protocol_run_guid: str, 
        requested_asset_name_in_protocol: str, 
        pylabrobot_definition_name_constraint: str, # This is the resource name like "corning_96_wellplate_360ul_flat"
        user_choice_instance_id: Optional[int] = None, 
        location_constraints: Optional[Dict[str, Any]] = None, # e.g., {"deck_name": "main_deck", "slot_name": "A1"}
        property_constraints: Optional[Dict[str, Any]] = None
    ) -> Tuple[Any, int, str]: # MODIFIED return type

        print(f"INFO: Acquiring labware '{requested_asset_name_in_protocol}' (definition name constraint: '{pylabrobot_definition_name_constraint}') for run '{protocol_run_guid}'.")
        # TODO: AM-10: Implement user_choice_instance_id, location_constraints, property_constraints in selection logic.

        labware_instance_to_acquire: Optional[LabwareInstanceOrm] = None
        if user_choice_instance_id:
            labware_instance_to_acquire = ads.get_labware_instance_by_id(self.db, user_choice_instance_id)
            if labware_instance_to_acquire and labware_instance_to_acquire.pylabrobot_definition_name != pylabrobot_definition_name_constraint:
                raise AssetAcquisitionError(f"Chosen labware instance ID {user_choice_instance_id} does not match definition constraint {pylabrobot_definition_name_constraint}.")
            if labware_instance_to_acquire and labware_instance_to_acquire.current_status not in [LabwareInstanceStatusEnum.AVAILABLE_IN_STORAGE, LabwareInstanceStatusEnum.AVAILABLE_ON_DECK]:
                 raise AssetAcquisitionError(f"Chosen labware instance ID {user_choice_instance_id} is not available (status: {labware_instance_to_acquire.current_status}).")
        else:
            # Basic selection: Prioritize AVAILABLE_ON_DECK, then AVAILABLE_IN_STORAGE
            lws = ads.list_labware_instances(self.db, pylabrobot_definition_name=pylabrobot_definition_name_constraint, status=LabwareInstanceStatusEnum.AVAILABLE_ON_DECK)
            if not lws: 
                lws = ads.list_labware_instances(self.db, pylabrobot_definition_name=pylabrobot_definition_name_constraint, status=LabwareInstanceStatusEnum.AVAILABLE_IN_STORAGE)
            if not lws: 
                raise AssetAcquisitionError(f"No labware found matching definition '{pylabrobot_definition_name_constraint}' with available status.")
            labware_instance_to_acquire = lws[0] # Basic: pick first

        if not labware_instance_to_acquire: # Should be caught by above, but defensive check
            raise AssetAcquisitionError(f"Labware matching criteria for '{requested_asset_name_in_protocol}' not found or not available.")

        # Fetch LabwareDefinition to get the python_fqn
        # Using the existing get_labware_definition (aliased by get_labware_definition_by_name)
        labware_def_orm = ads.get_labware_definition(self.db, labware_instance_to_acquire.pylabrobot_definition_name) # type: ignore
        if not labware_def_orm or not hasattr(labware_def_orm, 'python_fqn') or not labware_def_orm.python_fqn: # type: ignore
            error_msg = f"Python FQN not found for labware definition '{labware_instance_to_acquire.pylabrobot_definition_name}' for instance ID {labware_instance_to_acquire.id}." # type: ignore
            print(f"ERROR: {error_msg}")
            # Update instance status to ERROR if FQN is missing, as it's unusable
            if ads: # Check if ads is not the placeholder
                ads.update_labware_instance_location_and_status(
                    db=self.db, labware_instance_id=labware_instance_to_acquire.id, # type: ignore
                    new_status=LabwareInstanceStatusEnum.ERROR, 
                    status_details=error_msg
                )
            raise AssetAcquisitionError(error_msg)
        labware_fqn = labware_def_orm.python_fqn # type: ignore

        print(f"INFO: Attempting to create PLR object for labware instance '{labware_instance_to_acquire.user_assigned_name}' (ID: {labware_instance_to_acquire.id}) using FQN '{labware_fqn}'.") # type: ignore
        live_plr_labware = self.workcell_runtime.create_or_get_labware_plr_object(
            labware_instance_orm=labware_instance_to_acquire, # type: ignore
            labware_definition_fqn=labware_fqn
        )

        if not live_plr_labware:
            # WorkcellRuntime should have set status to ERROR
            error_msg = f"Failed to create PLR object for labware '{labware_instance_to_acquire.user_assigned_name}' (ID: {labware_instance_to_acquire.id}). Check WorkcellRuntime logs." # type: ignore
            print(f"ERROR: {error_msg}")
            raise AssetAcquisitionError(error_msg)

        # PLR object created successfully, now update status and handle location
        print(f"INFO: PLR object for labware '{labware_instance_to_acquire.user_assigned_name}' created. Updating status to IN_USE.") # type: ignore
        
        # Deck assignment (simplified)
        target_deck_orm_id: Optional[int] = None
        target_slot_name: Optional[str] = None

        if location_constraints and isinstance(location_constraints, dict):
            deck_name = location_constraints.get("deck_name")
            slot_name = location_constraints.get("slot_name")
            if deck_name and slot_name:
                print(f"INFO: Location constraint: place '{live_plr_labware.name}' on deck '{deck_name}' slot '{slot_name}'.")
                # Find the deck ManagedDeviceOrm
                # Assuming ads.list_managed_devices can filter by user_friendly_name and praxis_device_category
                deck_device_list = ads.list_managed_devices(self.db, user_friendly_name_filter=deck_name, praxis_category_filter=PraxisDeviceCategoryEnum.DECK) # type: ignore
                if not deck_device_list:
                    raise AssetAcquisitionError(f"Deck '{deck_name}' specified in location_constraints not found.")
                deck_device_orm = deck_device_list[0]
                target_deck_orm_id = deck_device_orm.id
                target_slot_name = slot_name
                
                print(f"DEBUG: Assigning to Deck ID {target_deck_orm_id}, Slot {target_slot_name}")
                self.workcell_runtime.assign_labware_to_deck_slot(
                    deck_device_orm_id=target_deck_orm_id, # type: ignore
                    slot_name=target_slot_name, # type: ignore
                    labware_plr_object=live_plr_labware,
                    labware_instance_orm_id=labware_instance_to_acquire.id # type: ignore
                )
            elif deck_name or slot_name: # Partial location constraint
                raise AssetAcquisitionError(f"Partial location constraint for '{requested_asset_name_in_protocol}'. Both 'deck_name' and 'slot_name' required if placing on deck.")


        # Update final status (IN_USE) and potentially new location if assigned to deck
        # assign_labware_to_deck_slot in WCR already updates status to AVAILABLE_ON_DECK.
        # Here we mark it as IN_USE for the run.
        updated_labware_instance_orm = ads.update_labware_instance_location_and_status(
            self.db,
            labware_instance_id=labware_instance_to_acquire.id, # type: ignore
            new_status=LabwareInstanceStatusEnum.IN_USE,
            current_protocol_run_guid=protocol_run_guid,
            status_details=f"In use by run {protocol_run_guid}",
        )

        if not updated_labware_instance_orm:
            critical_error_msg = f"CRITICAL: Labware '{labware_instance_to_acquire.user_assigned_name}' PLR object created/assigned, but FAILED to update its DB status to IN_USE for run '{protocol_run_guid}'." # type: ignore
            print(f"ERROR: {critical_error_msg}")
            raise AssetAcquisitionError(critical_error_msg)

        print(f"INFO: Labware '{updated_labware_instance_orm.user_assigned_name}' (ID: {updated_labware_instance_orm.id}) successfully acquired for run '{protocol_run_guid}'.") # type: ignore
        return live_plr_labware, labware_instance_to_acquire.id, "labware" # MODIFIED return value

    def release_device(
        self, 
        device_orm_id: int, # Removed protocol_run_guid, not strictly needed to release
        final_status: ManagedDeviceStatusEnum = ManagedDeviceStatusEnum.AVAILABLE, 
        status_details: Optional[str] = "Released from run"
    ):
        print(f"INFO: Releasing device ID {device_orm_id}. Target status: {final_status.name if final_status else 'N/A'}.")

        # First, instruct WorkcellRuntime to shut down the backend.
        # WorkcellRuntime.shutdown_device_backend also updates status to OFFLINE in DB.
        if self.workcell_runtime: # Check if workcell_runtime is available
            print(f"INFO: Calling WorkcellRuntime to shut down backend for device ID {device_orm_id}.")
            self.workcell_runtime.shutdown_device_backend(device_orm_id) 
            # After shutdown, device is OFFLINE. If final_status is AVAILABLE, it means
            # it's ready for another run which might re-initialize.
            # If the desired state after protocol is different from what shutdown_device_backend sets,
            # update it again. For now, let's assume shutdown_device_backend sets it appropriately (e.g. OFFLINE or AVAILABLE).
            # If final_status is different from OFFLINE (set by WCR shutdown), an explicit update is needed.
            # The ads.update_managed_device_status in WCR's shutdown sets it to OFFLINE.
            # If we want it to be AVAILABLE, we might need another call here.
            # For simplicity in this step: let WCR handle the primary status update during shutdown.
            # This method primarily ensures WCR is called.
            # However, we always want to ensure current_protocol_run_guid is cleared and final_status is respected.
            # WCR's shutdown_device_backend already calls ads.update_managed_device_status.
            # Let's ensure the final desired state is set.
            # WCR sets to OFFLINE and clears run_guid. If final_status is e.g. AVAILABLE, we update again.
            if ads: # Check if ads is not the placeholder
                device_after_wcr_shutdown = ads.get_managed_device_by_id(self.db, device_id_orm_id)
                if device_after_wcr_shutdown and device_after_wcr_shutdown.current_status != final_status:
                     print(f"INFO: WorkcellRuntime set device {device_orm_id} to {device_after_wcr_shutdown.current_status}, but final desired status is {final_status}. Updating.")
                     ads.update_managed_device_status(
                        self.db, 
                        device_orm_id, 
                        final_status, 
                        status_details=status_details,
                        current_protocol_run_guid=None # Ensure it's cleared
                    )
                elif not device_after_wcr_shutdown: # Should not happen if WCR worked
                     print(f"ERROR: Device ID {device_orm_id} not found after WorkcellRuntime shutdown attempt.")


        else: # Fallback if no workcell_runtime (e.g. testing or error)
            print(f"WARNING: WorkcellRuntime not available. Attempting direct DB status update for device ID {device_orm_id}.")
            if ads: # Check if ads is not the placeholder
                updated_device = ads.update_managed_device_status(
                    self.db, 
                    device_orm_id, 
                    final_status, # Use the requested final_status
                    status_details=status_details,
                    current_protocol_run_guid=None # Explicitly clear the run GUID
                )
                if not updated_device:
                    print(f"ERROR: Failed to update status for device ID {device_orm_id} directly in DB.")
        
        print(f"INFO: Device ID {device_orm_id} release process initiated.")

    def release_labware(
        self, 
        labware_instance_orm_id: int, # Removed protocol_run_guid
        final_status: LabwareInstanceStatusEnum, 
        final_properties_json_update: Optional[Dict[str, Any]] = None,
        clear_from_deck_device_id: Optional[int] = None, # If it needs to be cleared from a specific deck
        clear_from_slot_name: Optional[str] = None,      # Slot name on that deck
        status_details: Optional[str] = "Released from run"
    ):
        print(f"INFO: Releasing labware ID {labware_instance_orm_id}. Target status: {final_status.name}. Details: {status_details}")

        final_location_device_id_for_ads: Optional[int] = None # Default to None (e.g. if not on deck or being moved to storage)
        final_deck_slot_name_for_ads: Optional[str] = None

        if clear_from_deck_device_id is not None and clear_from_slot_name is not None:
            if self.workcell_runtime:
                print(f"INFO: Calling WorkcellRuntime to clear labware ID {labware_instance_orm_id} from deck ID {clear_from_deck_device_id}, slot '{clear_from_slot_name}'.")
                self.workcell_runtime.clear_deck_slot(
                    deck_device_orm_id=clear_from_deck_device_id,
                    slot_name=clear_from_slot_name,
                    labware_instance_orm_id=labware_instance_orm_id # WCR uses this to update status to AVAILABLE_IN_STORAGE
                )
                # After clearing, it's typically AVAILABLE_IN_STORAGE and its location fields are nulled by WCR's call to ADS.
                # If final_status is different (e.g. TO_BE_DISPOSED), the subsequent ADS call will set it.
                # Location fields are effectively nulled by WCR, so we don't need to pass them to the final ads call unless
                # we are moving it to a *new* specific non-deck location, which is not handled here.
            else: # pragma: no cover
                print(f"WARNING: WorkcellRuntime not available. Cannot clear labware ID {labware_instance_orm_id} from deck. Manual DB update for status only.")
        
        # Update status, properties, and clear run GUID.
        # If cleared from deck by WCR, its location (deck_id, slot) should already be nulled,
        # and status might be AVAILABLE_IN_STORAGE. This call can override status if needed.
        print(f"INFO: Updating final status and details for labware ID {labware_instance_orm_id} in DB.")
        if ads: # Check if ads is not the placeholder
            updated_labware = ads.update_labware_instance_location_and_status(
                self.db,
                labware_instance_id=labware_instance_orm_id,
                new_status=final_status, # Set to the desired final status
                properties_json_update=final_properties_json_update,
                # If NOT cleared from deck, these might be used to set a new static location.
                # If cleared, WCR's ads call would have nulled them.
                # For simplicity, this release does not actively try to change location beyond deck clearing.
                # If it was on a deck and cleared, these should be None to reflect that.
                # If it was never on a deck, or we want to set a new storage location description, that's different.
                # The current ads.update_labware_instance_location_and_status will set location fields if provided.
                # If clear_from_deck was called, WCR's ads call already nulled location_device_id and current_deck_slot_name.
                # If we pass None here for those, it won't change them from what WCR set.
                location_device_id=final_location_device_id_for_ads, 
                current_deck_slot_name=final_deck_slot_name_for_ads,
                # physical_location_description can be set here if needed for new storage location.
                current_protocol_run_guid=None, # Explicitly clear the run GUID
                status_details=status_details
            )
            if not updated_labware:
                print(f"ERROR: Failed to update final status for labware ID {labware_instance_orm_id} in DB.")
        
        print(f"INFO: Labware ID {labware_instance_orm_id} release process initiated.")

    def acquire_asset(self, protocol_run_guid: str, asset_requirement: AssetRequirementModel) -> Tuple[Any, int, str]: # MODIFIED return type
        """
        Acquires an asset based on the AssetRequirementModel.
        This is a basic dispatcher to specific acquire methods.
        Actual asset selection and locking logic is complex and part of full AssetManager implementation.
        """
        print(f"INFO: AssetManager attempting to acquire asset '{asset_requirement.name}' "
              f"of type '{asset_requirement.actual_type_str}' for run '{protocol_run_guid}'. "
              f"Constraints: {asset_requirement.constraints_json}")

        # Basic heuristic to differentiate device vs labware based on common naming or known types.
        # This needs to be made more robust.
        is_likely_device = "pipette" in asset_requirement.actual_type_str.lower() or \
                           "handler" in asset_requirement.actual_type_str.lower() or \
                           "reader" in asset_requirement.actual_type_str.lower() or \
                           any(kw in asset_requirement.actual_type_str.lower() for kw in ["star", "hamilton", "opentrons", "ot2"])


        # Ensure constraint dicts are passed correctly, even if empty
        constraints_for_device = asset_requirement.constraints_json if asset_requirement.constraints_json else None
        properties_for_labware = asset_requirement.constraints_json if asset_requirement.constraints_json else None


        if is_likely_device:
            print(f"DEBUG: acquire_asset dispatching to acquire_device for {asset_requirement.name}")
            # Assuming acquire_device is updated or can handle these params.
            # The existing acquire_device stub might need adjustment if its signature is very different.
            return self.acquire_device(
                protocol_run_guid=protocol_run_guid,
                requested_asset_name_in_protocol=asset_requirement.name,
                pylabrobot_class_name_constraint=asset_requirement.actual_type_str,
                constraints=constraints_for_device 
            )
        else:
            print(f"DEBUG: acquire_asset dispatching to acquire_labware for {asset_requirement.name}")
            # Assuming acquire_labware is updated or can handle these params.
            return self.acquire_labware(
                protocol_run_guid=protocol_run_guid,
                requested_asset_name_in_protocol=asset_requirement.name,
                pylabrobot_definition_name_constraint=asset_requirement.actual_type_str,
                property_constraints=properties_for_labware
            )

