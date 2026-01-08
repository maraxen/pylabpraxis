# Protocol Computation Graph & Parental Inference

**Created**: 2026-01-03
**Priority**: P2 - High (Core Feature Gap)
**Difficulty**: XL (3+ days, multi-phase)
**Status**: ✅ Complete

---

## Implementation Progress

### Completed (Phase 1: Static Analysis)

- [x] **Milestone 1**: Enhanced Type Inspection (`praxis/common/type_inspection.py`)
  - Added `extract_resource_types()` for `list[Well]`, `Sequence[TipSpot]`, etc.
  - Added `get_element_type()`, `is_container_type()` helpers
  - Added `PLR_RESOURCE_TYPES` constant with all PLR types
  - Tests: `tests/utils/test_type_inspection.py` (66 tests)

- [x] **Milestone 2**: Resource Hierarchy Registry (`praxis/backend/utils/plr_static_analysis/resource_hierarchy.py`)
  - `ResourceHierarchyRegistry` class with parental chain computation
  - Supports carrier-based (Hamilton) and slot-based (OT-2) decks
  - `DeckLayoutType` enum, `ResourceCategory` enum
  - Tests: `tests/utils/test_resource_hierarchy.py` (43 tests)

- [x] **Milestone 3**: Variable Type Tracking
  - `VariableTypeTracker` class for tracking types through assignments
  - Handles subscript (`plate["A1:A8"]` → `list[Well]`) and attribute access

- [x] **Milestone 4**: Computation Graph Extractor (`praxis/backend/utils/plr_static_analysis/visitors/computation_graph_extractor.py`)
  - `ComputationGraphExtractor` CST visitor
  - Extracts `OperationNode`, `ResourceNode`, `StatePrecondition`
  - Builds `ProtocolComputationGraph` with full operation/resource/precondition data
  - Tests: `tests/utils/test_computation_graph.py` (32 tests)

- [x] **Milestone 5**: Precondition Resolver (`praxis/backend/core/precondition_resolver.py`)
  - `PreconditionResolver` service
  - Resolves preconditions against deck state and available assets
  - Generates `DeckLayoutConfig` for unmet requirements
  - Tests: `tests/core/test_precondition_resolver.py` (18 tests)

- [x] **Canonical Test Protocols** (`tests/fixtures/protocols/`)
  - `simple_linear.py`, `loop_based.py`, `conditional.py`, `multi_machine.py`

### Completed (Phase 2: Integration & Tracers)

- [x] **Milestone 6**: Discovery Integration
  - Added `computation_graph_json`, `source_hash`, `graph_cached_at` to `FunctionProtocolDefinitionOrm`
  - Integrated graph extraction in `ProtocolDiscoveryVisitor._extract_computation_graph()`
  - Alembic migration: `e2f3a4b5c6d7_add_computation_graph_to_protocol_defs.py`

- [x] **Milestone 7**: Tracer Infrastructure (`praxis/backend/core/tracing/`)
  - `TracedValue`, `TracedResource`, `TracedWellCollection`, `TracedWell` classes
  - `TracedMachine` with method proxying for operation recording
  - `TracedComparison` for conditional tracking
  - Tests: `tests/core/test_tracers.py` (26 tests)

- [x] **Milestone 8**: Tracer Execution Engine
  - `OperationRecorder` collects operations into `ProtocolComputationGraph`
  - `ProtocolTracingExecutor` runs protocols with tracers
  - Handles async protocols, loop/conditional contexts

- [x] **Milestone 9**: Loop/Conditional Analysis
  - `TracedWellCollection.__iter__` yields symbolic elements for foreach patterns
  - `OperationRecorder.enter_loop()` / `exit_loop()` for loop context tracking
  - Conditional branch recording via `TracedComparison.__bool__`

---

## Problem Statement

When a protocol defines parameters like `source_wells: list[Well]` and calls `lh.transfer(source_wells, dest_wells)`, the system must infer:

1. **Resource Type Extraction**: `list[Well]` → element type is `Well`
2. **Parental Chain**: `Well` → `Plate` → `PlateCarrier` (or slot) → `Deck`
3. **Implicit State Requirements**: Transfer requires tips loaded → `TipRack` → `TipCarrier` → `Deck`
4. **Deck State Preconditions**: All required resources must be placed before execution
5. **Idempotency**: If preconditions are already satisfied, don't duplicate actions

---

## Current State (Gaps)

### 1. Container Type Inspection

**Location**: `praxis/common/type_inspection.py`

```python
# CURRENT: Only handles Union, not list/Sequence
def is_pylabrobot_resource(type_or_str: Any) -> bool:
    if origin is Union:  # ❌ Missing list, tuple, Sequence handling
        ...
```

**Missing**:

- `list[Well]` → should detect `Well` as resource
- `Sequence[Resource]` → should detect `Resource`
- `tuple[Plate, TipRack]` → should detect both

### 2. Parental Dependency Chain

**Location**: None (does not exist)

**Missing**: A mapping/service that understands:

- `Well` has parent `Plate`
- `TipSpot` has parent `TipRack`
- `Plate` sits on `PlateCarrier` or directly on slot-based deck
- `TipRack` sits on `TipCarrier` or directly on slot-based deck
- Carriers sit on `Deck` at rail positions
- Slot-based decks (OT-2) receive resources directly

### 3. Implicit Requirements from Operations

**Location**: `praxis/backend/utils/plr_static_analysis/visitors/protocol_requirement_extractor.py`

**Current**: Extracts hardware capabilities (`has_core96`, `has_iswap`)
**Missing**: Resource state requirements (tips on, plates placed)

### 4. Computational Graph Structure

**Location**: None (does not exist)

**Missing**: A graph representation of:

- Operation nodes (each `lh.xxx()` call)
- Data dependency edges (which resources flow where)
- State preconditions per node
- Execution ordering

---

## Proposed Architecture

### Phase 1: Enhanced Type Inspection

```python
# praxis/common/type_inspection.py

def extract_resource_types(type_or_str: Any) -> list[str]:
    """Extract all PLR resource types from a type hint, including generics.
    
    Examples:
        list[Well] -> ["Well"]
        Sequence[TipSpot] -> ["TipSpot"]  
        Union[Plate, TipRack] -> ["Plate", "TipRack"]
        tuple[Plate, list[Well]] -> ["Plate", "Well"]
    """
```

### Phase 2: Resource Parental Chain Registry

```python
# praxis/backend/utils/plr_static_analysis/resource_hierarchy.py

class ResourceHierarchyRegistry:
    """Registry of PLR resource parent-child relationships."""
    
    # Static knowledge of PLR hierarchy
    PARENTAL_CHAIN = {
        "Well": "Plate",
        "TipSpot": "TipRack", 
        "Plate": ["PlateCarrier", "Slot"],  # Depends on deck type
        "TipRack": ["TipCarrier", "Slot"],
        "PlateCarrier": "Deck",
        "TipCarrier": "Deck",
        "Slot": "Deck",  # For slot-based decks
    }
    
    DECK_TYPES = {
        "slot_based": ["OTDeck", "Opentrons*"],  # Resources go directly on slots
        "carrier_based": ["HamiltonSTARDeck", "*"],  # Resources need carriers
    }
    
    def get_full_chain(self, resource_type: str, deck_type: str) -> list[str]:
        """Get full parental chain from resource to deck."""
```

### Phase 3: Computational Graph Extractor

```python
# praxis/backend/utils/plr_static_analysis/visitors/computation_graph_extractor.py

class OperationNode(BaseModel):
    """A single operation in the protocol graph."""
    id: str
    method_name: str  # e.g., "transfer", "pick_up_tips"
    receiver: str  # e.g., "lh"
    arguments: dict[str, str]  # Arg name -> variable name
    line_number: int
    preconditions: list[StatePrecondition]

class ResourceNode(BaseModel):
    """A resource referenced in the protocol."""
    variable_name: str
    type_hint: str
    element_type: str | None  # For containers
    parental_chain: list[str]
    
class StatePrecondition(BaseModel):
    """A state that must be true before an operation."""
    precondition_type: str  # "resource_placed", "tips_loaded", "liquid_present"
    resource_variable: str
    target_location: str | None  # Deck position if known
    satisfied_by: str | None  # Which prior operation satisfies this
    
class ProtocolComputationGraph(BaseModel):
    """Complete computational graph for a protocol."""
    operations: list[OperationNode]
    resources: dict[str, ResourceNode]
    edges: list[tuple[str, str]]  # (from_op_id, to_op_id) for execution order
    preconditions: list[StatePrecondition]  # All required preconditions
```

### Phase 4: State Precondition Resolver

```python
# praxis/backend/core/precondition_resolver.py

class PreconditionResolver:
    """Resolves state preconditions against current deck state."""
    
    async def resolve_preconditions(
        self,
        graph: ProtocolComputationGraph,
        current_deck_state: DeckState,
        available_resources: list[ResourceOrm],
    ) -> ResolutionResult:
        """
        Determine what actions are needed to satisfy preconditions.
        
        Returns:
            - deck_config: DeckLayoutConfig to set up deck
            - already_satisfied: Preconditions already met
            - unresolvable: Preconditions that cannot be met
            - suggestions: Auto-assignment suggestions
        """
```

---

## Implementation Roadmap

### Milestone 1: Container Type Extraction (S - 2 hours)

- [ ] Enhance `is_pylabrobot_resource()` to handle `list`, `tuple`, `Sequence`
- [ ] Add `extract_resource_types()` function
- [ ] Unit tests for all container patterns

### Milestone 2: Resource Hierarchy Registry (M - 4 hours)

- [ ] Create `ResourceHierarchyRegistry` class
- [ ] Define static parental chain mappings
- [ ] Add deck type detection (slot-based vs carrier-based)
- [ ] Method to compute full chain for any resource type
- [ ] Unit tests

### Milestone 3: Variable Type Tracking in CST (L - 1 day)

- [ ] Create `VariableTypeTracker` visitor
- [ ] Track assignments: `wells = plate["A1:A8"]` → `wells: list[Well]`
- [ ] Handle attribute access: `plate.wells` → type of `wells`
- [ ] Handle subscript: `wells[0]` → `Well`
- [ ] Unit tests

### Milestone 4: Computation Graph Extractor (L - 1 day)  

- [ ] Create `ComputationGraphExtractor` visitor
- [ ] Extract operation nodes from method calls
- [ ] Build resource dependency edges
- [ ] Infer preconditions from operation signatures
- [ ] Unit tests

### Milestone 5: Precondition Resolver Service (L - 1 day)

- [ ] Create `PreconditionResolver` service
- [ ] Implement deck state comparison
- [ ] Generate `DeckLayoutConfig` from unmet preconditions
- [ ] Handle idempotency (already satisfied preconditions)
- [ ] Integration tests

### Milestone 6: Integration with Discovery & Run Setup (M - 4 hours)

- [ ] Store computation graph in `FunctionProtocolDefinitionOrm`
- [ ] Surface preconditions in Run Protocol workflow
- [ ] Auto-suggest deck configuration
- [ ] User confirmation/override flow

---

## Phase 2: Tracer-Based Runtime Analysis (Alternative/Complement to Static)

For protocols where static CST analysis is insufficient (loops, conditionals depending on values), we can use **JAX-style tracing** by executing the protocol with tracer objects.

### Why Tracers?

| Approach | Pros | Cons |
|----------|------|------|
| Pure Static (CST) | No execution needed, fast | Can't resolve loop counts, conditionals |
| Tracer Execution | Handles loops, conditionals | Requires protocol to be importable |
| Hybrid | Best of both | More complex implementation |

### Tracer Class Hierarchy

```python
# praxis/backend/core/tracing/tracers.py

@dataclass
class TracedValue(ABC):
    """Base class for all traced values."""
    name: str
    declared_type: str
    recorder: OperationRecorder
    
@dataclass
class TracedResource(TracedValue):
    """Tracer for PLR Resources (Plate, TipRack, etc.)."""
    resource_type: str = "Resource"
    parental_chain: list[str] = field(default_factory=list)
    
    def __getitem__(self, key) -> TracedWellCollection:
        """plate["A1:A8"] -> TracedWellCollection."""
        self._record_access("__getitem__", key)
        return TracedWellCollection(...)
    
    def wells(self) -> TracedWellCollection:
        """plate.wells() -> TracedWellCollection."""
        return self.__getitem__(":")

@dataclass
class TracedWellCollection(TracedValue):
    """Tracer for list[Well] / list[TipSpot]."""
    element_type: str = "Well"
    source_resource: TracedResource | None = None
    
    def __iter__(self):
        """For loops yield symbolic elements."""
        yield TracedWell(name=f"each_{self.name}", ...)
    
    def __getitem__(self, index) -> TracedWell:
        """wells[0] -> TracedWell."""
        return TracedWell(name=f"{self.name}[{index}]", ...)

@dataclass
class TracedMachine(TracedValue):
    """Tracer for machines (LiquidHandler, PlateReader)."""
    machine_type: str = "Machine"
    
    def __getattr__(self, name: str):
        """lh.transfer(...) -> record operation."""
        def method_proxy(*args, **kwargs):
            return self.recorder.record(self, name, args, kwargs)
        return method_proxy
```

### Loop Handling Strategy

```python
# Protocol code:
for well in source_plate.wells():
    await lh.aspirate(well, volume)

# During tracing:
# 1. source_plate.wells() returns TracedWellCollection
# 2. __iter__ yields ONE TracedWell representing "each element"  
# 3. lh.aspirate(traced_well, volume) records:
#    OperationNode(method="aspirate", 
#                  args={"resource": "each_of_source_plate.wells()"},
#                  is_foreach=True,
#                  foreach_source="source_plate.wells()")

# Result: We know the loop body without knowing iteration count
```

### Conditional Handling Strategy

```python
# Protocol code:
if volume > threshold:
    await lh.aspirate(source, volume)
else:
    await lh.aspirate(source, volume / 2)

# During tracing with TracedValue for volume:
# 1. volume > threshold -> TracedComparison (unknown result)
# 2. Execute BOTH branches, record as conditional:
#    ConditionalNode(
#        condition="volume > threshold",
#        true_branch=[aspirate(source, volume)],
#        false_branch=[aspirate(source, volume/2)]
#    )

# Result: Both branches recorded, preconditions merged
```

### Protocol Tracing Executor

```python
# praxis/backend/core/tracing/executor.py

class ProtocolTracingExecutor:
    """Execute protocol with tracers to build computation graph."""
    
    async def trace_protocol(
        self,
        protocol_func: Callable,
        parameter_types: dict[str, str],
    ) -> ProtocolComputationGraph:
        """Trace a protocol function to build its computation graph."""
        
        # Create traced arguments from type hints
        traced_args = {}
        for name, type_str in parameter_types.items():
            traced_args[name] = self._create_tracer(name, type_str)
        
        # Execute with tracers
        try:
            await protocol_func(**traced_args)
        except TracingComplete:
            pass  # Expected - tracer can't complete some operations
        
        return self.recorder.build_graph()
```

### Milestone 7: Tracer Infrastructure (L - 1-2 days)

- [ ] Create `TracedValue`, `TracedResource`, `TracedWellCollection`, `TracedWell` classes
- [ ] Implement `__getitem__`, `__iter__`, `__getattr__` for operation recording
- [ ] Create `TracedMachine` with method proxying
- [ ] Create `OperationRecorder` to collect operations into graph
- [ ] Unit tests for tracer behavior

### Milestone 8: Tracer Execution Engine (L - 1 day)

- [ ] Create `ProtocolTracingExecutor`
- [ ] Implement tracer creation from type hints
- [ ] Handle async protocol execution with tracers
- [ ] Graceful handling of untraced operations (log & continue)
- [ ] Integration tests

### Milestone 9: Conditional/Loop Analysis (M - 4 hours)

- [ ] Implement `TracedComparison` for conditionals
- [ ] Record both conditional branches
- [ ] Merge preconditions from all branches
- [ ] Test with complex protocols

---

## Success Criteria

1. **Type Extraction**: `list[Well]`, `Sequence[TipSpot]`, `tuple[Plate, TipRack]` all correctly identify resource types
2. **Parental Inference**: Given a `Well`, system correctly infers need for `Plate` → `PlateCarrier`/`Slot` → `Deck`
3. **Deck Type Awareness**: OT-2 correctly infers slot placement; Hamilton correctly infers carrier placement
4. **Precondition Detection**: `lh.transfer()` correctly infers tip requirement
5. **Idempotency**: If tips are already loaded, system doesn't suggest redundant `pick_up_tips`
6. **DeckLayoutConfig Generation**: System can generate a valid deck config JSON for protocol requirements

---

## Related Files

- `praxis/common/type_inspection.py` - Needs enhancement
- `praxis/backend/utils/plr_static_analysis/visitors/protocol_discovery.py` - Entry point
- `praxis/backend/utils/plr_static_analysis/visitors/protocol_requirement_extractor.py` - Extend
- `praxis/backend/utils/plr_static_analysis/models.py` - New models needed
- `praxis/backend/core/deck_config.py` - Output format
- `praxis/backend/services/capability_matcher.py` - May need integration

## References

- **JAX Tracing**: JAX uses tracer objects during function execution to record primitives into a Jaxpr IR
- **Static Analysis Alternative**: Since we can't execute protocols at discovery time, we use CST analysis instead
- **Limitations**: Runtime-dependent values (loop counts, conditional branches) cannot be fully resolved statically

---

## Appendix A: Complete PLR Type Coverage

Based on analysis of `praxis.db`, tracers must cover:

### Machine Types (from `machine_definition_catalog`)

| Machine Category | Backend | Tracer Class |
|------------------|---------|--------------|
| `LiquidHandler` | `LiquidHandlerBackend` | `TracedMachine` |
| `PlateReader` | `PlateReaderBackend` | `TracedMachine` |
| `HeaterShaker` | `HeaterShakerBackend` | `TracedMachine` |
| `Shaker` | `ShakerBackend` | `TracedMachine` |
| `TemperatureController` | `TemperatureControllerBackend` | `TracedMachine` |
| `Thermocycler` | `ThermocyclerBackend` | `TracedMachine` |
| `Centrifuge` | `CentrifugeBackend` | `TracedMachine` |
| `Incubator` | `IncubatorBackend` | `TracedMachine` |
| `PumpArray` | `PumpArrayBackend` | `TracedMachine` |
| `Pump` | `PumpBackend` | `TracedMachine` |
| `Sealer` | `SealerBackend` | `TracedMachine` |
| `Peeler` | `PeelerBackend` | `TracedMachine` |
| `PowderDispenser` | `PowderDispenserBackend` | `TracedMachine` |
| `Arm` | - | `TracedMachine` |
| `Fan` | `FanBackend` | `TracedMachine` |

### Resource Types (from `resource_definition_catalog.plr_category`)

| PLR Category | Tracer Class | Child Element Type |
|--------------|--------------|-------------------|
| `Plate` | `TracedResource` | `Well` via `TracedWellCollection` |
| `TipRack` | `TracedResource` | `TipSpot` via `TracedTipSpotCollection` |
| `Trough` | `TracedResource` | `Well` via `TracedWellCollection` |
| `TubeRack` | `TracedResource` | `Tube` |
| `Tube` | `TracedContainer` | - |
| `Container` | `TracedContainer` | - |
| `Lid` | `TracedResource` | - |
| `PlateCarrier` | `TracedCarrier` | `CarrierSite` |
| `TipCarrier` | `TracedCarrier` | `CarrierSite` |
| `TroughCarrier` | `TracedCarrier` | `CarrierSite` |
| `carrier` (generic) | `TracedCarrier` | `CarrierSite` |
| `deck` | `TracedDeck` | varies |
| `Resource` (base) | `TracedResource` | - |

### Union Types (Multiple Inheritance)

For resources that inherit from multiple types (rare but possible):

```python
class UnionTracer(TracedValue):
    """Tracer for types with multiple inheritance."""
    component_tracers: list[TracedValue]
    
    def __getattr__(self, name: str):
        """Try each component tracer until one handles the attribute."""
        for tracer in self.component_tracers:
            if hasattr(tracer, name):
                return getattr(tracer, name)
        raise AttributeError(name)
```

---

## Appendix B: Protocol Caching Strategy

### Storage by Mode

| Mode | Storage | Format |
|------|---------|--------|
| **Browser (Pyodide)** | Pre-loaded in `praxis.db` (SQLite) | Cloudpickled bytecode |
| **Lite (SQLite)** | `FunctionProtocolDefinitionOrm.cached_bytecode` | Cloudpickled bytecode |
| **Production (PostgreSQL)** | `FunctionProtocolDefinitionOrm.cached_bytecode` | Cloudpickled bytecode |

### Cache Schema Extension

```python
# praxis/backend/models/orm/protocol.py

class FunctionProtocolDefinitionOrm(Base):
    # ... existing fields ...
    
    # New caching fields
    cached_source_hash: Mapped[str | None] = mapped_column(
        String(64),
        comment="SHA-256 hash of source for cache invalidation",
    )
    cached_bytecode: Mapped[bytes | None] = mapped_column(
        LargeBinary,
        comment="Cloudpickled protocol function for execution",
    )
    cached_graph_json: Mapped[dict | None] = mapped_column(
        JSON,
        comment="Pre-computed computation graph (ProtocolComputationGraph)",
    )
    cache_created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        comment="When the cache was last generated",
    )
```

### Cloudpickle Serialization

```python
# praxis/backend/core/protocol_cache.py
import cloudpickle
import hashlib

class ProtocolCache:
    """Manages protocol caching for cross-platform execution."""
    
    def cache_protocol(
        self,
        protocol_func: Callable,
        source_code: str,
        graph: ProtocolComputationGraph,
    ) -> tuple[bytes, str, dict]:
        """Cache a protocol for later execution.
        
        Returns:
            (bytecode, source_hash, graph_json)
        """
        bytecode = cloudpickle.dumps(protocol_func)
        source_hash = hashlib.sha256(source_code.encode()).hexdigest()
        graph_json = graph.model_dump()
        return bytecode, source_hash, graph_json
    
    def load_cached_protocol(self, bytecode: bytes) -> Callable:
        """Load a cached protocol for execution."""
        return cloudpickle.loads(bytecode)
    
    def is_cache_valid(self, source_code: str, cached_hash: str) -> bool:
        """Check if cache is still valid."""
        current_hash = hashlib.sha256(source_code.encode()).hexdigest()
        return current_hash == cached_hash
```

### Browser Mode Pre-loading

For browser mode, during `generate_browser_db.py`:

1. Discover all protocols
2. Trace/analyze each to build computation graph
3. Cloudpickle each protocol function
4. Store bytecode + graph in `praxis.db`
5. Ship `praxis.db` with frontend assets

---

## Appendix C: Static vs Dynamic Graph Nodes

Following JAX's approach, we use a **single unified graph** with nodes marked as static or dynamic.

### Node Classification

```python
class GraphNodeType(str, Enum):
    STATIC = "static"  # Can be pre-computed/evaluated
    DYNAMIC = "dynamic"  # Requires runtime data
    CONDITIONAL = "conditional"  # Branches based on runtime value
    FOREACH = "foreach"  # Loop over collection
```

### Static Nodes (Pre-evaluable)

| Node Pattern | Static? | Example |
|--------------|---------|---------|
| Literal arguments | ✅ Yes | `lh.aspirate(well, 100)` - volume is static |
| Default parameter values | ✅ Yes | `volume: float = 100.0` |
| Known type operations | ✅ Yes | `plate.wells()` - always returns Well collection |
| Fixed method calls | ✅ Yes | `lh.pick_up_tips(tips)` |

### Dynamic Nodes

| Node Pattern | Dynamic? | Example |
|--------------|----------|---------|
| Parameter-dependent values | ✅ Yes | `lh.aspirate(well, volume)` - volume from param |
| Collection size | ✅ Yes | `len(wells)` - depends on actual plate |
| Conditionals on values | ✅ Yes | `if volume > 50` |
| Loop iterations | ✅ Yes | `for i in range(n)` |

### Graph Representation

```python
class ComputationGraphNode(BaseModel):
    """A node in the computation graph."""
    id: str
    node_type: GraphNodeType
    operation: str  # Method name or special: "foreach", "cond", etc.
    
    # For static nodes - pre-computed where possible
    static_value: Any | None = None
    can_precompute: bool = False
    
    # For dynamic nodes
    depends_on_params: list[str] = []  # Which params affect this
    
    # For foreach nodes
    foreach_source: str | None = None  # Variable being iterated
    foreach_body: list[str] = []  # Child node IDs in loop body
    
    # For conditional nodes  
    condition_expr: str | None = None
    true_branch: list[str] = []
    false_branch: list[str] = []
    
    # Common
    preconditions: list[str] = []  # Precondition IDs required
    creates_state: list[str] = []  # States this node creates
```

---

## Appendix D: Testing Strategy

### Canonical Test Protocol Suite

Create test protocols in `tests/fixtures/protocols/`:

#### 1. `simple_linear.py` - No loops, no conditionals

```python
@protocol_function
async def simple_transfer(
    lh: LiquidHandler,
    source: Plate,
    dest: Plate,
    tips: TipRack,
):
    """Simple A→B transfer."""
    await lh.pick_up_tips(tips)
    await lh.aspirate(source["A1"], 100)
    await lh.dispense(dest["A1"], 100)
    await lh.drop_tips(tips)
```

#### 2. `loop_based.py` - For loop over wells

```python
@protocol_function
async def multi_well_transfer(
    lh: LiquidHandler,
    source: Plate,
    dest: Plate,
    tips: TipRack,
    volume: float = 50.0,
):
    """Transfer to multiple wells."""
    await lh.pick_up_tips(tips)
    for i, (src, dst) in enumerate(zip(source.wells(), dest.wells())):
        await lh.transfer(src, dst, volume)
    await lh.drop_tips(tips)
```

#### 3. `conditional.py` - If/else based on parameter

```python
@protocol_function
async def conditional_volume(
    lh: LiquidHandler,
    plate: Plate,
    tips: TipRack,
    volume: float,
    threshold: float = 50.0,
):
    """Conditional aspiration based on volume."""
    await lh.pick_up_tips(tips)
    if volume > threshold:
        await lh.aspirate(plate["A1"], volume)
    else:
        await lh.aspirate(plate["A1"], volume / 2)
    await lh.drop_tips(tips)
```

#### 4. `nested_call.py` - Protocol calling another protocol

```python
@protocol_function
async def outer_protocol(
    lh: LiquidHandler,
    plate: Plate,
    tips: TipRack,
):
    """Outer protocol that calls inner."""
    await inner_transfer(lh, plate, tips)
    await lh.drop_tips(tips)

@protocol_function
async def inner_transfer(
    lh: LiquidHandler,
    plate: Plate,
    tips: TipRack,
):
    """Inner helper protocol."""
    await lh.pick_up_tips(tips)
    await lh.aspirate(plate["A1"], 100)
```

#### 5. `multi_machine.py` - Multiple machine types

```python
@protocol_function
async def plate_reader_workflow(
    lh: LiquidHandler,
    pr: PlateReader,
    plate: Plate,
    tips: TipRack,
):
    """Workflow involving multiple machines."""
    await lh.pick_up_tips(tips)
    await lh.aspirate(plate["A1"], 100)
    await lh.dispense(plate["B1"], 100)
    await lh.drop_tips(tips)
    result = await pr.read_absorbance(plate, wavelength=450)
```

### Test Coverage Matrix

| Test Category | Backend Pytest | Pyodide Browser | Coverage Target |
|---------------|----------------|-----------------|-----------------|
| Type extraction | ✅ Required | ✅ Required | 90% |
| Hierarchy registry | ✅ Required | ❌ Backend only | 90% |
| CST graph extraction | ✅ Required | ❌ Backend only | 85% |
| Tracer infrastructure | ✅ Required | ✅ Required | 80% |
| Precondition resolver | ✅ Required | ✅ Required | 80% |
| Protocol caching | ✅ Required | ✅ Required | 80% |
| E2E protocol execution | ✅ Required | ✅ Required | 70% |

### Test Commands

```bash
# Backend unit tests
uv run pytest tests/backend/utils/test_type_inspection.py -v
uv run pytest tests/backend/utils/test_resource_hierarchy.py -v
uv run pytest tests/backend/utils/test_computation_graph.py -v
uv run pytest tests/backend/core/test_tracers.py -v
uv run pytest tests/backend/core/test_precondition_resolver.py -v

# Integration tests
uv run pytest tests/integration/test_protocol_discovery.py -v
uv run pytest tests/integration/test_protocol_caching.py -v

# Full coverage report
uv run pytest --cov=praxis/backend --cov-report=html tests/
```
