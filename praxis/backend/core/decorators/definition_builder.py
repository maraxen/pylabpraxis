import inspect
import re
from typing import Any

from praxis.backend.models.pydantic_internals.protocol import (
  AssetRequirementModel,
  FunctionProtocolDefinitionCreate,
  ParameterMetadataModel,
)
from praxis.backend.utils.uuid import uuid7

from .models import CreateProtocolDefinitionData, get_callable_fqn
from .parameter_processor import _process_parameter


def _create_protocol_definition(
  data: CreateProtocolDefinitionData,
) -> tuple[FunctionProtocolDefinitionCreate, dict[str, Any] | None]:
  """Parse a function signature and decorator args to create a protocol definition."""
  resolved_name = data.name or data.func.__name__
  if not resolved_name:
    msg = (
      "Protocol function name cannot be empty (either provide 'name' argument or use "
      "a named function)."
    )
    raise ValueError(
      msg,
    )
  if (
    data.is_top_level
    and data.top_level_name_format
    and not re.match(data.top_level_name_format, resolved_name)
  ):
    msg = (
      f"Top-level protocol name '{resolved_name}' does not match format: "
      f"{data.top_level_name_format}"
    )
    raise ValueError(
      msg,
    )

  sig = inspect.signature(data.func)
  parameters_list: list[ParameterMetadataModel] = []
  assets_list: list[AssetRequirementModel] = []
  found_deck_param = False
  found_state_param_details: dict[str, Any] | None = None

  for param_name_sig, param_obj in sig.parameters.items():
    parameters_list, assets_list, found_deck_param, found_state_param_details = _process_parameter(
      param_name_sig,
      param_obj,
      data,
      parameters_list,
      assets_list,
      found_deck_param=found_deck_param,
      found_state_param_details=found_state_param_details,
    )

  if data.preconfigure_deck and not found_deck_param:
    msg = (
      f"Protocol '{resolved_name}' (preconfigure_deck=True) missing '{data.deck_param_name}' param."
    )
    raise TypeError(
      msg,
    )
  if data.is_top_level and not found_state_param_details:
    msg = f"Top-level protocol '{resolved_name}' must define a '{data.state_param_name}' parameter."
    raise TypeError(
      msg,
    )

  protocol_definition = FunctionProtocolDefinitionCreate(
    accession_id=uuid7(),
    name=resolved_name,
    version=data.version,
    description=(data.description or inspect.getdoc(data.func) or "No description provided."),
    fqn=get_callable_fqn(data.func),
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
