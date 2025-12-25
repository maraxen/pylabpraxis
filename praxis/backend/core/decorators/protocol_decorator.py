import asyncio
import contextvars
import functools
import inspect
import json
import time
import traceback
import uuid
from collections.abc import Callable
from typing import Any, cast

from pydantic import BaseModel as PydanticBaseModel
from pylabrobot.resources import Deck, Resource
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.core.orchestrator import ProtocolCancelledError
from praxis.backend.core.run_context import (
  PraxisRunContext,
  serialize_arguments,
)
from praxis.backend.models.pydantic_internals.protocol import (
  FunctionCallStatusEnum,
  ProtocolRunStatusEnum,
)
from praxis.backend.services.protocols import (
  log_function_call_end,
  log_function_call_start,
  protocol_run_service,
)
from praxis.backend.utils.logging import get_logger
from praxis.backend.utils.run_control import (
  ALLOWED_COMMANDS,
  clear_control_command,
  get_control_command,
)

from .definition_builder import _create_protocol_definition
from .models import (
  DEFAULT_DECK_PARAM_NAME,
  DEFAULT_STATE_PARAM_NAME,
  TOP_LEVEL_NAME_REGEX,
  CreateProtocolDefinitionData,
  ProtocolRuntimeInfo,
  praxis_run_context_cv,
)

logger = get_logger(__name__)


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


async def _process_wrapper_arguments(
  parent_context: PraxisRunContext,
  current_meta: ProtocolRuntimeInfo,
  processed_args: list,
  processed_kwargs: dict,
  *,
  _state_param_name: str,
  _protocol_unique_key: str,
  _func: Callable,
) -> tuple[uuid.UUID, PraxisRunContext, contextvars.Token]:
  this_function_def_db_accession_id = current_meta.db_accession_id
  if this_function_def_db_accession_id is None:
    msg = "Function definition DB accession ID is missing."
    raise ValueError(msg)

  state_details = current_meta.found_state_param_details

  if state_details:
    state_arg_name_in_sig = state_details["name"]
    processed_kwargs.pop(state_arg_name_in_sig, None)
    if state_details["expects_praxis_state"]:
      processed_kwargs[state_arg_name_in_sig] = parent_context.canonical_state
    elif state_details["expects_dict"] and state_arg_name_in_sig not in processed_kwargs:
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
    msg = "Failed to log function call start."
    raise RuntimeError(msg)

  context_for_this_call = parent_context.create_context_for_nested_call(
    new_parent_call_log_db_accession_id=current_call_log_db_accession_id,
  )
  token = praxis_run_context_cv.set(context_for_this_call)
  return current_call_log_db_accession_id, context_for_this_call, token


def protocol_function(
  name: str | None = None,
  version: str = "0.1.0",
  description: str | None = None,
  *,
  solo: bool = False,
  is_top_level: bool = False,
  preconfigure_deck: bool = False,
  deck_param_name: str = DEFAULT_DECK_PARAM_NAME,
  deck_construction: Callable | None = None,
  state_param_name: str = DEFAULT_STATE_PARAM_NAME,
  param_metadata: dict[str, Any] | None = None,
  category: str | None = None,
  tags: list[str] | None = None,
  top_level_name_format: str = TOP_LEVEL_NAME_REGEX,
) -> Callable:
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

  def decorator(func: Callable) -> Callable:
    protocol_definition, found_state_param_details = _create_protocol_definition(
      CreateProtocolDefinitionData(
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
    cast("Any", func)._protocol_definition = protocol_definition

    # TODO: The protocol registration should be handled by a discovery service.
    # _register_protocol(protocol_definition, func, found_state_param_details)

    # Create the runtime info object and attach it to the function.
    # This avoids using a global registry and allows for service-based discovery.
    protocol_runtime_info = ProtocolRuntimeInfo(
      pydantic_definition=protocol_definition,
      function_ref=func,
      found_state_param_details=found_state_param_details,
    )
    cast("Any", func)._protocol_runtime_info = protocol_runtime_info

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
      # Get the runtime metadata from the function itself, not a global registry.
      current_meta = func._protocol_runtime_info
      protocol_unique_key = (
        f"{current_meta.pydantic_definition.name}_v{current_meta.pydantic_definition.version}"
      )

      if not current_meta or not current_meta.db_accession_id:
        msg = f"Protocol '{protocol_unique_key}' not registered or missing DB ID."
        raise RuntimeError(
          msg,
        )

      parent_context = praxis_run_context_cv.get(None)
      if parent_context is None:
        msg = (
          "No PraxisRunContext found in contextvars. Ensure this function is called "
          "within a valid Praxis run context."
        )
        raise RuntimeError(
          msg,
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
        _state_param_name=state_param_name,
        _protocol_unique_key=protocol_unique_key,
        _func=func,
      )

      # Check for control commands (PAUSE/CANCEL) before executing the function
      # This allows the protocol to be interrupted at any decorated step
      try:
        await _handle_control_commands(
            context_for_this_call.run_accession_id,
            context_for_this_call.current_db_session
        )
      except ProtocolCancelledError:
        # Re-raise cancellation to be caught by the outer try/except block
        raise

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
            elif isinstance(result, Resource | Deck):
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
      await protocol_run_service.update_run_status(
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
      await protocol_run_service.update_run_status(
        db_session,
        run_accession_id,
        ProtocolRunStatusEnum.PAUSING,
      )
      await db_session.commit()
      await protocol_run_service.update_run_status(
        db_session,
        run_accession_id,
        ProtocolRunStatusEnum.PAUSED,
      )
      await db_session.commit()

      next_command = await _handle_pause_state(run_accession_id, db_session)

      if next_command == "RESUME":
        await clear_control_command(run_accession_id)
        logger.info("Protocol run %s RESUMING.", run_accession_id)
        await protocol_run_service.update_run_status(
          db_session,
          run_accession_id,
          ProtocolRunStatusEnum.RESUMING,
        )
        await db_session.commit()
        await protocol_run_service.update_run_status(
          db_session,
          run_accession_id,
          ProtocolRunStatusEnum.RUNNING,
        )
        await db_session.commit()
        continue  # Re-check for commands immediately after resuming

      if next_command == "CANCEL":
        await clear_control_command(run_accession_id)
        logger.info("Protocol run %s CANCELLING after pause.", run_accession_id)
        await protocol_run_service.update_run_status(
          db_session,
          run_accession_id,
          ProtocolRunStatusEnum.CANCELING,
        )
        await db_session.commit()
        await protocol_run_service.update_run_status(
          db_session,
          run_accession_id,
          ProtocolRunStatusEnum.CANCELLED,
          output_data_json=json.dumps({"status": "Cancelled by user."}),
        )
        await db_session.commit()
        msg = f"Run {run_accession_id} cancelled by user."
        raise ProtocolCancelledError(msg)

    elif command == "CANCEL":
      await clear_control_command(run_accession_id)
      logger.info("Protocol run %s CANCELLING.", run_accession_id)
      await protocol_run_service.update_run_status(
        db_session,
        run_accession_id,
        ProtocolRunStatusEnum.CANCELING,
      )
      await db_session.commit()
      await protocol_run_service.update_run_status(
        db_session,
        run_accession_id,
        ProtocolRunStatusEnum.CANCELLED,
        output_data_json=json.dumps({"status": "Cancelled by user."}),
      )
      await db_session.commit()
      msg = f"Run {run_accession_id} cancelled by user."
      raise ProtocolCancelledError(msg)

    elif command == "INTERVENE":
      await clear_control_command(run_accession_id)
      logger.info("Protocol run %s INTERVENING.", run_accession_id)
      await protocol_run_service.update_run_status(
        db_session,
        run_accession_id,
        ProtocolRunStatusEnum.INTERVENING,
      )
      await db_session.commit()
      # TODO: dispatch to intervention handler
