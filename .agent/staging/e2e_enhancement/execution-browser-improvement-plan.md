# E2E Enhancement Plan: execution-browser.spec.ts

**Target:** [execution-browser.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/execution-browser.spec.ts)  
**Baseline Score:** 2.2/10  
**Target Score:** 8.0/10  
**Effort Estimate:** 4-6 hours

---

## Goals

1. **Reliability** — Eliminate swallowed errors and flaky conditional patterns
2. **Isolation** — Enable parallel test execution with worker-indexed DBs
3. **Domain Coverage** — Verify actual protocol selection, machine assignment, and execution state
4. **Maintainability** — Introduce RunProtocolPage POM for wizard interactions

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Import from `fixtures/worker-db.fixture` instead of `@playwright/test`
- [ ] Use `gotoWithWorkerDb(page, '/app/run', testInfo)` for navigation
- [ ] Remove manual `waitForURL` + `waitForFunction` SQLite checks (handled by fixture)

### 1.2 Eliminate Swallowed Errors
- [ ] **Remove all `.catch(() => {})` patterns** on assertions (lines 115-118, 150-155)
- [ ] Replace `if (await x.isVisible().catch(() => false))` with deterministic `expect().toBeVisible()`
- [ ] If element presence is truly optional, use `test.skip()` with a clear reason

### 1.3 Eliminate Hardcoded Waits
| Current | Replacement |
|---------|-------------|
| `waitForTimeout(500)` after Continue | `expect(page.locator('.mat-step-content.ng-animating')).not.toBeVisible()` |
| `waitForTimeout(300)` after machine click | Wait for `selected()?.machine?.accession_id` change via `waitForFunction` |
| `waitForTimeout(500)` in loop | Use stepper index assertion: `expect(stepper).toHaveAttribute('aria-selected', 'true')` |

### 1.4 Remove Conditional Action Logic
**Before:**
```typescript
if (await protocolCard.isVisible({ timeout: 5000 }).catch(() => false)) {
    await protocolCard.click();
}
```

**After:**
```typescript
await expect(protocolCard).toBeVisible({ timeout: 10000 });
await protocolCard.click();
```

---

## Phase 2: Page Object Refactor

### 2.1 Create RunProtocolPage POM

**New File:** `e2e/pages/run-protocol.page.ts`

```typescript
import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class RunProtocolPage extends BasePage {
    constructor(page: Page) {
        super(page, '/app/run');
    }

    // === Locators ===
    get protocolCards(): Locator {
        return this.page.locator('app-protocol-card');
    }

    get continueButton(): Locator {
        return this.page.getByRole('button', { name: /Continue/i });
    }

    get startExecutionButton(): Locator {
        return this.page.getByRole('button', { name: /Start Execution/i });
    }

    get machineSelection(): Locator {
        return this.page.locator('app-machine-selection');
    }

    get stepper(): Locator {
        return this.page.locator('mat-stepper');
    }

    // === Actions ===
    async selectFirstProtocol(): Promise<void> {
        const card = this.protocolCards.first();
        await expect(card).toBeVisible({ timeout: 15000 });
        await card.click();
        // Wait for stepper to advance
        await this.waitForStepperAnimation();
    }

    async advanceStep(): Promise<void> {
        await expect(this.continueButton).toBeEnabled();
        await this.continueButton.click();
        await this.waitForStepperAnimation();
    }

    async selectFirstMachine(): Promise<void> {
        const machineCard = this.machineSelection.locator('app-machine-card').first();
        await expect(machineCard).toBeVisible();
        await machineCard.click();
    }

    async startExecution(): Promise<void> {
        await expect(this.startExecutionButton).toBeEnabled({ timeout: 10000 });
        await this.startExecutionButton.click();
    }

    // === Waiters ===
    async waitForStepperAnimation(): Promise<void> {
        // Wait for Angular animation to complete
        await this.page.waitForFunction(() => {
            const animating = document.querySelector('.mat-step-content.ng-animating');
            return !animating;
        }, null, { timeout: 5000 });
    }

    async waitForProtocolsLoaded(): Promise<void> {
        await expect(this.protocolCards.first()).toBeVisible({ timeout: 15000 });
    }

    // === Assertions ===
    async expectExecutionStarted(): Promise<void> {
        await expect(
            this.page.locator('mat-spinner').or(this.page.getByText('Initializing'))
        ).toBeVisible({ timeout: 10000 });
    }

    async expectSimulationMachineVisible(): Promise<void> {
        await expect(
            this.page.getByText(/Simulation Machine|sim-machine/i)
        ).toBeVisible({ timeout: 5000 });
    }
}
```

### 2.2 Refactor Test to Use POM

```typescript
import { test, expect, gotoWithWorkerDb } from '../fixtures/worker-db.fixture';
import { RunProtocolPage } from '../pages/run-protocol.page';

test.describe('Browser Mode Execution', () => {
    test('should start protocol execution in browser mode', async ({ page }, testInfo) => {
        await gotoWithWorkerDb(page, '/', testInfo);
        
        const runPage = new RunProtocolPage(page);
        await runPage.goto();
        await runPage.waitForProtocolsLoaded();
        
        await runPage.selectFirstProtocol();
        await runPage.advanceStep(); // Machine selection
        await runPage.selectFirstMachine();
        await runPage.advanceStep(); // Deck setup (or skip)
        await runPage.advanceStep(); // Review
        
        await runPage.startExecution();
        await runPage.expectExecutionStarted();
    });
});
```

---

## Phase 3: Domain Verification

### 3.1 Protocol Selection Verification
- [ ] After selecting a protocol, assert on the protocol name/ID in the wizard header
- [ ] Use `page.evaluate()` to read `wizardStateService.selectedProtocol()` signal value

### 3.2 Machine Selection Verification
- [ ] Assert the selected machine card shows "selected" state (check for class or attribute)
- [ ] Verify `isSimulated()` returns the expected value for browser mode

### 3.3 Execution State Verification
- [ ] After clicking "Start Execution", verify Angular store state changes:
```typescript
await page.waitForFunction(() => {
    const appStore = (window as any).appStore;
    return appStore?.executionState() === 'running' || appStore?.executionState() === 'initializing';
});
```
- [ ] Alternatively, mock the Pyodide worker and verify the call payload

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Empty Protocol List
```typescript
test('should show empty state when no protocols available', async ({ page }, testInfo) => {
    // Navigate with special flag or mock to simulate empty DB
    await gotoWithWorkerDb(page, '/?mockEmptyProtocols=1', testInfo);
    
    const runPage = new RunProtocolPage(page);
    await runPage.goto();
    
    await expect(page.getByText(/No protocols found/i)).toBeVisible();
});
```

### 4.2 Disabled Start Button (Deck Setup Required)
```typescript
test('should disable Start Execution when deck setup incomplete', async ({ page }, testInfo) => {
    // Skip deck setup step
    const runPage = new RunProtocolPage(page);
    // ... navigate to review without deck setup ...
    
    await expect(runPage.startExecutionButton).toBeDisabled();
    await expect(page.getByText(/Deck setup required/i)).toBeVisible();
});
```

### 4.3 Execution Failure
- [ ] Mock Pyodide worker to return error
- [ ] Verify error snackbar or dialog appears

---

## Verification Plan

### Automated
```bash
# Single test
npx playwright test e2e/specs/execution-browser.spec.ts --workers=1

# Parallel verification (after Phase 1)
npx playwright test e2e/specs/execution-browser.spec.ts --workers=4
```

### Manual Checklist
- [ ] Tests pass with `--workers=4`
- [ ] No console errors during test run
- [ ] Screenshots capture meaningful state transitions

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/execution-browser.spec.ts` | Refactor | ~150 → ~60 |
| `e2e/pages/run-protocol.page.ts` | Create | ~80 new |

---

## Acceptance Criteria

- [ ] Tests pass with parallel execution (`--workers=4`)
- [ ] Zero `.catch(() => {})` patterns
- [ ] Zero `waitForTimeout` calls
- [ ] Uses `RunProtocolPage` POM for all interactions
- [ ] Uses `worker-db.fixture` for isolation
- [ ] Verifies at least one domain state change (protocol selection or execution state)
- [ ] Baseline score improves to ≥8.0/10

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Deck setup is required for "Start Execution" | Add test data seeding that pre-configures deck, or mock `DeckGeneratorService` |
| Pyodide worker takes too long | Increase timeout or mock worker for deterministic behavior |
| Protocol list varies per DB seed | Use consistent `seed-data.ts` fixture |
