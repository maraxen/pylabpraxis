# pylint: disable=too-many-arguments, broad-except, fixme
"""Deck management for WorkcellRuntime."""

import inspect
import uuid
from typing import TYPE_CHECKING, Any, cast

from pylabrobot.resources import Coordinate, Deck

if TYPE_CHECKING:
  from praxis.backend.core.workcell_runtime.core import WorkcellRuntime

from praxis.backend.core.workcell_runtime.utils import log_workcell_runtime_errors
from praxis.backend.models import (
  PositioningConfig,
  ResourceOrm,
  ResourceStatusEnum,
)
from praxis.backend.models.pydantic_internals.filters import SearchFilters
from praxis.backend.utils.errors import WorkcellRuntimeError
from praxis.backend.utils.logging import get_logger

logger = get_logger(__name__)

COORDINATE_TUPLE_LENGTH = 3


class DeckManagerMixin:

  """Mixin for managing decks in WorkcellRuntime."""

  def get_active_deck_accession_id(self, deck: Deck) -> uuid.UUID:
    """Retrieve the ORM ID of an active PyLabRobot Deck instance."""
    runtime = cast("WorkcellRuntime", self)
    for orm_accession_id, active_deck in runtime._active_decks.items():
      if active_deck is deck:
        return orm_accession_id
    msg = f"Deck instance {deck} not found in active decks."
    raise WorkcellRuntimeError(msg)

  def get_active_deck(self, deck_orm_accession_id: uuid.UUID) -> Deck:
    """Retrieve an active PyLabRobot Deck instance by its ORM ID."""
    runtime = cast("WorkcellRuntime", self)
    deck = runtime._active_decks.get(deck_orm_accession_id)
    if deck is None:
      msg = f"Deck with ORM ID {deck_orm_accession_id} not found in active decks."
      raise WorkcellRuntimeError(
        msg,
      )
    if not isinstance(deck, Deck):
      msg = (
        f"Deck with ORM ID {deck_orm_accession_id} is not a valid PyLabRobot Deck instance. "
        f"Type is {type(deck)}."
      )
      raise TypeError(msg)
    return deck

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
  ) -> None:
    """Assign a live Resource to a specific location or position on a deck."""
    runtime = cast("WorkcellRuntime", self)
    if location is None and position_accession_id is None:
      msg = (
        "Either 'location' or 'position_accession_id' must be provided to assign a resource to "
        "a deck."
      )
      raise WorkcellRuntimeError(msg)

    if target in runtime._active_machines:
      inferred_target_type = "machine_orm_accession_id"
    elif target in runtime._active_decks:
      inferred_target_type = "deck_orm_accession_id"
    else:
      msg = f"Target ORM ID {target} not found in active machines or decks."
      raise WorkcellRuntimeError(
        msg,
      )

    resource = runtime.get_active_resource(resource_orm_accession_id)

    match inferred_target_type:
      case "deck_orm_accession_id":
        deck_orm_accession_id = target
        target_deck = runtime.get_active_deck(deck_orm_accession_id)
      case "machine_orm_accession_id":
        machine_orm_accession_id = target
        target_machine = runtime.get_active_machine(machine_orm_accession_id)
        target_deck = getattr(target_machine, "deck", None)
        if not isinstance(target_deck, Deck):
          msg = f"Machine ID {machine_orm_accession_id} does not have an associated deck."
          raise WorkcellRuntimeError(
            msg,
          )
        deck_orm_accession_id = runtime.get_active_deck_accession_id(target_deck)
      case _:
        msg = f"Unexpected target type: {inferred_target_type}. Expected deck_orm_accession_id or \
            machine_orm_accession_id."
        raise WorkcellRuntimeError(
          msg,
        )

    async with runtime.db_session_factory() as db_session:
      deck_orm = await runtime.deck_svc.get(db=db_session, accession_id=deck_orm_accession_id)
      if deck_orm is None:
        msg = f"Deck ORM ID {deck_orm_accession_id} not found in database."
        raise WorkcellRuntimeError(msg)

      # Check for occupancy if assigning to a named position
      if position_accession_id is not None:
        existing_resources = await runtime.resource_svc.get_multi(
          db=db_session,
          filters=SearchFilters(
            search_filters={
              "location_machine_accession_id": deck_orm.accession_id,
              "current_deck_position_name": str(position_accession_id),
            },
          ),
        )
        for res in existing_resources:
          if res.accession_id != resource_orm_accession_id:
            msg = (
              f"Position '{position_accession_id}' on deck ID {deck_orm.accession_id} "
              f"is already occupied by resource '{res.name}' (ID: {res.accession_id})."
            )
            raise WorkcellRuntimeError(msg)

      deck_orm_type_definition_accession_id = deck_orm.deck_type_id

      if deck_orm_type_definition_accession_id is None:
        msg = f"Deck ORM ID {deck_orm_accession_id} does not have a valid deck type definition."
        raise WorkcellRuntimeError(msg)

      deck_type_definition_orm = await runtime.deck_type_definition_svc.get(
        db=db_session,
        accession_id=deck_orm_type_definition_accession_id,
      )

      if deck_type_definition_orm is None:
        msg = f"Deck type definition for deck ORM ID {deck_orm_accession_id} not found in database."
        raise WorkcellRuntimeError(msg)

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
        final_location_for_plr = await runtime._get_calculated_location(
          target_deck=target_deck,
          deck_type_id=deck_type_definition_orm.accession_id,
          position_accession_id=position_accession_id,
          positioning_config=positioning_config,
        )
      else:
        msg = (
          "Internal error: Neither location nor position_accession_id provided after initial check."
        )
        raise WorkcellRuntimeError(msg)

      try:
        target_deck.assign_child_resource(
          resource=resource,
          location=final_location_for_plr,
        )
        await runtime.resource_svc.update_resource_location_and_status(
          db=db_session,
          resource_accession_id=resource_orm_accession_id,
          new_status=ResourceStatusEnum.AVAILABLE_ON_DECK,
          location_machine_accession_id=deck_orm.accession_id,
          current_deck_position_name=str(position_accession_id),
        )
        await db_session.commit()
      except Exception as e:  # pylint: disable=broad-except
        msg = (
          f"Error assigning resource '{resource.name}' to  "
          f"location {final_location_for_plr} on deck ID {deck_orm.accession_id}: {str(e)[:250]}"
        )
        raise WorkcellRuntimeError(
          msg,
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
  ) -> None:
    """Clear a resource from a specific position on a live deck."""
    runtime = cast("WorkcellRuntime", self)
    deck = runtime.get_active_deck(deck_orm_accession_id)

    if not isinstance(deck, Deck):
      msg = (
        "Deck from workcell runtime is not a Deck instance."
        "This indicates a major error as non-Deck objects"
        " should not be in the active decks."
      )
      raise WorkcellRuntimeError(
        msg,
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
      async with runtime.db_session_factory() as db_session:
        await runtime.resource_svc.update_resource_location_and_status(
          db=db_session,
          resource_accession_id=resource_orm_accession_id,
          new_status=ResourceStatusEnum.AVAILABLE_IN_STORAGE,
          location_machine_accession_id=None,
          current_deck_position_name=None,
        )
        await db_session.commit()

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error getting deck state representation",
    suffix=" - Ensure the deck ORM ID is valid and the deck is active.",
  )
  async def get_deck_state_representation(
    self,
    deck_orm_accession_id: uuid.UUID,
  ) -> dict[str, Any]:
    """Construct a dictionary representing the state of a specific deck."""
    runtime = cast("WorkcellRuntime", self)
    async with runtime.db_session_factory() as db_session:
      deck_orm = await runtime.deck_svc.get(db=db_session, accession_id=deck_orm_accession_id)

      if deck_orm is None or not hasattr(deck_orm, "id") or deck_orm.accession_id is None:
        msg = f"Deck ORM ID {deck_orm_accession_id} not found in database."
        raise WorkcellRuntimeError(msg)

      response_positions: list[dict[str, Any]] = []

      resources_on_deck: list[ResourceOrm] = await runtime.resource_svc.get_multi(
        db=db_session,
        filters=SearchFilters(
          search_filters={"location_machine_accession_id": deck_orm.accession_id},
        ),
      )

      for lw_instance in resources_on_deck:
        if lw_instance.current_deck_position_name is not None:
          if not hasattr(lw_instance, "resource_definition") or not lw_instance.resource_definition:
            logger.warning(
              "Resource instance ID %s is missing resource_definition relationship. Skipping.",
              lw_instance.accession_id,
            )
            continue
          lw_def = lw_instance.resource_definition

          lw_active_instance = runtime.get_active_resource(lw_instance.accession_id)

          lw_active_coords = lw_active_instance.get_absolute_location()

          resource_info_data = {
            "resource_accession_id": lw_instance.accession_id,
            "name": (lw_def.name or lw_instance.name or f"Resource_{lw_instance.accession_id}"),
            "fqn": lw_def.fqn,
            "category": str(lw_def.plr_category) if lw_def.plr_category else None,
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

      live_deck = runtime.get_active_deck(deck_orm_accession_id)
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
        except Exception as e:  # pylint: disable=broad-except
          logger.warning(
            "Could not get size from live deck object for ID %s: %s",
            deck_orm_accession_id,
            e,
          )

      return {
        "deck_accession_id": deck_orm.accession_id,
        "name": deck_orm.name or f"Deck_{deck_orm.accession_id}",
        "fqn": deck_orm.fqn,
        "size_x_mm": deck_size_x,
        "size_y_mm": deck_size_y,
        "size_z_mm": deck_size_z,
        "positions": response_positions,
      }

  async def get_last_initialized_deck_object(self) -> Deck | None:
    """Return the Deck most recently initialized by this runtime instance."""
    runtime = cast("WorkcellRuntime", self)
    if runtime._last_initialized_deck_object:
      return runtime._last_initialized_deck_object
    return None

  @log_workcell_runtime_errors(
    prefix="WorkcellRuntime: Error encountered calculating location from deck position",
    suffix=" - Ensure the deck type definition exists in the database.",
  )
  async def _get_calculated_location(
    self,
    target_deck: Deck,
    deck_type_id: uuid.UUID,
    position_accession_id: str | int | uuid.UUID,
    positioning_config: PositioningConfig | None,
  ) -> Coordinate:
    """Calculate the PyLabRobot Coordinate for a given position_accession_id."""
    runtime = cast("WorkcellRuntime", self)
    if positioning_config is None:
      logger.info(
        "No general positioning config for deck type ID %s, "
        "attempting to find position in DeckPositionDefinitionOrm.",
        deck_type_id,
      )
      if isinstance(position_accession_id, str | int | uuid.UUID):
        async with runtime.db_session_factory() as db_session:
          deck_type_definition = await runtime.deck_type_definition_svc.get(
            db=db_session,
            accession_id=deck_type_id,
          )
          if not deck_type_definition:
            msg = f"Deck type definition with ID {deck_type_id} not found."
            raise WorkcellRuntimeError(msg)
          all_deck_position_definitions = deck_type_definition.positions
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
            and found_position_def.nominal_x_mm
            and found_position_def.nominal_y_mm
          ):
            return Coordinate(
              x=found_position_def.nominal_x_mm,
              y=found_position_def.nominal_y_mm,
              z=found_position_def.nominal_z_mm
              if found_position_def.nominal_z_mm is not None
              else 0.0,
            )
          msg = (
            f"Position '{position_accession_id}' not found in predefined deck position "
            f"definitions for deck type ID {deck_type_id}."
          )
          raise WorkcellRuntimeError(
            msg,
          )
      else:
        msg = (
          f"No positioning configuration provided for deck type ID "
          f"{deck_type_id}. Cannot determine position location."
        )
        raise WorkcellRuntimeError(
          msg,
        )
    else:
      method_name = positioning_config.method_name
      arg_name = positioning_config.arg_name
      arg_type = positioning_config.arg_type
      method_params = positioning_config.params or {}

      position_method = getattr(target_deck, method_name, None)
      if position_method is None or not callable(position_method):
        msg = f"Deck does not have a valid position method '{method_name}' as configured."
        raise WorkcellRuntimeError(
          msg,
        )

      converted_position_arg: str | int
      if arg_type == "int":
        try:
          converted_position_arg = int(position_accession_id)
        except (ValueError, TypeError) as e:
          msg = (
            f"Expected integer for position_accession_id '{position_accession_id}' for method "
            f"'{method_name}' but got invalid type/value: {e}"
          )
          raise TypeError(
            msg,
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
        msg = (
          f"Error calling PLR method '{method_name}' with arguments "
          f"'{arg_name}={converted_position_arg}' and params '{method_params}': {e}. "
          "Check if method signature matches configuration."
        )
        raise WorkcellRuntimeError(
          msg,
        ) from e
      except Exception as e:  # pylint: disable=broad-except
        logger.exception("Unexpected error when calling PLR method '%s'", method_name)
        msg = f"Unexpected error when calling PLR method '{method_name}': {e}"
        raise WorkcellRuntimeError(
          msg,
        ) from e

      if not isinstance(calculated_location, Coordinate):
        if (
          isinstance(calculated_location, tuple)
          and len(calculated_location) == COORDINATE_TUPLE_LENGTH
        ):
          calculated_location = Coordinate(
            x=calculated_location[0],
            y=calculated_location[1],
            z=calculated_location[2],
          )
        else:
          msg = (
            f"Expected PLR method '{method_name}' to return a Coordinate or (x,y,z) "
            f"tuple, but got {type(calculated_location)}: {calculated_location}"
          )
          raise TypeError(
            msg,
          )
      return calculated_location
