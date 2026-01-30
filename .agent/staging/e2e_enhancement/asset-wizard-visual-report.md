# SDET Static Analysis: asset-wizard-visual.spec.ts

**Target File:** [asset-wizard-visual.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/asset-wizard-visual.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested
This test file performs **visual validation** of the Asset Wizard's **grid layout optimization** across three wizard steps. Unlike the functional `asset-wizard.spec.ts`, this test focuses on **screenshot capture** and **UI element rendering** rather than complete asset creation. Specifically:

1. **Navigation & Initialization**: Navigates to `/assets?mode=browser&resetdb=1` and waits for SQLite service readiness.
2. **Welcome Dialog Dismissal**: Attempts to dismiss onboarding modals via role-based button matching.
3. **Wizard Invocation**: Opens the Asset Wizard via `[data-tour-id="add-asset-btn"]` with force click.
4. **Step 1 - Asset Type Cards**: Verifies exactly 2 type cards render and captures screenshot.
5. **Step 2 - Category Cards**: Selects "Machine" type, verifies category cards exist (count > 0), captures screenshot.
6. **Step 3 - Machine Selection Grid**: Selects "LiquidHandler" category, verifies result cards render in `.results-grid`, captures screenshot.

**UI Elements Covered:**
- `[data-tour-id="add-asset-btn"]` button
- `app-asset-wizard` component shell
- `.type-card` elements (Step 1)
- `.category-card` elements (Step 2)
- `.results-grid` and `.result-card` elements (Step 3)
- `Next` button navigation

**State Changes Verified:**
- Wizard opens (stepper progression)
- Grid layouts render with mock data
- **No actual asset creation or persistence**

### Assertions (Success Criteria)

| Assertion | Line | Purpose |
|-----------|------|---------|
| `expect(addAssetBtn).toBeVisible()` | 55 | Add Asset button rendered |
| `expect(wizard).toBeVisible()` | 61 | Wizard dialog opened |
| `expect(wizard.locator('.type-card')).toHaveCount(2)` | 64 | Exactly 2 asset types displayed |
| `expect(catCount).toBeGreaterThan(0)` | 75 | At least 1 category card exists |
| `expect(grids.first()).toBeVisible()` | 91 | Machine selection grid rendered |
| `expect(resultCount).toBeGreaterThan(0)` | 95 | At least 1 result card in grid |

**Note**: Assertions are UI-centric with **no domain verification**. Success is purely visual—no validation of data integrity, persistence, or API consumption.

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

| Issue | Severity | Lines | Details |
|-------|----------|-------|---------|
| **Hardcoded `waitForTimeout(500)`** | 🔴 High | 98 | Fixed 500ms wait for "animation settling" before final screenshot. Should wait for CSS animation completion or use `expect().toBeVisible()` with appropriate timeout. |
| **Uses `force: true` Click** | 🔴 High | 58 | Forces click bypassing actionability checks. Indicates underlying overlay or animation issue that should be resolved structurally. |
| **Ignores `app.fixture.ts` / `worker-db.fixture.ts`** | 🔴 High | 1 | Imports from raw `@playwright/test`. Tests will conflict in parallel runs—workers share the same OPFS database. |
| **CSS Selectors: `.type-card`, `.category-card`, `.result-card`, `.results-grid`** | 🟡 Medium | 64, 72-95 | Internal implementation details rather than semantic/accessible selectors. Brittle against component refactors. |
| **Empty Catch Block Swallows Errors** | 🟡 Medium | 44-51 | `try/catch` with `catch (e) {}` silently ignores welcome dialog failures. May mask real blocking issues. |
| **Fallback Logic Masks Test Intent** | 🟡 Medium | 81-85 | Fallback from mocked `LiquidHandler` to first card dilutes assertion—test may pass even if mock failed. |
| **Relative Screenshot Paths** | 🟢 Low | 65, 77, 99 | Screenshots saved to `praxis/web-client/e2e/screenshots/...` relative path. Should use `testInfo.outputPath()` for CI artifact collection. |
| **No `afterEach` Cleanup** | 🟠 Medium | N/A | Test doesn't clean up wizard state or created artifacts between runs. |
| **Inconsistent `waitForSelector` with `.catch(() => {})`** | 🟡 Medium | 49 | Silent failure on backdrop wait can hide overlay persistence bugs. |

### Modern Standards (2026) Evaluation

| Criterion | Rating | Notes |
|-----------|--------|-------|
| **User-Facing Locators** | 5/10 | Uses `getByRole('button')` for navigation and dialog dismissal (good), but heavily relies on CSS class selectors (`.type-card`, `.category-card`, `.result-card`) for primary assertions. Should use `data-testid` or semantic locators. |
| **Test Isolation** | 3/10 | Uses `resetdb=1` for DB reset but lacks worker-indexed database isolation. No cleanup hooks. The test leaves the wizard in an unknown state (Step 3, not closed). |
| **Page Object Model (POM)** | 1/10 | **Does NOT use any POM**. The existing `BasePage` and potential `WizardPage` abstraction are ignored. All locator logic is inline, duplicating `asset-wizard.spec.ts`. |
| **Async Angular Handling** | 4/10 | Uses `waitForFunction()` for SQLite readiness (good), but `waitForTimeout(500)` for animations is an anti-pattern. Should leverage `expect(element).toBeVisible()` with auto-waiting or Angular zone stability checks. |

**Additional 2026 Issues:**
- **No Visual Regression Baseline**: Screenshots are captured but not compared against golden images. The "visual validation" claim is misleading—this is screenshot capture, not visual regression testing.
- **Mock Data Verification Gap**: Mocks 5 `LiquidHandler` definitions but never asserts that exactly 5 result cards appear. The test would pass even if the mock was ignored.

---

## 3. Test Value & Classification

### Scenario Relevance

| Aspect | Assessment |
|--------|------------|
| **User Journey Type** | **Visual Verification Utility** — Not a true user journey. This is a screenshot capture workflow for manual visual inspection, not automated validation. |
| **Real User Scenario** | ⚠️ Partial — Users do navigate the wizard, but they complete asset creation. This test stops at Step 3 without creating anything. |
| **Criticality** | **Low** — Visual appearance is important, but without baseline comparison this test only produces screenshots for manual review. Build failures won't be detected. |

### Classification

| Classification | Verdict |
|----------------|---------|
| **True E2E** vs **Interactive Unit** | **Screenshot Capture Utility** — Mocks all API responses, doesn't complete the workflow, doesn't verify persistence. This is closer to a manual QA helper than an automated E2E test. |
| **Integration Level** | Minimal — Tests Angular UI rendering with mock data. SQLite is initialized but not exercised (no writes). |

**Value Assessment:**
- As currently written, this test provides **minimal automated regression value**.
- It would be valuable if converted to a proper visual regression test using Playwright's `expect(page).toHaveScreenshot()` with golden baselines.

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

```
1. User navigates to /assets?mode=browser&resetdb=1
   ├─ App initializes SQLite OPFS database
   └─ Waits for sqliteService.isReady$ = true

2. [Optional] Welcome dialog appears
   ├─ User clicks "Get Started" / "Skip" / "Close"
   └─ Waits for CDK overlay backdrop to detach

3. User clicks "Add Asset" button (force click bypasses overlays)
   └─ Asset Wizard (`app-asset-wizard`) opens

4. STEP 1: Asset Type Selection
   ├─ User sees 2 type cards (Machine, Resource presumably)
   ├─ [SCREENSHOT: new-wizard-step1-types.png]
   ├─ User clicks first type card (Machine)
   └─ User clicks "Next"

5. STEP 2: Category Selection
   ├─ User sees category cards (count > 0, data from real or mock)
   ├─ [SCREENSHOT: new-wizard-step2-categories.png]
   ├─ User locates "LiquidHandler" card (or falls back to first)
   └─ User clicks "Next"

6. STEP 3: Machine Selection Grid
   ├─ User sees results grid with machine definition cards
   ├─ Waits 500ms for animations
   └─ [SCREENSHOT: new-wizard-step3-grid.png]

7. TEST ENDS (wizard remains open, no asset created)
```

### Contextual Fit

This test exists as a **visual audit companion** to `asset-wizard.spec.ts`:

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Asset Wizard Test Suite                          │
├─────────────────────────────────────────────────────────────────────┤
│  asset-wizard.spec.ts         │  asset-wizard-visual.spec.ts        │
│  └─ Functional Happy Path     │  └─ Screenshot Capture (3 steps)    │
│     • Creates Hamilton STAR   │     • No asset creation             │
│     • Verifies persistence    │     • No assertions on data         │
│     • Tests full workflow     │     • Manual visual review          │
├─────────────────────────────────────────────────────────────────────┤
│  DUPLICATION: ~70% of navigation logic is identical                  │
│  RECOMMENDATION: Consolidate into single POM-based test with        │
│                  optional screenshot points                          │
└─────────────────────────────────────────────────────────────────────┘
```

**Purpose Inferred:**
- Created during grid layout optimization work (line 5: "should display optimized grid layouts")
- Intended for manual comparison of before/after wizard card layouts
- Not designed for automated CI regression

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Impact | Recommendation |
|-----|--------|----------------|
| **No Asset Creation** | High | Test stops at Step 3. Doesn't verify complete wizard flow or asset persistence. |
| **No Visual Baseline Comparison** | High | Screenshots are captured but never compared. Use `expect(page).toHaveScreenshot()` with baselines. |
| **Mock Data Verification** | Medium | Mocks 5 LiquidHandler definitions but doesn't assert exactly 5 cards render. |
| **No Cleanup** | Medium | Wizard remains open at test end. May affect subsequent tests in serial execution. |
| **Parallel Safety** | High | No worker-indexed DB isolation. Will fail or corrupt state in parallel runs. |
| **Animation State Verification** | Medium | Waits 500ms but doesn't verify animations completed. CSS class-based transition checks needed. |

### Domain Specifics

| Area | Current Coverage | Gap |
|------|------------------|-----|
| **Data Integrity** | ❌ None | No verification that mocked data is consumed. Grid displays "something" but could be default/error state. |
| **Simulation vs. Reality** | ⚠️ Fully Mocked | Both `/facets` and `/frontends` API endpoints are mocked. Real definition catalog behavior is untested. |
| **Serialization** | ❌ None | Test never reaches backend/driver selection or asset creation. No config serialization tested. |
| **Error Handling** | ❌ None | No tests for: API failures, empty category scenarios, grid rendering errors, or wizard step validation. |
| **Grid Optimization Claims** | ⚠️ Unverified | Test name claims "optimized grid layouts" but doesn't measure: card count, spacing, responsive breakpoints, or performance metrics. |

### Visual Test Integrity Issues

| Issue | Detail |
|-------|--------|
| **Relaxed Assertions** | `catCount > 0` and `resultCount > 0` are weak. With mock data providing 5 definitions, test should verify exactly 5 cards. |
| **Fallback Logic** | Lines 81-85 fall back to first card if LiquidHandler not visible—this masks mock application failures. |
| **No Responsive Testing** | Grid optimization should be tested across viewport sizes. Test runs at default viewport only. |

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 3/10 | Captures screenshots of 3 wizard steps; no workflow completion or data verification |
| **Best Practices** | 3/10 | Force clicks, hardcoded waits, no POM, CSS selectors, empty catch blocks |
| **Test Value** | 2/10 | Screenshot utility without baseline comparison provides minimal automated value |
| **Isolation** | 2/10 | No fixture usage, no worker DB isolation, no cleanup, leaves wizard open |
| **Domain Coverage** | 1/10 | Purely visual; no data integrity, serialization, error handling, or mock verification |

**Overall**: **2.2/10**

---

## Priority Improvements

1. **🔴 Critical**: Convert to proper visual regression using `expect(page).toHaveScreenshot('step1-types.png')` with baseline images
2. **🔴 Critical**: Import from `fixtures/worker-db.fixture` for parallel-safe DB isolation
3. **🔴 Critical**: Replace `force: true` click with proper overlay handling via `waitForOverlaysToDismiss()` helper
4. **🔴 Critical**: Remove `waitForTimeout(500)` — use animation completion detection or stable locator assertions
5. **🟡 High**: Add `afterEach` cleanup to close wizard (press Escape or close button)
6. **🟡 High**: Strengthen assertions: verify exact card counts match mock data (5 LiquidHandler definitions → 5 result cards)
7. **🟡 High**: Remove fallback logic (lines 81-85) — if mock failed, test should fail explicitly
8. **🟠 Medium**: Add responsive viewport tests (tablet, mobile) for true grid optimization validation
9. **🟠 Medium**: Consider consolidation with `asset-wizard.spec.ts` — add screenshot checkpoints to functional test
10. **🟢 Low**: Use `testInfo.outputPath()` for screenshot paths to integrate with CI artifact collection

---

## Comparison with Related Tests

| Aspect | asset-wizard.spec.ts | asset-wizard-visual.spec.ts |
|--------|---------------------|----------------------------|
| **Score** | 4.6/10 | 2.2/10 |
| **Workflow Completion** | ✅ Creates asset | ❌ Stops at Step 3 |
| **Persistence Check** | ✅ (text visible) | ❌ None |
| **Screenshot Capture** | 7 screenshots | 3 screenshots |
| **Mock Verification** | ❌ Shallow | ❌ None |
| **POM Usage** | ❌ No | ❌ No |
| **Fixture Usage** | ❌ No | ❌ No |

**Consolidation Opportunity**: ~70% code duplication. Both should be refactored into a shared POM with optional screenshot checkpoints controlled via test configuration.
