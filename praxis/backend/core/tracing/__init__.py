"""Protocol tracing infrastructure for runtime analysis.

This package provides tracer objects for symbolically executing protocols
to extract computation graphs, handling loops and conditionals that cannot
be fully analyzed statically.
"""

from praxis.backend.core.tracing.executor import ProtocolTracingExecutor
from praxis.backend.core.tracing.recorder import OperationRecorder
from praxis.backend.core.tracing.tracers import (
  TracedMachine,
  TracedResource,
  TracedValue,
  TracedWell,
  TracedWellCollection,
)

__all__ = [
  "OperationRecorder",
  "ProtocolTracingExecutor",
  "TracedMachine",
  "TracedResource",
  "TracedValue",
  "TracedWell",
  "TracedWellCollection",
]
