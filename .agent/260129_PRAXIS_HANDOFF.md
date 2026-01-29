# Praxis Audit Remediation Handoff

**Created:** 2026-01-29 10:43  
**Updated:** 2026-01-29 10:44  
**Orchestrator:** Antigravity Session 8298305b

---

## ⚠️ Pre-Dispatch Requirements

### Uncommitted Changes (MUST COMMIT FIRST)
```
 M praxis/web-client/src/app/features/execution-monitor/components/run-detail.component.ts  ← isoDate fix
 M praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.html
 M praxis/web-client/e2e/page-objects/assets.page.ts
 M praxis/web-client/package-lock.json
 M E2E_STATUS.md
```

**Action:** Commit and push before Stage 1 dispatch so Jules has clean HEAD.

---

## File Conflict Zones

Sessions touching the **same file zone** cannot run in parallel:

| Zone | Files | Conflict Risk |
|------|-------|---------------|
| **ZONE-SQLITE** | `sqlite.service.ts`, `sqlite-opfs.service.ts`, `sqlite-opfs.worker.ts`, `async-repositories.ts` | HIGH - Session 1C touches all |
| **ZONE-WORKERS** | `python.worker.ts`, `sqlite-opfs.worker.ts` | MEDIUM - 1A & 1C overlap on worker |
| **ZONE-INTERCEPTORS** | `browser-mode.interceptor.ts`, `browser-mock-router.ts` | LOW - isolated |
| **ZONE-RUN-PROTOCOL** | `run-protocol.component.ts`, `execution.service.ts` | HIGH - 2A & 4A overlap |
| **ZONE-ASSETS** | `asset-wizard.*`, `assets.page.ts` | MEDIUM - 2C & 4B overlap |
| **ZONE-E2E** | `e2e/specs/*.spec.ts` | LOW - new files only |

---

## Revised Stage Plan (Conflict-Aware)

### Stage 0: Critical Blockers (In Flight)
| Session ID | Task | Files | Status |
|------------|------|-------|--------|
| 2920010481660839573 | OPFS Batch Optimization | `sqlite-opfs.service.ts`, `sqlite-opfs.worker.ts` | 🔄 IN FLIGHT |

> ⚠️ **BLOCKS:** Sessions 1A, 1C until complete (ZONE-SQLITE, ZONE-WORKERS)

---

### Stage 1: Non-Conflicting Cleanup (3 parallel after Stage 0)

| # | Task | Zone | Files | Safe to Parallel? |
|---|------|------|-------|-------------------|
| 1A | Interceptor type safety | ZONE-INTERCEPTORS | `browser-mode.interceptor.ts`, `browser-mock-router.ts` | ✅ YES |
| 1B | Dead code removal | ISOLATED | `AuthService`, `ProtocolListSkeleton`, barrels | ✅ YES |
| 1C | Shared component types | ZONE-SHARED | `praxis-autocomplete.ts`, `machine-card.ts`, `filter-chip.ts` | ✅ YES |

**Deferred to Stage 1B (after OPFS lands):**
| # | Task | Zone | Blocked By |
|---|------|------|------------|
| 1D | Worker type assertions | ZONE-WORKERS | Stage 0 |
| 1E | SQLite service types | ZONE-SQLITE | Stage 0 |

---

### Stage 2: Refactoring (Sequential by zone)

| # | Task | Zone | Files | Depends On |
|---|------|------|-------|------------|
| 2A | name-parser refactor | ISOLATED | `name-parser.ts` | None ✅ |
| 2B | run-protocol decomposition | ZONE-RUN-PROTOCOL | `run-protocol.component.ts` | Stage 1 |
| 2C | asset-wizard refactor | ZONE-ASSETS | `asset-wizard.component.ts` | Stage 1 |

> 2A can run in parallel with Stage 1. 2B and 2C are sequential within their zones.

---

### Stage 3: E2E Coverage (4 parallel - all new files)

| # | Spec File | Zone | Conflict Risk |
|---|-----------|------|---------------|
| 3A | `auth.spec.ts` | NEW FILE | ✅ None |
| 3B | `workcell-dashboard.spec.ts` | NEW FILE | ✅ None |
| 3C | `protocol-failure.spec.ts` | NEW FILE | ✅ None |
| 3D | `asset-lifecycle.spec.ts` | NEW FILE | ✅ None |

> All 4 can run in parallel after Stage 2.

---

### Stage 4: API & TODOs (Sequential by zone)

| # | Task | Zone | Files | Depends On |
|---|------|------|-------|------------|
| 4A | Pause/Resume API | ZONE-RUN-PROTOCOL | `execution.service.ts` | Stage 2B |
| 4B | Asset TODOs | ZONE-ASSETS | `machine-list.ts`, `resource-list.ts` | Stage 2C |
| 4C | Run Protocol TODOs | ZONE-RUN-PROTOCOL | `deck-setup-wizard.ts` | Stage 4A |

---

## Dispatch Order Summary

```
[COMMIT FIRST] → Push outstanding changes

[STAGE 0] 🔄 OPFS optimization (in-flight)
    ↓
[STAGE 1] ← Can start now (3 parallel)
    1A: Interceptor types     ✅ 
    1B: Dead code removal     ✅
    1C: Shared component types ✅
    ↓
[STAGE 1B] ← After Stage 0 completes (2 parallel)
    1D: Worker types
    1E: SQLite types
    ↓
[STAGE 2] 
    2A: name-parser (parallel with 1B)
    2B: run-protocol (after 1B)
    2C: asset-wizard (after 1B)
    ↓
[STAGE 3] ← All 4 parallel (new files only)
    3A-3D: E2E specs
    ↓
[STAGE 4] ← Sequential
    4A → 4B → 4C
```

---

## Session Log

| Session ID | Stage | Task | Started | Status |
|------------|-------|------|---------|--------|
| 2920010481660839573 | 0 | OPFS optimization | 2026-01-29 09:00 | ✅ COMPLETE - committed |
| 15794144165487980335 | 1A | Interceptor types | 2026-01-29 11:02 | ✅ APPLIED (c82031a8) |
| 3493277385922095211 | 1C | Shared component types | 2026-01-29 11:03 | ✅ APPLIED (c82031a8) |
| 2027710808879946702 | 1B | Dead code removal | 2026-01-29 11:02 | 🔄 IN PROGRESS |
| 1907399999957321808 | 1D | Worker types | 2026-01-29 11:03 | ✅ COMPLETE - needs zip |
| 13931300007146917902 | 1E | SQLite service types | 2026-01-29 11:03 | ⚠️ BLOCKED - needs guidance |
| 3029736680512750348 | - | E2E Failures Audit | 2026-01-29 11:03 | 🔄 IN PROGRESS |

### Session 1E Guidance (SQLite types)

The `as any` casts in SQLite services hide deep type incompatibilities:
- `properties_json` and `state_history` are stored as JSON but accessed as typed objects
- Repository generic types don't flow through the RxJS operators properly

**Recommended approach:** Cancel this session and handle manually with a focused strategy:
1. Create explicit `DbRowResult` interfaces matching SQLite return shapes
2. Add type-safe JSON parsing helpers with validation
3. Keep `as any` only at the JSON boundary (1-2 locations) instead of scattered

---

## Notes

- **Before dispatch:** Commit all outstanding changes
- Sessions in same ZONE must be sequential
- E2E specs are all new files → safe parallel
- Update this file after each batch lands
