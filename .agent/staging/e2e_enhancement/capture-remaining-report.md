# SDET Static Analysis: capture-remaining.spec.ts

**Target File:** [capture-remaining.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/capture-remaining.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested
This spec file captures **dialogs for visual documentation/screenshot purposes**, not functional verification. Specifically:

1. **Protocol Upload Dialog** — Opens via a `[data-tour-id]` button on the protocols page
2. **Hardware Discovery Dialog** — Opened via the Command Palette (`Ctrl+K`), typing "Discover"
3. **Welcome Dialog** — Triggered by removing the `praxis_onboarding_completed` localStorage key and navigating with `?welcome=true`

### Assertions (Success Criteria)
| Test | Assertion | Type |
|------|-----------|------|
| Protocol Upload | `dialog.first().toBeVisible()` | Visual presence check |
| Hardware Discovery | `dialog.first().toBeVisible()` | Visual presence check |
| Welcome Dialog | `dialog.first().toBeVisible()` | Visual presence check |

**Critical Observation:** The assertions are purely **visibility-based**. There is **no validation of dialog content, form elements, or expected UI state** within the dialogs.

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

| Issue | Severity | Location |
|-------|----------|----------|
| **Hardcoded `waitForTimeout(1000)`** | 🔴 Critical | `captureDialog()` line 27-28 — arbitrary wait before screenshot |
| **Hardcoded `waitForTimeout(1000)`** | 🔴 Critical | Test "15. hardware-discovery-dialog" line 45 — wait after typing "Discover" |
| **Uses `page.locator('..')` with internal selector** | 🟡 Medium | Line 36: `[data-tour-id="import-protocol-btn"]` — internal implementation detail |
| **Does not import `worker-db.fixture`** | 🔴 Critical | Uses bare `@playwright/test` import; no worker-indexed DB isolation |
| **No POM usage** | 🟡 Medium | Raw page interactions; no abstraction |
| **`Escape` key dismissal without verification** | 🟡 Medium | `captureDialog()` line 30 — assumes Escape closes dialog without checking |
| **`waitForLoadState('networkidle')`** | 🟡 Medium | Lines 21, 35 — can be unreliable in SPAs with background requests |
| **Generic `page.locator('input').fill()` selector** | 🔴 Critical | Line 44 — selects any input on the page (non-unique) |
| **Missing explicit TypeScript type for `page` in helper** | 🟡 Low | `captureDialog(page, name)` — TypeScript implicit any |

### Modern Standards (2026) Evaluation

| Criterion | Status | Notes |
|-----------|--------|-------|
| **User-Facing Locators** | ❌ Fails | Uses `[data-tour-id]`, bare `input`, and CSS selectors instead of `getByRole`, `getByLabel` |
| **Test Isolation** | ❌ Fails | Not using `worker-db.fixture`; `localStorage` manipulation is not run via `addInitScript` |
| **Page Object Model (POM)** | ❌ Fails | Zero abstraction; all logic is inline |
| **Async Angular Handling** | ⚠️ Partial | Uses `waitForFunction` for SQLite readiness (good), but combines with `waitForLoadState('networkidle')` and `waitForTimeout` (bad) |
| **Fixture Utilization** | ❌ Fails | No use of project fixtures (`worker-db.fixture`, `app.fixture`) |

---

## 3. Test Value & Classification

### Scenario Relevance
These tests capture **visual artifacts** for documentation or design review, not functional validation of dialog behavior. This is a **utility/documentation workflow**, not a critical user journey.

- ❌ Not a "Happy Path" functional test
- ❌ Not an edge case test
- ⚠️ Utility: Screenshot capture for design audits or marketing

### Classification
| Aspect | Assessment |
|--------|------------|
| **Type** | **Screenshot Utility** — Not a True E2E or Unit Test |
| **Mocking** | None (uses real app state) |
| **Integration** | Superficial — confirms dialogs open, does not validate contents |
| **CI Value** | Low — screenshots are side-effects, not assertions |

**Verdict:** This is a **Visual Capture Script** masquerading as an E2E test. It should be reclassified or moved to a dedicated screenshot/storybook pipeline.

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

**Test 1: Protocol Upload Dialog**
1. Navigate to `/app/home`, wait for SQLite ready
2. Set `praxis_onboarding_completed` in localStorage
3. Navigate to `/app/protocols`
4. Click the "Import Protocol" button (by `data-tour-id`)
5. Wait for dialog to appear
6. Screenshot, then dismiss with Escape

**Test 2: Hardware Discovery Dialog**
1. Navigate to `/app/home`, wait for SQLite ready
2. Set `praxis_onboarding_completed` in localStorage
3. Press `Ctrl+K` to open Command Palette
4. Type "Discover" into the input
5. Wait 1 second (hardcoded)
6. Press Enter to execute command
7. Wait for dialog to appear
8. Screenshot, then dismiss with Escape

**Test 3: Welcome Dialog**
1. Navigate to `/app/home`, wait for SQLite ready
2. Set `praxis_onboarding_completed` in localStorage (redundant — will be removed)
3. **Remove** `praxis_onboarding_completed` from localStorage
4. Navigate to `/app/home?welcome=true`
5. Wait for dialog to appear
6. Screenshot, then dismiss with Escape

### Contextual Fit
These tests are **tangential** to the core Praxis lab automation system. They:
- Validate dialogs can be opened (but not their content)
- Generate screenshots for design review or documentation
- Have no relationship to protocol execution, asset management, or machine control

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Severity | Description |
|-----|----------|-------------|
| **No content validation** | 🔴 High | Dialogs could be empty/broken and tests would pass |
| **No form interaction** | 🔴 High | Protocol upload dialog untested for file selection |
| **No hardware discovery verification** | 🔴 High | Does the discovery actually find anything? |
| **No welcome flow completion** | 🔴 High | Welcome dialog not exercised beyond screenshot |
| **No negative cases** | 🟡 Medium | What if dialogs fail to open? |

### Domain Specifics

| Area | Assessment |
|------|------------|
| **Data Integrity** | ❌ Not verified — no `praxis.db` content checks |
| **Simulation vs. Reality** | N/A — screenshots only |
| **Serialization** | N/A — no Pyodide/worker interaction |
| **Error Handling** | ❌ Not covered — no failure mode tests |

### Specific Issues

1. **welcomeDialog test is contradictory** — Sets `praxis_onboarding_completed` in `beforeEach`, then removes it inside the test. The `beforeEach` hook runs before every test, including this one, making the initial set redundant.

2. **Command Palette interaction is fragile** — Uses `page.locator('input').fill('Discover')` which will match the **first input on the page**, not necessarily the command palette input. If the page structure changes, this will break silently.

3. **Screenshot directory assumption** — `screenshotDir` is computed relative to `process.cwd()`, which can vary based on how tests are invoked.

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 2/10 | Screenshots only; no functional validation |
| **Best Practices** | 2/10 | Multiple hardcoded waits, no POM, no isolation |
| **Test Value** | 2/10 | Utility script, not a real test |
| **Isolation** | 2/10 | Missing worker-db fixture; localStorage not isolated |
| **Domain Coverage** | 1/10 | Zero domain-specific verification |

**Overall**: **1.8/10**

---

## Recommendations

### Short-Term (Quick Wins)
1. **Reclassify** — Move to a `e2e/scripts/` or `e2e/visual-capture/` directory
2. **Mark as skip** — `test.skip` or `test.fixme` to exclude from CI
3. **Remove hardcoded waits** — Replace with `expect(dialog).toBeVisible()` chaining

### Long-Term (Proper Screenshot Pipeline)
1. **Use Playwright's screenshot comparison** — `expect(page).toHaveScreenshot()` for visual regression
2. **Integrate with Storybook** — If dialogs are Material components, use Storybook for isolated visual testing
3. **Add functional assertions** — If keeping as E2E, validate dialog content (forms, buttons, expected text)
