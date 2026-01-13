# Agent Prompt: Service Layer Updates

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P1
**Batch:** [260113](./README.md)
**Backlog Reference:** [frontend_schema_sync.md](../../backlog/frontend_schema_sync.md)

---

## 1. The Task

The backend now uses `_json` suffix for JSONB fields (e.g., `inferred_requirements_json` instead of `inferred_requirements`). Services that access these fields need to be updated.

**User Value:** Align service layer with new backend field naming conventions.

---

## 2. Technical Implementation Strategy

**JSONB Field Naming Convention:**

| Old Field Name | New Field Name |
|:---------------|:---------------|
| `inferred_requirements` | `inferred_requirements_json` |
| `failure_modes` | `failure_modes_json` |
| `simulation_result` | `simulation_result_json` |

**Affected Services:**

- `simulation-results.service.ts` - Uses these fields when fetching from API

**API Response Mapping:**
The service maps API responses to frontend models. The API response now uses `_json` suffixes consistently.

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/core/services/simulation-results.service.ts` | Update property access for JSONB fields |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/core/api-generated/models/FunctionProtocolDefinitionRead.ts` | Shows `_json` suffix usage (no these fields; they're in extended model) |
| `praxis/web-client/src/app/core/db/schema.ts` | Shows full schema with `_json` fields |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular.
- **Frontend Path**: `praxis/web-client`
- Service methods should gracefully handle missing fields.

---

## 5. Implementation Details

### simulation-results.service.ts Updates

The service currently accesses properties without the `_json` suffix. Update these accesses:

**Line 40 - getInferredRequirements:**

```typescript
// Before
map(response => (response.inferred_requirements as unknown as InferredRequirement[]) || []),

// After
map(response => (response.inferred_requirements_json as unknown as InferredRequirement[]) || []),
```

**Line 58 - getFailureModes:**

```typescript
// Before
map(response => (response.failure_modes as unknown as FailureMode[]) || []),

// After
map(response => (response.failure_modes_json as unknown as FailureMode[]) || []),
```

**Line 76 - getSimulationResult:**

```typescript
// Before
map(response => (response.simulation_result as unknown as SimulationResult) || null),

// After
map(response => (response.simulation_result_json as unknown as SimulationResult) || null),
```

> **Note:** The API-generated types may not include these `_json` properties explicitly. In that case, use type assertion or optional chaining:
>
> ```typescript
> map(response => ((response as any).inferred_requirements_json as InferredRequirement[]) || []),
> ```

---

## 6. Verification Plan

**Definition of Done:**

1. No TypeScript errors related to property access:

   ```bash
   cd praxis/web-client && npx tsc --noEmit 2>&1 | grep simulation-results
   ```

   Expected: No output (no errors).

2. Build succeeds:

   ```bash
   cd praxis/web-client && npm run build 2>&1 | grep -c "error TS"
   ```

   Expected: Count decreases or is 0.

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status (Phase 3 tasks)
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- [simulation-results.service.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/core/services/simulation-results.service.ts)
- [schema.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/core/db/schema.ts)
