# E2E Enhancement Plan: verify-inventory.spec.ts

**Target:** [verify-inventory.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/verify-inventory.spec.ts)  
**Baseline Score:** 4.0/10  
**Target Score:** 8.0/10  
**Effort Estimate:** 3-4 hours

---

## Goals

1. **Reliability** — Eliminate flaky patterns and enable parallel execution
2. **Isolation** — Use worker-indexed database for safe concurrency
3. **Domain Coverage** — Complete the asset addition workflow and verify state
4. **Maintainability** — Abstract all selectors into a Page Object Model

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Import `workerDbTest` fixture from `e2e/fixtures/worker-db.fixture`
- [ ] Replace `test.beforeEach` with fixture-based setup
- [ ] Ensure worker-indexed database name is applied (`praxis-worker-{index}.db`)

**Current Pattern (Anti-Pattern):**
```typescript
test.beforeEach(async ({ page }) => {
  await page.goto('/app/playground', { waitUntil: 'networkidle' });
  await page.waitForFunction(() => ...sqliteService?.isReady$...);
});
```

**Target Pattern:**
```typescript
import { test } from '../fixtures/worker-db.fixture';

test('should load definitions...', async ({ page, dbName }) => {
  const playgroundPage = new PlaygroundPage(page, dbName);
  await playgroundPage.goto();
  await playgroundPage.waitForReady();
});
```

### 1.2 Eliminate Hardcoded Waits
- [ ] Remove `waitForLoadState('networkidle')` — replace with `waitFor(sidebar)` or `waitFor(dialog)`
- [ ] Remove magic timeout numbers — use centralized constants or POM methods

**Target:**
| Current | Replacement |
|---------|-------------|
| `waitFor({ timeout: 5000 })` | `await inventoryDialog.waitForCategoryChips()` |
| `waitFor({ timeout: 10000 })` | `await inventoryDialog.waitForAssetList()` |
| `networkidle` | `waitForFunction(() => sqliteService.isReady$...)` |

### 1.3 Replace Fragile Locators
- [ ] Replace `.mdc-tab` with `getByRole('tab', { name: 'Browse & Add' })`
- [ ] Replace `.type-card` with `getByRole('button', { name: /Machine/i })` or `getByTestId('type-card-machine')`
- [ ] Replace `mat-chip-option` with `getByRole('option')` or `getByLabel`

---

## Phase 2: Page Object Refactor (Priority: High)

### 2.1 Create InventoryDialogPage

Create `/e2e/page-objects/inventory-dialog.page.ts`:

```typescript
import { Page, Locator, expect } from '@playwright/test';

export class InventoryDialogPage {
    private page: Page;
    
    // Locators - User-Facing
    readonly dialog: Locator;
    readonly browseTab: Locator;
    readonly machineTypeCard: Locator;
    readonly continueButton: Locator;
    readonly categoryChips: Locator;
    readonly assetList: Locator;
    readonly emptyState: Locator;
    
    constructor(page: Page) {
        this.page = page;
        this.dialog = page.getByRole('dialog', { name: /Inventory/i });
        this.browseTab = page.getByRole('tab', { name: 'Browse & Add' });
        this.machineTypeCard = page.getByRole('button', { name: /Machine/i });
        this.continueButton = page.getByRole('button', { name: 'Continue' });
        this.categoryChips = page.getByRole('listbox').locator('[role="option"]');
        this.assetList = page.getByRole('listbox', { name: /Assets/i });
        this.emptyState = page.locator('[data-testid="empty-state"]');
    }
    
    async selectBrowseTab() {
        await this.browseTab.click();
        await expect(this.machineTypeCard).toBeVisible();
    }
    
    async selectMachineType() {
        await this.machineTypeCard.click();
        await expect(this.continueButton).toBeEnabled();
    }
    
    async selectCategory(name: string) {
        const chip = this.categoryChips.filter({ hasText: name });
        await chip.click();
    }
    
    async getCategories(): Promise<string[]> {
        await expect(this.categoryChips.first()).toBeVisible();
        return this.categoryChips.allInnerTexts();
    }
    
    async continueToNextStep() {
        await this.continueButton.click();
    }
    
    async waitForAssetList() {
        await expect(this.assetList).toBeVisible({ timeout: 10000 });
    }
}
```

### 2.2 Create PlaygroundPage

Create `/e2e/page-objects/playground.page.ts`:

```typescript
import { Page, Locator, expect, TestInfo } from '@playwright/test';
import { BasePage } from './base.page';
import { InventoryDialogPage } from './inventory-dialog.page';

export class PlaygroundPage extends BasePage {
    readonly openInventoryButton: Locator;
    
    constructor(page: Page, testInfo?: TestInfo) {
        super(page, '/app/playground', testInfo);
        this.openInventoryButton = page.getByRole('button', { name: 'Open Inventory Dialog' });
    }
    
    async openInventoryDialog(): Promise<InventoryDialogPage> {
        await this.openInventoryButton.click();
        const dialog = new InventoryDialogPage(this.page);
        await expect(dialog.dialog).toBeVisible();
        return dialog;
    }
    
    async getPlaygroundAssets(): Promise<any[]> {
        return this.page.evaluate(() => {
            const ng = (window as any).ng;
            const app = ng.getComponent(document.querySelector('app-root'));
            return app?.playgroundService?.assets$ ?? [];
        });
    }
}
```

### 2.3 Migrate Test to Use POMs

```typescript
import { test, expect } from '../fixtures/worker-db.fixture';
import { PlaygroundPage } from '../page-objects/playground.page';

test.describe('Inventory Dialog Verification', () => {
    test('should load definitions and allow filtering by machine category', async ({ page, testInfo }) => {
        const playground = new PlaygroundPage(page, testInfo);
        await playground.goto();
        
        const inventoryDialog = await playground.openInventoryDialog();
        await inventoryDialog.selectBrowseTab();
        await inventoryDialog.selectMachineType();
        await inventoryDialog.continueToNextStep();
        
        const categories = await inventoryDialog.getCategories();
        expect(categories.length).toBeGreaterThan(0);
        expect(categories).toContain('Liquid Handler');
        
        await inventoryDialog.selectCategory('Liquid Handler');
        await inventoryDialog.continueToNextStep();
        await inventoryDialog.waitForAssetList();
    });
});
```

---

## Phase 3: Domain Verification (Priority: Medium)

### 3.1 Complete Asset Addition Flow
- [ ] After selecting an asset, click "Add" and verify it appears in the playground
- [ ] Use `PlaygroundPage.getPlaygroundAssets()` to verify internal state

```typescript
test('should add selected asset to playground', async ({ page, testInfo }) => {
    const playground = new PlaygroundPage(page, testInfo);
    await playground.goto();
    
    const inventoryDialog = await playground.openInventoryDialog();
    // ...navigate to asset list...
    
    const asset = page.getByRole('option', { name: /Opentrons OT-2/i });
    await asset.click();
    await page.getByRole('button', { name: 'Add' }).click();
    
    // Verify UI
    await expect(page.getByTestId('playground-asset-card')).toBeVisible();
    
    // Verify Internal State
    const assets = await playground.getPlaygroundAssets();
    expect(assets).toHaveLength(1);
    expect(assets[0].definition.name).toBe('Opentrons OT-2');
});
```

### 3.2 Database Integrity Verification
- [ ] Verify expected tables exist (`machine_definitions`, `consumable_definitions`, etc.)
- [ ] Verify expected row counts match seeded data

```typescript
async function verifyDatabaseIntegrity(page: Page) {
    const result = await page.evaluate(async () => {
        const db = await (window as any).sqliteService?.getDatabase();
        const tables = db.exec("SELECT name FROM sqlite_master WHERE type='table'");
        const machineCount = db.exec("SELECT COUNT(*) FROM machine_definitions")[0].values[0][0];
        return { tables: tables[0].values.flat(), machineCount };
    });
    
    expect(result.tables).toContain('machine_definitions');
    expect(result.machineCount).toBeGreaterThan(5); // Known baseline
}
```

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Empty Database Scenario
- [ ] Test behavior when database has no definitions

```typescript
test('should show empty state when no definitions', async ({ page }) => {
    // Use a special resetdb mode that creates empty tables
    await page.goto('/app/playground?resetdb=empty');
    // ...
    await expect(inventoryDialog.emptyState).toBeVisible();
    await expect(inventoryDialog.emptyState).toContainText('No definitions found');
});
```

### 4.2 Malformed Definition Handling
- [ ] Inject a malformed definition and verify graceful degradation

---

## Verification Plan

### Automated
```bash
# Single worker (baseline)
npx playwright test e2e/specs/verify-inventory.spec.ts --workers=1

# Parallel execution (target)
npx playwright test e2e/specs/verify-inventory.spec.ts --workers=4

# With trace for debugging
npx playwright test e2e/specs/verify-inventory.spec.ts --trace=on
```

### Manual Checklist
- [ ] Test passes on fresh database
- [ ] Test passes after previous test has modified state
- [ ] No warnings in Playwright output about force clicks or timeouts
- [ ] All assertions use user-visible text or semantic roles

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/verify-inventory.spec.ts` | Refactor | 80-100 |
| `e2e/page-objects/inventory-dialog.page.ts` | Create | ~80 |
| `e2e/page-objects/playground.page.ts` | Create | ~50 |
| `e2e/fixtures/worker-db.fixture.ts` | Reference | 0 (import only) |

---

## Acceptance Criteria

- [ ] Tests pass with `--workers=4` (parallel execution)
- [ ] Zero `.mdc-*` or `.mat-*` internal Material selectors
- [ ] Zero `waitForLoadState('networkidle')` calls
- [ ] Uses `InventoryDialogPage` and `PlaygroundPage` POMs
- [ ] Verifies at least one asset is successfully added to playground state
- [ ] Baseline score improves from 4.0/10 to ≥8.0/10

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Existing tests depend on global state | Use worker isolation; each test gets fresh DB |
| Material components lack accessible names | Add `data-testid` attributes or advocate for ARIA labels in Angular components |
| Long test execution time | Reuse browser context; minimize navigation; consider test.describe.serial for related flows |
