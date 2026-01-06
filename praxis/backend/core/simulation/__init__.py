"""Protocol state simulation infrastructure.

This package provides hierarchical state simulation for protocols,
enabling automatic inference of state requirements (tips, liquid, deck placement)
and detection of failure modes at protocol discovery time.

The simulation builds on the tracing infrastructure to:
1. Define method contracts (preconditions and effects)
2. Track state through protocol execution
3. Detect failures at multiple precision levels (boolean → symbolic → exact)
4. Enumerate possible failure modes with early pruning

Modules:
- method_contracts: PLR method semantics (preconditions, effects)
- state_models: Hierarchical state representations
- stateful_tracers: State-aware protocol tracers
- pipeline: Multi-level simulation orchestration
- bounds_analyzer: Loop iteration analysis
- failure_detector: Failure mode enumeration
"""

from praxis.backend.core.simulation.bounds_analyzer import (
  BoundsAnalyzer,
  ItemizedResourceSpec,
  LoopBounds,
  compute_aggregate_effect,
)
from praxis.backend.core.simulation.failure_detector import (
  FailureDetectionResult,
  FailureMode,
  FailureModeDetector,
  detect_failure_modes,
  summarize_failure_modes,
)
from praxis.backend.core.simulation.graph_replay import (
  GraphReplayEngine,
  GraphReplayResult,
  ReplayState,
  ReplayViolation,
  replay_graph,
)
from praxis.backend.core.simulation.method_contracts import (
  METHOD_CONTRACTS,
  MethodContract,
  get_contract,
  get_contracts_for_type,
)
from praxis.backend.core.simulation.pipeline import (
  HierarchicalSimulationResult,
  HierarchicalSimulator,
  InferredRequirement,
  simulate_protocol,
  simulate_protocol_sync,
)
from praxis.backend.core.simulation.simulator import (
  SIMULATION_VERSION,
  ProtocolSimulationResult,
  ProtocolSimulator,
  analyze_protocol,
  analyze_protocol_sync,
  is_cache_valid,
)
from praxis.backend.core.simulation.state_models import (
  BooleanLiquidState,
  DeckState,
  ExactLiquidState,
  MachineState,
  SimulationState,
  StateLevel,
  StateViolation,
  SymbolicLiquidState,
  SymbolicVolume,
  TipState,
  ViolationType,
)
from praxis.backend.core.simulation.state_resolution import (
  OperationRecord,
  ResolutionType,
  StatePropertyType,
  StateResolution,
  UncertainStateChange,
  apply_resolution,
  identify_uncertain_states,
)
from praxis.backend.core.simulation.stateful_tracers import (
  StatefulTracedMachine,
  StatefulTracedResource,
  StatefulTracedWell,
  StatefulTracedWellCollection,
)

__all__ = [
  # Method contracts
  "METHOD_CONTRACTS",
  "MethodContract",
  "get_contract",
  "get_contracts_for_type",
  # State models
  "BooleanLiquidState",
  "DeckState",
  "ExactLiquidState",
  "MachineState",
  "SimulationState",
  "StateLevel",
  "StateViolation",
  "SymbolicLiquidState",
  "SymbolicVolume",
  "TipState",
  "ViolationType",
  # Stateful tracers
  "StatefulTracedMachine",
  "StatefulTracedResource",
  "StatefulTracedWell",
  "StatefulTracedWellCollection",
  # Pipeline
  "HierarchicalSimulationResult",
  "HierarchicalSimulator",
  "InferredRequirement",
  "simulate_protocol",
  "simulate_protocol_sync",
  # Bounds analyzer
  "BoundsAnalyzer",
  "ItemizedResourceSpec",
  "LoopBounds",
  "compute_aggregate_effect",
  # Failure detector
  "FailureDetectionResult",
  "FailureMode",
  "FailureModeDetector",
  "detect_failure_modes",
  "summarize_failure_modes",
  # Simulator facade
  "SIMULATION_VERSION",
  "ProtocolSimulationResult",
  "ProtocolSimulator",
  "analyze_protocol",
  "analyze_protocol_sync",
  "is_cache_valid",
  # Graph replay (browser-compatible)
  "GraphReplayEngine",
  "GraphReplayResult",
  "ReplayState",
  "ReplayViolation",
  "replay_graph",
  # State resolution
  "OperationRecord",
  "ResolutionType",
  "StatePropertyType",
  "StateResolution",
  "UncertainStateChange",
  "apply_resolution",
  "identify_uncertain_states",
]
