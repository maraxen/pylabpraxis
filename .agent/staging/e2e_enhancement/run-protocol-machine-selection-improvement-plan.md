# E2E Enhancement Plan: run-protocol-machine-selection.spec.ts

**Target:** [run-protocol-machine-selection.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/run-protocol-machine-selection.spec.ts)  
**Baseline Score:** 4.2/10  
**Target Score:** 8.0/10  
**Effort Estimate:** 3-4 hours

---

## Goals

1. **Reliability** — Eliminate flaky patterns (networkidle, .last() selectors)
2. **Isolation** — Enable parallel test execution via worker-indexed databases
3. **Domain Coverage** — Verify machine compatibility logic and state persistence
4. **Maintainability** — Leverage existing ProtocolPage and WizardPage POMs

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Replace import: `import { test, expect } from '@playwright/test'` → `import { test, expect } from '../fixtures/worker-db.fixture'`
- [ ] Use `gotoWithWorkerDb()` or `BasePage.goto()` for consistent initialization
- [ ] Remove manual `localStorage.clear()` from beforeEach (handled by `resetdb=1`)

**Before:**
```typescript
import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => {
        localStorage.clear();
        localStorage.setItem('praxis_mode', 'browser');
    });
});
```

**After:**
```typescript
import { test, expect, gotoWithWorkerDb } from '../fixtures/worker-db.fixture';

// No beforeEach needed - gotoWithWorkerDb handles isolation
```

### 1.2 Eliminate Flaky Wait Strategies
- [ ] Remove `waitUntil: 'networkidle'` (line 18)
- [ ] Replace with SQLite readiness wait (via fixture) + Angular state assertion

**Before:**
```typescript
await page.goto('/run-protocol?mode=browser', { waitUntil: 'networkidle' });
```

**After:**
```typescript
await gotoWithWorkerDb(page, '/run-protocol', testInfo, { waitForDb: true });
await protocolPage.protocolCards.first().waitFor({ state: 'visible' });
```

### 1.3 Replace Fragile Selectors
- [ ] Replace `.last()` button selections with scoped POM methods
- [ ] Replace `app-protocol-card` component selector with user-facing patterns

| Current | Replacement |
|---------|-------------|
| `page.locator('app-protocol-card').first()` | `protocolPage.protocolCards.first()` |
| `page.getByRole('button', { name: /Continue/i }).last()` | Scope within step container |
| `page.locator('[data-tour-id="run-step-machine"]')` | Acceptable (test-specific data attr) |

---

## Phase 2: Page Object Refactor

### 2.1 Migrate to Existing POMs

**File: `e2e/page-objects/protocol.page.ts`** already has:
- `selectFirstProtocol()` - handles protocol card selection
- `continueFromSelection()` - handles Continue button click

**File: `e2e/page-objects/wizard.page.ts`** should be extended with:
- `advanceToMachineStep()` - encapsulates stepper progression

**Refactored Test Structure:**
```typescript
import { test, expect } from '../fixtures/worker-db.fixture';
import { ProtocolPage } from '../page-objects/protocol.page';
import { WizardPage } from '../page-objects/wizard.page';

test.describe('Run Protocol - Machine Selection', () => {
    test('should navigate and select a simulated machine', async ({ page }, testInfo) => {
        const protocolPage = new ProtocolPage(page, testInfo);
        const wizardPage = new WizardPage(page, testInfo);
        
        await protocolPage.goto();
        await protocolPage.selectFirstProtocol();
        await wizardPage.completeParameterStep();
        
        // Machine selection assertions using wizard methods
        await wizardPage.verifyMachineStepVisible();
        await wizardPage.selectFirstSimulatedMachine();
        await wizardPage.verifyContinueEnabled();
    });
});
```

### 2.2 Extend WizardPage with Machine Selection Methods

**Add to `wizard.page.ts`:**
```typescript
async verifyMachineStepVisible(): Promise<void> {
    const machineStep = this.page.locator('[data-tour-id="run-step-machine"]');
    await expect(machineStep).toBeVisible();
    await expect(this.page.getByText(/Select Execution Machine/i)).toBeVisible();
}

async selectFirstSimulatedMachine(): Promise<void> {
    const machineCard = this.page
        .locator('app-machine-card')
        .filter({ hasText: /Simulated/i })
        .first();
    await machineCard.click();
    await expect(machineCard).toHaveClass(/border-primary|selected/);
}

async selectIncompatibleMachine(): Promise<void> {
    // For negative testing
    const incompatibleCard = this.page
        .locator('app-machine-card')
        .filter({ has: this.page.locator('[data-incompatible="true"]') })
        .first();
    await incompatibleCard.click();
}
```

---

## Phase 3: Domain Verification

### 3.1 Verify Machine Selection Persistence
- [ ] After selecting machine, verify selection is stored in Angular state
- [ ] Use `page.evaluate()` to inspect run state via `ng.getComponent()`

**Add verification:**
```typescript
async verifyMachineSelected(expectedAccessionId: string): Promise<void> {
    const selectedId = await this.page.evaluate(() => {
        const runStepComponent = document.querySelector('app-run-step-machine');
        if (!runStepComponent) return null;
        const component = (window as any).ng.getComponent(runStepComponent);
        return component?.selectedMachine?.machine?.accession_id;
    });
    expect(selectedId).toBe(expectedAccessionId);
}
```

### 3.2 Add Compatibility Edge Case Tests
- [ ] Test incompatible machine (should not select, show tooltip)
- [ ] Test physical mode blocking simulated machines

**New test cases:**
```typescript
test('should prevent selection of incompatible machine', async ({ page }, testInfo) => {
    // Setup: Load with a protocol that has specific requirements
    // Action: Click incompatible machine
    // Assert: Selection did not change, warning visible
});

test('should block simulated machines in physical mode', async ({ page }, testInfo) => {
    // Setup: Navigate with mode=physical (or without mode param)
    // Assert: Simulated machines show disabled state
    // Action: Click simulated machine
    // Assert: Selection blocked
});
```

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Empty Machine List
- [ ] Test scenario with no available machines
- [ ] Verify empty state UI displays correctly

### 4.2 Machine Fetch Failure
- [ ] Intercept machine list API and return error
- [ ] Verify graceful error handling

```typescript
test('should handle machine fetch failure gracefully', async ({ page }, testInfo) => {
    // Intercept and fail the machine list request
    await page.route('**/api/machines**', route => route.abort());
    
    // Navigate and advance to machine step
    // ...
    
    // Verify error state
    await expect(page.getByText(/Failed to load machines/i)).toBeVisible();
});
```

---

## Verification Plan

### Automated
```bash
# Single test verification
npx playwright test e2e/specs/run-protocol-machine-selection.spec.ts

# Parallel execution stress test (validates isolation)
npx playwright test e2e/specs/run-protocol-machine-selection.spec.ts --workers=4 --repeat-each=3

# Full run-protocol suite regression
npx playwright test e2e/specs/*protocol*.spec.ts --workers=4
```

### Manual Checklist
- [ ] Visual inspection of machine cards during test run
- [ ] Verify no console errors related to OPFS/database
- [ ] Confirm test works in both headed and headless modes

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/run-protocol-machine-selection.spec.ts` | Refactor | ~60 lines |
| `e2e/page-objects/wizard.page.ts` | Extend | +30 lines (machine methods) |
| `e2e/page-objects/protocol.page.ts` | No change | Reference only |

---

## Acceptance Criteria

- [ ] Tests pass with parallel execution (`--workers=4`)
- [ ] Zero `force: true` clicks
- [ ] Zero `waitForTimeout` calls
- [ ] Zero `.last()` selectors without step-scoping
- [ ] Uses `worker-db.fixture` import
- [ ] Uses ProtocolPage/WizardPage POMs
- [ ] Verifies machine selection state persistence
- [ ] Includes incompatible machine negative test
- [ ] Baseline score improves from 4.2 → ≥8.0/10

---

## Expected Score Improvement

| Category | Before | After | Delta |
|----------|--------|-------|-------|
| **Test Scope** | 6/10 | 8/10 | +2 (edge cases) |
| **Best Practices** | 3/10 | 9/10 | +6 (POM, fixture) |
| **Test Value** | 7/10 | 8/10 | +1 (negative tests) |
| **Isolation** | 2/10 | 9/10 | +7 (worker DB) |
| **Domain Coverage** | 3/10 | 7/10 | +4 (state verification) |
| **Overall** | **4.2/10** | **8.2/10** | **+4.0** |
