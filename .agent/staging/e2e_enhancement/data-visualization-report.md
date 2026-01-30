# SDET Static Analysis: data-visualization.spec.ts

**Target File:** [data-visualization.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/data-visualization.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested

The test file covers the **Data Visualization Page** — a Plotly-based charting component displaying experiment run data (transfer volumes, wells, temperature, pressure). The component is part of the lab automation tool's data analysis workflow.

**Functionality Verified:**
- Page navigation and basic render (`/run/data-visualization`)
- Page title displays correctly (`h1` with "Data Visualization")
- Chart canvas renders and is visible
- X-axis configuration can be changed (selecting 'temp' option)
- Chart export functionality (download as `chart.png`)
- Empty state display when data is cleared
- Data point selection on canvas click (coordinates-based interaction)

**UI Elements Exercised:**
- `<h1>` heading
- `<canvas>` (Plotly chart)
- `getByLabel('X-Axis')` — Material select dropdown
- `getByRole('option', { name: 'temp' })` — Dropdown option
- `getByRole('button', { name: 'Export' })` — Export button
- `app-data-visualization` — Angular component selector
- Selected point info text ("Selected Point", "X: 1", "Y: 2", "Temp: 25")

**State Changes:**
- Component data signal manipulation via `ng.getComponent()`
- Chart re-render on axis change
- Download event triggered

### Assertions (Success Criteria)

| Test Case | Primary Assertion |
|-----------|-------------------|
| Load page | `h1` has text "Data Visualization" |
| Render chart | `canvas` locator is visible |
| Change x-axis | `canvas` remains visible after axis change |
| Export chart | Download filename is `chart.png` |
| Show empty state | Text "No data available to display." is visible |
| Select data point | "Selected Point", "X: 1", "Y: 2", "Temp: 25" texts visible |

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

**🔴 Critical Issues:**

1. **Manual SQLite Readiness Wait (Lines 13-17):**
   ```typescript
   await page.waitForFunction(
       () => (window as any).sqliteService?.isReady$?.getValue() === true,
       null,
       { timeout: 30000 }
   );
   ```
   - This is **correct but duplicated**. The `BasePage.goto()` method already handles this.
   - Having this in `beforeEach` without using `BasePage` increases maintenance burden.

2. **Hardcoded Canvas Coordinates (Lines 65):**
   ```typescript
   await chart.click({ position: { x: 50, y: 250 } });
   ```
   - **Extremely brittle**. Chart dimensions and data point positions vary based on:
     - Viewport size
     - Data content
     - Plotly rendering variations
   - Will fail non-deterministically across environments.

3. **Hardcoded Expected Values (Lines 69-71):**
   ```typescript
   await expect(page.getByText('X: 1')).toBeVisible();
   await expect(page.getByText('Y: 2')).toBeVisible();
   await expect(page.getByText('Temp: 25')).toBeVisible();
   ```
   - Assumes specific mock data content. If seed data changes, tests break silently.

4. **Direct Component State Manipulation (Lines 48-53):**
   ```typescript
   await page.evaluate(() => {
       const component = (window as any).ng.getComponent(document.querySelector('app-data-visualization'));
       if (component) {
           component.data.set([]);
       }
   });
   ```
   - While this is a **valid pattern** for testing empty states without complex setup, it's **not isolated**.
   - Modifying component state directly bypasses Angular's change detection flow in some edge cases.
   - The pattern is acceptable for unit-style component tests, not true E2E.

5. **Missing Error Handling in Component Access:**
   - No assertion that `ng.getComponent` actually returned a component.
   - Silent failure if component lookup fails.

6. **No Page Object Model Usage:**
   - All selectors inline in test file.
   - No `DataVisualizationPage` abstraction.

**🟡 Minor Issues:**

1. **Mock Token (Line 8):** `'mock_token'` is set but the test doesn't verify any auth-gated behavior.
2. **No Cleanup Logic:** Test modifies component state (`data.set([])`) but doesn't restore it.
3. **CSS Selector for Component (Line 45):** `app-data-visualization` is implementation-specific.

### Modern Standards (2026) Evaluation

| Criterion | Status | Notes |
|-----------|--------|-------|
| **User-Facing Locators** | 🟢 Partial | Uses `getByRole`, `getByLabel`, `getByText`. But also uses `canvas`, `h1` without roles. |
| **Test Isolation** | 🔴 Fail | No worker-indexed DB, no cleanup, shared state between tests |
| **Page Object Model** | 🔴 Fail | No POM, all logic inline |
| **Async Angular Handling** | 🟡 Partial | SQLite readiness wait is correct but duplicated; no waiting for Plotly render completion |
| **Fixture Usage** | 🔴 Fail | Uses raw `test` import, no custom fixtures |
| **Accessibility Roles** | 🟡 Partial | Chart interactions don't use ARIA roles (canvas limitation) |

---

## 3. Test Value & Classification

### Scenario Relevance

**Scenario Type:** Mostly **Happy Path** with one **Edge Case** (empty state)

| Test | Journey Type | Real User Scenario? |
|------|--------------|---------------------|
| Load page | Happy Path | ✅ Yes – user navigates to data viz |
| Render chart | Happy Path | ✅ Yes – user expects to see chart |
| Change x-axis | Happy Path | ✅ Yes – users change axis configuration |
| Export chart | Happy Path | ✅ Yes – users export charts for reports |
| Show empty state | Edge Case | ⚠️ Partially – users wouldn't manually clear data, but may encounter empty runs |
| Select data point | Happy Path | ✅ Yes – users click points for details |

**Value Assessment:**
- The tests cover meaningful user interactions.
- The empty state test is valuable but artificially triggered.
- The data point selection test has limited practical value due to coordinate brittleness.

### Classification

**Classification: Interactive Unit Test (Leaning)**

| Factor | E2E | Unit-Style |
|--------|-----|------------|
| Uses real navigation | ✅ | |
| Uses real SQLite | ✅ (via `beforeEach` wait) | |
| Mocks auth | | ✅ |
| Manipulates component state directly | | ✅ |
| No backend API calls | | ✅ (uses mock data) |
| Tests integration between services | ✅ Partial | |

**Verdict:** This is a **Hybrid Test** — uses real navigation and DB infrastructure but manipulates component state directly for certain assertions. Closer to an **Integration Test** than a true E2E.

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

**Intended User Journey:**

1. **Authentication:** User is authenticated (mock token simulates logged-in state)
2. **Navigation:** User navigates to `/run/data-visualization`
3. **Page Load:** User waits for SQLite database to initialize and page to render
4. **View Chart:** User sees the main chart with default configuration
5. **Configure Visualization:**
   - User clicks X-Axis dropdown
   - User selects "temp" to change the chart's x-axis
6. **Export Data:** User clicks "Export" button and downloads chart as PNG
7. **Handle Empty Data:** (Edge case) User encounters scenario with no data
8. **Inspect Details:** User clicks on a data point to see its specifics (X, Y, Temp values)

### Contextual Fit

**Application Ecosystem Position:**

The Data Visualization component is a **downstream consumer** in the lab automation workflow:

```
Protocol Library → Protocol Execution → Run Logs → Data Visualization
                                                        ↑
                                                   (This Component)
```

**Dependencies:**
- **ProtocolService:** Provides protocol definitions and run history
- **SqliteService:** Stores run logs and transfer data
- **Plotly:** External charting library for rendering

**Integration Points:**
- Receives run data from `getRuns()` and `getTransferLogs()`
- Uses `ViewControlsComponent` for standardized filtering
- Opens `WellSelectorDialogComponent` for well filtering

**Critical for:**
- Scientists analyzing experiment results
- Operators validating transfer volumes
- QA checking data export functionality

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Severity | Description |
|-----|----------|-------------|
| **Y-Axis Configuration** | Medium | Only tests X-axis change, not Y-axis (which has 4 options) |
| **Well Selection Filter** | High | No test for `openWellSelector()` dialog integration |
| **Run Selection** | High | No test for selecting different runs from history table |
| **Filter/Search** | High | `ViewControlsComponent` filtering not exercised |
| **Live Data Updates** | Medium | Component has `interval(5000)` for live data, untested |
| **Multiple Runs** | High | No test for switching between runs |
| **Stats Grid** | Low | Statistics cards not verified |

### Domain Specifics

#### Data Integrity

| Check | Status | Notes |
|-------|--------|-------|
| SQLite DB initialized | 🟢 Tested | `waitForFunction` verifies `isReady$` |
| Run data loaded correctly | 🔴 Not Tested | No assertion on `runs()` signal content |
| Transfer logs parsed | 🔴 Not Tested | No verification of `getTransferLogs()` response |
| Data point values accurate | 🟡 Partial | Hardcoded expectations, no dynamic validation |
| Chart data matches SQLite | 🔴 Not Tested | No cross-verification between DB and chart |

#### Simulation vs. Reality

| Aspect | Status | Notes |
|--------|--------|-------|
| Uses real SQLite OPFS | ✅ Yes | Browser-mode with real SQLite |
| Uses real Plotly rendering | ✅ Yes | Actual charting library |
| Worker isolation | 🔴 No | Doesn't use `BasePage` worker-indexed DB |
| Simulates live data | 🔴 Not Tested | `addLiveDataPoint()` subscription untested |

#### Serialization

| Verification | Status | Notes |
|--------------|--------|-------|
| Chart export format | 🟢 Tested | Verifies filename is `chart.png` |
| Export content valid | 🔴 Not Tested | Doesn't verify PNG is valid/non-empty |
| API response parsing | 🔴 Not Tested | `TransferDataPoint` mapping not verified |
| Date parsing | 🔴 Not Tested | Timestamp handling in `loadRunData()` |

#### Error Handling

| Scenario | Status | Notes |
|----------|--------|-------|
| Empty data | 🟢 Tested | Verifies "No data available" message |
| Failed run load | 🔴 Not Tested | `catch` in `getRuns()` not exercised |
| Invalid transfer logs | 🔴 Not Tested | `getTransferLogs()` error path |
| Plotly render failure | 🔴 Not Tested | Chart library error handling |
| Network timeout | 🔴 Not Tested | Slow API response |

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 5/10 | Covers basics but misses major features (well selector, run switching, filters) |
| **Best Practices** | 4/10 | No POM, no fixtures, hardcoded coordinates, duplicated wait logic |
| **Test Value** | 6/10 | Happy path coverage is meaningful; data point test is fragile |
| **Isolation** | 3/10 | No worker-indexed DB, modifies shared state, no cleanup |
| **Domain Coverage** | 4/10 | Missing data integrity checks, live updates, error paths |

**Overall: 4.4/10**

### Key Recommendations (Priority Order)

1. **Critical:** Create `DataVisualizationPage` POM with proper `BasePage` extension
2. **Critical:** Remove hardcoded canvas coordinates; use Plotly hover/click APIs or skip flaky test
3. **High:** Add run switching and well selector tests
4. **High:** Implement worker-indexed DB isolation
5. **Medium:** Add data integrity verification (compare SQLite → Chart)
6. **Medium:** Test error scenarios (failed loads, empty runs)
7. **Low:** Add export content validation (verify PNG is valid)
