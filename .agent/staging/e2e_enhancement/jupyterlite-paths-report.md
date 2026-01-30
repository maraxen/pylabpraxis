# SDET Static Analysis: jupyterlite-paths.spec.ts

**Target File:** [jupyterlite-paths.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/jupyterlite-paths.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist  
**Baseline Score:** **4.5/10** (Partial Infrastructure Smoke)

---

## 1. Test Scope & Coverage

### What is Tested

| Verification Area | Covered? | Line(s) | Notes |
|-------------------|----------|---------|-------|
| **REPL Config Relative Paths** | ✅ | L17-25 | Verifies `jupyter-lite.json` uses `../build/schemas` and `../build/themes` |
| **Schemas Endpoint Accessibility** | ✅ | L27-33 | Confirms `/assets/jupyterlite/build/schemas/all.json` returns 200 |
| **Theme CSS Accessibility** | ✅ | L35-41 | Confirms theme CSS returns 200 with correct MIME type |
| **Response Listener for Path Doubling** | ✅ | L45-65 | Captures `/praxis/.../praxis/` and `/assets/jupyterlite/.../assets/jupyterlite/` duplications |
| **Playground Page Load** | ⚠️ | L68-81 | Navigates but relies on hardcoded timeout |
| **Iframe Initialization Check** | ⚠️ | L83-94 | Partial—checks `app-playground` visibility, not iframe content |
| **GH Pages Production Config** | ❌ | L103-121 | **Skipped** (`test.describe.skip`) — not executable |

### Assertions (Success Criteria)

| Assertion | Purpose | Mode |
|-----------|---------|------|
| `expect(response?.status()).toBe(200)` | Config file accessible | HTTP Status |
| `expect(config['jupyter-config-data']['settingsUrl']).toBe('../build/schemas')` | Relative path not doubled | Literal Match |
| `expect(config['jupyter-config-data']['themesUrl']).toBe('../build/themes')` | Relative path not doubled | Literal Match |
| `expect(contentType).toContain('application/json')` | Correct MIME type | Contains |
| `expect(contentType).toContain('text/css')` | Correct MIME type | Contains |
| `expect(doubledPathRequests).toHaveLength(0)` | No path doubling detected | Array Length |
| `expect(page.locator('app-playground')).toBeVisible()` | Angular component mounts | Visibility |

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique: Brittle Patterns Identified

| Issue | Location | Severity | Details |
|-------|----------|----------|---------|
| **Hardcoded `waitForTimeout`** | L72 | 🔴 **Critical** | `page.waitForTimeout(5000)` is an explicit time-based wait with no state-driven fallback. Should poll for console log, network idle on JupyterLite assets, or kernel ready state instead. |
| **Skipped Production Tests** | L103 | 🔴 **Critical** | `test.describe.skip` means GH Pages simulation is **never executed** in CI. These are commented-out, not conditional, making them dead code. |
| **CSS Selector for Iframe** | L90 | 🟡 **Medium** | `iframe[src*="jupyterlite"], .jupyter-container` uses implementation-detail selectors. If the class or `src` pattern changes, test breaks. |
| **Component-Tag Selector** | L87, L93 | 🟡 **Medium** | `app-playground` is an Angular implementation detail, not a user-facing role or test ID. |
| **Silent Console Logging** | L78-80 | 🟡 **Medium** | Failed requests are logged but not asserted. Test passes even if critical JupyterLite resources 404. |
| **No Worker Isolation** | Entire file | 🟡 **Medium** | Direct `page.goto()` without `dbName=praxis-worker-{index}`. Would conflict in parallel execution. |
| **No POM Usage** | Entire file | 🟡 **Medium** | No Page Object encapsulation—all logic inline. |
| **No Cleanup** | Entire file | 🟢 **Low** | Tests are read-only (fetch configs, navigate), minimal side effects. |

### Modern Standards (2026) Evaluation

| Criterion | Status | Notes |
|-----------|--------|-------|
| **User-Facing Locators** | ❌ Missing | Uses `iframe[src*="jupyterlite"]`, `app-playground` — no `getByRole` or `getByTestId`. |
| **Web-First Assertions** | ⚠️ Partial | Uses `expect(locator).toBeVisible()` ✅, but HTTP response checks are synchronous (OK for config files). |
| **Test Isolation** | ❌ Missing | No `dbName` param, no `resetdb=1`. Would collide in parallel workers. |
| **Cleanup** | ✅ N/A | Tests are stateless reads. |
| **Page Object Model** | ❌ None | No `PlaygroundPage` or `JupyterAssetVerifier` POM. |
| **Async Angular Handling** | ❌ Missing | No `waitForFunction` on Angular signals or SQLite service readiness. Uses raw `waitForSelector` with hardcoded timeout. |
| **No Hardcoded Waits** | ❌ Fails | `waitForTimeout(5000)` at L72. |

---

## 3. Test Value & Classification

### Scenario Relevance

| Question | Answer |
|----------|--------|
| **Is this a Critical User Journey?** | ⚠️ **Infrastructure Support.** This is not a user-visible flow—it verifies internal path resolution for multi-environment deployments. |
| **Happy Path or Edge Case?** | **Infrastructure Parity.** This is a "deployment correctness" test, not a user workflow. |
| **Would a Real User Perform This?** | ❌ **No.** Users do not manually fetch `jupyter-lite.json` or inspect path prefixes. They just open the Playground. |

### Classification

| Category | Assessment |
|----------|------------|
| **True E2E Test?** | ❌ **No.** This tests static asset configuration and network responses—not user interaction through the full stack. |
| **Integration Smoke Test?** | ⚠️ **Partially.** It exercises the Angular dev server serving JupyterLite assets, but does not verify the JupyterLite runtime or kernel. |
| **Infrastructure/Deployment Test?** | ✅ **Best Fit.** This is a **contract test** for correct `baseUrl` and relative path resolution when deployed to subdirectories like `/praxis/`. |
| **Interactive Unit Test?** | ❌ No. It does not mock anything; it hits the real dev server. |

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

Based **only on the test code**, the intended verification is:

1. **Fetch `/assets/jupyterlite/repl/jupyter-lite.json` directly via HTTP.**
   - Expect 200 status.
   - Parse JSON and verify `settingsUrl` and `themesUrl` use relative paths (`../build/...`), not absolute paths that could cause duplication.

2. **Fetch `/assets/jupyterlite/build/schemas/all.json`.**
   - Expect 200 status.
   - Confirm `Content-Type` is `application/json`.

3. **Fetch `/assets/jupyterlite/build/themes/@jupyterlab/theme-light-extension/index.css`.**
   - Expect 200 status.
   - Confirm `Content-Type` is `text/css`.

4. **Navigate to `/playground` and install network listener.**
   - Capture any response URLs containing doubled paths (`/praxis/.../praxis/` or `/assets/jupyterlite/.../assets/jupyterlite/`).
   - Wait 5 seconds (hardcoded).
   - Assert zero doubled-path requests.
   - Verify `app-playground` component is visible.

5. **Verify iframe element exists (soft check).**
   - Locate `iframe[src*="jupyterlite"]` or `.jupyter-container`.
   - Only verify `app-playground` is visible, not the iframe content.

6. **(Skipped) GH Pages Production Tests.**
   - Intended to verify `baseUrl: '/praxis/assets/jupyterlite/'` and correct relative paths in production config.

### Contextual Fit

This test addresses **Issue #123 (Path Doubling Bug)** pattern:
- When deployed to a subdirectory (e.g., GitHub Pages at `https://user.github.io/praxis/`), JupyterLite's internal `fetch()` calls can produce malformed URLs like `/praxis/praxis/assets/...` if:
  1. The Angular `base href` is set to `/praxis/`.
  2. JupyterLite configs use absolute `baseUrl` values that get prepended incorrectly.
  
The solution (which this test verifies) is:
- Use **relative paths** in `jupyter-lite.json` for nested resources.
- Use **explicit absolute paths** only in the root config.

This is a **deployment parity test**—not a user journey test.

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Description | Risk |
|-----|-------------|------|
| **Production Mode Never Tested** | `test.describe.skip` at L103 means GH Pages config (`baseUrl: '/praxis/assets/jupyterlite/'`) is **never verified** in CI. The development mode tests may pass while production deployments fail. | 🔴 **Critical.** Production-only regressions would go undetected. |
| **No Assertion on `failedRequests`** | L77-80 logs 404s but does not assert. Test passes even if core JupyterLite resources fail to load. | 🟡 **Medium.** Could mask asset-serving regressions. |
| **Iframe Content Not Verified** | L83-94 checks for `app-playground` visibility but not that the iframe has loaded or the kernel is responsive. | 🟡 **Medium.** Iframe could be a blank `about:blank` and test would pass. |
| **No Network Idle Wait** | Uses `waitForTimeout(5000)` instead of waiting for JupyterLite's background asset fetches to complete. | 🟡 **Medium.** Timing-sensitive—could miss late-loading doubled paths. |
| **No COOP/COEP Header Verification** | SharedArrayBuffer and cross-origin isolation are critical for Pyodide/JupyterLite. No test verifies these headers are set. | 🟡 **Medium.** Production could break if headers are misconfigured. |

### Domain-Specific Verification Gaps

| Domain Area | Covered? | Notes |
|-------------|----------|-------|
| **Data Integrity (`praxis.db`)** | ❌ N/A | Not relevant to this test scope. |
| **Simulation vs. Reality** | ❌ N/A | Not relevant—tests static asset paths, not runtime execution. |
| **Serialization** | ❌ N/A | Not relevant—no Python execution in this test. |
| **Error Handling** | ❌ Not Tested | No verification of graceful fallback if `jupyter-lite.json` is malformed or missing. |
| **Wheel File Accessibility** | ❌ Not Tested | Does not verify `.whl` files for `pylabrobot` or `micropip` are accessible without path doubling. |
| **Worker Isolation** | ❌ Not Tested | No `dbName` param—would conflict in parallel execution (though test is mostly stateless). |

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 5/10 | Covers dev mode config and path patterns; production mode skipped. |
| **Best Practices** | 3/10 | `waitForTimeout`, no POM, no worker isolation, CSS selectors. |
| **Test Value** | 4/10 | Infrastructure test, not user journey. Skipped production tests reduce value further. |
| **Isolation** | 4/10 | Stateless reads, but no explicit worker DB params if expanded. |
| **Domain Coverage** | 5/10 | Path resolution checked; no header or wheel verification. |

**Overall**: **4.5/10** — Useful infrastructure smoke test for dev mode, but production mode is never tested and patterns are outdated.

---

## Related Resources

- **KI Reference:** [Praxis Testing Knowledge > Subdirectory and BaseURL Navigation](file:///Users/mar/.local/share/ov/profiles/fast-gemini-flash/.gemini/antigravity/knowledge/praxis_testing_knowledge/artifacts/best_practices/angular_playwright_2026.md#7-subdirectory-and-baseurl-navigation)
- **Host Component:** [PlaygroundComponent](file:///Users/mar/Projects/praxis/praxis/web-client/src/app/features/playground/playground.component.ts)
- **Deployment Spec:** [ghpages-deployment.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/ghpages-deployment.spec.ts)
