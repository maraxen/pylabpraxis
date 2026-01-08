"""LibCST visitor for discovering protocol functions."""

import hashlib
from typing import Any

import libcst as cst

from praxis.backend.utils.plr_static_analysis.models import (
  ProtocolFunctionInfo,
  ProtocolParameterInfo,
)
from praxis.backend.utils.plr_static_analysis.type_annotation_analyzer import (
  TypeAnnotationAnalyzer,
)
from praxis.backend.utils.plr_static_analysis.visitors.base import BasePLRVisitor
from praxis.backend.utils.plr_static_analysis.visitors.computation_graph_extractor import (
  extract_graph_from_function,
)
from praxis.backend.utils.plr_static_analysis.visitors.protocol_requirement_extractor import (
  ProtocolRequirementExtractor,
)
from praxis.common.type_inspection import is_pylabrobot_resource


class ProtocolFunctionVisitor(BasePLRVisitor):
  """Visitor to find and extract metadata from @protocol_function decorated functions."""

  # Decorator names that indicate a protocol function
  PROTOCOL_DECORATOR_NAMES = {"protocol_function"}

  def __init__(self, module_name: str, file_path: str) -> None:
    """Initialize the visitor.

    Args:
      module_name: The module name (e.g., 'protocols.my_protocol')
      file_path: Absolute path to the source file

    """
    super().__init__(module_name, file_path)
    self.definitions: list[ProtocolFunctionInfo] = []

  def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:  # noqa: N802
    """Visit a function definition to check for protocol decorators."""
    if not self._has_protocol_decorator(node):
      return False

    self._process_protocol_function(node)
    # We don't need to traverse into the function body for discovery purposes,
    # unless we want to do nested protocol discovery (which we don't for now).
    # However, if we add requirements extraction here later, we might return True.
    return False

  def _has_protocol_decorator(self, node: cst.FunctionDef) -> bool:
    """Check if the function has a @protocol_function decorator."""
    for decorator in node.decorators:
      # Handle @protocol_function
      if isinstance(decorator.decorator, cst.Name):
        if decorator.decorator.value in self.PROTOCOL_DECORATOR_NAMES:
          return True
      # Handle @protocol_function(...)
      elif isinstance(decorator.decorator, cst.Call):
        func = decorator.decorator.func
        if (isinstance(func, cst.Name) and func.value in self.PROTOCOL_DECORATOR_NAMES) or (
          isinstance(func, cst.Attribute) and func.attr.value in self.PROTOCOL_DECORATOR_NAMES
        ):
          return True
      # Handle @module.protocol_function (attribute without call)
      elif (
        isinstance(decorator.decorator, cst.Attribute)
        and decorator.decorator.attr.value in self.PROTOCOL_DECORATOR_NAMES
      ):
        return True

    return False

  def _process_protocol_function(self, node: cst.FunctionDef) -> None:
    """Extract metadata from a protocol function node."""
    function_name = node.name.value
    docstring = self._get_docstring(node.body) or "Inferred from code."

    params_info: list[ProtocolParameterInfo] = []

    # Process parameters
    # node.params.params contains positional/keyword args
    # defaults are stored in node.params.params[-N:].default if they exist,
    # but LibCST structures defaults directly on the Param node.

    for param in node.params.params:
      param_name = param.name.value

      # Extract type hint
      type_hint = "Any"
      if param.annotation:
        type_hint = self._type_annotation_to_string(param.annotation.annotation)

      # Extract default value
      default_value = None
      is_optional = False
      if param.default:
        is_optional = True
        # CST to source string for default value
        default_value = cst.Module([]).code_for_node(param.default)

      is_asset = is_pylabrobot_resource(type_hint)

      # Type Inference for Index Selector using CST-based analysis
      field_type = None
      is_itemized = False
      itemized_spec = None

      # Use TypeAnnotationAnalyzer for comprehensive type detection
      # Supports: Well, TipSpot, list[Well], Sequence[TipSpot],
      #           tuple[Well, ...], Optional[Well], Well | None, etc.
      if param.annotation:
        analyzer = TypeAnnotationAnalyzer()
        type_info = analyzer.analyze(param.annotation.annotation)
        if type_info:
          field_type = type_info.field_type
          is_itemized = type_info.is_itemized
          itemized_spec = {
            "items_x": type_info.items_x,
            "items_y": type_info.items_y,
          }

      fqn = f"{self.module_path}.{function_name}.{param_name}"

      info = ProtocolParameterInfo(
        name=param_name,
        type_hint=type_hint,
        default_value=default_value,
        is_optional=is_optional,
        is_asset=is_asset,
        fqn=fqn,
        field_type=field_type,
        is_itemized=is_itemized,
        itemized_spec=itemized_spec,
      )

      if is_asset:
        info.asset_type = type_hint

      params_info.append(info)

    # Construct raw dicts for backward compatibility with DiscoveryService
    # This matches the structure created by the AST-based ProtocolVisitor
    uuid_placeholder = "00000000-0000-0000-0000-000000000000"  # Real UUIDs generated by service

    raw_assets = []
    raw_parameters = []

    for p in params_info:
      if p.is_asset:
        raw_assets.append(
          {
            "accession_id": uuid_placeholder,  # Service will replace this
            "name": p.name,
            "fqn": p.fqn,
            "type_hint_str": p.type_hint,
            "actual_type_str": p.type_hint,
            "optional": p.is_optional,
            "default_value_repr": p.default_value,
          }
        )
      else:
        raw_parameters.append(
          {
            "name": p.name,
            "fqn": p.fqn,
            "type_hint": p.type_hint,
            "optional": p.is_optional,
            "default_value_repr": p.default_value,
          }
        )

    # Extract computation graph
    computation_graph, source_hash = self._extract_computation_graph(node, params_info)

    # Infer requires_deck: False if no LiquidHandler or Deck param exists
    # This enables machine-only protocols (e.g., plate reader)
    requires_deck = any(
      "LiquidHandler" in p.type_hint or "Deck" in p.type_hint for p in params_info
    )

    definition = ProtocolFunctionInfo(
      name=function_name,
      fqn=f"{self.module_path}.{function_name}",
      module_name=self.module_path,
      source_file_path=self.file_path,
      docstring=docstring,
      parameters=params_info,
      raw_assets=raw_assets,
      raw_parameters=raw_parameters,
      hardware_requirements=self._extract_requirements(node),
      computation_graph=computation_graph,
      source_hash=source_hash,
      requires_deck=requires_deck,
    )

    self.definitions.append(definition)

  def _type_annotation_to_string(self, node: cst.BaseExpression) -> str:
    """Convert a type annotation node to a string representation."""
    return cst.Module([]).code_for_node(node)

  def _extract_requirements(self, node: cst.FunctionDef) -> dict[str, Any] | None:
    """Extract hardware requirements from the function body."""
    try:
      # Create a dummy module to wrap the function body for visitation
      # We clone the body to avoid modifying the original tree if that matters,
      # but here we just need to visit it.
      # A simple way is to use the extractor directly on the function node
      # but the extractor expects to visit Call nodes.

      extractor = ProtocolRequirementExtractor()
      node.visit(extractor)
      requirements_model = extractor.build_requirements()

      # Convert to dict for JSON serialization
      return requirements_model.model_dump(exclude_none=True)
    except Exception:
      # If extraction fails, we don't want to fail discovery
      # Log it? The visitor doesn't have a logger handy, passing one might be good.
      # For now, safe fail.
      return None

  def _extract_computation_graph(
    self,
    node: cst.FunctionDef,
    params_info: list[ProtocolParameterInfo],
  ) -> tuple[dict[str, Any] | None, str | None]:
    """Extract computation graph and source hash from the function.

    Args:
      node: The function definition CST node.
      params_info: Pre-extracted parameter information.

    Returns:
      Tuple of (computation_graph_dict, source_hash).

    """
    try:
      # Calculate source hash from the function source code
      source_code = cst.Module([]).code_for_node(node)
      source_hash = hashlib.sha256(source_code.encode()).hexdigest()[:16]

      # Build parameter types dict from params_info
      parameter_types = {p.name: p.type_hint for p in params_info}

      # Extract the computation graph
      graph = extract_graph_from_function(
        function_node=node,
        module_name=self.module_path,
        parameter_types=parameter_types,
      )

      # Convert to dict for JSON serialization
      return graph.model_dump(exclude_none=True), source_hash

    except Exception:
      # If extraction fails, we don't want to fail discovery
      # Safe fail with no graph
      return None, None
