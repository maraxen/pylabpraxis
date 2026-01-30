# E2E Enhancement Plan: asset-inventory.spec.ts

**Target:** [asset-inventory.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/asset-inventory.spec.ts)  
**Baseline Score:** 4.8/10  
**Target Score:** 8.0/10  
**Effort Estimate:** 3-4 hours

---

## Goals

1. **Reliability** — Eliminate hardcoded `waitForTimeout()` calls and implicit catch blocks
2. **Isolation** — Enable parallel test execution via worker-indexed DB fixture
3. **Domain Coverage** — Verify actual SQLite data integrity, not just UI presence
4. **Maintainability** — Refactor to use existing `AssetsPage` POM

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Change import from `@playwright/test` → `../fixtures/app.fixture`
- [ ] Remove manual `beforeEach` navigation (fixture handles it)
- [ ] Remove inline Welcome Dialog handling (fixture handles it)

**Before:**
```typescript
import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForURL('**/app/home', { timeout: 15000 }).catch(() => { ... });
    // ... manual dialog handling
});
```

**After:**
```typescript
import { test, expect } from '../fixtures/app.fixture';
// Fixture handles: navigation, DB isolation, Welcome Dialog dismissal
```

### 1.2 Eliminate Hardcoded Waits
- [ ] Line 75: Replace `waitForTimeout(500)` with waitFor on autocomplete options
- [ ] Line 88: Same pattern for fallback autocomplete
- [ ] Line 152: Same pattern for resource model autocomplete

**Before:**
```typescript
await machineTypeInput.fill('Opentrons');
await page.waitForTimeout(500); // BAD: arbitrary wait
await page.getByRole('option').first().click();
```

**After:**
```typescript
await machineTypeInput.fill('Opentrons');
await page.getByRole('option').first().waitFor({ state: 'visible', timeout: 5000 });
await page.getByRole('option').first().click();
```

### 1.3 Replace CSS Selectors with User-Facing Locators
- [ ] Line 44, 116, 129, 177: Replace `.sidebar-rail a[href="/app/assets"]` with role/testid
- [ ] Line 140, 145: Replace `.category-card` with testid pattern

**Before:**
```typescript
const assetsLink = page.locator('.sidebar-rail a[href="/app/assets"]');
```

**After:**
```typescript
const assetsLink = page.getByRole('link', { name: /Assets/i });
// OR: page.getByTestId('sidebar-assets-link');
```

### 1.4 Fix Silent Catch Block
- [ ] Line 15-17: Either assert redirect happens or use explicit waitFor

**Before:**
```typescript
await page.waitForURL('**/app/home', { timeout: 15000 }).catch(() => {
    console.log('Did not redirect to /app/home automatically');
});
```

**After (if fixture used, this is unnecessary):**
```typescript
// Fixture navigates with mode=browser, which handles routing
```

---

## Phase 2: Page Object Refactor

### 2.1 Use AssetsPage POM
The existing `assets.page.ts` already provides:
- `createMachine(name, category, modelQuery)`
- `createResource(name, category, modelQuery)`
- `navigateToMachines()`
- `navigateToRegistry()`
- `deleteMachine(name)`
- `deleteResource(name)`

- [ ] Import and instantiate `AssetsPage`
- [ ] Replace inline machine creation with `assetsPage.createMachine()`
- [ ] Replace inline resource creation with `assetsPage.createResource()`
- [ ] Replace inline tab navigation with POM methods

**Before (inline logic):**
```typescript
await page.getByRole('button', { name: /Add Machine/i }).click();
await expect(page.getByRole('heading', { name: /Add New Machine/i })).toBeVisible();
// ... 20+ lines of dialog interaction
```

**After (POM):**
```typescript
const assetsPage = new AssetsPage(page);
await assetsPage.goto(); // Handles navigation with DB isolation
await assetsPage.createMachine(machineName, 'LiquidHandler', 'Hamilton');
await assetsPage.navigateToMachines();
```

### 2.2 Add Cleanup in afterEach
- [ ] Track created assets in test scope
- [ ] Delete in `afterEach` to ensure isolation

```typescript
test.afterEach(async ({ page }) => {
    const assetsPage = new AssetsPage(page);
    // Cleanup any assets created during the test
    try {
        await assetsPage.navigateToMachines();
        await assetsPage.deleteMachine(testMachineName).catch(() => {});
        await assetsPage.navigateToRegistry();
        await assetsPage.deleteResource(testResourceName).catch(() => {});
    } catch {
        // Cleanup failure shouldn't fail test
    }
});
```

---

## Phase 3: Domain Verification

### 3.1 SQLite Data Integrity Assertions
- [ ] After creating machine, verify DB record structure
- [ ] After reload, verify record still has correct fields

```typescript
// Verify data integrity after creation
const machineData = await page.evaluate((name) => {
    const db = (window as any).sqliteService;
    if (!db) return null;
    return db.execSync(`SELECT * FROM machines WHERE name = ?`, [name]);
}, machineName);

expect(machineData).toBeDefined();
expect(machineData[0].name).toBe(machineName);
expect(machineData[0].machine_type_id).toBeDefined();
```

### 3.2 Persistence Verification Enhancement
- [ ] Verify record count before/after reload (not just visibility)

```typescript
const countBefore = await page.evaluate(() => {
    const db = (window as any).sqliteService;
    return db.execSync('SELECT COUNT(*) as count FROM machines')[0].count;
});

await page.reload();
await waitForDbReady(page);

const countAfter = await page.evaluate(() => {
    const db = (window as any).sqliteService;
    return db.execSync('SELECT COUNT(*) as count FROM machines')[0].count;
});

expect(countAfter).toBe(countBefore);
```

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Validation Error Tests
- [ ] Add test: Submit empty machine name → expect validation error
- [ ] Add test: Duplicate machine name → expect error or unique suffix

```typescript
test('should show validation error for empty machine name', async ({ page }) => {
    const assetsPage = new AssetsPage(page);
    await assetsPage.goto();
    
    await assetsPage.addMachineButton.click();
    // Complete wizard without filling name...
    // Expect Save button to be disabled or error message shown
});
```

### 4.2 Autocomplete Edge Cases
- [ ] Add test: Search query with no matching results → graceful handling

---

## Verification Plan

### Automated
```bash
# Single worker (baseline)
npx playwright test e2e/specs/asset-inventory.spec.ts --workers=1

# Parallel execution (target)
npx playwright test e2e/specs/asset-inventory.spec.ts --workers=4
```

### Manual Checklist
- [ ] All tests pass on first run
- [ ] Tests pass when run 5x consecutively  
- [ ] Tests pass in parallel with other asset tests
- [ ] No `waitForTimeout` in codebase search
- [ ] No `force: true` clicks

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/asset-inventory.spec.ts` | Major refactor | ~150 lines → ~80 lines |
| `e2e/page-objects/assets.page.ts` | Minor (if needed) | Add testid selectors |

---

## Refactored Test Structure (Target State)

```typescript
import { test, expect } from '../fixtures/app.fixture';
import { AssetsPage } from '../page-objects/assets.page';

test.describe('Asset Inventory Persistence', () => {
    let assetsPage: AssetsPage;
    const testMachineName = `E2E-Machine-${Date.now()}`;
    const testResourceName = `E2E-Resource-${Date.now()}`;

    test.beforeEach(async ({ page }) => {
        assetsPage = new AssetsPage(page);
        // Fixture handles: DB isolation, welcome dialog, app shell wait
    });

    test.afterEach(async ({ page }) => {
        // Cleanup created assets
        await assetsPage.navigateToMachines();
        await assetsPage.deleteMachine(testMachineName).catch(() => {});
        await assetsPage.navigateToRegistry();
        await assetsPage.deleteResource(testResourceName).catch(() => {});
    });

    test('machine persists across reloads', async ({ page }) => {
        await assetsPage.goto();
        await assetsPage.createMachine(testMachineName, 'LiquidHandler', 'Hamilton');
        
        await assetsPage.navigateToMachines();
        await expect(page.getByText(testMachineName)).toBeVisible();

        // Verify DB integrity
        const dbRecord = await page.evaluate((name) => 
            (window as any).sqliteService.execSync(
                'SELECT * FROM machines WHERE name = ?', [name]
            ), testMachineName);
        expect(dbRecord.length).toBe(1);

        // Persistence after reload
        await page.reload();
        await assetsPage.navigateToMachines();
        await expect(page.getByText(testMachineName)).toBeVisible();
    });

    test('resource persists across reloads', async ({ page }) => {
        await assetsPage.goto();
        await assetsPage.createResource(testResourceName, 'Plate', '96');
        
        await assetsPage.navigateToRegistry();
        await expect(page.getByText(testResourceName)).toBeVisible();

        await page.reload();
        await assetsPage.navigateToRegistry();
        await expect(page.getByText(testResourceName)).toBeVisible();
    });
});
```

---

## Acceptance Criteria

- [ ] Tests pass with `--workers=4` (parallel execution)
- [ ] Zero `force: true` clicks
- [ ] Zero `waitForTimeout` calls
- [ ] 100% POM usage for asset operations
- [ ] SQLite data integrity verified (not just UI presence)
- [ ] Cleanup in `afterEach` for isolation
- [ ] Baseline score improves from 4.8 → ≥8.0/10

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| POM methods don't match current UI | Medium | Verify `AssetsPage.createMachine()` against current wizard flow |
| `SqliteService` not exposed on window | Low | Check if `window.sqliteService` is accessible; if not, use Angular's `ng.getComponent()` pattern |
| DB isolation breaks existing data | Low | Worker-indexed DBs won't affect other tests or local dev state |
