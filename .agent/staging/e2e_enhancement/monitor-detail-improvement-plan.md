# E2E Enhancement Plan: monitor-detail.spec.ts

**Target:** [monitor-detail.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/monitor-detail.spec.ts)  
**Baseline Score:** 2.8/10  
**Target Score:** 8.0/10  
**Effort Estimate:** Medium (2-3 hours)

---

## Goals

1. **Compilation** — Fix broken import and add missing POM methods
2. **Reliability** — Enable parallel test execution with worker isolation
3. **Domain Coverage** — Verify actual run data integrity
4. **Maintainability** — Clean test structure with proper fixtures

---

## Phase 0: Critical Fixes (Priority: BLOCKER) 🔴

### 0.1 Fix Broken Import
```diff
- import { MonitorPage } from '../page-objects/monitor.page';
+ import { ExecutionMonitorPage } from '../page-objects/monitor.page';
```

### 0.2 Add Missing POM Methods to `monitor.page.ts`

```typescript
// Add to ExecutionMonitorPage class

/** Get the first run row from the history table */
getFirstRun(): Locator {
    return this.historyTable.locator('tbody tr').first();
}

/** Extract the run ID from a run row */
async getRunId(runRow: Locator): Promise<string> {
    // Assumes data-run-id attribute or text extraction
    const id = await runRow.getAttribute('data-run-id');
    if (id) return id;
    
    // Fallback: extract from inner text if structured
    const text = await runRow.locator('td').first().textContent();
    return text?.trim() || '';
}

/** Verify run detail page shows correct information for given run ID */
async verifyRunDetails(runId: string): Promise<void> {
    await this.page.waitForURL(`**/app/monitor/${runId}`, { timeout: 10000 });
    const heading = this.page.locator('h1, .run-title').first();
    await expect(heading).toBeVisible({ timeout: 10000 });
    // Optionally verify the run ID is present somewhere on the page
    await expect(this.page.locator('body')).toContainText(runId);
}
```

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration

**Before:**
```typescript
test.beforeEach(async ({ page }) => {
    monitorPage = new MonitorPage(page);
    await monitorPage.goto();
});
```

**After:**
```typescript
import { test, expect } from '../fixtures/worker-db.fixture';

test.describe('Run Detail View', () => {
    let monitorPage: ExecutionMonitorPage;

    test.beforeEach(async ({ page, testInfo }) => {
        monitorPage = new ExecutionMonitorPage(page);
        // Pass testInfo to enable worker-indexed DB
        await monitorPage.goto(testInfo);
    });
```

### 1.2 Add Cleanup Hook
```typescript
test.afterEach(async ({ page }) => {
    // Dismiss any lingering dialogs
    await page.keyboard.press('Escape').catch(() => {});
});
```

### 1.3 Add Data Prerequisites
The test assumes runs exist. Add setup to ensure at least one run is available:

```typescript
test.beforeAll(async ({ browser }) => {
    // Option 1: Use API to create a test run
    // Option 2: Execute a quick protocol to generate run data
    // Option 3: Use database seeding via page.evaluate()
});
```

---

## Phase 2: Page Object Refactor

### 2.1 Rename and Update Variable

```diff
- let monitorPage: MonitorPage;
+ let monitorPage: ExecutionMonitorPage;
```

### 2.2 Update Test to Use Existing POM Methods

Current `ExecutionMonitorPage` already has:
- `navigateToHistory()`
- `waitForHistoryRow(runName)`
- `openRunDetail(runName)`
- `openRunDetailById(runId)`
- `expectRunDetailVisible(runName)`

Refactor test to leverage these:

```typescript
test('navigates to the run detail page', async ({ page }) => {
    await monitorPage.navigateToHistory();
    
    // Get first run info using proper methods
    const firstRow = monitorPage.historyTable.locator('tbody tr').first();
    await expect(firstRow).toBeVisible({ timeout: 10000 });
    
    // Extract run name from row
    const runName = await firstRow.locator('td').first().textContent();
    
    // Use existing navigation method
    await monitorPage.openRunDetail(runName || '');
    
    // Verify using existing method
    await monitorPage.expectRunDetailVisible(runName || '');
});
```

---

## Phase 3: Domain Verification

### 3.1 Post-Navigation Verification
```typescript
test('navigates to the run detail page and verifies data', async ({ page }) => {
    await monitorPage.navigateToHistory();
    
    const firstRow = monitorPage.historyTable.locator('tbody tr').first();
    await expect(firstRow).toBeVisible();
    
    // Capture expected values before navigation
    const expectedName = await firstRow.locator('.run-name').textContent();
    const expectedStatus = await firstRow.locator('.run-status').textContent();
    
    await firstRow.click();
    await page.waitForURL(/\/app\/monitor\/.+$/);
    
    // DOMAIN: Verify actual data integrity
    await expect(page.locator('h1')).toContainText(expectedName!);
    await expect(page.getByTestId('run-status')).toContainText(expectedStatus!);
    
    // Verify timeline exists
    await expect(page.locator('.timeline-container')).toBeVisible();
    
    // Verify at least one log entry
    await expect(page.getByTestId('log-panel')).toBeVisible();
});
```

### 3.2 Verify Parameter Display
```typescript
test('displays run parameters correctly', async ({ page }) => {
    await monitorPage.navigateToHistory();
    await monitorPage.openRunDetail('Some Known Run');
    
    // Use existing method
    await monitorPage.verifyParameter('source_plate', 'Plate_A');
});
```

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Enhanced Error Cases
```typescript
test.describe('Error Handling', () => {
    test('displays error for invalid run ID format', async ({ page }) => {
        await page.goto('/app/monitor/invalid-run-id?mode=browser');
        await expect(page.getByText('Run not found')).toBeVisible();
    });

    test('displays error for non-existent UUID', async ({ page }) => {
        const fakeUUID = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee';
        await page.goto(`/app/monitor/${fakeUUID}?mode=browser`);
        await expect(page.getByText('Run not found')).toBeVisible();
    });

    test('handles empty run history gracefully', async ({ page }) => {
        // Navigate with reset DB to ensure empty state
        await page.goto('/app/monitor?mode=browser&resetdb=1');
        await expect(page.getByText(/No runs|No executions|Empty/i)).toBeVisible();
    });
});
```

---

## Verification Plan

### Automated
```bash
# Single worker (debug)
npx playwright test e2e/specs/monitor-detail.spec.ts --workers=1

# Parallel (validates isolation)
npx playwright test e2e/specs/monitor-detail.spec.ts --workers=4
```

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/monitor-detail.spec.ts` | Major refactor | ~27 → ~80 |
| `e2e/page-objects/monitor.page.ts` | Add methods | +20-30 lines |

---

## Acceptance Criteria

- [ ] Test compiles (import fixed)
- [ ] Tests pass with parallel execution (`--workers=4`)
- [ ] Uses `ExecutionMonitorPage` correctly
- [ ] Worker isolation via testInfo
- [ ] Verifies actual data on detail page
- [ ] Covers empty state scenario
- [ ] Covers multiple error conditions
- [ ] Baseline score improves to ≥8.0/10

---

## Priority Order

1. 🔴 **Fix import** (BLOCKER - test won't compile)
2. 🔴 **Add missing POM methods** (BLOCKER - test won't run)
3. 🟠 **Add data prerequisite or empty state handling**
4. 🟡 **Add worker isolation**
5. 🟡 **Add cleanup hook**
6. 🟢 **Add domain verification assertions**
7. 🟢 **Expand error case coverage**

