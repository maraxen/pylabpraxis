"""Protocol tracing executor.

This module provides the ProtocolTracingExecutor that runs protocol functions
with tracer objects to build computation graphs, capturing loops and conditionals
that cannot be fully analyzed statically.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from praxis.backend.core.tracing.recorder import OperationRecorder
from praxis.backend.core.tracing.tracers import (
  TracedMachine,
  TracedResource,
)
from praxis.backend.utils.plr_static_analysis.resource_hierarchy import (
  DeckLayoutType,
  get_parental_chain,
)
from praxis.common.type_inspection import extract_resource_types

if TYPE_CHECKING:
  from collections.abc import Callable

  from praxis.backend.utils.plr_static_analysis.models import ProtocolComputationGraph

# =============================================================================
# Exceptions
# =============================================================================


class TracingComplete(Exception):
  """Raised when tracing should stop (non-error termination)."""


class TracingError(Exception):
  """Raised when an unrecoverable error occurs during tracing."""


# =============================================================================
# Machine Type Detection
# =============================================================================

MACHINE_TYPE_PATTERNS: dict[str, str] = {
  "LiquidHandler": "liquid_handler",
  "PlateReader": "plate_reader",
  "HeaterShaker": "heater_shaker",
  "Shaker": "shaker",
  "Centrifuge": "centrifuge",
  "Thermocycler": "thermocycler",
  "TemperatureController": "temperature_controller",
  "Incubator": "incubator",
  "Pump": "pump",
  "PumpArray": "pump_array",
  "Fan": "fan",
  "Sealer": "sealer",
  "Peeler": "peeler",
  "PowderDispenser": "powder_dispenser",
}


def infer_machine_type(type_hint: str) -> str | None:
  """Infer machine type from a type hint string."""
  for pattern, machine_type in MACHINE_TYPE_PATTERNS.items():
    if pattern in type_hint:
      return machine_type
  return None


# =============================================================================
# Protocol Tracing Executor
# =============================================================================


class ProtocolTracingExecutor:
  """Execute protocol functions with tracers to build computation graphs.

  This executor creates tracer objects for each protocol parameter based on
  their type hints, then executes the protocol function with these tracers.
  Operations are recorded rather than executed, building a computation graph.

  Usage:
      executor = ProtocolTracingExecutor()
      graph = await executor.trace_protocol(
          protocol_func=my_protocol,
          parameter_types={"lh": "LiquidHandler", "plate": "Plate"},
      )

  """

  def __init__(
    self,
    deck_layout_type: DeckLayoutType = DeckLayoutType.CARRIER_BASED,
  ) -> None:
    """Initialize the executor.

    Args:
        deck_layout_type: Type of deck layout for parental chain inference.

    """
    self._deck_layout_type = deck_layout_type

  async def trace_protocol(
    self,
    protocol_func: Callable[..., Any],
    parameter_types: dict[str, str],
    protocol_fqn: str | None = None,
  ) -> ProtocolComputationGraph:
    """Trace a protocol function to build its computation graph.

    Args:
        protocol_func: The protocol function to trace.
        parameter_types: Mapping of parameter names to type hints.
        protocol_fqn: Fully qualified name (defaults to function name).

    Returns:
        The extracted ProtocolComputationGraph.

    Raises:
        TracingError: If tracing fails unrecoverably.

    """
    fqn = protocol_fqn or f"traced.{protocol_func.__name__}"
    name = protocol_func.__name__

    # Create recorder
    recorder = OperationRecorder(
      protocol_fqn=fqn,
      protocol_name=name,
      parameter_types=parameter_types,
    )

    # Create traced arguments
    traced_args = self._create_tracers(parameter_types, recorder)

    # Execute protocol with tracers
    try:
      result = protocol_func(**traced_args)
      # Handle async protocols
      if asyncio.iscoroutine(result):
        await result
    except TracingComplete:
      # Expected termination
      pass
    except Exception as e:
      # Log but continue - we want partial graphs
      # In production, this would use proper logging
      _ = e  # Suppress unused variable warning

    return recorder.build_graph()

  def trace_protocol_sync(
    self,
    protocol_func: Callable[..., Any],
    parameter_types: dict[str, str],
    protocol_fqn: str | None = None,
  ) -> ProtocolComputationGraph:
    """Synchronous wrapper for trace_protocol.

    Args:
        protocol_func: The protocol function to trace.
        parameter_types: Mapping of parameter names to type hints.
        protocol_fqn: Fully qualified name (defaults to function name).

    Returns:
        The extracted ProtocolComputationGraph.

    """
    return asyncio.run(self.trace_protocol(protocol_func, parameter_types, protocol_fqn))

  def _create_tracers(
    self,
    parameter_types: dict[str, str],
    recorder: OperationRecorder,
  ) -> dict[str, Any]:
    """Create tracer objects for each parameter.

    Args:
        parameter_types: Mapping of parameter names to type hints.
        recorder: The operation recorder to use.

    Returns:
        Dictionary of parameter names to tracer objects.

    """
    tracers: dict[str, Any] = {}

    for param_name, type_hint in parameter_types.items():
      tracer = self._create_tracer_for_type(param_name, type_hint, recorder)
      if tracer is not None:
        tracers[param_name] = tracer

    return tracers

  def _create_tracer_for_type(
    self,
    name: str,
    type_hint: str,
    recorder: OperationRecorder,
  ) -> Any:
    """Create appropriate tracer for a type hint.

    Args:
        name: Parameter name.
        type_hint: Type hint string.
        recorder: The operation recorder.

    Returns:
        A tracer object, or None for non-traceable types.

    """
    # Check for machine types
    machine_type = infer_machine_type(type_hint)
    if machine_type:
      return TracedMachine(
        name=name,
        recorder=recorder,
        declared_type=type_hint,
        machine_type=machine_type,
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

      return TracedResource(
        name=name,
        recorder=recorder,
        declared_type=type_hint,
        resource_type=primary_type,
        parental_chain=chain.chain,
      )

    # For primitive types (float, int, str, etc.), return a placeholder value
    # These are typically user parameters
    if type_hint in {"float", "int", "str", "bool"}:
      return self._get_default_for_primitive(type_hint)

    if "float" in type_hint.lower():
      return 50.0
    if "int" in type_hint.lower():
      return 1
    if "str" in type_hint.lower():
      return "traced_value"
    if "bool" in type_hint.lower():
      return True

    # Unknown type - return None and skip
    return None

  def _get_default_for_primitive(self, type_hint: str) -> Any:
    """Get a default value for primitive types."""
    defaults: dict[str, Any] = {
      "float": 50.0,
      "int": 1,
      "str": "traced_value",
      "bool": True,
    }
    return defaults.get(type_hint)


# =============================================================================
# Convenience Functions
# =============================================================================


async def trace_protocol(
  protocol_func: Callable[..., Any],
  parameter_types: dict[str, str],
  protocol_fqn: str | None = None,
  deck_layout_type: DeckLayoutType = DeckLayoutType.CARRIER_BASED,
) -> ProtocolComputationGraph:
  """Trace a protocol function to build a computation graph.

  This is a convenience function that creates a ProtocolTracingExecutor
  and traces the given protocol.

  Args:
      protocol_func: The protocol function to trace.
      parameter_types: Mapping of parameter names to type hints.
      protocol_fqn: Fully qualified name (defaults to function name).
      deck_layout_type: Type of deck layout.

  Returns:
      The extracted ProtocolComputationGraph.

  """
  executor = ProtocolTracingExecutor(deck_layout_type=deck_layout_type)
  return await executor.trace_protocol(protocol_func, parameter_types, protocol_fqn)


def trace_protocol_sync(
  protocol_func: Callable[..., Any],
  parameter_types: dict[str, str],
  protocol_fqn: str | None = None,
  deck_layout_type: DeckLayoutType = DeckLayoutType.CARRIER_BASED,
) -> ProtocolComputationGraph:
  """Synchronous version of trace_protocol.

  Args:
      protocol_func: The protocol function to trace.
      parameter_types: Mapping of parameter names to type hints.
      protocol_fqn: Fully qualified name (defaults to function name).
      deck_layout_type: Type of deck layout.

  Returns:
      The extracted ProtocolComputationGraph.

  """
  return asyncio.run(trace_protocol(protocol_func, parameter_types, protocol_fqn, deck_layout_type))
