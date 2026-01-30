# E2E Enhancement Plan: interactions/01-execution-controls.spec.ts

**Target:** [interactions/01-execution-controls.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/interactions/01-execution-controls.spec.ts)  
**Baseline Score:** 6.2/10  
**Target Score:** 8.5/10  
**Effort Estimate:** 4-6 hours

---

## Goals

1. **Reliability** — Eliminate `.first()` proliferation and timing-dependent failures
2. **Isolation** — Enable parallel test execution via worker-indexed DB
3. **Domain Coverage** — Verify run history persistence and execution state
4. **Maintainability** — Extract shared wizard setup into fixture

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Transition to `worker-db.fixture` pattern
- [ ] Update `beforeEach` to use `test.extend` with `testInfo` injection
- [ ] Use `BasePage.goto()` with worker index for database isolation

**Implementation:**
```typescript
// Before:
test.beforeEach(async ({ page }) => {
    const welcomePage = new WelcomePage(page);
    
// After:
import { test } from '../fixtures/worker-db.fixture';

test.beforeEach(async ({ page, testInfo }) => {
    const welcomePage = new WelcomePage(page, testInfo);
```

### 1.2 Extract Shared Wizard Setup
- [ ] Create fixture `preparedSimulationRun` that returns `{ monitorPage, protocolName }`
- [ ] Reduce test complexity to focus solely on control interactions

**Implementation:**
```typescript
// e2e/fixtures/execution-ready.fixture.ts
export const executionReadyFixture = test.extend({
    executionReady: async ({ page, testInfo }, use) => {
        const welcome = new WelcomePage(page, testInfo);
        await welcome.goto();
        await welcome.handleSplashScreen();
        
        const protocol = new ProtocolPage(page);
        await protocol.goto();
        await protocol.ensureSimulationMode();
        const protocolName = await protocol.selectFirstProtocol();
        await protocol.continueFromSelection();
        
        const wizard = new WizardPage(page);
        await wizard.completeParameterStep();
        await wizard.selectFirstCompatibleMachine();
        await wizard.waitForAssetsAutoConfigured();
        await wizard.advanceDeckSetup();
        await wizard.openReviewStep();
        await wizard.startExecution();
        
        const monitor = new ExecutionMonitorPage(page);
        await monitor.waitForLiveDashboard();
        
        await use({ monitorPage: monitor, protocolName });
    }
});
```

### 1.3 Eliminate Hardcoded Timeouts
- [ ] Centralize timeout constants in `e2e/config/timeouts.ts`
- [ ] Use config values for button visibility waits

**Implementation:**
```typescript
// e2e/config/timeouts.ts
export const TIMEOUTS = {
    BUTTON_VISIBLE: 15_000,
    STATUS_CHANGE: 30_000,
    DIALOG_APPEAR: 2_000,
};

// In test:
await expect(pauseBtn).toBeVisible({ timeout: TIMEOUTS.BUTTON_VISIBLE });
```

---

## Phase 2: Locator Refinement

### 2.1 Remove `.first()` Anti-Pattern
- [ ] Audit all `.first()` calls and replace with unique locators

| Current | Proposed |
|---------|----------|
| `getByRole('button', { name: /pause/i }).first()` | `getByTestId('pause-execution-btn')` or verify single match |
| `getByRole('button', { name: /resume/i }).first()` | `getByTestId('resume-execution-btn')` |
| `getByRole('button', { name: /confirm/i }).first()` | Scope to dialog: `dialog.getByRole('button', { name: /confirm/i })` |

### 2.2 Add Test Data Attributes (Component Change)
If test IDs don't exist, recommend adding to component:
```html
<!-- execution-monitor.component.html -->
<button mat-raised-button 
        (click)="pauseRun()"
        data-testid="pause-execution-btn">
    Pause
</button>
```

---

## Phase 3: Domain Verification

### 3.1 Progress-Based Pause Timing
- [ ] Wait for execution progress before attempting pause
- [ ] Avoid race condition where simulation completes before pause

**Implementation:**
```typescript
// Ensure run is actually running before pause:
await monitorPage.waitForStatus(/RUNNING/);
await monitorPage.waitForProgressAtLeast(5); // At least 5% complete

// Then attempt pause
const pauseBtn = page.getByTestId('pause-execution-btn');
await pauseBtn.click();
```

### 3.2 Post-Abort History Verification
- [ ] Verify aborted run appears in run history with correct status
- [ ] Validate data persisted to SQLite (not just UI state)

**Implementation:**
```typescript
test('should abort a simulated run', async ({ page }) => {
    // ... existing abort logic ...
    
    await monitorPage.waitForStatus(/CANCELLED|FAILED/);
    
    // NEW: Verify persistence
    await monitorPage.navigateToHistory();
    const row = await monitorPage.waitForHistoryRow(protocolName);
    await expect(row).toContainText(/CANCELLED|ABORTED/);
});
```

### 3.3 Button State Verification
- [ ] Assert button disabled states during transitions

**Implementation:**
```typescript
await pauseBtn.click();
// Pause button should become disabled or hidden during transition
await expect(pauseBtn).toBeDisabled({ timeout: 2000 }).catch(() => {
    // Some UIs hide rather than disable
    await expect(pauseBtn).not.toBeVisible();
});
await monitorPage.waitForStatus(/PAUSED/);
```

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Abort During Pause State
- [ ] Test: Pause run, then abort while paused

```typescript
test('should abort a paused run', async ({ executionReady }) => {
    const { monitorPage, page } = executionReady;
    
    await page.getByTestId('pause-execution-btn').click();
    await monitorPage.waitForStatus(/PAUSED/);
    
    await page.getByTestId('abort-execution-btn').click();
    await monitorPage.waitForStatus(/CANCELLED/);
});
```

### 4.2 Rapid Button Clicks
- [ ] Test: Click pause twice rapidly (debounce protection)

```typescript
test('should handle rapid pause clicks gracefully', async ({ executionReady }) => {
    const { monitorPage, page } = executionReady;
    const pauseBtn = page.getByTestId('pause-execution-btn');
    
    // Rapid double-click
    await pauseBtn.dblclick();
    
    // Should still end up in PAUSED state, not throw
    await monitorPage.waitForStatus(/PAUSED/);
});
```

---

## Verification Plan

### Automated
```bash
# Single worker (baseline)
npx playwright test e2e/specs/interactions/01-execution-controls.spec.ts

# Parallel execution (isolation test)
npx playwright test e2e/specs/interactions/01-execution-controls.spec.ts --workers=4 --repeat-each=3

# Headed debug for timing issues
npx playwright test e2e/specs/interactions/01-execution-controls.spec.ts --headed --timeout=120000
```

### Manual Verification
- [ ] Run test 10x consecutively to check flakiness
- [ ] Inspect Playwright trace for any timeout warnings
- [ ] Verify run history table contains aborted runs after test

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/interactions/01-execution-controls.spec.ts` | Refactor | ~60 lines |
| `e2e/fixtures/execution-ready.fixture.ts` | Create | ~40 lines |
| `e2e/config/timeouts.ts` | Create | ~15 lines |
| `execution-monitor.component.html` (optional) | Add test IDs | ~5 lines |

---

## Acceptance Criteria

- [ ] Tests pass with parallel execution (`--workers=4`)
- [ ] Zero `.first()` calls in test file
- [ ] Zero hardcoded timeout values (use config)
- [ ] Uses `worker-db.fixture` for isolation
- [ ] Verifies run history persistence after abort
- [ ] Baseline score improves from 6.2 → ≥8.5/10

---

## Priority Matrix

| Task | Impact | Effort | Priority |
|------|--------|--------|----------|
| Worker isolation fixture | High | Low | P0 |
| Extract shared wizard setup | High | Medium | P0 |
| Centralize timeouts | Medium | Low | P1 |
| Remove `.first()` calls | Medium | Low | P1 |
| Post-abort history check | High | Low | P1 |
| Button state assertions | Medium | Medium | P2 |
| Rapid click edge case | Low | Low | P3 |
