# E2E Enhancement Plan: 04-browser-persistence.spec.ts

**Target:** [04-browser-persistence.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/04-browser-persistence.spec.ts)  
**Baseline Score:** 4.4/10  
**Target Score:** 8.0/10  
**Effort Estimate:** 4-6 hours

---

## Goals

1. **Reliability** — Eliminate cross-browser incompatibilities and race conditions
2. **Isolation** — Enable parallel test execution with worker-indexed DBs
3. **Domain Coverage** — Verify actual database state, not just UI visibility
4. **Maintainability** — Use Page Object Model and fixtures consistently

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Replace `import { test, expect } from '@playwright/test'` with `import { test, expect } from '../fixtures/worker-db.fixture'`
- [ ] Pass `testInfo` to all Page Object constructors for worker-indexed DB routing
- [ ] Use `gotoWithWorkerDb()` helper for initial navigation

**Current:**
```typescript
import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
    const welcomePage = new WelcomePage(page);
    await welcomePage.goto();
```

**Target:**
```typescript
import { test, expect, gotoWithWorkerDb } from '../fixtures/worker-db.fixture';

test.beforeEach(async ({ page }, testInfo) => {
    const welcomePage = new WelcomePage(page, testInfo);
    await gotoWithWorkerDb(page, '/', testInfo);
```

### 1.2 Replace Non-Standard IndexedDB Clear
- [ ] Remove raw `page.evaluate()` with `indexedDB.databases()` (Firefox-incompatible)
- [ ] Use `SettingsPage.clearDataButton` if available, or create a `clearAllData()` POM method
- [ ] Alternative: Since we use worker-indexed DBs, we can use fresh DB per test via `resetdb=1`

**Current (Line 42-45):**
```typescript
await page.evaluate(async () => {
    const dbs = await window.indexedDB.databases();
    dbs.forEach(db => window.indexedDB.deleteDatabase(db.name!));
});
```

**Target:**
```typescript
// Option A: Use POM method
await settingsPage.goto();
await settingsPage.clearDataButton.click();
await page.getByRole('button', { name: /Confirm/i }).click();

// Option B: Navigate with resetdb=1 to force fresh DB
await gotoWithWorkerDb(page, '/', testInfo, { resetdb: true });
```

### 1.3 Add Post-Reload DB Ready Wait
- [ ] After any page reload, explicitly wait for `SqliteService.isReady$`
- [ ] This is automatic with `BasePage.goto()` when `testInfo` is provided

**Current (Lines 46-49):**
```typescript
await page.reload();
await assetsPage.goto();
```

**Target:**
```typescript
// BasePage.goto() handles DB ready wait when testInfo is provided
const assetsPage = new AssetsPage(page, testInfo);
await assetsPage.goto();
```

---

## Phase 2: Page Object Refactor

### 2.1 Use Existing POM Navigation Methods
- [ ] Replace `machinesTab.click()` with `navigateToMachines()`

**Current (Lines 50, 59):**
```typescript
await assetsPage.machinesTab.click();
```

**Target:**
```typescript
await assetsPage.navigateToMachines();
```

### 2.2 Remove Unused Imports
- [ ] Delete lines 5-6 (`fs` and `path` are imported but never used)

### 2.3 Extend SettingsPage for Robust Reset
- [ ] Add `clearAllData()` method to SettingsPage that handles both UI and fallback paths
- [ ] Ensure it waits for confirmation dialog and page reload

**Add to SettingsPage:**
```typescript
async clearAllData(): Promise<void> {
    // Try UI button first
    if (await this.clearDataButton.isVisible({ timeout: 2000 })) {
        await this.clearDataButton.click();
        await this.page.getByRole('button', { name: /Confirm/i }).click();
        await this.page.waitForLoadState('domcontentloaded');
        return;
    }
    
    // Fallback: localStorage clear (IndexedDB requires re-init)
    await this.page.evaluate(() => localStorage.clear());
    await this.page.reload();
    await this.page.waitForFunction(
        () => (window as any).sqliteService?.isReady$?.getValue() === true,
        null,
        { timeout: 60000 }
    );
}
```

---

## Phase 3: Domain Verification

### 3.1 Add Deep State Verification
- [ ] After export, query DB to capture actual row count
- [ ] After import, verify identical row count and specific asset exists in DB (not just UI)

**Add verification helper:**
```typescript
async function getAssetCount(page: Page): Promise<number> {
    return page.evaluate(() => {
        const db = (window as any).sqliteService?.db;
        if (!db) return -1;
        const result = db.exec('SELECT COUNT(*) as count FROM assets');
        return result[0]?.values[0]?.[0] ?? 0;
    });
}
```

**Use in test:**
```typescript
// Before export
const preExportCount = await getAssetCount(page);
expect(preExportCount).toBeGreaterThan(0);

// After import
const postImportCount = await getAssetCount(page);
expect(postImportCount).toBe(preExportCount);
```

### 3.2 Add Multi-Entity Verification (Enhancement)
- [ ] Create machine AND resource before export
- [ ] Verify both entities survive import cycle

```typescript
const machineName = `Persist-Machine-${Date.now()}`;
const resourceName = `Persist-Resource-${Date.now()}`;

await assetsPage.createMachine(machineName);
await assetsPage.createResource(resourceName);

// ... export, clear, import ...

await assetsPage.verifyAssetVisible(machineName);
await assetsPage.verifyAssetVisible(resourceName);
```

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Corrupt Database Import
- [ ] Create a test case that attempts to import a malformed file
- [ ] Verify error toast/message appears and app doesn't crash

```typescript
test('should handle invalid database import gracefully', async ({ page }, testInfo) => {
    const settingsPage = new SettingsPage(page, testInfo);
    await settingsPage.goto();
    
    // Create a temporary invalid file
    const invalidContent = 'not a sqlite database';
    const tempFile = '/tmp/invalid.db';
    await fs.promises.writeFile(tempFile, invalidContent);
    
    // Attempt import
    await settingsPage.importDatabase(tempFile);
    
    // Expect error handling
    await expect(page.getByRole('alert')).toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/invalid|corrupt|error/i)).toBeVisible();
});
```

### 4.2 Empty Database Export
- [ ] Test export when no assets exist
- [ ] Verify file is still valid and can be re-imported

---

## Verification Plan

### Automated
```bash
# Single-worker test (basic validation)
npx playwright test e2e/specs/04-browser-persistence.spec.ts --workers=1

# Multi-worker test (parallel isolation validation)
npx playwright test e2e/specs/04-browser-persistence.spec.ts --workers=4

# Cross-browser (Firefox/WebKit) - validates no indexedDB.databases() usage
npx playwright test e2e/specs/04-browser-persistence.spec.ts --project=firefox
```

### Manual Validation Checklist
- [ ] Test creates unique asset, exports, clears, imports, verifies
- [ ] No `waitForTimeout` calls remain (except in POMs with documented rationale)
- [ ] No `force: true` clicks remain
- [ ] Test passes in Firefox (no `indexedDB.databases()` dependency)

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/04-browser-persistence.spec.ts` | Refactor | ~40 lines |
| `e2e/page-objects/settings.page.ts` | Enhance | +15 lines (`clearAllData` method) |

---

## Acceptance Criteria

- [ ] Tests pass with parallel execution (`--workers=4`)
- [ ] Zero `force: true` clicks in spec file
- [ ] Zero `waitForTimeout` calls in spec file
- [ ] Uses `worker-db.fixture` for isolation
- [ ] Uses `navigateToMachines()` instead of direct tab click
- [ ] Verifies domain state (DB query) not just UI visibility
- [ ] No browser-specific API usage (`indexedDB.databases()` removed)
- [ ] Baseline score improves to ≥8.0/10

---

## Refactored Test (Target State)

```typescript
import { test, expect, gotoWithWorkerDb } from '../fixtures/worker-db.fixture';
import { WelcomePage } from '../page-objects/welcome.page';
import { AssetsPage } from '../page-objects/assets.page';
import { SettingsPage } from '../page-objects/settings.page';

test.describe('Browser Mode Specifics (DB Persistence)', () => {
    test.beforeEach(async ({ page }, testInfo) => {
        await gotoWithWorkerDb(page, '/', testInfo);
        const welcomePage = new WelcomePage(page, testInfo);
        await welcomePage.handleSplashScreen();
    });

    test('should export and import database preserving data', async ({ page }, testInfo) => {
        const assetsPage = new AssetsPage(page, testInfo);
        const settingsPage = new SettingsPage(page, testInfo);
        const uniqueName = `Persist-${Date.now()}`;

        // 1. Create Data
        await assetsPage.goto();
        await assetsPage.createMachine(uniqueName);
        await assetsPage.navigateToRegistry();
        await assetsPage.verifyAssetVisible(uniqueName);

        // 2. Verify DB state before export
        const preExportCount = await page.evaluate(() => {
            const db = (window as any).sqliteService?.db;
            return db ? db.exec('SELECT COUNT(*) FROM assets')[0]?.values[0]?.[0] : 0;
        });
        expect(preExportCount).toBeGreaterThan(0);

        // 3. Export DB
        await settingsPage.goto();
        const downloadPath = await settingsPage.exportDatabase();
        expect(downloadPath).toBeTruthy();

        // 4. Clear Data (use fresh DB via navigation with resetdb=1)
        await gotoWithWorkerDb(page, '/assets', testInfo, { resetdb: true });
        await assetsPage.navigateToMachines();
        await assetsPage.verifyAssetNotVisible(uniqueName);

        // 5. Import DB
        await settingsPage.goto();
        await settingsPage.importDatabase(downloadPath!);

        // 6. Verify Data Restored (UI)
        await assetsPage.goto();
        await assetsPage.navigateToMachines();
        await assetsPage.verifyAssetVisible(uniqueName);

        // 7. Verify Data Restored (DB state)
        const postImportCount = await page.evaluate(() => {
            const db = (window as any).sqliteService?.db;
            return db ? db.exec('SELECT COUNT(*) FROM assets')[0]?.values[0]?.[0] : 0;
        });
        expect(postImportCount).toBe(preExportCount);
    });
});
```
