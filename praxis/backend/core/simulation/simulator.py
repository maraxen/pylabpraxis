"""Protocol Simulator facade.

This module provides a high-level API for protocol simulation,
combining hierarchical state simulation and failure mode detection.
This is the main entry point for protocol discovery integration.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from praxis.backend.core.simulation.failure_detector import (
  FailureDetectionResult,
  FailureMode,
  FailureModeDetector,
)
from praxis.backend.core.simulation.pipeline import (
  HierarchicalSimulator,
  InferredRequirement,
)
from praxis.backend.utils.plr_static_analysis.resource_hierarchy import DeckLayoutType

if TYPE_CHECKING:
  from collections.abc import Callable

  from praxis.backend.utils.plr_static_analysis.models import ProtocolComputationGraph

# Version string for cache invalidation
# Bump this when simulation logic changes
SIMULATION_VERSION = "1.0.0"


# =============================================================================
# Result Models
# =============================================================================


class ProtocolSimulationResult(BaseModel):
  """Complete simulation result for a protocol.

  This model is designed to be cached with the protocol definition.
  """

  # Simulation outcome
  passed: bool = Field(default=False, description="Whether protocol passed all validation")

  # Hierarchical simulation results
  level_completed: str = Field(default="none", description="Highest level completed")
  level_failed: str | None = Field(default=None, description="Level where failure occurred")
  structural_error: str | None = Field(default=None, description="Structural error if any")

  # Violations found
  violations: list[dict[str, Any]] = Field(
    default_factory=list, description="All violations from simulation"
  )

  # Inferred requirements
  inferred_requirements: list[InferredRequirement] = Field(
    default_factory=list, description="Requirements inferred from simulation"
  )

  # Failure modes
  failure_modes: list[FailureMode] = Field(
    default_factory=list, description="Enumerated failure modes"
  )

  # Detection statistics
  failure_mode_stats: dict[str, Any] = Field(
    default_factory=dict, description="Failure detection statistics"
  )

  # Metadata
  simulation_version: str = Field(default=SIMULATION_VERSION)
  simulated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
  execution_time_ms: float = Field(default=0.0)

  def to_cache_dict(self) -> dict[str, Any]:
    """Convert to dictionary for database caching."""
    return self.model_dump(mode="json")

  @classmethod
  def from_cache_dict(cls, data: dict[str, Any]) -> ProtocolSimulationResult:
    """Reconstruct from cached dictionary."""
    return cls.model_validate(data)


# =============================================================================
# Protocol Simulator
# =============================================================================


class ProtocolSimulator:
  """High-level facade for protocol simulation.

  Combines hierarchical simulation and failure mode detection into
  a single interface suitable for protocol discovery integration.

  Usage:
      simulator = ProtocolSimulator()
      result = await simulator.analyze_protocol(
          protocol_func=my_protocol,
          parameter_types={"lh": "LiquidHandler", "plate": "Plate"},
      )

      # Check if protocol is valid
      if result.passed:
          print("Protocol validated successfully")
      else:
          for v in result.violations:
              print(f"Violation: {v['message']}")

      # Check failure modes
      for mode in result.failure_modes:
          print(f"Failure mode: {mode.message}")

  """

  def __init__(
    self,
    deck_layout_type: DeckLayoutType = DeckLayoutType.CARRIER_BASED,
    max_failure_states: int = 50,
    enable_failure_detection: bool = True,
  ) -> None:
    """Initialize the simulator.

    Args:
        deck_layout_type: Type of deck layout for resource hierarchy.
        max_failure_states: Maximum states to explore for failure detection.
        enable_failure_detection: Whether to run failure mode detection.

    """
    self._deck_layout_type = deck_layout_type
    self._max_failure_states = max_failure_states
    self._enable_failure_detection = enable_failure_detection
    self._simulator = HierarchicalSimulator(deck_layout_type=deck_layout_type)
    self._detector = FailureModeDetector(max_states=max_failure_states)

  async def analyze_protocol(
    self,
    protocol_func: Callable[..., Any],
    parameter_types: dict[str, str],
    graph: ProtocolComputationGraph | None = None,
  ) -> ProtocolSimulationResult:
    """Run full simulation analysis on a protocol.

    Performs:
    1. Hierarchical simulation (structural → boolean → symbolic → exact)
    2. Failure mode enumeration (if enabled)

    Args:
        protocol_func: The protocol function to analyze.
        parameter_types: Mapping of parameter names to type hints.
        graph: Optional pre-computed computation graph.

    Returns:
        ProtocolSimulationResult with all findings.

    """
    import time

    start_time = time.perf_counter()

    # Run hierarchical simulation
    sim_result = await self._simulator.simulate(
      protocol_func=protocol_func,
      parameter_types=parameter_types,
    )

    # Run failure mode detection if enabled
    failure_result: FailureDetectionResult | None = None
    if self._enable_failure_detection:
      failure_result = await self._detector.detect(
        protocol_func=protocol_func,
        parameter_types=parameter_types,
        graph=graph,
      )

    total_time = (time.perf_counter() - start_time) * 1000

    # Combine results
    return ProtocolSimulationResult(
      passed=sim_result.passed,
      level_completed=sim_result.level_completed,
      level_failed=sim_result.level_failed,
      structural_error=sim_result.structural_error,
      violations=sim_result.violations,
      inferred_requirements=sim_result.inferred_requirements,
      failure_modes=failure_result.failure_modes if failure_result else [],
      failure_mode_stats={
        "states_explored": failure_result.states_explored if failure_result else 0,
        "states_pruned": failure_result.states_pruned if failure_result else 0,
        "coverage": failure_result.coverage if failure_result else 0.0,
        "detection_time_ms": failure_result.detection_time_ms if failure_result else 0.0,
      },
      simulation_version=SIMULATION_VERSION,
      execution_time_ms=total_time,
    )

  def analyze_protocol_sync(
    self,
    protocol_func: Callable[..., Any],
    parameter_types: dict[str, str],
    graph: ProtocolComputationGraph | None = None,
  ) -> ProtocolSimulationResult:
    """Synchronous version of analyze_protocol."""
    return asyncio.run(
      self.analyze_protocol(
        protocol_func=protocol_func,
        parameter_types=parameter_types,
        graph=graph,
      )
    )


# =============================================================================
# Cache Validation
# =============================================================================


def is_cache_valid(
  cached_version: str | None,
  source_hash: str | None,
  current_source_hash: str | None,
) -> bool:
  """Check if cached simulation result is still valid.

  Args:
      cached_version: Version string from cache.
      source_hash: Source hash from cache.
      current_source_hash: Current source hash.

  Returns:
      True if cache is valid and can be used.

  """
  # Version must match
  if cached_version != SIMULATION_VERSION:
    return False

  # Source hash must match (if available)
  if source_hash is not None and current_source_hash is not None:
    if source_hash != current_source_hash:
      return False

  return True


# =============================================================================
# Convenience Functions
# =============================================================================


async def analyze_protocol(
  protocol_func: Callable[..., Any],
  parameter_types: dict[str, str],
  deck_layout_type: DeckLayoutType = DeckLayoutType.CARRIER_BASED,
  enable_failure_detection: bool = True,
) -> ProtocolSimulationResult:
  """Analyze a protocol with full simulation.

  Convenience function that creates a ProtocolSimulator and runs analysis.

  Args:
      protocol_func: The protocol function to analyze.
      parameter_types: Mapping of parameter names to type hints.
      deck_layout_type: Type of deck layout.
      enable_failure_detection: Whether to run failure detection.

  Returns:
      ProtocolSimulationResult with all findings.

  """
  simulator = ProtocolSimulator(
    deck_layout_type=deck_layout_type,
    enable_failure_detection=enable_failure_detection,
  )
  return await simulator.analyze_protocol(
    protocol_func=protocol_func,
    parameter_types=parameter_types,
  )


def analyze_protocol_sync(
  protocol_func: Callable[..., Any],
  parameter_types: dict[str, str],
  deck_layout_type: DeckLayoutType = DeckLayoutType.CARRIER_BASED,
  enable_failure_detection: bool = True,
) -> ProtocolSimulationResult:
  """Synchronous version of analyze_protocol."""
  return asyncio.run(
    analyze_protocol(
      protocol_func=protocol_func,
      parameter_types=parameter_types,
      deck_layout_type=deck_layout_type,
      enable_failure_detection=enable_failure_detection,
    )
  )
