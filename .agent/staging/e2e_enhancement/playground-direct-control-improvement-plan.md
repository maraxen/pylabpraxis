# E2E Enhancement Plan: playground-direct-control.spec.ts

**Target:** [playground-direct-control.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/playground-direct-control.spec.ts)  
**Baseline Score:** 5.6/10  
**Target Score:** 8.5/10  
**Effort Estimate:** ~3 hours

---

## Goals

1. **Isolation** — Enable parallel execution by removing `resetdb=1` and using `worker-db.fixture`.
2. **Abstraction** — Create/Use a `PlaygroundPage` POM to encapsulate playground interactions.
3. **Reliability** — Replace CSS selectors with user-facing locators.
4. **Deep Verification** — Inspect Pyodide/Service state to ensure hardware simulation actually started.

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Change import to `import { test, expect } from '../fixtures/worker-db.fixture';`
- [ ] Remove `resetdb=1` from the URL.
- [ ] Use `BasePage.goto()` to ensure `dbName` is properly appended (prevents SQLITE_BUSY).

### 1.2 Replace Implementation-Detail Locators
- [ ] Replace `.method-chip` with `page.getByRole('button', { name: methodRegex })`.
- [ ] Replace `.execute-btn` with `page.getByRole('button', { name: /execute/i })`.
- [ ] Replace `.command-result` check with specific text or ARIA state verification.

---

## Phase 2: Page Object Refactor

### 2.1 Playground POM
- [ ] Create `e2e/page-objects/playground.page.ts`.
- [ ] Add methods: `openInventory()`, `selectModule(moduleName)`, `executeCurrentMethod()`, `waitForSuccess()`.

---

## Phase 3: Domain Verification

### 3.1 Backend Instantiation Check
- [ ] Add verification that the backend has been correctly instantiated in the browser's memory:
  ```typescript
  const backendReady = await page.evaluate(() => {
    return (window as any).machineService?.getBackendInstance('Hamilton STAR') !== undefined;
  });
  expect(backendReady).toBe(true);
  ```

### 3.2 Result Details
- [ ] Instead of just checking for a primary-colored icon, verify the result text (e.g., "OK: Setup complete").

---

## Phase 4: Negative Testing

- [ ] Add a test case for "Backend Initialization Failure" by mocking a 500 response for the backend definition.
- [ ] Verify that the UI displays a meaningful error message in the playground instead of just hanging.

---

## Verification Plan

### Automated
```bash
# Run in parallel to verify worker isolation
npx playwright test e2e/specs/playground-direct-control.spec.ts --workers=4
```

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/playground-direct-control.spec.ts` | Refactor | ~80 lines |
| `e2e/page-objects/playground.page.ts` | Create | New file |

---

## Acceptance Criteria

- [ ] Zero occurrence of `force: true`.
- [ ] Parallel execution (workers > 1) passes consistently.
- [ ] Logic for method execution is abstracted into `PlaygroundPage`.
- [ ] Test verifies "Machine Service" state via `page.evaluate()`.
- [ ] Baseline score improves to ≥8.5/10.
