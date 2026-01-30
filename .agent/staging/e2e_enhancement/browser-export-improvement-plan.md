# E2E Enhancement Plan: browser-export.spec.ts

**Target:** [browser-export.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/browser-export.spec.ts)  
**Baseline Score:** 4.6/10  
**Target Score:** 8.0/10  
**Effort Estimate:** 3-4 hours

---

## Goals

1. **Reliability** — Eliminate flaky patterns and add proper test isolation
2. **Isolation** — Enable parallel test execution with worker-indexed databases
3. **Domain Coverage** — Verify actual database export/import operations
4. **Maintainability** — Use existing Page Object Model consistently

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Refactor to use `SettingsPage` with `testInfo` for worker-indexed DB isolation
- [ ] Use `BasePage.goto()` instead of raw `page.goto('/app/settings')`
- [ ] Ensure `mode=browser` is consistently enforced

**Before:**
```typescript
test.beforeEach(async ({ page }) => {
    await page.goto('/app/settings');
    // ...
});
```

**After:**
```typescript
import { SettingsPage } from '../page-objects/settings.page';

let settingsPage: SettingsPage;

test.beforeEach(async ({ page }, testInfo) => {
    settingsPage = new SettingsPage(page, testInfo);
    await settingsPage.goto();
    await settingsPage.dismissWelcomeDialogIfPresent();
});
```

### 1.2 Replace CSS Selector with User-Facing Locator
- [ ] Change `page.locator('app-confirmation-dialog')` to `page.getByRole('dialog')`
- [ ] Use dialog title text for specificity

**Before:**
```typescript
const dialog = page.locator('app-confirmation-dialog');
await expect(dialog).toBeVisible();
```

**After:**
```typescript
const dialog = page.getByRole('dialog', { name: /Import Database/i });
await expect(dialog).toBeVisible();
```

### 1.3 Add Explicit Timeout Documentation
- [ ] Replace magic number `timeout: 15000` with named constant and comment
- [ ] Consider reducing timeout or explaining why 15s is necessary

---

## Phase 2: Page Object Refactor

### 2.1 Use Existing SettingsPage Methods
- [ ] Replace inline export logic with `settingsPage.exportDatabase()`
- [ ] Add new POM method `openImportDialogAndCancel()` for safe import flow

**Current POM Methods Available:**
| Method | Status |
|--------|--------|
| `exportDatabase()` | ✅ Exists - use this |
| `importDatabase(filePath)` | ⚠️ Needs modification - add cancel option |
| `resetState()` | ✅ Exists - use for cleanup |

### 2.2 Add Missing POM Methods
- [ ] Add `dismissWelcomeDialogIfPresent()` to `BasePage` or `SettingsPage`
- [ ] Add `openImportDialogAndCancel()` method to test cancel flow safely

```typescript
// settings.page.ts addition
async openImportDialogAndCancel(): Promise<void> {
    const fileChooserPromise = this.page.waitForEvent('filechooser');
    await this.importButton.click();
    const fileChooser = await fileChooserPromise;
    
    // Use dummy file to trigger dialog
    await fileChooser.setFiles({
        name: 'test_backup.db',
        mimeType: 'application/x-sqlite3',
        buffer: Buffer.from('dummy')
    });
    
    // Wait for and cancel confirmation dialog
    const dialog = this.page.getByRole('dialog', { name: /Import Database/i });
    await expect(dialog).toBeVisible();
    await this.page.getByRole('button', { name: 'Cancel' }).click();
    await expect(dialog).toBeHidden();
}
```

---

## Phase 3: Domain Verification

### 3.1 Export Content Validation
- [ ] Verify downloaded file is a valid SQLite database
- [ ] Option A: Check file size > 0
- [ ] Option B: Use sqlite3 wasm to verify structure (advanced)

```typescript
test('Export Database produces valid SQLite file', async ({ page }) => {
    const downloadPromise = page.waitForEvent('download');
    await settingsPage.exportButton.click();
    const download = await downloadPromise;
    
    const path = await download.path();
    const stats = fs.statSync(path!);
    expect(stats.size).toBeGreaterThan(1024); // At least 1KB for valid DB
    
    // Optional: Check SQLite magic bytes
    const buffer = fs.readFileSync(path!);
    const magicBytes = buffer.toString('utf8', 0, 16);
    expect(magicBytes).toContain('SQLite format 3');
});
```

### 3.2 Full Import Path Verification (New Test)
- [ ] Add dedicated test for complete import with DB reset afterward
- [ ] Create fixture database with known data
- [ ] Verify data exists after import

```typescript
test.describe('Import Database - Full Path', () => {
    test('successfully imports and restores data', async ({ page }, testInfo) => {
        const settingsPage = new SettingsPage(page, testInfo);
        await settingsPage.goto();
        
        // Use a known good test database
        const testDbPath = path.join(__dirname, '../fixtures/test-praxis.db');
        
        await settingsPage.importDatabase(testDbPath);
        
        // Verify import succeeded - check for expected data
        // Navigate to assets page and verify expected items exist
    });
    
    test.afterEach(async ({ page }, testInfo) => {
        // Reset database after destructive import test
        const settingsPage = new SettingsPage(page, testInfo);
        await settingsPage.resetState();
    });
});
```

### 3.3 Post-Export State Verification
- [ ] Verify export doesn't corrupt or modify local state
- [ ] Navigate to another page and verify data still intact

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Invalid File Format Test
- [ ] Upload a non-SQLite file (e.g., PDF, text file)
- [ ] Verify error snackbar appears

```typescript
test('rejects non-SQLite file upload', async ({ page }) => {
    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.getByRole('button', { name: 'Import Database' }).click();
    const fileChooser = await fileChooserPromise;
    
    await fileChooser.setFiles({
        name: 'not_a_database.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from('This is not a database')
    });
    
    // Confirm the import
    await page.getByRole('button', { name: /Import and Refresh/i }).click();
    
    // Expect error handling
    await expect(page.getByText(/Import failed/i)).toBeVisible();
});
```

### 4.2 Empty File Test
- [ ] Upload 0-byte .db file
- [ ] Verify graceful error handling

### 4.3 Reset to Defaults Coverage
- [ ] Add test for "Reset Asset Inventory" button
- [ ] Verify confirmation dialog appears
- [ ] Verify cancel returns to previous state

---

## Verification Plan

### Automated
```bash
# Single test
npx playwright test e2e/specs/browser-export.spec.ts --timeout=120000

# Parallel execution (verify isolation works)
npx playwright test e2e/specs/browser-export.spec.ts --workers=4

# With trace for debugging
npx playwright test e2e/specs/browser-export.spec.ts --trace=on
```

### Manual Checklist
- [ ] Export button downloads file successfully
- [ ] Downloaded file can be opened in SQLite browser
- [ ] Import with cancel works without data loss
- [ ] Full import replaces data correctly

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/browser-export.spec.ts` | Refactor | ~80 → ~150 |
| `e2e/page-objects/settings.page.ts` | Extend | +20 (new methods) |
| `e2e/page-objects/base.page.ts` | Optional | +10 (welcome dialog) |
| `e2e/fixtures/test-praxis.db` | New | New fixture file |

---

## Acceptance Criteria

- [ ] Tests pass with parallel execution (`--workers=4`)
- [ ] Zero `force: true` clicks
- [ ] Zero `waitForTimeout` calls
- [ ] Uses `SettingsPage` POM for all interactions
- [ ] Verifies exported file is valid SQLite
- [ ] Covers error states (invalid file, empty file)
- [ ] Baseline score improves from 4.6/10 to ≥8.0/10

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Full import test is destructive | Use `afterEach` cleanup; run in isolated worker |
| SQLite validation requires external dependency | Start with size/magic byte check; defer wasm validation |
| Test may flake on slow CI | Use explicit waits; add retry logic for download events |
| Fixture database may become stale | Create fixture programmatically or version control it |

---

## Priority Order

```
Phase 1.1 (Worker Isolation)     ─── Critical ───┐
Phase 1.2 (Locator Fix)          ─── Quick Win ──┤
Phase 2.1 (Use Existing POM)     ─── Medium ─────┼── Sprint 1
Phase 3.1 (Export Validation)    ─── Medium ─────┘
Phase 3.2 (Full Import Path)     ─── Large ──────┐
Phase 3.3 (Post-Export State)    ─── Small ──────┼── Sprint 2
Phase 4.x (Error States)         ─── Stretch ────┘
```
