# Improvement Plan: interactions/03-asset-forms.spec.ts

**Target File:** [03-asset-forms.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/interactions/03-asset-forms.spec.ts)  
**Report Date:** 2026-01-30  
**Current Score:** 3.2/10  
**Target Score:** 8.0+/10

---

## Executive Summary

The current test file has **fundamental architecture problems** that make it non-functional against the actual wizard implementation. The tests attempt to navigate a 6-step wizard using incorrect selectors and skip mandatory steps. This improvement plan focuses on:

1. **Fixing the wizard navigation flow** to match actual implementation
2. **Leveraging existing POM methods** from `AssetsPage`
3. **Adding positive path tests** before negative validation tests
4. **Implementing proper synchronization** for Material Stepper animations

---

## Phase 1: Critical Fixes (Immediate)

### 1.1 Fix Wizard Step Navigation

**Problem:** Tests use non-existent selectors (`.definition-item`) and skip required steps.

**Solution:** Use the correct wizard flow and test IDs from `asset-wizard.html`:

```typescript
// WRONG (current):
const categoryCards = page.locator('.category-card');
await categoryCards.first().click();
const definitionItems = page.locator('.definition-item');
await definitionItems.first().click();

// CORRECT (proposed):
// Step 1: Select Asset Type (MACHINE)
const machineTypeCard = page.getByTestId('type-card-machine');
await machineTypeCard.click();
await page.getByTestId('wizard-next-button').click();

// Step 2: Select Category
const categoryCard = page.getByTestId('category-card-LiquidHandler');
await categoryCard.click();
await page.getByTestId('wizard-next-button').click();

// Step 3: Select Frontend (Machine Type)
const frontendCard = page.locator('[data-testid^="frontend-card-"]').first();
await frontendCard.click();
await page.getByTestId('wizard-next-button').click();

// Step 4: Select Backend (Driver)
const backendCard = page.locator('[data-testid^="backend-card-"]').first();
await backendCard.click();
await page.getByTestId('wizard-next-button').click();

// Now at Step 5: Configuration - can test name validation
```

### 1.2 Add Step Synchronization

**Problem:** No waiting for Material Stepper animations between steps.

**Solution:** Use or adapt `AssetsPage.waitForStepTransition()`:

```typescript
private async waitForConfigStep(wizard: Locator): Promise<void> {
    // Wait for animation settle
    await this.page.waitForTimeout(150);
    
    // Verify we're on Configuration step
    const heading = wizard.locator('h3:visible').filter({ hasText: /Complete Configuration/i });
    await expect(heading).toBeVisible({ timeout: 15000 });
}
```

### 1.3 Fix the Finish Button Selector

**Problem:** Button is labeled "Create Asset", not "Finish" or "Save".

**Solution:**
```typescript
// WRONG:
const finishBtn = page.getByRole('button', { name: /Finish|Save/i });

// CORRECT:
const createBtn = page.getByTestId('wizard-create-btn');
// Or fallback:
const createBtn = page.getByRole('button', { name: /Create Asset/i });
```

---

## Phase 2: Leverage Page Object Model

### 2.1 Create Dedicated Wizard Navigation Helper

**Location:** `e2e/page-objects/assets.page.ts`

Add a method specifically for navigating to the Configuration step without creating the asset:

```typescript
/**
 * Navigate through wizard steps to reach Configuration step.
 * Does NOT click Create - leaves wizard open for validation testing.
 */
async navigateToConfigStep(
    category: string = 'LiquidHandler'
): Promise<Locator> {
    await this.waitForOverlaysToDismiss();
    await this.addMachineButton.click();
    const wizard = await this.waitForWizard();

    // Step 1: Asset Type
    await wizard.getByTestId('type-card-machine').click();
    await this.clickNextButton(wizard);

    // Step 2: Category
    await this.waitForStepTransition(wizard, /Select Category/i);
    await wizard.getByTestId(`category-card-${category}`).click();
    await this.clickNextButton(wizard);

    // Step 3: Frontend
    await this.waitForStepTransition(wizard, /Select Machine Type/i);
    await wizard.locator('[data-testid^="frontend-card-"]').first().click();
    await this.clickNextButton(wizard);

    // Step 4: Backend
    await this.waitForStepTransition(wizard, /Select Driver/i);
    await wizard.locator('[data-testid^="backend-card-"]').first().click();
    await this.clickNextButton(wizard);

    // Step 5: Configuration
    await this.waitForStepTransition(wizard, /Complete Configuration/i);
    return wizard;
}
```

### 2.2 Refactor Tests to Use POM

```typescript
test('should validate machine name is required', async ({ page }) => {
    const assetsPage = new AssetsPage(page);
    await assetsPage.goto();
    await assetsPage.navigateToMachines();
    
    // Use new helper to get to config step
    const wizard = await assetsPage.navigateToConfigStep();
    
    const nameInput = wizard.getByTestId('input-instance-name');
    const createBtn = wizard.getByTestId('wizard-create-btn');
    
    // Verify name is required before going to Review step
    await nameInput.clear();
    const nextBtn = wizard.getByTestId('wizard-next-button');
    await expect(nextBtn).toBeDisabled();
    
    await nameInput.fill('Valid Machine Name');
    await expect(nextBtn).toBeEnabled();
});
```

---

## Phase 3: Add Missing Positive Path Tests

### 3.1 Happy Path: Create Machine Successfully

Before testing validation edge cases, add a test that verifies the core functionality works:

```typescript
test('should successfully create a machine through the wizard', async ({ page }) => {
    const assetsPage = new AssetsPage(page);
    await assetsPage.goto();
    await assetsPage.navigateToMachines();
    
    const machineName = `Test-Machine-${Date.now()}`;
    await assetsPage.createMachine(machineName, 'LiquidHandler');
    
    // Verify machine appears in the table
    await assetsPage.verifyAssetVisible(machineName);
    
    // Cleanup
    await assetsPage.deleteMachine(machineName);
});
```

### 3.2 Validation Tests Should Have Prerequisites

Structure validation tests as variations of the happy path:

```typescript
test.describe('Machine Wizard Validation', () => {
    let assetsPage: AssetsPage;
    let wizard: Locator;
    
    test.beforeEach(async ({ page }) => {
        assetsPage = new AssetsPage(page);
        await assetsPage.goto();
        await assetsPage.navigateToMachines();
        wizard = await assetsPage.navigateToConfigStep();
    });
    
    test('name field is required', async ({ page }) => {
        const nameInput = wizard.getByTestId('input-instance-name');
        await nameInput.clear();
        
        const nextBtn = wizard.getByTestId('wizard-next-button');
        await expect(nextBtn).toBeDisabled();
        
        // Also verify mat-error appears
        await expect(wizard.locator('mat-error')).toHaveText(/Name is required/i);
    });
    
    test('valid name enables progression', async ({ page }) => {
        const nameInput = wizard.getByTestId('input-instance-name');
        await nameInput.fill('My New Machine');
        
        const nextBtn = wizard.getByTestId('wizard-next-button');
        await expect(nextBtn).toBeEnabled();
    });
});
```

---

## Phase 4: Remove Conditional Test Logic

### 4.1 Fix the Advanced JSON Test

**Problem:** Test silently passes if toggle isn't visible.

**Solution Options:**

**Option A: Skip test explicitly if feature unavailable:**
```typescript
test('should show validation error for invalid JSON', async ({ page }) => {
    const wizard = await assetsPage.navigateToConfigStep('LiquidHandler');
    
    const advancedToggle = wizard.getByRole('button', { name: /Advanced/i });
    
    // Explicitly skip if feature unavailable
    if (!await advancedToggle.isVisible({ timeout: 2000 })) {
        test.skip(true, 'Advanced JSON configuration not available for this backend');
        return;
    }
    
    await advancedToggle.click();
    // ... rest of test
});
```

**Option B: Select a backend known to have the feature:**
```typescript
test('should validate JSON in connection info field (hardware backends)', async ({ page }) => {
    // Navigate to a specific hardware backend that requires connection_info
    const wizard = await assetsPage.navigateToConfigStep('LiquidHandler');
    
    // Select a hardware backend (not simulator)
    const hardwareBackend = wizard.locator('[data-testid^="backend-card-"]')
        .filter({ hasNotText: 'Simulated' }).first();
    
    await hardwareBackend.click();
    await wizard.getByTestId('wizard-next-button').click();
    
    // Now connection_info field should be visible
    const connectionInput = wizard.getByLabel(/Serial Port/i);
    await expect(connectionInput).toBeVisible();
    
    // Test invalid input
    await connectionInput.fill('invalid json: {');
    await expect(wizard.locator('mat-error')).toBeVisible();
});
```

---

## Phase 5: Error State Coverage

### 5.1 Add Network Error Handling Test

```typescript
test('should handle creation failure gracefully', async ({ page }) => {
    const wizard = await assetsPage.navigateToConfigStep();
    await wizard.getByTestId('input-instance-name').fill('Test Machine');
    await wizard.getByTestId('wizard-next-button').click();
    
    // Mock the asset creation to fail
    await page.route('**/api/machines', (route) => {
        route.fulfill({
            status: 500,
            body: JSON.stringify({ error: 'Internal Server Error' }),
        });
    });
    
    const createBtn = wizard.getByTestId('wizard-create-btn');
    await createBtn.click();
    
    // Verify error feedback
    await expect(page.getByText(/failed|error/i)).toBeVisible();
    // Wizard should remain open
    await expect(wizard).toBeVisible();
});
```

### 5.2 Add Duplicate Name Validation

```typescript
test('should prevent duplicate machine names', async ({ page }) => {
    const assetsPage = new AssetsPage(page);
    const duplicateName = 'Duplicate-Test-Machine';
    
    // Create first machine
    await assetsPage.createMachine(duplicateName);
    
    // Try to create second with same name
    const wizard = await assetsPage.navigateToConfigStep();
    await wizard.getByTestId('input-instance-name').fill(duplicateName);
    
    // Depending on implementation:
    // Either Next is disabled or error shown at Review step
    // ... assertions
});
```

---

## Implementation Checklist

| Phase | Task | Priority | Status |
|-------|------|----------|--------|
| 1.1 | Fix wizard step navigation selectors | 🔴 Critical | ⬜ |
| 1.2 | Add Material Stepper synchronization | 🔴 Critical | ⬜ |
| 1.3 | Fix "Create Asset" button selector | 🔴 Critical | ⬜ |
| 2.1 | Create `navigateToConfigStep()` POM helper | 🟡 High | ⬜ |
| 2.2 | Refactor tests to use POM | 🟡 High | ⬜ |
| 3.1 | Add happy path machine creation test | 🟡 High | ⬜ |
| 3.2 | Structure validation tests as variations | 🟢 Medium | ⬜ |
| 4.1 | Fix conditional test logic | 🟡 High | ⬜ |
| 5.1 | Add network error handling test | 🟢 Medium | ⬜ |
| 5.2 | Add duplicate name validation test | 🟢 Medium | ⬜ |

---

## Expected Outcomes

After implementing this plan:

| Metric | Before | After |
|--------|--------|-------|
| **Test Scope** | 3/10 | 7/10 |
| **Best Practices** | 4/10 | 8/10 |
| **Test Value** | 2/10 | 8/10 |
| **Isolation** | 5/10 | 8/10 |
| **Domain Coverage** | 2/10 | 7/10 |
| **Overall** | **3.2/10** | **7.6/10** |

---

## Appendix: File Changes Summary

| File | Changes |
|------|---------|
| `e2e/page-objects/assets.page.ts` | Add `navigateToConfigStep()` method |
| `e2e/specs/interactions/03-asset-forms.spec.ts` | Complete rewrite with correct selectors and flow |
| `e2e/specs/interactions/04-asset-forms-errors.spec.ts` | New file for error state tests (optional split) |
