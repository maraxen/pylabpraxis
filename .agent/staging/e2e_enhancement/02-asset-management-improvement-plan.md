# E2E Enhancement Plan: 02-asset-management.spec.ts

**Target:** [02-asset-management.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/02-asset-management.spec.ts)  
**Baseline Score:** 5.8/10  
**Target Score:** 8.0/10  
**Effort Estimate:** ~3 hours

---

## Goals

1. **Reliability** — Eliminate hardcoded waits and improve animation handling
2. **Isolation** — Enable parallel test execution via worker-indexed databases
3. **Domain Coverage** — Verify actual data persistence, not just UI visibility
4. **Cleanup** — Add proper teardown to prevent artifact accumulation
5. **Error Coverage** — Add validation and error path tests

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Enable Worker-Indexed Database Isolation

#### [MODIFY] [02-asset-management.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/02-asset-management.spec.ts)

**Current (L14-16):**
```typescript
test.beforeEach(async ({ page }) => {
    const welcomePage = new WelcomePage(page);
    assetsPage = new AssetsPage(page);
```

**Proposed:**
```typescript
test.beforeEach(async ({ page }, testInfo) => {
    const welcomePage = new WelcomePage(page, testInfo);
    assetsPage = new AssetsPage(page, testInfo);
```

**Rationale:**
- `BasePage` already supports `testInfo` for worker-indexed databases
- Each parallel worker will use `praxis-worker-{index}.db`
- Prevents OPFS contention and cross-test state pollution

---

### 1.2 Remove Hardcoded Wait

#### [MODIFY] [02-asset-management.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/02-asset-management.spec.ts)

**Current (L104-112):**
```typescript
test('should show search input on resource list', async ({ page }) => {
    // Navigate to Assets > Resources
    await assetsPage.goto();
    await assetsPage.waitForOverlay();
    await assetsPage.navigateToResources();

    // Wait for content to load - Resources tab shows ResourceAccordion
    await page.waitForTimeout(500);  // ← REMOVE THIS
});
```

**Proposed Option A (Add Assertion):**
```typescript
test('should show search input on resource list', async ({ page }) => {
    await assetsPage.goto();
    await assetsPage.waitForOverlay();
    await assetsPage.navigateToResources();

    // Verify search input is visible when Resources tab loads
    const searchInput = page.getByPlaceholder(/search/i);
    await expect(searchInput).toBeVisible({ timeout: 5000 });
});
```

**Proposed Option B (Remove Empty Test):**
- Delete this test entirely — it has no assertions and provides no value
- The functionality is implicitly tested by `should open Add Resource dialog`

---

### 1.3 Add Cleanup Hook

#### [MODIFY] [02-asset-management.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/02-asset-management.spec.ts)

**Add after `beforeEach` (L28):**
```typescript
// Track assets created during tests for cleanup
const createdAssets: { type: 'machine' | 'resource'; name: string }[] = [];

test.afterEach(async ({ page }) => {
    // Clean up any assets created during this test
    for (const asset of createdAssets) {
        try {
            if (asset.type === 'machine') {
                await assetsPage.navigateToMachines();
                await assetsPage.deleteMachine(asset.name);
            } else {
                await assetsPage.navigateToResources();
                await assetsPage.deleteResource(asset.name);
            }
        } catch {
            // Asset may not exist if test failed before creation
        }
    }
    createdAssets.length = 0; // Reset for next test
});
```

**Alternative (Simpler):** Rely on worker-indexed DB isolation + `resetdb=1` on navigation. Each test starts fresh.

---

## Phase 2: Page Object Improvements

### 2.1 Fix Silent Warning in verifyAssetVisible

#### [MODIFY] [assets.page.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/page-objects/assets.page.ts)

**Current (L310-328):**
```typescript
async verifyAssetVisible(name: string, timeout: number = 5000) {
    // ... search logic ...
    const assetExists = await this.page.getByText(name, { exact: false }).count() > 0;
    if (!assetExists) {
        console.warn(`[AssetsPage] Asset "${name}" not visible...`);
        // Don't fail - asset creation completed, UI display is a separate concern
    }
}
```

**Proposed:**
```typescript
async verifyAssetVisible(name: string, timeout: number = 5000) {
    await this.navigateToRegistry();
    
    const searchInput = this.page.getByPlaceholder(/search/i).first();
    if (await searchInput.isVisible({ timeout: 2000 }).catch(() => false)) {
        await searchInput.fill(name);
        await this.page.waitForTimeout(300); // Debounce
    }
    
    // FAIL EXPLICITLY if asset not found
    await expect(this.page.getByText(name, { exact: false })).toBeVisible({ timeout });
}
```

---

### 2.2 Accept testInfo in Constructors

#### [MODIFY] [assets.page.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/page-objects/assets.page.ts)

**Current (L13-14):**
```typescript
constructor(page: Page) {
    super(page, '/assets');
```

**Proposed:**
```typescript
constructor(page: Page, testInfo?: TestInfo) {
    super(page, '/assets', testInfo);
```

#### [MODIFY] [welcome.page.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/page-objects/welcome.page.ts)

**Current (L9-10):**
```typescript
constructor(page: Page) {
    super(page, '/');
```

**Proposed:**
```typescript
constructor(page: Page, testInfo?: TestInfo) {
    super(page, '/', testInfo);
```

---

## Phase 3: Domain Verification

### 3.1 Add Data Integrity Verification

#### [MODIFY] [02-asset-management.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/02-asset-management.spec.ts)

**Enhance `should add a new machine` test (L117-124):**

```typescript
test('should add a new machine', async ({ page }) => {
    const machineName = `Test Machine ${Date.now()}`;
    await assetsPage.goto();
    await assetsPage.waitForOverlay();
    await assetsPage.navigateToMachines();
    await assetsPage.createMachine(machineName);
    await assetsPage.verifyAssetVisible(machineName);
    
    // NEW: Verify data integrity via SQLite query
    const machineData = await page.evaluate(async (name) => {
        const db = (window as any).sqliteService?.db;
        if (!db) return null;
        const result = db.exec(`SELECT id, class_name, frontend_id FROM instances WHERE instance_name = '${name}'`);
        if (result.length === 0 || result[0].values.length === 0) return null;
        const [id, className, frontendId] = result[0].values[0];
        return { id, className, frontendId };
    }, machineName);
    
    expect(machineData).not.toBeNull();
    expect(machineData!.className).toBe('LiquidHandler');
});
```

---

### 3.2 Add Reload + Query Verification

**Enhance `should persist machine after page reload` test (L146-157):**

```typescript
test('should persist machine after page reload', async ({ page }) => {
    const machineName = `Persist Machine ${Date.now()}`;
    await assetsPage.goto();
    await assetsPage.waitForOverlay();
    await assetsPage.navigateToMachines();
    await assetsPage.createMachine(machineName);
    await assetsPage.verifyAssetVisible(machineName);
    
    // Get the ID before reload
    const machineId = await page.evaluate(async (name) => {
        const db = (window as any).sqliteService?.db;
        const result = db.exec(`SELECT id FROM instances WHERE instance_name = '${name}'`);
        return result[0]?.values[0]?.[0] ?? null;
    }, machineName);
    
    await page.reload();
    await assetsPage.waitForOverlay();
    
    // NEW: Verify same ID exists after reload (proves OPFS persistence)
    const persistedId = await page.evaluate(async (name) => {
        const db = (window as any).sqliteService?.db;
        const result = db.exec(`SELECT id FROM instances WHERE instance_name = '${name}'`);
        return result[0]?.values[0]?.[0] ?? null;
    }, machineName);
    
    expect(persistedId).toBe(machineId);
    await assetsPage.navigateToMachines();
    await assetsPage.verifyAssetVisible(machineName);
});
```

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Validation Error Tests

#### [ADD] New tests after CRUD block:

```typescript
test.describe('Validation & Error Handling', () => {
    
    test('should prevent machine creation with empty name', async ({ page }) => {
        await assetsPage.goto();
        await assetsPage.waitForOverlay();
        await assetsPage.addMachineButton.click();
        
        const wizard = page.locator('app-asset-wizard');
        await expect(wizard).toBeVisible({ timeout: 15000 });
        
        // Navigate through steps to Config
        // ... category, frontend, backend selection (use first available)
        const categoryCard = wizard.locator('[data-testid^="category-card-"]').first();
        await categoryCard.click();
        await wizard.getByTestId('wizard-next-button').click();
        
        const frontendCard = wizard.locator('[data-testid^="frontend-card-"]').first();
        await expect(frontendCard).toBeVisible({ timeout: 10000 });
        await frontendCard.click();
        await wizard.getByTestId('wizard-next-button').click();
        
        const backendCard = wizard.locator('[data-testid^="backend-card-"]').first();
        await expect(backendCard).toBeVisible({ timeout: 10000 });
        await backendCard.click();
        await wizard.getByTestId('wizard-next-button').click();
        
        // Clear the name input (it may have a default)
        const nameInput = wizard.getByTestId('input-instance-name');
        await nameInput.clear();
        
        // Verify Next button is disabled
        const nextBtn = wizard.getByTestId('wizard-next-button');
        await expect(nextBtn).toBeDisabled();
    });
    
    test('should cancel delete when dialog is dismissed', async ({ page }) => {
        const machineName = `Cancel Delete ${Date.now()}`;
        await assetsPage.goto();
        await assetsPage.waitForOverlay();
        await assetsPage.navigateToMachines();
        await assetsPage.createMachine(machineName);
        await assetsPage.verifyAssetVisible(machineName);
        
        // Navigate back to Machines tab
        await assetsPage.navigateToMachines();
        
        // Set up dialog handler to REJECT deletion
        page.once('dialog', dialog => dialog.dismiss());
        
        // Click delete
        const row = page.locator('tr').filter({ hasText: machineName });
        const deleteBtn = row.getByRole('button', { name: /delete/i });
        await deleteBtn.click();
        
        // Verify machine still exists
        await expect(row).toBeVisible({ timeout: 5000 });
    });
});
```

---

## Verification Plan

### Automated

```bash
# Run all tests in this spec
cd /Users/mar/Projects/praxis/praxis/web-client
npx playwright test e2e/specs/02-asset-management.spec.ts --workers=1 --timeout=120000

# Parallel execution test (verify isolation works)
npx playwright test e2e/specs/02-asset-management.spec.ts --workers=4 --repeat-each=2

# Full suite regression
npx playwright test --workers=4
```

### Manual Verification Checklist

1. **Search for hardcoded waits:**
   ```bash
   grep -n "waitForTimeout" e2e/specs/02-asset-management.spec.ts
   # Expected: 0 occurrences
   ```

2. **Search for force clicks:**
   ```bash
   grep -n "force: true" e2e/specs/02-asset-management.spec.ts
   # Expected: 0 occurrences (POM methods may still have them)
   ```

3. **Verify testInfo usage:**
   ```bash
   grep -n "testInfo" e2e/specs/02-asset-management.spec.ts
   # Expected: Present in beforeEach signature and page constructors
   ```

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/02-asset-management.spec.ts` | Refactor | ~60 lines modified/added |
| `e2e/page-objects/assets.page.ts` | Minor | Constructor + verifyAssetVisible (~10 lines) |
| `e2e/page-objects/welcome.page.ts` | Minor | Constructor (~3 lines) |

---

## Score Improvement Breakdown

| Category | Before | After | Improvement |
|----------|--------|-------|-------------|
| Test Scope | 7 | 8 | +1 (validation tests added) |
| Best Practices | 6 | 8 | +2 (waits removed, testInfo added) |
| Test Value | 8 | 8 | — (already good) |
| Isolation | 4 | 9 | +5 (worker DB + cleanup) |
| Domain Coverage | 4 | 7 | +3 (SQLite verification added) |
| **Overall** | **5.8** | **8.0** | **+2.2** |

---

## Acceptance Criteria

- [ ] Tests pass with `--workers=4` (parallel execution without flakiness)
- [ ] Zero `waitForTimeout` calls in spec file
- [ ] Uses `testInfo` for worker-indexed database isolation
- [ ] `AssetsPage` constructor accepts `testInfo` parameter
- [ ] `verifyAssetVisible` throws on failure (not silent warning)
- [ ] At least one test verifies SQLite data directly via `page.evaluate`
- [ ] Validation error test exists (empty name prevents creation)
- [ ] Delete cancellation test exists
- [ ] Baseline score improves to ≥8.0/10

---

## Implementation Order

1. **Phase 1.1** — Add `testInfo` to constructors (15 min)
2. **Phase 1.2** — Remove/fix the empty test at L104 (5 min)
3. **Phase 2.1** — Fix `verifyAssetVisible` to fail explicitly (10 min)
4. **Phase 3.1** — Add SQLite verification to `should add a new machine` (20 min)
5. **Phase 3.2** — Enhance persistence test with ID comparison (15 min)
6. **Phase 4** — Add validation/error tests (45 min)
7. **Verification** — Run parallel tests, fix any flakiness (30 min)

**Total Time:** ~2.5-3 hours
