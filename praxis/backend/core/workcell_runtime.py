# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, traceback-print
"""Workcell Runtime Management.

praxis/core/workcell_runtime.py

The WorkcellRuntime manages live PyLabRobot objects (machines, resources)
for an active workcell configuration. It translates database-defined assets
into operational PyLabRobot instances.
"""

from functools import wraps
import importlib
import inspect
import logging
import traceback
from typing import Any, Awaitable, Callable, Dict, List, Optional, Type
import warnings

from pylabrobot.liquid_handling.liquid_handler import LiquidHandler
from pylabrobot.machines import Machine
from pylabrobot.resources import Coordinate, Deck, Resource
from sqlalchemy.ext.asyncio import AsyncSession

import praxis.backend.services as svc
from praxis.backend.models import (
  DeckTypeDefinitionOrm,
  MachineCategoryEnum,
  MachineOrm,
  MachineStatusEnum,
  ResourceCategoryEnum,
  ResourceDefinitionCatalogOrm,
  ResourceInstanceOrm,
  ResourceInstanceStatusEnum,
)
from praxis.backend.utils.errors import WorkcellRuntimeError

logger = logging.getLogger(__name__)


def check_db_session(func: Callable) -> Callable:
  """Decorator to ensure a valid database session is available."""

  @wraps(func)
  async def wrapper(*args, **kwargs):
    if args[0].db_session is None:
      warn_message = (
        "No database session available for WorkcellRuntime. Use without db_session"
        " is not recommended."
      )
      warnings.warn(warn_message)
      logger.warning(warn_message)
    return await func(*args, **kwargs)

  return wrapper


def _get_class_from_fqn(class_fqn: str) -> Type:
  """Dynamically imports and returns a class from its fully qualified name."""
  if not class_fqn or "." not in class_fqn:
    raise ValueError("Invalid fully qualified class name: %s", class_fqn)
  module_name, class_name = class_fqn.rsplit(".", 1)
  imported_module = importlib.import_module(module_name)
  return getattr(imported_module, class_name)


class WorkcellRuntime:
  """Manages live PyLabRobot objects for an active workcell configuration.

  This class is responsible for initializing, maintaining, and shutting down
  PyLabRobot machine and resource instances based on database definitions.
  It also provides functionality to interact with the live deck state.
  """

  def __init__(self, db_session: Optional[AsyncSession] = None):
    """Initialize the WorkcellRuntime.

    Args:
      db_session (Optional[AsyncSession]): An optional SQLAlchemy async session
        for database interactions.

    """
    self.db_session = db_session
    self._active_machines: Dict[int, Machine] = {}
    self._active_resources: Dict[int, Resource] = {}
    self._active_decks: Dict[int, Deck] = {}
    self._last_initialized_deck_object: Optional[Deck] = None
    self._last_initialized_deck_orm_id: Optional[int] = None
    logger.info("WorkcellRuntime initialized with db_session: %s", db_session)

  @check_db_session
  async def initialize_machine(self, machine_orm: MachineOrm) -> Optional[Any]:
    """Initialize and connects to a machine's PyLabRobot machine/resource.

    Args:
      machine_orm (MachineOrm): The ORM object representing the machine to
        initialize.

    Returns:
      Optional[Any]: The initialized PyLabRobot machine instance, or None if
      initialization fails.

    """
    if not hasattr(machine_orm, "id") or machine_orm.id is None:
      logger.error(
        "WorkcellRuntime: Invalid machine_orm object passed to initialize_machine"
        " (no id)."
      )
      return None
    if machine_orm.id in self._active_machines:
      return self._active_machines[machine_orm.id]

    logger.info(
      "WorkcellRuntime: Initializing machine '%s' (ID: %d) using class '%s'.",
      machine_orm.user_friendly_name,
      machine_orm.id,
      machine_orm.pylabrobot_class_name,
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
          "WorkcellRuntime: 'name' in machine_config for %s differs. Using"
          " user_friendly_name.",
          instance_name,
        )
        init_params["name"] = instance_name

      valid_init_params = {k: v for k, v in init_params.items() if k in sig.parameters}
      extra_params = {k: v for k, v in init_params.items() if k not in sig.parameters}
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
          "WorkcellRuntime: Extra parameters in machine_config for %s not"
          " accepted by %s.__init__: %s",
          instance_name,
          TargetClass.__name__,
          extra_params.keys(),
        )

      machine_instance = TargetClass(**valid_init_params)

      if (
        hasattr(machine_instance, "setup")
        and isinstance(machine_instance.setup, Awaitable)
        and isinstance(machine_instance.setup, Callable)
      ):
        logger.info(
          "WorkcellRuntime: Calling setup() for '%s'...",
          machine_orm.user_friendly_name,
        )
        try:
          await machine_instance.setup()
        except Exception as e:
          logger.error(
            "WorkcellRuntime: Failed to call setup() for '%s': %s",
            machine_orm.user_friendly_name,
            e,
          )
          raise WorkcellRuntimeError(
            f"Machine '{machine_orm.user_friendly_name}' setup failed:"
            f" {str(e)[:250]}"
          ) from e
      else:
        logger.info(
          "WorkcellRuntime: No setup() method for '%s'.",
          machine_orm.user_friendly_name,
        )
        pass  # Some PLR Machines might not have `setup`.

      self._active_machines[machine_orm.id] = machine_instance
      logger.info(
        "WorkcellRuntime: Machine for '%s' initialized: %s",
        machine_orm.user_friendly_name,
        type(machine_instance).__name__,
      )

      if self.db_session is not None:
        await svc.update_machine_status(
          self.db_session,
          machine_orm.id,
          MachineStatusEnum.AVAILABLE,
          "Machine initialized.",
        )

      return machine_instance
    except Exception as e:
      logger.error(
        "WorkcellRuntime: Failed to initialize machine for '%s' using class"
        " '%s': %s",
        machine_orm.user_friendly_name,
        machine_orm.pylabrobot_class_name,
        e,
      )
      traceback.print_exc()
      if (
        self.db_session is not None
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

  @check_db_session
  async def create_or_get_resource(
    self, resource_instance_orm: ResourceInstanceOrm, resource_definition_fqn: str
  ) -> Optional[Resource]:
    """Create or retrieve a live PyLabRobot resource object.

    Args:
      resource_instance_orm (ResourceInstanceOrm): The ORM object representing
        the resource instance.
      resource_definition_fqn (str): The fully qualified Python name of the
        PyLabRobot resource class.

    Returns:
      Optional[Resource]: The live PyLabRobot resource object, or None if
      creation fails.

    """
    if not hasattr(resource_instance_orm, "id") or resource_instance_orm.id is None:
      logger.error("WorkcellRuntime: Invalid resource_instance_orm passed (no id).")
      return None
    if resource_instance_orm.id in self._active_resources:
      return self._active_resources[resource_instance_orm.id]

    logger.info(
      "Creating PLR resource '%s' (ID: %d) using definition FQN '%s'.",
      resource_instance_orm.user_assigned_name,
      resource_instance_orm.id,
      resource_definition_fqn,
    )
    try:
      ResourceClass = _get_class_from_fqn(resource_definition_fqn)
      resource = ResourceClass(name=resource_instance_orm.user_assigned_name)
      self._active_resources[resource_instance_orm.id] = resource
      logger.info(
        "PLR resource for '%s' created: %s",
        resource_instance_orm.user_assigned_name,
        type(resource).__name__,
      )
      return resource
    except Exception as e:
      error_message = (
        f"Failed to create PLR resource for '{resource_instance_orm.user_assigned_name}'"
        f" using FQN '{resource_definition_fqn}': {str(e)[:250]}"
      )
      logger.error("WorkcellRuntime: %s", error_message)
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
            "WorkcellRuntime: Failed to update ResourceInstance ID %d status to"
            " ERROR in DB: %s",
            resource_instance_orm.id,
            db_error,
          )
      return None

  def get_active_machine(self, machine_orm_id: int) -> Optional[Any]:
    """Retrieve an active PyLabRobot machine instance by its ORM ID.

    Args:
      machine_orm_id (int): The ID of the machine ORM object.

    Returns:
      Optional[Any]: The active PyLabRobot machine instance, or None if not found.

    """
    return self._active_machines.get(machine_orm_id)

  def get_active_deck(self, deck_orm_id: int) -> Optional[Deck]:
    """Retrieve an active PyLabRobot Deck instance by its ORM ID.

    Args:
      deck_orm_id (int): The ID of the deck ORM object.

    Returns:
      Optional[Deck]: The active PyLabRobot Deck instance, or None if not found.

    """
    return self._active_decks.get(deck_orm_id)

  @check_db_session
  async def shutdown_machine(self, machine_orm_id: int):
    """Shut down and removes a live PyLabRobot machine instance.

    Args:
      machine_orm_id (int): The ID of the machine ORM object to shut down.

    """
    machine_instance = self._active_machines.pop(machine_orm_id, None)
    if machine_instance:
      try:
        logger.info(
          "WorkcellRuntime: Shutting down machine for machine ID: %d...",
          machine_orm_id,
        )
        if (
          hasattr(machine_instance, "stop")
          and isinstance(machine_instance.stop, Awaitable)
          and isinstance(machine_instance.stop, Callable)
        ):
          logger.info(
            "WorkcellRuntime: Calling stop() for machine ID %d...", machine_orm_id
          )
          await machine_instance.stop()
        else:
          logger.warning(
            "WorkcellRuntime: No stop() method for machine ID %d that is callable"
            " and awaitable.",
            machine_orm_id,
          )
          pass  # If a machine instance does not have a stop method, it proceeds.

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
          "WorkcellRuntime: Exception during shutdown for machine ID %d: %s",
          machine_orm_id,
          e,
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
        "WorkcellRuntime: No active machine found for machine ID %d.", machine_orm_id
      )
      if self.db_session and svc:
        await svc.update_machine_status(
          self.db_session,
          machine_orm_id,
          MachineStatusEnum.OFFLINE,
          "Machine not found for shutdown.",
        )

  def get_active_resource(self, resource_instance_orm_id: int) -> Optional[Resource]:
    """Retrieve an active PyLabRobot resource object by its ORM ID.

    Args:
      resource_instance_orm_id (int): The ID of the resource instance ORM object.

    Returns:
      Optional[Resource]: The active PyLabRobot resource object, or None if not found.

    """
    return self._active_resources.get(resource_instance_orm_id)

  async def assign_resource_to_deck(
    self,
    parent_machine_orm_id: int,
    resource: Resource,
    resource_instance_orm_id: int,
    location: Optional[Coordinate | tuple[float, float, float]] = None,
    pose_id: Optional[str | int] = None,
  ):
    """Assign a live PyLabRobot resource to a specific location or pose on a deck.

    Args:
      parent_machine_orm_id (int): The ORM ID of the parent machine.
      resource (Resource): The PyLabRobot resource object to assign.
      resource_instance_orm_id (int): The ORM ID of the resource instance.
      location (Optional[Union[Coordinate, Tuple[float, float, float]]]): The
        coordinates to assign the resource to.
      pose_id (Optional[Union[str, int]]): The identifier of the pose to
        assign the resource to.

    Raises:
      WorkcellRuntimeError: If neither location nor pose_id is provided,
        the deck machine is not active, the machine is not a Deck instance,
        or if there's an error during assignment.

    """
    if location is None and pose_id is None:
      raise WorkcellRuntimeError(
        "Either 'location' or 'pose_id' must be provided to assign a resource"
        " to a deck."
      )
    if not isinstance(resource, Resource):
      error_message = (
        f"Resource instance ID {resource_instance_orm_id} is not a valid"
        f" PyLabRobot Resource object. Type is {type(resource)}."
      )
      logger.error(error_message)
      raise WorkcellRuntimeError(error_message)
    if self.db_session is None or svc is None:
      error_message = (
        "Database session or asset_data_service not available for resource"
        " assignment."
      )
      logger.error(error_message)
      raise WorkcellRuntimeError(error_message)
    target_deck_parent_orm = await svc.get_machine_by_id(
      self.db_session, parent_machine_orm_id
    )
    if not target_deck_parent_orm:
      error_message = (
        f"Parent machine with ID {parent_machine_orm_id} not found in database."
      )
      logger.error(error_message)
      raise WorkcellRuntimeError(error_message)
    if target_deck_parent_orm.deck_type_definition_id is None:
      error_message = (
        f"Parent machine ID {parent_machine_orm_id} is not a deck machine."
      )
      logger.error(error_message)
      raise WorkcellRuntimeError(error_message)
    deck_type_definition_orm = await svc.get_deck_type_definition_by_id(
      self.db_session, target_deck_parent_orm.deck_type_definition_id
    )
    if not deck_type_definition_orm:
      error_message = (
        f"Deck type definition for parent machine ID {parent_machine_orm_id}"
        " not found in database."
      )
      logger.error(error_message)
      raise WorkcellRuntimeError(error_message)

    pose_method_name = deck_type_definition_orm.pose_to_location_method_name
    deck_orm = await svc.get_deck_by_parent_machine_id(
      self.db_session, parent_machine_orm_id
    )

    if pose_method_name is None:
      error_message = (
        f"Deck type definition for parent machine ID {parent_machine_orm_id}"
        " does not specify a pose (slot, rails) to location method name."
      )
      logger.error(error_message)
      raise WorkcellRuntimeError(error_message)

    if not deck_orm:
      error_message = (
        f"Deck machine with parent machine ID {parent_machine_orm_id} not found"
        " in database."
      )
      logger.error(error_message)
      raise WorkcellRuntimeError(error_message)

    target_deck = self.get_active_deck(deck_orm.id)
    pose_method = getattr(target_deck, pose_method_name, None)
    if target_deck is None:
      error_message = f"Deck machine ID {deck_orm.id} is not an active machine."
      logger.error(error_message)
      raise WorkcellRuntimeError(error_message)
    if not isinstance(target_deck, Deck):
      error_message = f"Device ID {deck_orm.id} (name: "
      f"{getattr(target_deck, 'name', 'N/A')}) is not a Deck instance. "
      f"Type is {type(target_deck)}."
      logger.error(error_message)
      raise WorkcellRuntimeError(error_message)
    if pose_method is None or not callable(pose_method):
      error_message = (
        f"Deck type definition for parent machine ID {parent_machine_orm_id}"
        f" does not have a valid pose method '{pose_method_name}' on deck ID"
        f" {deck_orm.id}."
      )
      logger.error(error_message)
      raise WorkcellRuntimeError(error_message)

    deck_parent = target_deck.parent
    if deck_parent is None:
      error_message = (
        f"Deck ID {deck_orm.id} has no parent machine. Cannot assign resource."
      )
      logger.error(error_message)
      raise WorkcellRuntimeError(error_message)

    try:
      if pose_id is not None:
        target_deck.assign_child_resource(
          resource=resource, location=pose_method(pose_id)
        )
        if self.db_session and svc:
          await svc.update_resource_instance_location_and_status(
            self.db_session,
            resource_instance_orm_id,
            ResourceInstanceStatusEnum.AVAILABLE_ON_DECK,
            location_machine_id=deck_orm.id,
            current_deck_pose_name=str(pose_id),
          )
    except Exception as e:
      traceback.print_exc()
      raise WorkcellRuntimeError(
        f"Error assigning resource '{resource.name}' to pose '{pose_id}' on"
        f" deck ID {deck_orm_id}: {e}"
      ) from e

  async def clear_deck_pose(
    self,
    deck_machine_orm_id: int,
    pose_name: str,
    resource_instance_orm_id: Optional[int] = None,
  ):
    """Clears a resource from a specific pose on a live deck.

    Args:
      deck_machine_orm_id (int): The ORM ID of the deck machine.
      pose_name (str): The name of the pose to clear.
      resource_instance_orm_id (Optional[int]): The ORM ID of the resource
        instance that was in the pose, if known. Used for updating DB status.

    Raises:
      WorkcellRuntimeError: If the deck machine is not active, not a Deck
        instance, or if there's an error during unassignment.
    """
    deck_plr_obj = self.get_active_machine(deck_machine_orm_id)
    if not deck_plr_obj:
      raise WorkcellRuntimeError(
        f"Deck machine ID {deck_machine_orm_id} is not an active machine."
      )
    if not isinstance(deck_plr_obj, Deck):
      raise WorkcellRuntimeError(
        f"Device ID {deck_machine_orm_id} "
        f"(name: {getattr(deck_plr_obj, 'name', 'N/A')}) is not a Deck instance. "
        f"Type is {type(deck_plr_obj)}."
      )
    try:
      resource_in_pose = deck_plr_obj.get_resource(pose_name)
      if resource_in_pose:
        deck_plr_obj.unassign_child_resource(resource_in_pose)
      else:
        logger.warning(
          "No specific resource found in pose '%s' on deck ID %d to unassign."
          " Assuming pose is already clear or unassignment by name is sufficient.",
          pose_name,
          deck_machine_orm_id,
        )

      if resource_instance_orm_id and self.db_session and svc:
        await svc.update_resource_instance_location_and_status(
          self.db_session,
          resource_instance_orm_id,
          ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
          location_machine_id=None,
          current_deck_pose_name=None,
        )
    except Exception as e:
      traceback.print_exc()
      raise WorkcellRuntimeError(
        f"Error clearing deck pose '{pose_name}' on deck ID"
        f" {deck_machine_orm_id}: {e}"
      ) from e

  def execute_machine_action(
    self,
    machine_orm_id: int,
    action_name: str,
    params: Optional[Dict[str, Any]] = None,
  ) -> Any:
    """Executes a method/action on a live PyLabRobot machine instance.

    Args:
      machine_orm_id (int): The ORM ID of the machine to interact with.
      action_name (str): The name of the method to call on the machine object.
      params (Optional[Dict[str, Any]]): A dictionary of parameters to pass
        to the method.

    Returns:
      Any: The result of the executed action.

    Raises:
      WorkcellRuntimeError: If the machine is not active or if an error occurs
        during action execution.
      AttributeError: If the specified action name does not exist on the machine.
    """
    machine = self.get_active_machine(machine_orm_id)
    if not machine:
      raise WorkcellRuntimeError("Device ID %d machine not active.", machine_orm_id)
    if hasattr(machine, action_name) and callable(getattr(machine, action_name)):
      try:
        return getattr(machine, action_name)(**(params or {}))
      except Exception as e:
        traceback.print_exc()
        raise WorkcellRuntimeError(
          f"Error executing action '{action_name}' on machine ID"
          f" {machine_orm_id}: {e}"
        ) from e
    else:
      raise AttributeError(
        f"Device machine for ID {machine_orm_id} (type: {type(machine).__name__})"
        f" has no action '{action_name}'."
      )

  async def shutdown_all_machines(self):
    """Shuts down all currently active PyLabRobot machine instances."""
    logger.info("WorkcellRuntime: Shutting down all active machines...")
    for machine_id in list(self._active_machines.keys()):
      await self.shutdown_machine(machine_id)
    logger.info("WorkcellRuntime: All active machines processed for shutdown.")

  async def get_deck_plr_object(self, deck_machine_orm_id: int) -> Optional[Deck]:
    """Retrieves a specific live PyLabRobot Deck object by its ORM ID.

    This method prioritizes getting an already active deck. If not active,
    it attempts to initialize it.

    Args:
      deck_machine_orm_id (int): The ORM ID of the deck machine.

    Returns:
      Optional[Deck]: The live PyLabRobot Deck object, or None if it cannot
      be retrieved or initialized as a Deck.
    """
    deck_machine = self.get_active_machine(deck_machine_orm_id)
    if deck_machine and isinstance(deck_machine, Deck):
      return deck_machine

    if self.db_session and svc:
      deck_orm = await svc.get_machine_by_id(self.db_session, deck_machine_orm_id)
      if deck_orm and deck_orm.praxis_machine_category == MachineCategoryEnum.DECK:
        initialized_deck = await self.initialize_machine(deck_orm)
        if isinstance(initialized_deck, Deck):
          self._last_initialized_deck_object = initialized_deck
          self._last_initialized_deck_orm_id = deck_machine_orm_id
          return initialized_deck
    return None

  async def get_deck_state_representation(
    self, deck_machine_orm_id: int
  ) -> Dict[str, Any]:
    """Constructs a dictionary representing the state of a specific deck.

    This representation is suitable for serialization into `DeckStateResponse`.
    It uses a database-first approach for resources located on the deck.

    Args:
      deck_machine_orm_id (int): The ORM ID of the deck machine.

    Returns:
      Dict[str, Any]: A dictionary representing the deck's current state.

    Raises:
      WorkcellRuntimeError: If the database session or service is unavailable,
        the deck machine is not found in the database, or the machine is not
        categorized as a DECK.
    """

    if not self.db_session or not svc:
      raise WorkcellRuntimeError(
        "Database session or asset_data_service not available."
      )

    deck_orm = await svc.get_machine_by_id(self.db_session, deck_machine_orm_id)
    if not deck_orm:
      raise WorkcellRuntimeError(
        "Deck machine with ID %d not found in database.", deck_machine_orm_id
      )
    if deck_orm.praxis_machine_category != ResourceCategoryEnum.DECK:
      raise WorkcellRuntimeError(
        "Device ID %d (Name: %s) is not categorized as a DECK (Category: %s).",
        deck_machine_orm_id,
        deck_orm.user_friendly_name,
        deck_orm.praxis_machine_category,
      )

    response_poses: List[Dict[str, Any]] = []

    resources_on_deck = await svc.list_resource_instances(
      db=self.db_session,
      location_machine_id=deck_machine_orm_id,
    )

    for lw_instance in resources_on_deck:
      if lw_instance.current_deck_pose_name:
        if (
          not hasattr(lw_instance, "resource_definition")
          or not lw_instance.resource_definition
        ):
          logger.warning(
            "Resource instance ID %d is missing resource_definition relationship."
            " Skipping.",
            lw_instance.id,
          )
          continue
        lw_def = lw_instance.resource_definition

        resource_info_data = {
          "resource_instance_id": lw_instance.id,
          "user_assigned_name": (
            lw_instance.user_assigned_name or f"Resource_{lw_instance.id}"
          ),
          "pylabrobot_definition_name": lw_def.pylabrobot_definition_name,
          "python_fqn": lw_def.python_fqn,
          "category": (str(lw_def.plr_category.value) if lw_def.plr_category else None),
          "size_x_mm": lw_def.size_x_mm,
          "size_y_mm": lw_def.size_y_mm,
          "size_z_mm": lw_def.size_z_mm,
          "nominal_volume_ul": lw_def.nominal_volume_ul,
          "properties_json": lw_instance.properties_json,
          "model": lw_def.model,
        }
        pose_info_data = {
          "name": lw_instance.current_deck_pose_name,
          # Placeholder for coordinates, as they are not directly in ORM
          # and require a live PLR Deck object to compute.
          "x_coordinate": None,
          "y_coordinate": None,
          "z_coordinate": None,
          "labware": resource_info_data,
        }
        response_poses.append(pose_info_data)

    deck_size_x = None
    deck_size_y = None
    deck_size_z = None

    live_deck = await self.get_deck_plr_object(deck_machine_orm_id)
    if live_deck and hasattr(live_deck, "get_size"):
      try:
        deck_size_tuple = live_deck.get_size()  # Assuming (x,y,z)
        deck_size_x, deck_size_y, deck_size_z = deck_size_tuple
        logger.debug(
          "Retrieved live deck dimensions for ID %d: %s",
          deck_machine_orm_id,
          deck_size_tuple,
        )
      except Exception as e:
        logger.warning(
          "Could not get size from live deck object for ID %d: %s",
          deck_machine_orm_id,
          e,
        )

    deck_state_data = {
      "deck_id": deck_orm.id,
      "user_friendly_name": deck_orm.user_friendly_name or f"Deck_{deck_orm.id}",
      "pylabrobot_class_name": deck_orm.pylabrobot_class_name,
      "size_x_mm": deck_size_x,
      "size_y_mm": deck_size_y,
      "size_z_mm": deck_size_z,
      "poses": response_poses,
    }
    return deck_state_data

  async def get_last_initialized_deck_object(self) -> Optional[Deck]:
    """Return the Deck most recently initialized by this runtime instance."""
    if self._last_initialized_deck_object:
      return self._last_initialized_deck_object
    return None

  # TODO: WCR-7: Add methods for loading/applying full DeckConfigurationOrm to
  # the live deck. This would involve:
  # - Clearing all existing resource from the live deck (if any).
  # - Iterating through DeckPoseOrm entries in the DeckConfigurationOrm.
  # - For each pose with assigned resource:
  #   - Get/create the PlrResource for the ResourceInstanceOrm.
  #   - Call assign_resource_to_deck_pose with the target deck's ORM ID.
  # - This would be the primary way to set up a live deck to match a saved
  # configuration.
