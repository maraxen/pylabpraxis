# SDET Static Analysis: jupyterlite-optimization.spec.ts

**Target File:** [jupyterlite-optimization.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/jupyterlite-optimization.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested

This test file validates **optimization and infrastructure prerequisites** for JupyterLite/Pyodide in the Praxis application:

1. **Security Headers Test**: Verifies that the server returns correct Cross-Origin headers (`COOP: same-origin`, `COEP: require-corp`) necessary for `SharedArrayBuffer` and WebAssembly threaded execution.

2. **PyLabRobot Pre-loading Test**: Confirms that the scientific Python package `pylabrobot` is pre-bundled in the Pyodide environment (via lockfile) and does **not** require manual runtime installation from a local wheel.

3. **Service Worker Caching Test**: Validates that after the first load, the critical `pyodide-lock.json` file is served from the Service Worker cache on subsequent page loads.

### Assertions (Success Criteria)

| Test | Key Assertions |
|------|----------------|
| Security Headers | `COOP === 'same-origin'`, `COEP === 'require-corp'` |
| Phase 1: Pre-load | `'PLR_FOUND_{version}'` appears in console logs, `'Installing pylabrobot from local wheel...'` does NOT appear |
| Phase 2: Caching | `response.fromServiceWorker() === true` for `pyodide-lock.json` |

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

| Issue | Severity | Location | Description |
|-------|----------|----------|-------------|
| **Hardcoded `waitForTimeout(5000)`** | 🔴 Critical | Line 67 | Arbitrary 5s wait "to give SW time to register/cache" is flaky. If SW registers faster, time is wasted; if slower, test fails. |
| **No worker-db isolation** | 🟠 High | All tests | Tests use `@playwright/test` directly instead of project-standard `worker-db.fixture`. This breaks parallel execution due to OPFS contention. |
| **CSS class selector `.loading-overlay`** | 🟡 Medium | Line 35 | Uses an internal CSS class. Should use `getByTestId` or wait for a role-based indicator. |
| **Raw CSS selectors for JupyterLite** | 🟡 Medium | Line 44 | `.jp-CodeConsole-input .jp-InputArea-editor` is implementation-coupled. JupyterLite may change internal structure. |
| **Console log polling** | 🟡 Medium | Lines 38-40, 51-53 | Using `expect.poll()` on console logs is creative but unconventional. More reliable would be to use `page.waitForEvent('console')` with a filter. |
| **No onboarding bypass via `addInitScript`** | 🟡 Medium | Lines 27-30 | Setting localStorage *after* `page.goto('/')` then navigating again is a double-navigation anti-pattern. |
| **No `afterEach` cleanup** | 🟡 Medium | N/A | No explicit teardown. While `resetdb=1` on next run helps, Service Worker state may persist across tests. |

### Modern Standards (2026) Evaluation

#### User-Facing Locators
- **Issue**: Uses CSS classes (`.loading-overlay`, `.jp-*`) instead of role-based or test ID locators.
- **Recommendation**: Add `data-testid` attributes or use `getByRole('textbox')` for the JupyterLite code input.

#### Test Isolation  
- **Issue**: Does not use the `worker-db.fixture` available in the repository.
- **Impact**: Cannot run in parallel with other tests touching OPFS-backed SQLite.
- **Recommendation**: Import from `'../fixtures/worker-db.fixture'` and use `gotoWithWorkerDb()`.

#### Page Object Model (POM)
- **Issue**: No POM abstraction. All locators and actions inline in tests.
- **Recommendation**: Create a `PlaygroundPage` POM with methods like `executeCode(code: string)`, `waitForOutput(pattern: RegExp)`.

#### Async Angular Handling
- **Good**: Uses `waitForFunction` for SQLite readiness (implicitly via loading overlay check).
- **Issue**: Uses `networkidle` in Line 72 which is flaky for SPAs with background requests.
- **Recommendation**: Replace with explicit state assertions or `domcontentloaded` + explicit readiness marker.

---

## 3. Test Value & Classification

### Scenario Relevance

| Aspect | Assessment |
|--------|------------|
| **User Criticality** | 🟢 **High** — Cross-Origin headers are mandatory for Pyodide multi-threading. PyLabRobot pre-loading is essential for UX (eliminates 10-30s install delay). |
| **Happy Path vs Edge Case** | This is a **validation/regression test** for optimization infrastructure rather than a user journey. Users don't directly "test" COOP headers; they just expect the app to work fast. |
| **Realism** | 🟡 Partial — Real users import pylabrobot and run code, but they don't specifically verify console logs for "Installing" messages. |

### Classification

| Category | Rating | Justification |
|----------|--------|---------------|
| **True E2E** | 🟡 Partial | The Security Headers test is a pure API test (using `request.get`), not browser-based. The Phase 1 test is True E2E (full browser, Pyodide kernel). Phase 2 is E2E but environment-dependent (requires SW build). |
| **Integration Test** | ✅ Phase 1 | Validates the full stack: Angular app → Pyodide kernel → Python package availability. |
| **Infrastructure Test** | ✅ All | Primarily validates build/deployment configuration (headers, SW, pre-bundling). |

**Overall Classification**: **Infrastructure & Optimization Validation Suite** (not a user journey test).

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

```mermaid
flowchart TD
    subgraph "Test: Security Headers"
        A1[HTTP GET /] --> A2{Check COOP Header}
        A2 --> A3{Check COEP Header}
    end
    
    subgraph "Test: Phase 1 - Pre-load"
        B1[Set localStorage] --> B2[Navigate to /app/playground]
        B2 --> B3[Wait for loading overlay hidden]
        B3 --> B4[Wait for '✓ Ready signal sent']
        B4 --> B5[Find code input in iframe]
        B5 --> B6[Type 'import pylabrobot...' & Shift+Enter]
        B6 --> B7{Poll for 'PLR_FOUND_'}
        B7 --> B8{Assert NO 'Installing pylabrobot' log}
    end
    
    subgraph "Test: Phase 2 - Caching"
        C1[Navigate to /app/playground] --> C2[Wait 5s!]
        C2 --> C3[Reload page, wait for pyodide-lock.json]
        C3 --> C4{Assert response.fromServiceWorker()}
    end
```

### Contextual Fit

This test suite validates **performance optimization features** that are invisible to users but critical for UX:

1. **COOP/COEP**: Without these headers, Pyodide cannot use `SharedArrayBuffer`, degrading performance significantly.
2. **Pre-bundled Packages**: Ensures the build pipeline correctly includes pylabrobot in the Pyodide lockfile, avoiding runtime install delays.
3. **Service Worker**: Validates the caching layer that enables near-instant subsequent loads.

**Ecosystem Role**: This is a **regression gate** for the build/deployment pipeline, not a user simulation.

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Severity | Description |
|-----|----------|-------------|
| **No version validation** | 🟡 Medium | Test checks that `PLR_FOUND_{version}` appears but doesn't assert the expected version matches requirements. |
| **No SW registration failure handling** | 🟠 High | Phase 2 assumes SW is registered. If SW fails to register (e.g., dev mode, HTTPS issues), test fails without diagnostic info. |
| **No offline/cache-miss scenario** | 🟡 Medium | Only tests cache HIT. Doesn't validate behavior when SW cache is empty or corrupted. |
| **No multi-package validation** | 🟡 Medium | Only tests `pylabrobot`. Other pre-loaded packages (e.g., `numpy`, `scipy`) aren't validated. |
| **No kernel error handling** | 🟠 High | Doesn't test what happens if Pyodide kernel fails to initialize (e.g., out of memory, WASM load failure). |

### Domain Specifics

#### Data Integrity
- **Status**: ❌ Not validated
- **Gap**: Test doesn't verify that the pre-loaded pylabrobot package is functional beyond a simple `import`. No test of actual labware operations.

#### Simulation vs. Reality
- **Status**: ⚠️ Partially addressed
- **Current**: Uses `mode=browser` which runs in simulated (client-only) mode.
- **Gap**: Doesn't contrast behavior when connected to a real machine backend. Headers would still apply, but SW caching behavior may differ.

#### Serialization
- **Status**: ❌ Not tested
- **Gap**: No validation that arguments passed to pylabrobot functions are correctly serialized across the Pyodide/JS boundary. This is tested implicitly by the import succeeding, but no function calls are made.

#### Error Handling
- **Status**: ❌ Not tested
- **Missing scenarios**:
  - Invalid COOP/COEP headers (what error does the app show?)
  - pylabrobot import failure (corrupted wheel, missing dependency)
  - SW registration failure
  - `SharedArrayBuffer` unavailable (Safari, insecure contexts)

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 6/10 | Covers important infrastructure, but narrow (3 specific validations) |
| **Best Practices** | 4/10 | `waitForTimeout`, no worker-db isolation, CSS selectors, no POM |
| **Test Value** | 7/10 | High-value regression gate, but not a user journey |
| **Isolation** | 3/10 | No worker-db fixture, no SW cleanup, console log state shared |
| **Domain Coverage** | 4/10 | Surface-level validation only; no deep functional testing of pylabrobot or error states |

**Overall**: **4.8/10**

---

## Key Recommendations

1. **Replace `waitForTimeout(5000)` with SW registration detection**: Use `page.evaluate(() => navigator.serviceWorker.ready)`.
2. **Adopt `worker-db.fixture`**: Import from fixtures and use `gotoWithWorkerDb()` for parallel safety.
3. **Create `PlaygroundPage` POM**: Abstract JupyterLite iframe interactions into reusable methods.
4. **Add diagnostic assertions**: If SW is not active, log why (dev mode? HTTPS? Registration blocked?).
5. **Expand pylabrobot validation**: Test an actual function call (e.g., `LiquidHandler(backend=SimulatorBackend())`).
6. **Add negative tests**: What happens when headers are wrong? When package is missing?
