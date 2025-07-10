# pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements,fixme
"""Decorator for defining Praxis protocol functionality.

praxis/protocol_core/decorators.py

"""

import asyncio
import contextvars
import functools
import inspect
import json
import re
import time
import traceback
import uuid
from collections.abc import Callable
from typing import (
  Any,
  Union,
  get_args,
  get_origin,
)

from pydantic import BaseModel as PydanticBaseModel
from pylabrobot.resources import Deck, Resource
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.core.orchestrator import ProtocolCancelledError
from praxis.backend.core.run_context import (
    PROTOCOL_REGISTRY,
    PraxisRunContext,
    serialize_arguments,
)
from praxis.backend.models.pydantic.protocol import (
    AssetRequirementModel,
    FunctionCallStatusEnum,
    FunctionProtocolDefinitionCreate,
    ParameterMetadataModel,
    ProtocolRunStatusEnum,
    UIHint,
    DecoratedFunctionInfo,
)
from praxis.backend.models.pydantic.asset import CreateProtocolDefinitionData
from praxis.backend.services.protocols import (
    log_function_call_end,
    log_function_call_start,
    update_protocol_run_status,
)
from praxis.backend.utils.logging import get_logger
from praxis.backend.utils.run_control import (
  ALLOWED_COMMANDS,
  clear_control_command,
  get_control_command,
)
from praxis.backend.utils.type_inspection import (
  fqn_from_hint,
  is_pylabrobot_resource,
  serialize_type_hint,
)
from praxis.backend.utils.uuid import uuid7

praxis_run_context_cv: contextvars.ContextVar[PraxisRunContext] = contextvars.ContextVar(
  "praxis_run_context",
)

DEFAULT_DECK_PARAM_NAME = "deck"
DEFAULT_STATE_PARAM_NAME = "state"
TOP_LEVEL_NAME_REGEX = r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$"

logger = get_logger(__name__)


class ProtocolRuntimeInfo:
  """A container for runtime information about a protocol function."""

  def __init__(
    self,
    pydantic_definition: FunctionProtocolDefinitionCreate,
    function_ref: Callable,
    found_state_param_details: dict[str, Any] | None,
  ):
    """Initialize the ProtocolRuntimeInfo.

    Args:
      pydantic_definition (FunctionProtocolDefinitionCreate): The Pydantic model
        definition of the protocol function.
      function_ref (Callable): The actual function reference.
      found_state_param_details (Optional[dict[str, Any]]): Details about the
        state parameter if it exists.

    """
    self.pydantic_definition: FunctionProtocolDefinitionCreate = pydantic_definition
    self.function_ref: Callable = function_ref
    self.callable_wrapper: Callable | None = None
    self.db_accession_id: uuid.UUID | None = None
    self.found_state_param_details: dict[str, Any] | None = found_state_param_details


def get_callable_fqn(func: Callable) -> str:
  """Get the fully qualified name of a callable function.

  Args:
      func (Callable): The callable function.

  Returns:
      str: The fully qualified name (e.g., "module.submodule.function_name").

  """
  return f"{func.__module__}.{func.__qualname__}"


# --- Refactored Helper Functions for the Decorator ---


def _create_protocol_definition(
  data: CreateProtocolDefinitionData,
) -> tuple[FunctionProtocolDefinitionCreate, dict[str, Any] | None]:
  """Parse a function signature and decorator args to create a protocol definition."""
  resolved_name = data.name or data.func.__name__
  if not resolved_name:
    raise ValueError(
      "Protocol function name cannot be empty (either provide 'name' argument or use "
      "a named function).",
    )
  if (
    data.is_top_level
    and data.top_level_name_format
    and not re.match(data.top_level_name_format, resolved_name)
  ):
    raise ValueError(
      f"Top-level protocol name '{resolved_name}' does not match format: "
      f"{data.top_level_name_format}",
    )

  sig = inspect.signature(data.func)
  parameters_list: list[ParameterMetadataModel] = []
  assets_list: list[AssetRequirementModel] = []
  found_deck_param = False
  found_state_param_details: dict[str, Any] | None = None

  for param_name_sig, param_obj in sig.parameters.items():
    parameters_list, assets_list, found_deck_param, found_state_param_details = (
      self._process_parameter(
        param_name_sig,
        param_obj,
        data,
        parameters_list,
        assets_list,
        found_deck_param,
        found_state_param_details,
      )
    )

  if data.preconfigure_deck and not found_deck_param:
    raise TypeError(
      f"Protocol '{resolved_name}' (preconfigure_deck=True) missing "
      f"'{data.deck_param_name}' param.",
    )
  if data.is_top_level and not found_state_param_details:
    raise TypeError(
      f"Top-level protocol '{resolved_name}' must define a '{data.state_param_name}' " "parameter.",
    )

  protocol_definition = FunctionProtocolDefinitionCreate(
    accession_id=uuid7(),
    name=resolved_name,
    version=data.version,
    description=(data.description or inspect.getdoc(data.func) or "No description provided."),
    source_file_path=inspect.getfile(data.func),
    module_name=data.func.__module__,
    function_name=data.func.__name__,
    is_top_level=data.is_top_level,
    solo_execution=data.solo,
    preconfigure_deck=data.preconfigure_deck,
    deck_param_name=data.deck_param_name if data.preconfigure_deck else None,
    deck_construction_function_fqn=(
      get_callable_fqn(data.deck_construction) if data.deck_construction else None
    ),
    state_param_name=data.state_param_name,
    category=data.category,
    tags=data.tags,
    parameters=parameters_list,
    assets=assets_list,
  )
  return protocol_definition, found_state_param_details


def _process_parameter(
  param_name_sig: str,
  param_obj: inspect.Parameter,
  data: CreateProtocolDefinitionData,
  parameters_list: list[ParameterMetadataModel],
  assets_list: list[AssetRequirementModel],
  found_deck_param: bool,
  found_state_param_details: dict[str, Any] | None,
) -> tuple[list[ParameterMetadataModel], list[AssetRequirementModel], bool, dict[str, Any] | None]:
  param_type_hint = param_obj.annotation
  is_optional_param = (
    get_origin(param_type_hint) is Union and type(None) in get_args(param_type_hint)
  ) or (param_obj.default is not inspect.Parameter.empty)
  fqn = fqn_from_hint(param_type_hint)
  param_meta_entry = data.param_metadata.get(param_name_sig, {})
  p_description = param_meta_entry.get("description")
  p_constraints = param_meta_entry.get("constraints_json", {})
  p_ui_hints_dict = param_meta_entry.get("ui_hints")
  p_ui_hints = UIHint(**p_ui_hints_dict) if isinstance(p_ui_hints_dict, dict) else None

  common_model_args = {
    "name": param_name_sig,
    "type_hint": serialize_type_hint(param_type_hint),
    "fqn": fqn,
    "optional": is_optional_param,
    "default_value_repr": repr(param_obj.default)
    if param_obj.default is not inspect.Parameter.empty
    else None,
    "description": p_description,
    "constraints_json": p_constraints if isinstance(p_constraints, dict) else {},
    "ui_hints": p_ui_hints,
  }

  if data.preconfigure_deck and param_name_sig == data.deck_param_name:
    parameters_list.append(
      ParameterMetadataModel(**common_model_args, is_deck_param=True),
    )
    found_deck_param = True
  elif param_name_sig == data.state_param_name:
    is_state_type_match = fqn in {"PraxisState", "praxis.backend.core.definitions.PraxisState"}
    is_dict_type_match = fqn == "dict"
    found_state_param_details = {
      "name": param_name_sig,
      "expects_praxis_state": is_state_type_match,
      "expects_dict": is_dict_type_match,
    }
    parameters_list.append(ParameterMetadataModel(**common_model_args))
  else:
    type_for_plr_check = param_type_hint
    origin_check = get_origin(param_type_hint)
    args_check = get_args(param_type_hint)
    if origin_check is Union and type(None) in args_check:
      non_none_args = [arg for arg in args_check if arg is not type(None)]
      if len(non_none_args) == 1:
        type_for_plr_check = non_none_args[0]

    if is_pylabrobot_resource(type_for_plr_check):
      assets_list.append(AssetRequirementModel(**common_model_args))
    else:
      parameters_list.append(ParameterMetadataModel(**common_model_args))
  return parameters_list, assets_list, found_deck_param, found_state_param_details


async def _prepare_function_arguments(
  func: Callable,
  kwargs: dict,
  context_for_this_call: PraxisRunContext,
  found_state_param_details: dict[str, Any] | None,
  state_param_name: str,
) -> dict:
  processed_kwargs_for_call = dict(kwargs)
  sig_check = inspect.signature(func)
  if "__praxis_run_context__" in sig_check.parameters:
    processed_kwargs_for_call["__praxis_run_context__"] = context_for_this_call
  elif (
    found_state_param_details
    and found_state_param_details["name"] == state_param_name
    and sig_check.parameters[state_param_name].annotation == PraxisRunContext
  ):
    processed_kwargs_for_call[state_param_name] = context_for_this_call

  if (
    "__praxis_run_context__" in processed_kwargs_for_call
    and "__praxis_run_context__" not in func.__code__.co_varnames
    and not any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig_check.parameters.values())
  ):
    del processed_kwargs_for_call["__praxis_run_context__"]
  return processed_kwargs_for_call


async def _log_call_start(
  context: PraxisRunContext,
  function_def_db_id: uuid.UUID,
  parent_log_id: uuid.UUID | None,
  args: tuple,
  kwargs: dict,
) -> uuid.UUID | None:
  """Log the start of a function call and return its database ID."""
  try:
    sequence_val = context.get_and_increment_sequence_val()
    serialized_input_args = serialize_arguments(args, kwargs)
    call_log_entry_orm = await log_function_call_start(
      db=context.current_db_session,
      protocol_run_orm_accession_id=context.run_accession_id,
      function_definition_accession_id=function_def_db_id,
      sequence_in_run=sequence_val,
      input_args_json=serialized_input_args,
      parent_function_call_log_accession_id=parent_log_id,
    )
    return call_log_entry_orm.accession_id
  except Exception:  # pylint: disable=broad-except
    logger.exception(
      "Failed to log function call start for run %s",
      context.run_accession_id,
    )
    return None


def protocol_function(
  data: DecoratedFunctionInfo,
):
  """Decorate a function for use as a Praxis protocol.

  This decorator registers the function as a protocol with metadata and
  allows it to be executed within the Praxis orchestrator context.

  Args:
    name (Optional[str]): Name of the protocol function. If not provided,
      the function's name will be used.
    version (str): Version of the protocol function.
    description (Optional[str]): Description of the protocol function.
    solo (bool): If True, the protocol can be executed independently.
    is_top_level (bool): If True, this is a top-level protocol that can be
      called directly by the orchestrator.
    preconfigure_deck (bool): If True, the protocol expects a deck parameter
      for pre-configuration.
    deck_param_name (str): Name of the deck parameter if preconfigure_deck is True.
    deck_construction (Optional[Callable]): Function to construct the deck.
      This is used when preconfigure_deck is True.
    state_param_name (str): Name of the state parameter for top-level protocols.
    param_metadata (Optional[dict[str, dict[str, Any]]]): Metadata for parameters.
    category (Optional[str]): Category for organizing protocols.
    tags (Optional[list[str]]): Tags for additional categorization.
    top_level_name_format (Optional[str]): Regex format for top-level protocol names.

  """
  actual_param_metadata = param_metadata or {}
  actual_tags = tags or []

  def decorator(func: Callable):
    protocol_definition, found_state_param_details = _create_protocol_definition(
      FunctionProtocolDefinitionCreate(
        func=func,
        name=name,
        version=version,
        description=description,
        solo=solo,
        is_top_level=is_top_level,
        preconfigure_deck=preconfigure_deck,
        deck_param_name=deck_param_name,
        deck_construction=deck_construction,
        state_param_name=state_param_name,
        param_metadata=actual_param_metadata,
        category=category,
        tags=actual_tags,
        top_level_name_format=top_level_name_format,
      ),
    )
    func._protocol_definition = protocol_definition

    _register_protocol(protocol_definition, func, found_state_param_details)

    protocol_unique_key = f"{protocol_definition.name}_v{protocol_definition.version}"
    PROTOCOL_REGISTRY[protocol_unique_key] = protocol_runtime_info

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
      current_meta = PROTOCOL_REGISTRY.get(protocol_unique_key)
      if not current_meta or not current_meta.db_accession_id:
        raise RuntimeError(
          f"Protocol '{protocol_unique_key}' not registered or missing DB ID.",
        )

      parent_context = praxis_run_context_cv.get()
      if parent_context is None:
        raise RuntimeError(
          "No PraxisRunContext found in contextvars. Ensure this function is called "
          "within a valid Praxis run context.",
        )

      (
        current_call_log_db_accession_id,
        context_for_this_call,
        token,
      ) = await _process_wrapper_arguments(
        parent_context,
        current_meta,
        list(args),
        dict(kwargs),
        state_param_name,
        protocol_unique_key,  # Pass protocol_unique_key
        func,  # Pass func
      )

      result = None
      error = None
      status_enum_val = FunctionCallStatusEnum.SUCCESS
      start_time_perf = time.perf_counter()

      try:
        processed_kwargs_for_call = await _prepare_function_arguments(
          func,
          kwargs,
          context_for_this_call,
          current_meta.found_state_param_details,
          state_param_name,
        )

        if inspect.iscoroutinefunction(func):
          result = await func(*args, **processed_kwargs_for_call)
        else:
          loop = asyncio.get_running_loop()
          result = await loop.run_in_executor(
            None,
            functools.partial(func, *args, **processed_kwargs_for_call),
          )

      except ProtocolCancelledError:
        raise
      except Exception as e:
        # This is a broad exception catch because it wraps user-written protocol code,
        # which could raise any type of exception. We must catch it to ensure proper
        # logging and state management before re-raising.
        error = e
        status_enum_val = FunctionCallStatusEnum.ERROR
        logger.exception(
          "Error in protocol function '%s' (Run: %s)",
          protocol_unique_key,
          context_for_this_call.run_accession_id,
        )
      finally:
        praxis_run_context_cv.reset(token)
        end_time_perf = time.perf_counter()
        duration_ms = (end_time_perf - start_time_perf) * 1000

        try:
          serialized_result = None
          if error is None:
            if isinstance(result, PydanticBaseModel):
              try:
                serialized_result = result.model_dump_json(exclude_none=True)
              except AttributeError:
                serialized_result = json.dumps(result, default=str)
            elif isinstance(result, (Resource, Deck)):
              serialized_result = json.dumps(repr(result))
            else:
              try:
                serialized_result = json.dumps(result, default=str)
              except TypeError:
                serialized_result = json.dumps(repr(result))

          if current_call_log_db_accession_id:
            await log_function_call_end(
              db=context_for_this_call.current_db_session,
              function_call_log_accession_id=current_call_log_db_accession_id,
              status=status_enum_val,
              return_value_json=serialized_result,
              error_message=str(error) if error else None,
              error_traceback=traceback.format_exc() if error else None,
              duration_ms=duration_ms,
            )
        except Exception:  # pylint: disable=broad-except
          # Broad except is justified here as we must not let a logging failure
          # interrupt the protocol's exception propagation.
          logger.exception(
            "Failed to log function call end for '%s'",
            protocol_definition.name,
          )

      if error:
        if isinstance(error, ProtocolCancelledError):
          raise error
        raise error
      return result

    return wrapper

  return decorator


async def _process_wrapper_arguments(
  parent_context: PraxisRunContext,
  current_meta: ProtocolRuntimeInfo,
  processed_args: list,
  processed_kwargs: dict,
  state_param_name: str,
  protocol_unique_key: str,  # Added
  func: Callable,  # Added
) -> tuple[uuid.UUID, PraxisRunContext, contextvars.Token]:
  this_function_def_db_accession_id = current_meta.db_accession_id
  state_details = current_meta.found_state_param_details

  if state_details:
    state_arg_name_in_sig = state_details["name"]
    if state_arg_name_in_sig in processed_kwargs:
      del processed_kwargs[state_arg_name_in_sig]
    if state_details["expects_praxis_state"]:
      processed_kwargs[state_arg_name_in_sig] = parent_context.canonical_state
    elif state_details["expects_dict"]:
      if state_arg_name_in_sig not in processed_kwargs:
        processed_kwargs[state_arg_name_in_sig] = (
          parent_context.canonical_state.data.copy() if parent_context.canonical_state else {}
        )

  current_call_log_db_accession_id: uuid.UUID | None = None
  parent_log_accession_id_for_this_call = parent_context.current_call_log_db_accession_id

  current_call_log_db_accession_id = await _log_call_start(
    context=parent_context,
    function_def_db_id=this_function_def_db_accession_id,
    parent_log_id=parent_log_accession_id_for_this_call,
    args=tuple(processed_args),
    kwargs=processed_kwargs,
  )
  if not current_call_log_db_accession_id:
    raise RuntimeError("Failed to log function call start.")

  context_for_this_call = parent_context.create_context_for_nested_call(
    new_parent_call_log_db_accession_id=current_call_log_db_accession_id,
  )
  token = praxis_run_context_cv.set(context_for_this_call)
  return current_call_log_db_accession_id, context_for_this_call, token

  return decorator


async def _handle_pause_state(
  run_accession_id: uuid.UUID,
  db_session: AsyncSession,
) -> str:
  """Handle the logic when a protocol is in a PAUSED state, waiting for a command."""
  while True:
    await asyncio.sleep(1)
    command = await get_control_command(run_accession_id)

    if command in ["RESUME", "CANCEL"]:
      logger.info(
        "Received command '%s' while PAUSED for run %s.",
        command,
        run_accession_id,
      )
      return command

    if command == "INTERVENE":
      await clear_control_command(run_accession_id)
      logger.info("Protocol run %s INTERVENING during pause.", run_accession_id)
      await update_protocol_run_status(
        db_session,
        run_accession_id,
        ProtocolRunStatusEnum.INTERVENING,
      )
      await db_session.commit()
      # TODO: Dispatch to intervention handler

    elif command == "PAUSE":
      logger.info(
        "Received PAUSE command while already PAUSED for run %s. Ignoring.",
        run_accession_id,
      )
      continue

    elif command and command not in ALLOWED_COMMANDS:
      logger.warning(
        "Invalid command '%s' while PAUSED for run %s. Clearing.",
        command,
        run_accession_id,
      )
      await clear_control_command(run_accession_id)


async def _handle_control_commands(
  run_accession_id: uuid.UUID,
  db_session: AsyncSession,
) -> None:
  """Check for and handle control commands like PAUSE and CANCEL before execution."""
  while True:
    command = await get_control_command(run_accession_id)
    if not command:
      break  # No command, proceed with execution

    if command not in ALLOWED_COMMANDS:
      logger.warning(
        "Invalid control command '%s' for run %s. Clearing.",
        command,
        run_accession_id,
      )
      await clear_control_command(run_accession_id)
      continue

    if command == "PAUSE":
      await clear_control_command(run_accession_id)
      logger.info("Protocol run %s PAUSING.", run_accession_id)
      await update_protocol_run_status(
        db_session,
        run_accession_id,
        ProtocolRunStatusEnum.PAUSING,
      )
      await db_session.commit()
      await update_protocol_run_status(
        db_session,
        run_accession_id,
        ProtocolRunStatusEnum.PAUSED,
      )
      await db_session.commit()

      next_command = await _handle_pause_state(run_accession_id, db_session)

      if next_command == "RESUME":
        await clear_control_command(run_accession_id)
        logger.info("Protocol run %s RESUMING.", run_accession_id)
        await update_protocol_run_status(
          db_session,
          run_accession_id,
          ProtocolRunStatusEnum.RESUMING,
        )
        await db_session.commit()
        await update_protocol_run_status(
          db_session,
          run_accession_id,
          ProtocolRunStatusEnum.RUNNING,
        )
        await db_session.commit()
        continue  # Re-check for commands immediately after resuming

      if next_command == "CANCEL":
        await clear_control_command(run_accession_id)
        logger.info("Protocol run %s CANCELLING after pause.", run_accession_id)
        await update_protocol_run_status(
          db_session,
          run_accession_id,
          ProtocolRunStatusEnum.CANCELING,
        )
        await db_session.commit()
        await update_protocol_run_status(
          db_session,
          run_accession_id,
          ProtocolRunStatusEnum.CANCELLED,
          output_data_json=json.dumps({"status": "Cancelled by user."}),
        )
        await db_session.commit()
        raise ProtocolCancelledError(f"Run {run_accession_id} cancelled by user.")

    elif command == "CANCEL":
      await clear_control_command(run_accession_id)
      logger.info("Protocol run %s CANCELLING.", run_accession_id)
      await update_protocol_run_status(
        db_session,
        run_accession_id,
        ProtocolRunStatusEnum.CANCELING,
      )
      await db_session.commit()
      await update_protocol_run_status(
        db_session,
        run_accession_id,
        ProtocolRunStatusEnum.CANCELLED,
        output_data_json=json.dumps({"status": "Cancelled by user."}),
      )
      await db_session.commit()
      raise ProtocolCancelledError(f"Run {run_accession_id} cancelled by user.")

    elif command == "INTERVENE":
      await clear_control_command(run_accession_id)
      logger.info("Protocol run %s INTERVENING.", run_accession_id)
      await update_protocol_run_status(
        db_session,
        run_accession_id,
        ProtocolRunStatusEnum.INTERVENING,
      )
      await db_session.commit()
      # TODO: dispatch to intervention handler
