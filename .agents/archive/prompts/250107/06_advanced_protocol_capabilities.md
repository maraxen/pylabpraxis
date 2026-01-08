# Advanced Protocol Capabilities

**Backlog**: `advanced_protocol_capabilities.md`
**Priority**: High (Value Add)
**Effort**: Large

---

## Goal

Implement deep protocol inspection and resource constraint matching to enhance protocol reliability and resource management.

## Background

This work was originally planned as Phases 5 & 6 of the Capability Tracking system. The foundational work (protocol parsing, capability extraction, machine matching) is complete.

---

## Phase 1: Call Graph Analysis

### Tasks

1. **Extract Function Calls**
   - Extend `ProtocolFunctionVisitor` to capture all method calls on machine/resource objects
   - Build list of called methods per protocol function

2. **Identify Nested Protocol Calls**
   - Detect when one `@protocol_function` calls another
   - Track call hierarchy

3. **Build Dependency DAG**
   - Create directed acyclic graph of protocol execution order
   - Use for scheduling and parallelization hints

### Files to Modify

| File | Action |
|------|--------|
| `praxis/backend/utils/plr_static_analysis/visitors/protocol_discovery.py` | Extend visitor |
| `praxis/backend/utils/plr_static_analysis/models.py` | Add `CallGraphNode` model |
| `praxis/backend/services/protocol.py` | Store call graph in DB |

---

## Phase 2: Resource Flow Analysis

### Tasks

1. **Track Resource Usage**
   - Identify when resources are passed to methods (e.g., `lh.aspirate(plate)`)
   - Build resource lifetime tracking

2. **Detect Allocation/Deallocation Patterns**
   - Identify resource creation within protocol
   - Track when resources go out of scope

3. **Conflict Detection**
   - Detect if same resource is used by concurrent operations
   - Warn on potential race conditions

---

## Phase 3: Resource Constraint Matching

### Tasks

1. **Extract Physical Constraints**
   - Parse protocol parameters for constraints (e.g., `num_wells >= 96`)
   - Extract from type hints and docstrings

2. **Inventory Matching Service**
   - Match constraints to available assets
   - Rank assets by constraint satisfaction

3. **Placement Validation**
   - Real-time validation of deck placement
   - Check physical constraints (size, compatibility)

### Files to Modify

| File | Action |
|------|--------|
| `praxis/backend/services/capability_matcher.py` | Extend for resources |
| `praxis/backend/core/consumable_assignment.py` | Add constraint matching |
| `web-client/src/app/features/run-protocol/` | UI for constraint feedback |

---

## Success Criteria

- [ ] Call graph visualization in protocol detail view
- [ ] Resource flow timeline in protocol detail view
- [ ] Constraint warnings during asset selection
- [ ] Placement validation errors in deck setup
