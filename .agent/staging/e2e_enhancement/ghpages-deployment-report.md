# SDET Static Analysis: ghpages-deployment.spec.ts

**Target File:** [ghpages-deployment.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/ghpages-deployment.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested

This spec file validates the **GitHub Pages production deployment environment simulation**. It focuses on infrastructure concerns rather than application-level user journeys:

| Test Group | Tests | Focus |
|------------|-------|-------|
| **JupyterLite Path Resolution** | 6 tests | Resource pathing in `/praxis/` subdirectory; 404 detection; doubled-path prevention; theme CSS and schema JSON loading; REPL config relative paths; root config absolute paths |
| **Angular SPA Routing** | 4 tests | Route accessibility (`/app/home`, `/playground`, `/app/run-protocol`); deep links; asset loading validation |
| **Pyodide/SharedArrayBuffer Headers** | 2 tests | `Cross-Origin-Opener-Policy` and `Cross-Origin-Embedder-Policy` headers for SharedArrayBuffer |
| **Branding & Logo** | 1 test | Visual splash/logo renders on home |
| **SQLite/Browser Mode Initialization** | 1 test | `SqliteService.isReady$` observable reaches `true` |

**Key state changes verified:**
- HTTP response status codes (200 vs. 404)
- HTTP headers (COOP/COEP)
- URL structure/routing (no path doubling, correct base href)
- Service readiness via `window.sqliteService.isReady$.getValue()`

### Assertions (Success Criteria)

| Assertion Type | Location | Description |
|----------------|----------|-------------|
| **Resource 404 collection** | L45–47 | `failedResources` array must be empty |
| **Doubled path collection** | L77–79 | `doubledPaths` array must be empty |
| **HTTP 200** | L88, L95, L102, L114 | Direct resource fetches return `200 OK` |
| **JSON content validation** | L108–109, L120–121 | Config fields match expected path values |
| **Response `ok()`** | L129, L137 | SPA routes return HTTP success |
| **URL containment** | L132, L146 | URL includes `/praxis/` |
| **Component visibility** | L139, L208 | `app-playground`, logo elements visible |
| **Header equality** | L186, L193 | COOP = `same-origin`, COEP = `require-corp` |
| **Service readiness** | L226 | `window.sqliteService.isReady$.getValue() === true` |

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

| Issue | Severity | Location | Description |
|-------|----------|----------|-------------|
| **Hardcoded `waitForTimeout`** | 🔴 High | L39, L75 | 5–8 second fixed waits; no intelligent state-waiting; flaky under load |
| **Magic numbers** | 🟡 Medium | L39 (8000), L75 (5000), L139 (15000), L203 (15000), L223 (60000) | Inconsistent timeout values without constants |
| **Weak locator strategy** | 🟡 Medium | L207 | `[class*="logo"], img[alt*="Praxis"], svg` is extremely broad; could match unrelated elements |
| **No POM abstraction** | 🟡 Medium | Throughout | All logic is inline; no Page Object for `/playground` or `/app/home` |
| **Known bug exclusion** | 🟠 Low | L163–168 | `sqlite3-opfs-async-proxy.js` failure is silently ignored—technical debt under-tracked |
| **Missing cleanup** | 🟡 Medium | N/A | Tests do not reset state between runs; relies on stateless HTTP checks |

### Modern Standards (2026) Evaluation

#### User-Facing Locators
| Status | Notes |
|--------|-------|
| ❌ Poor | Uses CSS tag selectors (`app-playground`, `app-unified-shell`), class wildcards (`[class*="logo"]`), and custom selectors. No `getByRole`, `getByLabel`, or `getByTestId` patterns. |

#### Test Isolation
| Status | Notes |
|--------|-------|
| ⚠️ Partial | Tests are **stateless HTTP checks** (fetching resources), which are inherently isolated. However, the SQLite readiness test (L214–227) **does not** use the `worker-db.fixture` pattern, risking cross-test pollution if extended. |

#### Page Object Model (POM)
| Status | Notes |
|--------|-------|
| ❌ None | Zero usage of existing POMs. All selectors and navigation are inline. |

#### Async Angular Handling
| Status | Notes |
|--------|-------|
| ⚠️ Mixed | `waitForLoadState('networkidle')` (L174) is correct. `waitForFunction()` polling (L218–224) is acceptable. But L39/L75 use anti-pattern `waitForTimeout`. |

---

## 3. Test Value & Classification

### Scenario Relevance

| Aspect | Assessment |
|--------|------------|
| **User Journey** | ❌ Not a user journey—this is **infrastructure/deployment verification** |
| **Critical Path** | ✅ **Absolutely critical** for CI/CD gating—broken paths = unusable deployed app |
| **Real User Scenario** | ❌ Users do not manually verify HTTP headers or path doubling |
| **Regression Detection** | ✅ High value for catching build-time or `base href` configuration regressions |

### Classification

| Type | Justification |
|------|---------------|
| **True E2E (Infrastructure Layer)** | Tests the **real production simulation stack**—not the dev server. Uses the GH Pages config (`playwright.ghpages.config.ts`) with dedicated `webServer` command (`simulate-ghpages.sh`). No mocking. |

**Verdict:** This is a **Deployment Smoke Suite**, not a traditional E2E user journey. High value for its purpose.

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

There is **no user workflow**—this spec validates infrastructure. The implicit "workflow" is:

```
1. CI builds production bundle with `npm run build:gh-pages`
2. `simulate-ghpages.sh` serves the bundle from /praxis/ subdirectory
3. Playwright opens browser and validates:
   a. JupyterLite resources → all load with 200, no doubled paths
   b. SPA routes → /app/home, /playground, /run-protocol accessible
   c. Security headers → COOP/COEP set for SharedArrayBuffer
   d. Visual branding → logo renders
   e. SQLite → service becomes ready in browser mode
```

### Contextual Fit

| Role | Description |
|------|-------------|
| **Deployment Gate** | Runs as part of the GH Pages-specific test suite; blocks broken builds |
| **Regression Guard** | Catches subtle path resolution bugs (e.g., relative vs. absolute `baseUrl` issues) |
| **Integration Proof** | Verifies JupyterLite, SQLite WASM, and Angular SPA coexist under subdirectory deployment |

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Severity | Description |
|-----|----------|-------------|
| **Pyodide kernel bootstrap** | 🔴 Critical | Headers are validated, but no test confirms Pyodide actually **initializes and executes Python code** under GH Pages. |
| **JupyterLite kernel execution** | 🔴 Critical | Resource loading is verified, but there's no test that the REPL becomes functional. |
| **SQLite DB roundtrip** | 🟡 Medium | Only `isReady$` is checked; no write/read verification in deployed mode. |
| **Error recovery** | 🟡 Medium | No negative tests for invalid routes (404 page), broken configs, or header absence. |
| **Cross-browser coverage** | 🟠 Low | Config only runs `ghpages-chromium`; Safari (which lacks SharedArrayBuffer without headers) untested. |

### Domain Specifics

#### Data Integrity
| Status | Notes |
|--------|-------|
| ⚠️ Superficial | Tests verify `praxis.db` **service readiness** but not actual data loading/parsing. No query execution validation. |

#### Simulation vs. Reality
| Status | Notes |
|--------|-------|
| ✅ Good | Uses dedicated simulation server (`simulate-ghpages.sh`) that mirrors real GH Pages (subdirectory, COOP/COEP headers). Ground truth for deployment. |

#### Serialization
| Status | Notes |
|--------|-------|
| ❌ Not tested | No tests verify argument serialization to Pyodide worker. This is out of scope for a deployment smoke test but is a systemic gap. |

#### Error Handling
| Status | Notes |
|--------|-------|
| ❌ Missing | No 404 page tests, no malformed config tests, no header-missing tests. Known bug (`sqlite3-opfs-async-proxy.js`) is excluded rather than tested. |

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 7/10 | Comprehensive for deployment smoke; missing kernel execution proof |
| **Best Practices** | 5/10 | Hardcoded waits, no POM, weak locators |
| **Test Value** | 9/10 | Critical CI gate for GH Pages; high regression protection |
| **Isolation** | 7/10 | Stateless HTTP tests are inherently isolated; SQLite test less so |
| **Domain Coverage** | 5/10 | Focuses on paths/headers, not scientific computation or data integrity |

**Overall**: **6.6/10**

---

## Key Recommendations (Preview for Improvement Plan)

1. **Eliminate `waitForTimeout`** – Replace with `waitForResponse` interceptors or state assertions
2. **Add kernel execution smoke test** – Verify Pyodide/JupyterLite REPL can execute `print("hello")`  
3. **Extract constants** – Timeouts should be configurable, not magic numbers
4. **Add error state tests** – 404 routes, missing headers, malformed configs
5. **Consider Safari project** – GH Pages users include Safari; SharedArrayBuffer behavior differs
