# E2E Improvement Plan: `interactions/04-error-handling.spec.ts`

**Plan Date:** 2026-01-30  
**Priority:** High (Error Handling is Critical Path)  
**Current Score:** 5.0/10 (Functional Smoke)  
**Target Score:** 8.5/10 (Production Grade with Domain Coverage)

---

## Executive Summary

The current `04-error-handling.spec.ts` test file has significant gaps in actual error handling verification. Test 1 is mislabeled (tests log visibility, not failure states), and there is no coverage for Pyodide errors, serialization failures, or execution failures. This plan outlines a 4-phase remediation strategy to transform this into a robust error handling test suite.

---

## Phase 1: Infrastructure & Critical Fixes (Priority: Immediate)

### 1.1 Rename/Rewrite Mislabeled Test

**Current State:**
```typescript
test('should display error logs when a protocol execution fails', ...)
```

**Problem:** This test doesn't trigger or verify any failure.

**Action Items:**

| Task | Description | Effort |
|------|-------------|--------|
| **1.1.1** | Rename to `should display execution log panel during protocol run` | 5 min |
| **1.1.2** | Move to `interactions/02-execution-monitoring.spec.ts` or similar | 10 min |
| **1.1.3** | Create NEW test that actually triggers a protocol failure (see Phase 2) | 2-4 hrs |

### 1.2 Improve Locator Strategy

**Current Issues:**
- Line 40: `mat-card` filter by text
- Line 90: `mat-snack-bar-container` direct selector

**Recommended Changes:**

```typescript
// BEFORE (Line 40)
const logPanel = page.locator('mat-card').filter({ hasText: 'Execution Log' });

// AFTER: Use TestID or ARIA role
const logPanel = page.getByTestId('execution-log-panel')
    .or(page.getByRole('region', { name: /Execution Log/i }));
```

```typescript
// BEFORE (Line 90)
const snackBar = page.locator('mat-snack-bar-container');

// AFTER: Use ARIA role for announcements
const snackBar = page.getByRole('alert')
    .or(page.locator('mat-snack-bar-container'));
```

**Required App Changes:**
- Add `data-testid="execution-log-panel"` to the log card component
- Ensure Material SnackBar has `role="alert"` (default in Material 16+)

### 1.3 Verify Mock Route Was Triggered

**Current Issue (Test 3):** No confirmation that the mocked 500 route was actually hit.

```typescript
// BEFORE
await page.route('**/api/v1/protocols*', route => route.fulfill({...}));
await protocolPage.goto();
await expect(snackBar).toBeVisible({ timeout: 10000 });

// AFTER: Confirm the route was intercepted
let routeTriggered = false;
await page.route('**/api/v1/protocols*', async route => {
    routeTriggered = true;
    await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
    });
});

await protocolPage.goto();

// Assert route was triggered
expect(routeTriggered).toBe(true);
await expect(snackBar).toBeVisible({ timeout: 10000 });
```

---

## Phase 2: Real Error State Testing (Priority: High)

### 2.1 New Test: Protocol Execution Fails with FAILED Status

**Goal:** Trigger an actual execution failure and verify UI reflects the error state.

**Implementation Strategy:**
1. Use a mock protocol or inject a Python syntax error
2. Alternatively, use `page.evaluate` to call a service method that triggers failure

```typescript
test('should show FAILED status when protocol execution errors', async ({ page }) => {
    const protocolPage = new ProtocolPage(page);
    const wizardPage = new WizardPage(page);
    const monitorPage = new ExecutionMonitorPage(page);

    // Setup: Start normal execution
    await protocolPage.goto();
    await protocolPage.ensureSimulationMode();
    await protocolPage.selectFirstProtocol();
    await protocolPage.continueFromSelection();
    
    await wizardPage.completeParameterStep();
    await wizardPage.selectFirstCompatibleMachine();
    await wizardPage.waitForAssetsAutoConfigured();
    await wizardPage.advanceDeckSetup();
    await wizardPage.openReviewStep();
    
    // Inject failure before start
    await page.evaluate(() => {
        const executionService = (window as any).executionService;
        // Trigger a simulated error after N steps
        executionService?.setSimulationErrorAfterSteps?.(3);
    });

    await wizardPage.startExecution();
    await monitorPage.waitForLiveDashboard();

    // Wait for FAILED status
    await monitorPage.waitForStatus(/FAILED|ERROR/, 120000);

    // Verify error is displayed in logs
    const logPanel = page.getByTestId('execution-log-panel');
    await expect(logPanel).toContainText(/error|exception|failed/i);

    // Verify error notification appeared
    const errorNotification = page.getByRole('alert');
    await expect(errorNotification).toBeVisible();
});
```

### 2.2 New Test: Pyodide Initialization Failure

**Goal:** Verify graceful degradation when Pyodide fails to load.

```typescript
test('should show error when Pyodide fails to initialize', async ({ page }) => {
    // Block Pyodide core files
    await page.route('**/*pyodide*.wasm', route => route.abort('failed'));
    await page.route('**/*pyodide*.js', route => route.abort('failed'));

    const welcomePage = new WelcomePage(page);
    await welcomePage.goto();
    await welcomePage.handleSplashScreen();

    // Navigate to a feature that requires Pyodide
    await page.getByRole('link', { name: /Playground|Direct Control/i }).click();

    // Verify error state
    const errorMessage = page.getByRole('alert')
        .or(page.locator('.error-state, .pyodide-error'));
    await expect(errorMessage).toBeVisible({ timeout: 30000 });
    await expect(errorMessage).toContainText(/failed to load|initialization error|python/i);
});
```

### 2.3 New Test: Serialization Error Handling

**Goal:** Verify errors when protocol arguments cannot be serialized.

```typescript
test('should show error for invalid protocol parameters', async ({ page }) => {
    const protocolPage = new ProtocolPage(page);

    await protocolPage.goto();
    await protocolPage.ensureSimulationMode();
    await protocolPage.selectProtocolByName('SomeProtocolWithRequiredParams');
    await protocolPage.continueFromSelection();

    // Enter invalid value in a parameter field
    await page.getByLabel(/Volume|Amount/i).fill('INVALID_NOT_A_NUMBER');

    // Attempt to continue
    const continueButton = page.getByRole('button', { name: /Continue/i });
    await continueButton.click();

    // Verify validation error
    const validationError = page.locator('mat-error')
        .or(page.getByRole('alert', { name: /validation/i }));
    await expect(validationError).toBeVisible();
    await expect(validationError).toContainText(/invalid|must be/i);
});
```

---

## Phase 3: Network Resilience Testing (Priority: Medium)

### 3.1 HTTP 500 on Execution Start

```typescript
test('should show error when execution start fails', async ({ page }) => {
    await page.route('**/api/v1/runs', route => {
        if (route.request().method() === 'POST') {
            return route.fulfill({
                status: 500,
                body: JSON.stringify({ error: 'Execution service unavailable' })
            });
        }
        return route.continue();
    });

    // ... navigate through wizard to start execution ...

    const errorToast = page.getByRole('alert');
    await expect(errorToast).toBeVisible();
    await expect(errorToast).toContainText(/failed to start|unavailable/i);
});
```

### 3.2 Network Timeout During Execution

```typescript
test('should handle network timeout during status polling', async ({ page }) => {
    // Start execution normally
    // ... (wizard flow) ...

    // After execution starts, block status endpoint
    await page.route('**/api/v1/runs/*/status', route => {
        // Never respond (simulate hang)
        return new Promise(() => {});
    });

    // Verify reconnection UI or timeout message
    const connectionWarning = page.locator('.connection-warning, .status-error');
    await expect(connectionWarning).toBeVisible({ timeout: 60000 });
});
```

### 3.3 WebSocket Disconnect Recovery

```typescript
test('should reconnect when live execution feed disconnects', async ({ page }) => {
    // This requires app-level support for connection status indication
    // Placeholder for when live connection feature is implemented
});
```

---

## Phase 4: Database & State Error Handling (Priority: Medium)

### 4.1 SQLite/OPFS Initialization Failure

```typescript
test('should gracefully handle database initialization failure', async ({ page }) => {
    // Corrupt the OPFS or block WASM
    await page.route('**/*sql-wasm*.wasm', route => route.abort('failed'));

    const welcomePage = new WelcomePage(page);
    await welcomePage.goto();

    // Check for fallback behavior or error message
    const dbError = page.getByRole('alert');
    await expect(dbError).toBeVisible({ timeout: 30000 });
    await expect(dbError).toContainText(/database|storage|offline/i);
});
```

### 4.2 Invalid Database Schema

```typescript
test('should show error for incompatible database version', async ({ page }) => {
    // Pre-seed an old/invalid DB schema via evaluate
    await page.evaluate(() => {
        localStorage.setItem('praxis_db_version', '0.0.1-invalid');
    });

    await page.goto('/?mode=browser');

    // Verify migration error or prompt for reset
    const migrationError = page.locator('.migration-error, .schema-error');
    await expect(migrationError).toBeVisible({ timeout: 30000 });
});
```

---

## Implementation Checklist

### Phase 1: Infrastructure (Week 1)
- [ ] Rename Test 1 to accurately reflect its purpose
- [ ] Move Test 1 to execution-monitoring suite
- [ ] Add `data-testid` to log panel component
- [ ] Update snackbar selector to use ARIA role
- [ ] Add route verification to Test 3

### Phase 2: Real Errors (Week 2)
- [ ] Create `ExecutionService.setSimulationErrorAfterSteps()` helper
- [ ] Implement Test: FAILED execution status
- [ ] Implement Test: Pyodide initialization failure
- [ ] Implement Test: Parameter validation errors

### Phase 3: Network (Week 3)
- [ ] Implement Test: Execution start 500
- [ ] Implement Test: Network timeout on polling
- [ ] Document WebSocket recovery requirements

### Phase 4: Database (Week 4)
- [ ] Implement Test: OPFS/WASM initialization failure
- [ ] Implement Test: Schema version mismatch
- [ ] Add migration error UI component if missing

---

## Updated Test File Structure

```
e2e/specs/interactions/
├── 01-execution-controls.spec.ts
├── 02-execution-monitoring.spec.ts  # <-- Move log visibility test here
├── 03-navigation-stability.spec.ts
└── 04-error-handling.spec.ts        # <-- Rewrite with real error tests
    ├── describe('HTTP Error Handling')
    │   ├── test('backend 500 on protocol list')
    │   ├── test('backend 500 on execution start')
    │   └── test('network timeout handling')
    ├── describe('Execution Error Handling')
    │   ├── test('protocol failure shows FAILED status')
    │   └── test('validation errors block progression')
    └── describe('Infrastructure Error Handling')
        ├── test('Pyodide initialization failure')
        └── test('database initialization failure')
```

---

## Success Metrics

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Test Cases | 3 | 10+ | ✅ |
| Error Types Covered | 1 (HTTP 500) | 6+ | ✅ |
| Misleading Tests | 1 | 0 | ✅ |
| User-Facing Locators | 0% | 80%+ | ✅ |
| Aggregate Score | 5.0/10 | 8.5/10 | ✅ |

---

## Dependencies

| Dependency | Status | Owner |
|------------|--------|-------|
| `data-testid` on log panel | Required | Frontend |
| Execution error injection API | Required | Backend/Simulation |
| Connection status indicator | Nice-to-have | Frontend |
| Migration error UI | If missing | Frontend |

---

*Plan generated following Senior SDET Improvement Process v2.0*
