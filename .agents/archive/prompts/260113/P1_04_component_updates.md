# Agent Prompt: Component Updates for ProtocolRun Schema

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P1
**Batch:** [260113](./README.md)
**Backlog Reference:** [frontend_schema_sync.md](../../backlog/frontend_schema_sync.md)

---

## 1. The Task

The `data-visualization.component.ts` accesses `ProtocolRunRead` properties that have been renamed or removed in the new schema. This causes TypeScript compilation errors.

**User Value:** Fix component to use correct field names from the new schema.

---

## 2. Technical Implementation Strategy

**ProtocolRun Field Mapping:**

| Old Field | New Field | Notes |
|:----------|:----------|:------|
| `started_at` | `start_time` | Renamed |
| `completed_at` | `end_time` | Renamed |
| `protocol_name` | `name` | Use the run's `name` field |
| `protocol_definition_accession_id` | `top_level_protocol_definition_accession_id` | More specific FK |

**Current ProtocolRunRead fields (from API):**

- `accession_id`
- `created_at`, `updated_at`
- `name`
- `status`
- `start_time`, `end_time`
- `data_directory_path`
- `duration_ms`
- `input_parameters_json`, `resolved_assets_json`, `output_data_json`

**Missing:** `protocol_name` was never a direct field; it was derived from joining with protocol definition.

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/data/data-visualization.component.ts` | Fix ProtocolRunRead property access |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/core/api-generated/models/ProtocolRunRead.ts` | Current API model structure |
| `praxis/web-client/src/app/core/db/schema.ts` | Browser DB schema with correct field names |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular.
- **Frontend Path**: `praxis/web-client`
- Handle nullable Date fields properly (use `Date` constructor or leave undefined).
- Use TypeScript type guards or optional chaining for safety.

---

## 5. Implementation Details

### data-visualization.component.ts (Lines 643-658)

The component maps `ProtocolRunRead[]` to `MockRun[]` for visualization. Update the mapping:

**Current Code (approximately lines 643-658):**

```typescript
const mappedRuns: MockRun[] = runs.map(r => {
  const name = r.name || r.protocol_name || 'Unknown Protocol';
  // ...
  return {
    id: r.accession_id,
    protocolName: name,
    protocolId: r.top_level_protocol_definition_accession_id || r.protocol_definition_accession_id || 'unknown',
    status: (r.status || 'failed').toLowerCase() as 'completed' | 'running' | 'failed',
    startTime: r.started_at ? new Date(r.started_at) : new Date(r.created_at),
    endTime: r.completed_at ? new Date(r.completed_at) : undefined,
    wellCount: wellCount, 
    totalVolume: 1000
  };
});
```

**Fixed Code:**

```typescript
const mappedRuns: MockRun[] = runs.map(r => {
  // Use run name; fallback to 'Unknown Protocol' (protocol_name was never a direct field)
  const name = r.name || 'Unknown Protocol';
  // Infer well count based on protocol name/type
  let wellCount = 96;
  if (name.includes('Simple') || name.includes('Transfer')) wellCount = 12;
  
  return {
    id: r.accession_id,
    protocolName: name,
    // top_level_protocol_definition_accession_id is the correct FK
    protocolId: (r as any).top_level_protocol_definition_accession_id || 'unknown',
    status: (r.status || 'failed').toLowerCase() as 'completed' | 'running' | 'failed',
    // Use start_time instead of started_at
    startTime: r.start_time ? new Date(r.start_time) : (r.created_at ? new Date(r.created_at) : new Date()),
    // Use end_time instead of completed_at
    endTime: r.end_time ? new Date(r.end_time) : undefined,
    wellCount: wellCount, 
    totalVolume: 1000 // Default for seeded runs
  };
});
```

**Key Changes:**

1. Remove references to `r.protocol_name` (field doesn't exist)
2. `r.started_at` → `r.start_time`
3. `r.completed_at` → `r.end_time`
4. `r.protocol_definition_accession_id` → `r.top_level_protocol_definition_accession_id` (cast to `any` if not in type)

---

## 6. Verification Plan

**Definition of Done:**

1. No TypeScript errors for ProtocolRun field access:

   ```bash
   cd praxis/web-client && npx tsc --noEmit 2>&1 | grep data-visualization
   ```

   Expected: No output (no errors).

2. Component renders without runtime errors:

   ```bash
   cd praxis/web-client && npm run build
   ```

   Expected: Build succeeds.

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status (Phase 4 tasks)
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- [data-visualization.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/data/data-visualization.component.ts)
- [ProtocolRunRead.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/core/api-generated/models/ProtocolRunRead.ts)
