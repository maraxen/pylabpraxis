# pylint: disable=too-many-arguments, broad-except, fixme
"""Workcell Runtime Management.

praxis/core/workcell_runtime.py

The WorkcellRuntime manages live PyLabRobot objects (machines, resources)
for an active workcell configuration. It translates database-defined assets
into operational PyLabRobot instances.
"""

import asyncio
import datetime
import importlib
import inspect
import uuid
from collections.abc import Awaitable, Callable
from functools import partial
from typing import (
  Any,
  cast,
)

from pylabrobot.machines import Machine
from pylabrobot.resources import Coordinate, Deck, Resource
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import praxis.backend.services as svc
from praxis.backend.configure import PraxisConfiguration
from praxis.backend.core.workcell import Workcell
from praxis.backend.models import (
  MachineOrm,
  MachineStatusEnum,
  PositioningConfig,
  ResourceOrm,
  ResourceStatusEnum,
)
from praxis.backend.utils.errors import WorkcellRuntimeError
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)

log_workcell_runtime_errors = partial(
  log_async_runtime_errors,
  logger_instance=logger,
  raises=True,
  raises_exception=WorkcellRuntimeError,
)


def _get_class_from_fqn(class_fqn: str) -> type:
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

  def __init__(
    self,
    db_session_factory: async_sessionmaker[AsyncSession],
    config: PraxisConfiguration,
  ):
    """Initialize the WorkcellRuntime.

    Args:
      db_session_factory (async_sessionmaker[AsyncSession]): A factory for SQLAlchemy async sessions.
      workcell_name (str): The name of the workcell.
      workcell_save_file (str): The path for disk backups.

    """
    self.db_session_factory = db_session_factory
    self._active_machines: dict[uuid.UUID, Machine] = {}
    self._active_resources: dict[uuid.UUID, Resource] = {}
    self._active_decks: dict[uuid.UUID, Deck] = {}
    self._last_initialized_deck_object: Deck | None = None
    self._last_initialized_deck_orm_accession_id: uuid.UUID | None = None

    self._main_workcell = Workcell(
      name="praxis_workcell",  # Hardcoded name for now, can be configurable later
      save_file=config.workcell_state_file,
      backup_interval=60,
      num_backups=3,
    )
    self._workcell_db_accession_id: uuid.UUID | None = None
    self._state_sync_task: asyncio.Task | None = None
    logger.info("WorkcellRuntime initialized.")

  async def _link_workcell_to_db(self):
    """Links the in-memory Workcell to its persistent DB entry."""
    if self._workcell_db_accession_id is None:
      async with self.db_session_factory() as db_session:
        workcell_orm = await svc.create_workcell(
          db_session,
          name=self._main_workcell.name,
          initial_state=self._main_workcell.serialize_all_state(),
        )
        await db_session.commit()
        self._workcell_db_accession_id = workcell_orm.accession_id
        logger.info(
          "Workcell '%s' linked to DB ID: %s",
          self._main_workcell.name,
          self._workcell_db_accession_id,
        )

        db_state = await svc.read_workcell_state(
          db_session,
          self._workcell_db_accession_id,
        )
        if db_state:
          self._main_workcell.load_all_state(db_state)
          logger.info(
            "Workcell '%s' state loaded from DB on startup.",
            self._main_workcell.name,
          )

  async def _continuous_state_sync_loop(self):
    """Synchronize workcell state internally and continuously (DB & Disk)."""
    if self._workcell_db_accession_id is None:
      logger.error("Cannot start state sync loop: Workcell DB ID is not set.")
      return

    logger.info(
      "Starting continuous workcell state sync loop for workcell ID: %s",
      self._workcell_db_accession_id,
    )
    last_disk_backup_time = datetime.datetime.now(datetime.timezone.utc)

    while True:
      try:
        current_state_json = self._main_workcell.serialize_all_state()

        async with self.db_session_factory() as db_session:
          await svc.update_workcell_state(
            db_session,
            self._workcell_db_accession_id,
            current_state_json,
          )
          await db_session.commit()
        logger.debug(
          "Workcell state for ID %s updated in DB.",
          self._workcell_db_accession_id,
        )

        now = datetime.datetime.now(datetime.timezone.utc)
        if (
          now - last_disk_backup_time
        ).total_seconds() >= self._main_workcell.backup_interval:
          disk_backup_path = self._main_workcell.save_file.replace(
            ".json",
            f"_{self._main_workcell.backup_num}.json",
          )
          self._main_workcell.save_state_to_file(disk_backup_path)
          self._main_workcell.backup_num = (
            self._main_workcell.backup_num + 1
          ) % self._main_workcell.num_backups
          last_disk_backup_time = now
          logger.info(
            "Workcell state for ID %s backed up to disk: %s.",
            self._workcell_db_accession_id,
            disk_backup_path,
          )

      except asyncio.CancelledError:
        logger.info("Workcell state sync loop cancelled.")
        break
      # Justification: This is a top-level background task loop. A broad except
      # is necessary to catch any unexpected errors during the sync process,
      # log them, and allow the loop to continue, preventing the entire
      # runtime from crashing due to a transient issue.
      except Exception as e:  # pylint: disable=broad-except
        logger.error(
          "Error during continuous workcell state sync for ID %s: %s",
          self._workcell_db_accession_id,
          e,
          exc_info=True,
        )
      finally:
        await asyncio.sleep(5)

  async def start_workcell_state_sync(self):
    """Start the continuous workcell state synchronization task."""
    await self._link_workcell_to_db()
    if self._state_sync_task and not self._state_sync_task.done():
      logger.warning("Workcell state sync task is already running.")
      return

    self._state_sync_task = asyncio.create_task(self._continuous_state_sync_loop())
    logger.info(
      "Workcell state sync task started for ID %s.",
      self._workcell_db_accession_id,
    )

  async def stop_workcell_state_sync(self):
    """Stop the continuous workcell state synchronization task and performs final disk backup."""
    if self._state_sync_task:
      self._state_sync_task.cancel()
      try:
        await self._state_sync_task
      except asyncio.CancelledError:
        pass
      self._state_sync_task = None
    else:
      logger.info("No active workcell state sync task to stop.")

    if self._main_workcell:
      final_backup_path = self._main_workcell.save_file.replace(
        ".json",
        "_final_exit.json",
      )
      self._main_workcell.save_state_to_file(final_backup_path)  # type: ignore
      logger.info("Workcell state saved to disk on exit: %s", final_backup_path)

    if self._workcell_db_accession_id:
      try:
        async with self.db_session_factory() as db_session:
          await svc.update_workcell_state(
            db_session,
            self._workcell_db_accession_id,
            self._main_workcell.serialize_all_state(),
          )
          await db_session.commit()
          logger.info(
            "Final workcell state for ID %s committed to DB on exit.",
            self._workcell_db_accession_id,
          )
      # Justification: This is a final cleanup step on shutdown. A broad except
      # is necessary to log any error without crashing the shutdown process.
      except Exception as e:  # pylint: disable=broad-except
        logger.error(
          "Failed to commit final workcell state to DB on exit for ID %s: %s",
          self._workcell_db_accession_id,
          e,
        )

  def get_main_workcell(self) -> Workcell:
    """Return the main Workcell instance managed by the runtime."""
    if self._main_workcell is None:
      raise WorkcellRuntimeError("Main Workcell instance is not initialized.")
    return self._main_workcell

  def get_state_snapshot(self) -> dict[str, Any]:
    """Capture and return the current JSON-serializable state of the workcell."""
    return self._main_workcell.serialize_all_state()

  def apply_state_snapshot(self, snapshot_json: dict[str, Any]):
    """Apply a previously captured JSON state to the workcell."""
    self._main_workcell.load_all_state(snapshot_json)
    logger.info("Workcell state rolled back from snapshot.")

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error encountered calculating location from deck position",
    suffix=" - Ensure the deck type definition exists in the database.",
  )
  async def _get_calculated_location(
    self,
    target_deck: Deck,
    deck_type_definition_accession_id: uuid.UUID,
    position_accession_id: str | int | uuid.UUID,
    positioning_config: PositioningConfig | None,
  ) -> Coordinate:
    """Calculate the PyLabRobot Coordinate for a given position_accession_id.

    Based on the deck's positioning configuration or predefined positions, returns the
    corresponding PyLabRobot Coordinate for the position_accession_id on the target deck.
    Different Deck subclasses have different human interpretable position descriptions
    (e.g., "A1", "B2", "C3", etc. for slots, or 1,2,3, etc. for rails), this allows
    for easy interoperability and informing users of how to set-up a deck.


    Args:
        target_deck (Deck): The live PyLabRobot Deck object.
        deck_type_definition_accession_id (uuid.UUID): The ID of the associated
        DeckTypeDefinition.
        position_accession_id (Union[str, int, uuid.UUID]): The human-interpretable identifier for
        the position.
        positioning_config (Optional[PositioningConfig]): The general positioning
            configuration for the deck type.

    Returns:
        Coordinate: The calculated PyLabRobot Coordinate.

    Raises:
        WorkcellRuntimeError: If the location cannot be determined.
        TypeError: If the position_accession_id is not a valid type for the method.

    """
    if positioning_config is None:
      logger.info(
        "No general positioning config for deck type ID %s, "
        "attempting to find position in DeckPositionDefinitionOrm.",
        deck_type_definition_accession_id,
      )
      if isinstance(position_accession_id, (str, int, uuid.UUID)):
        async with self.db_session_factory() as db_session:
          all_deck_position_definitions = (
            await svc.read_position_definitions_for_deck_type(
              db_session,
              deck_type_definition_accession_id,
            )
          )
          found_position_def = next(
            (
              p
              for p in all_deck_position_definitions
              if p.position_accession_id == str(position_accession_id)
              or p.position_accession_id == int(position_accession_id)
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
          raise WorkcellRuntimeError(
            f"Position '{position_accession_id}' not found in predefined deck position "
            f"definitions for deck type ID {deck_type_definition_accession_id}.",
          )
      else:
        raise WorkcellRuntimeError(
          f"No positioning configuration provided for deck type ID "
          f"{deck_type_definition_accession_id}. Cannot determine position location.",
        )
    else:
      method_name = positioning_config.method_name
      arg_name = positioning_config.arg_name
      arg_type = positioning_config.arg_type
      method_params = positioning_config.params or {}

      position_method = getattr(target_deck, method_name, None)
      if position_method is None or not callable(position_method):
        raise WorkcellRuntimeError(
          f"Deck does not have a valid position method '{method_name}' as configured.",
        )

      converted_position_arg: str | int
      if arg_type == "int":
        try:
          converted_position_arg = int(position_accession_id)
        except (ValueError, TypeError) as e:
          raise TypeError(
            f"Expected integer for position_accession_id '{position_accession_id}' for method "
            f"'{method_name}' but got invalid type/value: {e}",
          ) from e
      else:
        converted_position_arg = str(position_accession_id)

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
          "Check if method signature matches configuration.",
        ) from e
      # Justification: This wraps a dynamic call to a PyLabRobot method, which could
      # raise any number of unexpected errors. Catching broadly ensures we can
      # provide a detailed error message about the failed dynamic call.
      except Exception as e:  # pylint: disable=broad-except
        logger.exception("Unexpected error when calling PLR method '%s'", method_name)
        raise WorkcellRuntimeError(
          f"Unexpected error when calling PLR method '{method_name}': {e}",
        ) from e

      if not isinstance(calculated_location, Coordinate):
        if isinstance(calculated_location, tuple) and len(calculated_location) == 3:
          calculated_location = Coordinate(
            x=calculated_location[0],
            y=calculated_location[1],
            z=calculated_location[2],
          )
        else:
          raise TypeError(
            f"Expected PLR method '{method_name}' to return a Coordinate or (x,y,z) "
            f"tuple, but got {type(calculated_location)}: {calculated_location}",
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
    if not hasattr(machine_orm, "id") or machine_orm.accession_id is None:
      raise WorkcellRuntimeError(
        "Invalid machine_orm object passed to initialize_machine (no id).",
      )

    if machine_orm.accession_id in self._active_machines:
      logger.info(
        "WorkcellRuntime: Machine '%s' (ID: %s) already active. Returning existing instance.",
        machine_orm.user_friendly_name,
        machine_orm.accession_id,
      )
      return self._active_machines[machine_orm.accession_id]

    shared_plr_instance: Machine | Resource | None = None
    if (
      machine_orm.is_resource
      and machine_orm.resource_counterpart
      and machine_orm.resource_counterpart.is_machine
      and machine_orm.resource_counterpart.machine_counterpart_accession_id
      == machine_orm.accession_id
    ):
      resource_orm = machine_orm.resource_counterpart
      if resource_orm.accession_id in self._active_resources:
        shared_plr_instance = self._active_resources[resource_orm.accession_id]
        logger.info(
          "WorkcellRuntime: Machine '%s' (ID: %s) is linked to active Resource "
          " '%s' (ID: %s). Reusing existing PLR object as the machine instance.",
          machine_orm.user_friendly_name,
          machine_orm.accession_id,
          resource_orm.user_assigned_name,
          resource_orm.accession_id,
        )
        if not isinstance(shared_plr_instance, Machine):
          raise TypeError(
            f"Linked Resource ID {resource_orm.accession_id} is active "
            f"but its PLR object  '{type(shared_plr_instance).__name__}' is "
            f"not a valid Machine instance.",
          )

    machine_instance: Machine
    if shared_plr_instance:
      machine_instance = cast(Machine, shared_plr_instance)
    else:
      logger.info(
        "WorkcellRuntime: Initializing new machine '%s' (ID: %s) using class '%s'.",
        machine_orm.user_friendly_name,
        machine_orm.accession_id,
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

        valid_init_params = {
          k: v for k, v in init_params.items() if k in sig.parameters
        }
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
            f"Machine '{machine_orm.user_friendly_name}' initialized, but it is "
            f"not a valid PyLabRobot Machine instance. "
            f"Type is {type(machine_instance).__name__}.",
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
              f"Failed to call setup() for machine "
              f"'{machine_orm.user_friendly_name}': {str(e)[:250]}"
            )
            raise WorkcellRuntimeError(error_message)
        else:
          raise WorkcellRuntimeError(
            f"Machine '{machine_orm.user_friendly_name}' does not have a valid"
            " setup() method that is callable and awaitable.",
          )
      # Justification: This wraps the dynamic instantiation and setup of a PyLabRobot
      # object, which can fail in numerous ways (missing dependencies, connection
      # errors, etc.). A broad catch is necessary to handle any such failure, log it,
      # update the machine's status to ERROR, and raise a specific runtime error.
      except Exception as e:  # pylint: disable=broad-except
        error_message = f"Failed to instantiate or setup machine \
                '{machine_orm.user_friendly_name}'\
                (ID: {machine_orm.accession_id}) using class '{machine_orm.python_fqn}': \
                {str(e)[:250]}"
        async with self.db_session_factory() as db_session:
          await svc.update_machine_status(
            db_session,
            machine_orm.accession_id,
            MachineStatusEnum.ERROR,
            f"Machine init failed: {str(e)[:250]}",
          )
          await db_session.commit()
        raise WorkcellRuntimeError(error_message) from e

    self._active_machines[machine_orm.accession_id] = machine_instance
    self._main_workcell.add_asset(machine_instance)
    logger.info(
      "WorkcellRuntime: Machine '%s' (ID: %s) added to main Workcell container.",
      machine_orm.user_friendly_name,
      machine_orm.accession_id,
    )

    if (
      machine_orm.is_resource
      and machine_orm.resource_counterpart
      and machine_orm.resource_counterpart.is_machine
      and machine_orm.resource_counterpart.machine_counterpart_accession_id
      == machine_orm.accession_id
    ):
      resource_orm = machine_orm.resource_counterpart
      if isinstance(machine_instance, Resource):
        self._active_resources[resource_orm.accession_id] = cast(
          Resource,
          machine_instance,
        )
        logger.info(
          "WorkcellRuntime: Machine '%s' (ID: %s) also registered as Resource "
          "'%s' (ID: %s) in _active_resources, sharing the same PLR object.",
          machine_orm.user_friendly_name,
          machine_orm.accession_id,
          resource_orm.user_assigned_name,
          resource_orm.accession_id,
        )
      else:
        logger.warning(
          "WorkcellRuntime: Machine '%s' (ID: %s) is flagged as a resource "
          "counterpart, but its PLR object type '%s' is not a PyLabRobot Resource"
          " subclass. It will not be registered in _active_resources.",
          machine_orm.user_friendly_name,
          machine_orm.accession_id,
          type(machine_instance).__name__,
        )

    if hasattr(machine_instance, "deck") and isinstance(
      machine_instance.deck,
      Deck,
    ):
      machine_deck: Deck = machine_instance.deck
      if not isinstance(machine_deck, Deck):
        raise TypeError(
          f"Machine '{machine_orm.user_friendly_name}' has a 'deck' attribute, "
          f"but it is not a Deck instance. Type is {type(machine_deck)}.",
        )

      async with self.db_session_factory() as db_session:
        deck_orm_entry = await svc.read_deck_instance_by_parent_machine_accession_id(
          db_session,
          machine_orm.accession_id,
        )

        if deck_orm_entry and deck_orm_entry.accession_id is not None:
          self._active_decks[deck_orm_entry.accession_id] = machine_deck
          self._last_initialized_deck_object = machine_deck
          self._last_initialized_deck_orm_accession_id = deck_orm_entry.accession_id
          logger.info(
            "Registered deck (DeckOrm ID: %s, PLR name: '%s') from machine '%s' \
            (ID: %s) to active decks.",
            deck_orm_entry.accession_id,
            machine_deck.name,
            machine_orm.user_friendly_name,
            machine_orm.accession_id,
          )
        else:
          logger.warning(
            "Machine '%s' (ID: %s) has a .deck attribute, but no corresponding DeckOrm \
            entry found with parent_machine_accession_id=%s. Deck not registered in \
              _active_decks.",
            machine_orm.user_friendly_name,
            machine_orm.accession_id,
            machine_orm.accession_id,
          )

    async with self.db_session_factory() as db_session:
      await svc.update_machine_status(
        db_session,
        machine_orm.accession_id,
        MachineStatusEnum.AVAILABLE,
        "Machine initialized successfully.",
      )
      await db_session.commit()
    return machine_instance

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error creating or getting resource",
    suffix=" - Ensure the resource instance ORM and definition FQN are valid.",
  )
  async def create_or_get_resource(
    self,
    resource_orm: ResourceOrm,
    resource_definition_fqn: str,
  ) -> Resource:
    """Create or retrieve a live PyLabRobot resource object.

    Args:
      resource_orm (ResourceOrm): The ORM object representing
        the resource instance.
      resource_definition_fqn (str): The fully qualified Python name of the
        PyLabRobot resource class.

    Raises:
      ValueError: If the resource_orm does not have a valid ID.
      WorkcellRuntimeError: If the resource creation fails or if the resource
        instance ORM is invalid.

    Returns:
      Resource: The live PyLabRobot resource object.

    """
    if not hasattr(resource_orm, "id") or resource_orm.accession_id is None:
      raise ValueError(
        "Invalid resource_orm object passed to create_or_get_resource (no id).",
      )

    if resource_orm.accession_id in self._active_resources:
      logger.info(
        "WorkcellRuntime: Resource '%s' (ID: %s) already active. Returning "
        "existing instance.",
        resource_orm.user_assigned_name,
        resource_orm.accession_id,
      )
      return self._active_resources[resource_orm.accession_id]

    shared_plr_instance: Machine | Resource | None = None
    if (
      resource_orm.is_machine
      and resource_orm.machine_counterpart
      and resource_orm.machine_counterpart.is_resource
      and resource_orm.machine_counterpart.resource_counterpart_accession_id
      == resource_orm.accession_id
    ):
      machine_orm = resource_orm.machine_counterpart
      if machine_orm.accession_id in self._active_machines:
        shared_plr_instance = self._active_machines[machine_orm.accession_id]
        logger.info(
          "WorkcellRuntime: Resource '%s' (ID: %s) is linked to active Machine "
          "'%s' (ID: %s). Reusing existing PLR object as the resource instance.",
          resource_orm.user_assigned_name,
          resource_orm.accession_id,
          machine_orm.user_friendly_name,
          machine_orm.accession_id,
        )
        if not isinstance(shared_plr_instance, Resource):
          raise TypeError(
            f"Linked Machine ID {machine_orm.accession_id} is active but its PLR object "
            f"'{type(shared_plr_instance).__name__}' is not a PyLabRobot Resource. "
            f"Cannot use as resource.",
          )

    resource_instance: Resource
    if shared_plr_instance:
      resource_instance = cast(Resource, shared_plr_instance)
    else:
      logger.info(
        "Creating new PLR resource '%s' (ID: %s) using definition FQN '%s'.",
        resource_orm.user_assigned_name,
        resource_orm.accession_id,
        resource_definition_fqn,
      )

      try:
        ResourceClass = _get_class_from_fqn(resource_definition_fqn)
        resource_instance = ResourceClass(name=resource_orm.user_assigned_name)
      # Justification: This wraps the dynamic instantiation of a PyLabRobot resource,
      # which can fail for various reasons. A broad catch is necessary to handle any
      # failure, log it, update the resource's status to ERROR, and raise a specific runtime error.
      except Exception as e:  # pylint: disable=broad-except
        error_message = (
          f"Failed to create PLR resource for "
          f"'{resource_orm.user_assigned_name}' using FQN '"
          f"{resource_definition_fqn}': {str(e)[:250]}"
        )
        if hasattr(resource_orm, "id") and resource_orm.accession_id is not None:
          try:
            async with self.db_session_factory() as db_session:
              await svc.update_resource_instance_location_and_status(
                db_session,
                resource_instance_accession_id=resource_orm.accession_id,
                new_status=ResourceStatusEnum.ERROR,
                status_details=error_message,
              )
              await db_session.commit()
          # Justification: This is a nested error handler. If updating the DB
          # status fails, we must catch it to ensure the original, more
          # important error is still raised.
          except Exception as db_error:  # pylint: disable=broad-except
            error_message += (
              f" Failed to update resource instance ID {resource_orm.accession_id} "
              f"status to ERROR in DB: {str(db_error)[:250]}"
            )
            raise WorkcellRuntimeError(error_message) from db_error
        raise WorkcellRuntimeError(error_message) from e

    self._active_resources[resource_orm.accession_id] = resource_instance
    self._main_workcell.add_asset(resource_instance)
    logger.info(
      "WorkcellRuntime: Resource '%s' (ID: %s) stored in _active_resources and added to main Workcell.",
      resource_orm.user_assigned_name,
      resource_orm.accession_id,
    )

    if (
      resource_orm.is_machine
      and resource_orm.machine_counterpart
      and resource_orm.machine_counterpart.is_resource
      and resource_orm.machine_counterpart.resource_counterpart_accession_id
      == resource_orm.accession_id
    ):
      machine_orm = resource_orm.machine_counterpart
      if isinstance(resource_instance, Machine):
        self._active_machines[machine_orm.accession_id] = cast(
          Machine,
          resource_instance,
        )
        logger.info(
          "WorkcellRuntime: Resource '%s' (ID: %s) also registered as Machine "
          "'%s' (ID: %s) in _active_machines, sharing the same PLR object.",
          resource_orm.user_assigned_name,
          resource_orm.accession_id,
          machine_orm.user_friendly_name,
          machine_orm.accession_id,
        )
      else:
        logger.warning(
          "WorkcellRuntime: Resource '%s' (ID: %s) is flagged as a machine "
          "counterpart, but its PLR object type '%s' is not a PyLabRobot Machine "
          "subclass. It will not be registered in _active_machines.",
          resource_orm.user_assigned_name,
          resource_orm.accession_id,
          type(resource_instance).__name__,
        )
    return resource_instance

  def get_active_machine(self, machine_orm_accession_id: uuid.UUID) -> Machine:
    """Retrieve an active PyLabRobot machine instance by its ORM ID.

    Args:
      machine_orm_accession_id (uuid.UUID): The ID of the machine ORM object.

    Returns:
      Machine: The active PyLabRobot machine instance.

    Raises:
      WorkcellRuntimeError: If the machine is not found in the active machines.

    """
    machine = self._active_machines.get(machine_orm_accession_id)
    if machine is None:
      raise WorkcellRuntimeError(
        f"Machine with ORM ID {machine_orm_accession_id} not found in active machines.",
      )
    if not isinstance(machine, Machine):
      raise TypeError(
        f"Machine with ORM ID {machine_orm_accession_id} is not a valid Machine instance."
        f" Type is {type(machine)}.",
      )
    return machine

  def get_active_machine_accession_id(self, machine: Machine) -> uuid.UUID:
    """Retrieve the ORM ID of an active PyLabRobot machine instance.

    Args:
      machine (Machine): The PyLabRobot Machine instance.

    Returns:
      uuid.UUID: The ORM ID of the machine.

    Raises:
      WorkcellRuntimeError: If the machine is not found in the active machines.

    """
    for orm_accession_id, active_machine in self._active_machines.items():
      if active_machine is machine:
        return orm_accession_id
    raise WorkcellRuntimeError(
      f"Machine instance {machine} not found in active machines.",
    )

  def get_active_deck_accession_id(self, deck: Deck) -> uuid.UUID:
    """Retrieve the ORM ID of an active PyLabRobot Deck instance.

    Args:
      deck (Deck): The PyLabRobot Deck instance.

    Returns:
      uuid.UUID: The ORM ID of the deck.

    Raises:
      WorkcellRuntimeError: If the deck is not found in the active decks.

    """
    for orm_accession_id, active_deck in self._active_decks.items():
      if active_deck is deck:
        return orm_accession_id
    raise WorkcellRuntimeError(f"Deck instance {deck} not found in active decks.")

  def get_active_resource(
    self,
    resource_orm_accession_id: uuid.UUID,
  ) -> Resource:
    """Retrieve an active PyLabRobot resource object by its ORM ID.

    Args:
      resource_orm_accession_id (uuid.UUID): The ID of the resource instance ORM object.

    Returns:
      Resource: The active PyLabRobot resource object.

    """
    resource = self._active_resources.get(resource_orm_accession_id)
    if resource is None:
      raise WorkcellRuntimeError(
        f"Resource instance with ORM ID {resource_orm_accession_id} not found in active \
          resources.",
      )
    if not isinstance(resource, Resource):
      raise TypeError(
        f"Resource instance with ORM ID {resource_orm_accession_id} is not a valid \
          PyLabRobot Resource instance. Type is {type(resource)}.",
      )
    return resource

  def get_active_resource_accession_id(self, resource: Resource) -> uuid.UUID:
    """Retrieve the ORM ID of an active PyLabRobot resource object.

    Args:
      resource (Resource): The PyLabRobot Resource instance.

    Returns:
      uuid.UUID: The ORM ID of the resource.

    """
    for orm_accession_id, active_resource in self._active_resources.items():
      if active_resource is resource:
        return orm_accession_id
    raise WorkcellRuntimeError(f"Resource instance {resource}")

  def get_active_deck(self, deck_orm_accession_id: uuid.UUID) -> Deck:
    """Retrieve an active PyLabRobot Deck instance by its ORM ID.

    Args:
      deck_orm_accession_id (uuid.UUID): The ID of the deck ORM object.

    Returns:
      Deck: The active PyLabRobot Deck instance.

    """
    deck = self._active_decks.get(deck_orm_accession_id)
    if deck is None:
      raise WorkcellRuntimeError(
        f"Deck with ORM ID {deck_orm_accession_id} not found in active decks.",
      )
    if not isinstance(deck, Deck):
      raise TypeError(
        f"Deck with ORM ID {deck_orm_accession_id} is not a valid PyLabRobot Deck instance."
        f" Type is {type(deck)}.",
      )
    return deck

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error shutting down machine",
    suffix=" - Ensure the machine ORM ID is valid and the machine is active.",
  )
  async def shutdown_machine(self, machine_orm_accession_id: uuid.UUID):
    """Shut down and removes a live PyLabRobot machine instance.

    Args:
      machine_orm_accession_id (uuid.UUID): The ID of the machine ORM object to shut down.

    Raises:
      WorkcellRuntimeError: If the machine is not found, or if the shutdown fails.

    """
    machine_instance = self._active_machines.pop(machine_orm_accession_id, None)
    try:
      if machine_instance is not None:
        logger.info(
          "WorkcellRuntime: Shutting down machine for machine ID: %s...",
          machine_orm_accession_id,
        )
        if (
          hasattr(machine_instance, "stop")
          and isinstance(machine_instance.stop, Awaitable)
          and isinstance(machine_instance.stop, Callable)
        ):
          logger.info(
            "WorkcellRuntime: Calling stop() for machine ID %s...",
            machine_orm_accession_id,
          )
          await machine_instance.stop()
        else:
          raise WorkcellRuntimeError(
            f"No stop() method for \
            {machine_instance.__class__.__name__} machine {machine_orm_accession_id} \
              that is callable and awaitable.",
          )
        async with self.db_session_factory() as db_session:
          await svc.update_machine_status(
            db_session,
            machine_orm_accession_id,
            MachineStatusEnum.OFFLINE,
            "Machine shut down.",
          )
          await db_session.commit()

      # Justification: This is a fallback for when a machine is not found in the active
      # list but is expected to be. It ensures the DB status is updated to reflect
      # the offline state, preventing it from being stuck in an inconsistent state.
      else:  # pylint: disable=broad-except
        async with self.db_session_factory() as db_session:
          await svc.update_machine_status(
            db_session,
            machine_orm_accession_id,
            MachineStatusEnum.OFFLINE,
            "Machine not found for shutdown.",
          )
          await db_session.commit()
        raise WorkcellRuntimeError(
          f"Machine with ID {machine_orm_accession_id} is not currently active and is \
          unexpectedly offline.",
        )

    # Justification: This wraps the machine's `stop()` method, which can raise
    # any exception. A broad catch is needed to ensure the machine's status is
    # updated to ERROR in the database, preventing it from being stuck in an
    # inconsistent state.
    except Exception as e:  # pylint: disable=broad-except
      if machine_instance is None:
        raise WorkcellRuntimeError(
          f"No active machine instance found for machine ID {machine_orm_accession_id}.",
        ) from e
      self._active_machines[machine_orm_accession_id] = machine_instance
      async with self.db_session_factory() as db_session:
        await svc.update_machine_status(
          db_session,
          machine_orm_accession_id,
          MachineStatusEnum.ERROR,
          f"Shutdown failed: {str(e)[:250]}",
        )
        await db_session.commit()
      raise WorkcellRuntimeError(
        f"Error shutting down machine ID {machine_orm_accession_id}: \
        {str(e)[:250]}",
      ) from e

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error assigning resource to deck",
    suffix=" - Ensure the resource and deck are valid and connected.",
  )
  async def assign_resource_to_deck(
    self,
    resource_orm_accession_id: uuid.UUID,
    target: uuid.UUID,
    location: Coordinate | tuple[float, float, float] | None = None,
    position_accession_id: str | int | uuid.UUID | None = None,
  ):
    """Assign a live Resource to a specific location or position on a deck.

    Args:
      resource_orm_accession_id (uuid.UUID): The ID of the resource instance ORM object.
      target (uuid.UUID): The target deck or machine ORM ID.
      location (Optional[Union[Coordinate, tuple[float, float, float]]]): The
        explicit location coordinates on the deck.
      position_accession_id (Optional[Union[str, int, uuid.UUID]]): The position ID on the deck.


    Raises:
      WorkcellRuntimeError: If neither location nor position_accession_id is provided, or if
        the resource is not a valid PyLabRobot Resource instance, or if the deck
        is not found or not active.
      TypeError: If the resource is not a valid PyLabRobot Resource instance.

    """
    if location is None and position_accession_id is None:
      raise WorkcellRuntimeError(
        "Either 'location' or 'position_accession_id' must be provided to assign a resource"
        " to a deck.",
      )

    if target in self._active_machines:
      inferred_target_type = "machine_orm_accession_id"
    elif target in self._active_decks:
      inferred_target_type = "deck_orm_accession_id"
    else:
      raise WorkcellRuntimeError(
        f"Target ORM ID {target} not found in active machines or decks.",
      )

    resource = self.get_active_resource(resource_orm_accession_id)

    match inferred_target_type:
      case "deck_orm_accession_id":
        deck_orm_accession_id = cast(uuid.UUID, target)
        target_deck = self.get_active_deck(deck_orm_accession_id)
      case "machine_orm_accession_id":
        machine_orm_accession_id = cast(uuid.UUID, target)
        target_machine = self.get_active_machine(machine_orm_accession_id)
        target_deck = getattr(target_machine, "deck", None)
        if not isinstance(target_deck, Deck):
          raise WorkcellRuntimeError(
            f"Machine ID {machine_orm_accession_id} does not have an associated deck.",
          )
        deck_orm_accession_id = self.get_active_deck_accession_id(target_deck)
      case _:
        raise WorkcellRuntimeError(
          f"Unexpected target type: {inferred_target_type}. Expected deck_orm_accession_id or \
            machine_orm_accession_id.",
        )

    async with self.db_session_factory() as db_session:
      deck_orm = await svc.read_deck_instance(db_session, deck_orm_accession_id)
      if deck_orm is None:
        raise WorkcellRuntimeError(
          f"Deck ORM ID {deck_orm_accession_id} not found in database.",
        )
      deck_orm_type_definition_accession_id = deck_orm.deck_type_definition_accession_id

      if deck_orm_type_definition_accession_id is None:
        raise WorkcellRuntimeError(
          f"Deck ORM ID {deck_orm_accession_id} does not have a valid deck type definition.",
        )

      deck_type_definition_orm = await svc.read_deck_type_definition(
        db_session,
        deck_orm_type_definition_accession_id,
      )

      if deck_type_definition_orm is None:
        raise WorkcellRuntimeError(
          f"Deck type definition for deck ORM ID {deck_orm_accession_id} not found in database.",
        )

      positioning_config = PositioningConfig.model_validate(
        deck_type_definition_orm.positioning_config_json,
      )

      final_location_for_plr: Coordinate
      if location is not None:
        if isinstance(location, tuple):
          final_location_for_plr = Coordinate(
            x=location[0],
            y=location[1],
            z=location[2],
          )
        else:
          final_location_for_plr = location
      elif position_accession_id is not None:
        final_location_for_plr = await self._get_calculated_location(
          target_deck=target_deck,
          deck_type_definition_accession_id=deck_type_definition_orm.accession_id,
          position_accession_id=position_accession_id,
          positioning_config=positioning_config,
        )
      else:
        raise WorkcellRuntimeError(
          "Internal error: Neither location nor position_accession_id provided after initial check.",
        )

      try:
        target_deck.assign_child_resource(
          resource=resource,
          location=final_location_for_plr,
        )
        await svc.update_resource_instance_location_and_status(
          db_session,
          resource_orm_accession_id,
          ResourceStatusEnum.AVAILABLE_ON_DECK,
          location_machine_accession_id=deck_orm.accession_id,
          current_deck_position_name=str(position_accession_id),
        )
        await db_session.commit()
      # Justification: This wraps the deck's `assign_child_resource` method, which
      # can raise various exceptions. A broad catch is needed to provide a
      # clear error message about the assignment failure.
      except Exception as e:  # pylint: disable=broad-except
        raise WorkcellRuntimeError(
          f"Error assigning resource '{resource.name}' to  "
          f"location {final_location_for_plr} on deck ID {deck_orm.accession_id}: {str(e)[:250]}",
        ) from e

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error clearing deck position",
    suffix=" - Ensure the deck ORM ID and position name are valid.",
  )
  async def clear_deck_position(
    self,
    deck_orm_accession_id: uuid.UUID,
    position_name: str,
    resource_orm_accession_id: uuid.UUID | None = None,
  ):
    """Clear a resource from a specific position on a live deck.

    Args:
      deck_orm_accession_id (uuid.UUID): The ORM ID of the deck.
      position_name (str): The name of the position to clear.
      resource_orm_accession_id (Optional[uuid.UUID]): The ORM ID of the resource
        instance that was in the position, if known. Used for updating DB status.

    Raises:
      WorkcellRuntimeError: If the deck is not active, not a Deck
        instance, or if there's an error during unassignment.

    """
    deck = self.get_active_deck(deck_orm_accession_id)

    if not isinstance(deck, Deck):
      raise WorkcellRuntimeError(
        "Deck from workcell runtime is not a Deck instance."
        "This indicates a major error as non-Deck objects"
        " should not be in the active decks.",
      )
    logger.info(
      "WorkcellRuntime: Clearing position '%s' on deck ID %s.",
      position_name,
      deck_orm_accession_id,
    )

    resource_in_position = deck.get_resource(position_name)
    if resource_in_position:
      deck.unassign_child_resource(resource_in_position)
    else:
      logger.warning(
        "No specific resource found in position '%s' on deck ID %s to unassign."
        " Assuming position is already clear or unassignment by name is sufficient.",
        position_name,
        deck_orm_accession_id,
      )

    if resource_orm_accession_id:
      async with self.db_session_factory() as db_session:
        await svc.update_resource_instance_location_and_status(
          db_session,
          resource_orm_accession_id,
          ResourceStatusEnum.AVAILABLE_IN_STORAGE,
          location_machine_accession_id=None,
          current_deck_position_name=None,
        )
        await db_session.commit()

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error executing machine action",
    suffix=" - Ensure the machine is active and the action exists.",
  )
  async def execute_machine_action(
    self,
    machine_orm_accession_id: uuid.UUID,
    action_name: str,
    params: dict[str, Any] | None = None,
  ) -> Any:
    """Execute a method/action on a live PyLabRobot machine instance.

    Args:
      machine_orm_accession_id (uuid.UUID): The ORM ID of the machine to interact with.
      action_name (str): The name of the method to call on the machine object.
      params (Optional[dict[str, Any]]): A dictionary of parameters to pass
        to the method.

    Returns:
      Any: The result of the executed action.

    Raises:
      WorkcellRuntimeError: If the machine is not active or if an error occurs
        during action execution.
      AttributeError: If the specified action name does not exist on the machine.

    """
    machine = self.get_active_machine(machine_orm_accession_id)
    logger.info(
      "WorkcellRuntime: Executing action '%s' on machine ID %s with params: %s",
      action_name,
      machine_orm_accession_id,
      params,
    )

    if hasattr(machine, action_name) and callable(getattr(machine, action_name)):
      if inspect.iscoroutinefunction(getattr(machine, action_name)):
        logger.debug(
          "WorkcellRuntime: Calling asynchronous action '%s' on machine ID %s.",
          action_name,
          machine_orm_accession_id,
        )
        return await getattr(machine, action_name)(**(params or {}))
      logger.debug(
        "WorkcellRuntime: Calling synchronous action '%s' on machine ID %s.",
        action_name,
        machine_orm_accession_id,
      )
      return getattr(machine, action_name)(**(params or {}))
    raise AttributeError(
      f"Machine for ID {machine_orm_accession_id} (type: {type(machine).__name__})"
      f" has no action '{action_name}'.",
    )

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error shutting down all machines",
    suffix=" - Ensure all machines are properly initialized and connected.",
  )
  async def shutdown_all_machines(self):
    """Shut down all currently active PyLabRobot machine instances."""
    logger.info("WorkcellRuntime: Shutting down all active machines...")
    for machine_accession_id in list(self._active_machines.keys()):
      try:
        logger.info(
          "WorkcellRuntime: Shutting down machine ID %s...",
          machine_accession_id,
        )
        await self.shutdown_machine(machine_accession_id)
      except WorkcellRuntimeError as e:
        logger.error(
          "WorkcellRuntime: Error shutting down machine ID %s: %s",
          machine_accession_id,
          str(e),
        )
        continue
    logger.info("WorkcellRuntime: All active machines processed for shutdown.")

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error getting deck state representation",
    suffix=" - Ensure the deck ORM ID is valid and the deck is active.",
  )
  async def get_deck_state_representation(
    self,
    deck_orm_accession_id: uuid.UUID,
  ) -> dict[str, Any]:
    """Construct a dictionary representing the state of a specific deck.

    This representation is suitable for serialization into `DeckStateResponse`.
    It uses a database-first approach for resources located on the deck.

    Args:
      deck_orm_accession_id (uuid.UUID): The ORM ID of the deck.

    Returns:
      dict[str, Any]: A dictionary representing the deck's current state.

    Raises:
      WorkcellRuntimeError: If the database session or service is unavailable,
        the deck is not found in the database, or the machine is not
        categorized as a DECK.

    """
    async with self.db_session_factory() as db_session:
      deck_orm = await svc.read_deck_instance(db_session, deck_orm_accession_id)

      if (
        deck_orm is None or not hasattr(deck_orm, "id") or deck_orm.accession_id is None
      ):
        raise WorkcellRuntimeError(
          f"Deck ORM ID {deck_orm_accession_id} not found in database.",
        )

      response_positions: list[dict[str, Any]] = []

      resources_on_deck: list[ResourceOrm] = await svc.list_resource_instances(
        db=db_session,
        location_machine_accession_id=deck_orm.accession_id,
      )

      for lw_instance in resources_on_deck:
        if lw_instance.current_deck_position_name is not None:
          if (
            not hasattr(lw_instance, "resource_definition")
            or not lw_instance.resource_definition
          ):
            logger.warning(
              "Resource instance ID %s is missing resource_definition relationship."
              " Skipping.",
              lw_instance.accession_id,
            )
            continue
          lw_def = lw_instance.resource_definition

          lw_active_instance = self.get_active_resource(lw_instance.accession_id)

          lw_active_coords = lw_active_instance.get_absolute_location()

          resource_info_data = {
            "resource_instance_accession_id": lw_instance.accession_id,
            "user_assigned_name": (
              lw_instance.user_assigned_name or f"Resource_{lw_instance.accession_id}"
            ),
            "name": lw_def.name,
            "python_fqn": lw_def.python_fqn,
            "category": (
              str(lw_def.plr_category.value) if lw_def.plr_category else None
            ),
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

      live_deck = self.get_active_deck(deck_orm_accession_id)
      if live_deck is not None and hasattr(live_deck, "get_size"):
        try:
          deck_size_tuple = (
            live_deck.get_size_x(),
            live_deck.get_size_y(),
            live_deck.get_size_z(),
          )
          deck_size_x, deck_size_y, deck_size_z = deck_size_tuple
          logger.debug(
            "Retrieved live deck dimensions for ID %s: %s",
            deck_orm_accession_id,
            deck_size_tuple,
          )
        # Justification: This wraps a call to a PyLabRobot object's method, which
        # could raise unexpected errors. A broad catch allows us to log a warning
        # and continue, rather than crashing the state representation process.
        except Exception as e:  # pylint: disable=broad-except
          logger.warning(
            "Could not get size from live deck object for ID %s: %s",
            deck_orm_accession_id,
            e,
          )

      deck_state_data = {
        "deck_accession_id": deck_orm.accession_id,
        "name": deck_orm.name or f"Deck_{deck_orm.accession_id}",
        "python_fqn": deck_orm.python_fqn,
        "size_x_mm": deck_size_x,
        "size_y_mm": deck_size_y,
        "size_z_mm": deck_size_z,
        "positions": response_positions,
      }
      return deck_state_data

  async def get_last_initialized_deck_object(self) -> Deck | None:
    """Return the Deck most recently initialized by this runtime instance."""
    if self._last_initialized_deck_object:
      return self._last_initialized_deck_object
    return None

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error clearing resource",
    suffix=" - Ensure the resource is valid and exists in active resources.",
  )
  async def clear_resource_instance(self, resource_orm_accession_id: uuid.UUID):
    """Clear a resource from the workcell runtime.

    Args:
      resource_orm_accession_id (uuid.UUID): The ORM ID of the resource instance to clear.

    Raises:
      WorkcellRuntimeError: If the resource is not found in active resources.

    """
    if resource_orm_accession_id in self._active_resources:
      del self._active_resources[resource_orm_accession_id]

    async with self.db_session_factory() as db_session:
      await svc.update_resource_instance_location_and_status(
        db_session,
        resource_instance_accession_id=resource_orm_accession_id,
        new_status=ResourceStatusEnum.AVAILABLE_IN_STORAGE,
        status_details="Resource cleared from active resources.",
      )
      await db_session.commit()

    logger.info(
      "WorkcellRuntime: Cleared resource with ORM ID %s from active resources.",
      resource_orm_accession_id,
    )
