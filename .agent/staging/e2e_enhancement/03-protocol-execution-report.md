# SDET Static Analysis: 03-protocol-execution.spec.ts

**Target File:** [03-protocol-execution.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/03-protocol-execution.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested
This test file verifies the **complete protocol execution lifecycle** in simulation mode:

1. **Protocol Selection** (`select protocol from library`)
   - Navigation to protocol library
   - Enabling simulation mode
   - Selecting a protocol from available cards
   - Continuing to the wizard workflow

2. **Wizard Workflow Completion** (`complete setup wizard steps`)
   - Parameter configuration step
   - Machine selection (with simulation preference)
   - Asset auto-configuration
   - Well selection (if applicable)
   - Deck setup (skip or advance)
   - Review & Run step validation

3. **Execution Lifecycle Monitoring** (`execute protocol and monitor lifecycle`)
   - Execution launch
   - Status transitions (RUNNING → COMPLETED)
   - Progress tracking (≥50% milestone)
   - Log entry verification
   - History table navigation
   - Run detail page validation

4. **Parameter Serialization Verification** (`parameter values reach execution`)
   - Custom parameter input (`volume_ul = 123.45`)
   - End-to-end verification that the parameter appears in run details

**UI Elements Covered:**
| Element | Locator Strategy |
|---------|------------------|
| Sidebar rail | CSS `.sidebar-rail` |
| Protocol cards | Component `app-protocol-card` |
| Wizard step locators | `data-tour-id` attributes |
| Status chip | `data-testid="run-status"` |
| Log panel | `data-testid="log-panel"` |
| Run info card | `mat-card` with text filter |
| History table | Component `app-run-history-table table` |
| Progress bar | Component `mat-progress-bar` |

### Assertions (Success Criteria)

| Test | Key Assertions |
|------|----------------|
| **Protocol Selection** | `[data-tour-id="run-step-params"]` visible after selection |
| **Wizard Complete** | Review tab `aria-selected="true"`, "Ready to Launch" heading visible, protocol name matches |
| **Execution Lifecycle** | Status contains `RUNNING|COMPLETED`, progress ≥50%, logs contain "Executing protocol" and "Execution completed successfully", history row appears, detail view shows run name |
| **Parameter Verification** | Parameter grid shows `volume_ul` = `123.45` |

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

| Issue | Severity | Location | Details |
|-------|----------|----------|---------|
| **`test.describe.serial`** | 🟠 High | Line 7 | Serial execution disables parallelism. While state dependency exists between tests, this pattern should be avoided for CI efficiency. Consider using fixtures for state setup. |
| **CSS class locators** | 🟠 High | Line 16, 38, 45 | `.sidebar-rail`, `.praxis-card`, `h3.card-title` are implementation details. Should use role/testid. |
| **`force: true` click** | 🔴 Critical | `protocol.page.ts:60` | Bypasses clickability checks. Indicates underlying overlay or animation issue that should be fixed. |
| **Missing worker-db fixture** | 🔴 Critical | Line 1 | Uses `@playwright/test` instead of `worker-db.fixture`. No DB isolation. |
| **No TestInfo passed to POMs** | 🔴 Critical | Lines 33, 43, 53, etc. | Page objects support `testInfo` but it's never provided. |
| **Silent error swallowing** | 🟠 High | Lines 11-13, 20-24, 29 | `.catch(() => {})` and empty `console.log` patterns mask genuine failures. |
| **Hardcoded screenshot paths** | 🟡 Medium | Lines 39, 48, 75, 112 | `/tmp/e2e-protocol/` paths may conflict between workers or CI runs. Should use `testInfo.outputPath()`. |
| **Mixed locator strategies** | 🟡 Medium | Throughout | Some use `getByRole()` (good), others use CSS selectors (bad). Inconsistent. |
| **Component instantiation in helpers** | 🟡 Medium | `protocol.page.ts:117-128` | `ProtocolPage` creates `WizardPage` and `ExecutionMonitorPage` internally, creating hidden dependencies. |

### Modern Standards (2026) Evaluation

| Category | Grade | Notes |
|----------|-------|-------|
| **User-Facing Locators** | ⚠️ **Mixed** | `getByRole('button', { name: /Continue/i })`, `getByTestId('run-status')` are good. CSS selectors like `.sidebar-rail`, `.praxis-card` are not. |
| **Test Isolation** | ❌ **Fail** | `test.describe.serial` creates test interdependencies. No worker-db fixture. Cleanup relies on Escape key (brittle). |
| **Page Object Model (POM)** | ✅ **Strong** | Excellent abstraction: `ProtocolPage`, `WizardPage`, `ExecutionMonitorPage`. Methods are well-named and reusable. |
| **Async Angular Handling** | ⚠️ **Partial** | Uses `waitForFunction()` for progress bar, `waitFor()` for elements. However, no explicit SQLite readiness wait since `goto()` is overridden but `testInfo` not passed. |

### Best Practice Violations Summary

```typescript
// ❌ Anti-pattern: Serial execution
test.describe.serial('Protocol Execution E2E', () => {

// ❌ Anti-pattern: Silent catch
}).catch(() => {});

// ❌ Anti-pattern: Force click (from POM)
await firstCard.click({ force: true });

// ❌ Anti-pattern: CSS selector for core verification
await expect(page.locator('.sidebar-rail')).toBeVisible();

// ✅ Good: Role-based locator
await page.getByRole('button', { name: /Continue/i })

// ✅ Good: Test ID locator
await this.page.getByTestId('run-status')
```

---

## 3. Test Value & Classification

### Scenario Relevance

| Dimension | Assessment |
|-----------|------------|
| **Journey Type** | **Critical Happy Path** — This is THE core user journey of the application: selecting a protocol, configuring it, and executing it. |
| **Real User Scenario** | ✅ **Yes** — This exactly mirrors what a lab technician would do: pick a protocol, set parameters, select machines/assets, and run. |
| **Business Value** | **Maximum** — If this flow breaks, the application is non-functional for its primary purpose. |
| **Edge Cases Covered** | ❌ **None** — No failure scenarios (invalid protocol, missing assets, execution errors). |

### Classification

| Metric | Classification |
|--------|----------------|
| **Type** | **True E2E Test** |
| **Mocking Level** | Minimal (simulation mode, but real application stack) |
| **Integration Depth** | Deep (browser → Angular → Pyodide/SQLite → execution engine → history) |

**Verdict:** This is a **high-value, mission-critical E2E test** covering the primary user journey. However, its serial execution pattern and missing isolation infrastructure make it fragile for CI.

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

```
═══════════════════════════════════════════════════════════════
  PROTOCOL EXECUTION USER JOURNEY
═══════════════════════════════════════════════════════════════

┌─────────────────┐
│  1. NAVIGATE    │  User lands on home, app redirects to /app/home
└────────┬────────┘
         │
         ▼ Dismiss welcome dialog if present
         │
┌─────────────────┐
│  2. PROTOCOL    │  Navigate to /app/run
│     LIBRARY     │  Enable simulation mode (toggle button)
│                 │  Select a protocol from card gallery
│                 │  Click "Continue" to enter wizard
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. PARAMETERS  │  [data-tour-id="run-step-params"]
│     STEP        │  Configure protocol parameters (e.g., volume_ul)
│                 │  Click "Continue"
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. MACHINE     │  [data-tour-id="run-step-machine"]
│     SELECTION   │  Select from available machines
│                 │  Prefer "Simulation" or "Chatterbox" in sim mode
│                 │  Handle "Configure Simulation" dialog if appears
│                 │  Click "Continue"
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  5. ASSET       │  [data-tour-id="run-step-assets"]
│     CONFIGURATION │  Auto-configure from inventory
│                 │  Manual fallback if not ready
│                 │  Click "Continue"
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  6. WELL        │  [data-tour-id="run-step-wells"] (if applicable)
│     SELECTION   │  Open well selection dialog per requirement
│                 │  Select wells from plate visualization
│                 │  Click "Continue"
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  7. DECK        │  [data-tour-id="run-step-deck"]
│     SETUP       │  Skip setup or configure deck positions
│                 │  Click "Skip Setup" or "Continue to Review"
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  8. REVIEW      │  Review & Run tab selected
│     & RUN       │  "Ready to Launch" heading visible
│                 │  Protocol name verified
│                 │  Click "Start Execution"
└────────┬────────┘
         │
         ▼ Navigation to /run/live
┌─────────────────┐
│  9. LIVE        │  [data-testid="run-detail-view"]
│     MONITOR     │  Status chip transitions: PENDING → RUNNING → COMPLETED
│                 │  Progress bar tracks execution
│                 │  Log panel shows: "Executing protocol", "Execution completed"
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  10. HISTORY    │  Navigate to /app/monitor
│     & DETAILS   │  Find run in history table by name
│                 │  Click to open detail view
│                 │  Verify parameter values persisted correctly
└─────────────────┘
```

### Contextual Fit

**Role in Application Ecosystem:**

This test covers the **core value proposition** of Praxis:
- **Protocol Library**: Central repository of lab automation scripts (Python/Pyodide)
- **Execution Wizard**: Multi-step configuration UI (Angular Material Steppers)
- **Machine Selection**: Integration with simulated/real hardware
- **Asset Management**: Consumables tracking from SQLite database
- **Execution Engine**: Python/Pyodide worker execution with real-time monitoring
- **Run History**: Persistent audit trail in SQLite

**Dependency Graph:**
```
03-protocol-execution
    └── Depends on: SQLite service ready
    └── Depends on: Protocol library populated (seed data)
    └── Depends on: Simulation machine available
    └── Enables: 04-browser-persistence (run history verification)
```

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Severity | Description |
|-----|----------|-------------|
| **No error scenario testing** | 🔴 Critical | What happens if: protocol Python has syntax error? Machine becomes unavailable mid-execution? Required asset is out of stock? |
| **No cancellation test** | 🔴 Critical | User should be able to cancel an in-progress execution. Not tested. |
| **No partial completion** | 🟠 High | Long-running protocols with step-by-step progress are not tested. Only simple protocols that complete in seconds. |
| **No multi-protocol queue** | 🟡 Medium | Real users often queue multiple protocols. Not tested. |
| **No parameter validation** | 🟠 High | What if `volume_ul` is invalid (negative, text, beyond instrument limits)? Not tested. |
| **No simulation vs. real mode toggle** | 🟠 High | Test only covers simulation mode. Real hardware mode has different behavior. |

### Domain Specifics

| Area | Status | Details |
|------|--------|---------|
| **Data Integrity** | ⚠️ Partial | Protocol selection is verified by name match. Run history shows in table. But SQLite persistence is assumed, not explicitly verified via `evaluate()` or DB inspection. |
| **Simulation vs. Reality** | ✅ Covered | Test explicitly selects simulation mode and handles the "Configure Simulation" dialog. Machine behavior is simulated, not real. |
| **Serialization** | ⚠️ Partial | The `parameter values reach execution` test verifies post-execution parameter display, but doesn't inspect the actual arguments passed to the Pyodide worker. We see the result, not the serialization. |
| **Error Handling** | ❌ Not Tested | No negative tests for: invalid parameters, missing protocols, execution failures, Python exceptions. |

### Pyodide Worker Verification Gap

The most significant domain-specific gap is **Python execution verification**. The test trusts that:
1. The protocol Python script ran correctly
2. Log entries come from actual execution (not mocked)
3. Parameters were correctly serialized and passed to the worker

**What's missing:**
```typescript
// Ideal: Deep verification via browser context
const pyodideOutput = await page.evaluate(async () => {
    const kernel = (window as any).jupyterLiteKernel;
    return kernel.lastExecutionOutput;
});
expect(pyodideOutput).toContain('volume_ul=123.45');
```

### SQLite State Verification Gap

Run history appears in the table, but we don't verify:
```typescript
// Ideal: Direct DB verification
const runData = await page.evaluate(async () => {
    const db = (window as any).sqliteService;
    return await db.query('SELECT * FROM runs WHERE id = ?', [runId]);
});
expect(runData.parameters.volume_ul).toBe(123.45);
```

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 7/10 | Covers the complete happy path of the core journey. Missing error scenarios. |
| **Best Practices** | 4/10 | Serial execution, force clicks, CSS selectors, missing worker-db, no testInfo. |
| **Test Value** | 9/10 | Maximum business value—this is the primary user journey. |
| **Isolation** | 3/10 | Serial tests with shared state, no DB isolation, brittle cleanup. |
| **Domain Coverage** | 5/10 | Covers execution lifecycle but doesn't verify Python/Pyodide internals or SQLite state. |

**Overall**: **5.6/10**

---

## Key Recommendations

### Priority 1: Infrastructure (Blocking Parallel Execution)
1. **Migrate to `worker-db.fixture`** for isolated parallel execution
2. **Pass `testInfo` to all Page Objects** for consistent DB naming
3. **Remove `test.describe.serial`** and refactor tests to be independent
4. **Remove `force: true` clicks** by fixing underlying overlay/animation issues

### Priority 2: Locator Modernization
1. **Replace `.sidebar-rail`** with `getByRole('navigation')` or `getByTestId('sidebar')`
2. **Replace `.praxis-card`** with component-level test IDs
3. **Standardize** `data-testid` on all interactive elements

### Priority 3: Domain Verification
1. **Add Pyodide output inspection** to verify serialized parameters
2. **Add SQLite query verification** for run persistence
3. **Add log content verification** beyond text matching (structured log inspection)

### Priority 4: Error Scenarios
1. **Invalid parameter test**: Negative numbers, text in numeric fields
2. **Execution failure test**: Python script that throws exception
3. **Cancellation test**: Cancel mid-execution and verify state cleanup
4. **Missing asset test**: Protocol requiring unavailable consumable
