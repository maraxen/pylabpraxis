# E2E Enhancement Plan: user-journeys.spec.ts

**Target:** [user-journeys.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/user-journeys.spec.ts)  
**Baseline Score:** 4.6/10  
**Target Score:** 8.0/10  
**Effort Estimate:** ~4 hours

---

## Goals

1. **Reliability** — Eliminate flaky patterns (hardcoded waits, force clicks)
2. **Isolation** — Enable parallel test execution via worker-indexed databases
3. **Domain Coverage** — Verify actual state changes, not just UI navigation
4. **Maintainability** — Use Page Object Model consistently

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration

#### [MODIFY] [user-journeys.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/user-journeys.spec.ts)

**Current (L1-2):**
```typescript
import { test, expect } from '@playwright/test';
```

**Proposed:**
```typescript
import { test, expect } from '../fixtures/worker-db.fixture';
// OR if fixture doesn't exist:
import { BasePage } from '../page-objects/base.page';
```

**Changes:**
- Replace direct `page.goto()` calls with `BasePage.goto()` or fixture-based navigation
- Add `testInfo` to enable `dbName=praxis-worker-{index}` isolation
- Remove manual `mode=browser` appending (handled by BasePage)

---

### 1.2 Eliminate Hardcoded Waits

| Line | Current | Replacement |
|------|---------|-------------|
| L15-17 | `waitForLoadState('networkidle')` | Remove entirely — rely on UI assertions |
| L68 | `waitForTimeout(500)` | `await expect(wizard.locator('h3:visible')).toBeVisible()` |
| L118 | `waitForTimeout(1000)` | `await expect(page.getByRole('tab')).toHaveAttribute('aria-selected', 'true')` |

---

### 1.3 Replace Force Clicks

| Line | Current | Fix |
|------|---------|-----|
| L51 | `addBtn.click({ force: true })` | Use `waitForOverlaysToDismiss()` from `AssetsPage`, then normal click |
| L133 | `frontendCard.click({ force: true })` | Wait for stepper animation, then click |

**Pattern to use:**
```typescript
// Before clicking, ensure no overlays are blocking
await page.locator('.cdk-overlay-backdrop').waitFor({ state: 'hidden', timeout: 5000 }).catch(() => {});
await addBtn.click();
```

---

## Phase 2: Page Object Refactor

### 2.1 Use Existing POMs

#### [MODIFY] [user-journeys.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/user-journeys.spec.ts)

**Asset Management test refactor:**

```typescript
test('Asset Management: View and Create Machine', async ({ page }) => {
  const assetsPage = new AssetsPage(page);
  
  // Navigate with proper isolation
  await assetsPage.goto();
  await assetsPage.navigateToMachines();
  
  // Create using POM method (already handles all wizard steps)
  await assetsPage.createMachine('New Robot', 'LiquidHandler');
  
  // Verify persistence (Phase 3)
  await assetsPage.verifyAssetVisible('New Robot');
});
```

**Protocol Workflow test refactor:**

```typescript
test('Protocol Workflow: Select and Run', async ({ page }) => {
  const wizard = new WizardPage(page);
  
  await page.goto('/protocols?mode=browser');
  
  // Click run on Simple Transfer
  const row = page.locator('tr', { hasText: 'Simple Transfer' });
  await row.getByRole('button', { name: /run|play/i }).click();
  
  await page.waitForURL(/.*\/run/);
  
  // Use WizardPage methods
  await wizard.completeParameterStep();
  await wizard.selectFirstCompatibleMachine();
  await wizard.waitForAssetsAutoConfigured();
  await wizard.advanceDeckSetup();
  await wizard.openReviewStep();
  await wizard.startExecution();
  
  // Verify execution started
  await page.waitForURL('**/run/live');
});
```

---

## Phase 3: Domain Verification

### 3.1 Post-Creation Verification

Add after wizard closes in Asset Management test:

```typescript
// Verify asset persisted to SQLite
await page.goto('/assets?type=machine&mode=browser');
await expect(page.getByText('New Robot')).toBeVisible({ timeout: 10000 });

// Optional: Deep verification via evaluate
const assetExists = await page.evaluate(async () => {
  const db = (window as any).sqliteService?.db;
  if (!db) return false;
  const result = db.exec("SELECT name FROM machines WHERE name = 'New Robot'");
  return result.length > 0 && result[0].values.length > 0;
});
expect(assetExists).toBe(true);
```

### 3.2 Execution Outcome Verification

Add after "Start Execution" in Protocol Workflow test:

```typescript
// Verify navigation to live view
await page.waitForURL('**/run/live', { timeout: 15000 });

// Verify execution status indicator
await expect(page.getByTestId('execution-status')).toBeVisible();

// Verify run appears in history (eventual consistency)
await expect(async () => {
  const statusText = await page.getByTestId('execution-status').textContent();
  expect(['Running', 'Queued', 'Starting']).toContain(statusText);
}).toPass({ timeout: 10000 });
```

---

## Phase 4: Error State Coverage (Stretch)

Add new tests:

```typescript
test('Asset Creation: Validation prevents empty name', async ({ page }) => {
  const assetsPage = new AssetsPage(page);
  await assetsPage.goto();
  await assetsPage.addMachineButton.click();
  
  // Navigate to config step
  // ... category, frontend, backend selection ...
  
  // Leave name empty, verify Create is disabled
  const createBtn = page.getByTestId('wizard-create-btn');
  await expect(createBtn).toBeDisabled();
});

test('Protocol Workflow: Handles missing machine gracefully', async ({ page }) => {
  // Delete all machines first
  // Try to run protocol
  // Verify error message shown
});
```

---

## Verification Plan

### Automated

```bash
# Run only the refactored test
cd /Users/mar/Projects/praxis/praxis/web-client
npx playwright test e2e/specs/user-journeys.spec.ts --workers=1 --timeout=120000

# Parallel execution test (verify isolation works)
npx playwright test e2e/specs/user-journeys.spec.ts --workers=4 --repeat-each=2
```

### Manual Verification

1. **Watch test execution** with UI mode:
   ```bash
   npx playwright test e2e/specs/user-journeys.spec.ts --ui
   ```

2. **Verify no force clicks** — Search for `force: true` in the file; should be zero occurrences

3. **Verify no hardcoded waits** — Search for `waitForTimeout`; should be zero occurrences

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/user-journeys.spec.ts` | Refactor | ~150 lines rewritten |
| `e2e/page-objects/assets.page.ts` | Minor | Add any missing helpers |
| `e2e/page-objects/wizard.page.ts` | None | Already has required methods |

---

## Acceptance Criteria

- [ ] Tests pass with `--workers=4` (parallel execution)
- [ ] Zero `force: true` clicks
- [ ] Zero `waitForTimeout` calls
- [ ] Uses `AssetsPage` and `WizardPage` POMs
- [ ] Verifies asset appears in list after creation
- [ ] Verifies navigation to `/run/live` after execution
- [ ] Baseline score improves to ≥8.0/10
