"""Operation recorder for protocol tracing.

This module provides the OperationRecorder class that collects operations
recorded during protocol tracing and builds them into a ProtocolComputationGraph.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from praxis.backend.utils.plr_static_analysis.models import (
  GraphNodeType,
  OperationNode,
  PreconditionType,
  ProtocolComputationGraph,
  ResourceNode,
  StatePrecondition,
)


# =============================================================================
# Loop/Conditional Context
# =============================================================================


@dataclass
class LoopContext:
  """Context for a loop during tracing."""

  iterator_var: str
  """Loop variable name"""

  source_collection: str
  """Collection being iterated"""

  operation_ids: list[str] = field(default_factory=list)
  """Operations recorded inside this loop"""


@dataclass
class ConditionalContext:
  """Context for a conditional during tracing."""

  condition_expr: str
  """The condition expression"""

  true_branch_ops: list[str] = field(default_factory=list)
  """Operations in the true branch"""

  false_branch_ops: list[str] = field(default_factory=list)
  """Operations in the false branch"""

  in_true_branch: bool = True
  """Currently recording true branch"""


# =============================================================================
# Operation Recorder
# =============================================================================


class OperationRecorder:
  """Records operations during protocol tracing.

  This class maintains state during protocol tracing, collecting:
  - Machine method calls as OperationNodes
  - Loop contexts (foreach patterns)
  - Conditional contexts (if/else branches)
  - Resource tracking

  After tracing, call build_graph() to produce a ProtocolComputationGraph.
  """

  def __init__(
    self,
    protocol_fqn: str,
    protocol_name: str | None = None,
    parameter_types: dict[str, str] | None = None,
  ) -> None:
    """Initialize the recorder.

    Args:
        protocol_fqn: Fully qualified name of the protocol.
        protocol_name: Simple name (defaults to last part of fqn).
        parameter_types: Mapping of parameter names to type hints.

    """
    self._protocol_fqn = protocol_fqn
    self._protocol_name = protocol_name or protocol_fqn.split(".")[-1]
    self._parameter_types = parameter_types or {}

    # Collected data
    self._operations: list[OperationNode] = []
    self._resources: dict[str, ResourceNode] = {}
    self._preconditions: list[StatePrecondition] = []
    self._execution_order: list[str] = []

    # Counters
    self._op_counter = 0
    self._precond_counter = 0

    # Control flow tracking
    self._loop_stack: list[LoopContext] = []
    self._conditional_stack: list[ConditionalContext] = []
    self._active_states: set[str] = set()

    # Machine types discovered
    self._machine_types: set[str] = set()
    self._resource_types: set[str] = set()

    # Flags
    self._has_loops = False
    self._has_conditionals = False

  def _generate_op_id(self) -> str:
    """Generate a unique operation ID."""
    self._op_counter += 1
    return f"traced_op_{self._op_counter}"

  def _generate_precond_id(self) -> str:
    """Generate a unique precondition ID."""
    self._precond_counter += 1
    return f"traced_precond_{self._precond_counter}"

  # ---------------------------------------------------------------------------
  # Operation Recording
  # ---------------------------------------------------------------------------

  def record_operation(
    self,
    receiver: str,
    receiver_type: str,
    method: str,
    args: list[str],
    kwargs: dict[str, str],
  ) -> str:
    """Record a method call operation.

    Args:
        receiver: Variable name of the receiver (e.g., 'lh').
        receiver_type: Type of the receiver (e.g., 'liquid_handler').
        method: Method name (e.g., 'aspirate').
        args: Positional arguments as strings.
        kwargs: Keyword arguments as strings.

    Returns:
        The operation ID.

    """
    op_id = self._generate_op_id()

    # Track machine type
    self._machine_types.add(receiver_type)

    # Build arguments dict
    arg_names = ["resource", "volume", "source", "destination", "tips"]
    arguments: dict[str, str] = {}
    for i, arg in enumerate(args):
      arg_name = arg_names[i] if i < len(arg_names) else f"arg{i}"
      arguments[arg_name] = arg
    arguments.update(kwargs)

    # Determine preconditions
    precondition_ids = self._determine_preconditions(method, arguments, receiver)

    # Determine node type
    node_type = GraphNodeType.STATIC
    if self._loop_stack:
      node_type = GraphNodeType.FOREACH

    # Create operation node
    operation = OperationNode(
      id=op_id,
      line_number=0,  # Not available during tracing
      method_name=method,
      receiver_variable=receiver,
      receiver_type=receiver_type,
      arguments=arguments,
      node_type=node_type,
      preconditions=precondition_ids,
    )

    # Handle state changes
    if method in {"pick_up_tips", "pick_up_tips96"}:
      operation.creates_state.append("tips_loaded")
      self._active_states.add("tips_loaded")
      # Satisfy pending tips_loaded preconditions
      for p in self._preconditions:
        if p.precondition_type == PreconditionType.TIPS_LOADED and p.satisfied_by is None:
          p.satisfied_by = op_id

    if method in {"drop_tips", "drop_tips96", "return_tips"}:
      self._active_states.discard("tips_loaded")

    # Record in appropriate context
    if self._loop_stack:
      self._loop_stack[-1].operation_ids.append(op_id)
      operation.foreach_source = self._loop_stack[-1].source_collection
    elif self._conditional_stack:
      ctx = self._conditional_stack[-1]
      if ctx.in_true_branch:
        ctx.true_branch_ops.append(op_id)
      else:
        ctx.false_branch_ops.append(op_id)

    self._operations.append(operation)
    self._execution_order.append(op_id)

    return op_id

  def _determine_preconditions(
    self,
    method: str,
    arguments: dict[str, str],
    receiver: str,
  ) -> list[str]:
    """Determine preconditions for an operation."""
    precond_ids: list[str] = []

    # Tips required for liquid handling operations
    tips_required = {
      "aspirate",
      "dispense",
      "transfer",
      "mix",
      "blow_out",
      "touch_tip",
      "drop_tips",
      "return_tips",
    }

    if method in tips_required and "tips_loaded" not in self._active_states:
      precond_id = self._generate_precond_id()
      self._preconditions.append(
        StatePrecondition(
          id=precond_id,
          precondition_type=PreconditionType.TIPS_LOADED,
          resource_variable=receiver,
          resource_type="TipRack",
        )
      )
      precond_ids.append(precond_id)

    return precond_ids

  # ---------------------------------------------------------------------------
  # Resource Registration
  # ---------------------------------------------------------------------------

  def register_resource(
    self,
    name: str,
    declared_type: str,
    resource_type: str,
    is_parameter: bool = True,
    parental_chain: list[str] | None = None,
  ) -> None:
    """Register a resource for tracking.

    Args:
        name: Variable name.
        declared_type: Full type hint.
        resource_type: PLR resource type.
        is_parameter: Whether this is a function parameter.
        parental_chain: Parent types to deck.

    """
    self._resource_types.add(resource_type)

    # Determine element type for containers
    element_type = None
    is_container = False
    if "list[" in declared_type.lower() or "sequence[" in declared_type.lower():
      is_container = True
      # Extract inner type
      if "Well" in declared_type:
        element_type = "Well"
      elif "TipSpot" in declared_type:
        element_type = "TipSpot"

    self._resources[name] = ResourceNode(
      variable_name=name,
      declared_type=declared_type,
      element_type=element_type,
      is_container=is_container,
      is_parameter=is_parameter,
      parental_chain=parental_chain or [],
    )

    # Add resource_on_deck precondition for parameters
    if is_parameter:
      precond_id = self._generate_precond_id()
      self._preconditions.append(
        StatePrecondition(
          id=precond_id,
          precondition_type=PreconditionType.RESOURCE_ON_DECK,
          resource_variable=name,
          resource_type=resource_type,
          can_be_auto_satisfied=True,
        )
      )

  # ---------------------------------------------------------------------------
  # Control Flow
  # ---------------------------------------------------------------------------

  def enter_loop(self, iterator_var: str, source_collection: str) -> None:
    """Record entering a loop.

    Args:
        iterator_var: The loop variable name.
        source_collection: The collection being iterated.

    """
    self._has_loops = True
    self._loop_stack.append(
      LoopContext(iterator_var=iterator_var, source_collection=source_collection)
    )

  def exit_loop(self) -> None:
    """Record exiting a loop."""
    if self._loop_stack:
      ctx = self._loop_stack.pop()
      # Mark operations as part of foreach
      for op_id in ctx.operation_ids:
        for op in self._operations:
          if op.id == op_id:
            op.foreach_body.append(op_id)

  def enter_conditional(self, condition_expr: str) -> None:
    """Record entering a conditional.

    Args:
        condition_expr: The condition expression as string.

    """
    self._has_conditionals = True
    self._conditional_stack.append(ConditionalContext(condition_expr=condition_expr))

  def switch_to_false_branch(self) -> None:
    """Switch to recording the false branch of current conditional."""
    if self._conditional_stack:
      self._conditional_stack[-1].in_true_branch = False

  def exit_conditional(self) -> None:
    """Record exiting a conditional."""
    if self._conditional_stack:
      self._conditional_stack.pop()

  # ---------------------------------------------------------------------------
  # Graph Building
  # ---------------------------------------------------------------------------

  def build_graph(self) -> ProtocolComputationGraph:
    """Build the final computation graph from recorded operations.

    Returns:
        A ProtocolComputationGraph containing all recorded data.

    """
    return ProtocolComputationGraph(
      protocol_fqn=self._protocol_fqn,
      protocol_name=self._protocol_name,
      operations=self._operations,
      resources=self._resources,
      preconditions=self._preconditions,
      execution_order=self._execution_order,
      machine_types=sorted(self._machine_types),
      resource_types=sorted(self._resource_types),
      has_loops=self._has_loops,
      has_conditionals=self._has_conditionals,
    )
