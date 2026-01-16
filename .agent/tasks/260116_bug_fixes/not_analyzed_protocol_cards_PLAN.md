# Plan: Fix "Not Analyzed" Badge on Protocols

## Goal

Fix the issue where protocol cards display "Not Analyzed" even when the database contains simulation results. Ideally, they should show "Ready" or relevant warnings.

## Problem Analysis

The issue stems from a mismatch between the SQLite database schema and the Frontend Data Model, coupled with incomplete mock data seeding.

1. **Frontend/Backend Mismatch**:
    - **Frontend Model (`ProtocolDefinition`)**: Expects `simulation_result: SimulationResult`.
    - **Database/Repository (`FunctionProtocolDefinition`)**: Returns `simulation_result_json: Record<string, unknown>`.
    - **Result**: `protocol.simulation_result` is `undefined` at runtime because the property name is `simulation_result_json`.

2. **Incomplete Mock Data**:
    - **Generation Script**: Seeds `simulation_result_json` with `{"status": "ready", "simulated": true}`.
    - **Frontend Interface (`SimulationResult`)**: Expects `passed`, `failure_modes`, `inferred_requirements`, etc. The seed data does not match the interface.

## User Review Required
>
> [!NOTE]
> This plan modifies the shared `ProtocolDefinition` interface. This is a low-risk change that aligns the model with the actual data structure found in Browser Mode (SQLite) and likely matches the backend serialization pattern more closely.

## Proposed Changes

### Frontend Code

#### [MODIFY] [protocol.models.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/protocols/models/protocol.models.ts)

Update the `ProtocolDefinition` interface to support the potentially unmapped JSON field from the database.

```typescript
export interface ProtocolDefinition {
  // ... existing fields
  simulation_result?: SimulationResult;
  // [NEW] Add alias for DB compatibility
  simulation_result_json?: SimulationResult; 
}
```

#### [MODIFY] [protocol-warning-badge.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/shared/components/protocol-warning-badge/protocol-warning-badge.component.ts)

Update the component logic to check `simulation_result_json` as a fallback.

```typescript
    // In failureModes computation
    return this.protocol.failure_modes ??
        this.protocol.simulation_result?.failure_modes ??
        this.protocol.simulation_result_json?.failure_modes ?? // [NEW] Check json field
        [];

    // In status computation
    const hasSimulation = this.protocol.simulation_result ||
        this.protocol.simulation_result_json || // [NEW] Check json field
        this.protocol.failure_modes ||
        this.protocol.simulation_version;
```

### Backend / Scripts

#### [MODIFY] [generate_browser_db.py](file:///Users/mar/Projects/pylabpraxis/scripts/generate_browser_db.py)

Update the seeding logic to construct a valid `SimulationResult` object structure.

```python
# Construct a proper SimulationResult object
simulation_result = {
    "passed": True,
    "level_completed": "logical",
    "violations": [],
    "inferred_requirements": [],
    "failure_modes": [],
    "failure_mode_stats": {},
    "simulation_version": "0.1.0",
    "execution_time_ms": 0,
    "simulated_at": now
}

# ...
safe_json_dumps(simulation_result), # simulation_result_json
```

## Verification Plan

### Automated Tests

Run the existing component tests (if any) or create a new test case for the badge.

- **Command**: `npm run test` (focus on `protocol-warning-badge.component.spec.ts`)

### Manual Verification

1. **Regenerate Database**: Run `uv run scripts/generate_browser_db.py`.
2. **Reset Browser DB**: Open the app with `?resetdb=1` to ensure new data is loaded.
3. **Inspect Protocols**:
    - Navigate to Protocol Library.
    - Verify that protocol cards show the "Ready" (Green Check) badge instead of "Not Analyzed".
    - Hover over the badge to confirm tooltip says "All simulation checks passed".
