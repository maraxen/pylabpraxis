# pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements,fixme,logging-fstring-interpolation
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
from typing import Any, Callable, Dict, List, Optional, Union, get_args, get_origin

from pydantic import BaseModel as PydanticBaseModel
from pylabrobot.resources import Deck, Resource

from praxis.backend.core.orchestrator import ProtocolCancelledError
from praxis.backend.core.run_context import (
  PROTOCOL_REGISTRY,
  PraxisRunContext,
  PraxisState,
  serialize_arguments,
)
from praxis.backend.models import (
  AssetRequirementModel,
  FunctionCallStatusEnum,
  FunctionProtocolDefinitionModel,
  ParameterMetadataModel,
  ProtocolRunStatusEnum,
  UIHint,
)
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
from praxis.backend.utils.uuid import uuid7

praxis_run_context_cv: contextvars.ContextVar[PraxisRunContext] = (
  contextvars.ContextVar("praxis_run_context")
)

DEFAULT_DECK_PARAM_NAME = "deck"
DEFAULT_STATE_PARAM_NAME = "state"
TOP_LEVEL_NAME_REGEX = r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$"

logger = get_logger(__name__)


class ProtocolRuntimeInfo:
  """A container for runtime information about a protocol function."""

  def __init__(
    self,
    pydantic_definition: FunctionProtocolDefinitionModel,
    function_ref: Callable,
    found_state_param_details: Optional[Dict[str, Any]],
  ):
    """Initialize the ProtocolRuntimeInfo.

    Args:
      pydantic_definition (FunctionProtocolDefinitionModel): The Pydantic model
        definition of the protocol function.
      function_ref (Callable): The actual function reference.
      found_state_param_details (Optional[Dict[str, Any]]): Details about the
        state parameter if it exists.

    """
    self.pydantic_definition: FunctionProtocolDefinitionModel = pydantic_definition
    self.function_ref: Callable = function_ref
    self.callable_wrapper: Optional[Callable] = None
    self.db_accession_id: Optional[uuid.UUID] = None
    self.found_state_param_details: Optional[Dict[str, Any]] = found_state_param_details


def is_pylabrobot_resource(obj_type: Any) -> bool:
  """Check if the given type is a Pylabrobot Resource or Union of Resources."""
  if obj_type is inspect.Parameter.empty:
    return False
  origin = get_origin(obj_type)
  args = get_args(obj_type)
  if origin is Union:
    return any(is_pylabrobot_resource(arg) for arg in args if arg is not type(None))
  try:
    if inspect.isclass(obj_type):
      return issubclass(obj_type, Resource)
  except TypeError:  # pragma: no cover
    pass
  return False


def fqn_from_hint(type_hint: Any) -> str:
  """Get the fully qualified name of a type hint.

  For built-in types, this returns just the type name (e.g., "int"), not "builtins.int".
  For types from the "praxis." namespace, returns the fully qualified name.
  For Union or Optional types, returns the FQN of the non-None type(s).
  For generics, returns the FQN of the generic type.
  """
  if type_hint == inspect.Parameter.empty:
    return "Any"
  actual_type = type_hint
  origin = get_origin(type_hint)
  args = get_args(type_hint)
  if origin is Union and type(None) in args:
    non_none_args = [arg for arg in args if arg is not type(None)]
  if hasattr(actual_type, "__name__"):
    module = getattr(actual_type, "__module__", "")
    if isinstance(module, str) and (
      module.startswith("praxis.") or module == "builtins"
    ):
      return (
        f"{module}.{actual_type.__name__}"
        if module and module != "builtins"
        else actual_type.__name__
      )
    return actual_type.__name__
  return str(actual_type)


def serialize_type_hint(type_hint: Any) -> str:
  """Serialize a type hint to a string representation."""
  if type_hint == inspect.Parameter.empty:
    return "Any"
  return str(type_hint)


# --- End Helper Functions ---
# TODO: add decorators for deck construction and state management


async def protocol_function(
  name: Optional[str] = None,
  version: str = "0.1.0",
  description: Optional[str] = None,
  solo: bool = False,
  is_top_level: bool = False,
  preconfigure_deck: bool = False,
  deck_param_name: str = DEFAULT_DECK_PARAM_NAME,
  state_param_name: str = DEFAULT_STATE_PARAM_NAME,
  param_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
  category: Optional[str] = None,
  tags: Optional[List[str]] = None,
  top_level_name_format: Optional[str] = TOP_LEVEL_NAME_REGEX,
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
      for preconfiguration.
    deck_param_name (str): Name of the deck parameter if preconfigure_deck is True.
    state_param_name (str): Name of the state parameter for top-level protocols.
    param_metadata (Optional[Dict[str, Dict[str, Any]]]): Metadata for parameters.
    category (Optional[str]): Category for organizing protocols.
    tags (Optional[List[str]]): Tags for additional categorization.
    top_level_name_format (Optional[str]): Regex format for top-level protocol names.

  """
  actual_param_metadata = param_metadata or {}
  actual_tags = tags or []

  def decorator(func: Callable):
    resolved_name = name or func.__name__
    if not resolved_name:
      raise ValueError(
        "Protocol function name cannot be empty (either provide 'name' argument or use "
        "a named function)."
      )
    if (
      is_top_level
      and top_level_name_format
      and not re.match(top_level_name_format, resolved_name)
    ):
      raise ValueError(
        f"Top-level protocol name '{resolved_name}' does not match format: "
        f"{top_level_name_format}"
      )

    protocol_unique_key = f"{resolved_name}_v{version}"

    sig = inspect.signature(func)
    parameters_list: List[ParameterMetadataModel] = []
    assets_list: List[AssetRequirementModel] = []
    found_deck_param = False
    found_state_param_details: Optional[Dict[str, Any]] = None

    for param_name_sig, param_obj in sig.parameters.items():
      param_type_hint = param_obj.annotation
      is_optional_param = (
        get_origin(param_type_hint) is Union and type(None) in get_args(param_type_hint)
      ) or (param_obj.default is not inspect.Parameter.empty)
      fqn = fqn_from_hint(param_type_hint)
      param_meta_entry = actual_param_metadata.get(param_name_sig, {})
      p_description = param_meta_entry.get("description")
      p_constraints = param_meta_entry.get("constraints_json", {})
      p_ui_hints_dict = param_meta_entry.get("ui_hints")
      p_ui_hints = (
        UIHint(**p_ui_hints_dict) if isinstance(p_ui_hints_dict, dict) else None
      )

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

      if preconfigure_deck and param_name_sig == deck_param_name:
        parameters_list.append(
          ParameterMetadataModel(**common_model_args, is_deck_param=True)
        )
        found_deck_param = True
        continue

      if param_name_sig == state_param_name:
        is_state_type_match = (
          fqn == "PraxisState"
          or fqn == "praxis.backend.core.definitions.PraxisState"
          or fqn == "PraxisState"
        )
        is_dict_type_match = fqn == "dict"
        found_state_param_details = {
          "name": param_name_sig,
          "expects_praxis_state": is_state_type_match,
          "expects_dict": is_dict_type_match,
        }
        parameters_list.append(ParameterMetadataModel(**common_model_args))
        continue

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

    if preconfigure_deck and not found_deck_param:
      raise TypeError(
        f"Protocol '{resolved_name}' (preconfigure_deck=True) missing "
        f"'{deck_param_name}' param."
      )
    if is_top_level and not found_state_param_details:
      raise TypeError(
        f"Top-level protocol '{resolved_name}' must define a '{state_param_name}' "
        f"parameter."
      )

    protocol_definition = FunctionProtocolDefinitionModel(
      accession_id=uuid7(),
      name=resolved_name,
      version=version,
      description=(description or inspect.getdoc(func) or "No description provided."),
      source_file_path=inspect.getfile(func),
      module_name=func.__module__,
      function_name=func.__name__,
      is_top_level=is_top_level,
      solo_execution=solo,
      preconfigure_deck=preconfigure_deck,
      deck_param_name=deck_param_name if preconfigure_deck else None,
      state_param_name=state_param_name,
      category=category,
      tags=actual_tags,
      parameters=parameters_list,
      assets=assets_list,
    )
    setattr(func, "_protocol_definition", protocol_definition)

    protocol_runtime_info = ProtocolRuntimeInfo(
      pydantic_definition=protocol_definition,
      function_ref=func,
      found_state_param_details=found_state_param_details,
    )
    PROTOCOL_REGISTRY[protocol_unique_key] = protocol_runtime_info

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
      current_meta = PROTOCOL_REGISTRY.get(protocol_unique_key)
      if not current_meta or not current_meta.db_accession_id:
        raise RuntimeError(
          f"Protocol '{protocol_unique_key}' not registered or missing DB ID."
        )

      parent_context = praxis_run_context_cv.get()
      if parent_context is None:
        raise RuntimeError(
          "No PraxisRunContext found in contextvars. Ensure this function is called "
          "within a valid Praxis run context."
        )

      this_function_def_db_accession_id = current_meta.db_accession_id
      state_details = current_meta.found_state_param_details

      processed_args = list(args)
      processed_kwargs = dict(kwargs)

      if state_details:
        state_arg_name_in_sig = state_details["name"]
        if state_arg_name_in_sig in processed_kwargs:
          del processed_kwargs[state_arg_name_in_sig]
        if state_details["expects_praxis_state"]:
          processed_kwargs[state_arg_name_in_sig] = parent_context.canonical_state
        elif state_details["expects_dict"]:
          if state_arg_name_in_sig not in processed_kwargs:
            processed_kwargs[state_arg_name_in_sig] = (
              parent_context.canonical_state.data.copy()
              if parent_context.canonical_state
              else {}
            )

      current_call_log_db_accession_id: Optional[uuid.UUID] = None
      parent_log_accession_id_for_this_call = (
        parent_context.current_call_log_db_accession_id
      )

      if parent_context.current_db_session and this_function_def_db_accession_id:
        try:
          sequence_val = parent_context.get_and_increment_sequence_val()
          serialized_input_args = serialize_arguments(
            tuple(processed_args), processed_kwargs
          )
          call_log_entry_orm = await log_function_call_start(
            db=parent_context.current_db_session,
            protocol_run_orm_accession_id=parent_context.run_accession_id,
            function_definition_accession_id=this_function_def_db_accession_id,
            sequence_in_run=sequence_val,
            input_args_json=serialized_input_args,
            parent_function_call_log_accession_id=parent_log_accession_id_for_this_call,
          )
          current_call_log_db_accession_id = call_log_entry_orm.accession_id
        except Exception as log_e:
          logger.error(
            "Failed to log_function_call_start for '%s': %s",
            protocol_definition.name,
            log_e,
            exc_info=True,
          )

      context_for_this_call = parent_context.create_context_for_nested_call(
        new_parent_call_log_db_accession_id=current_call_log_db_accession_id
      )
      token = praxis_run_context_cv.set(context_for_this_call)

      result = None
      error = None
      status_enum_val = FunctionCallStatusEnum.SUCCESS
      start_time_perf = time.perf_counter()

      try:
        run_accession_id = context_for_this_call.run_accession_id
        current_db_session = context_for_this_call.current_db_session
        logger.info(
          "Executing protocol function '%s v%s' (Run: %s, Call ID: %s)",
          protocol_definition.name,
          protocol_definition.version,
          context_for_this_call.run_accession_id,
          current_call_log_db_accession_id,
        )
      except Exception as e:
        logger.error(
          "Failed to log function call start for '%s': %s",
          protocol_definition.name,
          e,
          exc_info=True,
        )
        raise RuntimeError(
          f"Failed to log function call start for '{protocol_definition.name}': {e}"
        )

      while True:
        command = await get_control_command(run_accession_id)
        if not command:
          break

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
            current_db_session,
            run_accession_id,
            ProtocolRunStatusEnum.PAUSING,
          )
          await current_db_session.commit()
          await update_protocol_run_status(
            current_db_session,
            run_accession_id,
            ProtocolRunStatusEnum.PAUSED,
          )
          await current_db_session.commit()

          pause_loop_command_after_resume = None
          while True:
            await asyncio.sleep(1)
            pause_loop_command = await get_control_command(run_accession_id)
            pause_loop_command_after_resume = pause_loop_command
            if pause_loop_command in ["RESUME", "CANCEL"]:
              logger.info(
                "Received command '%s' while PAUSED for run %s.",
                pause_loop_command,
                run_accession_id,
              )
              break
            elif pause_loop_command == "INTERVENE":
              await clear_control_command(run_accession_id)
              logger.info("Protocol run %s INTERVENING during pause.", run_accession_id)
              await update_protocol_run_status(
                current_db_session,
                run_accession_id,
                ProtocolRunStatusEnum.INTERVENING,
              )
              await current_db_session.commit()
            elif pause_loop_command == "PAUSE":
              logger.info(
                "Received PAUSE command while already PAUSED for run %s. Ignoring.",
                run_accession_id,
              )
              continue
            elif pause_loop_command and pause_loop_command not in [*ALLOWED_COMMANDS]:
              logger.warning(
                "Invalid command '%s' while PAUSED for run %s. Clearing.",
                pause_loop_command,
                run_accession_id,
              )
              await clear_control_command(run_accession_id)
            elif pause_loop_command in ALLOWED_COMMANDS:
              logger.info(
                "Received command '%s' while PAUSED for run %s.",
                pause_loop_command,
                run_accession_id,
              )
              if pause_loop_command == "INTERVENE":
                await clear_control_command(run_accession_id)
                logger.info("Protocol run %s INTERVENING.", run_accession_id)
                await update_protocol_run_status(
                  current_db_session,
                  run_accession_id,
                  ProtocolRunStatusEnum.INTERVENING,
                )
                await current_db_session.commit()
                # TODO: dispatch to intervention handler)

          if pause_loop_command_after_resume == "RESUME":
            await clear_control_command(run_accession_id)
            logger.info("Protocol run %s RESUMING.", run_accession_id)
            await update_protocol_run_status(
              current_db_session,
              run_accession_id,
              ProtocolRunStatusEnum.RESUMING,
            )
            await current_db_session.commit()
            await update_protocol_run_status(
              current_db_session,
              run_accession_id,
              ProtocolRunStatusEnum.RUNNING,
            )
            await current_db_session.commit()
            break
          elif pause_loop_command_after_resume == "CANCEL":
            await clear_control_command(run_accession_id)
            logger.info("Protocol run %s CANCELLING after pause.", run_accession_id)
            await update_protocol_run_status(
              current_db_session,
              run_accession_id,
              ProtocolRunStatusEnum.CANCELING,
            )
            await current_db_session.commit()
            await update_protocol_run_status(
              current_db_session,
              run_accession_id,
              ProtocolRunStatusEnum.CANCELLED,
              output_data_json=json.dumps({"status": "Cancelled by user."}),
            )
            await current_db_session.commit()
            raise ProtocolCancelledError(f"Run {run_accession_id} cancelled by user.")

        elif command == "CANCEL":
          await clear_control_command(run_accession_id)
          logger.info("Protocol run %s CANCELLING.", run_accession_id)
          await update_protocol_run_status(
            current_db_session,
            run_accession_id,
            ProtocolRunStatusEnum.CANCELING,
          )
          await current_db_session.commit()
          await update_protocol_run_status(
            current_db_session,
            run_accession_id,
            ProtocolRunStatusEnum.CANCELLED,
            output_data_json=json.dumps({"status": "Cancelled by user."}),
          )
          await current_db_session.commit()
          raise ProtocolCancelledError(f"Run {run_accession_id} cancelled by user.")

        elif command == "INTERVENE":
          await clear_control_command(run_accession_id)
          logger.info("Protocol run %s INTERVENING.", run_accession_id)
          await update_protocol_run_status(
            current_db_session,
            run_accession_id,
            ProtocolRunStatusEnum.INTERVENING,
          )
          await current_db_session.commit()
          # TODO: dispatch to intervention handler

      try:
        processed_kwargs_for_call = processed_kwargs.copy()
        sig_check = inspect.signature(func)
        if "__praxis_run_context__" in sig_check.parameters:
          processed_kwargs_for_call["__praxis_run_context__"] = context_for_this_call
        elif (
          state_details
          and state_details["name"] == state_param_name
          and sig_check.parameters[state_param_name].annotation == PraxisRunContext
        ):
          processed_kwargs_for_call[state_param_name] = context_for_this_call

        if (
          "__praxis_run_context__" in processed_kwargs_for_call
          and "__praxis_run_context__" not in func.__code__.co_varnames
          and not any(
            p.kind == inspect.Parameter.VAR_KEYWORD
            for p in sig_check.parameters.values()
          )
        ):
          del processed_kwargs_for_call["__praxis_run_context__"]

        if inspect.iscoroutinefunction(func):
          result = await func(*processed_args, **processed_kwargs_for_call)
        else:
          loop = asyncio.get_running_loop()
          result = await loop.run_in_executor(
            None, functools.partial(func, *processed_args, **processed_kwargs_for_call)
          )

      except ProtocolCancelledError:
        raise
      except Exception as e:
        error = e
        status_enum_val = FunctionCallStatusEnum.ERROR
        logger.error(
          "ERROR in '%s' (Run: %s): %s",
          protocol_unique_key,
          context_for_this_call.run_accession_id,
          e,
          exc_info=True,
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
              serialized_result = json.dumps(result, default=str)
          if current_call_log_db_accession_id is None:
            current_call_log_db_accession_id = (
              context_for_this_call.current_call_log_db_accession_id
            )
          if current_call_log_db_accession_id is None:
            raise RuntimeError(
              "No current call log DB ID found. Cannot log function call end."
            )
          await log_function_call_end(
            db=context_for_this_call.current_db_session,
            function_call_log_accession_id=current_call_log_db_accession_id,
            status=status_enum_val,
            return_value_json=serialized_result,
            error_message=str(error) if error else None,
            error_traceback=traceback.format_exc() if error else None,
            duration_ms=duration_ms,
          )
        except Exception as log_e:
          logger.error(
            "Failed to log_function_call_end for '%s': %s",
            protocol_definition.name,
            log_e,
            exc_info=True,
          )

      if error:
        if isinstance(error, ProtocolCancelledError):
          raise error
        raise error
      return result

    return wrapper

  return decorator
