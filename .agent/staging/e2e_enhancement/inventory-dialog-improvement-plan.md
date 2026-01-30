# E2E Enhancement Plan: inventory-dialog.spec.ts

**Target:** [inventory-dialog.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/inventory-dialog.spec.ts)  
**Baseline Score:** 1.6/10  
**Target Score:** 8.5/10  
**Effort Estimate:** 4-5 hours (complete rewrite)

---

## Goals

1. **Correctness** — Target actual UI elements that exist in AssetWizard
2. **Reliability** — Use stable selectors (data-testid, getByRole)
3. **Domain Coverage** — Verify SQLite persistence after asset creation
4. **Maintainability** — Create AssetWizardPage POM for reuse

---

## Immediate Action: Delete & Replace

The current test file is **non-functional** — every selector targets a non-existent UI. It should be:
1. Marked as `@skip` or deleted
2. Replaced with a new test suite targeting the actual `AssetWizard` component

---

## Phase 1: Create AssetWizardPage POM (Priority: Critical)

### 1.1 New Page Object Model

Create `e2e/pages/asset-wizard.page.ts`:

```typescript
import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class AssetWizardPage extends BasePage {
  readonly dialog: Locator;
  readonly stepper: Locator;
  
  // Step indicators
  readonly stepType: Locator;
  readonly stepCategory: Locator;
  readonly stepMachineType: Locator;
  readonly stepDriver: Locator;
  readonly stepConfig: Locator;
  readonly stepReview: Locator;
  
  // Type Step
  readonly machineTypeCard: Locator;
  readonly resourceTypeCard: Locator;
  
  // Navigation
  readonly nextButton: Locator;
  readonly backButton: Locator;
  readonly createButton: Locator;
  
  // Config Step
  readonly instanceNameInput: Locator;
  
  constructor(page: Page) {
    super(page, '/app/playground?mode=browser');
    
    this.dialog = page.locator('app-asset-wizard');
    this.stepper = page.locator('mat-stepper');
    
    // Type step cards
    this.machineTypeCard = page.locator('[data-testid="type-card-machine"]');
    this.resourceTypeCard = page.locator('[data-testid="type-card-resource"]');
    
    // Navigation buttons
    this.nextButton = page.locator('[data-testid="wizard-next-button"]');
    this.backButton = page.locator('[data-testid="wizard-back-button"]');
    this.createButton = page.locator('[data-testid="wizard-create-btn"]');
    
    // Config inputs
    this.instanceNameInput = page.locator('[data-testid="input-instance-name"]');
  }
  
  async openFromPlaygroundHeader(type: 'machine' | 'resource' | 'browse' = 'machine') {
    const ariaLabels: Record<string, string> = {
      machine: 'Add Machine',
      resource: 'Add Resource',
      browse: 'Browse Inventory'
    };
    await this.page.getByRole('button', { name: ariaLabels[type] }).click();
    await expect(this.dialog).toBeVisible({ timeout: 5000 });
  }
  
  async selectAssetType(type: 'MACHINE' | 'RESOURCE') {
    const card = type === 'MACHINE' ? this.machineTypeCard : this.resourceTypeCard;
    await card.click();
    await this.nextButton.click();
  }
  
  async selectCategory(category: string) {
    await this.page.locator(`[data-testid="category-card-${category}"]`).click();
    await this.nextButton.click();
  }
  
  async selectFrontend(index: number = 0) {
    const frontendCards = this.page.locator('.result-card');
    await frontendCards.nth(index).click();
    await this.nextButton.click();
  }
  
  async selectBackend(preferSimulator: boolean = true) {
    if (preferSimulator) {
      // Select the simulated backend
      const simulatorCard = this.page.locator('.result-card:has-text("Simulated")').first();
      if (await simulatorCard.isVisible()) {
        await simulatorCard.click();
      } else {
        // Fall back to first backend
        await this.page.locator('.result-card').first().click();
      }
    } else {
      await this.page.locator('.result-card').first().click();
    }
    await this.nextButton.click();
  }
  
  async configureAsset(name: string, description?: string) {
    await this.instanceNameInput.fill(name);
    if (description) {
      await this.page.locator('textarea[formControlName="description"]').fill(description);
    }
    await this.nextButton.click();
  }
  
  async createAsset() {
    await this.createButton.click();
  }
  
  async waitForDialogClose() {
    await expect(this.dialog).not.toBeVisible({ timeout: 10000 });
  }
}
```

### 1.2 Use Worker DB Fixture

- [ ] Transition to worker-indexed database (`praxis-worker-N.db`)
- [ ] Import from shared fixture: `import { test } from './fixtures/worker-db.fixture'`

---

## Phase 2: Rewrite Test Suite

### 2.1 New Test: Machine Addition (Happy Path)

```typescript
import { test, expect } from '@playwright/test';
import { AssetWizardPage } from '../pages/asset-wizard.page';

test.describe('Asset Wizard - Machine Provisioning', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate and handle overlays
    await page.goto('/app/playground?mode=browser');
    await page.waitForLoadState('networkidle');
    
    // Dismiss any onboarding
    const skipButton = page.getByRole('button', { name: /skip|dismiss/i });
    if (await skipButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await skipButton.click();
    }
  });
  
  test('should add a simulated machine and verify persistence', async ({ page }) => {
    const wizard = new AssetWizardPage(page);
    
    // 1. Open wizard
    await wizard.openFromPlaygroundHeader('machine');
    
    // 2. Type already pre-selected as MACHINE, proceed
    await wizard.nextButton.click();
    
    // 3. Select category (first available)
    const firstCategory = page.locator('.category-card').first();
    await firstCategory.click();
    await wizard.nextButton.click();
    
    // 4. Select machine type (frontend)
    await wizard.selectFrontend(0);
    
    // 5. Select simulated backend
    await wizard.selectBackend(true);
    
    // 6. Configure
    const uniqueName = `Test Machine ${Date.now()}`;
    await wizard.configureAsset(uniqueName);
    
    // 7. Create
    await wizard.createAsset();
    await wizard.waitForDialogClose();
    
    // 8. Verify machine appears in Direct Control tab
    await page.getByRole('tab', { name: 'Direct Control' }).click();
    await expect(page.locator('.machine-card').filter({ hasText: uniqueName })).toBeVisible({ timeout: 5000 });
  });
  
  test('should validate form required fields', async ({ page }) => {
    const wizard = new AssetWizardPage(page);
    
    await wizard.openFromPlaygroundHeader('machine');
    
    // Try to proceed without selection
    await wizard.nextButton.click();
    
    // Should remain on step (form invalid)
    await expect(wizard.machineTypeCard).toBeVisible();
  });
  
});
```

### 2.2 New Test: Resource Addition

```typescript
test('should add a resource via wizard', async ({ page }) => {
  const wizard = new AssetWizardPage(page);
  
  await wizard.openFromPlaygroundHeader('resource');
  await wizard.selectAssetType('RESOURCE');
  
  // Category selection
  await page.locator('.category-card').first().click();
  await wizard.nextButton.click();
  
  // Definition search
  const searchInput = page.locator('input[placeholder*="Plate"]');
  await searchInput.fill('96');
  await page.locator('.result-card').first().click();
  await wizard.nextButton.click();
  
  // Config
  await wizard.configureAsset(`Test Resource ${Date.now()}`);
  
  // Create
  await wizard.createAsset();
  await wizard.waitForDialogClose();
});
```

---

## Phase 3: Domain Verification

### 3.1 Post-Action Database Verification

```typescript
test('should persist machine to SQLite', async ({ page }) => {
  const wizard = new AssetWizardPage(page);
  const machineName = `Verified Machine ${Date.now()}`;
  
  // ... creation steps ...
  
  // Verify via Angular component state (Deep State Verification)
  const machineCount = await page.evaluate(() => {
    const component = (window as any).ng?.getComponent(
      document.querySelector('app-playground')
    );
    return component?.availableMachines()?.length ?? 0;
  });
  
  expect(machineCount).toBeGreaterThanOrEqual(1);
  
  // Alternative: Verify via page reload persistence
  await page.reload();
  await page.waitForLoadState('networkidle');
  await page.getByRole('tab', { name: 'Direct Control' }).click();
  await expect(page.locator('.machine-card').filter({ hasText: machineName }))
    .toBeVisible({ timeout: 10000 });
});
```

---

## Phase 4: Error State Coverage (Stretch)

- [ ] Test empty category list handling
- [ ] Test no-backends-found state
- [ ] Test form validation error messages
- [ ] Test wizard cancellation (dialog close without save)
- [ ] Test connection info requirement for hardware backends

---

## Verification Plan

### Automated
```bash
# Run new tests in parallel
npx playwright test e2e/specs/asset-wizard.spec.ts --workers=4

# Run with trace for debugging
npx playwright test e2e/specs/asset-wizard.spec.ts --trace=on
```

### Manual Checklist
- [ ] Wizard opens from all three header buttons
- [ ] Stepper navigation works forward/backward
- [ ] Simulator selection available
- [ ] Machine appears in Direct Control after creation

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/inventory-dialog.spec.ts` | DELETE | 88 (entire file) |
| `e2e/specs/asset-wizard.spec.ts` | CREATE | ~150 |
| `e2e/pages/asset-wizard.page.ts` | CREATE | ~100 |
| `e2e/fixtures/worker-db.fixture.ts` | MODIFY | Import in new test |

---

## Acceptance Criteria

- [ ] Old test deleted or archived with skip annotation
- [ ] New test suite passes with 4 parallel workers
- [ ] Zero `waitForTimeout` calls
- [ ] Uses `data-testid` selectors from actual implementation
- [ ] Verifies machine appears after creation
- [ ] Uses AssetWizardPage POM consistently
- [ ] Baseline score improves to ≥8.5/10

---

## Notes

This is a **complete rewrite** rather than a refactor because:
1. Every single selector in the current test is wrong
2. The UI structure assumed (tabs) doesn't match reality (stepper)
3. The button labels and aria-labels don't match
4. No shared logic is salvageable

The current test provides **false confidence** — it would fail immediately on any real test run, so removing it doesn't reduce coverage (coverage was already 0%).
