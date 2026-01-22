# Plan: Fix "Not Analyzed" Badge on Protocols

## Goal

Fix the issue where protocol cards display "Not Analyzed" even when the database contains simulation results. Ideally, they should show "Ready" or relevant warnings.

## Problem Analysis

The issue stems from a mismatch between the SQLite database schema and the Frontend Data Model, coupled with incomplete mock data seeding.

1. **Frontend/Backend Mismatch**:
    - **Frontend Model (`ProtocolDefinition`)**: Expects `simulation_result: SimulationResult` (domain object).
    - **Database/Repository (`FunctionProtocolDefinition`)**: Returns `simulation_result_json: string` (raw JSON column).
    - **Result**: `protocol.simulation_result` is `undefined` at runtime because the property name is `simulation_result_json` and may need parsing.

2. **Incomplete Mock Data**:
    - **Generation Script**: Seeds `simulation_result_json` with minimal structure `{"status": "ready", "simulated": true}`.
    - **Frontend Interface (`SimulationResult`)**: Expects `passed`, `failure_modes`, `inferred_requirements`, `simulation_version`, etc.
    - The seed data does not match the interface shape.

3. **Architectural Issue**:
    - The original plan proposed adding `simulation_result_json` to the `ProtocolDefinition` interface.
    - This creates **dual-field confusion**: components wouldn't know which field to trust.
    - **Better approach**: Transform at the service/repository boundary (Adapter Pattern).

## User Review Required

> [!IMPORTANT]
> This revised plan uses **Service-Layer Transformation** (Adapter Pattern) instead of polluting the domain model.
>
> - **NO changes to `ProtocolDefinition` interface** (keeps it clean)
> - Transformation happens in Repository/Service when loading from SQLite
> - Components only see the proper domain object (`simulation_result`)
> - Single source of truth, maintainable, type-safe

## Proposed Changes

### Service/Repository Layer (Data Transformation)

#### [MODIFY] [repositories.ts](file:///Users/mar/Projects/praxis/praxis/web-client/src/app/core/db/repositories.ts) OR [protocol.service.ts](file:///Users/mar/Projects/praxis/praxis/web-client/src/app/features/protocols/services/protocol.service.ts)

**Add a mapping function** that transforms raw database rows into domain objects:

```typescript
/**
 * Maps raw SQLite protocol row to ProtocolDefinition domain object
 * Handles JSON deserialization and field name normalization
 */
function mapProtocolEntity(row: any): ProtocolDefinition {
  // Parse simulation_result_json if it's a string (SQLite TEXT column)
  let simulationResult: SimulationResult | null = null;
  
  if (row.simulation_result_json) {
    try {
      // Check if already parsed (some ORMs auto-deserialize)
      simulationResult = typeof row.simulation_result_json === 'string'
        ? JSON.parse(row.simulation_result_json)
        : row.simulation_result_json;
    } catch (e) {
      console.error('Failed to parse simulation_result_json', e);
    }
  }
  
  return {
    ...row,
    // Map JSON column to domain property (single source of truth)
    simulation_result: simulationResult,
    // Remove raw DB field to prevent confusion
    simulation_result_json: undefined
  } as ProtocolDefinition;
}
```

**Update Protocol Repository methods** to use the mapper:

```typescript
class ProtocolRepository {
  async getAll(): Promise<ProtocolDefinition[]> {
    const rows = await this.db.query('SELECT * FROM function_protocol_definitions');
    return rows.map(mapProtocolEntity);
  }
  
  async getById(id: string): Promise<ProtocolDefinition | null> {
    const row = await this.db.queryOne('SELECT * FROM function_protocol_definitions WHERE id = ?', [id]);
    return row ? mapProtocolEntity(row) : null;
  }
}
```

#### [NO CHANGE] [protocol.models.ts](file:///Users/mar/Projects/praxis/praxis/web-client/src/app/features/protocols/models/protocol.models.ts)

**Keep the interface clean** - no `simulation_result_json` field added.

#### [NO CHANGE] [protocol-warning-badge.component.ts](file:///Users/mar/Projects/praxis/praxis/web-client/src/app/shared/components/protocol-warning-badge/protocol-warning-badge.component.ts)

**Component logic stays simple** - only checks `simulation_result` (no fallback needed).

### Backend / Scripts

#### [MODIFY] [generate_browser_db.py](file:///Users/mar/Projects/praxis/scripts/generate_browser_db.py)

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

1. **Unit Test - Mapper Function**:
   - Create test cases for `mapProtocolEntity`:
     - Input: row with `simulation_result_json` as string → verify parsed object
     - Input: row with `simulation_result_json` as object → verify passed through
     - Input: row with `simulation_result_json = null` → verify null result
     - Input: row with invalid JSON string → verify graceful error handling

2. **Component Tests**:
   - Run existing badge component tests
   - **Command**: `npm run test` (focus on `protocol-warning-badge.component.spec.ts`)
   - Verify badge still works with properly mapped `simulation_result`

### Manual Verification

1. **Regenerate Database**: Run `uv run scripts/generate_browser_db.py`.
2. **Reset Browser DB**: Open the app with `?resetdb=1` to ensure new data is loaded.
3. **Inspect Protocols**:
    - Navigate to Protocol Library.
    - Verify that protocol cards show the "Ready" (Green Check) badge instead of "Not Analyzed".
    - Hover over the badge to confirm tooltip says "All simulation checks passed".
