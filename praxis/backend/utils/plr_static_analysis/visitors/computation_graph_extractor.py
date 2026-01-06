"""Computation graph extractor for protocol functions.

This module provides a LibCST visitor that analyzes protocol function bodies
to extract a computational graph representation, including:
- Operation nodes (method calls on machines)
- Resource nodes (PLR resources used)
- State preconditions (requirements for each operation)
- Execution order

The extractor tracks variable types and infers preconditions from known
method patterns (e.g., `lh.transfer()` requires tips loaded).
"""

from typing import Any

import libcst as cst

from praxis.backend.utils.plr_static_analysis.models import (
  GraphNodeType,
  OperationNode,
  PreconditionType,
  ProtocolComputationGraph,
  ResourceNode,
  StatePrecondition,
)
from praxis.backend.utils.plr_static_analysis.resource_hierarchy import (
  DeckLayoutType,
  get_parental_chain,
)
from praxis.common.type_inspection import (
  extract_resource_types,
  get_element_type,
  is_container_type,
)

# =============================================================================
# Method Patterns and Preconditions
# =============================================================================

# Methods that require tips to be loaded
TIPS_REQUIRED_METHODS: frozenset[str] = frozenset({
  "aspirate",
  "dispense",
  "transfer",
  "mix",
  "blow_out",
  "touch_tip",
  "drop_tips",
  "return_tips",
})

# Methods that create "tips loaded" state
TIPS_LOADING_METHODS: frozenset[str] = frozenset({
  "pick_up_tips",
  "pick_up_tips96",
})

# Methods that remove "tips loaded" state
TIPS_DROPPING_METHODS: frozenset[str] = frozenset({
  "drop_tips",
  "drop_tips96",
  "return_tips",
})

# Methods that require plate access (not covered by lid)
PLATE_ACCESS_METHODS: frozenset[str] = frozenset({
  "aspirate",
  "dispense",
  "transfer",
  "mix",
  "read_absorbance",
  "read_fluorescence",
  "read_luminescence",
})

# Methods that move plates (require iSWAP or similar)
PLATE_MOVE_METHODS: frozenset[str] = frozenset({
  "move_plate",
  "get_plate",
  "put_plate",
  "move_lid",
})

# Variable name patterns that indicate machine type
MACHINE_VAR_PATTERNS: dict[str, str] = {
  "lh": "liquid_handler",
  "liquid_handler": "liquid_handler",
  "pr": "plate_reader",
  "plate_reader": "plate_reader",
  "reader": "plate_reader",
  "hs": "heater_shaker",
  "heater_shaker": "heater_shaker",
  "shaker": "shaker",
  "centrifuge": "centrifuge",
  "cf": "centrifuge",
  "tc": "thermocycler",
  "thermocycler": "thermocycler",
  "incubator": "incubator",
}


# =============================================================================
# Variable Type Tracker
# =============================================================================


class VariableTypeTracker:
  """Tracks variable types throughout a protocol function body.

  This class maintains a mapping of variable names to their inferred types,
  handling assignments, subscript operations, and attribute access.
  """

  def __init__(self, parameter_types: dict[str, str]) -> None:
    """Initialize with known parameter types.

    Args:
        parameter_types: Mapping of parameter names to their type hints.

    """
    self._types: dict[str, str] = parameter_types.copy()
    self._sources: dict[str, str] = {}  # Variable -> source expression

  def get_type(self, var_name: str) -> str | None:
    """Get the type for a variable."""
    return self._types.get(var_name)

  def set_type(self, var_name: str, type_hint: str, source: str | None = None) -> None:
    """Set the type for a variable."""
    self._types[var_name] = type_hint
    if source:
      self._sources[var_name] = source

  def get_source(self, var_name: str) -> str | None:
    """Get the source expression for a variable."""
    return self._sources.get(var_name)

  def infer_subscript_type(self, base_type: str, key: str) -> str:
    """Infer the type of a subscript operation.

    Args:
        base_type: Type of the base expression.
        key: The subscript key (e.g., "A1:A8").

    Returns:
        Inferred type of the subscript result.

    """
    # Plate["A1:A8"] -> list[Well]
    if "Plate" in base_type:
      if ":" in key:
        return "list[Well]"
      return "Well"

    # TipRack["A1:A8"] -> list[TipSpot]
    if "TipRack" in base_type:
      if ":" in key:
        return "list[TipSpot]"
      return "TipSpot"

    # list[X][0] -> X
    if base_type.startswith("list["):
      elem = get_element_type(base_type)
      if elem:
        return elem

    return base_type

  def infer_attribute_type(self, base_type: str, attr: str) -> str:
    """Infer the type of an attribute access.

    Args:
        base_type: Type of the base expression.
        attr: The attribute name.

    Returns:
        Inferred type of the attribute access.

    """
    # plate.wells() -> list[Well]
    if attr == "wells" and "Plate" in base_type:
      return "list[Well]"

    # tiprack.tips() -> list[TipSpot]
    if attr in ("tips", "tip_spots") and "TipRack" in base_type:
      return "list[TipSpot]"

    return "Any"


# =============================================================================
# Computation Graph Extractor
# =============================================================================


class ComputationGraphExtractor(cst.CSTVisitor):
  """Extracts a computation graph from a protocol function body.

  This visitor analyzes LibCST nodes to build a ProtocolComputationGraph
  containing operations, resources, preconditions, and execution order.

  Usage:
      extractor = ComputationGraphExtractor(
          protocol_fqn="my_module.my_protocol",
          parameter_types={"lh": "LiquidHandler", "plate": "Plate"},
      )
      function_node.body.walk(extractor)
      graph = extractor.build_graph()

  """

  def __init__(
    self,
    protocol_fqn: str,
    parameter_types: dict[str, str],
    deck_layout_type: DeckLayoutType = DeckLayoutType.CARRIER_BASED,
  ) -> None:
    """Initialize the extractor.

    Args:
        protocol_fqn: Fully qualified name of the protocol function.
        parameter_types: Mapping of parameter names to their type hints.
        deck_layout_type: Type of deck layout for parental chain inference.

    """
    self._protocol_fqn = protocol_fqn
    self._protocol_name = protocol_fqn.split(".")[-1] if "." in protocol_fqn else protocol_fqn
    self._deck_layout_type = deck_layout_type

    # Type tracking
    self._type_tracker = VariableTypeTracker(parameter_types)
    self._parameter_names = set(parameter_types.keys())

    # Graph components
    self._operations: list[OperationNode] = []
    self._resources: dict[str, ResourceNode] = {}
    self._preconditions: list[StatePrecondition] = []
    self._execution_order: list[str] = []

    # State tracking
    self._active_states: set[str] = set()  # Currently active states (e.g., "tips_loaded")
    self._machine_types: set[str] = set()
    self._op_counter = 0
    self._precond_counter = 0
    self._has_loops = False
    self._has_conditionals = False

    # Current line tracking (updated as we visit)
    self._current_line = 0

    # Initialize resources from parameters
    self._initialize_resources_from_params(parameter_types)

  def _initialize_resources_from_params(self, parameter_types: dict[str, str]) -> None:
    """Create ResourceNode entries for all PLR resource parameters."""
    for param_name, type_hint in parameter_types.items():
      resource_types = extract_resource_types(type_hint)
      if resource_types:
        # This parameter is a PLR resource
        elem_type = get_element_type(type_hint)
        is_container = is_container_type(type_hint)

        # Get primary resource type for parental chain
        primary_type = elem_type if elem_type else resource_types[0]
        chain = get_parental_chain(primary_type, self._deck_layout_type)

        self._resources[param_name] = ResourceNode(
          variable_name=param_name,
          declared_type=type_hint,
          element_type=elem_type,
          is_container=is_container,
          is_parameter=True,
          parental_chain=chain.chain,
        )

        # Add resource_on_deck precondition
        precond_id = self._create_precondition(
          PreconditionType.RESOURCE_ON_DECK,
          param_name,
          resource_type=primary_type,
        )
        # Mark as auto-satisfiable
        for p in self._preconditions:
          if p.id == precond_id:
            p.can_be_auto_satisfied = True

  def _generate_op_id(self) -> str:
    """Generate a unique operation ID."""
    self._op_counter += 1
    return f"op_{self._op_counter}"

  def _generate_precond_id(self) -> str:
    """Generate a unique precondition ID."""
    self._precond_counter += 1
    return f"precond_{self._precond_counter}"

  def _create_precondition(
    self,
    precond_type: PreconditionType,
    resource_var: str,
    resource_type: str | None = None,
    required_state: dict[str, Any] | None = None,
    satisfied_by: str | None = None,
  ) -> str:
    """Create a precondition and return its ID."""
    precond_id = self._generate_precond_id()
    self._preconditions.append(
      StatePrecondition(
        id=precond_id,
        precondition_type=precond_type,
        resource_variable=resource_var,
        resource_type=resource_type,
        required_state=required_state or {},
        satisfied_by=satisfied_by,
      )
    )
    return precond_id

  def _infer_machine_type(self, var_name: str) -> str | None:
    """Infer machine type from variable name."""
    lower_name = var_name.lower()
    for pattern, machine_type in MACHINE_VAR_PATTERNS.items():
      if pattern in lower_name:
        return machine_type
    return None

  def _get_expr_source(self, node: cst.BaseExpression) -> str:
    """Get source code string for an expression."""
    return cst.Module([]).code_for_node(node)

  def _get_receiver_info(
    self, func: cst.Attribute
  ) -> tuple[str, str | None]:
    """Extract receiver variable name and inferred type from attribute access.

    Returns:
        Tuple of (receiver_name, receiver_type).

    """
    receiver = func.value
    receiver_name = "?"

    if isinstance(receiver, cst.Name):
      receiver_name = receiver.value
    elif isinstance(receiver, cst.Attribute):
      # Handle chained access like self.lh.method()
      receiver_name = func.attr.value

    receiver_type = self._type_tracker.get_type(receiver_name)
    return receiver_name, receiver_type

  def visit_For(self, node: cst.For) -> bool:  # noqa: N802
    """Track that the protocol contains loops."""
    self._has_loops = True
    return True

  def visit_While(self, node: cst.While) -> bool:  # noqa: N802
    """Track that the protocol contains loops."""
    self._has_loops = True
    return True

  def visit_If(self, node: cst.If) -> bool:  # noqa: N802
    """Track that the protocol contains conditionals."""
    self._has_conditionals = True
    return True

  def visit_Assign(self, node: cst.Assign) -> bool:  # noqa: N802
    """Track variable assignments for type inference."""
    # Get assigned variable name(s)
    for target in node.targets:
      if isinstance(target.target, cst.Name):
        var_name = target.target.value
        source_expr = self._get_expr_source(node.value)

        # Try to infer type from the assignment
        inferred_type = self._infer_assignment_type(node.value)
        if inferred_type:
          self._type_tracker.set_type(var_name, inferred_type, source_expr)

          # If this is a PLR resource, add a ResourceNode
          resource_types = extract_resource_types(inferred_type)
          if resource_types:
            elem_type = get_element_type(inferred_type)
            primary_type = elem_type if elem_type else resource_types[0]
            chain = get_parental_chain(primary_type, self._deck_layout_type)

            self._resources[var_name] = ResourceNode(
              variable_name=var_name,
              declared_type=inferred_type,
              element_type=elem_type,
              is_container=is_container_type(inferred_type),
              is_parameter=False,
              parental_chain=chain.chain,
              source_expression=source_expr,
            )

    return True

  def _infer_assignment_type(self, value: cst.BaseExpression) -> str | None:
    """Infer the type of an assignment value."""
    # Handle subscript: plate["A1:A8"]
    if isinstance(value, cst.Subscript):
      base_name = self._get_expr_source(value.value)
      base_type = self._type_tracker.get_type(base_name)
      if base_type:
        # Get the subscript key
        if value.slice and isinstance(value.slice[0].slice, cst.Index):
          key_node = value.slice[0].slice.value
          if isinstance(key_node, (cst.SimpleString, cst.ConcatenatedString)):
            key = self._get_expr_source(key_node).strip("\"'")
            return self._type_tracker.infer_subscript_type(base_type, key)
        # Default to list of element type
        elem = get_element_type(base_type)
        if elem:
          return f"list[{elem}]"
      return None

    # Handle attribute access: plate.wells()
    if isinstance(value, cst.Call) and isinstance(value.func, cst.Attribute):
      base_name = self._get_expr_source(value.func.value)
      base_type = self._type_tracker.get_type(base_name)
      attr_name = value.func.attr.value
      if base_type:
        return self._type_tracker.infer_attribute_type(base_type, attr_name)

    # Handle simple name reference
    if isinstance(value, cst.Name):
      return self._type_tracker.get_type(value.value)

    return None

  def visit_Call(self, node: cst.Call) -> bool:  # noqa: N802
    """Process method calls to extract operations."""
    # Only process attribute method calls (e.g., lh.aspirate())
    if not isinstance(node.func, cst.Attribute):
      return True

    method_name = node.func.attr.value
    receiver_name, receiver_type = self._get_receiver_info(node.func)

    # Check if this is a machine method call
    machine_type = self._infer_machine_type(receiver_name)
    if machine_type:
      self._machine_types.add(machine_type)

      # Create operation node
      op_id = self._generate_op_id()
      args = self._extract_arguments(node)

      # Determine preconditions for this operation
      precondition_ids = self._determine_preconditions(method_name, args, receiver_name)

      # Check if this operation creates state
      creates = []
      if method_name in TIPS_LOADING_METHODS:
        creates.append("tips_loaded")
        self._active_states.add("tips_loaded")
        # Satisfy any tips_loaded preconditions from this operation
        for p in self._preconditions:
          if (
            p.precondition_type == PreconditionType.TIPS_LOADED
            and p.satisfied_by is None
          ):
            p.satisfied_by = op_id

      if method_name in TIPS_DROPPING_METHODS:
        self._active_states.discard("tips_loaded")

      # Determine node type
      node_type = GraphNodeType.STATIC
      depends_on = []
      for arg_name, arg_expr in args.items():
        if arg_expr in self._parameter_names:
          depends_on.append(arg_expr)
          node_type = GraphNodeType.DYNAMIC

      operation = OperationNode(
        id=op_id,
        line_number=self._current_line,
        method_name=method_name,
        receiver_variable=receiver_name,
        receiver_type=receiver_type,
        arguments=args,
        node_type=node_type,
        preconditions=precondition_ids,
        creates_state=creates,
        depends_on_params=depends_on,
      )

      self._operations.append(operation)
      self._execution_order.append(op_id)

    return True

  def _extract_arguments(self, node: cst.Call) -> dict[str, str]:
    """Extract arguments from a Call node."""
    args: dict[str, str] = {}

    # Positional arguments (try to use common names)
    common_arg_names = ["resource", "volume", "source", "destination", "tips"]
    for i, arg in enumerate(node.args):
      if arg.keyword:
        arg_name = arg.keyword.value
      elif i < len(common_arg_names):
        arg_name = common_arg_names[i]
      else:
        arg_name = f"arg{i}"

      args[arg_name] = self._get_expr_source(arg.value)

    return args

  def _determine_preconditions(
    self,
    method_name: str,
    args: dict[str, str],
    receiver_name: str,
  ) -> list[str]:
    """Determine preconditions required for an operation."""
    precondition_ids: list[str] = []

    # Tips required?
    if method_name in TIPS_REQUIRED_METHODS:
      if "tips_loaded" not in self._active_states:
        precond_id = self._create_precondition(
          PreconditionType.TIPS_LOADED,
          receiver_name,
          resource_type="TipRack",
        )
        precondition_ids.append(precond_id)

    # Plate access required?
    if method_name in PLATE_ACCESS_METHODS:
      # Check first argument for resource variable
      resource_arg = args.get("resource") or args.get("source")
      if resource_arg:
        # Extract base variable name
        base_var = resource_arg.split("[")[0].split(".")[0].strip()
        if base_var in self._resources:
          precond_id = self._create_precondition(
            PreconditionType.PLATE_ACCESSIBLE,
            base_var,
            resource_type=self._resources[base_var].declared_type,
          )
          precondition_ids.append(precond_id)

    return precondition_ids

  def build_graph(self) -> ProtocolComputationGraph:
    """Build the final ProtocolComputationGraph."""
    # Collect all resource types
    resource_types: set[str] = set()
    for res in self._resources.values():
      for rt in extract_resource_types(res.declared_type):
        resource_types.add(rt)

    return ProtocolComputationGraph(
      protocol_fqn=self._protocol_fqn,
      protocol_name=self._protocol_name,
      operations=self._operations,
      resources=self._resources,
      preconditions=self._preconditions,
      execution_order=self._execution_order,
      machine_types=sorted(self._machine_types),
      resource_types=sorted(resource_types),
      has_loops=self._has_loops,
      has_conditionals=self._has_conditionals,
    )


# =============================================================================
# Convenience Functions
# =============================================================================


def extract_graph_from_function(
  function_node: cst.FunctionDef,
  module_name: str,
  parameter_types: dict[str, str] | None = None,
  deck_layout_type: DeckLayoutType = DeckLayoutType.CARRIER_BASED,
) -> ProtocolComputationGraph:
  """Extract a computation graph from a function definition.

  Args:
      function_node: The LibCST FunctionDef node to analyze.
      module_name: The module name for FQN generation.
      parameter_types: Optional pre-extracted parameter types.
      deck_layout_type: Type of deck layout.

  Returns:
      The extracted ProtocolComputationGraph.

  """
  func_name = function_node.name.value
  fqn = f"{module_name}.{func_name}"

  # Extract parameter types if not provided
  if parameter_types is None:
    parameter_types = {}
    for param in function_node.params.params:
      param_name = param.name.value
      if param.annotation:
        type_hint = cst.Module([]).code_for_node(param.annotation.annotation)
        parameter_types[param_name] = type_hint
      else:
        parameter_types[param_name] = "Any"

  extractor = ComputationGraphExtractor(
    protocol_fqn=fqn,
    parameter_types=parameter_types,
    deck_layout_type=deck_layout_type,
  )

  # Visit the function node - this will traverse into the body
  _walk_cst_node(function_node, extractor)

  return extractor.build_graph()


def _walk_cst_node(node: cst.CSTNode, visitor: cst.CSTVisitor) -> None:
  """Manually walk a CST node with a visitor.

  LibCST's walk method is only available on Module, so we need to
  manually traverse the tree for other node types.
  """
  # Visit this node
  should_descend = True

  # Check for visitor methods
  node_type = type(node).__name__
  visit_method = getattr(visitor, f"visit_{node_type}", None)
  if visit_method:
    result = visit_method(node)
    if result is False:
      should_descend = False

  # Descend into children if allowed
  if should_descend:
    for child in node.children:
      if isinstance(child, cst.CSTNode):
        _walk_cst_node(child, visitor)


def extract_graph_from_source(
  source: str,
  function_name: str,
  module_name: str = "protocol",
  deck_layout_type: DeckLayoutType = DeckLayoutType.CARRIER_BASED,
) -> ProtocolComputationGraph | None:
  """Extract a computation graph from source code.

  Args:
      source: Python source code containing the function.
      function_name: Name of the function to extract.
      module_name: Module name for FQN generation.
      deck_layout_type: Type of deck layout.

  Returns:
      The extracted ProtocolComputationGraph, or None if function not found.

  """
  try:
    tree = cst.parse_module(source)
  except cst.ParserSyntaxError:
    return None

  # Find the function
  for stmt in tree.body:
    if isinstance(stmt, cst.FunctionDef) and stmt.name.value == function_name:
      return extract_graph_from_function(
        stmt, module_name, deck_layout_type=deck_layout_type
      )

  return None
