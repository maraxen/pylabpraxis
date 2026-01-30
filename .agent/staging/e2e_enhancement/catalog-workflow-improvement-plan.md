# E2E Enhancement Plan: catalog-workflow.spec.ts

**Target:** [catalog-workflow.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/catalog-workflow.spec.ts)  
**Baseline Score:** 3.2/10  
**Target Score:** 8.0/10  
**Effort Estimate:** 3-4 hours

---

## Goals

1. **Reliability** — Enable parallel worker execution with isolated databases
2. **Isolation** — Use worker-indexed DB fixture for OPFS isolation
3. **Domain Coverage** — Verify machine creation persists and appears in inventory
4. **Maintainability** — Extract Inventory Dialog page object for reuse

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Replace `import { test, expect } from '@playwright/test'` with:
  ```typescript
  import { test, expect, gotoWithWorkerDb } from '../fixtures/worker-db.fixture';
  ```
- [ ] Replace `page.goto('/app/playground?resetdb=1')` with:
  ```typescript
  await gotoWithWorkerDb(page, '/app/playground', testInfo);
  ```
- [ ] Add `testInfo` parameter to test signature:
  ```typescript
  test('should show catalog tab...', async ({ page }, testInfo) => {
  ```

### 1.2 Eliminate Brittle Onboarding Handling
- [ ] Replace try-catch with proper conditional:
  ```typescript
  const skipBtn = page.getByRole('button', { name: /Skip/i });
  if (await skipBtn.isVisible({ timeout: 2000 })) {
      await skipBtn.click();
  }
  ```

### 1.3 Replace Implementation-Specific Selectors
- [ ] Replace `mat-card-title` with:
  ```typescript
  page.getByRole('heading', { level: 3 }).first()
  // OR add data-testid="catalog-machine-title" to component
  ```

---

## Phase 2: Page Object Refactor

### 2.1 Create InventoryDialogPage

Create `e2e/page-objects/inventory-dialog.page.ts`:

```typescript
import { Page, Locator, expect } from '@playwright/test';

export class InventoryDialogPage {
    private readonly page: Page;
    private readonly dialog: Locator;
    
    // Tab Locators
    readonly catalogTab: Locator;
    readonly quickAddTab: Locator;
    readonly browseAddTab: Locator;
    readonly currentItemsTab: Locator;
    
    constructor(page: Page) {
        this.page = page;
        this.dialog = page.locator('app-inventory-dialog');
        
        this.catalogTab = page.getByRole('tab', { name: 'Catalog' });
        this.quickAddTab = page.getByRole('tab', { name: 'Quick Add' });
        this.browseAddTab = page.getByRole('tab', { name: 'Browse & Add' });
        this.currentItemsTab = page.getByRole('tab', { name: 'Current Items' });
    }
    
    async open() {
        await this.page.getByLabel('Open Inventory Dialog').click();
        await this.dialog.waitFor({ state: 'visible' });
    }
    
    async selectTab(tabName: 'Catalog' | 'Quick Add' | 'Browse & Add' | 'Current Items') {
        const tab = this.page.getByRole('tab', { name: tabName });
        await tab.click();
        await expect(tab).toHaveAttribute('aria-selected', 'true');
    }
    
    async getCatalogItems(): Promise<Locator> {
        await this.catalogTab.click();
        const items = this.page.locator('[data-testid="catalog-item"]');
        await items.first().waitFor({ state: 'visible', timeout: 15000 });
        return items;
    }
    
    async addSimulatedMachine(index: number = 0) {
        const addButtons = this.page.getByRole('button', { name: 'Add Simulated' });
        await addButtons.nth(index).click();
    }
    
    async getMachinesInInventory(): Promise<string[]> {
        await this.selectTab('Current Items');
        const machines = this.page.locator('[data-testid="inventory-machine-name"]');
        const count = await machines.count();
        const names: string[] = [];
        for (let i = 0; i < count; i++) {
            names.push(await machines.nth(i).innerText());
        }
        return names;
    }
    
    async assertMachineInInventory(namePattern: string | RegExp) {
        await this.selectTab('Current Items');
        const matcher = typeof namePattern === 'string' 
            ? new RegExp(namePattern, 'i') 
            : namePattern;
        await expect(this.page.getByText(matcher).first()).toBeVisible({ timeout: 10000 });
    }
}
```

### 2.2 Refactor Test to Use POM

```typescript
import { test, expect, gotoWithWorkerDb } from '../fixtures/worker-db.fixture';
import { InventoryDialogPage } from '../page-objects/inventory-dialog.page';
import { WelcomePage } from '../page-objects/welcome.page';

test.describe('Catalog to Inventory Workflow', () => {
    test('should add simulated machine from catalog', async ({ page }, testInfo) => {
        // Setup
        await gotoWithWorkerDb(page, '/app/playground', testInfo);
        const welcomePage = new WelcomePage(page);
        await welcomePage.dismissOnboarding();
        
        // Open inventory and verify catalog
        const inventory = new InventoryDialogPage(page);
        await inventory.open();
        
        await expect(inventory.catalogTab).toBeVisible();
        await expect(inventory.catalogTab).toHaveAttribute('aria-selected', 'true');
        
        // Add simulated machine
        await inventory.addSimulatedMachine(0);
        
        // Verify navigation to Browse & Add
        await expect(inventory.browseAddTab).toHaveAttribute('aria-selected', 'true');
        
        // CRITICAL: Verify machine was actually created
        await inventory.assertMachineInInventory(/Simulation|Simulated/);
    });
});
```

---

## Phase 3: Domain Verification

### 3.1 Post-Action Verification

Add machine creation outcome check:

```typescript
// After adding simulated machine, verify it persists
await inventory.selectTab('Current Items');
const machines = await inventory.getMachinesInInventory();
expect(machines.length).toBeGreaterThan(0);
expect(machines.some(m => /simulation|simulated/i.test(m))).toBe(true);
```

### 3.2 SQLite State Verification

Add deep state verification using Angular's internal API:

```typescript
// Verify machine exists in SQLite database
const machineCount = await page.evaluate(async () => {
    const sqliteService = (window as any).sqliteService;
    if (!sqliteService?.db) return 0;
    const result = await sqliteService.db.exec(
        "SELECT COUNT(*) as count FROM machines WHERE type = 'simulation'"
    );
    return result[0]?.values?.[0]?.[0] ?? 0;
});
expect(machineCount).toBeGreaterThan(0);
```

### 3.3 Persistence Verification

Add reload-and-verify pattern:

```typescript
test('simulated machine persists after reload', async ({ page }, testInfo) => {
    // ... add machine via catalog ...
    
    // Reload page (without resetdb to preserve data)
    await gotoWithWorkerDb(page, '/app/playground', testInfo, { resetdb: false });
    
    const inventory = new InventoryDialogPage(page);
    await inventory.open();
    await inventory.assertMachineInInventory(/Simulation/);
});
```

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Catalog Load Failure

```typescript
test('handles catalog load failure gracefully', async ({ page }, testInfo) => {
    // Intercept catalog API and force failure
    await page.route('**/api/catalog/machines', route => {
        route.fulfill({ status: 500, body: 'Internal Server Error' });
    });
    
    await gotoWithWorkerDb(page, '/app/playground', testInfo);
    const inventory = new InventoryDialogPage(page);
    await inventory.open();
    
    // Should show error state, not blank/broken UI
    await expect(page.getByText(/failed to load|error|try again/i)).toBeVisible();
});
```

### 4.2 Duplicate Machine Handling

```typescript
test('prevents duplicate simulated machine names', async ({ page }, testInfo) => {
    // Add first machine
    // ... 
    
    // Try to add same machine again
    await inventory.addSimulatedMachine(0);
    
    // Should show conflict/rename dialog or increment name
    // Verify appropriate handling
});
```

---

## Verification Plan

### Automated
```bash
# Run in isolation
npx playwright test e2e/specs/catalog-workflow.spec.ts --headed

# Verify parallel execution works
npx playwright test e2e/specs/catalog-workflow.spec.ts --workers=4 --repeat-each=3

# Full regression
npx playwright test --grep "catalog|inventory" --workers=4
```

### Manual Verification Checklist
- [ ] Test passes when run with 4 workers
- [ ] No `force: true` in click operations
- [ ] No hardcoded `waitForTimeout` calls
- [ ] Machine appears in "Current Items" after creation
- [ ] SQLite query confirms persistence

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/catalog-workflow.spec.ts` | Refactor | ~60 → ~40 |
| `e2e/page-objects/inventory-dialog.page.ts` | Create | ~80 (new) |
| `e2e/page-objects/welcome.page.ts` | Update | Add `dismissOnboarding()` if missing |

---

## Component Integration Points

```
┌─────────────────────────────────────────────────────────────────┐
│               CATALOG-WORKFLOW TEST DEPENDENCIES                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  worker-db.fixture.ts                                          │
│  └── gotoWithWorkerDb()  ←── Required for isolation            │
│                                                                 │
│  page-objects/                                                  │
│  ├── inventory-dialog.page.ts  ←── NEW: Extract dialog logic   │
│  ├── welcome.page.ts           ←── Onboarding dismissal        │
│  └── base.page.ts              ←── Overlay handling            │
│                                                                 │
│  Angular Components:                                            │
│  ├── app-inventory-dialog      ←── Main dialog component       │
│  ├── mat-tab-group             ←── Tab navigation              │
│  └── catalog machine cards     ←── Definition display          │
│                                                                 │
│  Services:                                                      │
│  ├── SqliteService             ←── Database readiness          │
│  └── MachineService            ←── Machine CRUD operations     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Acceptance Criteria

- [ ] Tests pass with `--workers=4` (parallel execution)
- [ ] Zero `force: true` clicks
- [ ] Zero `waitForTimeout` calls
- [ ] Uses `InventoryDialogPage` POM
- [ ] Verifies machine appears in "Current Items" tab
- [ ] SQLite state verification confirms persistence
- [ ] Baseline score improves to ≥ 8.0/10

---

## Post-Implementation Scoring

| Category | Before | After | Delta |
|----------|--------|-------|-------|
| Test Scope | 4/10 | 8/10 | +4 |
| Best Practices | 3/10 | 8/10 | +5 |
| Test Value | 5/10 | 8/10 | +3 |
| Isolation | 2/10 | 9/10 | +7 |
| Domain Coverage | 2/10 | 7/10 | +5 |
| **Overall** | **3.2/10** | **8.0/10** | **+4.8** |
