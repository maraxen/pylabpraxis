"""Hierarchical simulation pipeline.

This module orchestrates multi-level protocol simulation:
1. Structural validation (Level 0) - using existing tracers
2. Boolean state pass (Level 1) - fast binary state
3. Symbolic state pass (Level 2) - constraint-based volumes
4. Exact state pass (Level 3) - numeric edge case detection

The hierarchical approach enables efficient simulation by detecting
issues at the cheapest level that can catch them.
"""

from __future__ import annotations

import asyncio
from praxis.backend.utils.async_run import run_sync
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from praxis.backend.core.simulation.state_models import (
  BooleanLiquidState,
  SimulationState,
  StateViolation,
)
from praxis.backend.core.simulation.stateful_tracers import (
  StatefulTracedMachine,
  StatefulTracedResource,
)
from praxis.backend.core.tracing.executor import (
  ProtocolTracingExecutor,
  TracingError,
  infer_machine_type,
)
from praxis.backend.core.tracing.recorder import OperationRecorder
from praxis.backend.utils.plr_static_analysis.resource_hierarchy import (
  DeckLayoutType,
  get_parental_chain,
)
from praxis.common.type_inspection import extract_resource_types

if TYPE_CHECKING:
  from collections.abc import Callable

# =============================================================================
# Result Models
# =============================================================================


class InferredRequirement(BaseModel):
  """A requirement inferred from simulation."""

  requirement_type: str = Field(description="Type: tips_required, resource_on_deck, liquid_present")
  resource: str | None = Field(default=None, description="Resource involved")
  details: dict[str, Any] = Field(default_factory=dict)
  inferred_at_level: str = Field(description="Level at which this was inferred")


class HierarchicalSimulationResult(BaseModel):
  """Result of hierarchical protocol simulation."""

  passed: bool = Field(default=False, description="Whether simulation passed all levels")

  level_completed: str = Field(default="none", description="Highest level completed without failure")

  level_failed: str | None = Field(default=None, description="Level at which simulation failed")

  violations: list[dict[str, Any]] = Field(default_factory=list, description="All violations found")

  inferred_requirements: list[InferredRequirement] = Field(
    default_factory=list, description="Requirements inferred from simulation"
  )

  computation_graph: dict[str, Any] | None = Field(default=None, description="Extracted computation graph")

  structural_error: str | None = Field(default=None, description="Structural error if Level 0 failed")

  edge_cases: list[dict[str, Any]] = Field(
    default_factory=list, description="Edge cases detected at exact level"
  )

  execution_time_ms: float = Field(default=0.0, description="Total simulation time in milliseconds")


# =============================================================================
# Stateful Simulation Result
# =============================================================================


@dataclass
class StatefulSimulationResult:
  """Result of running protocol with stateful tracers."""

  final_state: SimulationState
  """State after execution"""

  violations: list[StateViolation] = field(default_factory=list)
  """Violations detected during execution"""

  exception: Exception | None = None
  """Exception if execution failed"""


# =============================================================================
# Hierarchical Simulator
# =============================================================================


class HierarchicalSimulator:
  """Runs protocol with state-aware tracers at multiple precision levels.

  The simulator executes the protocol multiple times with increasing
  precision, detecting issues at the cheapest level possible:

  1. Level 0 (Structural): Catch wrong methods, bad signatures
  2. Level 1 (Boolean): Catch missing tips, empty wells (fast)
  3. Level 2 (Symbolic): Catch constraint violations (medium)
  4. Level 3 (Exact): Catch numeric edge cases (precise)

  Usage:
      simulator = HierarchicalSimulator()
      result = await simulator.simulate(
          protocol_func=my_protocol,
          parameter_types={"lh": "LiquidHandler", "plate": "Plate"},
      )
      if result.passed:
          print("Protocol validated successfully")
      else:
          print(f"Failed at {result.level_failed}: {result.violations}")

  """

  def __init__(
    self,
    deck_layout_type: DeckLayoutType = DeckLayoutType.CARRIER_BASED,
  ) -> None:
    """Initialize the simulator.

    Args:
        deck_layout_type: Type of deck layout for resource hierarchy.

    """
    self._deck_layout_type = deck_layout_type
    self._base_executor = ProtocolTracingExecutor(deck_layout_type=deck_layout_type)

  async def simulate(
    self,
    protocol_func: Callable[..., Any],
    parameter_types: dict[str, str],
    initial_state: SimulationState | None = None,
    run_all_levels: bool = False,
  ) -> HierarchicalSimulationResult:
    """Run hierarchical simulation with progressive refinement.

    Args:
        protocol_func: The protocol function to simulate.
        parameter_types: Mapping of parameter names to type hints.
        initial_state: Optional initial state (defaults to empty boolean).
        run_all_levels: If True, run all levels even if earlier ones fail.

    Returns:
        HierarchicalSimulationResult with violations and inferred requirements.

    """
    import time

    start_time = time.perf_counter()

    # Level 0: Structural validation
    structural_result = await self._run_structural_validation(protocol_func, parameter_types)

    if structural_result.structural_error:
      return HierarchicalSimulationResult(
        passed=False,
        level_failed="structural",
        structural_error=structural_result.structural_error,
        execution_time_ms=(time.perf_counter() - start_time) * 1000,
      )

    # Level 1: Boolean state pass
    bool_state = initial_state or SimulationState.default_boolean()
    bool_result = await self._run_with_state(protocol_func, parameter_types, bool_state)

    if bool_result.violations and not run_all_levels:
      return HierarchicalSimulationResult(
        passed=False,
        level_completed="structural",
        level_failed="boolean",
        violations=[self._violation_to_dict(v) for v in bool_result.violations],
        computation_graph=structural_result.computation_graph,
        inferred_requirements=self._infer_requirements(bool_result),
        execution_time_ms=(time.perf_counter() - start_time) * 1000,
      )

    # Level 2: Symbolic state pass
    sym_state = bool_state.promote()
    sym_result = await self._run_with_state(protocol_func, parameter_types, sym_state)

    if sym_result.violations and not run_all_levels:
      all_violations = bool_result.violations + sym_result.violations
      return HierarchicalSimulationResult(
        passed=False,
        level_completed="boolean",
        level_failed="symbolic",
        violations=[self._violation_to_dict(v) for v in all_violations],
        computation_graph=structural_result.computation_graph,
        inferred_requirements=self._infer_requirements(sym_result),
        execution_time_ms=(time.perf_counter() - start_time) * 1000,
      )

    # Level 3: Exact pass with edge case detection
    edge_cases = self._find_edge_cases(sym_result)
    exact_violations: list[StateViolation] = []

    for case in edge_cases:
      exact_state = sym_state.promote_to_exact_with_values(case)
      exact_result = await self._run_with_state(protocol_func, parameter_types, exact_state)
      if exact_result.violations:
        exact_violations.extend(exact_result.violations)

    all_violations = bool_result.violations + sym_result.violations + exact_violations

    if all_violations:
      return HierarchicalSimulationResult(
        passed=False,
        level_completed="symbolic" if not exact_violations else "exact",
        level_failed="exact" if exact_violations else "symbolic",
        violations=[self._violation_to_dict(v) for v in all_violations],
        computation_graph=structural_result.computation_graph,
        inferred_requirements=self._infer_requirements(sym_result),
        edge_cases=[{"values": case, "violations": len(exact_violations)} for case in edge_cases],
        execution_time_ms=(time.perf_counter() - start_time) * 1000,
      )

    # All levels passed
    return HierarchicalSimulationResult(
      passed=True,
      level_completed="exact",
      computation_graph=structural_result.computation_graph,
      inferred_requirements=self._infer_requirements(sym_result),
      execution_time_ms=(time.perf_counter() - start_time) * 1000,
    )

  async def _run_structural_validation(
    self,
    protocol_func: Callable[..., Any],
    parameter_types: dict[str, str],
  ) -> HierarchicalSimulationResult:
    """Level 0: Structural validation using base tracers.

    Catches wrong methods, bad signatures, structural errors.
    """
    try:
      graph = await self._base_executor.trace_protocol(
        protocol_func=protocol_func,
        parameter_types=parameter_types,
      )
      return HierarchicalSimulationResult(
        passed=True,
        computation_graph=graph.model_dump(),
      )
    except TracingError as e:
      return HierarchicalSimulationResult(
        passed=False,
        structural_error=str(e),
      )
    except AttributeError as e:
      return HierarchicalSimulationResult(
        passed=False,
        structural_error=f"Unknown method or attribute: {e}",
      )
    except Exception as e:
      return HierarchicalSimulationResult(
        passed=False,
        structural_error=f"Unexpected error during tracing: {e}",
      )

  async def _run_with_state(
    self,
    protocol_func: Callable[..., Any],
    parameter_types: dict[str, str],
    state: SimulationState,
  ) -> StatefulSimulationResult:
    """Run protocol with state-aware tracers.

    Args:
        protocol_func: The protocol function.
        parameter_types: Parameter type mapping.
        state: Initial simulation state.

    Returns:
        Result with final state and violations.

    """
    # Create stateful tracers
    tracers = self._create_stateful_tracers(parameter_types, state)

    # Execute protocol
    try:
      result = protocol_func(**tracers)
      if asyncio.iscoroutine(result):
        await result
    except Exception:
      # Collect violations even on exception
      pass

    # Collect violations from all machine tracers
    violations: list[StateViolation] = []
    for tracer in tracers.values():
      if isinstance(tracer, StatefulTracedMachine):
        violations.extend(tracer.violations)

    return StatefulSimulationResult(
      final_state=state,
      violations=violations,
    )

  def _create_stateful_tracers(
    self,
    parameter_types: dict[str, str],
    state: SimulationState,
  ) -> dict[str, Any]:
    """Create stateful tracer objects for each parameter.

    Args:
        parameter_types: Mapping of parameter names to type hints.
        state: Simulation state to share among tracers.

    Returns:
        Dictionary of parameter names to tracer objects.

    """
    # Create a recorder for tracking operations
    recorder = OperationRecorder(
      protocol_fqn="simulation",
      protocol_name="simulation",
      parameter_types=parameter_types,
    )

    tracers: dict[str, Any] = {}

    for param_name, type_hint in parameter_types.items():
      tracer = self._create_stateful_tracer_for_type(
        param_name, type_hint, recorder, state
      )
      if tracer is not None:
        tracers[param_name] = tracer

    return tracers

  def _create_stateful_tracer_for_type(
    self,
    name: str,
    type_hint: str,
    recorder: OperationRecorder,
    state: SimulationState,
  ) -> Any:
    """Create appropriate stateful tracer for a type hint."""
    # Check for machine types
    machine_type = infer_machine_type(type_hint)
    if machine_type:
      return StatefulTracedMachine(
        name=name,
        recorder=recorder,
        declared_type=type_hint,
        machine_type=machine_type,
        state=state,
      )

    # Check for PLR resource types
    resource_types = extract_resource_types(type_hint)
    if resource_types:
      primary_type = resource_types[0]
      chain = get_parental_chain(primary_type, self._deck_layout_type)

      # Register resource with recorder
      recorder.register_resource(
        name=name,
        declared_type=type_hint,
        resource_type=primary_type,
        is_parameter=True,
        parental_chain=chain.chain,
      )

      # Mark as on deck in state
      state.deck_state.place_on_deck(name)

      # Mark as having liquid (default assumption for source resources)
      if isinstance(state.liquid_state, BooleanLiquidState):
        state.liquid_state.set_has_liquid(name, True)
        state.liquid_state.set_has_capacity(name, True)

      return StatefulTracedResource(
        name=name,
        recorder=recorder,
        declared_type=type_hint,
        resource_type=primary_type,
        parental_chain=chain.chain,
        state=state,
      )

    # For primitive types, return placeholder values
    if type_hint in {"float", "int", "str", "bool"}:
      return self._get_default_for_primitive(type_hint)

    if "float" in type_hint.lower():
      return 50.0
    if "int" in type_hint.lower():
      return 1
    if "str" in type_hint.lower():
      return "simulated_value"
    if "bool" in type_hint.lower():
      return True

    return None

  def _get_default_for_primitive(self, type_hint: str) -> Any:
    """Get default value for primitive types."""
    defaults: dict[str, Any] = {
      "float": 50.0,
      "int": 1,
      "str": "simulated_value",
      "bool": True,
    }
    return defaults.get(type_hint)

  def _violation_to_dict(self, violation: StateViolation) -> dict[str, Any]:
    """Convert a StateViolation to a dictionary."""
    return {
      "type": violation.violation_type.value,
      "operation_id": violation.operation_id,
      "method_name": violation.method_name,
      "resource": violation.resource_name,
      "message": violation.message,
      "suggested_fix": violation.suggested_fix,
      "level": violation.state_level.value,
      "details": violation.details,
    }

  def _infer_requirements(
    self,
    result: StatefulSimulationResult,
  ) -> list[InferredRequirement]:
    """Infer requirements from simulation result.

    Analyzes violations and state to determine what requirements
    the protocol has that weren't satisfied.
    """
    requirements: list[InferredRequirement] = []

    for violation in result.violations:
      if violation.violation_type.value == "tips_not_loaded":
        requirements.append(
          InferredRequirement(
            requirement_type="tips_required",
            details={"before_operation": violation.method_name},
            inferred_at_level=violation.state_level.value,
          )
        )
      elif violation.violation_type.value == "resource_not_on_deck":
        requirements.append(
          InferredRequirement(
            requirement_type="resource_on_deck",
            resource=violation.resource_name,
            inferred_at_level=violation.state_level.value,
          )
        )
      elif violation.violation_type.value == "no_liquid":
        requirements.append(
          InferredRequirement(
            requirement_type="liquid_present",
            resource=violation.resource_name,
            inferred_at_level=violation.state_level.value,
          )
        )

    return requirements

  def _find_edge_cases(
    self,
    result: StatefulSimulationResult,
  ) -> list[dict[str, float]]:
    """Find edge cases to test at exact level.

    Analyzes symbolic constraints to find boundary values
    that should be tested with exact simulation.
    """
    # For now, return a set of default edge cases
    # A full implementation would analyze symbolic constraints
    edge_cases: list[dict[str, float]] = []

    # Test with near-empty volumes
    edge_cases.append({"default": 1.0})

    # Test with near-full volumes
    edge_cases.append({"default": 199.0})

    # Test with exact transfer amounts
    edge_cases.append({"default": 50.0})

    return edge_cases


# =============================================================================
# Convenience Functions
# =============================================================================


async def simulate_protocol(
  protocol_func: Callable[..., Any],
  parameter_types: dict[str, str],
  initial_state: SimulationState | None = None,
  deck_layout_type: DeckLayoutType = DeckLayoutType.CARRIER_BASED,
) -> HierarchicalSimulationResult:
  """Simulate a protocol with hierarchical state checking.

  This is a convenience function that creates a HierarchicalSimulator
  and runs the simulation.

  Args:
      protocol_func: The protocol function to simulate.
      parameter_types: Mapping of parameter names to type hints.
      initial_state: Optional initial state.
      deck_layout_type: Type of deck layout.

  Returns:
      HierarchicalSimulationResult with violations and requirements.

  """
  simulator = HierarchicalSimulator(deck_layout_type=deck_layout_type)
  return await simulator.simulate(
    protocol_func=protocol_func,
    parameter_types=parameter_types,
    initial_state=initial_state,
  )


def simulate_protocol_sync(
  protocol_func: Callable[..., Any],
  parameter_types: dict[str, str],
  initial_state: SimulationState | None = None,
  deck_layout_type: DeckLayoutType = DeckLayoutType.CARRIER_BASED,
) -> HierarchicalSimulationResult:
  """Synchronous version of simulate_protocol."""
  return run_sync(
    simulate_protocol(
      protocol_func=protocol_func,
      parameter_types=parameter_types,
      initial_state=initial_state,
      deck_layout_type=deck_layout_type,
    )
  )
