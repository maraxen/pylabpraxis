# E2E Enhancement Plan: data-visualization.spec.ts

**Target:** [data-visualization.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/data-visualization.spec.ts)  
**Baseline Score:** 4.4/10  
**Target Score:** 8.0/10  
**Effort Estimate:** 4-6 hours

---

## Goals

1. **Reliability** — Eliminate brittle coordinate-based interactions and hardcoded expectations
2. **Isolation** — Enable parallel test execution via worker-indexed DB
3. **Domain Coverage** — Verify actual data flow from SQLite → Chart
4. **Maintainability** — Implement Page Object Model for all interactions

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Create `DataVisualizationPage` extending `BasePage`
- [ ] Use `BasePage.goto()` for consistent initialization with worker-indexed DB
- [ ] Remove duplicated `waitForFunction` in `beforeEach`

**Implementation:**

```typescript
// e2e/page-objects/data-visualization.page.ts
import { Page, TestInfo, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class DataVisualizationPage extends BasePage {
    // Locators
    readonly heading: Locator;
    readonly chart: Locator;
    readonly xAxisSelect: Locator;
    readonly yAxisSelect: Locator;
    readonly exportButton: Locator;
    readonly emptyStateMessage: Locator;
    readonly selectedPointInfo: Locator;
    readonly runHistoryTable: Locator;
    readonly wellSelectorButton: Locator;

    constructor(page: Page, testInfo?: TestInfo) {
        super(page, '/run/data-visualization', testInfo);
        
        this.heading = page.getByRole('heading', { level: 1, name: 'Data Visualization' });
        this.chart = page.locator('plotly-plot').first();
        this.xAxisSelect = page.getByLabel('X-Axis');
        this.yAxisSelect = page.getByLabel('Y-Axis');
        this.exportButton = page.getByRole('button', { name: /export/i });
        this.emptyStateMessage = page.getByText('No data available to display.');
        this.selectedPointInfo = page.locator('.selected-point-info'); // Add data-testid in component
        this.runHistoryTable = page.locator('.run-table');
        this.wellSelectorButton = page.getByRole('button', { name: /select wells/i });
    }

    async selectXAxis(option: string) {
        await this.xAxisSelect.click();
        await this.page.getByRole('option', { name: option }).click();
        // Wait for chart to re-render
        await this.waitForChartLoad();
    }

    async waitForChartLoad() {
        // Wait for Plotly to finish rendering (check for plot container with data)
        await this.page.waitForFunction(() => {
            const plotDiv = document.querySelector('.js-plotly-plot');
            return plotDiv && (plotDiv as any).data?.length > 0;
        }, null, { timeout: 10000 });
    }

    async selectRunByIndex(index: number) {
        const rows = this.runHistoryTable.locator('tr[mat-row]');
        await rows.nth(index).click();
        await this.waitForChartLoad();
    }

    async getChartDataPointCount(): Promise<number> {
        return await this.page.evaluate(() => {
            const plotDiv = document.querySelector('.js-plotly-plot') as any;
            return plotDiv?.data?.[0]?.x?.length ?? 0;
        });
    }
}
```

### 1.2 Eliminate Hardcoded Canvas Interactions
- [ ] Remove coordinate-based canvas click test (line 65)
- [ ] Replace with Plotly-aware interaction OR mark as flaky skip
- [ ] If testing data point selection is critical, add `data-testid` to selection UI

**Rationale:** Plotly charts don't expose accessible elements for individual data points. The only reliable way to test selection is:
1. Trigger via Plotly's JavaScript API
2. Add a dedicated "Select Point" UI control for testing
3. Skip the interaction and test only the result UI

### 1.3 Remove Hardcoded Data Expectations
- [ ] Replace hardcoded `X: 1`, `Y: 2`, `Temp: 25` with dynamic assertions
- [ ] Use `page.evaluate()` to read actual component state and verify UI matches

---

## Phase 2: Page Object Refactor

### 2.1 Migrate All Selectors to POM
- [ ] Move all inline locators to `DataVisualizationPage`
- [ ] Add reusable methods for common actions

### 2.2 Add Test Helpers
- [ ] Add method to verify chart has data: `async hasChartData(): Promise<boolean>`
- [ ] Add method to get run count from table: `async getRunCount(): Promise<number>`
- [ ] Add method to trigger export and verify: `async exportAndVerify(): Promise<void>`

---

## Phase 3: Domain Verification

### 3.1 Data Integrity Verification
- [ ] After page load, verify `runs()` signal has expected structure
- [ ] Cross-check chart data points against SQLite transfer logs
- [ ] Verify statistics cards (Total Volume, Wells, Data Points, Runs)

**Implementation:**

```typescript
test('should display correct statistics from database', async ({ page }) => {
    const vizPage = new DataVisualizationPage(page, testInfo);
    await vizPage.goto();
    
    // Read SQLite data directly
    const stats = await page.evaluate(() => {
        const component = (window as any).ng.getComponent(
            document.querySelector('app-data-visualization')
        );
        return {
            totalVolume: component.totalVolume(),
            dataPointCount: component.filteredData().length,
            runCount: component.runs().length
        };
    });
    
    // Verify UI matches component state
    await expect(page.getByText(`${stats.totalVolume} µL`)).toBeVisible();
    await expect(page.getByText(`${stats.dataPointCount}`)).toBeVisible();
});
```

### 3.2 Run Switching Verification
- [ ] Add test for selecting a run from history table
- [ ] Verify chart updates to show selected run's data
- [ ] Verify stats update accordingly

### 3.3 Well Selector Integration
- [ ] Add test for opening well selector dialog
- [ ] Test selecting/deselecting wells
- [ ] Verify chart filters to selected wells

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Network Error Simulation
- [ ] Mock `getTransferLogs()` to return error
- [ ] Verify error message displays
- [ ] Verify graceful degradation

### 4.2 Empty Database Scenario  
- [ ] Test with empty runs array (not via component manipulation)
- [ ] Verify empty state displays properly
- [ ] Verify navigation works to add data

**Implementation:**

```typescript
test('should handle empty database gracefully', async ({ browser }) => {
    // Use fresh browser context with empty DB
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // Navigate with freshDb=true to get empty state
    await page.goto('/run/data-visualization?mode=browser&freshDb=true');
    
    await expect(page.getByText('No data available')).toBeVisible();
    await context.close();
});
```

---

## Verification Plan

### Automated
```bash
# Single worker (baseline)
npx playwright test e2e/specs/data-visualization.spec.ts

# Parallel execution (isolation proof)
npx playwright test e2e/specs/data-visualization.spec.ts --workers=4

# With tracing for debugging
npx playwright test e2e/specs/data-visualization.spec.ts --trace=on
```

### Manual Verification
- [ ] Run tests 3x to verify no flakiness
- [ ] Verify screenshots capture expected state
- [ ] Confirm no console errors during test execution

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/data-visualization.spec.ts` | Major Refactor | ~74 (rewrite) |
| `e2e/page-objects/data-visualization.page.ts` | New File | ~80 |
| `src/app/features/data/data-visualization.component.ts` | Minor | Add `data-testid` attributes (optional) |

---

## Acceptance Criteria

- [ ] Tests pass with parallel execution (`--workers=4`)
- [ ] Zero coordinate-based canvas interactions
- [ ] Zero hardcoded data expectations
- [ ] Uses `DataVisualizationPage` POM for all interactions
- [ ] Verifies at least one SQLite → UI data flow
- [ ] Covers run switching workflow
- [ ] Baseline score improves from 4.4/10 to ≥8.0/10

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Plotly interactions may still be flaky | Use Plotly JS API for testing, not DOM clicks |
| Worker isolation may expose hidden bugs | Run thorough regression before parallel execution |
| Component `data-testid` additions require code changes | Use existing ARIA labels where possible |
| Live data interval may cause timing issues | Mock `interval()` or use controlled test clock |

---

## Dependencies

- `worker-db.fixture.ts` patterns from existing test infrastructure  
- `BasePage` class for isolation support
- Potential component updates for `data-testid` attributes

---

## Estimated Timeline

| Phase | Duration |
|-------|----------|
| Phase 1: Infrastructure | 2 hours |
| Phase 2: POM Refactor | 1 hour |
| Phase 3: Domain Verification | 1.5 hours |
| Phase 4: Error States | 0.5 hours |
| **Total** | **4-6 hours** |
