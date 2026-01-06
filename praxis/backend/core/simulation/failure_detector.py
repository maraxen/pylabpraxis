"""Failure mode detection for protocol simulation.

This module enumerates possible failure states and uses early pruning
to efficiently detect all ways a protocol can fail.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from itertools import product
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from praxis.backend.core.simulation.pipeline import (
  HierarchicalSimulator,
)
from praxis.backend.core.simulation.state_models import (
  BooleanLiquidState,
  SimulationState,
)

if TYPE_CHECKING:
  from collections.abc import Callable, Iterator

  from praxis.backend.utils.plr_static_analysis.models import ProtocolComputationGraph

# =============================================================================
# Failure Mode Models
# =============================================================================


class FailureMode(BaseModel):
  """A detected failure mode for a protocol."""

  initial_state: dict[str, Any] = Field(description="State configuration that causes failure")

  failure_point: str = Field(description="Operation ID where failure occurs")

  failure_type: str = Field(description="Type of failure (tips_not_loaded, no_liquid, etc.)")

  message: str = Field(description="Human-readable failure description")

  suggested_fix: str | None = Field(default=None, description="How to prevent this failure")

  severity: str = Field(default="error", description="Severity: error, warning, info")


class FailureDetectionResult(BaseModel):
  """Result of failure mode detection."""

  failure_modes: list[FailureMode] = Field(default_factory=list)

  states_explored: int = Field(default=0, description="Number of states tested")

  states_pruned: int = Field(default=0, description="Number of states skipped via pruning")

  detection_time_ms: float = Field(default=0.0)

  coverage: float = Field(default=0.0, description="Percentage of state space explored")


# =============================================================================
# Boolean State Generator
# =============================================================================


@dataclass
class BooleanStateConfig:
  """Configuration for generating boolean states."""

  resources: list[str] = field(default_factory=list)
  """Resource names to consider for deck placement"""

  tip_states: list[bool] = field(default_factory=lambda: [True, False])
  """Possible tip states to test"""

  liquid_states: list[bool] = field(default_factory=lambda: [True, False])
  """Possible liquid states to test"""


def generate_boolean_states(
  config: BooleanStateConfig,
) -> Iterator[SimulationState]:
  """Generate candidate boolean states for testing.

  Uses combinatorial generation but with smart defaults to
  reduce the state space.

  Args:
      config: Configuration for state generation.

  Yields:
      SimulationState objects to test.

  """
  # Generate deck placement combinations
  # For N resources, we have 2^N combinations, but we can prune:
  # - At least one machine must be present (implied by protocol)
  # - Resources mentioned in protocol should be on deck

  # Generate tip state combinations
  for tips_loaded in config.tip_states:
    # Generate liquid state combinations for each resource
    if not config.resources:
      # No resources - just tip state
      state = SimulationState.default_boolean()
      state.tip_state.tips_loaded = tips_loaded
      if tips_loaded:
        state.tip_state.tips_count = 8  # Default single-channel
      yield state
      continue

    # For each combination of liquid presence
    for liquid_combo in product(config.liquid_states, repeat=len(config.resources)):
      state = SimulationState.default_boolean()
      state.tip_state.tips_loaded = tips_loaded
      if tips_loaded:
        state.tip_state.tips_count = 8

      # Set liquid state for each resource
      liquid_state = BooleanLiquidState()
      for resource, has_liquid in zip(config.resources, liquid_combo, strict=False):
        liquid_state.set_has_liquid(resource, has_liquid)
        liquid_state.set_has_capacity(resource, True)  # Always have some capacity
        state.deck_state.place_on_deck(resource)

      state.liquid_state = liquid_state
      yield state


# =============================================================================
# Failure Mode Detector
# =============================================================================


class FailureModeDetector:
  """Detects possible failure modes by exploring state space.

  Uses early pruning to efficiently detect all ways a protocol can fail:
  - If operation N fails with state S, skip states that match S and
    don't change before N
  - Prioritize testing states most likely to reveal failures

  Usage:
      detector = FailureModeDetector()
      result = await detector.detect(
          protocol_func=my_protocol,
          parameter_types={"lh": "LiquidHandler", "plate": "Plate"},
          graph=computation_graph,
      )
      for mode in result.failure_modes:
          print(f"Failure: {mode.message}")

  """

  def __init__(
    self,
    max_states: int = 100,
    enable_pruning: bool = True,
  ) -> None:
    """Initialize the detector.

    Args:
        max_states: Maximum states to explore.
        enable_pruning: Whether to use early pruning.

    """
    self._max_states = max_states
    self._enable_pruning = enable_pruning
    self._simulator = HierarchicalSimulator()

  async def detect(
    self,
    protocol_func: Callable[..., Any],
    parameter_types: dict[str, str],
    graph: ProtocolComputationGraph | None = None,
  ) -> FailureDetectionResult:
    """Detect failure modes for a protocol.

    Args:
        protocol_func: The protocol function to analyze.
        parameter_types: Parameter type mapping.
        graph: Optional pre-computed computation graph.

    Returns:
        FailureDetectionResult with all detected failure modes.

    """
    import time

    start_time = time.perf_counter()

    # Extract resources from parameter types
    resources = self._extract_resources(parameter_types)

    # Generate candidate states
    config = BooleanStateConfig(resources=resources)
    candidates = list(generate_boolean_states(config))

    # Track results
    failure_modes: list[FailureMode] = []
    pruned_states: set[str] = set()
    states_explored = 0
    states_pruned = 0

    for state in candidates:
      if states_explored >= self._max_states:
        break

      # Check if this state can be pruned
      state_key = self._state_key(state)
      if self._enable_pruning and state_key in pruned_states:
        states_pruned += 1
        continue

      states_explored += 1

      # Run simulation with this state
      result = await self._simulator.simulate(
        protocol_func=protocol_func,
        parameter_types=parameter_types,
        initial_state=state,
      )

      if not result.passed and result.violations:
        # Found a failure mode
        violation = result.violations[0]  # Primary violation

        failure_mode = FailureMode(
          initial_state=self._state_to_dict(state),
          failure_point=violation.get("operation_id", "unknown"),
          failure_type=violation.get("type", "unknown"),
          message=violation.get("message", "Unknown failure"),
          suggested_fix=violation.get("suggested_fix"),
        )
        failure_modes.append(failure_mode)

        # Add to pruned states for future candidates
        if self._enable_pruning:
          self._add_pruned_state(state, violation, pruned_states)

    # Calculate coverage
    total_possible = len(candidates)
    coverage = (states_explored / total_possible * 100) if total_possible > 0 else 100.0

    return FailureDetectionResult(
      failure_modes=failure_modes,
      states_explored=states_explored,
      states_pruned=states_pruned,
      detection_time_ms=(time.perf_counter() - start_time) * 1000,
      coverage=coverage,
    )

  def detect_sync(
    self,
    protocol_func: Callable[..., Any],
    parameter_types: dict[str, str],
    graph: ProtocolComputationGraph | None = None,
  ) -> FailureDetectionResult:
    """Synchronous version of detect."""
    return asyncio.run(self.detect(protocol_func, parameter_types, graph))

  def _extract_resources(self, parameter_types: dict[str, str]) -> list[str]:
    """Extract resource names from parameter types."""
    from praxis.common.type_inspection import extract_resource_types

    resources = []
    for name, type_hint in parameter_types.items():
      if extract_resource_types(type_hint):
        resources.append(name)
    return resources

  def _state_key(self, state: SimulationState) -> str:
    """Generate a hashable key for a state.

    Used for pruning - states with the same key will behave
    identically up to the first operation.
    """
    parts = [
      f"tips={state.tip_state.tips_loaded}",
      f"count={state.tip_state.tips_count}",
    ]

    if isinstance(state.liquid_state, BooleanLiquidState):
      for resource, has_liquid in sorted(state.liquid_state.has_liquid.items()):
        parts.append(f"{resource}:liq={has_liquid}")

    return "|".join(parts)

  def _state_to_dict(self, state: SimulationState) -> dict[str, Any]:
    """Convert state to a dictionary for reporting."""
    result: dict[str, Any] = {
      "tips_loaded": state.tip_state.tips_loaded,
      "tips_count": state.tip_state.tips_count,
      "level": state.level.value,
    }

    if isinstance(state.liquid_state, BooleanLiquidState):
      result["liquid"] = dict(state.liquid_state.has_liquid)
      result["capacity"] = dict(state.liquid_state.has_capacity)

    result["on_deck"] = dict(state.deck_state.on_deck)

    return result

  def _add_pruned_state(
    self,
    state: SimulationState,
    violation: dict[str, Any],
    pruned_states: set[str],
  ) -> None:
    """Add state signature to pruned set.

    If a state fails at operation N, any state that:
    1. Has the same relevant state components
    2. Doesn't have any operations before N that would change those components

    ...will also fail. We can skip simulating those states.
    """
    # For now, use simple state key pruning
    # A more sophisticated implementation would track which state
    # components are relevant to the failure
    state_key = self._state_key(state)
    pruned_states.add(state_key)


# =============================================================================
# Convenience Functions
# =============================================================================


async def detect_failure_modes(
  protocol_func: Callable[..., Any],
  parameter_types: dict[str, str],
  max_states: int = 100,
) -> FailureDetectionResult:
  """Detect failure modes for a protocol.

  This is a convenience function that creates a FailureModeDetector
  and runs detection.

  Args:
      protocol_func: The protocol function to analyze.
      parameter_types: Parameter type mapping.
      max_states: Maximum states to explore.

  Returns:
      FailureDetectionResult with all detected failure modes.

  """
  detector = FailureModeDetector(max_states=max_states)
  return await detector.detect(protocol_func, parameter_types)


def summarize_failure_modes(result: FailureDetectionResult) -> str:
  """Generate a human-readable summary of failure modes.

  Args:
      result: The detection result.

  Returns:
      Formatted summary string.

  """
  if not result.failure_modes:
    return "No failure modes detected."

  lines = [
    f"Detected {len(result.failure_modes)} failure mode(s):",
    f"  States explored: {result.states_explored}",
    f"  States pruned: {result.states_pruned}",
    f"  Coverage: {result.coverage:.1f}%",
    "",
  ]

  for i, mode in enumerate(result.failure_modes, 1):
    lines.append(f"{i}. {mode.failure_type}")
    lines.append(f"   Message: {mode.message}")
    if mode.suggested_fix:
      lines.append(f"   Fix: {mode.suggested_fix}")
    lines.append(f"   At: {mode.failure_point}")
    lines.append("")

  return "\n".join(lines)
