"""Graph-based protocol replay for browser-compatible simulation.

This module enables simulation by replaying a pre-extracted computation graph
with stateful tracers, without requiring the original protocol function.

Key benefits:
- Works in Pyodide (no PLR module imports needed)
- Uses pre-computed graph from backend discovery
- Catches structural and state violations
- Returns clear error messages

Limitations:
- Cannot catch dynamic/runtime issues
- Cannot execute conditional branches (uses static analysis)
- Loop iterations estimated from items_x × items_y
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field

from praxis.backend.core.simulation.method_contracts import get_contract
from praxis.backend.core.simulation.state_models import (
  BooleanLiquidState,
  SimulationState,
  StateViolation,
  ViolationType,
)
from praxis.backend.utils.plr_static_analysis.models import (
  GraphNodeType,
  OperationNode,
  ProtocolComputationGraph,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Replay Result Types
# =============================================================================


class ReplayViolation(BaseModel):
  """A violation detected during graph replay."""

  operation_id: str = Field(description="ID of the operation that caused violation")
  operation_index: int = Field(description="Index in execution order")
  method_name: str = Field(description="Method that failed")
  receiver: str = Field(description="Variable receiving the call")
  violation_type: str = Field(description="Type of violation")
  message: str = Field(description="Human-readable error message")
  suggested_fix: str | None = Field(default=None, description="How to fix this")
  line_number: int | None = Field(default=None, description="Source line if available")


class GraphReplayResult(BaseModel):
  """Result of replaying a computation graph."""

  passed: bool = Field(default=False, description="Whether replay passed without violations")

  violations: list[ReplayViolation] = Field(
    default_factory=list, description="All violations found during replay"
  )

  operations_executed: int = Field(default=0, description="Number of operations replayed")

  final_state_summary: dict[str, Any] = Field(
    default_factory=dict, description="Summary of final state"
  )

  replay_mode: str = Field(default="graph", description="Replay mode used")

  errors: list[str] = Field(
    default_factory=list, description="Non-violation errors (parse errors, etc.)"
  )


# =============================================================================
# Graph Replay State
# =============================================================================


@dataclass
class ReplayState:
  """Tracks state during graph replay."""

  simulation_state: SimulationState
  """Core simulation state (tips, deck, liquid)"""

  operations_executed: int = 0
  """Counter of operations processed"""

  violations: list[ReplayViolation] = field(default_factory=list)
  """Collected violations"""

  errors: list[str] = field(default_factory=list)
  """Non-violation errors"""


# =============================================================================
# Graph Replay Engine
# =============================================================================


class GraphReplayEngine:
  """Replays computation graphs with state simulation.

  This engine processes a ProtocolComputationGraph, executing each
  operation symbolically while tracking state changes and detecting
  violations.

  Usage:
      engine = GraphReplayEngine()
      result = engine.replay(computation_graph)

      if result.passed:
          print("Protocol graph validates successfully")
      else:
          for v in result.violations:
              print(f"Error at line {v.line_number}: {v.message}")

  """

  def replay(
    self,
    graph: ProtocolComputationGraph | dict[str, Any],
    initial_state: SimulationState | None = None,
  ) -> GraphReplayResult:
    """Replay a computation graph with state simulation.

    Args:
        graph: The computation graph to replay (Pydantic model or dict).
        initial_state: Optional initial state (defaults to boolean with all true).

    Returns:
        GraphReplayResult with violations and state summary.

    """
    # Parse graph if dict
    if isinstance(graph, dict):
      try:
        graph = ProtocolComputationGraph.model_validate(graph)
      except Exception as e:
        return GraphReplayResult(
          passed=False,
          errors=[f"Failed to parse computation graph: {e}"],
        )

    # Initialize state
    state = self._initialize_state(graph, initial_state)

    # Process operations in execution order
    for i, op_id in enumerate(graph.execution_order):
      # Find operation by ID
      operation = self._find_operation(graph, op_id)
      if operation is None:
        state.errors.append(f"Operation {op_id} not found in graph")
        continue

      # Execute operation
      self._execute_operation(operation, graph, state, i)
      state.operations_executed += 1

    # Build result
    return GraphReplayResult(
      passed=len(state.violations) == 0 and len(state.errors) == 0,
      violations=state.violations,
      operations_executed=state.operations_executed,
      final_state_summary=self._summarize_state(state),
      replay_mode="graph",
      errors=state.errors,
    )

  def replay_from_dict(
    self,
    graph_dict: dict[str, Any],
  ) -> GraphReplayResult:
    """Convenience method for replaying from a dictionary.

    Useful when loading from database JSON column.

    Args:
        graph_dict: Computation graph as dictionary.

    Returns:
        GraphReplayResult.

    """
    return self.replay(graph_dict)

  def _initialize_state(
    self,
    graph: ProtocolComputationGraph,
    initial_state: SimulationState | None,
  ) -> ReplayState:
    """Initialize replay state from graph resources."""
    if initial_state:
      sim_state = initial_state.copy()
    else:
      sim_state = SimulationState.default_boolean()

    # Register all resources as on deck with liquid
    for var_name, resource in graph.resources.items():
      sim_state.deck_state.place_on_deck(var_name)

      # Assume source resources have liquid
      if isinstance(sim_state.liquid_state, BooleanLiquidState):
        sim_state.liquid_state.set_has_liquid(var_name, True)
        sim_state.liquid_state.set_has_capacity(var_name, True)

    return ReplayState(simulation_state=sim_state)

  def _find_operation(
    self,
    graph: ProtocolComputationGraph,
    op_id: str,
  ) -> OperationNode | None:
    """Find operation by ID."""
    for op in graph.operations:
      if op.id == op_id:
        return op
    return None

  def _execute_operation(
    self,
    operation: OperationNode,
    graph: ProtocolComputationGraph,
    state: ReplayState,
    index: int,
  ) -> None:
    """Execute a single operation and check for violations."""
    # Handle foreach nodes (loops)
    if operation.node_type == GraphNodeType.FOREACH:
      self._execute_foreach(operation, graph, state, index)
      return

    # Handle conditional nodes
    if operation.node_type == GraphNodeType.CONDITIONAL:
      # For now, we analyze both branches
      self._execute_conditional(operation, graph, state, index)
      return

    # Regular operation - check preconditions
    receiver_type = self._infer_receiver_type(operation, graph)
    contract = get_contract(receiver_type, operation.method_name)

    if contract:
      violations = self._check_contract(
        operation, contract, graph, state.simulation_state
      )
      for v in violations:
        state.violations.append(
          ReplayViolation(
            operation_id=operation.id,
            operation_index=index,
            method_name=operation.method_name,
            receiver=operation.receiver_variable,
            violation_type=v.violation_type.value,
            message=v.message,
            suggested_fix=v.suggested_fix,
            line_number=operation.line_number,
          )
        )

      # Apply effects even if there are violations (to continue analysis)
      self._apply_effects(operation, contract, state.simulation_state)

  def _execute_foreach(
    self,
    operation: OperationNode,
    graph: ProtocolComputationGraph,
    state: ReplayState,
    index: int,
  ) -> None:
    """Execute a foreach loop node.

    Uses items_x × items_y to estimate iteration count, then
    executes body operations once (representing one iteration).
    """
    # Get iteration count estimate
    iteration_count = self._estimate_loop_iterations(operation, graph)

    # Execute body operations (representing loop body)
    for body_op_id in operation.foreach_body:
      body_op = self._find_operation(graph, body_op_id)
      if body_op:
        self._execute_operation(body_op, graph, state, index)

  def _execute_conditional(
    self,
    operation: OperationNode,
    graph: ProtocolComputationGraph,
    state: ReplayState,
    index: int,
  ) -> None:
    """Execute a conditional node.

    Analyzes both branches since we can't know which will be taken.
    """
    # Execute true branch
    for branch_op_id in operation.true_branch:
      branch_op = self._find_operation(graph, branch_op_id)
      if branch_op:
        self._execute_operation(branch_op, graph, state, index)

    # Execute false branch
    for branch_op_id in operation.false_branch:
      branch_op = self._find_operation(graph, branch_op_id)
      if branch_op:
        self._execute_operation(branch_op, graph, state, index)

  def _infer_receiver_type(
    self,
    operation: OperationNode,
    graph: ProtocolComputationGraph,
  ) -> str:
    """Infer the type of the operation's receiver."""
    # Use explicit type if available
    if operation.receiver_type:
      return operation.receiver_type.lower()

    # Look up in resources
    receiver = operation.receiver_variable
    if receiver in graph.resources:
      resource = graph.resources[receiver]
      declared = resource.declared_type.lower()

      # Map to our contract types
      if "liquidhandler" in declared or "lh" in declared:
        return "liquid_handler"
      if "platereader" in declared or "reader" in declared:
        return "plate_reader"
      if "heatershaker" in declared or "shaker" in declared:
        return "heater_shaker"

      return declared

    return "unknown"

  def _check_contract(
    self,
    operation: OperationNode,
    contract: Any,
    graph: ProtocolComputationGraph,
    state: SimulationState,
  ) -> list[StateViolation]:
    """Check method contract preconditions."""
    violations: list[StateViolation] = []

    # Check tips requirement
    if contract.requires_tips and not state.tip_state.tips_loaded:
      violations.append(
        StateViolation(
          violation_type=ViolationType.TIPS_NOT_LOADED,
          operation_id=operation.id,
          method_name=operation.method_name,
          message=f"Method '{operation.method_name}' requires tips to be loaded",
          suggested_fix="Add pick_up_tips() before this operation",
          state_level=state.level,
        )
      )

    # Check tips count if specified
    if contract.requires_tips_count:
      if state.tip_state.tips_count < contract.requires_tips_count:
        violations.append(
          StateViolation(
            violation_type=ViolationType.INSUFFICIENT_TIPS,
            operation_id=operation.id,
            method_name=operation.method_name,
            message=f"Method '{operation.method_name}' requires {contract.requires_tips_count} tips, "
            f"only {state.tip_state.tips_count} loaded",
            suggested_fix="Use pick_up_tips96() or ensure enough tips are loaded",
            state_level=state.level,
          )
        )

    # Check deck placement
    for arg_name in contract.requires_on_deck:
      if arg_name in operation.arguments:
        resource_var = operation.arguments[arg_name]
        # Extract variable name from expression (e.g., "plate" from "plate['A1']")
        base_var = resource_var.split("[")[0].split(".")[0]
        if not state.deck_state.is_on_deck(base_var):
          violations.append(
            StateViolation(
              violation_type=ViolationType.RESOURCE_NOT_ON_DECK,
              operation_id=operation.id,
              method_name=operation.method_name,
              resource_name=base_var,
              message=f"Resource '{base_var}' must be on deck for '{operation.method_name}'",
              suggested_fix=f"Ensure '{base_var}' is placed on the deck",
              state_level=state.level,
            )
          )

    # Check liquid presence (for aspirate-like operations)
    if contract.requires_liquid_in:
      arg_name = contract.requires_liquid_in
      if arg_name in operation.arguments:
        resource_var = operation.arguments[arg_name]
        base_var = resource_var.split("[")[0].split(".")[0]
        if isinstance(state.liquid_state, BooleanLiquidState):
          if not state.liquid_state.check_has_liquid(base_var):
            violations.append(
              StateViolation(
                violation_type=ViolationType.NO_LIQUID,
                operation_id=operation.id,
                method_name=operation.method_name,
                resource_name=base_var,
                message=f"Resource '{base_var}' must contain liquid for '{operation.method_name}'",
                suggested_fix=f"Ensure '{base_var}' has liquid before aspiration",
                state_level=state.level,
              )
            )

    return violations

  def _apply_effects(
    self,
    operation: OperationNode,
    contract: Any,
    state: SimulationState,
  ) -> None:
    """Apply contract effects to state."""
    # Tip loading
    if contract.loads_tips:
      state.tip_state.tips_loaded = True
      state.tip_state.tips_count = contract.loads_tips_count or 8

    # Tip dropping
    if contract.drops_tips:
      state.tip_state.tips_loaded = False
      state.tip_state.tips_count = 0

    # Liquid transfer effects handled by state model methods
    # (simplified for graph replay - just track boolean state)

  def _estimate_loop_iterations(
    self,
    operation: OperationNode,
    graph: ProtocolComputationGraph,
  ) -> int:
    """Estimate loop iterations from resource dimensions."""
    if operation.foreach_source:
      source_var = operation.foreach_source.split(".")[0]
      if source_var in graph.resources:
        resource = graph.resources[source_var]
        if resource.items_x and resource.items_y:
          return resource.items_x * resource.items_y

    # Default estimate
    return 96

  def _summarize_state(self, state: ReplayState) -> dict[str, Any]:
    """Create a summary of final state."""
    return {
      "tips_loaded": state.simulation_state.tip_state.tips_loaded,
      "tips_count": state.simulation_state.tip_state.tips_count,
      "resources_on_deck": list(state.simulation_state.deck_state.on_deck.keys()),
      "level": state.simulation_state.level.value,
    }


# =============================================================================
# Convenience Functions
# =============================================================================


def replay_graph(
  graph: ProtocolComputationGraph | dict[str, Any],
  initial_state: SimulationState | None = None,
) -> GraphReplayResult:
  """Replay a computation graph with state simulation.

  Convenience function that creates a GraphReplayEngine and runs replay.

  Args:
      graph: The computation graph to replay.
      initial_state: Optional initial state.

  Returns:
      GraphReplayResult with violations and state summary.

  """
  engine = GraphReplayEngine()
  return engine.replay(graph, initial_state)
