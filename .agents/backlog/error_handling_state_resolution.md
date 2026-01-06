# Error Handling & State Resolution

**Priority**: P2 (High)
**Owner**: Full Stack
**Created**: 2026-01-05
**Status**: Completed

---

## Overview

When a protocol step errors during execution, there is **uncertainty about the state** that was supposed to be updated by that step. Rather than assuming success or failure, the system should:

1. **Pause execution** on error
2. **Identify affected state** using tracer/simulation infrastructure
3. **Present user with resolution options**
4. **Log resolution for audit trail**
5. **Allow resume or abort** based on resolved state

---

## Problem Statement

### Example Scenario

```python
async def transfer_protocol(lh: LiquidHandler, source: Plate, dest: Plate):
    await lh.aspirate(source["A1"], 50)  # ✓ Success
    await lh.dispense(dest["A1"], 50)    # ✗ ERROR: Dispense failed
```

After the error:

- Did 50µL leave the tip? Maybe partially?
- Does `source["A1"]` have 50µL less? Yes (aspirate succeeded)
- Does `dest["A1"]` have 50µL more? Unknown (dispense failed)
- Is there liquid in the tip? Unknown

### Current Behavior

- Error is logged
- Execution stops
- User has no way to resolve state uncertainty
- Next run starts with incorrect state assumptions

### Target Behavior

1. Error is detected
2. System identifies: "Dispense to dest['A1'] failed - 50µL transfer uncertain"
3. User is prompted: "Did the liquid dispense successfully?"
   - **Yes** → Update state as if succeeded
   - **Partial** → Enter actual volume dispensed
   - **No** → Rollback aspirate effect, mark source as recovered
4. Resolution logged for audit
5. User can resume or abort

---

## Architecture

### Generalized Approach Using Computation Graph

The key insight is that we already have the infrastructure to determine **implicated states** at any point in execution:

1. **Computation Graph**: Records the sequence of operations
2. **Method Contracts**: Define preconditions and effects for each operation
3. **State Tracers**: Track state changes throughout execution
4. **Constraint Inference**: Determine which states are affected by each operation

When an error occurs, we can use this infrastructure to:

1. Identify the failed operation from the graph
2. Look up its method contract to find expected state changes
3. Query the state tracer for the current state values
4. Present ALL implicated states to the user for resolution

### Edge Case Handling

For complex scenarios where method contracts don't exist or are incomplete:

```python
def identify_implicated_states_generic(
    failed_operation: OperationRecord,
    graph: ProtocolComputationGraph,
    state_snapshot: SimulationState,
) -> list[UncertainStateChange]:
    """
    Use computation graph data flow analysis to identify
    any state that could have been affected by the failed operation.
    """
    
    # Get all arguments that were passed to the operation
    arg_resources = extract_resource_references(failed_operation.args)
    
    # For each resource, identify what state properties exist
    uncertain = []
    for resource_ref in arg_resources:
        resource_state = state_snapshot.get_resource_state(resource_ref)
        
        # Every mutable property of touched resources is potentially uncertain
        for prop_name, prop_value in resource_state.mutable_properties():
            uncertain.append(UncertainStateChange(
                state_key=f"{resource_ref}.{prop_name}",
                current_value=prop_value,
                description=f"State of {resource_ref}.{prop_name} may have changed",
                resolution_type="arbitrary",  # User can enter any value
            ))
    
    return uncertain
```

### Arbitrary Resolution Support

Rather than just "Yes/No/Partial", allow users to arbitrarily resolve states:

```python
class StateResolution(BaseModel):
    """User's resolution of an uncertain state change."""
    
    operation_id: str
    resolution_type: ResolutionType
    
    # For arbitrary resolutions - user can specify exact values
    resolved_values: dict[str, Any] = {}  # e.g., {"source.A1.volume": 45.0, "tip.has_liquid": False}
    
    # Audit trail
    resolved_by: str
    resolved_at: datetime
    notes: str | None = None
```

### Integration with Existing Infrastructure

```
┌─────────────────────────────────────────────────────────────────┐
│                    Error Occurs During Execution                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. OperationRecorder has full operation history                 │
│  2. StatefulTracedMachine has current state snapshot             │
│  3. MethodContracts (if available) define expected effects       │
│  4. ComputationGraph shows data flow dependencies                │
│                                                                  │
│                              ↓                                   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ StateResolutionService.identifyUncertainStates()            ││
│  │                                                              ││
│  │ 1. Query method contract for known effects (fast path)      ││
│  │ 2. If no contract, use graph analysis:                      ││
│  │    - Find all resource refs in operation args               ││
│  │    - For each resource, enumerate mutable properties        ││
│  │    - Mark all as potentially uncertain                      ││
│  │ 3. Return list of UncertainStateChange with current values  ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│                              ↓                                   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ StateResolutionDialog                                        ││
│  │                                                              ││
│  │ Shows each uncertain state with:                             ││
│  │ - Current value (from state snapshot)                        ││
│  │ - Input field for user to specify actual value               ││
│  │ - Quick actions: "Confirm as-is", "Reset to previous"        ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## State Resolution Model

### Resolution Types

```python
from enum import Enum
from pydantic import BaseModel

class ResolutionType(Enum):
    CONFIRMED_SUCCESS = "confirmed_success"  # Effect actually happened
    CONFIRMED_FAILURE = "confirmed_failure"  # Effect did not happen
    PARTIAL = "partial"  # Effect partially happened (e.g., partial volume)
    UNKNOWN = "unknown"  # User cannot determine - system uses conservative estimate

class StateResolution(BaseModel):
    """User's resolution of an uncertain state change."""
    
    operation_id: str  # ID of the failed operation
    resolution_type: ResolutionType
    
    # For partial resolutions
    partial_values: dict[str, Any] | None = None  # e.g., {"volume": 25.0}
    
    # Audit trail
    resolved_by: str  # User or "system"
    resolved_at: datetime
    notes: str | None = None  # Optional user notes
```

### Affected State Identification

Using method contracts to identify what state might have changed:

```python
def identify_uncertain_state(
    failed_operation: OperationRecord,
    contracts: dict[str, MethodContract],
) -> list[UncertainStateChange]:
    """Identify state that may or may not have changed due to failure."""
    
    contract = contracts.get(failed_operation.method_name)
    if not contract:
        return []
    
    uncertain = []
    
    # Check each effect in the contract
    if contract.aspirates_from:
        uncertain.append(UncertainStateChange(
            state_key=f"{failed_operation.args[contract.aspirates_from]}.volume",
            expected_delta=-contract.get_volume(failed_operation),
            description=f"Volume change in {contract.aspirates_from}",
        ))
    
    if contract.dispenses_to:
        uncertain.append(UncertainStateChange(
            state_key=f"{failed_operation.args[contract.dispenses_to]}.volume",
            expected_delta=+contract.get_volume(failed_operation),
            description=f"Volume change in {contract.dispenses_to}",
        ))
    
    if contract.loads_tips:
        uncertain.append(UncertainStateChange(
            state_key="machine.tips_loaded",
            expected_delta=True,
            description="Tip pickup",
        ))
    
    return uncertain
```

---

## UI Components

### State Resolution Dialog

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️ Operation Failed - State Uncertain                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  The following operation failed:                                 │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ lh.dispense(dest_plate["A1"], 50)                           ││
│  │ Error: Pressure fault detected                               ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  The system cannot determine if the liquid was dispensed.        │
│  Please verify and select the actual outcome:                    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🔘 Liquid dispensed successfully (50µL to dest_plate A1)    ││
│  │ 🔘 Liquid did NOT dispense (50µL still in tip)              ││
│  │ 🔘 Partial dispense: [____] µL                              ││
│  │ 🔘 I don't know (use conservative estimate)                 ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Optional notes: [___________________________________]           │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Resolve   │  │    Abort    │  │   View Affected State   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Affected State Viewer

Shows what resources are affected and their current vs expected state:

```
┌─────────────────────────────────────────────────────────────────┐
│  Affected State                                                  │
├──────────────┬──────────────┬──────────────────────────────────┤
│  Resource    │  Before      │  After (if succeeded)            │
├──────────────┼──────────────┼──────────────────────────────────┤
│  dest A1     │  0µL         │  50µL                            │
│  tip (ch 1)  │  50µL        │  0µL                             │
└──────────────┴──────────────┴──────────────────────────────────┘
```

---

## Audit Logging

All resolutions should be logged for audit purposes:

```python
class StateResolutionLog(BaseModel):
    """Audit log entry for a state resolution."""
    
    run_id: str
    operation_id: str
    operation: str  # Human-readable operation description
    error: str
    uncertain_state: list[UncertainStateChange]
    resolution: StateResolution
    resolved_by: str
    resolved_at: datetime
    
    # Post-resolution actions
    action_taken: Literal["resume", "abort", "retry"]
```

Store in database for later review and debugging.

---

## Implementation Tasks

### Phase 1: Backend - State Uncertainty Detection

- [x] Create `UncertainStateChange` model
- [x] Implement `identify_uncertain_state()` using method contracts
- [x] Create `StateResolution` model
- [x] Unit tests for uncertainty detection

### Phase 2: Backend - Resolution Processing

- [x] Implement `apply_resolution()` to update simulation state
- [x] Implement rollback logic for "confirmed failure"
- [x] Implement partial volume handling
- [x] Create `StateResolutionLog` model and repository
- [x] Unit tests for resolution processing

### Phase 3: Backend - API Endpoints

- [x] `POST /api/v1/runs/{id}/resolve-state` - Submit resolution
- [x] `GET /api/v1/runs/{id}/uncertain-state` - Get uncertain state for a paused run
- [x] `POST /api/v1/runs/{id}/resume` - Resume after resolution
- [x] Integration tests

### Phase 4: Frontend - Resolution Dialog

- [x] Create `StateResolutionDialogComponent`
- [x] Create `AffectedStateViewerComponent`
- [x] Integrate with `ExecutionService` error handling
- [x] Unit tests

### Phase 5: Frontend - Execution Monitor Integration

- [x] Show "Awaiting Resolution" status for paused runs
- [x] Show resolution history in run detail view
- [x] Add quick-access to resolution dialog from run card
- [x] Integration tests

### Phase 6: Browser Mode Support

- [x] Implement resolution logic in Pyodide worker
- [x] Store resolution logs in SqliteService
- [x] E2E tests for browser mode resolution flow

---

## Files to Create/Modify

### Backend

| File | Action | Description |
|------|--------|-------------|
| `core/simulation/state_resolution.py` | Create | Resolution models and logic |
| `services/state_resolution_service.py` | Create | Resolution processing |
| `api/runs.py` | Modify | Add resolution endpoints |
| `models/orm/resolution.py` | Create | ORM for resolution logs |

### Frontend

| File | Action | Description |
|------|--------|-------------|
| `features/execution-monitor/dialogs/state-resolution.component.ts` | Create | Resolution dialog |
| `features/execution-monitor/components/affected-state-viewer.component.ts` | Create | State viewer |
| `core/services/execution.service.ts` | Modify | Handle resolution flow |

---

## Success Criteria

1. [x] Errors during execution trigger resolution dialog
2. [x] Uncertain state is correctly identified from method contracts
3. [x] User can resolve as success, failure, partial, or unknown
4. [x] Resolution updates simulation state correctly
5. [x] Resolution is logged for audit
6. [x] User can resume or abort after resolution
7. [x] Works in browser mode with Pyodide

---

## Related Documents

- [protocol_simulation.md](./protocol_simulation.md) - Simulation infrastructure
- [execution_monitor.md](./execution_monitor.md) - Run monitoring
- [state_snapshot_tracing.md](./state_snapshot_tracing.md) - State tracking
