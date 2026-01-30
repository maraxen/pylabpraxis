# E2E Enhancement Plan: protocol-execution.spec.ts

**Target:** [protocol-execution.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/protocol-execution.spec.ts)  
**Baseline Score:** 6.4/10  
**Target Score:** 8.0/10  
**Effort Estimate:** Medium (2-3 hours)

---

## Goals

1. **Reliability** — Enable parallel test execution with worker isolation
2. **Isolation** — Use worker-indexed DB pattern
3. **Domain Coverage** — Verify data persistence and serialization
4. **Maintainability** — Remove silent error swallowing

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration

**Before:**
```typescript
test.beforeEach(async ({ page }) => {
    protocolPage = new ProtocolPage(page);
    await page.goto('/');
    // ... manual SQLite wait
});
```

**After:**
```typescript
import { test, expect } from '../fixtures/worker-db.fixture';

test.describe('Protocol Wizard Flow', () => {
    let protocolPage: ProtocolPage;

    test.beforeEach(async ({ page, testInfo }) => {
        protocolPage = new ProtocolPage(page);
        
        // Use BasePage.goto() which handles:
        // - mode=browser
        // - worker-indexed dbName
        // - resetdb=1
        // - SQLite ready wait
        await protocolPage.goto(testInfo);
        
        // Handle Welcome Dialog if present
        await page.getByRole('button', { name: /Skip for Now/i })
            .click({ timeout: 5000 })
            .catch(() => {}); // OK if not present
    });
});
```

### 1.2 Replace Silent Catches with Explicit Handling

**Before:**
```typescript
await page.waitForURL('**/app/home', { timeout: 15000 }).catch(() => {
    console.log('Did not redirect to /app/home automatically');
});
```

**After:**
```typescript
// Option 1: Make it an explicit assertion
await expect(page).toHaveURL(/\/app\/home/, { timeout: 15000 });

// Option 2: If truly optional, use soft assertion
await expect.soft(page).toHaveURL(/\/app\/home/, { timeout: 15000 });
```

### 1.3 Use Consistent Screenshot Path Structure

```typescript
const screenshotDir = `/tmp/e2e-protocol-${testInfo.workerIndex}`;
await page.screenshot({ path: `${screenshotDir}/01-protocol-library.png` });
```

---

## Phase 2: Page Object Refactor

### 2.1 Leverage BasePage.goto() in ProtocolPage

The `ProtocolPage` already extends `BasePage`. Ensure the test uses it:

```typescript
// ProtocolPage.goto() already waits for protocolCards
await protocolPage.goto(testInfo);
```

### 2.2 Remove Duplicate SQLite Wait Logic

The test manually waits for SQLite, but `BasePage.goto()` already does this:

```typescript
// DELETE this duplicate logic:
await page.waitForFunction(
    () => (window as any).sqliteService?.isReady$?.getValue() === true,
    null,
    { timeout: 30000 }
);
```

---

## Phase 3: Domain Verification

### 3.1 Verify Run Persisted in History

```typescript
await test.step('Verify Run in History', async () => {
    const monitor = new ExecutionMonitorPage(page);
    await monitor.navigateToHistory();
    
    // Verify the run we just executed exists
    const latestRow = monitor.historyTable.locator('tbody tr').first();
    await expect(latestRow).toBeVisible();
    
    // Verify it's for the protocol we ran
    await expect(latestRow).toContainText(/Simple Transfer|Protocol/i);
    
    // Verify status is completed
    await expect(latestRow).toContainText(/Completed|Succeeded/i);
});
```

### 3.2 Verify Simulation Mode Active

```typescript
await test.step('Confirm Simulation Mode', async () => {
    // Ensure we're in simulation mode
    await protocolPage.ensureSimulationMode();
    
    const simToggle = page.getByRole('button', { name: /^Simulation$/i });
    await expect(simToggle).toHaveAttribute('aria-pressed', 'true');
});
```

### 3.3 Deep State Verification via Angular

```typescript
await test.step('Verify Wizard State', async () => {
    const wizardState = await page.evaluate(() => {
        const wizard = (window as any).ng?.getComponent(
            document.querySelector('app-run-wizard')
        );
        return {
            currentStep: wizard?.currentStep,
            selectedProtocol: wizard?.selectedProtocolId,
            isValid: wizard?.isValid
        };
    });
    
    expect(wizardState.selectedProtocol).toBeTruthy();
    expect(wizardState.isValid).toBe(true);
});
```

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Add Failure Scenario Tests

```typescript
test.describe('Error Scenarios', () => {
    test('handles missing protocol gracefully', async ({ page }) => {
        await page.goto('/app/run?protocolId=non-existent&mode=browser');
        await expect(page.getByText(/Protocol not found|Error/i)).toBeVisible();
    });

    test('handles execution cancel', async ({ page }) => {
        // Start a long-running protocol
        await protocolPage.selectProtocol('Long Running Protocol');
        await protocolPage.advanceToReview();
        await protocolPage.startExecution();
        
        // Cancel mid-execution
        await page.getByRole('button', { name: /Cancel|Abort/i }).click();
        
        // Verify cancelled state
        const status = await protocolPage.getExecutionStatus();
        expect(status).toMatch(/Cancelled|Aborted/i);
    });
});
```

---

## Verification Plan

### Automated
```bash
# Single worker (debug)
npx playwright test e2e/specs/protocol-execution.spec.ts --workers=1

# Parallel (validates isolation)
npx playwright test e2e/specs/protocol-execution.spec.ts --workers=4

# With trace for debugging
npx playwright test e2e/specs/protocol-execution.spec.ts --trace=on
```

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/protocol-execution.spec.ts` | Refactor | ~101 → ~130 |

---

## Acceptance Criteria

- [ ] Tests pass with parallel execution (`--workers=4`)
- [ ] Uses `BasePage.goto()` for worker isolation
- [ ] No silent `.catch()` that swallows failures
- [ ] Verifies run persisted in history after execution
- [ ] Uses consistent screenshot naming
- [ ] Adds at least one failure scenario
- [ ] Baseline score improves to ≥8.0/10

---

## Priority Order

1. 🟠 **Add worker isolation** via BasePage.goto()
2. 🟠 **Remove duplicate SQLite wait logic**
3. 🟡 **Replace silent catches with soft assertions**
4. 🟡 **Add post-execution history verification**
5. 🟢 **Add simulation mode verification**
6. 🟢 **Add error scenario tests**

