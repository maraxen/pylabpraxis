# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, traceback-print, too-many-lines
"""
praxis/core/workcell_runtime.py

The WorkcellRuntime manages live PyLabRobot objects (backends, resources)
for an active workcell configuration. It translates database-defined assets
into operational PyLabRobot instances.

Version 4: Refactored deck handling for explicit targeting and added deck state representation.
"""
from typing import Dict, Any, Optional, Type, List
import importlib
import traceback
import inspect
from sqlalchemy.ext.asyncio import AsyncSession


from praxis.backend.models import (
    ManagedDeviceOrm, LabwareInstanceOrm, LabwareDefinitionCatalogOrm,
    ManagedDeviceStatusEnum, LabwareInstanceStatusEnum, PraxisDeviceCategoryEnum
)
import praxis.backend.services.asset_data_service as ads
from pylabrobot.resources import Resource as PlrResource, Deck as PlrDeck
from pylabrobot.liquid_handling.backends.backend import LiquidHandlerBackend


def _get_class_from_fqn(class_fqn: str) -> Type:
    """Dynamically imports and returns a class from its fully qualified name."""
    if not class_fqn or '.' not in class_fqn:
        raise ValueError(f"Invalid fully qualified class name: {class_fqn}")
    module_name, class_name = class_fqn.rsplit('.', 1)
    imported_module = importlib.import_module(module_name)
    return getattr(imported_module, class_name)


class WorkcellRuntimeError(Exception):
    """Custom exception for WorkcellRuntime errors."""


class WorkcellRuntime:
    def __init__(self, db_session: Optional[AsyncSession] = None): # DbSession type
        self.db_session = db_session
        self._active_device_backends: Dict[int, Any] = {} # Maps ManagedDeviceOrm.id to live PLR backend/resource
        self._active_plr_labware_objects: Dict[int, PlrResource] = {} # Maps LabwareInstanceOrm.id to live PLR Resource

        # Renamed for clarity, stores the last initialized deck's ORM ID and PLR object.
        # This is for potential informational purposes or specific fallbacks if ever needed,
        # but core logic should rely on explicit deck IDs.
        self._last_initialized_deck_object: Optional[PlrDeck] = None
        self._last_initialized_deck_orm_id: Optional[int] = None


    async def initialize_device_backend(self, device_orm: ManagedDeviceOrm) -> Optional[Any]:
        """
        Initializes and connects to a device's PyLabRobot backend/resource.
        """
        if not hasattr(device_orm, 'id') or device_orm.id is None:
             print(f"ERROR: Invalid device_orm object passed to initialize_device_backend (no id).")
             return None
        if device_orm.id in self._active_device_backends:
            return self._active_device_backends[device_orm.id]

        print(f"INFO: Initializing backend/device '{device_orm.user_friendly_name}' (ID: {device_orm.id}) "
              f"using class '{device_orm.pylabrobot_class_name}'.")
        try:
            TargetClass = _get_class_from_fqn(device_orm.pylabrobot_class_name)
            backend_config = device_orm.backend_config_json or {}
            instance_name = device_orm.user_friendly_name # Use user-friendly name for PLR object name

            init_params = backend_config.copy()
            sig = inspect.signature(TargetClass.__init__)

            if 'name' in sig.parameters:
                init_params['name'] = instance_name
            elif 'name' in init_params and init_params['name'] != instance_name:
                 print(f"WARNING: 'name' in backend_config for {instance_name} differs. Using user_friendly_name.")
                 init_params['name'] = instance_name

            valid_init_params = {k: v for k, v in init_params.items() if k in sig.parameters}
            extra_params = {k:v for k,v in init_params.items() if k not in sig.parameters}
            if extra_params and 'options' in sig.parameters and isinstance(init_params.get('options'), dict):
                valid_init_params.setdefault('options', {}).update(extra_params)
            elif extra_params and 'options' in sig.parameters :
                 valid_init_params['options'] = extra_params
            elif extra_params:
                print(f"WARNING: Extra parameters in backend_config for {instance_name} not accepted by {TargetClass.__name__}.__init__: {extra_params.keys()}")

            backend_instance = TargetClass(**valid_init_params)

            if hasattr(backend_instance, 'setup') and callable(backend_instance.setup):
                print(f"INFO: Calling setup() for '{device_orm.user_friendly_name}'...")
                backend_instance.setup()

            self._active_device_backends[device_orm.id] = backend_instance
            print(f"INFO: Backend for '{device_orm.user_friendly_name}' initialized: {type(backend_instance).__name__}")

            if self.db_session and ads:
                await ads.update_managed_device_status(self.db_session, device_orm.id, ManagedDeviceStatusEnum.AVAILABLE, "Backend initialized.")

            # If this device is a PlrDeck, note it as the last initialized deck.
            # This does NOT make it the sole target for deck operations.
            if isinstance(backend_instance, PlrDeck):
                self._last_initialized_deck_object = backend_instance
                self._last_initialized_deck_orm_id = device_orm.id
                print(f"INFO: Device '{device_orm.user_friendly_name}' (ID: {device_orm.id}) identified as a PLR Deck object.")

            return backend_instance
        except Exception as e:
            print(f"ERROR: Failed to initialize backend for '{device_orm.user_friendly_name}' "
                  f"using class '{device_orm.pylabrobot_class_name}': {e}")
            traceback.print_exc()
            if self.db_session and ads and hasattr(device_orm, 'id') and device_orm.id is not None:
                ads.update_managed_device_status(self.db_session, device_orm.id, ManagedDeviceStatusEnum.ERROR, f"Backend init failed: {str(e)[:250]}")
            return None

    def create_or_get_labware_plr_object(
        self,
        labware_instance_orm: LabwareInstanceOrm,
        labware_definition_fqn: str
    ) -> Optional[PlrResource]:
        if not hasattr(labware_instance_orm, 'id') or labware_instance_orm.id is None:
            print(f"ERROR: Invalid labware_instance_orm passed (no id)."); return None
        if labware_instance_orm.id in self._active_plr_labware_objects:
            return self._active_plr_labware_objects[labware_instance_orm.id]

        print(f"INFO: Creating PLR object for labware '{labware_instance_orm.user_assigned_name}' (ID: {labware_instance_orm.id}) "
              f"using definition FQN '{labware_definition_fqn}'.")
        try:
            LabwareClass = _get_class_from_fqn(labware_definition_fqn)
            plr_object = LabwareClass(name=labware_instance_orm.user_assigned_name)
            self._active_plr_labware_objects[labware_instance_orm.id] = plr_object
            print(f"INFO: PLR object for '{labware_instance_orm.user_assigned_name}' created: {type(plr_object).__name__}")
            return plr_object
        except Exception as e:
            error_message = f"Failed to create PLR object for '{labware_instance_orm.user_assigned_name}' using FQN '{labware_definition_fqn}': {str(e)[:250]}"
            print(f"ERROR: {error_message}")
            traceback.print_exc()
            if self.db_session and ads and hasattr(labware_instance_orm, 'id') and labware_instance_orm.id is not None:
                try:
                    ads.update_labware_instance_location_and_status(
                        db=self.db_session,
                        labware_instance_id=labware_instance_orm.id,
                        new_status=LabwareInstanceStatusEnum.ERROR,
                        status_details=error_message
                    )
                except Exception as db_error: # pragma: no cover
                    print(f"ERROR: Failed to update LabwareInstance ID {labware_instance_orm.id} status to ERROR in DB: {db_error}")
            return None

    def get_active_device_backend(self, device_orm_id: int) -> Optional[Any]:
        return self._active_device_backends.get(device_orm_id)

    def shutdown_device_backend(self, device_orm_id: int):
        backend_instance = self._active_device_backends.pop(device_orm_id, None)
        if backend_instance:
            print(f"INFO: Shutting down backend for device ID: {device_orm_id}...")
            if hasattr(backend_instance, 'stop') and callable(backend_instance.stop):
                try:
                    backend_instance.stop()
                except Exception as e: # pragma: no cover
                    print(f"ERROR: Exception during stop() for device ID {device_orm_id}: {e}")
            if self._last_initialized_deck_orm_id == device_orm_id:
                self._last_initialized_deck_object = None
                self._last_initialized_deck_orm_id = None
            if self.db_session and ads:
                ads.update_managed_device_status(self.db_session, device_orm_id, ManagedDeviceStatusEnum.OFFLINE, "Backend shut down.")

    def get_active_labware_plr_object(self, labware_instance_orm_id: int) -> Optional[PlrResource]:
        return self._active_plr_labware_objects.get(labware_instance_orm_id)

    def assign_labware_to_deck_slot(self, deck_device_orm_id: int, slot_name: str, labware_plr_object: PlrResource, labware_instance_orm_id: int): # TODO: rework to use specific subclasses for assign to slot or general location
        deck_plr_obj = self.get_active_device_backend(deck_device_orm_id)
        if not deck_plr_obj:
            raise WorkcellRuntimeError(f"Deck device ID {deck_device_orm_id} is not an active backend.")
        if not isinstance(deck_plr_obj, PlrDeck):
            raise WorkcellRuntimeError(f"Device ID {deck_device_orm_id} (name: {getattr(deck_plr_obj, 'name', 'N/A')}) is not a PlrDeck instance. Type is {type(deck_plr_obj)}.")
        try:
            deck_plr_obj.assign_child_resource(resource=labware_plr_object, slot=slot_name) #TODO: have it inspect for args look for slots or rails, have it inspect for assign_child_resource_to_slot
            if self.db_session and ads:
                ads.update_labware_instance_location_and_status(
                    self.db_session,
                    labware_instance_orm_id,
                    LabwareInstanceStatusEnum.AVAILABLE_ON_DECK,
                    location_device_id=deck_device_orm_id,
                    current_deck_slot_name=slot_name
                )
        except Exception as e:
            traceback.print_exc()
            raise WorkcellRuntimeError(f"Error assigning labware '{labware_plr_object.name}' to slot '{slot_name}' on deck ID {deck_device_orm_id}: {e}")

    def clear_deck_slot(self, deck_device_orm_id: int, slot_name: str, labware_instance_orm_id: Optional[int] = None):
        deck_plr_obj = self.get_active_device_backend(deck_device_orm_id)
        if not deck_plr_obj:
            raise WorkcellRuntimeError(f"Deck device ID {deck_device_orm_id} is not an active backend.")
        if not isinstance(deck_plr_obj, PlrDeck):
            raise WorkcellRuntimeError(f"Device ID {deck_device_orm_id} (name: {getattr(deck_plr_obj, 'name', 'N/A')}) is not a PlrDeck instance. Type is {type(deck_plr_obj)}.")
        try:
            # PyLabRobot's PlrDeck unassign_child_resource can take either the resource object or the slot name.
            # It's safer to pass the slot name if we are unsure if the resource object is tracked.
            # However, if the slot has a resource, PLR might need the specific resource.
            # Let's try to get the resource first if the deck object allows easy lookup by slot.
            resource_in_slot = None
            if hasattr(deck_plr_obj, 'get_resource'): # Check if deck has a direct way to get resource by slot
                resource_in_slot = deck_plr_obj.get_resource(slot_name)

            if resource_in_slot:
                deck_plr_obj.unassign_child_resource(resource_in_slot)
            else: # Fallback to unassigning by slot name if resource not found or lookup not available
                deck_plr_obj.unassign_child_resource(slot_name)

            if labware_instance_orm_id and self.db_session and ads:
                ads.update_labware_instance_location_and_status(
                    self.db_session,
                    labware_instance_orm_id,
                    LabwareInstanceStatusEnum.AVAILABLE_IN_STORAGE, # Or another appropriate status
                    location_device_id=None,
                    current_deck_slot_name=None
                )
        except Exception as e:
            traceback.print_exc()
            raise WorkcellRuntimeError(f"Error clearing deck slot '{slot_name}' on deck ID {deck_device_orm_id}: {e}")

    def execute_device_action(self, device_orm_id: int, action_name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        backend = self.get_active_device_backend(device_orm_id)
        if not backend:
            raise WorkcellRuntimeError(f"Device ID {device_orm_id} backend not active.")
        if hasattr(backend, action_name) and callable(getattr(backend, action_name)):
            try:
                return getattr(backend, action_name)(**(params or {}))
            except Exception as e:
                traceback.print_exc()
                raise WorkcellRuntimeError(f"Error executing action '{action_name}' on device ID {device_orm_id}: {e}")
        else:
            raise AttributeError(f"Device backend for ID {device_orm_id} (type: {type(backend).__name__}) has no action '{action_name}'.")

    def shutdown_all_backends(self):
        print("INFO: Shutting down all active device backends...")
        for device_id in list(self._active_device_backends.keys()):
            self.shutdown_device_backend(device_id)
        print("INFO: All active backends processed for shutdown.")

    def get_deck_plr_object(self, deck_device_orm_id: int) -> Optional[PlrDeck]:
        """Gets a specific PLR Deck object by its ORM ID."""
        # This method prioritizes getting an already active deck.
        # If not active, it attempts to initialize it.
        deck_backend = self.get_active_device_backend(deck_device_orm_id)
        if deck_backend and isinstance(deck_backend, PlrDeck):
            return deck_backend

        if self.db_session and ads:
            deck_orm = ads.get_managed_device_by_id(self.db_session, deck_device_orm_id)
            if deck_orm and deck_orm.praxis_device_category == PraxisDeviceCategoryEnum.DECK:
                initialized_deck = self.initialize_device_backend(deck_orm)
                if isinstance(initialized_deck, PlrDeck):
                    return initialized_deck
        return None


    def get_deck_state_representation(self, deck_device_orm_id: int) -> Dict[str, Any]:
        """
        Constructs a dictionary representing the state of a specific deck,
        suitable for serialization into DeckStateResponse.
        Uses a DB-first approach for labware on deck.
        """
        if not self.db_session or not ads:
            raise WorkcellRuntimeError("Database session or asset_data_service not available.") # pragma: no cover

        deck_orm = ads.get_managed_device_by_id(self.db_session, deck_device_orm_id)
        if not deck_orm:
            raise WorkcellRuntimeError(f"Deck device with ID {deck_device_orm_id} not found in database.")
        if deck_orm.praxis_device_category != PraxisDeviceCategoryEnum.DECK:
            raise WorkcellRuntimeError(f"Device ID {deck_device_orm_id} (Name: {deck_orm.user_friendly_name}) is not categorized as a DECK (Category: {deck_orm.praxis_device_category}).")

        # Attempt to initialize/get live deck object to ensure it's 'ONLINE' or for future use with coordinates.
        # For now, the state representation is primarily DB-driven for assigned labware.
        # live_deck = self.get_deck_plr_object(deck_device_orm_id)
        # if not live_deck:
        #     print(f"WARNING: Live PlrDeck object for ID {deck_device_orm_id} could not be initialized or retrieved. "
        #           "Deck state will be based purely on database records of labware locations.")
            # Depending on requirements, we might raise an error here if live deck is mandatory for state.

        response_slots: List[Dict[str, Any]] = []
        # Fetch labware instances currently located on this specific deck device.
        # Assuming list_labware_instances can filter by location_device_id and optionally status.
        labware_on_deck = ads.list_labware_instances(
            db=self.db_session,
            location_device_id=deck_device_orm_id,
            # Consider if specific statuses like IN_USE or AVAILABLE_ON_DECK are needed.
            # If no status filter, it gets all labware instances that have this deck as their location.
        )

        for lw_instance in labware_on_deck:
            if lw_instance.current_deck_slot_name: # Ensure it has a slot name to be included
                if not hasattr(lw_instance, 'labware_definition') or not lw_instance.labware_definition: # pragma: no cover
                    print(f"WARNING: Labware instance ID {lw_instance.id} is missing labware_definition relationship. Skipping.")
                    continue
                lw_def = lw_instance.labware_definition

                labware_info_data = {
                    "labware_instance_id": lw_instance.id,
                    "user_assigned_name": lw_instance.user_assigned_name or f"Labware_{lw_instance.id}",
                    "pylabrobot_definition_name": lw_def.pylabrobot_definition_name,
                    "python_fqn": lw_def.python_fqn,
                    "category": str(lw_def.plr_category.value) if lw_def.plr_category else None, # Ensure enum is converted to string if not using Pydantic's enum handling
                    "size_x_mm": lw_def.size_x_mm,
                    "size_y_mm": lw_def.size_y_mm,
                    "size_z_mm": lw_def.size_z_mm,
                    "nominal_volume_ul": lw_def.nominal_volume_ul,
                    "properties_json": lw_instance.properties_json,
                    "model": lw_def.model,
                }
                slot_info_data = {
                    "name": lw_instance.current_deck_slot_name,
                    # TODO: Get slot coordinates from live_deck (e.g., live_deck.get_slot_center(slot_name))
                    # or from DeckConfigurationOrm if a specific layout is active and defines these.
                    "x_coordinate": None, # Placeholder
                    "y_coordinate": None, # Placeholder
                    "z_coordinate": None, # Placeholder
                    "labware": labware_info_data,
                }
                response_slots.append(slot_info_data)

        # TODO: Add empty slots. This would typically come from:
        # 1. A specific DeckConfigurationOrm that is "active" on this deck_device_orm_id, listing all its slots.
        # 2. Or, if a live_deck PlrDeck object is available, introspecting its defined slot names/sites.
        # For now, only slots with labware (according to DB) are reported.

        # Placeholder for overall deck dimensions.
        # This might come from deck_orm.pylabrobot_definition (if decks have their own "definition" like labware)
        # or from the live PlrDeck object.
        deck_size_x = None
        deck_size_y = None
        deck_size_z = None
        # Example: if live_deck and hasattr(live_deck, 'get_size'):
        #     deck_size_tuple = live_deck.get_size() # Assuming (x,y,z)
        #     deck_size_x, deck_size_y, deck_size_z = deck_size_tuple


        deck_state_data = {
            "deck_id": deck_orm.id,
            "user_friendly_name": deck_orm.user_friendly_name or f"Deck_{deck_orm.id}",
            "pylabrobot_class_name": deck_orm.pylabrobot_class_name,
            "size_x_mm": deck_size_x,
            "size_y_mm": deck_size_y,
            "size_z_mm": deck_size_z,
            "slots": response_slots,
        }
        return deck_state_data

    # get_main_deck_plr_object is now less central.
    # Renaming to indicate it gets the last initialized deck, or a specific one.
    def get_last_initialized_deck_object(self) -> Optional[PlrDeck]:
        """Returns the PlrDeck object that was most recently initialized by this runtime instance."""
        if self._last_initialized_deck_object:
            # Verify it's still active, re-initialize if not?
            # For now, just return if set.
            return self._last_initialized_deck_object

        # If not set, or if we want to ensure it's the "main" one from DB (if such a concept exists)
        # This part would need a way to identify a "main" deck from DB if that's desired.
        # For now, it just returns the last one this instance touched.
        return None

    # TODO: WCR-7: Add methods for loading/applying full DeckConfigurationOrm to the live deck.
    # This would involve:
    # - Clearing all existing labware from the live deck (if any).
    # - Iterating through DeckSlotOrm entries in the DeckConfigurationOrm.
    # - For each slot with assigned labware:
    #   - Get/create the PlrResource for the LabwareInstanceOrm.
    #   - Call assign_labware_to_deck_slot with the target deck's ORM ID.
    # - This would be the primary way to set up a live deck to match a saved configuration.
