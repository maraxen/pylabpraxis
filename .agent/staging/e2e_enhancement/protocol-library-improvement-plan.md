# E2E Enhancement Plan: `protocol-library.spec.ts`

**Target:** [protocol-library.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/protocol-library.spec.ts)  
**SDET Report:** [protocol-library-report.md](./protocol-library-report.md)  
**Baseline Score:** 6.0/10  
**Target Score:** 8.5/10  
**Effort Estimate:** ~4 hours

---

## Goals

1. **Reliability** — Eliminate `waitForTimeout(500)` patterns with proper Angular stability checks
2. **Maintainability** — Create a `ProtocolLibraryPage` Page Object Model to encapsulate selectors
3. **Coverage** — Add tests for card view, upload flow, empty state, and data integrity
4. **Modern Standards** — Replace CSS class selectors with role-based locators where possible

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Eliminate Hardcoded Waits

#### [MODIFY] [protocol-library.spec.ts L53, L72](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/protocol-library.spec.ts#L53)

**Current (L53, L72):**
```typescript
// Wait for Angular to settle
await page.waitForTimeout(500);
// ...
// Wait for filter to apply
await page.waitForTimeout(500);
```

**Proposed:**
```typescript
// Wait for Angular zone to stabilize and filter to apply
await page.waitForFunction(() => {
  const rows = document.querySelectorAll('tr[mat-row]');
  return rows.length > 0; // Or check for specific expected row count
});
```

**Changes:**
- Replace arbitrary `500ms` with condition-based waiting
- Use `waitForFunction` to poll for actual DOM state change
- For filter tests, wait for the expected row count or absence

---

### 1.2 Improve Locator Strategy

Replace implementation-detail selectors with more resilient patterns.

| Current Selector | Proposed Alternative | Notes |
|------------------|---------------------|-------|
| `table[mat-table]` | `page.getByRole('table')` | Role-based, Material renders standard `<table>` |
| `tr[mat-row]` | `page.getByRole('row')` (excluding header) | Filter with `.filter({ hasNotText: /Name.*Version/i })` |
| `.mat-mdc-select-panel` | `page.getByRole('listbox')` | Material uses `role="listbox"` for select panels |
| `mat-dialog-container` | `page.getByRole('dialog')` | Standard role for dialogs |

**Example refactor:**
```typescript
// Current (L81-82)
const protocolRow = page.locator('tr[mat-row]').first();
await protocolRow.click();

// Proposed
const protocolTable = page.getByRole('table');
const protocolRow = protocolTable.getByRole('row').filter({ hasNotText: /Name.*Version/i }).first();
await protocolRow.click();
```

---

## Phase 2: Page Object Model (Priority: High)

### 2.1 Create ProtocolLibraryPage POM

#### [CREATE] `e2e/page-objects/protocol-library.page.ts`

```typescript
import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class ProtocolLibraryPage extends BasePage {
  readonly searchInput: Locator;
  readonly table: Locator;
  readonly loadingSpinner: Locator;
  readonly uploadButton: Locator;
  readonly detailDialog: Locator;

  constructor(page: Page) {
    super(page, '/app/protocols');
    this.searchInput = page.getByPlaceholder(/Search/i);
    this.table = page.getByRole('table');
    this.loadingSpinner = page.locator('mat-spinner');
    this.uploadButton = page.locator('[data-tour-id="import-protocol-btn"]');
    this.detailDialog = page.getByRole('dialog');
  }

  async goto() {
    await super.goto('?mode=browser');
    await this.waitForTableReady();
  }

  async waitForTableReady(timeout = 30000): Promise<void> {
    // Wait for table or card view to render
    await expect(this.table.or(this.page.locator('app-protocol-card'))).toBeVisible({ timeout });
    await expect(this.loadingSpinner).not.toBeVisible({ timeout: 5000 });
  }

  /** Returns all visible protocol rows (excludes header) */
  getProtocolRows(): Locator {
    return this.table.getByRole('row').filter({ hasNotText: /^Name.*Version.*Description/i });
  }

  /** Returns a specific protocol row by name */
  getRowByName(name: string): Locator {
    return this.getProtocolRows().filter({ hasText: name });
  }

  async searchProtocol(query: string): Promise<void> {
    await expect(this.searchInput).toBeVisible();
    await this.searchInput.fill(query);
    // Wait for filter to apply by checking row content
    await this.page.waitForFunction(
      (q) => {
        const rows = Array.from(document.querySelectorAll('tr[mat-row]'));
        return rows.length === 0 || rows.some(r => r.textContent?.toLowerCase().includes(q.toLowerCase()));
      },
      query,
      { timeout: 10000 }
    );
  }

  async openStatusFilter(): Promise<Locator> {
    const statusCombobox = this.page.getByRole('combobox', { name: /Status/i });
    await expect(statusCombobox).toBeVisible({ timeout: 5000 });
    await statusCombobox.click();
    const panel = this.page.getByRole('listbox');
    await expect(panel).toBeVisible({ timeout: 10000 });
    return panel;
  }

  async filterByStatus(status: string): Promise<void> {
    const panel = await this.openStatusFilter();
    const option = panel.getByRole('option', { name: new RegExp(status, 'i') });
    await expect(option).toBeVisible({ timeout: 5000 });
    await option.click();
    // Wait for filter to apply
    await this.page.waitForFunction(() => {
      return document.querySelectorAll('tr[mat-row]').length >= 0;
    }, { timeout: 10000 });
  }

  async openProtocolDetails(name?: string): Promise<void> {
    const row = name ? this.getRowByName(name) : this.getProtocolRows().first();
    await row.click();
    await expect(this.detailDialog).toBeVisible({ timeout: 10000 });
  }

  async runProtocolFromTable(name?: string): Promise<void> {
    const row = name ? this.getRowByName(name) : this.getProtocolRows().first();
    const playButton = row.getByRole('button').filter({ has: this.page.locator('mat-icon:has-text("play_arrow")') });
    await playButton.click();
    await expect(this.page).toHaveURL(/\/run/, { timeout: 10000 });
  }

  async toggleToCardView(): Promise<void> {
    const cardViewToggle = this.page.getByRole('button', { name: /Card/i })
      .or(this.page.locator('[aria-label*="card"]'));
    if (await cardViewToggle.isVisible({ timeout: 3000 }).catch(() => false)) {
      await cardViewToggle.click();
      await expect(this.page.locator('app-protocol-card').first()).toBeVisible({ timeout: 10000 });
    }
  }

  async getDisplayedProtocolCount(): Promise<number> {
    return await this.getProtocolRows().count();
  }

  async assertDialogHasRunButton(): Promise<void> {
    const runButton = this.detailDialog.getByRole('button', { name: /Run Protocol/i });
    await expect(runButton).toBeVisible({ timeout: 5000 });
  }

  async assertDialogContent(expectedName: string): Promise<void> {
    await expect(this.detailDialog).toContainText(expectedName, { timeout: 5000 });
  }
}
```

### 2.2 Refactored Test Using POM

#### [MODIFY] [protocol-library.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/protocol-library.spec.ts)

```typescript
import { test, expect } from '../fixtures/app.fixture';
import { ProtocolLibraryPage } from '../page-objects/protocol-library.page';

test.describe('Protocol Library', () => {
  let protocolLibrary: ProtocolLibraryPage;

  test.beforeEach(async ({ page }) => {
    protocolLibrary = new ProtocolLibraryPage(page);
    await protocolLibrary.goto();
  });

  test('should load the protocol library page', async ({ page }) => {
    await expect(page.getByRole('heading', { level: 1 })).toContainText(/Protocol/i);
    const count = await protocolLibrary.getDisplayedProtocolCount();
    expect(count).toBeGreaterThan(0);
  });

  test('should search for a protocol by name', async () => {
    await protocolLibrary.searchProtocol('Kinetic');
    await expect(protocolLibrary.getRowByName('Kinetic Assay')).toBeVisible();
    await expect(protocolLibrary.getRowByName('Simple Transfer')).not.toBeVisible({ timeout: 5000 });
  });

  test('should filter protocols by status', async () => {
    await protocolLibrary.filterByStatus('Not Simulated');
    const count = await protocolLibrary.getDisplayedProtocolCount();
    expect(count).toBeGreaterThanOrEqual(1);
  });

  test('should open protocol details', async () => {
    await protocolLibrary.openProtocolDetails();
    await protocolLibrary.assertDialogHasRunButton();
  });

  test('should start a protocol run from the library', async ({ page }) => {
    await protocolLibrary.runProtocolFromTable();
    await expect(page).toHaveURL(/\/run/);
  });
});
```

---

## Phase 3: Coverage Expansion (Priority: Medium)

### 3.1 Card View Toggle Test

```typescript
test('should toggle to card view and display protocol cards', async ({ page }) => {
  await protocolLibrary.toggleToCardView();
  const cards = page.locator('app-protocol-card');
  await expect(cards.first()).toBeVisible();
  const cardCount = await cards.count();
  expect(cardCount).toBeGreaterThan(0);
});
```

### 3.2 Protocol Data Integrity Verification

```typescript
test('should display correct protocol metadata in table row', async () => {
  // Verify a known seeded protocol has correct data
  const kineticRow = protocolLibrary.getRowByName('Kinetic Assay');
  await expect(kineticRow).toBeVisible();
  
  // Check category badge is present
  await expect(kineticRow).toContainText(/Plate Reading|Assay/i);
  
  // Check version format (e.g., "1.0.0" or similar)
  await expect(kineticRow).toContainText(/\d+\.\d+/);
});
```

### 3.3 Protocol Detail Dialog Content Verification

```typescript
test('should display full protocol details in dialog', async () => {
  await protocolLibrary.openProtocolDetails('Kinetic Assay');
  
  // Verify dialog shows protocol name
  await protocolLibrary.assertDialogContent('Kinetic Assay');
  
  // Verify dialog has key elements
  const dialog = protocolLibrary.detailDialog;
  await expect(dialog.getByRole('button', { name: /Run Protocol/i })).toBeVisible();
  
  // Could add: description, category, parameter list verification
});
```

### 3.4 Empty State Test

```typescript
test('should display empty state when no protocols match search', async ({ page }) => {
  await protocolLibrary.searchProtocol('NONEXISTENT_PROTOCOL_XYZ');
  
  // Wait for filter to apply
  await page.waitForFunction(() => {
    return document.querySelectorAll('tr[mat-row]').length === 0;
  }, { timeout: 10000 });
  
  // Verify empty state message
  await expect(page.getByText(/No protocols found/i)).toBeVisible();
});
```

### 3.5 Error State Test (API Failure Simulation)

```typescript
test('should handle protocol load failure gracefully', async ({ page }) => {
  // Intercept the protocol service and fail it
  await page.route('**/api/protocols**', route => route.abort('failed'));
  
  // Navigate fresh (not using goto which expects success)
  await page.goto('/app/protocols?mode=browser');
  
  // Verify error handling (depends on component implementation)
  // At minimum, page should not crash
  await expect(page.getByRole('heading', { level: 1 })).toContainText(/Protocol/i);
});
```

---

## Phase 4: Domain-Specific Tests (Priority: Medium)

### 4.1 Protocol Run with Query Param Verification

```typescript
test('should pass correct protocolId when running from table', async ({ page }) => {
  // Get the first protocol's name to trace
  const firstRow = protocolLibrary.getRowByName('Kinetic Assay');
  await expect(firstRow).toBeVisible();
  
  // Click run button
  const playButton = firstRow.getByRole('button').filter({ 
    has: page.locator('mat-icon:has-text("play_arrow")') 
  });
  await playButton.click();
  
  // Verify URL contains protocolId parameter
  await expect(page).toHaveURL(/\/run\?.*protocolId=/);
});
```

### 4.2 SQLite Data Verification

```typescript
test('should have protocols loaded from SQLite database', async ({ page }) => {
  // Access Angular component's signal state
  const protocolCount = await page.evaluate(() => {
    const component = (window as any).ng?.getComponent(
      document.querySelector('app-protocol-library')
    );
    return component?.protocols()?.length ?? 0;
  });
  
  expect(protocolCount).toBeGreaterThan(0);
});
```

---

## Phase 5: Stretch Goals (Priority: Low)

### 5.1 Protocol Upload Flow

```typescript
test.skip('should upload a .py protocol file and show it in the library', async ({ page }) => {
  // Complex: requires mocking file input and observing ProtocolService.uploadProtocol
  // Placeholder for future implementation
});
```

### 5.2 Category Filter (After Bug Fix)

```typescript
test.skip('should filter protocols by category', async () => {
  // BLOCKED by FIXME in component (L43-47 of test file)
  // categoryOptions() computed signal doesn't propagate to ViewControlsComponent
});
```

---

## Verification Plan

### Automated

```bash
# Run single test with verbose logging
cd /Users/mar/Projects/praxis/praxis/web-client
npx playwright test e2e/specs/protocol-library.spec.ts --workers=1 --timeout=120000

# Parallel execution test (verify worker isolation)
npx playwright test e2e/specs/protocol-library.spec.ts --workers=4 --repeat-each=2

# With tracing for debugging
npx playwright test e2e/specs/protocol-library.spec.ts --trace=on
```

### Manual Verification

1. **No hardcoded waits** — `grep -n "waitForTimeout" e2e/specs/protocol-library.spec.ts` should return 0 lines
2. **POM usage** — All DOM interactions should use `ProtocolLibraryPage` methods
3. **Role-based locators** — Search for `tr\[mat-row\]` should be minimal (only in POM internals)
4. **Test independence** — Each test should pass when run in isolation: `npx playwright test --grep "filter protocols"`

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/protocol-library.spec.ts` | Major Refactor | ~100 lines rewritten |
| `e2e/page-objects/protocol-library.page.ts` | Create | ~120 lines |

---

## Acceptance Criteria

- [ ] Tests pass with `--workers=4` (parallel execution)
- [ ] Zero `waitForTimeout` calls in spec file
- [ ] Uses `ProtocolLibraryPage` POM for all interactions
- [ ] At least 3 new test cases added (card view, empty state, data verification)
- [ ] All assertions use web-first patterns (no manual `page.evaluate` except for deep state checks)
- [ ] Baseline score improves to ≥8.0/10
- [ ] Category filter test added as `.skip` pending component bug fix

---

## Appendix: Component Bug Documentation

### Category Filter Bug (FIXME)

**Location:** `ProtocolLibraryComponent` L211-219

**Symptom:** `categoryOptions()` is a computed signal derived from `protocols()`. When `ViewControlsComponent` receives `viewConfig` as a plain `@Input()` (not a signal input), it doesn't re-render when `categoryOptions()` updates after initial protocol load.

**Root Cause:** Angular signal-to-input propagation timing issue. `viewConfig()` is computed at component initialization when `protocols()` is empty, so `categoryOptions()` is `[]`.

**Potential Fix:**
1. Convert `ViewControlsComponent` to use signal inputs (`input()` instead of `@Input()`).
2. Or, defer `viewConfig()` computation until `protocols()` is populated.
3. Or, manually trigger change detection after `loadProtocols()` completes.

**Workaround for E2E:** Test Status filter (static options) instead of Category filter (dynamic options).
