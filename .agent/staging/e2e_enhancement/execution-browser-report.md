# SDET Static Analysis: execution-browser.spec.ts

**Target File:** [execution-browser.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/execution-browser.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested
This test file validates the **Browser Mode Protocol Execution** workflow — specifically the multi-step wizard for selecting and running a protocol without a physical machine backend. The tests cover:

1. **Navigation**: Going from home (`/app/home`) to the Run Protocol page (`/app/run`).
2. **Protocol Selection**: Clicking on an `app-protocol-card` component.
3. **Wizard Progression**: Clicking "Continue" buttons through multiple stepper steps.
4. **Machine Selection**: Interacting with `app-machine-selection` to select a simulation machine.
5. **Execution Initiation**: Clicking "Start Execution" and observing loading indicators (`mat-spinner` or "Initializing" text).
6. **Simulation Machine Visibility**: Verifying that "Simulation Machine" or "sim-machine" text appears as an option.

### Assertions (Success Criteria)
| Test | Key Assertions |
|------|----------------|
| `should start protocol execution in browser mode` | Protocol cards load; "Start Execution" button becomes visible; loading indicators appear OR button is disabled (deck setup required). |
| `should show simulation machine in browser mode` | "Simulation Machine" or "sim-machine" text is visible in the machine selection step. |

**Assertion Strength: Weak (2/10)**
- Many assertions are wrapped in `.catch(() => {})`, effectively swallowing failures and making the tests pass regardless of actual behavior.
- No assertions on data integrity, application state, or backend calls.

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

#### Critical Issues

| Line(s) | Issue | Severity |
|---------|-------|----------|
| 18-19 | **Swallowed Navigation Error**: `waitForURL` inside `.catch(() => console.log(...))` means a failed redirect is logged but not failed. | 🔴 High |
| 75-77, 81-84, 88-91, 96-100, 104-129, 139-155 | **Conditional Test Logic**: Almost every action is wrapped in `if (await ...isVisible().catch(() => false))`. This creates "quantum" tests that do nothing if the element doesn't appear. | 🔴 High |
| 83, 91, 98, 112 | **Hardcoded `waitForTimeout`**: Magic numbers (300ms, 500ms) without condition-based waiting. Causes flakiness and false positives. | 🔴 High |
| 58 | **Brittle CSS Selector**: `[class*="protocol"]` is extremely vague and could match anything (e.g., `protocol-error`, `protocol-skeleton`). | 🟠 Medium |
| 74, 87, 138 | **Angular Component Selectors as Locators**: `app-protocol-card`, `app-machine-selection` are implementation details, not user-facing locators. | 🟠 Medium |
| 115-118 | **Swallowed Assertion**: The `expect().toBeVisible().catch(() => {})` block means this assertion can never fail the test. | 🔴 High |
| 150-155 | **Swallowed Assertion**: Same pattern — the simulation machine check cannot fail the test. | 🔴 High |

#### Additional Issues

- **No Worker Isolation**: Uses raw `page.goto('/')` instead of the `worker-db.fixture` pattern. This will cause OPFS contention in parallel runs.
- **No Cleanup of Created Resources**: If `Start Execution` creates persistent state (a run record), there's no cleanup.
- **Duplicate Screenshot** (Lines 60 and 71): Path `01_protocol_load.png` is written twice.
- **Console-Only Debugging** (Line 66): Printing `text?.substring(0, 500)` is a poor substitute for structured debugging.

### Modern Standards (2026) Evaluation

| Criterion | Status | Notes |
|-----------|--------|-------|
| **User-Facing Locators** | ❌ Fail | Uses CSS class wildcards (`[class*="protocol"]`), Angular component selectors (`app-protocol-card`), and raw `button:has-text()` instead of `getByRole` or `getByLabel`. |
| **Test Isolation** | ❌ Fail | No worker-indexed database. Tests will conflict in parallel. `afterEach` only presses Escape, no DB/state cleanup. |
| **Page Object Model (POM)** | ❌ Fail | Zero POMs used. All logic is inline. `RunProtocolPage`, `MachineSelectionComponent` helpers don't exist. |
| **Async Angular Handling** | ⚠️ Partial | Uses `waitForFunction` for SQLite readiness (good), but then relies on `waitForTimeout` instead of waiting for Angular signals or state changes. |

---

## 3. Test Value & Classification

### Scenario Relevance
- **Critical User Journey**: Yes — Running a protocol is a core workflow.
- **Realistic User Scenario**: Partially — A real user would not proceed through a wizard if steps are optional. The test's conditional logic (`if visible`) doesn't represent deterministic user behavior.

### Classification
**Interactive Unit Test (Masquerading as E2E)**

| Reason | |
|--------|-----|
| Does it test the full stack? | No — No verification of Pyodide execution, serialization, or state persistence. |
| Does it assert on outcomes? | No — Only checks if UI elements appear (when they happen to). |
| Are backend responses verified? | No — No network mocking or response validation. |
| Is it deterministic? | No — Conditional logic means workflow varies per run. |

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow
Based on the code, the intended user journey is:

1. **App Loads**: User navigates to `/`, redirected to `/app/home`.
2. **Database Initializes**: SQLite OPFS database becomes ready (`sqliteService.isReady$`).
3. **Welcome Dialog Dismissed**: If present, user clicks "Skip for Now".
4. **Navigate to Run**: User goes to `/app/run`.
5. **Select Protocol**: User clicks on the first available protocol card.
6. **Advance Through Wizard**: User clicks "Continue" multiple times.
7. **Select Machine**: (Optional) User clicks on a machine card if visible.
8. **Start Execution**: User clicks "Start Execution" button.
9. **Execution Feedback**: System shows `mat-spinner` or "Initializing" text.

### Contextual Fit
The `RunProtocolComponent` is a **1500+ line wizard** with:
- Protocol selection
- Asset selection (labware, plates, etc.)
- Machine compatibility loading
- Deck setup (physical slot assignment)
- Execution initiation (spawns Pyodide worker)

This test scratches the surface of **Step 1 (Protocol Selection)** and **Step 5 (Machine Selection)** but does not meaningfully test the others.

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Impact |
|-----|--------|
| **Asset Selection Step** | The wizard has an asset selection step (`onAssetSelectionChange`). The test skips this entirely. |
| **Deck Setup Validation** | The "Start Execution" button is disabled unless deck setup is complete. Test observes this but does not test deck setup. |
| **Execution Outcome** | No verification that execution actually started, produced output, or reached a terminal state. |
| **Stepper State** | No assertion on `mat-stepper` step index or completion status. |

### Domain Specifics

#### Data Integrity
- ❌ **No OPFS Verification**: The test waits for `sqliteService.isReady$` but doesn't verify that protocols were actually loaded from the database.
- ❌ **No Protocol Validation**: Clicking `app-protocol-card.first()` doesn't verify the protocol's name, ID, or category.

#### Simulation vs. Reality
- ⚠️ **Ambiguous Machine Mode**: The second test checks for "Simulation Machine" text but doesn't assert that `isPhysicalMode` is false or that the backend type is correctly inferred.
- ❌ **No Backend Interaction**: Real execution would call `/api/machine/...` or spawn a WebSocket. None of this is verified.

#### Serialization
- ❌ **No Pyodide Verification**: The execution flow serializes protocol arguments and sends them to a Pyodide worker. This test makes no attempt to intercept or verify that payload.
- ❌ **No GRPC/REST Mocking**: Execution commands should be validated even in browser mode (simulation).

#### Error Handling
- ❌ **No Negative Tests**: What happens if the protocol list is empty? If the machine list is empty? If execution fails?
- ❌ **No Network Error Simulation**: What if SQLite fails to load?

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 3/10 | Covers navigation and UI presence, not workflows or state. |
| **Best Practices** | 2/10 | Hardcoded waits, swallowed errors, no POMs, no isolation. |
| **Test Value** | 3/10 | Tests a critical path but with non-deterministic conditional logic. |
| **Isolation** | 1/10 | No worker-indexed DB, no cleanup, will conflict in parallel. |
| **Domain Coverage** | 2/10 | No data integrity, serialization, or execution validation. |

**Overall**: **2.2/10**

---

## Recommendations Summary

1. **Migrate to `worker-db.fixture`** for parallel-safe execution.
2. **Remove all `catch(() => {})` patterns** — tests must fail when assertions fail.
3. **Replace conditional logic with deterministic assertions** — if a protocol card should appear, assert it; don't silently skip.
4. **Create `RunProtocolPage` POM** with methods like `selectProtocol()`, `advanceToStep()`, `startExecution()`.
5. **Wait for Angular state, not timeouts** — use `waitForFunction` on signals or NgRx store selectors.
6. **Add domain verification**:
   - Assert protocol name/ID after selection.
   - Assert deck completion state before execution.
   - Mock and intercept Pyodide execution calls.
7. **Add negative test coverage** for empty states and error conditions.
