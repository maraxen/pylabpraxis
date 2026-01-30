# E2E Enhancement Plan: machine-frontend-backend.spec.ts

**Target:** [machine-frontend-backend.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/machine-frontend-backend.spec.ts)  
**Baseline Score:** 5.0/10  
**Target Score:** 8.0/10  
**Effort Estimate:** 4-6 hours

---

## Goals

1. **Reliability** — Eliminate brittle CSS selectors and inconsistent waits
2. **Isolation** — Enable parallel test execution with worker-indexed DBs
3. **Domain Coverage** — Verify machine creation correctness in SQLite
4. **Maintainability** — Leverage `AssetsPage` POM methods consistently

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Add `testInfo` parameter to `AssetsPage` constructor calls in `beforeEach`
- [ ] Ensure all navigation uses `BasePage.goto()` for worker-indexed DB (`praxis-worker-{N}.db`)
- [ ] Refactor inline URL (line 468) to use proper playground page object or BasePage pattern

**Code Change:**
```typescript
// BEFORE (line 16-19)
test.beforeEach(async ({ page }) => {
    const welcomePage = new WelcomePage(page);
    assetsPage = new AssetsPage(page);

// AFTER
test.beforeEach(async ({ page }, testInfo) => {
    const welcomePage = new WelcomePage(page, testInfo);
    assetsPage = new AssetsPage(page, testInfo);
```

### 1.2 Add Test Cleanup
- [ ] Add `afterEach` hook to delete created machines
- [ ] Use `assetsPage.deleteMachine()` for teardown

**Code Change:**
```typescript
test.afterEach(async () => {
    // Clean up any machines created during test
    // Machine names follow pattern: "Test Machine {timestamp}" or "Persist Machine {timestamp}"
    // The deleteMachine method handles dialog confirmation
});
```

### 1.3 Replace Brittle CSS Selectors
| Current Selector | Line(s) | Replacement |
|:-----------------|:--------|:------------|
| `button.selection-card:visible` | 45, 51, 69, 72, etc. | `getByTestId('frontend-card-*')` or `getByRole('option')` |
| `button.selection-card.definition-card:visible` | 128, 196, 234, etc. | `getByTestId('backend-card-*')` |
| `.simulated-chip` | 165 | `getByTestId('simulated-badge')` or `getByText('Simulated')` |
| Back button via mat-icon filter | 379, 418 | `getByTestId('wizard-back-btn')` or `getByRole('button', { name: /Back/i })` |
| `.stepper` div filter | 454 | `getByTestId('stepper-indicator-0')` or `getByRole('tab')` |

**Prerequisite:** Angular component changes required to add `data-testid` attributes.

### 1.4 Standardize Timeouts
- [ ] Create or use existing timeout constants
- [ ] Replace magic numbers (5000, 10000, 15000) with named constants

---

## Phase 2: Page Object Refactor

### 2.1 Use Existing POM Methods
The `AssetsPage` already has robust methods that the spec ignores. Refactor tests to delegate:

| Spec Inline Logic | POM Method to Use |
|:------------------|:------------------|
| Open dialog + Step 1-3 + Finish | `assetsPage.createMachine(name, category, modelQuery)` |
| Step navigation with Next button | `assetsPage.clickNextButton()` (private, but logic can be reused) |
| Wait for step heading | `assetsPage.waitForStepTransition()` |
| Dismiss overlays | `assetsPage.waitForOverlaysToDismiss()` |

### 2.2 Extract Wizard Navigation Helpers
- [ ] Add `openMachineDialog()` method to `AssetsPage`
- [ ] Add `selectFrontend(name: string)` method
- [ ] Add `selectBackend(nameOrSimulated: string)` method
- [ ] Add `configureInstance(name: string)` method

**New POM Methods:**
```typescript
async openMachineDialog(): Promise<Locator> {
    await this.waitForOverlaysToDismiss();
    await this.addMachineButton.click();
    const dialog = this.page.getByRole('dialog');
    await expect(dialog).toBeVisible({ timeout: 10000 });
    return dialog;
}

async selectFrontend(dialog: Locator, frontendName: string): Promise<void> {
    const card = dialog.getByTestId(`frontend-card-${frontendName}`);
    await expect(card).toBeVisible({ timeout: 15000 });
    await card.click();
}
```

### 2.3 Simplify Test Bodies
After POM refactor, tests should be ~5-10 lines:

```typescript
test('should complete full 3-step machine creation flow', async () => {
    const testMachineName = `Test Machine ${Date.now()}`;
    await assetsPage.goto();
    await assetsPage.navigateToMachines();
    await assetsPage.createMachine(testMachineName, 'LiquidHandler', 'ChatterBox');
    await expect(page.getByText(testMachineName)).toBeVisible();
});
```

---

## Phase 3: Domain Verification

### 3.1 Post-Creation Database Verification
- [ ] Add `page.evaluate()` check to verify machine record in SQLite
- [ ] Verify `frontend_id`, `backend_id`, and `name` fields match selections

**Code Change:**
```typescript
// After machine creation
const machineRecord = await page.evaluate(async (machineName) => {
    const sqliteService = (window as any).sqliteService;
    const repos = await sqliteService.getAsyncRepositories().toPromise();
    return repos.machines.findByName(machineName).toPromise();
}, testMachineName);

expect(machineRecord).toBeDefined();
expect(machineRecord.frontend_id).toBe(expectedFrontendId);
expect(machineRecord.backend_id).toBe(expectedBackendId);
```

### 3.2 Backend Filtering Correctness
- [ ] Add test: When PlateReader frontend selected, LiquidHandler backends should NOT appear
- [ ] Verify backend count changes based on frontend selection

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Validation Tests
- [ ] Test: Submit with empty instance name → Finish button disabled or error displayed
- [ ] Test: Submit with duplicate machine name → Error message shown

### 4.2 Cancel Behavior
- [ ] Test: Cancel mid-flow → No machine created, form state reset on reopen

### 4.3 Accessibility
- [ ] Test: Complete wizard using keyboard only (Tab, Enter, Arrow keys)
- [ ] Verify focus management during step transitions

---

## Verification Plan

### Automated
```bash
# Single test run
npx playwright test e2e/specs/machine-frontend-backend.spec.ts --workers=1

# Parallel execution (target state)
npx playwright test e2e/specs/machine-frontend-backend.spec.ts --workers=4

# Repeat run for flakiness detection
npx playwright test e2e/specs/machine-frontend-backend.spec.ts --repeat-each=3
```

### Manual Checklist
- [ ] Verify no `force: true` clicks remain
- [ ] Verify no `waitForTimeout` calls
- [ ] Verify all CSS class selectors replaced with test IDs or roles
- [ ] Confirm parallel execution doesn't cause DB contention

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/machine-frontend-backend.spec.ts` | Major Refactor | ~400 (entire file) |
| `e2e/page-objects/assets.page.ts` | Add Methods | +50-80 (new wizard helpers) |
| `src/app/.../machine-dialog.component.html` | Add Attributes | +10-15 (data-testid attrs) |

---

## Acceptance Criteria

- [ ] Tests pass with `--workers=4` parallel execution
- [ ] Zero `force: true` clicks
- [ ] Zero `waitForTimeout` calls
- [ ] Zero raw CSS class selectors (use `getByRole`, `getByLabel`, `getByTestId`)
- [ ] All tests use `AssetsPage` POM methods
- [ ] Database record verification included in full-flow test
- [ ] `afterEach` cleanup implemented
- [ ] Baseline score improves from 5.0/10 to ≥8.0/10

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|:-----|:-----------|:-----------|
| Angular component changes break existing tests | Medium | Implement data-testid first, update selectors atomically |
| Database cleanup in afterEach causes test coupling | Low | Use unique `Date.now()` names, delete by exact name |
| POM refactor is extensive | High | Do Phase 1 first to stabilize, then POM in separate PR |
