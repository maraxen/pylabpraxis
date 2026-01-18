import inspect
import re
from typing import Any, cast

from praxis.backend.models.domain.protocol import (
  AssetRequirement as AssetRequirementModel,
)
from praxis.backend.models.domain.protocol import (
  DataViewMetadataModel,
  FunctionProtocolDefinitionCreate,
  ParameterMetadataModel,
)
from praxis.backend.utils.uuid import uuid7

from .models import (
  CreateProtocolDefinitionData,
  DataViewDefinition,
  DecoratedProtocolFunc,
  SetupInstruction,
  get_callable_fqn,
)
from .parameter_processor import _process_parameter


def _convert_data_views(
  data_views: list[DataViewDefinition] | None,
) -> list[DataViewMetadataModel]:
  """Convert DataViewDefinition objects to DataViewMetadataModel Pydantic models."""
  if not data_views:
    return []

  return [
    DataViewMetadataModel(
      name=dv.name,
      description=dv.description,
      source_type=dv.source_type,
      source_filter_json=dv.source_filter,
      data_schema_json=dv.schema,
      required=dv.required,
      default_value_json=dv.default_value,
    )
    for dv in data_views
  ]


def _convert_setup_instructions(
  setup_instructions: list[str | SetupInstruction] | None,
) -> list[dict[str, Any]] | None:
  """Convert setup instructions to JSON-serializable dicts.

  Args:
    setup_instructions: List of setup instructions, either as strings or
      SetupInstruction dataclass instances.

  Returns:
    List of dicts ready for JSON serialization, or None if no instructions.

  """
  if not setup_instructions:
    return None

  result: list[dict[str, Any]] = []
  for instruction in setup_instructions:
    if isinstance(instruction, str):
      # String instructions are treated as required severity
      result.append(
        {
          "message": instruction,
          "severity": "required",
          "position": None,
          "resource_type": None,
        }
      )
    elif isinstance(instruction, SetupInstruction):
      result.append(
        {
          "message": instruction.message,
          "severity": instruction.severity,
          "position": instruction.position,
          "resource_type": instruction.resource_type,
        }
      )
    else:
      # Already a dict (shouldn't happen after decorator processing)
      result.append(instruction)  # type: ignore[arg-type]

  return result


def _create_protocol_definition(
  data: CreateProtocolDefinitionData,
) -> tuple[FunctionProtocolDefinitionCreate, dict[str, Any] | None]:
  """Parse a function signature and decorator args to create a protocol definition."""
  resolved_name = data.name or cast("DecoratedProtocolFunc", data.func).__name__
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

  # Convert data views from dataclass to Pydantic model
  data_views_models = _convert_data_views(data.data_views)

  # Convert setup instructions to JSON-serializable format
  setup_instructions_json = _convert_setup_instructions(data.setup_instructions)

  # Determine requires_deck value:
  # - If explicitly set via decorator, use that value
  # - Otherwise, infer from parameters: True if LiquidHandler/Deck param exists
  if data.requires_deck is not None:
    requires_deck = data.requires_deck
  else:
    # Infer from parameter types
    requires_deck = any(
      "LiquidHandler" in str(param_obj.annotation) or "Deck" in str(param_obj.annotation)
      for param_obj in sig.parameters.values()
    )

  protocol_accession_id = uuid7()

  for asset in assets_list:
    asset.protocol_definition_accession_id = protocol_accession_id

  protocol_definition = FunctionProtocolDefinitionCreate(
    accession_id=protocol_accession_id,
    name=resolved_name,
    version=data.version,
    description=(data.description or inspect.getdoc(data.func) or "No description provided."),
    fqn=get_callable_fqn(data.func),
    source_file_path=inspect.getfile(data.func),
    module_name=cast("DecoratedProtocolFunc", data.func).__module__,
    function_name=cast("DecoratedProtocolFunc", data.func).__name__,
    is_top_level=data.is_top_level,
    solo_execution=data.solo,
    preconfigure_deck=data.preconfigure_deck,
    requires_deck=requires_deck,
    deck_param_name=data.deck_param_name if data.preconfigure_deck else None,
    deck_construction_function_fqn=(
      get_callable_fqn(data.deck_construction) if data.deck_construction else None
    ),
    deck_layout_path=data.deck_layout_path,
    data_views=data_views_models,
    setup_instructions_json=setup_instructions_json,
    state_param_name=data.state_param_name,
    category=data.category,
    tags=data.tags,
    parameters=parameters_list,
    assets=assets_list,
  )
  return protocol_definition, found_state_param_details
