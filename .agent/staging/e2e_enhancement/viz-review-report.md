# SDET Static Analysis: viz-review.spec.ts

**Target File:** [viz-review.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/viz-review.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested
This test suite captures **visual screenshot artifacts** for manual review rather than verifying functional behavior. Specifically:

- **Page Screenshots:** Asset Library, Protocol Library, Run Protocol Config pages
- **Nav Rail & Responsive:** Sidebar rail visibility, hover state, collapsed view (768px width)
- **Theme Toggle:** Light/dark mode transitions, deck-view in both themes
- **Protocol Detail Panel:** Opening a dialog/detail panel from protocol list

**UI Elements Exercised:**
- `.sidebar-rail`, `.nav-item` (CSS classes)
- `[data-tour-id="theme-toggle"]` (custom attribute)
- `button:has-text(/Simulate/i)` (filter locator)
- `tr[mat-row], app-protocol-card` (component/element selectors)
- `.mat-mdc-dialog-container, app-protocol-detail` (dialog selectors)

**State Changes:**
- Theme transitions (Light → Dark → System → Light)
- Viewport resize (1280x720 → 768x1024)
- Navigation between pages (`/app/home`, `/app/assets`, `/app/protocols`, `/app/run`, `/app/workcell`)

### Assertions (Success Criteria)
**Critical Finding: There are NO meaningful assertions.**

The entire test suite has **zero `expect()` assertions**. Success is determined solely by:
1. Screenshots being captured without throwing errors
2. `console.log()` statements confirming captures

The only implicit "assertions" are:
- `waitFor({ state: 'visible' })` calls that could fail if elements don't appear
- `waitForSelector()` calls with `.catch(() => {})` that swallow failures

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

| Issue | Severity | Location |
|-------|----------|----------|
| **Excessive hardcoded waits** | 🔴 Critical | Lines 28, 33, 40, 47, 56, 68, 75, 84, 91, 98, 102, 109, 119 |
| **`force: true` clicks** | 🟠 High | Lines 90, 107, 108 |
| **CSS class locators** | 🟠 High | Lines 59, 66, 76 |
| **Swallowed errors** | 🟠 High | Lines 60, 123 |
| **No test isolation** | 🟠 High | Entire file |
| **Duplicate splash handling** | 🟡 Medium | Lines 18-20, repeated 8+ times |
| **No DB isolation** | 🟠 High | Uses `resetdb=0` globally |

**Detailed Critique:**

1. **Hardcoded Waits Everywhere** (13 instances of `waitForTimeout`)
   - `await page.waitForTimeout(5000);` appears 4 times — 20 seconds wasted per test
   - 2000ms waits after every navigation — arbitrary, not state-driven
   - Total potential wait time: ~35+ seconds per test, regardless of actual load speed

2. **`force: true` Anti-Pattern**
   - Theme toggle clicked with `force: true` (line 90, 107, 108)
   - Indicates actionability issues (overlays, animations) not properly resolved
   - Should use `waitForOverlay()` helper from `BasePage` instead

3. **Silent Failure Swallowing**
   - `.catch(() => console.log('...'))` on line 60 — hides real failures
   - `.catch(() => {})` on line 123 — completely swallows errors

4. **No Worker-Indexed DB Isolation**
   - Uses `resetdb=0` which prevents parallel execution
   - Does NOT use `worker-db.fixture.ts` infrastructure
   - Will cause flakiness in parallel test runs

### Modern Standards (2026) Evaluation

| Criterion | Status | Details |
|-----------|--------|---------|
| **User-Facing Locators** | 🟠 Partial | Uses `getByRole` in WelcomePage POM, but inline test uses CSS classes (`.sidebar-rail`, `.nav-item`) |
| **Test Isolation** | ❌ Fail | No `afterEach` cleanup, no worker DB isolation, shared state between tests |
| **Page Object Model** | 🟠 Partial | Uses `WelcomePage` for splash handling only; all page-specific logic is inline |
| **Async Angular Handling** | ❌ Fail | Uses timeouts instead of waiting for Angular signals/state stabilization |
| **Strict Mode Compatible** | 🟠 Partial | Most locators are unique, but `.first()` calls may hide issues |

**Missing Best Practices:**
- No `testInfo` passed to POMs for worker isolation
- Imports from `@playwright/test` instead of `worker-db.fixture`
- No use of `BasePage.goto()` which handles service readiness
- No `test.describe.configure({ mode: 'serial' })` despite shared state dependency

---

## 3. Test Value & Classification

### Scenario Relevance
**Classification: Low-Value Screenshot Capture Utility**

This is **NOT a user journey test**. It's a developer utility for:
- Generating visual artifacts for documentation
- Manual review of UI appearance across themes/viewports
- Screenshot regression baseline capture

**User Scenario Validity:** ❌ No real user would perform these actions in sequence:
- Toggle theme multiple times rapidly
- Resize viewport mid-session
- Navigate to every page just to view it

### Classification
**Type: Screenshot Capture Utility (Not E2E Test)**

| Characteristic | Assessment |
|----------------|------------|
| Tests real user journey | ❌ No |
| Validates business logic | ❌ No |
| Has meaningful assertions | ❌ No |
| Tests full stack integration | ❌ No — just UI appearance |
| Can catch regressions | 🟡 Only with manual review |
| Contributes to confidence | ❌ Minimal |

**Recommendation:** Reclassify or move to `e2e/utilities/` or `e2e/visual-capture/` directory to clarify intent.

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

**Test 1: "Capture Page Screenshots"**
1. Navigate to `/app/home` with `mode=browser&resetdb=0`
2. Handle splash screen (dismiss if present)
3. Wait 5 seconds (arbitrary)
4. Navigate to `/app/assets` → capture `asset-library.png`
5. Navigate to `/app/protocols` → capture `protocol-library.png`
6. Navigate to `/app/run` → capture `run-protocol-config.png`

**Test 2: "Capture Nav and Responsive Screenshots"**
1. Navigate to `/app/home`
2. Wait 5 seconds
3. Capture nav rail element
4. Hover first nav item → capture `nav-rail-hover.png`
5. Resize viewport to tablet (768x1024)
6. Capture `sidebar-collapsed.png`

**Test 3: "Capture Theme and Panel Screenshots"**
1. Navigate to `/app/home`
2. Wait 5 seconds
3. Click theme toggle (Light → Dark)
4. Capture `global-dark-mode.png`
5. Navigate to `/app/workcell`
6. Click "Simulate" button
7. Capture `deck-view-dark.png`
8. Toggle theme twice (→ System → Light)
9. Capture `deck-view.png`
10. Navigate to `/app/protocols`
11. Click first protocol row
12. Capture `protocol-detail-panel.png`

### Contextual Fit
**Role:** Developer utility for visual QA, not production test coverage.

This test should be:
- Run manually when verifying UI changes
- NOT included in CI/CD test suite
- Tagged with `@visual` or `@utility` for selective execution
- Potentially converted to Playwright's visual comparison (`toHaveScreenshot()`)

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths
This test is fundamentally a capture utility, but IF it were to be converted to proper E2E tests:

| Gap | Description |
|-----|-------------|
| **No data verification** | Asset library shows items, but no check that data loaded correctly |
| **No theme persistence** | Theme state not verified across navigation |
| **No responsive behavior validation** | Viewport resized, but no assertion that layout adapted |
| **No dialog content verification** | Protocol detail opens, but content not validated |
| **No workcell state verification** | Simulate button clicked, but simulation state not verified |

### Domain Specifics

- **Data Integrity**: ❌ Not addressed
  - `resetdb=0` means using whatever existing state
  - No verification of what data appears in Asset Library or Protocol Library
  - Screenshots captured without validating content correctness

- **Simulation vs. Reality**: ⚠️ Partially addressed
  - Uses `mode=browser` (Pyodide in-browser execution)
  - Clicks "Simulate" button but doesn't verify simulation started
  - No machine state verification

- **Serialization**: ❌ Not addressed
  - No protocol execution tested
  - No verification of Pyodide worker initialization
  - No argument serialization verification

- **Error Handling**: ❌ Not addressed
  - Errors are swallowed (`.catch(() => {})`)
  - No negative test cases
  - No verification of error states/toasts

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 2/10 | UI capture only, no behavior validation |
| **Best Practices** | 2/10 | 13 hardcoded waits, force clicks, no isolation |
| **Test Value** | 2/10 | Utility suite, not regression test |
| **Isolation** | 1/10 | No worker DB, no cleanup, shared state |
| **Domain Coverage** | 1/10 | Zero domain-specific validation |

**Overall**: **1.6/10**

---

## Recommendations

1. **Reclassify** — Move to `e2e/utilities/` or `visual-capture/` directory
2. **Add Visual Regression** — Convert to `toHaveScreenshot()` with baselines
3. **If keeping as test:**
   - Add worker-indexed DB isolation
   - Replace all `waitForTimeout` with state-driven waits
   - Add actual assertions for loaded state
   - Remove `force: true` clicks
4. **Skip in CI** — Add `test.skip` condition or tag-based exclusion
