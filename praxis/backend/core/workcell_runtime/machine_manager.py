# pylint: disable=too-many-arguments, broad-except, fixme
"""Machine management for WorkcellRuntime."""

import inspect
import uuid
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, cast

from pylabrobot.machines import Machine
from pylabrobot.resources import Deck, Resource

if TYPE_CHECKING:
  from pylabrobot.liquid_handling.liquid_handler import LiquidHandler

  from praxis.backend.core.workcell_runtime.core import WorkcellRuntime

from praxis.backend.core.workcell_runtime.utils import (
  get_class_from_fqn,
  log_workcell_runtime_errors,
)
from praxis.backend.models import MachineOrm, MachineStatusEnum
from praxis.backend.utils.errors import WorkcellRuntimeError
from praxis.backend.utils.logging import get_logger

logger = get_logger(__name__)


class MachineManagerMixin:
  """Mixin for managing machines in WorkcellRuntime."""

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error initializing machine",
    suffix=" - Ensure the machine ORM is valid, the class, and machine is connected.",
  )
  async def initialize_machine(self, machine_orm: MachineOrm) -> Machine:
    """Initialize and connects to a machine's PyLabRobot machine/resource."""
    # We assume self is WorkcellRuntime
    runtime = cast("WorkcellRuntime", self)

    if not hasattr(machine_orm, "id") or machine_orm.accession_id is None:
      msg = "Invalid machine_orm object passed to initialize_machine (no id)."
      raise WorkcellRuntimeError(
        msg,
      )

    if machine_orm.accession_id in runtime._active_machines:
      logger.info(
        "WorkcellRuntime: Machine '%s' (ID: %s) already active. Returning existing instance.",
        machine_orm.name,
        machine_orm.accession_id,
      )
      return runtime._active_machines[machine_orm.accession_id]

    shared_plr_instance: Machine | Resource | None = None
    if (
      machine_orm.is_resource
      and machine_orm.resource_counterpart
      and machine_orm.resource_counterpart.is_machine
      and machine_orm.resource_counterpart.machine_counterpart
      and machine_orm.resource_counterpart.machine_counterpart.accession_id
      == machine_orm.accession_id
    ):
      resource_orm = machine_orm.resource_counterpart
      if resource_orm.accession_id in runtime._active_resources:
        shared_plr_instance = runtime._active_resources[resource_orm.accession_id]
        logger.info(
          "WorkcellRuntime: Machine '%s' (ID: %s) is linked to active Resource "
          " '%s' (ID: %s). Reusing existing PLR object as the machine instance.",
          machine_orm.name,
          machine_orm.accession_id,
          resource_orm.name,
          resource_orm.accession_id,
        )
        if not isinstance(shared_plr_instance, Machine):
          msg = (
            f"Linked Resource ID {resource_orm.accession_id} is active "
            f"but its PLR object  '{type(shared_plr_instance).__name__}' is "
            f"not a valid Machine instance."
          )
          raise TypeError(
            msg,
          )

    machine_instance: Machine
    if shared_plr_instance:
      machine_instance = cast("Machine", shared_plr_instance)
    else:
      logger.info(
        "WorkcellRuntime: Initializing new machine '%s' (ID: %s) using class '%s'.",
        machine_orm.name,
        machine_orm.accession_id,
        machine_orm.fqn,
      )
      try:
        target_class = get_class_from_fqn(machine_orm.fqn)
        machine_config = machine_orm.properties_json or {}
        instance_name = machine_orm.name

        init_params = machine_config.copy()
        sig = inspect.signature(target_class.__init__)

        if "name" in sig.parameters:
          init_params["name"] = instance_name
        elif "name" in init_params and init_params["name"] != instance_name:
          logger.warning(
            "WorkcellRuntime: 'name' in machine_config for %s differs. Using name.",
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
            "WorkcellRuntime: Extra parameters in machine_config for %s not "
            "accepted by %s.__init__: %s",
            instance_name,
            target_class.__name__,
            extra_params.keys(),
          )

        machine_instance = target_class(**valid_init_params)

        if not isinstance(machine_instance, Machine):
          msg = (
            f"Machine '{machine_orm.name}' initialized, but it is not a valid PyLabRobot Machine "
            f"instance. Type is {type(machine_instance).__name__}."
          )
          raise TypeError(msg)

        if (
          hasattr(machine_instance, "setup")
          and isinstance(machine_instance.setup, Awaitable)
          and isinstance(machine_instance.setup, Callable)
        ):
          logger.info(
            "WorkcellRuntime: Calling setup() for '%s'...",
            machine_orm.name,
          )
          try:
            await machine_instance.setup()
          except Exception as e:
            error_message = (
              f"Failed to call setup() for machine '{machine_orm.name}': {str(e)[:250]}"
            )
            raise WorkcellRuntimeError(error_message) from e
        else:
          msg = (
            f"Machine '{machine_orm.name}' does not have a valid setup() method that is callable "
            "and awaitable."
          )
          raise WorkcellRuntimeError(msg)
      except Exception as e:  # pylint: disable=broad-except
        error_message = f"Failed to instantiate or setup machine \
                '{machine_orm.name}'\
                (ID: {machine_orm.accession_id}) using class '{machine_orm.fqn}': \
                {str(e)[:250]}"
        async with runtime.db_session_factory() as db_session:
          await runtime.machine_svc.update_machine_status(
            db_session,
            machine_orm.accession_id,
            MachineStatusEnum.ERROR,
            f"Machine init failed: {str(e)[:250]}",
          )
          await db_session.commit()
        raise WorkcellRuntimeError(error_message) from e

    runtime._active_machines[machine_orm.accession_id] = machine_instance
    runtime._main_workcell.add_asset(machine_instance)
    logger.info(
      "WorkcellRuntime: Machine '%s' (ID: %s) added to main Workcell container.",
      machine_orm.name,
      machine_orm.accession_id,
    )

    if (
      machine_orm.is_resource
      and machine_orm.resource_counterpart
      and machine_orm.resource_counterpart.is_machine
      and machine_orm.resource_counterpart.machine_counterpart
      and machine_orm.resource_counterpart.machine_counterpart.accession_id
      == machine_orm.accession_id
    ):
      resource_orm = machine_orm.resource_counterpart
      if isinstance(machine_instance, Resource):
        runtime._active_resources[resource_orm.accession_id] = cast("Resource", machine_instance)
        logger.info(
          "WorkcellRuntime: Machine '%s' (ID: %s) also registered as Resource "
          "'%s' (ID: %s) in _active_resources, sharing the same PLR object.",
          machine_orm.name,
          machine_orm.accession_id,
          resource_orm.name,
          resource_orm.accession_id,
        )
      else:
        logger.warning(
          "WorkcellRuntime: Machine '%s' (ID: %s) is flagged as a resource "
          "counterpart, but its PLR object type '%s' is not a PyLabRobot Resource"
          " subclass. It will not be registered in _active_resources.",
          machine_orm.name,
          machine_orm.accession_id,
          type(machine_instance).__name__,
        )

    if hasattr(machine_instance, "deck") and isinstance(machine_instance.deck, Deck):
      machine_deck: Deck = cast("LiquidHandler", machine_instance).deck  # type: ignore
      if not isinstance(machine_deck, Deck):
        msg = (
          f"Machine '{machine_orm.name}' has a 'deck' attribute, "
          f"but it is not a Deck instance. Type is {type(machine_deck)}."
        )
        raise TypeError(
          msg,
        )

      async with runtime.db_session_factory() as db_session:
        deck_orm_entry = await runtime.deck_svc.read_decks_by_machine_id(
          db_session,
          machine_orm.accession_id,
        )

        if deck_orm_entry and deck_orm_entry.accession_id is not None:
          runtime._active_decks[deck_orm_entry.accession_id] = machine_deck
          runtime._last_initialized_deck_object = machine_deck
          runtime._last_initialized_deck_orm_accession_id = deck_orm_entry.accession_id
          logger.info(
            "Registered deck (DeckOrm ID: %s, PLR name: '%s') from machine '%s' \
            (ID: %s) to active decks.",
            deck_orm_entry.accession_id,
            machine_deck.name,
            machine_orm.name,
            machine_orm.accession_id,
          )
        else:
          logger.warning(
            "Machine '%s' (ID: %s) has a .deck attribute, but no corresponding DeckOrm \
            entry found with parent_machine_accession_id=%s. Deck not registered in \
              _active_decks.",
            machine_orm.name,
            machine_orm.accession_id,
            machine_orm.accession_id,
          )

    async with runtime.db_session_factory() as db_session:
      await runtime.machine_svc.update_machine_status(
        db_session,
        machine_orm.accession_id,
        MachineStatusEnum.AVAILABLE,
        "Machine initialized successfully.",
      )
      await db_session.commit()
    return machine_instance

  def get_active_machine(self, machine_orm_accession_id: uuid.UUID) -> Machine:
    """Retrieve an active PyLabRobot machine instance by its ORM ID."""
    runtime = cast("WorkcellRuntime", self)
    machine = runtime._active_machines.get(machine_orm_accession_id)
    if machine is None:
      msg = f"Machine with ORM ID {machine_orm_accession_id} not found in active machines."
      raise WorkcellRuntimeError(
        msg,
      )
    if not isinstance(machine, Machine):
      msg = (
        f"Machine with ORM ID {machine_orm_accession_id} is not a valid Machine instance. "
        f"Type is {type(machine)}."
      )
      raise TypeError(msg)
    return machine

  def get_active_machine_accession_id(self, machine: Machine) -> uuid.UUID:
    """Retrieve the ORM ID of an active PyLabRobot machine instance."""
    runtime = cast("WorkcellRuntime", self)
    for orm_accession_id, active_machine in runtime._active_machines.items():
      if active_machine is machine:
        return orm_accession_id
    msg = f"Machine instance {machine} not found in active machines."
    raise WorkcellRuntimeError(
      msg,
    )

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error shutting down machine",
    suffix=" - Ensure the machine ORM ID is valid and the machine is active.",
  )
  async def shutdown_machine(self, machine_orm_accession_id: uuid.UUID) -> None:
    """Shut down and removes a live PyLabRobot machine instance."""
    runtime = cast("WorkcellRuntime", self)
    machine_instance = runtime._active_machines.pop(machine_orm_accession_id, None)
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
          msg = (
            f"No stop() method for {machine_instance.__class__.__name__} machine "
            f"{machine_orm_accession_id} that is callable and awaitable."
          )
          raise WorkcellRuntimeError(msg)
        async with runtime.db_session_factory() as db_session:
          await runtime.machine_svc.update_machine_status(
            db_session,
            machine_orm_accession_id,
            MachineStatusEnum.OFFLINE,
            "Machine shut down.",
          )
          await db_session.commit()

      else:  # pylint: disable=broad-except
        async with runtime.db_session_factory() as db_session:
          await runtime.machine_svc.update_machine_status(
            db_session,
            machine_orm_accession_id,
            MachineStatusEnum.OFFLINE,
            "Machine not found for shutdown.",
          )
          await db_session.commit()
        msg = (
          f"Machine with ID {machine_orm_accession_id} is not currently active and is "
          "unexpectedly offline."
        )
        raise WorkcellRuntimeError(msg)

    except Exception as e:  # pylint: disable=broad-except
      if machine_instance is None:
        msg = f"No active machine instance found for machine ID {machine_orm_accession_id}."
        raise WorkcellRuntimeError(
          msg,
        ) from e
      runtime._active_machines[machine_orm_accession_id] = machine_instance
      async with runtime.db_session_factory() as db_session:
        await runtime.machine_svc.update_machine_status(
          db_session,
          machine_orm_accession_id,
          MachineStatusEnum.ERROR,
          f"Shutdown failed: {str(e)[:250]}",
        )
        await db_session.commit()
      msg = f"Error shutting down machine ID {machine_orm_accession_id}: \
        {str(e)[:250]}"
      raise WorkcellRuntimeError(
        msg,
      ) from e

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
    """Execute a method/action on a live PyLabRobot machine instance."""
    # self = cast("WorkcellRuntime", self) # Not needed for this method strictly speaking if get_active_machine is available
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
    msg = (
      f"Machine for ID {machine_orm_accession_id} (type: {type(machine).__name__}) has no action "
      f"'{action_name}'."
    )
    raise AttributeError(msg)

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error shutting down all machines",
    suffix=" - Ensure all machines are properly initialized and connected.",
  )
  async def shutdown_all_machines(self) -> None:
    """Shut down all currently active PyLabRobot machine instances."""
    runtime = cast("WorkcellRuntime", self)
    logger.info("WorkcellRuntime: Shutting down all active machines...")
    for machine_accession_id in list(runtime._active_machines.keys()):
      try:
        logger.info(
          "WorkcellRuntime: Shutting down machine ID %s...",
          machine_accession_id,
        )
        await self.shutdown_machine(machine_accession_id)
      except WorkcellRuntimeError:
        logger.exception(
          "WorkcellRuntime: Error shutting down machine ID %s",
          machine_accession_id,
        )
        continue
    logger.info("WorkcellRuntime: All active machines processed for shutdown.")
