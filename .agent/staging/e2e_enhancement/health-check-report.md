# SDET Static Analysis: health-check.spec.ts

**Target File:** [health-check.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/health-check.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested

This is a **minimal infrastructure verification test** designed to validate the E2E environment before running heavier test suites. It verifies:

1. **App Shell Rendering** — Checks that `.sidebar-rail` is visible after navigation
2. **SQLite Service Initialization** — Validates `sqliteService.isReady$` returns `true`
3. **Worker-Indexed Database Isolation** — Uses `app.fixture` which navigates with `dbName=praxis-worker-N`

The test explicitly documents its purpose: "Use this to verify global setup stabilization without running full specs."

### Assertions (Success Criteria)

| Assertion | Target | Type |
|-----------|--------|------|
| `.sidebar-rail` visible | App shell loaded | UI Visibility |
| `sqliteService.isReady$.getValue() === true` | Database initialized | State Check |

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

#### ✅ Strengths

1. **Uses `app.fixture` Correctly (Line 1)**
   ```typescript
   import { test, expect } from '../fixtures/app.fixture';
   ```
   - Inherits worker-indexed database isolation
   - Automatic localStorage flag setting
   - Welcome dialog dismissal handled by fixture

2. **Well-Documented Purpose (Lines 3-13)**
   - JSDoc clearly explains what the test verifies
   - Documents dependency on fixture behavior

3. **Console Logging for Debugging (Lines 22, 25, 33)**
   - Provides execution traceability without polluting assertions

#### 🟡 Moderate Issues

1. **Redundant Assertion (Line 23)**
   ```typescript
   await expect(page.locator('.sidebar-rail')).toBeVisible();
   ```
   - The fixture's `beforeEach` already asserts this (app.fixture.ts:83)
   - Assertion is duplicated but serves a documentation purpose

2. **Window Object Coupling (Lines 26-29)**
   ```typescript
   const service = (window as any).sqliteService;
   return service && typeof service.isReady$?.getValue === 'function' && service.isReady$.getValue() === true;
   ```
   - Relies on `sqliteService` being exposed on `window`
   - Tightly coupled to Angular service implementation detail
   - However: This is acceptable for infrastructure tests

3. **CSS Class Selector Instead of Semantic Locator**
   - `.sidebar-rail` is implementation-specific
   - Better: Use `getByRole('navigation')` or `getByTestId('sidebar')`
   - Mitigation: This matches established pattern in fixture

### Modern Standards (2026) Evaluation

| Standard | Rating | Notes |
|----------|--------|-------|
| **User-Facing Locators** | ⚠️ Partial | CSS class `.sidebar-rail` vs. semantic alternatives |
| **Test Isolation** | ✅ Excellent | Uses `app.fixture` with worker-indexed DB |
| **Fixture Usage** | ✅ Excellent | Properly imports and leverages project fixture |
| **Async Handling** | ✅ Good | Uses `page.evaluate` for synchronous state check |
| **Documentation** | ✅ Excellent | Clear JSDoc explaining purpose and dependencies |

---

## 3. Test Value & Classification

### Scenario Relevance

**Infrastructure Smoke Test**: This is a **pre-flight check** rather than a user journey. It answers:
- "Is the app bootstrapping correctly?"
- "Is the database layer functional?"
- "Is the fixture working as expected?"

Real users would never consciously "verify sidebar visibility" — but developers/CI need this gate.

### Classification

| Aspect | Classification | Rationale |
|--------|---------------|-----------|
| **Test Type** | **Environmental Health Check** | Validates infrastructure, not user flows |
| **Layer Tested** | Angular Bootstrap + OPFS/SQLite | Framework initialization + storage layer |
| **Mocking Level** | None | Full stack verification |
| **CI Purpose** | **Gate Test** | Should run first; if it fails, skip entire suite |

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

```
[Fixture navigates to /?mode=browser&dbName=praxis-worker-N&resetdb=1]
     ↓
[Angular app bootstraps]
     ↓
[SqliteService initializes OPFS database]
     ↓
[App shell renders (.sidebar-rail visible)]
     ↓
[Welcome dialog dismissed (by fixture)]
     ↓
[Test asserts UI and service state]
     ↓
[✅ Pass = Environment is stable for subsequent tests]
```

### Contextual Fit

This test is the **foundation layer** of the E2E test pyramid:

```
                ┌───────────────────────────┐
                │  Full User Journeys       │  ← Depends on...
                ├───────────────────────────┤
                │  Feature-Specific Tests   │  ← Depends on...
                ├───────────────────────────┤
                │  Component Interaction    │  ← Depends on...
                ├───────────────────────────┤
         ▶▶▶    │  HEALTH CHECK (this)      │  ◀◀◀ Foundation
                └───────────────────────────┘
```

If the health check fails:
- Database isolation is broken
- App bootstrap failed
- No point running other E2E tests

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Severity | Description |
|-----|----------|-------------|
| **Definition Loading** | Low | Could verify seed data exists (e.g., `protocol_definitions` count > 0) |
| **Pyodide Bootstrap** | Medium | No verification that Pyodide worker initializes |
| **Network Layer** | Low | No API health check (appropriate for browser-mode) |

### Domain Specifics

#### Data Integrity

| Aspect | Status | Details |
|--------|--------|---------|
| **DB Schema Valid** | ⚠️ Implicit | `isReady$` only confirms initialization, not schema integrity |
| **Seed Data Present** | ❌ Not Verified | Could add: `SELECT COUNT(*) FROM protocol_definitions` |

#### Simulation vs. Reality

| Aspect | Status | Details |
|--------|--------|---------|
| **Mode Detection** | ⚠️ Implicit | Fixture sets `mode=browser` but test doesn't verify |

#### Serialization

Not applicable for this infrastructure test.

#### Error Handling

| Aspect | Status | Details |
|--------|--------|---------|
| **DB Init Failure** | ⚠️ Timeout | If DB fails, test times out after 30000ms |
| **App Bootstrap Failure** | ⚠️ Timeout | If Angular crashes, `.sidebar-rail` never appears |

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 8/10 | Focused, clear purpose |
| **Best Practices** | 8/10 | Uses fixture correctly, good documentation |
| **Test Value** | 9/10 | Critical gate test for CI pipeline |
| **Isolation** | 10/10 | Proper worker-indexed DB via fixture |
| **Domain Coverage** | 5/10 | Limited to bootstrap, no seed data verification |

**Overall**: **8.0/10**

---

## Recommendations

### Quick Wins

1. **Add Seed Data Verification** (5 min):
   ```typescript
   const protocolCount = await page.evaluate(async () => {
       const db = await (window as any).sqliteService.getDatabase();
       const result = db.exec("SELECT COUNT(*) FROM protocol_definitions");
       return result[0]?.values[0]?.[0] || 0;
   });
   expect(protocolCount).toBeGreaterThan(0);
   ```

2. **Add Mode Verification** (2 min):
   ```typescript
   const isBrowserMode = await page.evaluate(() => {
       return (window as any).modeService?.isBrowserMode?.() ?? false;
   });
   expect(isBrowserMode).toBe(true);
   ```

### Stretch Goals

3. **Pyodide Bootstrap Check**:
   ```typescript
   const pyodideReady = await page.evaluate(() => {
       return (window as any).pyodideService?.isReady$?.getValue() === true;
   });
   expect(pyodideReady).toBe(true);
   ```

---

## Files Reviewed

| File | Purpose | Lines |
|------|---------|-------|
| `e2e/specs/health-check.spec.ts` | Test spec | 36 |
| `e2e/fixtures/app.fixture.ts` | Fixture (used correctly) | 134 |
