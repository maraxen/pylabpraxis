# Task: Protocol Computation Graph & Parental Inference System

**Dispatch Mode**: 🧠 **Expert Mode** (Advanced Agent Required)

## Overview

This is a **multi-phase, XL-sized** feature that introduces a computational graph representation for protocols, enabling automatic inference of resource requirements and deck state preconditions.

## Context Files to Read First

Read these files carefully before starting:

1. `.agents/backlog/protocol_computation_graph.md` - Full specification and architecture
2. `praxis/common/type_inspection.py` - Current type inspection (needs enhancement)
3. `praxis/backend/utils/plr_static_analysis/visitors/protocol_discovery.py` - Existing protocol visitor
4. `praxis/backend/utils/plr_static_analysis/visitors/protocol_requirement_extractor.py` - Existing requirement extractor
5. `praxis/backend/utils/plr_static_analysis/models.py` - Existing models
6. `praxis/backend/core/deck_config.py` - Target output format (DeckLayoutConfig)
7. `praxis/backend/services/resource_type_definition.py` - Resource category knowledge

## Problem Statement

When a protocol declares parameters like:

```python
@protocol_function
async def my_protocol(
    lh: LiquidHandler,
    source_wells: list[Well],
    dest_plate: Plate,
    tips: TipRack,
):
    await lh.pick_up_tips(tips)
    await lh.transfer(source_wells, dest_plate.wells())
```

The system must:

1. **Extract resource types from containers**: `list[Well]` → element type `Well`
2. **Infer parental chain**: `Well` → `Plate` → `PlateCarrier`/`Slot` → `Deck`
3. **Detect implicit requirements**: `transfer` requires tips loaded → tip precondition
4. **Build computational graph**: Sequence of operations with dependencies
5. **Generate deck configuration**: Produce `DeckLayoutConfig` JSON
6. **Handle idempotency**: Don't suggest actions for already-satisfied preconditions

## Implementation Plan

### Phase 1: Enhanced Type Inspection

**File**: `praxis/common/type_inspection.py`

Add support for generic container types:

```python
from typing import get_origin, get_args, Sequence

def extract_resource_types(type_or_str: Any) -> list[str]:
    """Extract all PLR resource types from a type hint, including generics.
    
    Handles:
    - list[Well] -> ["Well"]
    - Sequence[TipSpot] -> ["TipSpot"]
    - tuple[Plate, TipRack] -> ["Plate", "TipRack"]
    - Union[Plate, None] -> ["Plate"]
    """
    if isinstance(type_or_str, str):
        return _extract_from_string(type_or_str)
    
    origin = get_origin(type_or_str)
    
    # Handle generic containers
    if origin in (list, tuple, set, frozenset) or origin is Sequence:
        args = get_args(type_or_str)
        results = []
        for arg in args:
            results.extend(extract_resource_types(arg))
        return results
    
    # Handle Union (including Optional)
    if origin is Union:
        args = get_args(type_or_str)
        results = []
        for arg in args:
            if arg is not type(None):
                results.extend(extract_resource_types(arg))
        return results
    
    # Base case: single type
    if is_pylabrobot_resource(type_or_str):
        name = getattr(type_or_str, "__name__", str(type_or_str))
        return [name]
    
    return []

def _extract_from_string(type_str: str) -> list[str]:
    """Parse type string like 'list[Well]' -> ['Well']."""
    import re
    # Match patterns like list[Well], Sequence[TipSpot], etc.
    pattern = r'\b(Well|Plate|TipRack|TipSpot|Container|Resource|Carrier|Deck|Spot|Trough)\b'
    return re.findall(pattern, type_str)
```

### Phase 2: Resource Hierarchy Registry

**New File**: `praxis/backend/utils/plr_static_analysis/resource_hierarchy.py`

```python
from enum import Enum
from pydantic import BaseModel

class DeckLayoutType(str, Enum):
    SLOT_BASED = "slot_based"  # OT-2, resources go directly on slots
    CARRIER_BASED = "carrier_based"  # Hamilton, resources need carriers

class ResourceHierarchyRegistry:
    """Static registry of PLR resource parent-child relationships."""
    
    # Direct parent mappings (child -> parent type)
    DIRECT_PARENT = {
        "Well": "Plate",
        "TipSpot": "TipRack",
        "Spot": "Carrier",  # Generic carrier spot
    }
    
    # Resources that can sit on carriers (carrier-based decks)
    CARRIER_RESOURCES = {
        "Plate": "PlateCarrier",
        "TipRack": "TipCarrier",
        "Trough": "TroughCarrier",
    }
    
    # Resources that can sit directly on slots (slot-based decks)
    SLOT_RESOURCES = {"Plate", "TipRack", "Trough", "Container"}
    
    # Carriers always sit on deck
    CARRIERS = {"PlateCarrier", "TipCarrier", "TroughCarrier", "Carrier"}
    
    # Deck type patterns
    SLOT_BASED_DECKS = {"OTDeck", "Opentrons"}
    CARRIER_BASED_DECKS = {"HamiltonSTARDeck", "Hamilton", "STARDeck"}
    
    def get_parental_chain(
        self, 
        resource_type: str, 
        deck_layout_type: DeckLayoutType = DeckLayoutType.CARRIER_BASED,
    ) -> list[str]:
        """Get full parental chain from resource up to Deck.
        
        Example for carrier-based:
            Well -> [Plate, PlateCarrier, Deck]
        
        Example for slot-based:
            Well -> [Plate, Slot, Deck]
        """
        chain = []
        current = resource_type
        
        # Step 1: Handle sub-resource to resource (Well -> Plate)
        if current in self.DIRECT_PARENT:
            parent = self.DIRECT_PARENT[current]
            chain.append(parent)
            current = parent
        
        # Step 2: Handle resource to carrier/slot
        if deck_layout_type == DeckLayoutType.CARRIER_BASED:
            if current in self.CARRIER_RESOURCES:
                carrier = self.CARRIER_RESOURCES[current]
                chain.append(carrier)
                chain.append("Deck")
            elif current in self.CARRIERS:
                chain.append("Deck")
        else:  # SLOT_BASED
            if current in self.SLOT_RESOURCES:
                chain.append("Slot")
                chain.append("Deck")
        
        return chain
    
    def infer_deck_type(self, deck_class_name: str) -> DeckLayoutType:
        """Infer deck layout type from deck class name."""
        for pattern in self.SLOT_BASED_DECKS:
            if pattern.lower() in deck_class_name.lower():
                return DeckLayoutType.SLOT_BASED
        return DeckLayoutType.CARRIER_BASED
```

### Phase 3: Computation Graph Models

**File**: `praxis/backend/utils/plr_static_analysis/models.py`

Add new models for the computation graph:

```python
class OperationNode(BaseModel):
    """A single operation in the protocol execution graph."""
    id: str = Field(description="Unique identifier for this operation")
    line_number: int = Field(description="Source line number")
    method_name: str = Field(description="Method being called (e.g., 'transfer')")
    receiver_variable: str = Field(description="Variable receiving the call (e.g., 'lh')")
    receiver_type: str | None = Field(default=None, description="Inferred type of receiver")
    arguments: dict[str, str] = Field(default_factory=dict, description="Arg name -> variable name")
    preconditions: list[str] = Field(default_factory=list, description="Required precondition IDs")
    
class ResourceNode(BaseModel):
    """A resource referenced in the protocol."""
    variable_name: str
    declared_type: str = Field(description="Type as declared in signature")
    element_type: str | None = Field(default=None, description="For containers, the element type")
    is_container: bool = Field(default=False)
    parental_chain: list[str] = Field(default_factory=list)
    placement_requirements: dict[str, Any] = Field(default_factory=dict)

class StatePrecondition(BaseModel):
    """A condition that must be true for an operation to succeed."""
    id: str
    precondition_type: Literal["resource_on_deck", "tips_loaded", "liquid_present", "plate_accessible"]
    resource_variable: str
    required_state: dict[str, Any] = Field(default_factory=dict)
    can_be_auto_satisfied: bool = Field(default=True, description="Can system auto-satisfy this?")

class ProtocolComputationGraph(BaseModel):
    """Complete computational graph for a protocol."""
    protocol_fqn: str
    operations: list[OperationNode] = Field(default_factory=list)
    resources: dict[str, ResourceNode] = Field(default_factory=dict)
    preconditions: list[StatePrecondition] = Field(default_factory=list)
    execution_order: list[str] = Field(default_factory=list, description="Operation IDs in order")
    inferred_deck_requirements: dict[str, Any] = Field(default_factory=dict)
```

### Phase 4: Computation Graph Extractor Visitor

**New File**: `praxis/backend/utils/plr_static_analysis/visitors/computation_graph_extractor.py`

```python
class ComputationGraphExtractor(cst.CSTVisitor):
    """Extracts a computation graph from a protocol function body.
    
    This visitor:
    1. Tracks variable assignments and their types
    2. Records method calls as operation nodes
    3. Builds resource dependency edges
    4. Infers state preconditions from operations
    """
    
    # Method patterns that imply preconditions
    PRECONDITION_PATTERNS = {
        "transfer": ["tips_loaded"],
        "aspirate": ["tips_loaded"],
        "dispense": ["tips_loaded"],
        "pick_up_tips": [],  # Creates tips_loaded state
        "drop_tips": ["tips_loaded"],
        "move_plate": ["plate_accessible"],
    }
    
    # Methods that create state
    STATE_CREATING_METHODS = {
        "pick_up_tips": "tips_loaded",
        "pick_up_tips96": "tips_loaded",
    }
    
    def __init__(self, parameter_types: dict[str, str]):
        """Initialize with known parameter types from function signature."""
        self._variable_types: dict[str, str] = parameter_types.copy()
        self._operations: list[OperationNode] = []
        self._resources: dict[str, ResourceNode] = {}
        self._preconditions: list[StatePrecondition] = []
        self._active_states: set[str] = set()  # Track created states
        self._op_counter = 0
```

### Phase 5: Precondition Resolver Service

**New File**: `praxis/backend/core/precondition_resolver.py`

```python
class ResolutionResult(BaseModel):
    """Result of resolving preconditions against current state."""
    can_execute: bool = Field(description="All preconditions can be satisfied")
    deck_config: DeckLayoutConfig | None = Field(default=None)
    already_satisfied: list[str] = Field(default_factory=list)
    needs_action: list[str] = Field(default_factory=list)
    unresolvable: list[str] = Field(default_factory=list)
    suggestions: list[dict[str, Any]] = Field(default_factory=list)

class PreconditionResolver:
    """Resolves protocol preconditions against current deck/asset state."""
    
    async def resolve(
        self,
        graph: ProtocolComputationGraph,
        current_deck_state: dict[str, Any],
        available_assets: list[ResourceOrm],
        deck_type: DeckLayoutType,
    ) -> ResolutionResult:
        """Resolve all preconditions and generate deck configuration."""
```

## Testing Requirements

### Unit Tests

1. **Type Extraction Tests** (`tests/backend/common/test_type_inspection.py`):
   - `test_extract_list_well` -> `["Well"]`
   - `test_extract_sequence_tipspot` -> `["TipSpot"]`
   - `test_extract_tuple_mixed` -> `["Plate", "TipRack"]`
   - `test_extract_optional_plate` -> `["Plate"]`
   - `test_extract_nested_list_list_well` -> `["Well"]`

2. **Hierarchy Tests** (`tests/backend/utils/test_resource_hierarchy.py`):
   - `test_well_chain_carrier_based` -> `["Plate", "PlateCarrier", "Deck"]`
   - `test_well_chain_slot_based` -> `["Plate", "Slot", "Deck"]`
   - `test_tiprack_chain` -> `["TipCarrier", "Deck"]`

3. **Graph Extractor Tests** (`tests/backend/utils/test_computation_graph.py`):
   - Test simple protocol produces correct graph
   - Test preconditions are correctly inferred
   - Test state creation is tracked

4. **Resolver Tests** (`tests/backend/core/test_precondition_resolver.py`):
   - Test already-satisfied preconditions are detected
   - Test deck config is correctly generated
   - Test unresolvable preconditions are flagged

## Definition of Done

- [ ] `extract_resource_types()` handles all container patterns
- [ ] `ResourceHierarchyRegistry` correctly computes parental chains
- [ ] `ComputationGraphExtractor` produces valid graphs from protocols
- [ ] `PreconditionResolver` generates correct `DeckLayoutConfig`
- [ ] Idempotency works (already-satisfied preconditions are skipped)
- [ ] All unit tests pass
- [ ] Integration with protocol discovery stores graph in DB
- [ ] `.agents/backlog/protocol_computation_graph.md` marked complete
- [ ] `.agents/DEVELOPMENT_MATRIX.md` updated

## Notes for Agent

1. **Start with Phase 1** - Enhanced type inspection is the foundation
2. **Use LibCST extensively** - Don't try to execute protocols, analyze the CST
3. **Reference JAX's approach** - Build a declarative IR, not an imperative executor
4. **Handle unknowns gracefully** - If a type can't be resolved, flag it for user input
5. **Test incrementally** - Each phase should have passing tests before moving to next

---

## Phase 6: Tracer-Based Analysis (For Loops/Conditionals)

For protocols where static CST analysis is insufficient (loops, conditionals depending on runtime values), we complement with **JAX-style tracing**.

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
    """Tracer for PLR Resources."""
    resource_type: str = "Resource"
    
    def __getitem__(self, key) -> TracedWellCollection:
        """plate["A1:A8"] -> TracedWellCollection."""
        self._record_access("__getitem__", key)
        return TracedWellCollection(
            name=f"{self.name}[{key}]",
            element_type="Well" if self.resource_type == "Plate" else "TipSpot",
            source_resource=self,
            recorder=self.recorder,
        )

@dataclass
class TracedWellCollection(TracedValue):
    """Tracer for list[Well] / list[TipSpot]."""
    
    def __iter__(self):
        """For loops yield symbolic element."""
        # Yield ONE symbolic element representing "each item"
        yield TracedWell(
            name=f"each_of_{self.name}",
            recorder=self.recorder,
        )

@dataclass  
class TracedMachine(TracedValue):
    """Tracer for machines."""
    
    def __getattr__(self, name: str):
        """lh.transfer(...) -> record operation."""
        def method_proxy(*args, **kwargs):
            return self.recorder.record(self, name, args, kwargs)
        return method_proxy
```

### Loop Handling

```python
# Protocol:
for well in source_plate.wells():
    await lh.aspirate(well, 100)

# Tracing:
# 1. source_plate.wells() -> TracedWellCollection
# 2. __iter__ yields TracedWell("each_of_source_plate.wells()")
# 3. lh.aspirate records OperationNode(is_foreach=True)

# Result: Loop body analyzed without knowing iteration count
```

### Conditional Handling

```python
# Protocol:
if volume > 50:
    await lh.aspirate(source, volume)
else:
    await lh.aspirate(source, volume/2)

# Tracing (both branches executed and recorded):
ConditionalNode(
    condition="volume > 50",
    true_branch=[aspirate(source, volume)],
    false_branch=[aspirate(source, volume/2)]
)
# Preconditions from BOTH branches merged
```

### When to Use Each Approach

| Approach | Use When |
|----------|----------|
| Static CST Only | Protocol is importable, no complex control flow |
| Tracer Execution | Protocol has loops/conditionals over resources |
| CST + Tracer Hybrid | Best coverage - CST first, tracer for unknowns |
