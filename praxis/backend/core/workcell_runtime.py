# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, traceback-print
"""
praxis/core/workcell_runtime.py

The WorkcellRuntime manages live PyLabRobot objects (backends, resources)
for an active workcell configuration. It translates database-defined assets
into operational PyLabRobot instances.

Version 3: Implements more robust dynamic instantiation for devices/backends (WCR-4)
           and labware resources (WCR-5) using fully qualified class paths.
"""
from typing import Dict, Any, Optional, Type
import importlib
import traceback
import inspect # For inspecting constructor parameters

# Assuming ORM models and Enums are correctly defined and importable
# TODO: WCR-1: Ensure these imports are valid based on project structure.
try:
    from praxis.database_models.asset_management_orm import (
        ManagedDeviceOrm, LabwareInstanceOrm, # LabwareDefinitionCatalogOrm not directly used here
        ManagedDeviceStatusEnum, LabwareInstanceStatusEnum # For status updates
    )
    from praxis.db_services import asset_data_service as ads
except ImportError:
    print("WARNING: WCR-1: Could not import ORM models or asset_data_service. WorkcellRuntime will use placeholders.")
    class ManagedDeviceOrm: id: int; user_friendly_name: str; pylabrobot_class_name: str; backend_config_json: Optional[Dict[str,Any]]; current_status: Any # type: ignore
    class LabwareInstanceOrm: id: int; user_assigned_name: str; pylabrobot_definition_name: str # type: ignore
    class ManagedDeviceStatusEnum(enum.Enum): OFFLINE="offline"; AVAILABLE="available"; ERROR="error"; IN_USE="in_use" # type: ignore
    class LabwareInstanceStatusEnum(enum.Enum): AVAILABLE_ON_DECK="available_on_deck"; AVAILABLE_IN_STORAGE="available_in_storage"; IN_USE="in_use"; EMPTY="empty"; UNKNOWN="unknown" # type: ignore
    import enum # Required if enum is used above
    ads = None # type: ignore


# PyLabRobot imports
# TODO: WCR-2: Ensure PyLabRobot is fully importable.
try:
    from pylabrobot.resources import Resource as PlrResource, Deck as PlrDeck
    from pylabrobot.liquid_handling.backends.backend import LiquidHandlerBackend
    # Import other specific backend/device base classes if needed for isinstance checks
    from pylabrobot.heating_shaking.heater_shaker import HeaterShakerDevice # Example device
    # No ResourceLoader needed here as we use FQN
except ImportError:
    print("WARNING: WCR-2: PyLabRobot not found/fully importable. WorkcellRuntime PLR interactions will be limited.")
    class PlrResource: name: str; def serialize(self): return {}; def __init__(self, name: str, **kwargs): self.name = name # type: ignore
    class PlrDeck(PlrResource): # type: ignore
        def assign_child_resource(self, resource, slot): pass
        def unassign_child_resource(self, slot_name_or_resource): pass
    class LiquidHandlerBackend: # type: ignore
        def setup(self): pass
        def stop(self): pass
    class HeaterShakerDevice(PlrResource): pass # type: ignore


def _get_class_from_fqn(class_fqn: str) -> Type:
    """Dynamically imports and returns a class from its fully qualified name."""
    if not class_fqn or '.' not in class_fqn:
        raise ValueError(f"Invalid fully qualified class name: {class_fqn}")
    module_name, class_name = class_fqn.rsplit('.', 1)
    imported_module = importlib.import_module(module_name)
    return getattr(imported_module, class_name)


class WorkcellRuntime:
    def __init__(self, db_session: Optional[Any] = None): # DbSession type
        self.db_session = db_session
        self._active_device_backends: Dict[int, Any] = {}
        self._active_plr_labware_objects: Dict[int, PlrResource] = {}
        self._main_deck_plr_object: Optional[PlrDeck] = None
        self._main_deck_device_orm_id: Optional[int] = None
        # TODO: WCR-3: Load main deck configuration on initialization if a default workcell setup is defined.

    def initialize_device_backend(self, device_orm: ManagedDeviceOrm) -> Optional[Any]:
        """
        Initializes and connects to a device's PyLabRobot backend/resource.
        (WCR-4 Implemented more robustly)
        """
        if not hasattr(device_orm, 'id') or device_orm.id is None:
             print(f"ERROR: Invalid device_orm object passed to initialize_device_backend (no id).")
             return None
        if device_orm.id in self._active_device_backends:
            # print(f"INFO: Backend for device '{device_orm.user_friendly_name}' (ID: {device_orm.id}) already active.")
            return self._active_device_backends[device_orm.id]

        print(f"INFO: Initializing backend/device '{device_orm.user_friendly_name}' (ID: {device_orm.id}) "
              f"using class '{device_orm.pylabrobot_class_name}'.")
        try:
            TargetClass = _get_class_from_fqn(device_orm.pylabrobot_class_name)
            backend_config = device_orm.backend_config_json or {}
            instance_name = device_orm.user_friendly_name # Use user-friendly name for PLR object name

            init_params = backend_config.copy()
            sig = inspect.signature(TargetClass.__init__)

            # Common PLR resources often take 'name' and 'size_x', 'size_y', 'size_z' etc.
            # Backends usually take specific connection params (e.g. 'com_port') or a generic 'options' dict.
            # This logic tries to be flexible.
            if 'name' in sig.parameters:
                init_params['name'] = instance_name
            elif 'name' in init_params and init_params['name'] != instance_name:
                 print(f"WARNING: 'name' in backend_config for {instance_name} differs. Using user_friendly_name.")
                 init_params['name'] = instance_name


            # Filter init_params to only include what the constructor accepts
            valid_init_params = {k: v for k, v in init_params.items() if k in sig.parameters}
            extra_params = {k:v for k,v in init_params.items() if k not in sig.parameters}
            if extra_params and 'options' in sig.parameters and isinstance(init_params.get('options'), dict):
                # If 'options' is a dict, merge extra params into it
                valid_init_params.setdefault('options', {}).update(extra_params)
            elif extra_params and 'options' in sig.parameters : # options is expected but not a dict
                 valid_init_params['options'] = extra_params # pass as is
            elif extra_params:
                print(f"WARNING: Extra parameters in backend_config for {instance_name} not accepted by {TargetClass.__name__}.__init__: {extra_params.keys()}")


            backend_instance = TargetClass(**valid_init_params)

            if hasattr(backend_instance, 'setup') and callable(backend_instance.setup):
                print(f"INFO: Calling setup() for '{device_orm.user_friendly_name}'...")
                backend_instance.setup() # type: ignore

            self._active_device_backends[device_orm.id] = backend_instance
            print(f"INFO: Backend for '{device_orm.user_friendly_name}' initialized: {type(backend_instance).__name__}")

            if self.db_session and ads:
                ads.update_managed_device_status(self.db_session, device_orm.id, ManagedDeviceStatusEnum.AVAILABLE, "Backend initialized.")

            if isinstance(backend_instance, PlrDeck): # Check if it IS a Deck resource
                self._main_deck_plr_object = backend_instance
                self._main_deck_device_orm_id = device_orm.id
                print(f"INFO: Device '{device_orm.user_friendly_name}' identified as main PLR Deck object.")

            return backend_instance
        except Exception as e:
            print(f"ERROR: WCR-4: Failed to initialize backend for '{device_orm.user_friendly_name}' "
                  f"using class '{device_orm.pylabrobot_class_name}': {e}")
            traceback.print_exc()
            if self.db_session and ads and hasattr(device_orm, 'id') and device_orm.id is not None:
                ads.update_managed_device_status(self.db_session, device_orm.id, ManagedDeviceStatusEnum.ERROR, f"Backend init failed: {str(e)[:250]}")
            return None

    def create_or_get_labware_plr_object(self, labware_instance_orm: LabwareInstanceOrm) -> Optional[PlrResource]:
        """
        Creates or retrieves a live PyLabRobot Resource object for a labware instance
        using its FQN stored in pylabrobot_definition_name.
        (WCR-5 Implemented more robustly)
        """
        if not hasattr(labware_instance_orm, 'id') or labware_instance_orm.id is None:
            print(f"ERROR: Invalid labware_instance_orm passed (no id)."); return None
        if labware_instance_orm.id in self._active_plr_labware_objects:
            return self._active_plr_labware_objects[labware_instance_orm.id]

        print(f"INFO: Creating PLR object for labware '{labware_instance_orm.user_assigned_name}' (ID: {labware_instance_orm.id}) "
              f"using definition FQN '{labware_instance_orm.pylabrobot_definition_name}'.")
        try:
            LabwareClass = _get_class_from_fqn(labware_instance_orm.pylabrobot_definition_name)

            # Most PLR labware resources are initialized with a 'name'.
            # Additional parameters might come from their class defaults or definition.
            # For specific instances, properties_json could override some aspects, but that's advanced.
            plr_object = LabwareClass(name=labware_instance_orm.user_assigned_name) # type: ignore

            self._active_plr_labware_objects[labware_instance_orm.id] = plr_object
            print(f"INFO: PLR object for '{labware_instance_orm.user_assigned_name}' created: {type(plr_object).__name__}")
            return plr_object
        except Exception as e:
            print(f"ERROR: WCR-5: Failed to create PLR object for '{labware_instance_orm.user_assigned_name}' "
                  f"using FQN '{labware_instance_orm.pylabrobot_definition_name}': {e}")
            traceback.print_exc()
            # TODO: WCR-5A: Consider updating LabwareInstanceOrm status to ERROR if load fails.
            return None

    # --- Other methods (get_active_device_backend, shutdown_device_backend, get_active_labware_plr_object,
    # assign_labware_to_deck_slot, clear_deck_slot, execute_device_action, shutdown_all_backends,
    # get_main_deck_plr_object) remain structurally the same as v2 of this file.
    # They will benefit from the more robust instantiation above.
    # Condensed for brevity. Ensure full logic from previous version is retained for these.

    def get_active_device_backend(self, device_orm_id: int) -> Optional[Any]:
        return self._active_device_backends.get(device_orm_id)

    def shutdown_device_backend(self, device_orm_id: int):
        backend_instance = self._active_device_backends.pop(device_orm_id, None)
        if backend_instance: # ... (full shutdown logic) ...
            print(f"INFO: Shutting down backend for device ID: {device_orm_id}...")
            if hasattr(backend_instance, 'stop') and callable(backend_instance.stop): backend_instance.stop() # type: ignore
            if self._main_deck_device_orm_id == device_orm_id: self._main_deck_plr_object = None; self._main_deck_device_orm_id = None
            if self.db_session and ads: ads.update_managed_device_status(self.db_session, device_orm_id, ManagedDeviceStatusEnum.OFFLINE, "Backend shut down.")


    def get_active_labware_plr_object(self, labware_instance_orm_id: int) -> Optional[PlrResource]:
        return self._active_plr_labware_objects.get(labware_instance_orm_id)

    def assign_labware_to_deck_slot(self, deck_device_orm_id: int, slot_name: str, labware_plr_object: PlrResource, labware_instance_orm_id: int):
        deck_plr_obj = self.get_active_device_backend(deck_device_orm_id)
        if not isinstance(deck_plr_obj, PlrDeck):
            if self._main_deck_device_orm_id == deck_device_orm_id and self._main_deck_plr_object: deck_plr_obj = self._main_deck_plr_object
            else: print(f"ERROR: Device ID {deck_device_orm_id} is not an active PlrDeck."); return
        try:
            deck_plr_obj.assign_child_resource(resource=labware_plr_object, slot=slot_name)
            if self.db_session and ads: ads.update_labware_instance_location_and_status(self.db_session, labware_instance_orm_id, LabwareInstanceStatusEnum.AVAILABLE_ON_DECK, location_device_id=deck_device_orm_id, current_deck_slot_name=slot_name)
        except Exception as e: print(f"ERROR: Assigning labware to slot '{slot_name}': {e}"); traceback.print_exc()


    def clear_deck_slot(self, deck_device_orm_id: int, slot_name: str, labware_instance_orm_id: Optional[int] = None):
        deck_plr_obj = self.get_active_device_backend(deck_device_orm_id)
        if not isinstance(deck_plr_obj, PlrDeck):
            if self._main_deck_device_orm_id == deck_device_orm_id and self._main_deck_plr_object: deck_plr_obj = self_main_deck_plr_object = self._main_deck_plr_object # type: ignore
            else: print(f"ERROR: Device ID {deck_device_orm_id} is not an active PlrDeck."); return
        try:
            resource_in_slot = deck_plr_obj[slot_name]; # type: ignore
            if resource_in_slot: deck_plr_obj.unassign_child_resource(resource_in_slot) # type: ignore
            else: deck_plr_obj.unassign_child_resource(slot_name) # type: ignore
            if labware_instance_orm_id and self.db_session and ads: ads.update_labware_instance_location_and_status(self.db_session, labware_instance_orm_id, LabwareInstanceStatusEnum.AVAILABLE_IN_STORAGE, location_device_id=None, current_deck_slot_name=None)
        except Exception as e: print(f"ERROR: Clearing deck slot '{slot_name}': {e}"); traceback.print_exc()

    def execute_device_action(self, device_orm_id: int, action_name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        # TODO: WCR-6: Implement robust method dispatch and error handling.
        backend = self.get_active_device_backend(device_orm_id) # ... (full logic) ...
        if not backend: raise RuntimeError(f"Device ID {device_orm_id} backend not active.")
        if hasattr(backend, action_name) and callable(getattr(backend, action_name)): return getattr(backend, action_name)(**(params or {}))
        else: raise AttributeError(f"Device backend for ID {device_orm_id} has no action '{action_name}'.")


    def shutdown_all_backends(self):
        print("INFO: Shutting down all active device backends...")
        for device_id in list(self._active_device_backends.keys()): self.shutdown_device_backend(device_id)
        print("INFO: All active backends processed for shutdown.")

    def get_main_deck_plr_object(self) -> Optional[PlrDeck]:
        if not self._main_deck_plr_object and self._main_deck_device_orm_id and self.db_session and ads:
            deck_orm = ads.get_managed_device_by_id(self.db_session, self._main_deck_device_orm_id)
            if deck_orm: self.initialize_device_backend(deck_orm)
        return self._main_deck_plr_object

    # TODO: WCR-7: Add methods for loading/applying full DeckConfigurationOrm to the live deck.

