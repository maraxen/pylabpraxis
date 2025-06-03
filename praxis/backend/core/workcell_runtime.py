# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, traceback-print
"""Workcell Runtime Management.

praxis/core/workcell_runtime.py

The WorkcellRuntime manages live PyLabRobot objects (machines, resources)
for an active workcell configuration. It translates database-defined assets
into operational PyLabRobot instances.
"""

import importlib
import inspect
import logging
import traceback
import warnings
from functools import partial, wraps
from typing import (
  Any,
  Awaitable,
  Callable,
  Dict,
  List,
  Literal,
  Optional,
  Type,
  Union,
  cast,
)

from pylabrobot.liquid_handling.liquid_handler import LiquidHandler
from pylabrobot.machines import Machine
from pylabrobot.resources import Coordinate, Deck, Resource
from sqlalchemy.ext.asyncio import AsyncSession

import praxis.backend.services as svc
from praxis.backend.models import (
  DeckTypeDefinitionBase,
  DeckTypeDefinitionOrm,
  MachineCategoryEnum,
  MachineOrm,
  MachineStatusEnum,
  PositioningConfig,
  ResourceCategoryEnum,
  ResourceDefinitionCatalogOrm,
  ResourceInstanceOrm,
  ResourceInstanceStatusEnum,
)
from praxis.backend.utils.errors import WorkcellRuntimeError, log_async_runtime_errors

logger = logging.getLogger(__name__)

log_workcell_runtime_errors = partial(
  log_async_runtime_errors,
  logger_instance=logger,
  raises=True,
  raises_exception=WorkcellRuntimeError,
)


def _get_class_from_fqn(class_fqn: str) -> Type:
  """Import and return a class dynamically from its fully qualified name."""
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

  def __init__(self, db_session: AsyncSession):
    """Initialize the WorkcellRuntime.

    Args:
      db_session (AsyncSession): A SQLAlchemy async session for database interactions.

    """
    self.db_session = db_session
    self._active_machines: Dict[int, Machine] = {}
    self._active_resources: Dict[int, Resource] = {}
    self._active_decks: Dict[int, Deck] = {}
    self._last_initialized_deck_object: Optional[Deck] = None
    self._last_initialized_deck_orm_id: Optional[int] = None
    logger.info("WorkcellRuntime initialized with db_session: %s", db_session)

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error encountered calculating location from deck position",
    suffix=" - Ensure the deck type definition exists in the database.",
  )
  async def _get_calculated_location(
    self,
    target_deck: Deck,
    deck_type_definition_id: int,
    position_id: Union[str, int],
    positioning_config: Optional[PositioningConfig],
  ) -> Coordinate:
    """Calculate the PyLabRobot Coordinate for a given position_id.

    Based on the deck's positioning configuration or predefined positions, returns the
    corresponding PyLabRobot Coordinate for the position_id on the target deck.
    Different Deck subclasses have different human interpretable position descriptions
    (e.g., "A1", "B2", "C3", etc. for slots, or 1,2,3, etc. for rails), this allows
    for easy interoperability and informing users of how to set-up a deck.


    Args:
        target_deck (Deck): The live PyLabRobot Deck object.
        deck_type_definition_id (int): The ID of the associated DeckTypeDefinition.
        position_id (Union[str, int]): The human-interpretable identifier for the
        position.
        positioning_config (Optional[PositioningConfig]): The general positioning
            configuration for the deck type.

    Returns:
        Coordinate: The calculated PyLabRobot Coordinate.

    Raises:
        WorkcellRuntimeError: If the location cannot be determined.
        TypeError: If the position_id is not a valid type for the method.

    """
    if positioning_config is None:
      logger.info(
        f"No general positioning config for deck type ID {deck_type_definition_id},"
        " attempting to find position in DeckPositionDefinitionOrm."
      )
      if isinstance(position_id, (str, int)):
        if self.db_session is not None:
          all_deck_position_definitions = (
            await svc.get_position_definitions_for_deck_type(
              self.db_session, deck_type_definition_id
            )
          )
          found_position_def = next(
            (
              p
              for p in all_deck_position_definitions
              if p.position_id == str(position_id) or p.position_id == int(position_id)
            ),
            None,
          )
          if (
            found_position_def
            and found_position_def.nominal_x_mm is not None
            and found_position_def.nominal_y_mm is not None
          ):
            return Coordinate(
              x=found_position_def.nominal_x_mm,
              y=found_position_def.nominal_y_mm,
              z=found_position_def.nominal_z_mm
              if found_position_def.nominal_z_mm is not None
              else 0.0,
            )
          else:
            raise WorkcellRuntimeError(
              f"Position '{position_id}' not found in predefined deck position "
              f"definitions for deck type ID {deck_type_definition_id}."
            )
        else:
          raise TypeError(
            f"Position ID for deck type ID {deck_type_definition_id} must be a string "
            f"or integer for direct lookup."
          )
      else:
        raise WorkcellRuntimeError(
          f"No positioning configuration provided for deck type ID "
          f"{deck_type_definition_id}. Cannot determine position location."
        )
    else:
      method_name = positioning_config.method_name
      arg_name = positioning_config.arg_name
      arg_type = positioning_config.arg_type
      method_params = positioning_config.params or {}

      position_method = getattr(target_deck, method_name, None)
      if position_method is None or not callable(position_method):
        raise WorkcellRuntimeError(
          f"Deck does not have a valid position method '{method_name}' as configured."
        )

      converted_position_arg: Union[str, int]
      if arg_type == "int":
        try:
          converted_position_arg = int(position_id)
        except (ValueError, TypeError) as e:
          raise TypeError(
            f"Expected integer for position_id '{position_id}' for method "
            f"'{method_name}' but got invalid type/value: {e}"
          ) from e
      else:
        converted_position_arg = str(position_id)

      try:
        sig = inspect.signature(position_method)
        bound_args = sig.bind_partial(**method_params)
        bound_args.arguments[arg_name] = converted_position_arg
        bound_args.apply_defaults()
        calculated_location = position_method(*bound_args.args, **bound_args.kwargs)

      except TypeError as e:
        raise WorkcellRuntimeError(
          f"Error calling PLR method '{method_name}' with arguments "
          f"'{arg_name}={converted_position_arg}' and params '{method_params}': {e}. "
          "Check if method signature matches configuration."
        ) from e
      except Exception as e:
        raise WorkcellRuntimeError(
          f"Unexpected error when calling PLR method '{method_name}': {e}"
        ) from e

      # Ensure the calculated location is a PyLabRobot Coordinate object
      if not isinstance(calculated_location, Coordinate):
        if isinstance(calculated_location, tuple) and len(calculated_location) == 3:
          calculated_location = Coordinate(
            x=calculated_location[0], y=calculated_location[1], z=calculated_location[2]
          )
        else:
          raise TypeError(
            f"Expected PLR method '{method_name}' to return a Coordinate or (x,y,z) "
            f"tuple, but got {type(calculated_location)}: {calculated_location}"
          )
      return calculated_location

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error initializing machine",
    suffix=" - Ensure the machine ORM is valid, the class, and machine is connected.",
  )
  async def initialize_machine(self, machine_orm: MachineOrm) -> Machine:
    """Initialize and connects to a machine's PyLabRobot machine/resource.

    Args:
      machine_orm (MachineOrm): The ORM representing the machine to
        initialize.

    Raises:
      WorkcellRuntimeError: If the machine ORM is invalid, or if the machine
        initialization fails.
      ValueError: If the machine ORM does not have a valid ID.
      TypeError: If the initialized machine is not a valid PyLabRobot Machine instance.

    Returns:
      Machine: The initialized PyLabRobot machine instance.
          If the machine already exists in _active_machines, it returns that instance.

    """
    if not hasattr(machine_orm, "id") or machine_orm.id is None:
      raise WorkcellRuntimeError(
        "Invalid machine_orm object passed to initialize_machine" " (no id)."
      )

    if machine_orm.id in self._active_machines:
      return self._active_machines[machine_orm.id]

    logger.info(
      "WorkcellRuntime: Initializing machine '%s' (ID: %d) using class '%s'.",
      machine_orm.user_friendly_name,
      machine_orm.id,
      machine_orm.python_fqn,
    )

    try:
      TargetClass = _get_class_from_fqn(machine_orm.python_fqn)
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

      if not isinstance(machine_instance, Machine):
        raise TypeError(
          f"Machine '{machine_orm.user_friendly_name}' initialized, but it is not a"
          f" valid PyLabRobot Machine instance. Type is {type(machine_instance)}."
        )

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
          error_message = (
            f"Failed to call setup() for machine '{machine_orm.user_friendly_name}':"
            f" {str(e)[:250]}"
          )
          raise WorkcellRuntimeError(error_message)
      else:
        raise WorkcellRuntimeError(
          f"Machine '{machine_orm.user_friendly_name}' does not have a valid"
          " setup() method that is callable and awaitable."
        )

      self._active_machines[machine_orm.id] = machine_instance

      logger.info(
        "WorkcellRuntime: Machine for '%s' initialized: %s",
        machine_orm.user_friendly_name,
        type(machine_instance).__name__,
      )

      if hasattr(machine_instance, "deck") and isinstance(
        getattr(machine_instance, "deck"), Deck
      ):
        machine_deck: Deck = getattr(machine_instance, "deck")
        if not isinstance(machine_deck, Deck):
          raise TypeError(
            f"Machine '{machine_orm.user_friendly_name}' has a 'deck' attribute, "
            f"but it is not a Deck instance. Type is {type(machine_deck)}."
          )

        deck_orm_entry = await svc.get_deck_by_parent_machine_id(
          self.db_session, machine_orm.id
        )

        if deck_orm_entry and deck_orm_entry.id is not None:
          self._active_decks[deck_orm_entry.id] = machine_deck
          self._last_initialized_deck_object = machine_deck
          self._last_initialized_deck_orm_id = deck_orm_entry.id
          logger.info(
            "Registered deck (DeckOrm ID: %d, PLR name: '%s') from machine '%s' \
              (ID: %d) to active decks.",
            deck_orm_entry.id,
            machine_deck.name,
            machine_orm.user_friendly_name,
            machine_orm.id,
          )
        else:
          logger.warning(
            "Machine '%s' (ID: %d) has a .deck attribute, but no corresponding DeckOrm \
              entry found with parent_machine_id=%d. Deck not registered in \
                _active_decks.",
            machine_orm.user_friendly_name,
            machine_orm.id,
            machine_orm.id,
          )

      await svc.update_machine_status(
        self.db_session,
        machine_orm.id,
        MachineStatusEnum.AVAILABLE,
        "Machine initialized successfully.",
      )
      return machine_instance
    except Exception as e:
      error_message = f"Failed to initialize machine '{machine_orm.user_friendly_name}'\
        (ID: {machine_orm.id}) using class '{machine_orm.python_fqn}': \
          {str(e)[:250]}"
      await svc.update_machine_status(
        self.db_session,
        machine_orm.id,
        MachineStatusEnum.ERROR,
        f"Machine init failed: {str(e)[:250]}",
      )
      raise WorkcellRuntimeError(error_message) from e

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error creating or getting resource",
    suffix=" - Ensure the resource instance ORM and definition FQN are valid.",
  )
  async def create_or_get_resource(
    self, resource_instance_orm: ResourceInstanceOrm, resource_definition_fqn: str
  ) -> Resource:
    """Create or retrieve a live PyLabRobot resource object.

    Args:
      resource_instance_orm (ResourceInstanceOrm): The ORM object representing
        the resource instance.
      resource_definition_fqn (str): The fully qualified Python name of the
        PyLabRobot resource class.

    Raises:
      ValueError: If the resource_instance_orm does not have a valid ID.
      WorkcellRuntimeError: If the resource creation fails or if the resource
        instance ORM is invalid.

    Returns:
      Resource: The live PyLabRobot resource object.

    """
    if not hasattr(resource_instance_orm, "id") or resource_instance_orm.id is None:
      raise ValueError(
        "Invalid resource_instance_orm object passed to create_or_get_resource"
        " (no id)."
      )

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
        f"Failed to create PLR resource for '{resource_instance_orm.user_assigned_name}"
        f"' using FQN '{resource_definition_fqn}': {str(e)[:250]}"
      )
      if hasattr(resource_instance_orm, "id") and resource_instance_orm.id is not None:
        try:
          await svc.update_resource_instance_location_and_status(
            self.db_session,
            resource_instance_id=resource_instance_orm.id,
            new_status=ResourceInstanceStatusEnum.ERROR,
            status_details=error_message,
          )
        except Exception as db_error:  # pragma: no cover
          error_message += (
            f" Failed to update resource instance ID {resource_instance_orm.id} status"
            f" to ERROR in DB: {str(db_error)[:250]}"
          )
          raise WorkcellRuntimeError(error_message) from db_error
      raise WorkcellRuntimeError(error_message) from e

  def get_active_machine(self, machine_orm_id: int) -> Optional[Machine]:
    """Retrieve an active PyLabRobot machine instance by its ORM ID.

    Args:
      machine_orm_id (int): The ID of the machine ORM object.

    Returns:
      Optional[Machine]: The active PyLabRobot machine instance, or None if not found.

    """
    return self._active_machines.get(machine_orm_id)

  def get_active_machine_id(self, machine: Machine) -> Optional[int]:
    """Retrieve the ORM ID of an active PyLabRobot machine instance.

    Args:
      machine (Machine): The PyLabRobot Machine instance.

    Returns:
      Optional[int]: The ORM ID of the machine, or None if not found in active machines.

    """
    for orm_id, active_machine in self._active_machines.items():
      if active_machine is machine:
        return orm_id
    return None

  def get_active_deck_id(self, deck: Deck) -> Optional[int]:
    """Retrieve the ORM ID of an active PyLabRobot Deck instance.

    Args:
      deck (Deck): The PyLabRobot Deck instance.

    Returns:
      Optional[int]: The ORM ID of the deck, or None if not found in active decks.

    """
    for orm_id, active_deck in self._active_decks.items():
      if active_deck is deck:
        return orm_id
    return None

  def get_active_resource_id(self, resource: Resource) -> Optional[int]:
    """Retrieve the ORM ID of an active PyLabRobot resource object.

    Args:
      resource (Resource): The PyLabRobot Resource instance.

    Returns:
      Optional[int]: The ORM ID of the resource, or None if not found in active
      resources.

    """
    for orm_id, active_resource in self._active_resources.items():
      if active_resource is resource:
        return orm_id
    return None

  def get_active_deck(self, deck_orm_id: int) -> Optional[Deck]:
    """Retrieve an active PyLabRobot Deck instance by its ORM ID.

    Args:
      deck_orm_id (int): The ID of the deck ORM object.

    Returns:
      Optional[Deck]: The active PyLabRobot Deck instance, or None if not found.

    """
    return self._active_decks.get(deck_orm_id)

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error shutting down machine",
    suffix=" - Ensure the machine ORM ID is valid and the machine is active.",
  )
  async def shutdown_machine(self, machine_orm_id: int):
    """Shut down and removes a live PyLabRobot machine instance.

    Args:
      machine_orm_id (int): The ID of the machine ORM object to shut down.

    Raises:
      WorkcellRuntimeError: If the machine is not found, or if the shutdown fails.

    """
    machine_instance = self._active_machines.pop(machine_orm_id, None)
    try:
      if machine_instance is not None:
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
          raise WorkcellRuntimeError(f"No stop() method for \
            {machine_instance.__class__.__name__} machine {machine_orm_id} \
              that is callable and awaitable.")

        await svc.update_machine_status(
          self.db_session,
          machine_orm_id,
          MachineStatusEnum.OFFLINE,
          "Machine shut down.",
        )

      else:
        await svc.update_machine_status(
          self.db_session,
          machine_orm_id,
          MachineStatusEnum.OFFLINE,
          "Machine not found for shutdown.",
        )
        raise WorkcellRuntimeError(
          f"Machine with ID {machine_orm_id} is not currently active and is \
          unexpectedly offline."
        )

    except Exception as e:
      if machine_instance is None:
        raise WorkcellRuntimeError(
          f"No active machine instance found for machine ID {machine_orm_id}."
        ) from e
      self._active_machines[machine_orm_id] = machine_instance
      await svc.update_machine_status(
        self.db_session,
        machine_orm_id,
        MachineStatusEnum.ERROR,
        f"Shutdown failed: {str(e)[:250]}",
      )
      raise WorkcellRuntimeError(f"Error shutting down machine ID {machine_orm_id}: \
        {str(e)[:250]}") from e

  def get_active_resource(self, resource_instance_orm_id: int) -> Optional[Resource]:
    """Retrieve an active PyLabRobot resource object by its ORM ID.

    Args:
      resource_instance_orm_id (int): The ID of the resource instance ORM object.

    Returns:
      Optional[Resource]: The active PyLabRobot resource object, or None if not found.

    """
    return self._active_resources.get(resource_instance_orm_id)

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error assigning resource to deck",
    suffix=" - Ensure the resource and deck are valid and connected.",
  )
  async def assign_resource_to_deck(
    self,
    resource: Resource,
    resource_instance_orm_id: int,
    target: int | Machine | Deck,
    location: Optional[Union[Coordinate, tuple[float, float, float]]] = None,
    position_id: Optional[Union[str, int]] = None,
  ):
    """Assign a live Resource to a specific location or position on a deck.

    Args:
      resource (Resource): The PyLabRobot Resource instance to assign.
      resource_instance_orm_id (int): The ID of the resource instance ORM object.
      location (Optional[Union[Coordinate, tuple[float, float, float]]]): The
        explicit location coordinates on the deck.
      position_id (Optional[Union[str, int]]): The position ID on the deck.
      target (int | Machine | Deck): The target deck or machine ORM ID, or the
        live PyLabRobot Deck or Machine instance.


    Raises:
      WorkcellRuntimeError: If neither location nor position_id is provided, or if
        the resource is not a valid PyLabRobot Resource instance, or if the deck
        is not found or not active.
      TypeError: If the resource is not a valid PyLabRobot Resource instance.

    """
    if location is None and position_id is None:
      raise WorkcellRuntimeError(
        "Either 'location' or 'position_id' must be provided to assign a resource"
        " to a deck."
      )

    if not isinstance(resource, Resource):
      raise TypeError(f"Resource instance ID {resource_instance_orm_id} is not a valid \
        PyLabRobot Resource object. Type is {type(resource)}.")

    if isinstance(target, Machine):
      inferred_target_type = "Machine"
    elif isinstance(target, Deck):
      inferred_target_type = "Deck"
    elif isinstance(target, int):
      if target in self._active_machines.keys():
        inferred_target_type = "machine_orm_id"
      elif target in self._active_decks.keys():
        inferred_target_type = "deck_orm_id"
      else:
        raise WorkcellRuntimeError(
          f"Target ORM ID {target} not found in active machines or decks."
        )
    else:
      raise TypeError(
        f"Target must be a Machine, Deck, or ORM ID (int), but got {type(target)}."
      )

    match inferred_target_type:
      case "Machine":
        if not isinstance(target, Machine):
          raise TypeError(f"Target is a Machine instance, but type is {type(target)}.")
        parent_machine_orm_id = self.get_active_machine_id(target)
        if parent_machine_orm_id is None:
          raise WorkcellRuntimeError(
            f"Machine {target} is not an active machine with a valid ORM ID."
          )
        target_deck = getattr(target, "deck", None)
        if target_deck is None or not isinstance(target_deck, Deck):
          raise WorkcellRuntimeError(
            f"Machine ID {target} does not have an associated deck."
          )
        fetched_target = self.get_active_deck_id(target_deck)
        if fetched_target is None:
          raise WorkcellRuntimeError(
            f"Machine ID {target} is not an active machine with a valid deck."
          )
        deck_orm_id = fetched_target
      case "Deck":
        target_deck = target
        if not isinstance(target_deck, Deck):
          raise TypeError(
            f"Target is a Deck instance, but type is {type(target_deck)}."
          )
        deck_orm_id = self.get_active_deck_id(target_deck)
        if deck_orm_id is None:
          raise WorkcellRuntimeError(f"Deck {target_deck} is not an active deck.")
      case "deck_orm_id":
        deck_orm_id = cast(int, target)
        target_deck = self.get_active_deck(deck_orm_id)
        if target_deck is None:
          raise WorkcellRuntimeError(f"Deck ID {deck_orm_id} is not an active deck.")
      case "machine_orm_id":
        machine_orm_id = cast(int, target)
        target_machine = self.get_active_machine(machine_orm_id)
        if target_machine is None:
          raise WorkcellRuntimeError(
            f"Machine ID {machine_orm_id} is not an active machine."
          )
        target_deck = getattr(target_machine, "deck", None)
        if target_deck is None or not isinstance(target_deck, Deck):
          raise WorkcellRuntimeError(
            f"Machine ID {machine_orm_id} does not have an associated deck."
          )
        deck_orm_id = self.get_active_deck_id(target_deck)
      case _:
        raise WorkcellRuntimeError(
          f"Unexpected target type: {inferred_target_type}. Expected Machine, Deck, or \
            int ORM ID."
        )

    if deck_orm_id is None:
      raise WorkcellRuntimeError("Deck ORM ID could not be determined from the target.")

    deck_orm = await svc.get_deck_by_id(self.db_session, deck_orm_id)
    if deck_orm is None:
      raise WorkcellRuntimeError(f"Deck ORM ID {deck_orm_id} not found in database.")
    deck_orm_type_definition_id = deck_orm.deck_type_definition_id

    if deck_orm_type_definition_id is None:
      raise WorkcellRuntimeError(
        f"Deck ORM ID {deck_orm_id} does not have a valid deck type definition."
      )

    deck_type_definition_orm = await svc.get_deck_type_definition_by_id(
      self.db_session, deck_orm_type_definition_id
    )

    if deck_type_definition_orm is None:
      raise WorkcellRuntimeError(
        f"Deck type definition for deck ORM ID {deck_orm_id} not found in database."
      )

    positioning_config = PositioningConfig.model_validate(
      deck_type_definition_orm.positioning_config_json
    )

    final_location_for_plr: Coordinate
    if location is not None:
      # If explicit coordinates are provided, use them directly
      if isinstance(location, tuple):
        final_location_for_plr = Coordinate(x=location[0], y=location[1], z=location[2])
      else:
        final_location_for_plr = location
    elif position_id is not None:
      # Delegate position calculation to the helper function
      final_location_for_plr = await self._get_calculated_location(
        target_deck=target_deck,
        deck_type_definition_id=deck_type_definition_orm.id,
        position_id=position_id,
        positioning_config=positioning_config,
      )
    else:
      # This case should ideally be caught by the initial check, but for type safety.
      raise WorkcellRuntimeError(
        "Internal error: Neither location nor position_id provided after initial check."
      )

    try:
      target_deck.assign_child_resource(
        resource=resource, location=final_location_for_plr
      )
      await svc.update_resource_instance_location_and_status(
        self.db_session,
        resource_instance_orm_id,
        ResourceInstanceStatusEnum.AVAILABLE_ON_DECK,
        location_machine_id=deck_orm.id,
        current_deck_position_name=str(position_id),
      )
    except Exception as e:
      raise WorkcellRuntimeError(
        f"Error assigning resource '{resource.name}' to  "
        f"location {final_location_for_plr} on deck ID {deck_orm.id}: {str(e)[:250]}"
      ) from e

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error clearing deck position",
    suffix=" - Ensure the deck machine ORM ID and position name are valid.",
  )
  async def clear_deck_position(
    self,
    deck_machine_orm_id: int,
    position_name: str,
    resource_instance_orm_id: Optional[int] = None,
  ):
    """Clear a resource from a specific position on a live deck.

    Args:
      deck_machine_orm_id (int): The ORM ID of the deck machine.
      position_name (str): The name of the position to clear.
      resource_instance_orm_id (Optional[int]): The ORM ID of the resource
        instance that was in the position, if known. Used for updating DB status.

    Raises:
      WorkcellRuntimeError: If the deck machine is not active, not a Deck
        instance, or if there's an error during unassignment.

    """
    deck = self.get_active_deck(deck_machine_orm_id)

    if deck is None:
      raise WorkcellRuntimeError(
        f"Deck machine ID {deck_machine_orm_id} is not currently active."
      )

    if not isinstance(deck, Deck):
      raise WorkcellRuntimeError(
        "Deck from workcell runtime is not a Deck instance."
        "This indicates a major error as non-Deck objects"
        " should not be in the active decks."
      )
    logger.info(
      "WorkcellRuntime: Clearing position '%s' on deck ID %d.",
      position_name,
      deck_machine_orm_id,
    )

    resource_in_position = deck.get_resource(position_name)
    if resource_in_position:
      deck.unassign_child_resource(resource_in_position)
    else:
      logger.warning(
        "No specific resource found in position '%s' on deck ID %d to unassign."
        " Assuming position is already clear or unassignment by name is sufficient.",
        position_name,
        deck_machine_orm_id,
      )

    if resource_instance_orm_id:
      await svc.update_resource_instance_location_and_status(
        self.db_session,
        resource_instance_orm_id,
        ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
        location_machine_id=None,
        current_deck_position_name=None,
      )

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error executing machine action",
    suffix=" - Ensure the machine is active and the action exists.",
  )
  async def execute_machine_action(
    self,
    machine_orm_id: int,
    action_name: str,
    params: Optional[Dict[str, Any]] = None,
  ) -> Any:
    """Execute a method/action on a live PyLabRobot machine instance.

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
    if machine is None:
      raise WorkcellRuntimeError(
        f"WorkcellRuntime: Machine ID {machine_orm_id} machine not active."
      )

    if not isinstance(machine, Machine):
      raise WorkcellRuntimeError(
        f"WorkcellRuntime: Machine ID {machine_orm_id} is not a valid PyLabRobot"
        f" Machine instance, but {type(machine).__name__}."
      )
    logger.info(
      "WorkcellRuntime: Executing action '%s' on machine ID %d with params: %s",
      action_name,
      machine_orm_id,
      params,
    )

    if hasattr(machine, action_name) and callable(getattr(machine, action_name)):
      if isinstance(getattr(machine, action_name), Awaitable):
        logger.debug(
          "WorkcellRuntime: Calling asynchronous action '%s' on machine ID %d.",
          action_name,
          machine_orm_id,
        )
        return await getattr(machine, action_name)(**(params or {}))
      else:
        # If the action is a synchronous method, call it directly
        logger.debug(
          "WorkcellRuntime: Calling synchronous action '%s' on machine ID %d.",
          action_name,
          machine_orm_id,
        )
        return getattr(machine, action_name)(**(params or {}))
    else:
      raise AttributeError(
        f"Machine for ID {machine_orm_id} (type: {type(machine).__name__})"
        f" has no action '{action_name}'."
      )

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error shutting down all machines",
    suffix=" - Ensure all machines are properly initialized and connected.",
  )
  async def shutdown_all_machines(self):
    """Shut down all currently active PyLabRobot machine instances."""
    logger.info("WorkcellRuntime: Shutting down all active machines...")
    for machine_id in list(self._active_machines.keys()):
      try:
        logger.info("WorkcellRuntime: Shutting down machine ID %d...", machine_id)
        await self.shutdown_machine(machine_id)
      except WorkcellRuntimeError as e:
        logger.error(
          "WorkcellRuntime: Error shutting down machine ID %d: %s",
          machine_id,
          str(e),
        )
        continue
    logger.info("WorkcellRuntime: All active machines processed for shutdown.")

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error getting deck state representation",
    suffix=" - Ensure the deck machine ORM ID is valid and the deck is active.",
  )
  async def get_deck_state_representation(self, deck_orm_id: int) -> Dict[str, Any]:
    """Construct a dictionary representing the state of a specific deck.

    This representation is suitable for serialization into `DeckStateResponse`.
    It uses a database-first approach for resources located on the deck.

    Args:
      deck_orm_id (int): The ORM ID of the deck machine.

    Returns:
      Dict[str, Any]: A dictionary representing the deck's current state.

    Raises:
      WorkcellRuntimeError: If the database session or service is unavailable,
        the deck machine is not found in the database, or the machine is not
        categorized as a DECK.

    """
    deck_orm = await svc.get_deck_by_id(self.db_session, deck_orm_id)

    if deck_orm is None or not hasattr(deck_orm, "id") or deck_orm.id is None:
      raise WorkcellRuntimeError(f"Deck ORM ID {deck_orm_id} not found in database.")

    response_positions: List[Dict[str, Any]] = []

    resources_on_deck: List[ResourceInstanceOrm] = await svc.list_resource_instances(
      db=self.db_session,
      location_machine_id=deck_orm.id,
    )

    for lw_instance in resources_on_deck:
      if lw_instance.current_deck_position_name is not None:
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

        lw_active_instance = self.get_active_resource(lw_instance.id)
        if lw_active_instance is None or not isinstance(lw_active_instance, Resource):
          raise WorkcellRuntimeError(
            f"Resource instance ID {lw_instance.id} identified in deck {deck_orm.id} "
            "is not an active resource."
          )

        lw_active_coords = lw_active_instance.get_absolute_location()

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
        position_info_data = {
          "name": lw_instance.current_deck_position_name,
          "x_coordinate": lw_active_coords.x,
          "y_coordinate": lw_active_coords.y,
          "z_coordinate": lw_active_coords.z,
          "resource": resource_info_data,
        }
        response_positions.append(position_info_data)

    deck_size_x = None
    deck_size_y = None
    deck_size_z = None

    live_deck = self.get_active_deck(deck_orm_id)
    if live_deck is not None and hasattr(live_deck, "get_size"):
      try:
        deck_size_tuple = (
          live_deck.get_size_x(),
          live_deck.get_size_y(),
          live_deck.get_size_z(),
        )
        deck_size_x, deck_size_y, deck_size_z = deck_size_tuple
        logger.debug(
          "Retrieved live deck dimensions for ID %d: %s",
          deck_orm_id,
          deck_size_tuple,
        )
      except Exception as e:
        logger.warning(
          "Could not get size from live deck object for ID %d: %s",
          deck_orm_id,
          e,
        )

    deck_state_data = {
      "deck_id": deck_orm.id,
      "name": deck_orm.name or f"Deck_{deck_orm.id}",
      "python_fqn": deck_orm.python_fqn,
      "size_x_mm": deck_size_x,
      "size_y_mm": deck_size_y,
      "size_z_mm": deck_size_z,
      "positions": response_positions,
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
  # - Iterating through DeckPositionOrm entries in the DeckConfigurationOrm.
  # - For each position with assigned resource:
  #   - Get/create the PlrResource for the ResourceInstanceOrm.
  #   - Call assign_resource_to_deck_position with the target deck's ORM ID.
  # - This would be the primary way to set up a live deck to match a saved
  # configuration.
