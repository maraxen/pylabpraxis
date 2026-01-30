# SDET Static Analysis: 01-onboarding.spec.ts

**Target File:** [01-onboarding.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/01-onboarding.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested
This test file verifies the **first-time user onboarding experience**:
- Simulates a first-time user by clearing `localStorage`
- Navigates to the application root
- Checks for a **splash/welcome screen** (specifically a heading containing "Welcome to Praxis")
- Dismisses the splash via a "Skip" or "Start Tutorial" button
- Verifies the **dashboard loaded** by asserting visibility of the `.sidebar-rail` element (the main layout navigation rail)

### Assertions (Success Criteria)
| Assertion | Method | Location |
|-----------|--------|----------|
| Splash screen appears | `waitFor({ state: 'visible' })` | `WelcomePage.handleSplashScreen()` (L19) |
| Sidebar rail is visible | `toBeVisible()` | `WelcomePage.verifyDashboardLoaded()` (L33) |

**Key Observation:** Assertions are minimal. The test only confirms visual presence of the splash and the sidebar rail. It does **not** verify:
- Actual onboarding content/steps
- Tutorial flow completion
- Persistence of "onboarding completed" state
- Correct routing post-dismissal

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

| Issue | Severity | Location | Description |
|-------|----------|----------|-------------|
| **Implicit sync via `try/catch`** | 🟡 Medium | `WelcomePage.handleSplashScreen()` | Uses a `try/catch` around `waitFor` with a 5s timeout. If the splash genuinely fails, the error is swallowed silently with only a `console.log`. This masks genuine failures. |
| **Hardcoded timeout (5000ms)** | 🟡 Medium | `WelcomePage.handleSplashScreen()` L19 | Arbitrary wait; may be too short for slow CPU/CI or too long for fast local runs. |
| **CSS class-based assertion** | 🔴 High | `WelcomePage.verifyDashboardLoaded()` L33 | Uses `.sidebar-rail` (internal implementation detail) instead of user-facing locators like `getByRole('navigation')` or `getByTestId`. This is **brittle** if styling/structure changes. |
| **No TestInfo passed to WelcomePage** | 🟡 Medium | Spec L13 | `WelcomePage` extends `BasePage`, which supports worker-indexed DB isolation via `testInfo`. However, `testInfo` is **not passed** in the constructor call. This **disables parallel isolation**. |
| **Duplicative navigation** | 🟢 Low | Spec L7-9 vs. L15-16 | The spec's `beforeEach` navigates to `/` and reloads. Then `welcomePage.goto()` navigates again. This is redundant and adds unnecessary page loads. |
| **Storage cleared *after* navigation** | 🟡 Medium | Spec L7-9 | The test navigates to `/`, then clears localStorage, then reloads. However, Angular services may have already read localStorage during the first navigation's bootstrap. The clear+reload pattern should work, but is not the most robust approach (see `addInitScript` pattern or route setup). |

### Modern Standards (2026) Evaluation

| Practice | Status | Notes |
|----------|--------|-------|
| **User-Facing Locators** | ⚠️ **Mixed** | `getByRole('button', { name: /Skip/i })` and `getByRole('heading', ...)` are good. However, `page.locator('.sidebar-rail')` is an internal CSS class. |
| **Test Isolation** | ❌ **Incomplete** | Does not use `worker-db.fixture.ts` for DB isolation. Does attempt localStorage reset, but pattern is not fully robust. No `afterEach` cleanup. |
| **Page Object Model (POM)** | ✅ **Good** | Uses `WelcomePage` which extends `BasePage`. Locators are defined as class properties. |
| **Async Angular Handling** | ⚠️ **Partial** | `BasePage.goto()` waits for `sqliteService.isReady$`, which is correct. However, `WelcomePage.goto()` inherits this but **does not pass `testInfo`**, so the worker-indexed DB logic is skipped. The splash handling uses a `try/catch` which can mask failures. |

---

## 3. Test Value & Classification

### Scenario Relevance
- **Happy Path?** **Yes** — This is a critical first-touch user journey. A broken onboarding experience is a high-impact UX failure.
- **Realistic Scenario?** **Partially** — The test simulates a first-time user, which is realistic. However, it only verifies that *something* appears and navigation to the dashboard succeeds. It doesn't test the *actual onboarding content* or user choices.

### Classification
| Metric | Classification |
|--------|----------------|
| **Type** | **Shallow E2E / Smoke Test** |
| **Mocking Level** | Low (uses real app, clears storage for isolation) |
| **Integration Depth** | Low (only verifies DOM presence, not state changes or persistence) |

**Verdict:** This is a **Smoke Test** masquerading as an E2E journey test. It confirms "the app boots and shows something" but doesn't verify the onboarding *functionality*.

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

```
1. User visits the application for the first time (localStorage is empty)
2. Application bootstraps and shows a "Welcome to Praxis" splash screen
3. User sees two options: "Start Tutorial" or "Skip"
4. User clicks one of the buttons (test prefers "Skip")
5. Splash screen dismisses
6. User arrives at the dashboard (indicated by visible sidebar navigation rail)
```

### Contextual Fit
The **onboarding flow** is the entry point for all new users. It sets the tone for the application experience. In a lab automation context (Praxis), onboarding likely involves:
- Explaining the browser-based SQLite database
- Introducing the asset management workflow (machines, plates, reagents)
- Guiding users to create their first protocol
- Possibly loading default data (`praxis.db`)

This test verifies the *shell* of this journey but not its *substance*. It's a necessary but **insufficient** gate for release confidence.

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths
| Gap | Severity | Description |
|-----|----------|-------------|
| **Tutorial flow not tested** | 🔴 High | The "Start Tutorial" button is handled but its corresponding flow is never exercised. |
| **Onboarding completion persistence** | 🔴 High | No assertion that `localStorage.setItem('praxis_onboarding_completed', 'true')` (or equivalent) is set after dismissal. |
| **Dashboard content verification** | 🟡 Medium | Only the sidebar rail visibility is checked. No verification of actual dashboard widgets (workcell status, quick actions, etc.). |
| **Parallel execution safety** | 🟡 Medium | Does not use worker-indexed DB, risking state leakage in parallel runs. |

### Domain Specifics

| Domain Check | Status | Details |
|--------------|--------|---------|
| **Data Integrity** | ❌ Not Tested | Does not verify that `praxis.db` is correctly initialized or that default seed data is present post-onboarding. |
| **Simulation vs. Reality** | N/A | No simulated instruments involved in this test. |
| **Serialization** | N/A | No protocol submission or Pyodide worker interaction. |
| **Error Handling** | ❌ Not Tested | What happens if the splash screen fails to render? The `try/catch` swallows the error silently. No negative test for corrupted localStorage or missing assets. |

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 4/10 | Covers only splash appearance and sidebar visibility. |
| **Best Practices** | 5/10 | Good POM usage, but CSS selector instead of ARIA, missing TestInfo, silent error swallowing. |
| **Test Value** | 4/10 | Smoke-level verification, not a true journey test. |
| **Isolation** | 4/10 | localStorage reset is attempted but pattern is not robust; no worker-indexed DB. |
| **Domain Coverage** | 2/10 | No verification of onboarding content, data seeding, or state persistence. |

**Overall**: **3.8/10** — This is a **minimal smoke test** that should be either:
1. **Promoted** to a full onboarding journey test covering tutorial steps and state persistence, or
2. **Reclassified** as a smoke/health check and complemented with dedicated onboarding tests.
