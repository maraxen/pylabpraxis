# E2E Enhancement Plan: asset-wizard.spec.ts

**Target:** [asset-wizard.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/asset-wizard.spec.ts)  
**Baseline Score:** 4.6/10  
**Target Score:** 8.0/10  
**Effort Estimate:** 4-6 hours

---

## Goals

1. **Reliability** — Eliminate flaky patterns (hardcoded waits, force clicks)
2. **Isolation** — Enable parallel test execution via worker-indexed DB
3. **Domain Coverage** — Verify actual SQLite state changes, not just UI assertions
4. **Maintainability** — Leverage existing `AssetsPage` POM to reduce duplication

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Change import from `@playwright/test` to `../fixtures/app.fixture`
- [ ] Remove manual `waitForFunction()` for SQLite readiness (fixture handles this)
- [ ] Remove manual welcome dialog dismissal (fixture handles this)

**Before:**
```typescript
import { test, expect } from '@playwright/test';
// ...
await page.goto('/assets?mode=browser&resetdb=1');
await page.waitForFunction(() => window.sqliteService?.isReady$?.getValue() === true, null, { timeout: 30000 });
```

**After:**
```typescript
import { test, expect, buildIsolatedUrl } from '../fixtures/app.fixture';
// ...
// beforeEach in fixture handles navigation, DB wait, and welcome dismissal
```

### 1.2 Eliminate Hardcoded Waits
- [ ] Replace `waitForTimeout(1000)` with explicit wait for search results

**Before (Line 83):**
```typescript
await wizard.getByLabel('Search Definitions').fill('STAR');
await page.waitForTimeout(1000); // debounce
await wizard.locator('.result-card').first().click();
```

**After:**
```typescript
await wizard.getByLabel('Search Definitions').fill('STAR');
// Wait for at least one result to appear (debounce-tolerant)
const resultCard = wizard.locator('.result-card').first();
await expect(resultCard).toBeVisible({ timeout: 5000 });
await resultCard.click();
```

### 1.3 Replace Force Clicks (if any)
Current test doesn't use `force: true`, which is good. However, add overlay stabilization:

- [ ] Add `await page.locator('.cdk-overlay-backdrop').waitFor({ state: 'hidden' }).catch(() => {})` before wizard open

---

## Phase 2: Page Object Refactor

### 2.1 Use Existing `AssetsPage` POM
The `AssetsPage` class already provides:
- `waitForWizard()` — Safe wizard appearance wait
- `waitForStepTransition()` — Animation-aware step advancement
- `clickNextButton()` — Handles button enable state
- `selectWizardCard()` — Card selection with class verification
- `waitForOverlaysToDismiss()` — CDK overlay handling

- [ ] Import and instantiate `AssetsPage`
- [ ] Replace inline wizard logic with POM method calls

**Refactored Test Structure:**
```typescript
import { test, expect } from '../fixtures/app.fixture';
import { AssetsPage } from '../page-objects/assets.page';

test.describe('Asset Wizard Journey', () => {
    test('should guide the user through creating a Hamilton STAR machine', async ({ page }, testInfo) => {
        const assetsPage = new AssetsPage(page);
        
        // Navigate to assets (fixture provides isolated DB)
        await assetsPage.goto();
        
        // Use POM's createMachine with custom params or manual steps if needed
        await assetsPage.createMachine('Hamilton STAR Test', 'LiquidHandler', 'STAR');
        
        // Verify asset visible
        await assetsPage.verifyAssetVisible('Hamilton STAR Test');
    });
});
```

### 2.2 If Custom Steps Needed, Extract to POM
If this test requires unique steps not covered by `createMachine()`, extend the POM:
- [ ] Add `createMachineWithScreenshots()` method that captures at each step
- [ ] Add `verifyWizardStep()` helper for step-by-step testing

---

## Phase 3: Domain Verification

### 3.1 Post-Creation SQLite Verification
- [ ] Add `page.evaluate()` query to verify machine exists in database

```typescript
// After wizard closes
const machineData = await page.evaluate(async (name) => {
    const db = (window as any).sqliteService;
    const result = await db.query(
        'SELECT * FROM machines WHERE instance_name = ?',
        [name]
    );
    return result[0];
}, 'Hamilton STAR Test');

expect(machineData).toBeDefined();
expect(machineData.category).toBe('LiquidHandler');
expect(machineData.frontend_fqn).toContain('STAR');
```

### 3.2 Persistence Verification (Page Reload)
- [ ] Add reload assertion to verify OPFS persistence

```typescript
// After creation assertion
await page.reload();
await page.waitForFunction(...); // Wait for DB ready
await expect(page.getByText('Hamilton STAR Test')).toBeVisible({ timeout: 15000 });
```

### 3.3 Mock Removal Consideration
- [ ] Evaluate removing API mocks to test real definition catalog
- [ ] If mocks remain, add assertion that mock data was consumed correctly:

```typescript
// After selecting result card
const selectedText = await wizard.locator('.result-card.selected').textContent();
expect(selectedText).toContain('Hamilton STAR');
```

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Cancel Flow
- [ ] Add test for user clicking Cancel mid-wizard

```typescript
test('should handle wizard cancellation gracefully', async ({ page }) => {
    // Open wizard
    // Navigate to step 2
    // Click Cancel or press Escape
    // Verify wizard closes without creating asset
    // Verify no partial data in DB
});
```

### 4.2 Empty Search Results
- [ ] Add test for no matching definitions

```typescript
test('should display empty state when no definitions match', async ({ page }) => {
    // Override mock to return empty array
    // Search for "XYZ_NONEXISTENT"
    // Verify empty state message appears
    // Verify Next button is disabled
});
```

### 4.3 Validation Errors
- [ ] Add test for form validation

```typescript
test('should prevent creation with empty instance name', async ({ page }) => {
    // Navigate to config step
    // Leave name empty
    // Verify Next/Create button disabled or shows validation error
});
```

---

## Verification Plan

### Automated
```bash
# Run single test file
npx playwright test e2e/specs/asset-wizard.spec.ts --headed

# Run with parallelism to verify isolation
npx playwright test e2e/specs/asset-wizard.spec.ts --workers=4

# Run with tracing for debugging
npx playwright test e2e/specs/asset-wizard.spec.ts --trace=on
```

### Manual Verification Checklist
- [ ] No `waitForTimeout` calls remain in spec
- [ ] Imports use `../fixtures/app.fixture`
- [ ] Uses `AssetsPage` POM
- [ ] SQLite verification query exists
- [ ] Page reload persistence test exists
- [ ] All tests pass with `--workers=4`

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/asset-wizard.spec.ts` | Refactor | ~80 lines (major rewrite) |
| `e2e/page-objects/assets.page.ts` | Extend (optional) | +20 lines if adding screenshot helpers |

---

## Consolidation Opportunity

`asset-wizard-visual.spec.ts` shares ~80% of the same wizard navigation logic. Consider:

1. **Option A**: Merge into single spec with multiple test cases:
   - `should create a machine via wizard`
   - `should display optimized grid layouts`

2. **Option B**: Create shared helper in POM that both specs use:
   - `AssetsPage.navigateWizardToStep(stepNumber, options)` with optional screenshot capture

---

## Acceptance Criteria

- [ ] Tests pass with parallel execution (`--workers=4`)
- [ ] Zero `waitForTimeout` calls
- [ ] Zero `force: true` clicks
- [ ] Uses `app.fixture` or `worker-db.fixture`
- [ ] Uses `AssetsPage` POM for wizard interactions
- [ ] SQLite verification confirms machine row exists with correct data
- [ ] Page reload confirms persistence
- [ ] Baseline score improves to ≥8.0/10

---

## Estimated Final Score After Implementation

| Category | Current | Target | Improvement |
|----------|---------|--------|-------------|
| Test Scope | 6/10 | 8/10 | +Persistence, +SQLite verification |
| Best Practices | 4/10 | 9/10 | +POM, +fixture, -waits |
| Test Value | 6/10 | 8/10 | +Real integration (less mocking) |
| Isolation | 4/10 | 9/10 | +Worker DB, +cleanup |
| Domain Coverage | 3/10 | 7/10 | +SQLite queries, +error cases |

**Projected Overall: 8.2/10**
