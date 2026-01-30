# SDET Static Analysis: medium-priority-capture.spec.ts

**Target File:** [medium-priority-capture.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/medium-priority-capture.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested
This test file is designed as a **screenshot capture utility**, not a functional test suite. It captures visual states across three categories:

1. **Empty States** (`Capture Empty States`)
   - Protocol library with no matching search results
   - Asset list with no matching search results
   - Workcell dashboard base state

2. **Loading States** (`Capture Loading States`)
   - Workcell initial load (spinner)
   - Login page (normal, error, and loading states via query params)

3. **Charts and Visualizations** (`Capture Charts and Visualizations`)
   - Full wizard workflow: protocol selection → parameters → machine → assets → deck → review → execution
   - Telemetry chart during live execution
   - Plate heatmap (optional)
   - Full workcell dashboard during execution

### Assertions (Success Criteria)
| Assertion | Location | What It Validates |
|-----------|----------|-------------------|
| `telemetryChart.toBeVisible()` | Line 139 | Telemetry chart component renders post-execution start |
| `protocolCards.first().waitFor()` | Line 104 | Protocol cards load before interaction |

**Critical Observation:** This file has only **2 explicit assertions** across 160 lines. The "success" criteria is primarily **"screenshots are captured without throwing"** rather than behavioral validation.

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

| Issue | Severity | Location | Description |
|-------|----------|----------|-------------|
| **Hardcoded `waitForTimeout`** | 🔴 Critical | Lines 32, 38, 46, 50, 58, 69, 75, 81, 87, 108, 113, 117, 121, 125, 129, 142 | 16 instances of arbitrary time-based waits (500ms–3000ms). These are flaky—slower environments will fail, faster ones waste time. |
| **Non-unique CSS Selectors** | 🟠 High | Line 35, 47, 138, 149 | `input[placeholder*="Search"]` and tag-based locators (`app-telemetry-chart`, `app-plate-heatmap`) are implementation-coupled and not resilient to refactoring. |
| **`force: true` Click** | 🟠 High | `ProtocolPage.selectFirstProtocol()` (POM) | Force clicks bypass actionability checks, hiding real UI issues like overlays or disabled states. |
| **Loose Error Handling** | 🟡 Medium | Lines 36, 48, 150 | `.isVisible()` with `.catch(() => false)` silently swallows failures, masking genuine issues. |
| **No Test Isolation** | 🟠 High | Test Suite | Tests share the same browser context. If `beforeAll` fails, all tests fail. No `afterEach` cleanup. |
| **File System Side Effects** | 🟠 High | Lines 8–13 | Writing to `e2e/screenshots/` is a side effect that persists across runs. No cleanup of stale screenshots. |

### Modern Standards (2026) Evaluation

| Standard | Status | Evidence |
|----------|--------|----------|
| **User-Facing Locators** | ❌ Fail | Heavy reliance on CSS attribute selectors (`input[placeholder*="Search"]`) and Angular component tags (`app-telemetry-chart`). Should use `getByRole`, `getByLabel`. |
| **Test Isolation** | ❌ Fail | No `test.describe.configure({ mode: 'parallel' })`, no worker isolation, no `beforeEach` reset. Tests are serially dependent. |
| **Page Object Model (POM)** | 🟡 Partial | Uses `WelcomePage`, `ProtocolPage`, `WizardPage` effectively in test 3, but tests 1–2 have inline locators and logic that belong in POMs. |
| **Async Angular Handling** | ❌ Fail | Uses `waitForTimeout` instead of `waitForSelector`, `waitForLoadState('networkidle')`, or Angular-aware waiting (e.g., waiting for `(ngOnInit)` completion). |
| **Fixtures** | ❌ Fail | Does not use Playwright fixtures for page setup, database seeding, or screenshot directory management. |

---

## 3. Test Value & Classification

### Scenario Relevance
| Aspect | Assessment |
|--------|------------|
| **User Journey** | The third test (`Capture Charts and Visualizations`) follows a **critical happy path**: full wizard workflow → execution → dashboard visualization. This is a core user journey. |
| **Realistic Scenario** | Tests 1–2 are **synthetic**: they fabricate empty states via nonsensical search queries (`xyznonexistent123`) and mock query parameters (`mockError`, `mockLoading`). These are not real user scenarios. |
| **Edge Case vs. Happy Path** | Tests 1–2 are edge-case screenshots. Test 3 is a happy path. |

### Classification
| Category | Verdict |
|----------|---------|
| **True E2E Test** | ❌ No — This is a **Visual Documentation Utility**, not a functional E2E test. |
| **Interactive Unit Test** | ❌ No — It interacts with real components across multiple pages. |
| **Screenshot Capture Utility** | ✅ Yes — Primary purpose is artifact generation for documentation/design review. |

**Recommendation:** This file should be **excluded from CI test runs** and invoked on-demand (e.g., `npm run screenshots:medium`). It adds no regression value.

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

**Test 1: Capture Empty States**
1. Navigate to `/app/protocols?mode=browser&resetdb=0`
2. Dismiss any splash/welcome screen
3. Search for nonsensical string to force "no results" state
4. Capture screenshot
5. Repeat for `/app/assets` and `/app/workcell`

**Test 2: Capture Loading States**
1. Navigate to `/app/workcell` and capture before Angular hydrates (loading spinner)
2. Navigate to login page with `forceLogin=true` (normal state)
3. Navigate with `mockError=...` (error state simulation)
4. Navigate with `mockLoading=true` (loading state simulation)

**Test 3: Capture Charts and Visualizations**
1. Navigate to `/app/run?mode=browser&resetdb=true` (resets database)
2. Handle splash screen
3. Select first protocol card
4. Continue → configure parameters
5. Select simulation machine
6. Auto-configure assets
7. Advance deck setup
8. Open review step
9. Start execution
10. Wait for telemetry chart to become visible
11. Capture telemetry chart, plate heatmap (if present), and full workcell screenshots

### Contextual Fit
This spec serves as a **screenshot batch job** for generating documentation assets. It exercises:
- The run wizard (core workflow)
- Dashboard/workcell views
- Login page states (via mock parameters)

It does **not** validate correctness—only that components render to a point where screenshots can be taken.

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Impact | Recommendation |
|-----|--------|----------------|
| **No assertion on empty state UI** | Low | If "empty state" design changes, test won't catch it. Add `expect(emptyStateMessage).toBeVisible()`. |
| **No assertion on loading spinner** | Low | Loading state might never appear if app loads too fast. Add `expect(spinner).toBeVisible()`. |
| **No validation of chart data** | Medium | Telemetry chart could render empty (no data points). Assert `chartDataPoints.count() > 0`. |
| **No execution completion verification** | High | Test captures screenshot mid-execution but never confirms execution succeeds. |
| **Login page mock params are undocumented** | Medium | `mockError`, `mockLoading` are magic strings with no validation they're still supported. |

### Domain Specifics

| Domain Area | Assessment |
|-------------|------------|
| **Data Integrity** | ❌ **Not Validated** — `resetdb=true` is used but there's no assertion that praxis.db reset succeeded. Protocol/asset data is assumed to exist. |
| **Simulation vs. Reality** | 🟡 **Implicit** — `ensureSimulationMode()` is called, but no verification that backend is in simulation mode (no API call check). |
| **Serialization** | ❌ **Not Covered** — Wizard submits protocol config, but there's no validation that arguments are correctly serialized to Pyodide worker. |
| **Error Handling** | ❌ **Not Covered** — No tests for: invalid DB upload, Python syntax errors, machine connection failures, invalid parameter values. |

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 3/10 | Purpose is screenshot capture, not testing. Only 2 assertions in 160 lines. |
| **Best Practices** | 2/10 | 16 `waitForTimeout` calls, non-semantic locators, no isolation, force clicks in POM. |
| **Test Value** | 2/10 | Visual utility, not regression test. Should be excluded from CI. |
| **Isolation** | 2/10 | Shared file system state, no cleanup, serial test execution. |
| **Domain Coverage** | 1/10 | No data integrity checks, no serialization verification, no error states. |

**Overall**: **2.0/10**

---

## Recommendations Summary

1. **Reclassify**: Move to `e2e/utilities/` or `e2e/visual/` and exclude from `npx playwright test`.
2. **Eliminate `waitForTimeout`**: Replace with state-driven waits (e.g., `waitForSelector`, `waitForLoadState`).
3. **Add Real Assertions**: If this must run as a test, convert to visual regression with `toMatchSnapshot()`.
4. **Fixture-ize**: Use Playwright fixtures for screenshot directory management and cleanup.
5. **POM Consolidation**: Move inline locators (search inputs, chart locators) into POMs.
