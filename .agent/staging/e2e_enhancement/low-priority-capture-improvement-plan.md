# E2E Enhancement Plan: low-priority-capture.spec.ts

**Target:** [low-priority-capture.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/low-priority-capture.spec.ts)  
**Baseline Score:** 2.0/10  
**Target Score:** 8.0/10  
**Effort Estimate:** 4-6 hours (Medium - requires test strategy redesign)

---

## Goals

1. **Reliability** — Eliminate hardcoded waits, use deterministic assertions
2. **Isolation** — Enable parallel test execution with worker-indexed databases
3. **Domain Coverage** — Validate export/import functionality, not just UI presence
4. **Maintainability** — Leverage existing `SettingsPage` POM fully

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
**Current:**
```typescript
import { test, expect } from '@playwright/test';
```

**Target:**
```typescript
import { test, expect, gotoWithWorkerDb } from '../../fixtures/worker-db.fixture';
```

**Tasks:**
- [ ] Replace `@playwright/test` import with `worker-db.fixture`
- [ ] Replace `page.goto()` with `gotoWithWorkerDb(page, path, testInfo)`
- [ ] Remove hardcoded `MODE_PARAMS = 'mode=browser'`

### 1.2 Eliminate Hardcoded Waits
**Current (Line 29):**
```typescript
await page.waitForTimeout(2000);
```

**Target:**
```typescript
// Wait for settings page to be fully rendered
await settingsPage.exportButton.waitFor({ state: 'visible' });
// Or use Angular stability
await page.waitForLoadState('networkidle');
```

**Tasks:**
- [ ] Remove `waitForTimeout(2000)` on line 29
- [ ] Replace with action-completion waits (button visibility, network idle)
- [ ] Verify snackbar wait uses timeout appropriately (10s is reasonable for async ops)

### 1.3 Replace CSS Selectors with Semantic Locators
**Current (Line 42):**
```typescript
const snackbar = page.locator('.mat-mdc-snack-bar-container, .mdc-snackbar__surface').first();
```

**Target:**
```typescript
// Material snackbars have role="alert" by default
const snackbar = page.getByRole('alert');
// Or by snackbar message content
const snackbar = page.getByText(/Database exported/i);
```

**Tasks:**
- [ ] Replace CSS class selector with `getByRole('alert')` or `getByText()`
- [ ] Verify snackbar role in actual component (may need to add ARIA attributes)

---

## Phase 2: Page Object Refactor

### 2.1 Use Existing SettingsPage POM
**Current:** Inline button locator
```typescript
const exportButton = page.getByRole('button', { name: 'Export Database' });
```

**Target:** Leverage `SettingsPage`
```typescript
import { SettingsPage } from '../page-objects/settings.page';

const settingsPage = new SettingsPage(page);
const downloadPath = await settingsPage.exportDatabase();
```

**Tasks:**
- [ ] Import and instantiate `SettingsPage`
- [ ] Replace inline `exportButton` locator with `settingsPage.exportButton`
- [ ] Use `settingsPage.exportDatabase()` method which properly awaits download

### 2.2 Add Screenshot Helper to SettingsPage (Optional)
If screenshot capture remains a requirement:

```typescript
// In settings.page.ts
async captureSettingsScreenshot(path: string): Promise<void> {
    await this.exportButton.waitFor({ state: 'visible' });
    await this.page.screenshot({ path, fullPage: true });
}
```

**Tasks:**
- [ ] Consider whether screenshot capture belongs in POM or test utilities
- [ ] If retained, add helper method to avoid inline screenshot logic

---

## Phase 3: Domain Verification

### 3.1 Validate Export Functionality
**Current:** Click button, wait for snackbar (no actual validation)

**Target:** Verify download completes and file is valid
```typescript
test('Export Database produces valid SQLite file', async ({ page }) => {
    const settingsPage = new SettingsPage(page);
    
    // Use POM method that returns download path
    const downloadPath = await settingsPage.exportDatabase();
    
    // Verify file exists and has content
    const stats = fs.statSync(downloadPath);
    expect(stats.size).toBeGreaterThan(0);
    
    // Verify SQLite header (magic bytes: "SQLite format 3")
    const buffer = fs.readFileSync(downloadPath);
    const header = buffer.toString('utf8', 0, 16);
    expect(header).toContain('SQLite format 3');
});
```

**Tasks:**
- [ ] Capture download using `settingsPage.exportDatabase()`
- [ ] Add file existence assertion
- [ ] Add SQLite header validation
- [ ] (Stretch) Query exported DB to verify table structure

### 3.2 Add Import Round-Trip Verification
```typescript
test('Export and re-import produces identical data', async ({ page }) => {
    const settingsPage = new SettingsPage(page);
    
    // Export current state
    const downloadPath = await settingsPage.exportDatabase();
    
    // Import back
    await settingsPage.importDatabase(downloadPath);
    
    // Verify data integrity via application state
    // (specific verification depends on what data is expected)
});
```

**Tasks:**
- [ ] Add test for import functionality
- [ ] Verify round-trip data integrity

### 3.3 Snackbar Content Verification
**Current:** Checks snackbar visible

**Target:** Verify message content
```typescript
await expect(page.getByRole('alert')).toHaveText(/exported successfully/i);
```

**Tasks:**
- [ ] Add assertion on snackbar message content
- [ ] Verify both success and error message scenarios

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Export Failure Scenarios
```typescript
test.describe('Settings Error Handling', () => {
    test('displays error snackbar when export fails', async ({ page }) => {
        // Inject failure condition (e.g., fill OPFS storage)
        // Attempt export
        // Verify error snackbar appears with appropriate message
    });
});
```

**Tasks:**
- [ ] Identify injectable failure conditions
- [ ] Add at least one negative test case
- [ ] Verify error snackbar messaging

### 4.2 OPFS Toggle Coverage
```typescript
test('OPFS toggle switches database backend', async ({ page }) => {
    const settingsPage = new SettingsPage(page);
    
    const initialState = await settingsPage.isOpfsEnabled();
    await settingsPage.toggleOpfs(!initialState);
    
    // Verify toggle persisted after page reload
    expect(await settingsPage.isOpfsEnabled()).toBe(!initialState);
});
```

**Tasks:**
- [ ] Add OPFS toggle test
- [ ] Verify persistence across page loads

---

## Phase 5: Test Cleanup & Isolation

### 5.1 Screenshot Directory Management
**Current:** Directory created but never cleaned

**Target:**
```typescript
test.afterAll(async () => {
    // Clean up screenshots from this run
    if (fs.existsSync(screenshotDir)) {
        fs.rmSync(screenshotDir, { recursive: true });
    }
});
```

**Tasks:**
- [ ] Add `afterAll` cleanup hook
- [ ] Or move screenshots to temp directory that's auto-cleaned

### 5.2 Download Cleanup
```typescript
test.afterEach(async ({}, testInfo) => {
    // Clean up any downloads from this test
    const downloads = testInfo.attachments.filter(a => a.name === 'download');
    // Handle cleanup
});
```

**Tasks:**
- [ ] Add download cleanup in `afterEach`

---

## Verification Plan

### Automated
```bash
# Run refactored test in isolation
npx playwright test e2e/specs/low-priority-capture.spec.ts --headed

# Verify parallel execution works
npx playwright test e2e/specs/low-priority-capture.spec.ts --workers=4

# Run with tracing for debugging
npx playwright test e2e/specs/low-priority-capture.spec.ts --trace on
```

### Manual Verification
- [ ] Verify exported database opens in SQLite client
- [ ] Verify imported database restores expected state
- [ ] Confirm no screenshots left after test completes

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/low-priority-capture.spec.ts` | Refactor | ~50 → ~80 |
| `e2e/page-objects/settings.page.ts` | Enhancement | +10-15 (optional helper methods) |

---

## Proposed Test Structure (After Refactor)

```typescript
import { test, expect, gotoWithWorkerDb } from '../../fixtures/worker-db.fixture';
import { SettingsPage } from '../page-objects/settings.page';
import { WelcomePage } from '../page-objects/welcome.page';
import * as fs from 'fs';

test.describe('Settings Page Functionality', () => {
    let settingsPage: SettingsPage;

    test.beforeEach(async ({ page }, testInfo) => {
        await gotoWithWorkerDb(page, '/app/settings', testInfo);
        await new WelcomePage(page).handleSplashScreen();
        settingsPage = new SettingsPage(page);
    });

    test('renders settings interface', async ({ page }) => {
        await expect(settingsPage.exportButton).toBeVisible();
        await expect(settingsPage.importButton).toBeVisible();
    });

    test('exports database with valid SQLite file', async ({ page }) => {
        const downloadPath = await settingsPage.exportDatabase();
        
        // Verify file validity
        const buffer = fs.readFileSync(downloadPath);
        expect(buffer.toString('utf8', 0, 16)).toContain('SQLite format 3');
    });

    test('shows success snackbar after export', async ({ page }) => {
        await settingsPage.exportButton.click();
        await expect(page.getByRole('alert')).toHaveText(/exported/i);
    });
});
```

---

## Acceptance Criteria

- [ ] Tests pass with parallel execution (`--workers=4`)
- [ ] Zero `waitForTimeout` calls
- [ ] Uses `worker-db.fixture` for isolation
- [ ] Uses `SettingsPage` POM exclusively
- [ ] Verifies export file validity (SQLite header check)
- [ ] Verifies snackbar message content
- [ ] Includes cleanup in `afterEach`/`afterAll`
- [ ] Baseline score improves from 2.0 to ≥8.0/10

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| `SettingsPage.exportDatabase()` may not work as expected | Verify POM method before refactor |
| Snackbar role may not be `alert` | Inspect actual component ARIA attributes |
| Export may be slow, causing flaky tests | Add appropriate timeout (30s+) |
| Screenshot capture may be required for documentation | Move to separate documentation spec if needed |

---

## Decision: Rename or Split?

**Option A: Rename to `settings-functionality.spec.ts`**
- Transform into full Settings page E2E test
- Remove "screenshot capture" focus

**Option B: Split into two files**
- `settings.spec.ts` — Full functionality tests
- `visual-capture/settings-screenshots.spec.ts` — Documentation screenshots only

**Recommendation:** Option A - This test provides minimal value as screenshot utility; better to convert to proper E2E coverage of Settings page.
