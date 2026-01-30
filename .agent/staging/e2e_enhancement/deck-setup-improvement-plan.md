# E2E Enhancement Plan: deck-setup.spec.ts

**Target:** [deck-setup.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/deck-setup.spec.ts)  
**Baseline Score:** 2.0/10  
**Target Score:** 8.0/10  
**Effort Estimate:** 4-6 hours

---

## Goals

1. **Reliability** — Eliminate hardcoded waits and flaky navigation patterns
2. **Isolation** — Enable parallel test execution with worker-indexed databases
3. **Domain Coverage** — Verify actual deck wizard state transitions and serialization
4. **Maintainability** — Leverage existing `WizardPage` POM and create `DeckSetupPage` for wizard-specific logic

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Import from `fixtures/worker-db.fixture` instead of `@playwright/test`
- [ ] Use `gotoWithWorkerDb()` for initial navigation
- [ ] Ensure each parallel worker gets isolated database state

**Code Change:**
```typescript
// Before
import { test, expect } from '@playwright/test';
await page.goto('/');

// After
import { test, expect, gotoWithWorkerDb } from '../fixtures/worker-db.fixture';
await gotoWithWorkerDb(page, '/app/home', testInfo, { resetdb: true });
```

### 1.2 Eliminate Hardcoded Waits
- [ ] Remove all 4 `waitForTimeout` calls (lines 59, 64, 69, 87)
- [ ] Replace with `WizardPage` step transition methods that wait for animations

**Replacements:**
| Remove | Replace With |
|--------|--------------|
| `page.waitForTimeout(500)` after Continue clicks | `WizardPage.completeParameterStep()` etc. |
| `page.waitForTimeout(2000)` before screenshot | `expect(wizard).toHaveCSS('opacity', '1')` + Angular animation wait |

### 1.3 Use WizardPage POM
- [ ] Import and instantiate existing `WizardPage` from `e2e/page-objects/wizard.page.ts`
- [ ] Replace inline navigation with `WizardPage` methods:
  - `completeParameterStep()`
  - `selectFirstCompatibleMachine()`
  - `waitForAssetsAutoConfigured()`
  - `advanceDeckSetup()` (needs modification — see Phase 2)

**Before:**
```typescript
const continueBtn = page.getByRole('button', { name: /Continue/i });
await continueBtn.click();
await page.waitForTimeout(500);
await continueBtn.click();
// ... repeated 4 times
```

**After:**
```typescript
const wizardPage = new WizardPage(page);
await wizardPage.completeParameterStep();
await wizardPage.selectFirstCompatibleMachine();
await wizardPage.waitForAssetsAutoConfigured();
// Now at deck step
```

---

## Phase 2: Page Object Refactor

### 2.1 Create `DeckSetupPage` POM
Create a new page object for deck wizard interactions:

**File:** `e2e/page-objects/deck-setup.page.ts`

```typescript
import { expect, Locator, Page } from '@playwright/test';

export class DeckSetupPage {
    private readonly page: Page;
    private readonly wizardRoot: Locator;
    private readonly carrierStep: Locator;
    private readonly resourceStep: Locator;
    private readonly verificationStep: Locator;
    private readonly skipButton: Locator;
    private readonly nextButton: Locator;
    private readonly backButton: Locator;
    private readonly confirmButton: Locator;

    constructor(page: Page) {
        this.page = page;
        this.wizardRoot = page.locator('app-deck-setup-wizard');
        this.carrierStep = page.locator('app-carrier-placement-step');
        this.resourceStep = page.locator('app-resource-placement-step');
        this.verificationStep = page.locator('app-verification-step');
        this.skipButton = this.wizardRoot.getByRole('button', { name: /Skip Setup/i });
        this.nextButton = this.wizardRoot.getByRole('button', { name: /Next/i });
        this.backButton = this.wizardRoot.getByRole('button', { name: /Back/i });
        this.confirmButton = this.wizardRoot.getByRole('button', { name: /Confirm & Continue/i });
    }

    async waitForWizardVisible() {
        await expect(this.wizardRoot).toBeVisible({ timeout: 15000 });
    }

    async isOnCarrierStep(): Promise<boolean> {
        return this.carrierStep.isVisible({ timeout: 2000 }).catch(() => false);
    }

    async isOnResourceStep(): Promise<boolean> {
        return this.resourceStep.isVisible({ timeout: 2000 }).catch(() => false);
    }

    async isOnVerificationStep(): Promise<boolean> {
        return this.verificationStep.isVisible({ timeout: 2000 }).catch(() => false);
    }

    async getProgress(): Promise<number> {
        const bar = this.wizardRoot.locator('mat-progress-bar');
        const value = await bar.getAttribute('aria-valuenow');
        return value ? parseInt(value, 10) : 0;
    }

    async markCarrierPlaced(carrierName: string) {
        const carrierItem = this.carrierStep.locator('.carrier-item', { hasText: carrierName });
        const checkbox = carrierItem.locator('mat-checkbox, input[type="checkbox"]');
        await checkbox.check();
    }

    async markAllCarriersPlaced() {
        const items = this.carrierStep.locator('.carrier-item');
        const count = await items.count();
        for (let i = 0; i < count; i++) {
            const checkbox = items.nth(i).locator('mat-checkbox, input[type="checkbox"]');
            if (!(await checkbox.isChecked())) {
                await checkbox.check();
            }
        }
    }

    async advanceToResourceStep() {
        await this.markAllCarriersPlaced();
        await this.nextButton.click();
        await expect(this.resourceStep).toBeVisible({ timeout: 5000 });
    }

    async markAllResourcesPlaced() {
        const items = this.resourceStep.locator('.assignment-item');
        const count = await items.count();
        for (let i = 0; i < count; i++) {
            const checkbox = items.nth(i).locator('mat-checkbox, input[type="checkbox"]');
            if (!(await checkbox.isChecked())) {
                await checkbox.check();
            }
        }
    }

    async advanceToVerificationStep() {
        await this.markAllResourcesPlaced();
        await this.nextButton.click();
        await expect(this.verificationStep).toBeVisible({ timeout: 5000 });
    }

    async confirmSetup() {
        await expect(this.confirmButton).toBeEnabled();
        await this.confirmButton.click();
    }

    async skipSetup() {
        await this.skipButton.click();
    }

    async getWizardState(): Promise<{currentStep: string, progress: number}> {
        return this.page.evaluate(() => {
            const cmp = (window as any).ng?.getComponent?.(document.querySelector('app-deck-setup-wizard'));
            return {
                currentStep: cmp?.wizardState?.currentStep?.() || 'unknown',
                progress: cmp?.wizardState?.progress?.() || 0
            };
        });
    }
}
```

### 2.2 Extend WizardPage for Deck Setup Entry
- [ ] Add method to `WizardPage` to navigate *to* deck step and return control

```typescript
// In wizard.page.ts
async navigateToDeckSetup(): Promise<void> {
    await this.completeParameterStep();
    await this.selectFirstCompatibleMachine();
    await this.waitForAssetsAutoConfigured();
    // Now deckStep should be visible
    await this.deckStep.waitFor({ state: 'visible' });
}
```

---

## Phase 3: Domain Verification

### 3.1 Wizard State Verification
- [ ] Use `ng.getComponent()` to access `WizardStateService` internals
- [ ] Verify step transitions after each interaction

**Test:**
```typescript
test('should transition through all wizard steps', async ({ page }) => {
    const deckPage = new DeckSetupPage(page);
    await deckPage.waitForWizardVisible();
    
    // Verify initial state
    const initialState = await deckPage.getWizardState();
    expect(initialState.currentStep).toBe('carrier-placement');
    expect(initialState.progress).toBeGreaterThanOrEqual(0);
    
    // Advance through steps
    await deckPage.advanceToResourceStep();
    const step2 = await deckPage.getWizardState();
    expect(step2.currentStep).toBe('resource-placement');
    
    await deckPage.advanceToVerificationStep();
    const step3 = await deckPage.getWizardState();
    expect(step3.currentStep).toBe('verification');
});
```

### 3.2 AssetMap Serialization Verification
- [ ] Capture the result of `onConfirm()` by listening for dialog close event
- [ ] Verify the `assetMap` structure is valid

**Test:**
```typescript
test('should produce valid assetMap on confirm', async ({ page }) => {
    const deckPage = new DeckSetupPage(page);
    await deckPage.waitForWizardVisible();
    
    await deckPage.advanceToResourceStep();
    await deckPage.advanceToVerificationStep();
    
    // Capture assetMap before confirmation
    const assetMap = await page.evaluate(() => {
        const cmp = (window as any).ng?.getComponent?.(document.querySelector('app-deck-setup-wizard'));
        return cmp?.wizardState?.getAssetMap?.();
    });
    
    expect(assetMap).toBeDefined();
    expect(typeof assetMap).toBe('object');
    // Add protocol-specific assertions based on requirements
});
```

### 3.3 Skip Behavior Verification
- [ ] Test that skip emits `setupSkipped` event
- [ ] Verify app continues to Review step after skip

**Test:**
```typescript
test('should allow skipping deck setup', async ({ page }) => {
    const deckPage = new DeckSetupPage(page);
    await deckPage.waitForWizardVisible();
    
    await deckPage.skipSetup();
    
    // Should navigate to Review step
    await expect(page.getByRole('heading', { name: /Ready to Launch/i })).toBeVisible({ timeout: 10000 });
});
```

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Invalid State Transitions
- [ ] Attempt to click "Next" when carriers are not marked (button should be disabled)

### 4.2 Missing Deck Resource
- [ ] Test protocol that doesn't require deck setup (wizard should not appear)

### 4.3 Back Navigation
- [ ] Verify "Back" button returns to previous step with state preserved

---

## Verification Plan

### Automated
```bash
# Run with parallel workers to verify isolation
npx playwright test e2e/specs/deck-setup.spec.ts --workers=4

# Run with tracing for debugging
npx playwright test e2e/specs/deck-setup.spec.ts --trace=on
```

### Manual Checklist
- [ ] Screenshots still captured (regression check for original functionality)
- [ ] No console errors during wizard navigation
- [ ] Tests complete in < 30 seconds each

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/deck-setup.spec.ts` | Refactor | ~100 → ~150 |
| `e2e/page-objects/deck-setup.page.ts` | Create | ~100 (new) |
| `e2e/page-objects/wizard.page.ts` | Extend | +10-15 |

---

## Acceptance Criteria

- [ ] Tests pass with parallel execution (`--workers=4`)
- [ ] Zero `force: true` clicks
- [ ] Zero `waitForTimeout` calls  
- [ ] Uses `DeckSetupPage` POM for wizard interactions
- [ ] Uses `WizardPage` POM for navigation to deck step
- [ ] Verifies `WizardStateService.currentStep()` after each transition
- [ ] Verifies `assetMap` structure on confirmation
- [ ] Tests skip behavior
- [ ] Baseline score improves to ≥8.0/10

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Wizard DOM structure differs from assumptions | Use `ng.getComponent()` for state verification, not DOM inspection |
| Protocol doesn't have deck requirements | Add protocol filter or seed specific protocol with deck requirements |
| Material animations cause timing issues | Add `waitForOverlaysToDismiss()` and animation duration waits |
