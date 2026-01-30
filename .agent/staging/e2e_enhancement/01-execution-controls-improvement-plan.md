# E2E Enhancement Plan: 01-execution-controls.spec.ts

**Target:** [01-execution-controls.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/interactions/01-execution-controls.spec.ts)  
**Baseline Score:** 6.4/10  
**Target Score:** 8.5/10  
**Effort Estimate:** 3-4 hours

---

## Goals

1. **Reliability** — Enable parallel execution with worker-indexed DB isolation
2. **Isolation** — Add explicit teardown to terminate orphaned executions
3. **Domain Coverage** — Verify state persistence and telemetry continuity
4. **Maintainability** — Extract repeated wizard flow to shared helper

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Import custom fixture from `e2e/fixtures/worker-db.fixture.ts` (or create if missing)
- [ ] Replace `test` import with `test.extend()` fixture pattern
- [ ] Pass `testInfo` to all Page Object constructors for DB isolation

**Before:**
```typescript
import { test, expect } from '@playwright/test';
// ...
const welcomePage = new WelcomePage(page);
```

**After:**
```typescript
import { test } from '../fixtures/worker-db.fixture';
// ...
const welcomePage = new WelcomePage(page, testInfo);
```

### 1.2 Add Explicit Cleanup
- [ ] Add `afterEach` hook to terminate any running execution
- [ ] Use `monitorPage.forceAbort()` helper if execution is still active

```typescript
test.afterEach(async ({ page }) => {
    // Force abort any running execution to prevent state leakage
    const abortBtn = page.getByRole('button', { name: /stop|abort/i });
    if (await abortBtn.isVisible({ timeout: 1000 }).catch(() => false)) {
        await abortBtn.click();
        const confirmBtn = page.getByRole('button', { name: /confirm|yes/i });
        if (await confirmBtn.isVisible({ timeout: 1000 }).catch(() => false)) {
            await confirmBtn.click();
        }
    }
});
```

### 1.3 Simplify Abort Button Selector
- [ ] Remove redundant `.filter()` call on abort button

**Before:**
```typescript
const abortBtn = page.getByRole('button', { name: /stop|abort|cancel/i })
    .filter({ hasText: /Stop|Abort|Cancel/i }).first();
```

**After:**
```typescript
const abortBtn = page.getByRole('button', { name: /stop|abort|cancel/i }).first();
```

---

## Phase 2: Extract Shared Helpers (Maintainability)

### 2.1 Create `launchExecutionFromWizard()` Helper
- [ ] Extract the 10-line wizard flow into a reusable utility
- [ ] Add to `wizard.page.ts` or create `e2e/helpers/wizard.helper.ts`

```typescript
// e2e/helpers/wizard.helper.ts
export async function launchSimulatedExecution(
    page: Page,
    options?: { protocolName?: string }
): Promise<void> {
    const protocolPage = new ProtocolPage(page);
    const wizardPage = new WizardPage(page);

    await protocolPage.goto();
    await protocolPage.ensureSimulationMode();
    
    if (options?.protocolName) {
        await protocolPage.selectProtocolByName(options.protocolName);
    } else {
        await protocolPage.selectFirstProtocol();
    }
    await protocolPage.continueFromSelection();
    
    await wizardPage.completeParameterStep();
    await wizardPage.selectFirstCompatibleMachine();
    await wizardPage.waitForAssetsAutoConfigured();
    await wizardPage.advanceDeckSetup();
    await wizardPage.openReviewStep();
    await wizardPage.startExecution();
}
```

### 2.2 Refactor Tests to Use Helper
- [ ] Replace duplicate wizard code in both tests
- [ ] Reduce test body from ~30 lines to ~15 lines each

---

## Phase 3: Domain Verification (Coverage)

### 3.1 Progress Persistence During Pause
- [ ] Before pause: Capture progress value
- [ ] After resume: Verify progress >= previous value

```typescript
// Capture progress before pause
const progressBefore = await page.locator('mat-progress-bar')
    .getAttribute('aria-valuenow');

// ... pause and resume ...

// Verify progress maintained or advanced
const progressAfter = await page.locator('mat-progress-bar')
    .getAttribute('aria-valuenow');
expect(Number(progressAfter)).toBeGreaterThanOrEqual(Number(progressBefore));
```

### 3.2 Button State Verification
- [ ] After pause: Verify Pause button hidden/disabled
- [ ] After resume: Verify Resume button hidden/disabled

```typescript
await pauseBtn.click();
await expect(pauseBtn).toBeHidden({ timeout: 5000 });  // or .toBeDisabled()
```

### 3.3 Run History Verification (Post-Abort)
- [ ] After abort: Navigate to `/app/monitor`
- [ ] Verify run appears in history table with `CANCELLED` status

```typescript
await monitorPage.navigateToHistory();
const row = await monitorPage.waitForHistoryRow(runName);
await expect(row).toContainText(/CANCELLED|ABORTED/i);
```

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Abort Rejection Flow
- [ ] Add test: Click Abort → Cancel confirmation → Verify still RUNNING

```typescript
test('should continue running when abort is cancelled', async ({ page }) => {
    // ... launch execution ...
    await abortBtn.click();
    const cancelBtn = page.getByRole('button', { name: /cancel|no|nevermind/i });
    await cancelBtn.click();
    await monitorPage.waitForStatus(/RUNNING/);
});
```

### 4.2 Abort During Pause
- [ ] Add test: Pause → Abort → Verify CANCELLED

```typescript
test('should allow abort while paused', async ({ page }) => {
    // ... launch and pause ...
    await abortBtn.click();
    // Handle confirmation
    await monitorPage.waitForStatus(/CANCELLED|FAILED/);
});
```

---

## Verification Plan

### Automated
```bash
# Run with parallel workers to validate isolation
npx playwright test e2e/specs/interactions/01-execution-controls.spec.ts --workers=4

# Run with tracing for debugging
npx playwright test e2e/specs/interactions/01-execution-controls.spec.ts --trace=on
```

### Manual Checklist
- [ ] Verify no `force: true` clicks remain
- [ ] Verify no `waitForTimeout` calls remain  
- [ ] Confirm all 4 parallel workers use distinct DBs (check console logs)
- [ ] Verify run history reflects test executions

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/interactions/01-execution-controls.spec.ts` | Refactor | ~60 → ~50 |
| `e2e/helpers/wizard.helper.ts` | Create | +30 |
| `e2e/fixtures/worker-db.fixture.ts` | Update or verify | +5 |
| `e2e/page-objects/monitor.page.ts` | Add `forceAbort()` | +10 |

---

## Acceptance Criteria

- [ ] Tests pass with `--workers=4` (parallel execution)
- [ ] Zero `force: true` clicks
- [ ] Zero `waitForTimeout` calls
- [ ] Uses worker-indexed DB fixture
- [ ] Wizard flow extracted to shared helper
- [ ] Post-pause progress verification added
- [ ] Run history verification added (abort test)
- [ ] Baseline score improves from 6.4 → ≥8.5/10

---

## Priority Matrix

| Task | Effort | Impact | Priority |
|------|--------|--------|----------|
| Worker isolation integration | 30 min | High | **P0** |
| Add afterEach cleanup | 15 min | Medium | **P1** |
| Extract wizard helper | 45 min | Medium | **P1** |
| Progress persistence check | 30 min | High | **P1** |
| Simplify abort selector | 5 min | Low | **P2** |
| Run history verification | 45 min | Medium | **P2** |
| Abort rejection test | 30 min | Medium | **P3** |
| Abort during pause test | 20 min | Low | **P3** |

**Total Estimated Effort:** 3-4 hours
