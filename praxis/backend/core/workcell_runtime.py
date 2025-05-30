# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, traceback-print, too-many-lines
"""
praxis/core/workcell_runtime.py

The WorkcellRuntime manages live PyLabRobot objects (machines, resources)
for an active workcell configuration. It translates database-defined assets
into operational PyLabRobot instances.

Version 4: Refactored deck handling for explicit targeting and added deck state representation.
"""

from typing import Dict, Any, Optional, Type, List, Awaitable, Callable
import importlib
import traceback
import inspect
from sqlalchemy.ext.asyncio import AsyncSession


from praxis.backend.models import (
    MachineOrm,
    ResourceInstanceOrm,
    ResourceDefinitionCatalogOrm,
    MachineStatusEnum,
    ResourceInstanceStatusEnum,
    MachineCategoryEnum,
)
import praxis.backend.services as svc
from pylabrobot.resources import Resource, Deck, Coordinate
from pylabrobot.machines import Machine
from pylabrobot.liquid_handling.liquid_handler import LiquidHandler
import logging

logger = logging.getLogger(__name__)


def _get_class_from_fqn(class_fqn: str) -> Type:
    """Dynamically imports and returns a class from its fully qualified name."""
    if not class_fqn or "." not in class_fqn:
        raise ValueError(f"Invalid fully qualified class name: {class_fqn}")
    module_name, class_name = class_fqn.rsplit(".", 1)
    imported_module = importlib.import_module(module_name)
    return getattr(imported_module, class_name)


class WorkcellRuntimeError(Exception):
    """Custom exception for WorkcellRuntime errors."""


class WorkcellRuntime:
    def __init__(self, db_session: Optional[AsyncSession] = None):
        self.db_session = db_session
        self._active_machines: Dict[int, Machine] = {}
        self._active_resources: Dict[int, Resource] = {}
        self._last_initialized_deck_object: Optional[Deck] = None
        self._last_initialized_deck_orm_id: Optional[int] = None

    async def initialize_machine(self, machine_orm: MachineOrm) -> Optional[Any]:
        """
        Initializes and connects to a machine's PyLabRobot machine/resource.
        """
        if not hasattr(machine_orm, "id") or machine_orm.id is None:
            logger.error(
                "WorkcellRuntime: Invalid machine_orm object passed to "
                "initialize_machine (no id)."
            )
            return None
        if machine_orm.id in self._active_machines:
            return self._active_machines[machine_orm.id]

        logger.info(
            f"WorkcellRuntime: Initializing machine/machine "
            f"'{machine_orm.user_friendly_name}' (ID: {machine_orm.id}) "
            f"using class '{machine_orm.pylabrobot_class_name}'."
        )
        try:
            TargetClass = _get_class_from_fqn(machine_orm.pylabrobot_class_name)
            machine_config = machine_orm.backend_config_json or {}
            instance_name = machine_orm.user_friendly_name

            init_params = machine_config.copy()
            sig = inspect.signature(TargetClass.__init__)

            if "name" in sig.parameters:
                init_params["name"] = instance_name
            elif "name" in init_params and init_params["name"] != instance_name:
                logger.warning(
                    f"WorkcellRuntime: 'name' in machine_config for {instance_name} "
                    f"differs. Using user_friendly_name."
                )
                init_params["name"] = instance_name

            valid_init_params = {
                k: v for k, v in init_params.items() if k in sig.parameters
            }
            extra_params = {
                k: v for k, v in init_params.items() if k not in sig.parameters
            }
            if (
                extra_params
                and "options" in sig.parameters
                and isinstance(init_params.get("options"), dict)
            ):
                valid_init_params.setdefault("options", {}).update(extra_params)
            elif extra_params and "options" in sig.parameters:
                valid_init_params["options"] = extra_params
            elif extra_params:
                logger.warning(
                    f"WorkcellRuntime: Extra parameters in machine_config for "
                    f"{instance_name} not accepted by {TargetClass.__name__}.__init__: "
                    f"{extra_params.keys()}"
                )

            machine_instance = TargetClass(**valid_init_params)

            if (
                hasattr(machine_instance, "setup")
                and isinstance(machine_instance.setup, Awaitable)
                and isinstance(machine_instance.setup, Callable)
            ):
                logger.info(
                    f"WorkcellRuntime: Calling setup() for '{machine_orm.user_friendly_name}'..."
                )
                try:
                    await machine_instance.setup()
                except Exception as e:
                    logger.error(
                        f"WorkcellRuntime: Failed to call setup() for "
                        f"'{machine_orm.user_friendly_name}': {e}"
                    )
                    raise WorkcellRuntimeError(
                        f"Machine '{machine_orm.user_friendly_name}' setup failed: {str(e)[:250]}"
                    )
            else:
                logger.info(
                    f"WorkcellRuntime: No setup() method for '{machine_orm.user_friendly_name}'."
                )
                raise WorkcellRuntimeError(
                    f"Machine '{machine_orm.user_friendly_name}' does not implement a setup() "
                    f"method."
                )

            self._active_machines[machine_orm.id] = machine_instance
            logger.info(
                f"WorkcellRuntime: Machine for '{machine_orm.user_friendly_name}' initialized: "
                f"{type(machine_instance).__name__}"
            )

            if self.db_session and svc:
                await svc.update_machine_status(
                    self.db_session,
                    machine_orm.id,
                    MachineStatusEnum.AVAILABLE,
                    "Machine initialized.",
                )
            else:
                logger.warning(
                    "WorkcellRuntime: No db_session or service available. "
                    "Machine status will not be updated in the database."
                )

            return machine_instance
        except Exception as e:
            logger.error(
                f"WorkcellRuntime: Failed to initialize machine for "
                f"'{machine_orm.user_friendly_name}' "
                f"using class '{machine_orm.pylabrobot_class_name}': {e}"
            )
            traceback.print_exc()
            if (
                self.db_session
                and svc
                and hasattr(machine_orm, "id")
                and machine_orm.id is not None
            ):
                await svc.update_machine_status(
                    self.db_session,
                    machine_orm.id,
                    MachineStatusEnum.ERROR,
                    f"Machine init failed: {str(e)[:250]}",
                )
            return None

    async def create_or_get_resource(
        self, resource_instance_orm: ResourceInstanceOrm, resource_definition_fqn: str
    ) -> Optional[Resource]:
        if not hasattr(resource_instance_orm, "id") or resource_instance_orm.id is None:
            logger.error(
                "WorkcellRuntime: Invalid resource_instance_orm passed (no id)."
            )
            return None
        if resource_instance_orm.id in self._active_resources:
            return self._active_resources[resource_instance_orm.id]

        print(
            f"INFO: Creating PLR resource '{resource_instance_orm.user_assigned_name}' "
            f"(ID: {resource_instance_orm.id}) "
            f"using definition FQN '{resource_definition_fqn}'."
        )
        try:
            ResourceClass = _get_class_from_fqn(resource_definition_fqn)
            resource = ResourceClass(name=resource_instance_orm.user_assigned_name)
            self._active_resources[resource_instance_orm.id] = resource
            print(
                f"INFO: PLR resource for '{resource_instance_orm.user_assigned_name}' created: "
                f"{type(resource).__name__}"
            )
            return resource
        except Exception as e:
            error_message = "Failed to create PLR resource for "
            f"'{resource_instance_orm.user_assigned_name}' using FQN '{resource_definition_fqn}': "
            f"{str(e)[:250]}"
            logger.error(f"WorkcellRuntime: {error_message}")
            traceback.print_exc()
            if (
                self.db_session
                and svc
                and hasattr(resource_instance_orm, "id")
                and resource_instance_orm.id is not None
            ):
                try:
                    await svc.update_resource_instance_location_and_status(
                        db=self.db_session,
                        resource_instance_id=resource_instance_orm.id,
                        new_status=ResourceInstanceStatusEnum.ERROR,
                        status_details=error_message,
                    )
                except Exception as db_error:  # pragma: no cover
                    logger.error(
                        f"WorkcellRuntime: Failed to update ResourceInstance ID "
                        f"{resource_instance_orm.id} status to ERROR in DB: {db_error}"
                    )
            return None

    def get_active_machine(self, machine_orm_id: int) -> Optional[Any]:
        return self._active_machines.get(machine_orm_id)

    async def shutdown_machine(self, machine_orm_id: int):
        machine_instance = self._active_machines.pop(machine_orm_id, None)
        if machine_instance:
            try:
                logger.info(
                    f"WorkcellRuntime: Shutting down machine for machine ID: {machine_orm_id}..."
                )
                if (
                    hasattr(machine_instance, "stop")
                    and isinstance(machine_instance.stop, Awaitable)
                    and isinstance(machine_instance.stop, Callable)
                ):
                    logger.info(
                        f"WorkcellRuntime: Calling stop() for machine ID {machine_orm_id}..."
                    )
                    await machine_instance.stop()

                else:
                    logger.warning(
                        f"WorkcellRuntime: No stop() method for machine ID {machine_orm_id} that is "
                        f"callable and awaitable."
                    )
                    raise WorkcellRuntimeError(
                        f"Machine with ID {machine_orm_id} does not implement a stop() method."
                    )
                if self._last_initialized_deck_orm_id == machine_orm_id:
                    self._last_initialized_deck_object = None
                    self._last_initialized_deck_orm_id = None
                if self.db_session and svc:
                    await svc.update_machine_status(
                        self.db_session,
                        machine_orm_id,
                        MachineStatusEnum.OFFLINE,
                        "Machine shut down.",
                    )
            except Exception as e:
                logger.error(
                    f"WorkcellRuntime: Exception during shutdown for machine ID {machine_orm_id}: {e}"
                )
                traceback.print_exc()
                if self.db_session and svc:
                    await svc.update_machine_status(
                        self.db_session,
                        machine_orm_id,
                        MachineStatusEnum.ERROR,
                        f"Shutdown failed: {str(e)[:250]}",
                    )
        else:
            logger.warning(
                f"WorkcellRuntime: No active machine found for machine ID {machine_orm_id}."
            )
            if self.db_session and svc:
                await svc.update_machine_status(
                    self.db_session,
                    machine_orm_id,
                    MachineStatusEnum.OFFLINE,
                    "Machine not found for shutdown.",
                )

    def get_active_resource(self, resource_instance_orm_id: int) -> Optional[Resource]:
        return self._active_resources.get(resource_instance_orm_id)

    async def assign_resource_to_deck(
        self,
        deck_orm_id: int,
        resource: Resource,
        resource_instance_orm_id: int,
        location: Coordinate | tuple[float, float, float] | None = None,
        slot_id: str | int | None = None,
    ):
        if location is None and slot_id is None:
            raise WorkcellRuntimeError(
                "Either 'location' or 'slot_id' must be provided to assign a resource to a deck."
            )
        target_deck = self.get_active_machine(deck_orm_id)
        if target_deck is None:
            raise WorkcellRuntimeError(
                f"Deck machine ID {deck_orm_id} is not assigned to an active machine."
            )
        if not isinstance(target_deck, Deck):
            raise WorkcellRuntimeError(
                f"Device ID {deck_orm_id} (name: {getattr(target_deck, 'name', 'N/A')}) is not a "
                f"Deck instance. Type is {type(target_deck)}."
            )
        try:
            if slot_id is not None:
                target_deck.assign_child_resource(
                    resource=resource, location=target_deck.get_slot_location(slot_id)
                )
                if self.db_session and svc:
                    await svc.update_resource_instance_location_and_status(
                        self.db_session,
                        resource_instance_orm_id,
                        ResourceInstanceStatusEnum.AVAILABLE_ON_DECK,
                        location_id=deck_orm_id,
                        current_deck_slot_id=slot_id,
                    )
        except Exception as e:
            traceback.print_exc()
            raise WorkcellRuntimeError(
                f"Error assigning resource '{resource_plr_object.name}' to slot '{slot_name}' on deck ID {deck_machine_orm_id}: {e}"
            )

    def clear_deck_slot(
        self,
        deck_machine_orm_id: int,
        slot_name: str,
        resource_instance_orm_id: Optional[int] = None,
    ):
        deck_plr_obj = self.get_active_machine_machine(deck_machine_orm_id)
        if not deck_plr_obj:
            raise WorkcellRuntimeError(
                f"Deck machine ID {deck_machine_orm_id} is not an active machine."
            )
        if not isinstance(deck_plr_obj, PlrDeck):
            raise WorkcellRuntimeError(
                f"Device ID {deck_machine_orm_id} (name: {getattr(deck_plr_obj, 'name', 'N/A')}) is not a PlrDeck instance. Type is {type(deck_plr_obj)}."
            )
        try:
            # PyLabRobot's PlrDeck unassign_child_resource can take either the resource object or the slot name.
            # It's safer to pass the slot name if we are unsure if the resource object is tracked.
            # However, if the slot has a resource, PLR might need the specific resource.
            # Let's try to get the resource first if the deck object allows easy lookup by slot.
            resource_in_slot = None
            if hasattr(
                deck_plr_obj, "get_resource"
            ):  # Check if deck has a direct way to get resource by slot
                resource_in_slot = deck_plr_obj.get_resource(slot_name)

            if resource_in_slot:
                deck_plr_obj.unassign_child_resource(resource_in_slot)
            else:  # Fallback to unassigning by slot name if resource not found or lookup not available
                deck_plr_obj.unassign_child_resource(slot_name)

            if resource_instance_orm_id and self.db_session and svc:
                svc.update_resource_instance_location_and_status(
                    self.db_session,
                    resource_instance_orm_id,
                    ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,  # Or another appropriate status
                    location_machine_id=None,
                    current_deck_slot_name=None,
                )
        except Exception as e:
            traceback.print_exc()
            raise WorkcellRuntimeError(
                f"Error clearing deck slot '{slot_name}' on deck ID {deck_machine_orm_id}: {e}"
            )

    def execute_machine_action(
        self,
        machine_orm_id: int,
        action_name: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        machine = self.get_active_machine_machine(machine_orm_id)
        if not machine:
            raise WorkcellRuntimeError(
                f"Device ID {machine_orm_id} machine not active."
            )
        if hasattr(machine, action_name) and callable(getattr(machine, action_name)):
            try:
                return getattr(machine, action_name)(**(params or {}))
            except Exception as e:
                traceback.print_exc()
                raise WorkcellRuntimeError(
                    f"Error executing action '{action_name}' on machine ID {machine_orm_id}: {e}"
                )
        else:
            raise AttributeError(
                f"Device machine for ID {machine_orm_id} (type: {type(machine).__name__}) has no action '{action_name}'."
            )

    def shutdown_all_machines(self):
        logger.info("WorkcellRuntime: Shutting down all active machine machines...")
        for machine_id in list(self._active_machine_machines.keys()):
            self.shutdown_machine_machine(machine_id)
        logger.info("WorkcellRuntime: All active machines processed for shutdown.")

    def get_deck_plr_object(self, deck_machine_orm_id: int) -> Optional[PlrDeck]:
        """Gets a specific PLR Deck object by its ORM ID."""
        # This method prioritizes getting an already active deck.
        # If not active, it attempts to initialize it.
        deck_machine = self.get_active_machine_machine(deck_machine_orm_id)
        if deck_machine and isinstance(deck_machine, PlrDeck):
            return deck_machine

        if self.db_session and svc:
            deck_orm = svc.get_machine_by_id(self.db_session, deck_machine_orm_id)
            if (
                deck_orm
                and deck_orm.praxis_machine_category == MachineCategoryEnum.DECK
            ):
                initialized_deck = self.initialize_machine_machine(deck_orm)
                if isinstance(initialized_deck, PlrDeck):
                    return initialized_deck
        return None

    def get_deck_state_representation(self, deck_machine_orm_id: int) -> Dict[str, Any]:
        """
        Constructs a dictionary representing the state of a specific deck,
        suitable for serialization into DeckStateResponse.
        Uses a DB-first approach for resource on deck.
        """
        if not self.db_session or not svc:
            raise WorkcellRuntimeError(
                "Database session or asset_data_service not available."
            )  # pragma: no cover

        deck_orm = svc.get_machine_by_id(self.db_session, deck_machine_orm_id)
        if not deck_orm:
            raise WorkcellRuntimeError(
                f"Deck machine with ID {deck_machine_orm_id} not found in database."
            )
        if deck_orm.praxis_machine_category != MachineCategoryEnum.DECK:
            raise WorkcellRuntimeError(
                f"Device ID {deck_machine_orm_id} (Name: {deck_orm.user_friendly_name}) is not categorized as a DECK (Category: {deck_orm.praxis_machine_category})."
            )

        # Attempt to initialize/get live deck object to ensure it's 'ONLINE' or for future use with coordinates.
        # For now, the state representation is primarily DB-driven for assigned resource.
        # live_deck = self.get_deck_plr_object(deck_machine_orm_id)
        # if not live_deck:
        #     print(f"WARNING: Live PlrDeck object for ID {deck_machine_orm_id} could not be initialized or retrieved. "
        #           "Deck state will be based purely on database records of resource locations.")
        # Depending on requirements, we might raise an error here if live deck is mandatory for state.

        response_slots: List[Dict[str, Any]] = []
        # Fetch resource instances currently located on this specific deck machine.
        # Assuming list_resource_instances can filter by location_machine_id and optionally status.
        resource_on_deck = svc.list_resource_instances(
            db=self.db_session,
            location_machine_id=deck_machine_orm_id,
            # Consider if specific statuses like IN_USE or AVAILABLE_ON_DECK are needed.
            # If no status filter, it gets all resource instances that have this deck as their location.
        )

        for lw_instance in resource_on_deck:
            if (
                lw_instance.current_deck_slot_name
            ):  # Ensure it has a slot name to be included
                if (
                    not hasattr(lw_instance, "resource_definition")
                    or not lw_instance.resource_definition
                ):  # pragma: no cover
                    print(
                        f"WARNING: Resource instance ID {lw_instance.id} is missing resource_definition relationship. Skipping."
                    )
                    continue
                lw_def = lw_instance.resource_definition

                resource_info_data = {
                    "resource_instance_id": lw_instance.id,
                    "user_assigned_name": lw_instance.user_assigned_name
                    or f"Resource_{lw_instance.id}",
                    "pylabrobot_definition_name": lw_def.pylabrobot_definition_name,
                    "python_fqn": lw_def.python_fqn,
                    "category": str(lw_def.plr_category.value)
                    if lw_def.plr_category
                    else None,  # Ensure enum is converted to string if not using Pydantic's enum handling
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
                    "x_coordinate": None,  # Placeholder
                    "y_coordinate": None,  # Placeholder
                    "z_coordinate": None,  # Placeholder
                    "resource": resource_info_data,
                }
                response_slots.append(slot_info_data)

        # TODO: Add empty slots. This would typically come from:
        # 1. A specific DeckConfigurationOrm that is "active" on this deck_machine_orm_id, listing all its slots.
        # 2. Or, if a live_deck PlrDeck object is available, introspecting its defined slot names/sites.
        # For now, only slots with resource (according to DB) are reported.

        # Placeholder for overall deck dimensions.
        # This might come from deck_orm.pylabrobot_definition (if decks have their own "definition" like resource)
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
    # - Clearing all existing resource from the live deck (if any).
    # - Iterating through DeckSlotOrm entries in the DeckConfigurationOrm.
    # - For each slot with assigned resource:
    #   - Get/create the PlrResource for the ResourceInstanceOrm.
    #   - Call assign_resource_to_deck_slot with the target deck's ORM ID.
    # - This would be the primary way to set up a live deck to match a saved configuration.
