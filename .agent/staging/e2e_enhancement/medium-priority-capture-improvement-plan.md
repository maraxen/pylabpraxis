# E2E Enhancement Plan: medium-priority-capture.spec.ts

**Target:** [medium-priority-capture.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/medium-priority-capture.spec.ts)  
**Baseline Score:** 2.0/10  
**Target Score:** 7.0/10 (Note: Lower target since this is a utility, not a functional test)  
**Effort Estimate:** Low-Medium (3-4 hours)

---

## Goals

1. **Reclassification** — Properly categorize as visual utility, not E2E test
2. **Reliability** — Eliminate all hardcoded waits
3. **Maintainability** — Consolidate inline logic into POMs
4. **Isolation** — Enable parallel execution and clean up side effects

---

## Phase 0: Architectural Decision (Priority: Critical)

### 0.1 Reclassify or Delete
- [ ] **Decision Required**: Is this file needed in CI, or is it an on-demand utility?
  - **If CI**: Convert to visual regression tests with `toMatchSnapshot()`
  - **If On-Demand**: Move to `e2e/utilities/` and exclude from default test run

### 0.2 Move to Appropriate Location
```bash
# Option A: Move to utilities folder
mkdir -p e2e/utilities
mv e2e/specs/medium-priority-capture.spec.ts e2e/utilities/

# Option B: Rename to indicate non-CI status
mv e2e/specs/medium-priority-capture.spec.ts e2e/specs/_medium-priority-capture.visual.ts
```

- [ ] Update `playwright.config.ts` to exclude `utilities/` or `*.visual.ts` from default runs

---

## Phase 1: Infrastructure & Reliability (Priority: High)

### 1.1 Eliminate Hardcoded Waits (16 instances)

| Line | Current | Replacement |
|------|---------|-------------|
| 32 | `waitForTimeout(2000)` | `await page.waitForLoadState('networkidle')` |
| 38 | `waitForTimeout(1000)` | `await expect(grid).toBeEmpty()` or debounce wait |
| 46 | `waitForTimeout(2000)` | `await page.waitForLoadState('networkidle')` |
| 50 | `waitForTimeout(1000)` | `await expect(assetGrid).toBeEmpty()` |
| 58 | `waitForTimeout(2000)` | `await page.waitForLoadState('networkidle')` |
| 69 | `waitForTimeout(500)` | `await expect(spinner).toBeVisible()` |
| 75 | `waitForTimeout(1000)` | `await page.waitForLoadState('domcontentloaded')` |
| 81 | `waitForTimeout(1000)` | `await page.waitForLoadState('domcontentloaded')` |
| 87 | `waitForTimeout(1000)` | `await page.waitForLoadState('domcontentloaded')` |
| 108-129 | Various | Use wizard step completion signals |
| 142 | `waitForTimeout(3000)` | `await chartDataReady.waitFor()` |

- [ ] Create helper: `waitForAngularStability()` using `networkidle` + DOM stability

### 1.2 Replace Inline Locators with Semantic Alternatives

| Current | Replacement |
|---------|-------------|
| `input[placeholder*="Search"]` | `page.getByRole('searchbox')` or `page.getByPlaceholder('Search')` |
| `app-telemetry-chart` | `page.getByTestId('telemetry-chart')` (requires data-testid) |
| `app-plate-heatmap` | `page.getByTestId('plate-heatmap')` |

- [ ] Add `data-testid` attributes to Angular components

### 1.3 Fixture for Screenshot Directory

```typescript
// e2e/fixtures/screenshot.fixture.ts
import { test as base } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

export const test = base.extend<{ screenshotDir: string }>({
  screenshotDir: async ({}, use, testInfo) => {
    const dir = path.join(process.cwd(), 'e2e/screenshots', testInfo.titlePath[0] || 'default');
    fs.mkdirSync(dir, { recursive: true });
    await use(dir);
    // Optional: cleanup old screenshots
  },
});
```

- [ ] Migrate to fixture-based screenshot management
- [ ] Remove `beforeAll` file system manipulation

---

## Phase 2: Page Object Consolidation

### 2.1 Create `SearchableListPage` Base POM

```typescript
// e2e/page-objects/searchable-list.page.ts
export abstract class SearchableListPage extends BasePage {
  get searchInput() {
    return this.page.getByRole('searchbox');
  }

  async searchFor(query: string) {
    await this.searchInput.fill(query);
    await this.page.waitForLoadState('networkidle');
  }

  async assertEmptyState() {
    await expect(this.emptyStateIndicator).toBeVisible();
  }
  
  abstract get emptyStateIndicator(): Locator;
}
```

- [ ] Extend for `ProtocolListPage` and `AssetListPage`

### 2.2 Create `DashboardPage` POM

```typescript
// e2e/page-objects/dashboard.page.ts
export class DashboardPage extends BasePage {
  get telemetryChart() {
    return this.page.getByTestId('telemetry-chart');
  }

  get plateHeatmap() {
    return this.page.getByTestId('plate-heatmap');
  }

  async waitForChartsLoaded() {
    await this.telemetryChart.waitFor({ state: 'visible' });
    // Wait for chart data (canvas rendered, SVG paths exist, etc.)
  }
}
```

- [ ] Extract chart/visualization locators from test file

---

## Phase 3: Optional Enhancements (If Kept as Visual Regression)

### 3.1 Convert to Visual Regression

```typescript
test('Empty protocol library matches baseline', async ({ page }) => {
  // ... setup
  await expect(page).toHaveScreenshot('empty-protocol-library.png', {
    maxDiffPixelRatio: 0.05,
  });
});
```

- [ ] Replace `screenshot()` calls with `toHaveScreenshot()`
- [ ] Establish baseline screenshots

### 3.2 Add Meaningful Assertions

Even as a utility, add guards:

```typescript
// Before screenshot
await expect(page.getByText('No protocols found')).toBeVisible();
await page.screenshot({ path: ... });
```

- [ ] Add assertion before each screenshot to validate expected state

---

## Phase 4: Error State Coverage (Stretch)

If converting to a real test suite:

- [ ] Test empty state component renders correctly
- [ ] Validate loading spinner accessibility
- [ ] Verify chart data presence (not just visibility)

---

## Verification Plan

### Automated
```bash
# If kept in specs/
npx playwright test e2e/specs/medium-priority-capture.spec.ts --workers=1

# If moved to utilities/
npx playwright test e2e/utilities/medium-priority-capture.spec.ts
```

### Manual Verification
- [ ] Screenshots are generated in correct directory
- [ ] No flaky failures on slow network

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/medium-priority-capture.spec.ts` | Refactor/Move | 160 |
| `e2e/fixtures/screenshot.fixture.ts` | Create | ~25 |
| `e2e/page-objects/searchable-list.page.ts` | Create | ~40 |
| `e2e/page-objects/dashboard.page.ts` | Create | ~30 |
| `playwright.config.ts` | Update | ~5 |

---

## Acceptance Criteria

- [ ] **Reclassification done**: File is either moved to utilities or converted to visual regression
- [ ] Zero `waitForTimeout` calls (currently 16)
- [ ] Zero inline locators (all in POMs)
- [ ] Uses Playwright fixtures for screenshot directory
- [ ] If in CI: `toHaveScreenshot()` used with baselines
- [ ] If utility: excluded from default `npx playwright test` run
- [ ] Baseline score improves from 2.0/10 to ≥7.0/10
