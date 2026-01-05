# Hierarchical Protocol State Simulation

**Priority**: P2 (High)
**Owner**: Backend
**Created**: 2026-01-04
**Status**: ✅ Implemented (2026-01-05)

---

## Overview

Given a protocol function like:

```python
async def simple_transfer(lh: LiquidHandler, target_plate: Plate, dest_plate: Plate):
    await lh.transfer_96(target_plate, dest_plate)
```

The system must infer:
1. **Deck state requirements**: `target_plate` and `dest_plate` must be on `lh.deck`
2. **Tip requirements**: 96 tips must be available
3. **Source state**: `target_plate` wells must have liquid
4. **Destination state**: `dest_plate` wells must have capacity

The simulation runs at **protocol discovery/sync time** (not runtime) and uses a **hierarchical validation approach** for tractability.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  Protocol Discovery/Sync Time                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  LEVEL 0: Tracer Execution (State-Independent)                  │
│  ─────────────────────────────────────────────                  │
│  • Uses existing TracedMachine/TracedResource infrastructure    │
│  • Catches: wrong methods, bad signatures, structural errors    │
│  • If fails here → fails regardless of state                    │
│                                                                  │
│  LEVEL 1-3: Hierarchical State Simulation (State-Dependent)     │
│  ─────────────────────────────────────────────────────────────  │
│  • Level 1: Boolean State (has_liquid: bool, tips_loaded: bool) │
│  • Level 2: Symbolic Volumes (v1, v2 with constraints)          │
│  • Level 3: Exact Volumes (binary search for edge cases)        │
│                                                                  │
│  FAILURE MODE ENUMERATION                                       │
│  ─────────────────────────────────────────────────────────────  │
│  • Generate candidate initial states                            │
│  • Early pruning: if op N fails with state S, skip states       │
│    that match S and don't change before N                       │
│                                                                  │
│  CACHE: Results stored with protocol definition                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Runtime (Deck Setup)                          │
├─────────────────────────────────────────────────────────────────┤
│  1. Load Cached Requirements                                    │
│  2. Validate Against Provided Deck State                        │
│  3. Report Unmet Requirements                                   │
│  4. Suggest Fixes                                               │
└─────────────────────────────────────────────────────────────────┘
```

### Existing Infrastructure (To Be Used)

The following tracer classes already exist in `praxis/backend/core/tracing/`:

| Class | File | Purpose |
|-------|------|---------|
| `TracedValue` | `tracers.py` | Base class for all tracers |
| `TracedWell` | `tracers.py` | Single well/tipspot tracer |
| `TracedWellCollection` | `tracers.py` | Collection of wells tracer |
| `TracedResource` | `tracers.py` | PLR resource tracer |
| `TracedMachine` | `tracers.py` | Machine with method recording |
| `OperationRecorder` | `recorder.py` | Collects operations into graph |
| `ProtocolTracingExecutor` | `executor.py` | Runs protocol with tracers |

---

## Phase 0: Tracer Execution (State-Independent Validation)

Use the existing tracer infrastructure to catch structural errors that fail regardless of state.

### Purpose

Run the protocol with `TracedMachine`/`TracedResource` objects to detect:
- Methods that don't exist on the machine type
- Wrong argument counts or types
- Missing required parameters
- Structural issues in control flow

If a protocol fails at this level, it will **always fail** - no state configuration can save it.

### Integration with Existing Infrastructure

```python
from praxis.backend.core.tracing.executor import ProtocolTracingExecutor

async def validate_protocol_structure(
    protocol_func: Callable,
    parameter_types: dict[str, str],
) -> TracerValidationResult:
    """Level 0: Structural validation using existing tracers."""

    executor = ProtocolTracingExecutor()

    try:
        graph = await executor.trace_protocol(
            protocol_func=protocol_func,
            parameter_types=parameter_types,
        )
        return TracerValidationResult(
            passed=True,
            computation_graph=graph,
        )
    except TracingError as e:
        return TracerValidationResult(
            passed=False,
            error=str(e),
            error_type="structural",
        )
    except AttributeError as e:
        # Method doesn't exist
        return TracerValidationResult(
            passed=False,
            error=f"Unknown method: {e}",
            error_type="unknown_method",
        )
```

### Enhancements to Existing Tracers

The existing `TracedMachine` proxies method calls but may not validate signatures. Enhance to:

- [ ] **Validate method existence** - Check if method is known for machine type
- [ ] **Validate argument count** - Check positional/keyword arg counts
- [ ] **Record method contracts** - Link to Phase 1 contracts for state simulation
- [ ] **Better error messages** - Include line numbers and context

### Tasks

- [ ] Add method validation to `TracedMachine.__getattr__`
- [ ] Create `TracerValidationResult` model
- [ ] Integrate tracer execution as first pass in simulation pipeline
- [ ] Add tests for structural error detection
- [ ] Ensure graceful handling of async protocol execution

### Files to Modify

- `praxis/backend/core/tracing/tracers.py` - Enhance validation
- `praxis/backend/core/tracing/executor.py` - Validation wrapper

---

## Phase 1: PLR Method Semantics Database

Create a comprehensive database of PLR method contracts capturing requirements and effects.

### Method Contract Model

```python
@dataclass
class MethodContract:
    """Contract for a PLR method."""
    method_name: str
    receiver_type: str  # "LiquidHandler", "PlateReader", etc.

    # === Preconditions (state that must be true before) ===

    # Tip requirements
    requires_tips: bool = False
    requires_tips_count: int | None = None  # e.g., 96 for transfer_96

    # Deck placement
    requires_on_deck: list[str] = field(default_factory=list)  # arg names

    # Liquid state
    requires_liquid_in: str | None = None  # arg name that must have liquid
    requires_capacity_in: str | None = None  # arg name that must have capacity
    requires_volume_min: float | None = None  # minimum volume required

    # Machine state
    requires_machine_ready: bool = True
    requires_temperature: tuple[float, float] | None = None  # (min, max)

    # === Effects (state changes after execution) ===

    # Tip state changes
    loads_tips: bool = False
    loads_tips_count: int | None = None
    drops_tips: bool = False

    # Liquid transfers
    aspirates_from: str | None = None  # arg name
    aspirate_volume_arg: str | None = None  # which arg specifies volume
    dispenses_to: str | None = None  # arg name
    dispense_volume_arg: str | None = None
    transfers: tuple[str, str] | None = None  # (source_arg, dest_arg)

    # Other effects
    moves_resource: tuple[str, str] | None = None  # (resource_arg, dest_arg)
```

### LiquidHandler Methods to Model

| Method | Tips Required | Liquid Req | Effects |
|--------|--------------|------------|---------|
| `pick_up_tips(tips)` | No | No | loads_tips |
| `pick_up_tips96(tips)` | No | No | loads_tips(96) |
| `drop_tips(tips)` | Yes | No | drops_tips |
| `aspirate(resource, vol)` | Yes | resource has liquid | removes liquid from resource |
| `dispense(resource, vol)` | Yes | resource has capacity | adds liquid to resource |
| `transfer(src, dest, vol)` | Yes | src has liquid, dest has capacity | moves liquid src→dest |
| `transfer_96(src, dest)` | Yes(96) | src wells have liquid | moves liquid src→dest |
| `mix(resource, vol, n)` | Yes | resource has liquid | no net transfer |
| `blow_out(resource)` | Yes | No | clears remaining liquid |

### Tasks

- [ ] Create `MethodContract` dataclass
- [ ] Create `METHOD_CONTRACTS: dict[str, MethodContract]` registry
- [ ] Model all LiquidHandler methods
- [ ] Model PlateReader methods (read_absorbance, etc.)
- [ ] Model HeaterShaker methods (set_temperature, shake, etc.)
- [ ] Model transport methods (move_plate, get_plate, put_plate)
- [ ] Unit tests for contract lookup

### Files to Create

- `praxis/backend/core/simulation/method_contracts.py`

---

## Phase 2: State-Aware Tracers

Extend the existing tracer infrastructure to carry and validate state during execution.

### Key Insight

Rather than a separate executor that walks the computation graph, we **re-run the protocol with state-aware tracers**:

1. Same execution path as Level 0
2. Tracers carry state (tips, liquid, deck placement)
3. Before each operation, check preconditions against state
4. After each operation, apply effects to state
5. Collect violations as we go

### Enhanced Tracer Classes

```python
@dataclass
class StatefulTracedMachine(TracedMachine):
    """Machine tracer that tracks and validates state."""

    state: SimulationState = field(default_factory=SimulationState)
    """Current simulation state"""

    contracts: dict[str, MethodContract] = field(default_factory=dict)
    """Method contracts for precondition/effect checking"""

    violations: list[StateViolation] = field(default_factory=list)
    """Collected violations during execution"""

    def __getattr__(self, method_name: str) -> Callable:
        """Intercept method calls to check preconditions and apply effects."""

        def method_proxy(*args, **kwargs):
            contract = self.contracts.get(method_name)

            if contract:
                # Check preconditions
                violation = self._check_preconditions(method_name, contract, args, kwargs)
                if violation:
                    self.violations.append(violation)

                # Apply effects (even if violation, to continue simulation)
                self._apply_effects(method_name, contract, args, kwargs)

            # Still record the operation
            return self.recorder.record(self, method_name, args, kwargs)

        return method_proxy
```

### Hierarchical State Levels

The `SimulationState` supports three precision levels:

```python
class SimulationState:
    """State container that supports hierarchical precision levels."""

    level: Literal["boolean", "symbolic", "exact"]

    # Common state
    on_deck: dict[str, bool]
    tips_loaded: bool
    tips_count: int

    # Level-dependent liquid state
    liquid_state: BooleanLiquidState | SymbolicLiquidState | ExactLiquidState

    def promote(self) -> SimulationState:
        """Promote to next precision level."""
        if self.level == "boolean":
            return self._to_symbolic()
        elif self.level == "symbolic":
            return self._to_exact()
        return self
```

### State Level Implementations

```python
@dataclass
class BooleanLiquidState:
    """Fast: just has_liquid/has_capacity booleans."""
    has_liquid: dict[str, bool]  # "plate.A1" -> True/False
    has_capacity: dict[str, bool]

@dataclass
class SymbolicLiquidState:
    """Medium: symbolic volumes with constraints."""
    volumes: dict[str, str]  # "plate.A1" -> "v1" (symbol)
    constraints: list[str]  # ["v1 > 0", "v1 <= 200"]

@dataclass
class ExactLiquidState:
    """Precise: exact numeric volumes."""
    volumes: dict[str, float]  # "plate.A1" -> 150.0
```

### Tasks

- [ ] Create `StatefulTracedMachine` extending `TracedMachine`
- [ ] Create `SimulationState` with level support
- [ ] Create `BooleanLiquidState`, `SymbolicLiquidState`, `ExactLiquidState`
- [ ] Implement `_check_preconditions()` method
- [ ] Implement `_apply_effects()` method
- [ ] Implement state promotion (`boolean` → `symbolic` → `exact`)
- [ ] Unit tests for state-aware tracing

### Files to Create

- `praxis/backend/core/simulation/stateful_tracers.py`
- `praxis/backend/core/simulation/state_models.py`

---

## Phase 3: Hierarchical Simulation Pipeline

Orchestrate the multi-level simulation using state-aware tracers.

### Pipeline Design

```python
class HierarchicalSimulator:
    """Runs protocol with state-aware tracers at multiple precision levels."""

    def __init__(self, contracts: dict[str, MethodContract]):
        self.contracts = contracts

    async def simulate(
        self,
        protocol_func: Callable,
        parameter_types: dict[str, str],
        initial_state: SimulationState | None = None,
    ) -> HierarchicalSimulationResult:
        """Run hierarchical simulation with progressive refinement."""

        # Level 0: Structural validation (existing tracers)
        tracer_result = await self._run_structural_validation(
            protocol_func, parameter_types
        )
        if not tracer_result.passed:
            return HierarchicalSimulationResult(
                level_failed="structural",
                error=tracer_result.error,
            )

        # Level 1: Boolean state pass
        bool_state = initial_state or SimulationState.default_boolean()
        bool_result = await self._run_with_state(
            protocol_func, parameter_types, bool_state
        )
        if bool_result.violations:
            return HierarchicalSimulationResult(
                level_failed="boolean",
                violations=bool_result.violations,
            )

        # Level 2: Symbolic state pass (only if boolean passed)
        sym_state = bool_state.promote()  # boolean → symbolic
        sym_result = await self._run_with_state(
            protocol_func, parameter_types, sym_state
        )
        if not sym_result.constraints_satisfiable():
            return HierarchicalSimulationResult(
                level_failed="symbolic",
                unsatisfiable_constraints=sym_result.conflicts,
            )

        # Level 3: Exact pass with binary search for edge cases
        edge_cases = sym_result.find_edge_cases()
        for case in edge_cases:
            exact_state = sym_state.promote_with_values(case)
            exact_result = await self._run_with_state(
                protocol_func, parameter_types, exact_state
            )
            if exact_result.violations:
                return HierarchicalSimulationResult(
                    level_failed="exact",
                    edge_case=case,
                    violations=exact_result.violations,
                )

        return HierarchicalSimulationResult(
            passed=True,
            inferred_requirements=self._collect_requirements(sym_result),
            computation_graph=tracer_result.computation_graph,
        )

    async def _run_with_state(
        self,
        protocol_func: Callable,
        parameter_types: dict[str, str],
        state: SimulationState,
    ) -> StatefulSimulationResult:
        """Run protocol with state-aware tracers."""

        # Create stateful tracers
        tracers = self._create_stateful_tracers(parameter_types, state)

        # Execute protocol
        try:
            await protocol_func(**tracers)
        except Exception as e:
            # Collect any violations before exception
            pass

        # Collect results from tracers
        return StatefulSimulationResult(
            final_state=self._collect_final_state(tracers),
            violations=self._collect_violations(tracers),
            constraints=self._collect_constraints(tracers),
        )
```

### Tasks

- [ ] Create `HierarchicalSimulator` class
- [ ] Implement `_run_structural_validation()` using existing executor
- [ ] Implement `_run_with_state()` using `StatefulTracedMachine`
- [ ] Implement `_create_stateful_tracers()` factory
- [ ] Implement edge case detection from symbolic constraints
- [ ] Implement `_collect_requirements()` for final inference
- [ ] Unit tests for each simulation level

### Files to Create

- `praxis/backend/core/simulation/pipeline.py`

---

## Phase 4: Bounds Analyzer for Loops

Compute exact iteration counts using `items_x` and `items_y`.

### Design

```python
class BoundsAnalyzer:
    """Analyzes loop bounds using resource dimensions."""

    def analyze_loop(
        self,
        loop_node: OperationNode,
        graph: ProtocolComputationGraph,
        resource_specs: dict[str, ItemizedResourceSpec],
    ) -> LoopBounds:
        """Determine loop iteration count."""

        # e.g., "for well in plate.wells()"
        source_var = loop_node.foreach_source  # "plate"

        if source_var in resource_specs:
            spec = resource_specs[source_var]
            iteration_count = spec.items_x * spec.items_y
            return LoopBounds(
                exact_count=iteration_count,
                source=f"{source_var}.wells()",
            )

        # Unknown bounds - use conservative estimate
        return LoopBounds(
            min_count=1,
            max_count=None,  # Unknown
            is_bounded=False,
        )
```

### Integration with Executor

When the executor encounters a `foreach` node:
1. Query `BoundsAnalyzer` for iteration count
2. If exact count known, unroll symbolically or compute aggregate effect
3. If unknown, use conservative merge (assume all items affected)

### Tasks

- [ ] Create `BoundsAnalyzer` class
- [ ] Implement loop bounds inference from `items_x * items_y`
- [ ] Handle nested loops
- [ ] Handle conditional loops (`while` with condition)
- [ ] Integrate with `SymbolicExecutor`
- [ ] Unit tests

### Files to Create

- `praxis/backend/core/simulation/bounds_analyzer.py`

---

## Phase 5: Failure Mode Detector

Enumerate possible failure states with hierarchical pruning.

### Failure Mode Enumeration

```python
class FailureModeDetector:
    """Detects possible failure modes by exploring state space."""

    def detect_failures(
        self,
        graph: ProtocolComputationGraph,
    ) -> list[FailureMode]:
        """Enumerate failure modes with early pruning."""

        # Generate candidate initial states
        candidates = self._generate_candidate_states(graph)

        failures = []
        pruned_states = set()  # States proven to fail early

        for state in candidates:
            # Skip if we know this state fails from earlier analysis
            if self._is_pruned(state, pruned_states):
                continue

            result = simulate_hierarchical(graph, state)

            if not result.passed:
                failures.append(FailureMode(
                    initial_state=state,
                    failure_point=result.failure_point,
                    violation=result.violation,
                    suggested_fix=self._suggest_fix(result),
                ))

                # Add to pruned states for future candidates
                self._add_pruned_state(state, result.failure_point, pruned_states)

        return failures

    def _generate_candidate_states(
        self,
        graph: ProtocolComputationGraph,
    ) -> Iterator[BooleanState]:
        """Generate candidate initial states to test."""

        # Resources that might or might not be on deck
        resources = list(graph.resources.keys())

        # Generate combinations (with smart pruning)
        for placement_combo in self._placement_combinations(resources):
            for tip_state in [True, False]:
                for liquid_config in self._liquid_configurations(graph):
                    yield BooleanState(
                        on_deck=placement_combo,
                        tips_loaded=tip_state,
                        has_liquid=liquid_config,
                        ...
                    )
```

### Early Pruning Strategy

If operation N fails with state S, and S doesn't change between operations 1 and N, then:
- Any state that matches S at operation 1 will also fail
- Don't need to re-simulate those states

```python
def _is_pruned(self, state: BooleanState, pruned: set) -> bool:
    """Check if state is known to fail from earlier analysis."""
    # Hash the relevant state components
    state_key = self._state_key(state)
    return state_key in pruned
```

### Tasks

- [ ] Create `FailureModeDetector` class
- [ ] Implement candidate state generation
- [ ] Implement early pruning based on failure propagation
- [ ] Implement fix suggestion generation
- [ ] Integration with hierarchical executor
- [ ] Unit tests

### Files to Create

- `praxis/backend/core/simulation/failure_detector.py`

---

## Phase 6: Integration & Caching

Hook into protocol discovery and cache results.

### Discovery Integration

```python
# In protocol_discovery.py

async def _discover_protocol(self, func_info: ProtocolFunctionInfo) -> ...:
    # ... existing discovery logic ...

    # Extract computation graph (existing)
    graph = self._extract_computation_graph(func_info)

    # NEW: Run simulation to infer requirements
    simulator = ProtocolSimulator()
    simulation_result = simulator.analyze_protocol(graph)

    # Cache with protocol
    func_info.simulation_result = simulation_result.model_dump()
    func_info.inferred_requirements = simulation_result.inferred_requirements
    func_info.failure_modes = simulation_result.failure_modes
```

### Database Schema Extension

```python
class FunctionProtocolDefinitionOrm(Base):
    # ... existing fields ...

    # Simulation results
    simulation_result_json: Mapped[dict | None] = mapped_column(
        JSON,
        comment="Cached simulation result",
    )
    inferred_requirements_json: Mapped[dict | None] = mapped_column(
        JSON,
        comment="Inferred state requirements",
    )
    failure_modes_json: Mapped[list | None] = mapped_column(
        JSON,
        comment="Known failure modes",
    )
    simulation_version: Mapped[str | None] = mapped_column(
        String(32),
        comment="Simulator version for cache invalidation",
    )
```

### UI Surfacing

In the deck setup wizard:
1. Load cached requirements
2. Validate current deck state against requirements
3. Show warnings for potential failure modes
4. Suggest fixes (add tips, place resources, etc.)

### Tasks

- [ ] Create `ProtocolSimulator` facade class
- [ ] Integrate with `ProtocolDiscoveryVisitor`
- [ ] Add database columns for caching
- [ ] Create Alembic migration
- [ ] Surface requirements in deck setup wizard
- [ ] Show failure mode warnings in UI
- [ ] Unit and integration tests

### Files to Create/Modify

- `praxis/backend/core/simulation/simulator.py` (facade)
- `praxis/backend/utils/plr_static_analysis/visitors/protocol_discovery.py` (modify)
- `praxis/backend/models/orm/protocol.py` (modify)
- `alembic/versions/xxx_add_simulation_cache.py`

---

## Performance Targets

| Operation | Target Time | Notes |
|-----------|-------------|-------|
| Boolean simulation | < 10ms | Per protocol |
| Symbolic simulation | < 50ms | Per protocol |
| Exact simulation | < 100ms | Per edge case |
| Full hierarchical | < 200ms | Total per protocol |
| Failure mode enum | < 1s | At discovery time |

---

## Success Criteria

1. [x] `transfer_96(source, dest)` correctly infers: tips(96), source on deck, dest on deck, source has liquid
2. [x] Loop iteration counts computed from `items_x * items_y`
3. [x] Hierarchical simulation catches errors at appropriate level
4. [x] Early pruning reduces state space exploration by 50%+
5. [ ] Simulation results cached and loaded correctly (Phase 6 - future)
6. [ ] UI shows meaningful requirements and failure modes (Phase 6 - future)
7. [x] Performance targets met

---

## Related Files

| File | Purpose |
|------|---------|
| `praxis/backend/core/precondition_resolver.py` | Existing resolver (will use simulation results) |
| `praxis/backend/utils/plr_static_analysis/models.py` | Graph models |
| `praxis/backend/utils/plr_static_analysis/visitors/computation_graph_extractor.py` | Graph extraction |
| `praxis/backend/utils/plr_static_analysis/resource_hierarchy.py` | Resource hierarchy |

### New Simulation Module Files (Implemented 2026-01-05)

| File | Purpose |
|------|---------|
| `praxis/backend/core/simulation/__init__.py` | Module exports |
| `praxis/backend/core/simulation/method_contracts.py` | PLR method contracts (preconditions/effects) |
| `praxis/backend/core/simulation/state_models.py` | Boolean/Symbolic/Exact state models |
| `praxis/backend/core/simulation/stateful_tracers.py` | State-aware tracers extending base tracers |
| `praxis/backend/core/simulation/pipeline.py` | HierarchicalSimulator orchestration |
| `praxis/backend/core/simulation/bounds_analyzer.py` | Loop bounds analysis |
| `praxis/backend/core/simulation/failure_detector.py` | Failure mode enumeration |
| `tests/core/test_simulation.py` | Comprehensive test suite (49 tests)

---

## References

- **Symbolic Execution**: Similar to techniques used in program analysis
- **Abstract Interpretation**: Boolean state is an abstraction of concrete state
- **Constraint Solving**: Symbolic volumes with constraints similar to SMT solving
- **Early Pruning**: Based on monotonicity of precondition failures
