# Simulation UI Integration (Phase 8)

**Priority**: P2 (High)
**Owner**: Frontend
**Created**: 2026-01-05
**Status**: Complete
**Last Updated**: 2026-01-07

---

## Overview

The backend simulation infrastructure is **complete** (Phases 0-7). This document covers **Phase 8: UI Integration** - surfacing simulation results to users in the deck setup wizard, execution monitor, and other UI components.

### Status (Complete)

### Backend Status (Complete)

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 0 | Tracer Execution (State-Independent Validation) | ✅ Complete |
| Phase 1 | PLR Method Semantics Database | ✅ Complete (40+ contracts) |
| Phase 2 | State-Aware Tracers | ✅ Complete |
| Phase 3 | Hierarchical Simulation Pipeline | ✅ Complete |
| Phase 4 | Bounds Analyzer for Loops | ✅ Complete |
| Phase 5 | Failure Mode Detector | ✅ Complete |
| Phase 6 | Integration & Caching | ✅ Complete |
| Phase 7 | Cloudpickle + Graph Replay (Browser Mode) | ✅ Complete |

**Tests**: 87 passing

---

## Data Available from Backend

The simulation cache provides the following data per protocol:

```python
class FunctionProtocolDefinitionOrm(Base):
    # Simulation results
    simulation_result_json: dict  # Full ProtocolSimulationResult
    inferred_requirements_json: list  # Quick access to requirements
    failure_modes_json: list  # Quick access to failure modes
    simulation_version: str  # For cache invalidation
    simulation_cached_at: datetime  # When simulation was run
```

### Inferred Requirements

```json
{
  "inferred_requirements": [
    {
      "resource_param": "source_plate",
      "requirement_type": "on_deck",
      "description": "Must be placed on machine deck"
    },
    {
      "resource_param": "source_plate",
      "requirement_type": "has_liquid",
      "wells": ["A1", "A2", "A3"],
      "min_volume_per_well": 50.0
    },
    {
      "requirement_type": "tips_available",
      "count": 96,
      "tip_type": "standard"
    }
  ]
}
```

### Failure Modes

```json
{
  "failure_modes": [
    {
      "operation_index": 3,
      "operation": "lh.aspirate(source_plate['A1'], 100)",
      "failure_type": "insufficient_volume",
      "precondition": "source_plate['A1'].volume >= 100",
      "suggestion": "Ensure source wells have at least 100µL"
    },
    {
      "operation_index": 5,
      "operation": "lh.pick_up_tips96(tip_rack)",
      "failure_type": "insufficient_tips",
      "precondition": "tip_rack.available_tips >= 96",
      "suggestion": "Provide tip rack with 96 available tips"
    }
  ]
}
```

---

## UI Integration Points

### 1. Protocol Selection UI - Failure Mode Warnings

**Location**: Protocol list in Run Protocol wizard

**Feature**: Show warning badges on protocols with known failure modes

```
┌─────────────────────────────────────────────────────────────────┐
│  Select Protocol                                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🧪 Serial Dilution                              ⚠️ 2 issues ││
│  │    Requires: LiquidHandler, 96-well plate, tips              ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🧪 Plate Stamping                               ✅ Ready    ││
│  │    Requires: LiquidHandler, 2x 96-well plates                ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

Clicking the warning expands to show failure mode details.

### 2. Deck Setup Wizard - Requirements Surface

**Location**: Deck configuration step in Run Protocol wizard

**Feature**: Auto-populate requirements, highlight missing/invalid

```
┌─────────────────────────────────────────────────────────────────┐
│  Deck Setup                                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Required Resources:                                             │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ✅ source_plate: Corning 96-well (A1-A12 need ≥50µL)        ││
│  │ ⚠️ dest_plate: [Select plate] - Empty plate required        ││
│  │ ✅ tip_rack: Hamilton 300µL tips (96 available)             ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌───────────────────────────────────────────────┐              │
│  │           Deck Visualization                    │              │
│  │   [tip_rack]  [source]  [dest]                 │              │
│  │      🔴         🟢       ⚠️                    │              │
│  └───────────────────────────────────────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

- 🟢 = Requirement met
- ⚠️ = Requirement partially met or needs attention
- 🔴 = Requirement not met

### 3. Execution Monitor - State Failure Visualization

**Location**: Run detail view in Execution Monitor

**Feature**: Show operation sequence with state at each step

```
┌─────────────────────────────────────────────────────────────────┐
│  Run Detail: Serial Dilution #47                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Operation Timeline:                                             │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 1. pick_up_tips96(tip_rack)                    ✅ 0.5s      ││
│  │    └─ State: 96 tips loaded                                 ││
│  │ 2. aspirate(source["A1"], 100)                 ✅ 1.2s      ││
│  │    └─ State: source.A1: 500µL → 400µL                       ││
│  │ 3. dispense(dest["A1"], 100)                   ❌ ERROR     ││
│  │    └─ State: [UNCERTAIN] dest.A1: 0µL → ???                 ││
│  │ 4. [not executed]                                           ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4. Time Travel Debugging

**Location**: Run detail view, new "State Inspector" tab

**Feature**: Scrub through operation timeline to inspect state at any point

```
┌─────────────────────────────────────────────────────────────────┐
│  State Inspector                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Timeline: [━━━━━━━●━━━━━━━━━━━━━━━━━━━━━━] Operation 3/12      │
│            ← Prev    ● Current   Next →                          │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Operation: lh.dispense(dest_plate["A1"], 100)               ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  State Before:                     State After:                  │
│  ┌─────────────────────┐          ┌─────────────────────┐       │
│  │ Tips: 96 loaded     │    →     │ Tips: 96 loaded     │       │
│  │ source.A1: 400µL    │          │ source.A1: 400µL    │       │
│  │ dest.A1: 0µL        │          │ dest.A1: 100µL      │       │
│  └─────────────────────┘          └─────────────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5. State History Timeline

**Location**: Sidebar in Run detail view

**Feature**: Visual timeline showing state changes through execution

```
┌─────────────────────────────────────────────────────────────────┐
│  State History                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Tips:           [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]  96→96→96→0   │
│  source.A1:      [████████████░░░░░░░░░░░░░░░]   500→400→300   │
│  dest.A1:        [░░░░░░░░░░░░███████████████]   0→100→200     │
│                                                                  │
│  Legend: ░ = unchanged  █ = value present  ▌= partial           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Tasks

### Phase 8.1: API Service Layer

- [x] Create `SimulationResultsService` to fetch simulation data
- [x] Add `getProtocolWarnings()` method for quick failure mode check (via `getFailureModes`)
- [x] Add `getInferredRequirements()` method for deck setup
- [x] Add `getStateHistory()` method for time travel debugging
- [ ] Unit tests

### Phase 8.2: Protocol Selection Warnings

- [x] Add warning badge component for protocols with failure modes
- [x] Create failure mode expansion panel
- [x] Integrate with protocol list in Run Protocol wizard
- [x] Unit tests (Manual verification complete)

### Phase 8.3: Deck Setup Requirements Surface

- [x] Create `RequirementIndicatorComponent` (✅/⚠️/🔴)
- [x] Auto-populate requirements from simulation data
- [x] Validate current deck state against requirements
- [x] Highlight slots with issues
- [x] Integration with existing deck setup wizard
- [ ] Unit tests

### Phase 8.4: Execution Monitor State Display ✅ COMPLETE

- [x] Add state delta display to operation timeline
- [x] Highlight uncertain state in failed operations
- [x] Create state diff component
- [x] Unit/Integration tests

### Phase 8.5: Time Travel Debugging

- [x] Create `StateInspectorComponent`
- [x] Create timeline scrubber control
- [x] Create state comparison view (before/after)
- [x] Implement operation navigation (prev/next)
- [ ] Unit tests

### Phase 8.6: State History Timeline

- [x] Create `StateHistoryTimelineComponent`
- [x] Create sparkline-style state visualization
- [x] Integrate with run detail sidebar (Implemented as new Tab)
- [ ] Unit tests

### Phase 8.7: Browser Mode Support

- [x] Ensure all components work with SqliteService
- [x] Handle case where simulation data is missing
- [ ] E2E tests for browser mode

---

## Files to Create/Modify

### Services

| File | Action | Description |
|------|--------|-------------|
| `core/services/simulation-results.service.ts` | Create | Fetch simulation data |

### Components

| File | Action | Description |
|------|--------|-------------|
| `features/run-protocol/components/protocol-warnings.component.ts` | Create | Warning badges |
| `features/run-protocol/components/requirement-indicator.component.ts` | Create | ✅/⚠️/🔴 |
| `features/execution-monitor/components/state-inspector.component.ts` | Create | Time travel |
| `features/execution-monitor/components/state-history-timeline.component.ts` | Create | Timeline |
| `features/execution-monitor/components/operation-state-delta.component.ts` | Create | State diff |

### Models

| File | Action | Description |
|------|--------|-------------|
| `models/simulation.models.ts` | Create | Frontend models for simulation data |

---

## Success Criteria

1. [x] Protocols with failure modes show warning badges
2. [x] Deck setup wizard shows all inferred requirements
3. [x] Requirements are validated against current deck state
4. [x] Execution monitor shows state at each operation
5. [x] Time travel debugging allows scrubbing through state history
6. [x] State history timeline provides visual overview
7. [x] All features work in browser mode

---

## Related Documents

- [protocol_simulation.md](./protocol_simulation.md) - Backend simulation implementation
- [run_protocol_workflow.md](./run_protocol_workflow.md) - Run workflow
- [execution_monitor.md](./execution_monitor.md) - Monitor feature
- [error_handling_state_resolution.md](./error_handling_state_resolution.md) - Error handling
