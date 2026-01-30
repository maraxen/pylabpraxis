# E2E Static Analysis Report: `interactions/04-error-handling.spec.ts`

**Audit Date:** 2026-01-30  
**Auditor:** Senior SDET / Angular Specialist  
**Classification:** Interaction Test Suite – Error Handling & System Resilience  

---

## 1. Test Scope & Coverage

### What is Tested

This test file contains **3 test cases** focused on error handling and system resilience scenarios:

| Test Case | Description |
|-----------|-------------|
| `should display error logs when a protocol execution fails` | Starts a protocol execution, navigates to the live dashboard, and verifies that an "Execution Log" panel is visible. |
| `should remain live when navigating away and back during execution` | Performs a round-trip navigation (Monitor → Settings → Monitor) during a running execution and verifies status persistence. |
| `should show user-friendly error on backend failure` | Mocks a 500 HTTP error on the `/api/v1/protocols*` route and verifies that a Material SnackBar appears with an error message. |

### UI Elements & State Changes Verified

- **Navigation:** `/app/run`, `/settings`, `/app/monitor`
- **Material Components:** `mat-card` (Execution Log panel), `mat-snack-bar-container`
- **Execution States:** `RUNNING`, `COMPLETED` via `run-status` test ID
- **Wizard Flow:** Full protocol selection → parameters → machine → assets → deck → review → execution

### Key Assertions

| Test | Assertion(s) |
|------|-------------|
| Test 1 | `logPanel.toBeVisible()` – Log panel with text "Execution Log" is visible after execution starts |
| Test 2 | `page.toHaveURL(/\/settings/)` – Navigation to settings succeeded; `waitForStatus(/RUNNING\|COMPLETED/)` – Run is still active after returning |
| Test 3 | `snackBar.toBeVisible({ timeout: 10000 })` – SnackBar appears; `snackBar.toContainText(/error\|failed/i)` – Contains error message |

---

## 2. Code Review & Best Practices (Static Analysis)

### 2.1 Critique: Brittle Logic & Potential Issues

| Issue | Location | Severity | Description |
|-------|----------|----------|-------------|
| **Misleading Test Name** | Test 1 title | 🟡 Medium | Test is named "should display error logs when a **protocol execution fails**" but does NOT actually trigger or verify a failure. It only confirms the log panel is visible during a normal execution. |
| **No Actual Error Verification** | Test 1 | 🔴 High | The test doesn't verify actual error content, log entries indicating errors, or failure state transitions. It's a misnomer. |
| **Hardcoded Regex for Status** | Lines 63, 74 | 🟡 Medium | `waitForStatus(/RUNNING/)` and `/RUNNING|COMPLETED/` may miss intermediate states (e.g., `PAUSED`, `FAILED`). |
| **CSS-Based Selector for Log Panel** | Line 40 | 🟡 Medium | `page.locator('mat-card').filter({ hasText: 'Execution Log' })` – Not using `getByTestId` or ARIA role. Brittle if card title changes. |
| **CSS-Based Selector for SnackBar** | Line 90 | 🟡 Medium | `page.locator('mat-snack-bar-container')` – Should prefer `getByRole('alert')` or a test ID for Material SnackBar components. |
| **Implicit API Dependency** | Test 3 | 🟢 Low | Relies on specific route pattern `**/api/v1/protocols*` which may not be the actual endpoint in browser mode. |
| **No Verification of Route Intercept** | Test 3 | 🟡 Medium | Test doesn't confirm that the mocked route was actually triggered (no `await page.waitForResponse()`). |

### 2.2 Modern Standards Evaluation (2026)

| Standard | Current State | Recommendation |
|----------|---------------|----------------|
| **User-Facing Locators** | ⚠️ Mixed | Test 1 uses `mat-card.filter({ hasText: ... })` – not user-facing. Test 3 uses component selector for snackbar. Should use `getByRole('alert')` or `getByTestId`. |
| **Test Isolation** | ✅ Good | Each test uses `beforeEach` to handle splash screen. However, no explicit state cleanup between tests. |
| **POM Usage** | ✅ Excellent | Properly leverages `WelcomePage`, `ProtocolPage`, `WizardPage`, `ExecutionMonitorPage`, `SettingsPage` POMs. |
| **Worker-Indexed DB Isolation** | ⚠️ Partial | `BasePage` supports worker-indexed DBs, but `WizardPage` and some POMs don't extend `BasePage` or use `testInfo`. |
| **Async/Angular State Handling** | ✅ Good | Uses POM methods like `waitForLiveDashboard()`, `waitForStatus()` which internally wait for Angular signals. |
| **Animation Handling** | ⚠️ Not Addressed | No explicit handling for Material animation settling (snackbar fade-in, stepper transitions). |

### 2.3 Fixture Usage

| Aspect | Assessment |
|--------|------------|
| **Custom Fixtures** | ❌ Not Used | Tests don't use custom fixtures; POMs are instantiated inline. |
| **Test Data Fixtures** | ❌ Not Used | No fixture for pre-seeding database with known protocols or machines. |
| **Page Object Fixtures** | ❌ Not Used | Could benefit from a fixture that provides pre-initialized POMs. |

---

## 3. Test Value & Classification

### 3.1 Scenario Relevance

| Test | Relevance | Real User Scenario? |
|------|-----------|---------------------|
| Test 1 | 🟡 Low (Mislabeled) | **No.** A real user cares if error logs appear **when errors occur**, not just that a log panel exists. This is a visibility smoke test, not an error handling test. |
| Test 2 | ✅ High | **Yes.** Users frequently navigate away (e.g., to check settings, view other data) during long-running executions. Verifying stateful navigation is critical. |
| Test 3 | ✅ Critical | **Yes.** Backend failures must surface user-visible feedback. However, current implementation tests only HTTP 500 on protocol listing—not during execution or serialization. |

### 3.2 Classification

| Test | Classification | Justification |
|------|----------------|---------------|
| Test 1 | **Interactive Visual Check** | Does not test error handling at all. Merely checks log panel visibility during happy path. |
| Test 2 | **True E2E (Navigation + State)** | Tests real navigation and verifies that the execution state persists across route changes. Uses actual application flow. |
| Test 3 | **Hybrid (API Mock + UI Verification)** | Uses `page.route()` to mock a backend error, then verifies UI response. This is partial E2E—backend is stubbed. |

### 3.3 Overall Test Value Score

| Dimension | Score (0-10) | Notes |
|-----------|--------------|-------|
| **Test Scope** | 4 | Covers 3 scenarios but Test 1 is mislabeled and doesn't test what it claims. |
| **Best Practices** | 6 | Good POM usage, but selector strategy and animation handling need improvement. |
| **Test Value** | 5 | Test 2 and Test 3 are valuable; Test 1 is misleading. |
| **Isolation** | 7 | Good beforeEach setup, but no explicit state cleanup or fixture isolation. |
| **Domain Coverage** | 3 | Minimal error handling coverage. Doesn't test actual failure states, serialization errors, or Pyodide errors. |

**Aggregate Score: 5.0 / 10** – Functional Smoke (Unreliable/Shallow)

---

## 4. User Flow & Intent Reconstruction

### 4.1 Reverse Engineered Workflow

#### Test 1: "Display Error Logs on Failure" (Mislabeled)
```
1. User lands on Welcome page → Splash screen is dismissed
2. User navigates to /app/run (Protocol Selection)
3. User ensures Simulation Mode is active
4. User selects the first available protocol
5. User clicks Continue to advance to the wizard
6. User completes Parameter step (defaults accepted)
7. User selects first compatible machine (simulation machine)
8. User waits for assets to auto-configure
9. User advances through Deck Setup (Skip or Continue)
10. User opens Review step and clicks "Start Execution"
11. User waits for Live Dashboard to appear
12. VERIFY: Log panel with "Execution Log" heading is visible
```

#### Test 2: Navigation Persistence During Execution
```
1-11. (Same as Test 1 through waiting for Live Dashboard)
12. User waits for status to show RUNNING
13. User navigates to /settings
14. VERIFY: URL contains /settings
15. User navigates back to /app/monitor
16. User waits for Live Dashboard again
17. VERIFY: Status still shows RUNNING or COMPLETED
```

#### Test 3: Backend 500 Error Handling
```
1. User lands on Welcome page → Splash screen is dismissed
2. [MOCK] API route for /api/v1/protocols* returns HTTP 500
3. User navigates to /app/run (Protocol Selection)
4. VERIFY: SnackBar appears with error/failed message
```

### 4.2 Contextual Fit

| Test | Place in Ecosystem |
|------|-------------------|
| Test 1 | Should be part of **Monitor/Execution Dashboard** tests, not error handling. Belongs in "execution visibility" or "log panel rendering" suite. |
| Test 2 | Excellent fit for **System Resilience** or **Navigation Stability** category. Critical for SPA behavior validation. |
| Test 3 | Core **Error Handling** test, but limited to protocol listing endpoint. Should be expanded to cover execution errors, serialization errors, etc. |

---

## 5. Gap Analysis (Scientific & State Logic)

### 5.1 Missing Critical Paths

| Gap | Severity | Description |
|-----|----------|-------------|
| **No Actual Protocol Failure Test** | 🔴 Critical | Test 1 claims to test failure scenarios but doesn't trigger any failure. Need a test that causes Python/protocol execution to fail (e.g., syntax error, missing resource). |
| **No Pyodide/Worker Error Handling** | 🔴 Critical | When Pyodide fails to initialize, throws a Python exception, or the web worker crashes—what does the user see? Not tested. |
| **No Serialization Error Test** | 🔴 Critical | When protocol arguments fail to serialize for the Pyodide worker, is there feedback? Not tested. |
| **No DB Load/Parse Error Test** | 🟡 High | What happens if `praxis.db` is corrupted, empty, or in an incompatible schema version? Not tested. |
| **No Network Timeout Test** | 🟡 High | What if API calls hang indefinitely? Only HTTP 500 is tested. |
| **No WebSocket/SSE Disconnect Test** | 🟡 High | If the execution monitor loses its live connection, is there a reconnection attempt or error message? Not tested. |

### 5.2 Domain-Specific Gaps

#### Data Integrity

| Question | Answer |
|----------|--------|
| Are we validating `praxis.db` is loaded/parsed correctly? | ❌ No—Test 3 mocks the API, bypassing actual DB loading. |
| Is SQLite initialization failure tested? | ❌ No tests for OPFS failures or SQL-wasm loading errors. |

#### Simulation vs. Reality

| Question | Answer |
|----------|--------|
| Are we using simulation mode correctly? | ✅ Yes—`ensureSimulationMode()` is called in Tests 1 and 2. |
| Is simulation environment fully instantiated? | ⚠️ Implicit—We don't verify that the simulation machine is properly configured. |

#### Serialization to Pyodide

| Question | Answer |
|----------|--------|
| Are protocol arguments serialized correctly? | ❌ Not verified—We only check that execution starts, not that parameters were passed correctly. |
| Is there error handling for serialization failures? | ❌ No test coverage for malformed arguments or type mismatches. |

#### Error Handling Coverage

| Error Type | Tested? |
|------------|---------|
| HTTP 500 on Protocol List | ✅ Yes |
| HTTP 500 on Execution Start | ❌ No |
| HTTP 500 during Execution (status check) | ❌ No |
| Pyodide initialization failure | ❌ No |
| Python syntax error during execution | ❌ No |
| Protocol completion with FAILED status | ❌ No |
| Invalid machine configuration | ❌ No |
| Asset not found / incompatible | ❌ No |
| OPFS write failure | ❌ No |

### 5.3 State Machine Verification Gaps

The test doesn't verify the complete error state machine:

```
IDLE → RUNNING → ERROR (not tested)
IDLE → RUNNING → COMPLETED (happy path only)
IDLE → ERROR (initialization failure—not tested)
```

---

## Summary Findings

### Strengths
1. **Good POM Architecture:** Test leverages well-structured Page Objects for navigation and interaction.
2. **Simulation Mode Awareness:** Tests correctly enable simulation mode for predictable execution.
3. **Navigation Resilience Test:** Test 2 is a valuable SPA resilience check.
4. **API Mock Pattern:** Test 3 demonstrates the correct pattern for mocking HTTP errors.

### Critical Weaknesses
1. **Misleading Test Name:** Test 1 doesn't test error handling at all—rename or rewrite.
2. **No Actual Failure Testing:** No test triggers or verifies a real protocol failure state.
3. **Shallow Error Coverage:** Only HTTP 500 on one endpoint; no Pyodide, serialization, or execution errors.
4. **No Deep State Verification:** Tests check UI visibility but not actual error payloads, log contents, or recovery actions.

---

*Report generated following Senior SDET Audit Process v2.0*
