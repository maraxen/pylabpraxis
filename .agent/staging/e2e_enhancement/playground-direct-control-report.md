# SDET Static Analysis: playground-direct-control.spec.ts

**Target File:** [playground-direct-control.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/playground-direct-control.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested
- **Playground Initialization**: Verifies `/app/playground` loads with `mode=browser`.
- **SQLite Readiness**: Waits for `SqliteService` to report as ready.
- **Inventory Integration**: Tests opening the inventory dialog from the playground header.
- **Asset Creation**: Uses `AssetsPage` to create a "Hamilton STAR" liquid handler.
- **Direct Control**: Verifies switching to the "Direct Control" tab and visibility of the control component.
- **Method Execution**: If methods are found (Setup, etc.), it attempts execution and verifies a success feedback icon.

### Assertions (Success Criteria)
- `expect(inventoryBtn).toBeVisible()`
- `expect(directControl).toBeVisible()`
- `expect(executeBtn).toBeVisible()` and `toBeEnabled()`
- `expect(successIcon).toBeVisible()` (Success state verification)
- `expect(noMethodsMessage).toBeVisible()` (Graceful fallback if no methods)

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code
- **Brittle Locators**: Uses CSS classes like `.method-chip`, `.execute-btn`, and `.command-result`. These are implementation details that break on styling refactors.
- **Race Condition Handling**: Uses `Promise.race` with two `waitFor` calls. While clever, this pattern is often a sign of unpredictable component state.
- **Silent Failures**: The Welcome Dialog handler uses a generic `try/catch` which swallows errors, potentially hiding UI blocking issues.
- **Manual Logging**: Scattered `console.log` statements within the test code; should ideally use `testInfo.annotations` or rely on Playwright traces.
- **Mocking Strategy**: Mocks `api/v1/machines/definitions` but does so inside the test instead of a global fixture, leading to boilerplate.

### Modern Standards (2026) Evaluation
- **User-Facing Locators**: 🟡 Partial. Uses `getByRole('tab')` but leans heavily on CSS selectors for action buttons.
- **Test Isolation**: 🔴 Poor. Does not remove created machines. Uses `resetdb=1` which is destructive to the global browser state for other tests.
- **Page Object Model (POM)**: 🟡 Partial. Uses `AssetsPage` for creation but writes raw Playwright logic for Playground-specific controls instead of having a `PlaygroundPage` POM.
- **Async Angular Handling**: 🟡 Partial. Manually polls `sqliteService.isReady$`, which is a low-level leak of implementation details into the test.

---

## 3. Test Value & Classification

### Scenario Relevance
- **Critical Path**: This is a High-Value "Happy Path" test. The "Direct Control" of a freshly created machine is a core selling point of the Praxis platform.

### Classification
- **Interactive Component Integration**: It's more than a unit test but less than a full E2E. Since it mocks the machine definitions and runs in `mode=browser`, it's testing the *integration* of Angular components and the Browser-side SQLite state.

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow
1. User enters Playground.
2. User notices the inventory is empty or wants to add a robot.
3. User opens the Inventory manager.
4. User "crafts" a Hamilton STAR liquid handler.
5. User navigates back to Direct Control to see the new robot.
6. User runs the "Setup" sequence to initialize the simulated hardware.

### Contextual Fit
- This test bridges the gap between **Asset Management** (creation) and **Execution** (usage). It ensures the "Discovery" mechanism in the playground works correctly for new devices.

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths
- **Deep State Verification**: Doesn't check if the machine's backend (Hamilton STAR) was actually instantiated in Pyodide.
- **Serialization**: The test doesn't verify the structure of the command sent to the backend.
- **DB Conflict**: Since it uses a hardcoded DB, multiple workers will fail due to SQLite locking issues.

### Domain Specifics
- **Data Integrity**: Does not verify the SQLite schema or record contents after creation.
- **Simulation vs. Reality**: The test doesn't differentiate between a successful UI transition and a successful "Hardware Response" from the simulator.
- **Error Handling**: Missing negative tests (e.g., what if the backend name is invalid? what if the REPL fails to load?).

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 🟢 8/10 | Covers a complete initialization → usage cycle. |
| **Best Practices** | 🔴 4/10 | Heavy use of CSS classes and manual implementation detail polling. |
| **Test Value** | 🟢 8/10 | Tests critical integration between Assets and Playground. |
| **Isolation** | 🔴 3/10 | Destroying/modifying global browser DB state; lacks worker isolation. |
| **Domain Coverage** | 🟡 5/10 | Checks result icon but not internal Pyodide state. |

**Overall**: **5.6/10**
