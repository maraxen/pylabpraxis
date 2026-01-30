# SDET Static Analysis: interactions/01-execution-controls.spec.ts

**Target File:** [interactions/01-execution-controls.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/interactions/01-execution-controls.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested
This test file validates the **execution control buttons** during a simulated protocol run:
- **Pause/Resume flow**: Clicking "Pause" transitions status to `PAUSED`, then clicking "Resume" transitions back to `RUNNING` or `COMPLETED`
- **Abort flow**: Clicking "Stop/Abort/Cancel" (with optional confirmation dialog) transitions status to `CANCELLED` or `FAILED`

**UI Elements Verified:**
- Protocol selection wizard (parameter step, machine step, assets step, deck step, review step)
- Start Execution button
- Pause button (visibility and clickability)
- Resume button (visibility and clickability)
- Abort/Stop/Cancel button (visibility and clickability)
- Confirmation dialog buttons (if present)
- Status chip displaying execution state

**State Changes Verified:**
- Execution transitions: `RUNNING` → `PAUSED` → `RUNNING`/`COMPLETED`
- Execution abort transitions: `RUNNING` → `CANCELLED`/`FAILED`

### Assertions (Success Criteria)
| Assertion | Location |
|-----------|----------|
| Pause button is visible within 15s | Line 39 |
| Status contains `PAUSED` after clicking Pause | Line 43 |
| Resume button is visible within 15s | Line 47 |
| Status contains `RUNNING` or `COMPLETED` after Resume | Line 51 |
| Abort button is visible within 15s | Line 76 |
| Status contains `CANCELLED` or `FAILED` after Abort | Line 86 |

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

**Strengths ✅:**
1. **User-facing locators**: Uses `getByRole('button', { name: /pause/i })` extensively — excellent accessibility-first approach
2. **POM utilization**: Leverages `WelcomePage`, `ProtocolPage`, `WizardPage`, and `ExecutionMonitorPage` for wizard navigation
3. **Flexible regex matching**: Abort button uses `.filter({ hasText: /Stop|Abort|Cancel/i })` to handle UI variations
4. **Dialog handling**: Gracefully handles optional confirmation dialogs with try-catch pattern (`isVisible({ timeout: 2000 })`)
5. **Status flexibility**: `waitForStatus()` in monitor POM handles `COMPLETED` as acceptable terminal state

**Weaknesses ⚠️:**
1. **`.first()` proliferation**: Heavy use of `.first()` (lines 38, 46, 75, 80) suggests locator ambiguity — potential strict mode violations
2. **Hardcoded 15s timeouts**: Custom timeouts scattered in test code (lines 39, 47, 76) rather than centralized configuration
3. **No worker isolation**: Uses `WelcomePage.goto()` which doesn't pass `testInfo` for worker-indexed DB isolation — will fail in parallel execution
4. **Force click leak**: `ProtocolPage.selectFirstProtocol()` uses `force: true` (line 60 in protocol.page.ts)
5. **Missing assertion between wizard steps**: No intermediate assertions verifying wizard state transitions

### Modern Standards (2026) Evaluation

| Criterion | Score | Notes |
|-----------|-------|-------|
| **User-Facing Locators** | 9/10 | Excellent `getByRole` usage; minor deduction for `.first()` fallbacks |
| **Test Isolation** | 4/10 | No `afterEach` cleanup, no worker-indexed DB, shared state risk |
| **Page Object Model** | 8/10 | Good abstraction, but wizard orchestration duplicated (lines 22-33 and 59-70 are identical) |
| **Async Angular Handling** | 7/10 | `waitForLiveDashboard()` uses `waitFor()`, but no explicit Angular zone stabilization |

**Specific Issues:**

1. **Missing `testInfo` injection**:
   ```typescript
   // Current (line 12-14):
   const welcomePage = new WelcomePage(page);
   await welcomePage.goto();
   
   // Should be:
   const welcomePage = new WelcomePage(page, testInfo);
   await welcomePage.goto(); // Will use worker-indexed DB
   ```

2. **Duplicate setup code**: Both tests perform identical wizard setup (lines 22-35, 59-72). Should extract to a fixture or shared setup.

3. **Status RegExp fragility**:
   ```typescript
   // Line 51 - Will fail if status is "RUNNING (Step 3/5)"
   await monitorPage.waitForStatus(/RUNNING|COMPLETED/);
   // Safer: /RUNNING|COMPLETED|SUCCEEDED/
   ```

---

## 3. Test Value & Classification

### Scenario Relevance
| Aspect | Assessment |
|--------|------------|
| **User Journey** | ✅ **Critical Happy Path** — Pause/Resume/Abort are core execution controls for lab automation |
| **Real User Scenario** | ✅ Yes — Users routinely pause runs for reagent replacement, abort failed runs |
| **Business Impact** | HIGH — Failed abort control could leave instruments in undefined state |
| **Edge Case Coverage** | MINIMAL — Only tests success paths, no failure modes |

### Classification
**True E2E Test** ✅
- Full stack integration: navigates through all wizard steps
- Real Angular services: `ProtocolService`, `ExecutionService`, `MonitorService`
- Uses simulation mode (not mock) — Pyodide worker actually processes execution
- No network mocks or service stubs visible

**Confidence Level**: 85% True E2E
- Minor uncertainty: Does `ensureSimulationMode()` configure a full simulated backend or just UI toggle?

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

**Test 1: Pause and Resume**
```
1. User opens application → splash screen handled
2. User navigates to /app/run (protocol selection)
3. User enables simulation mode toggle
4. User clicks first available protocol card
5. User clicks "Continue" to parameters step
6. User clicks "Continue" (default parameters accepted)
7. User selects first compatible machine (simulation/chatterbox preferred)
8. User auto-configures assets (or manually selects)
9. User skips/continues deck setup
10. User opens Review & Run tab
11. User clicks "Start Execution"
12. Dashboard loads with live execution view
13. User clicks "Pause" button
14. UI shows PAUSED status
15. User clicks "Resume" button
16. UI shows RUNNING or COMPLETED status
```

**Test 2: Abort**
```
Steps 1-12: Same as above
13. User clicks "Stop/Abort/Cancel" button
14. (Optional) User confirms abort in dialog
15. UI shows CANCELLED or FAILED status
```

### Contextual Fit
This test validates the **Execution Monitor** component's control surface, which integrates with:
- **Pyodide Worker**: Execution state machine (`IDLE` → `RUNNING` → `PAUSED` → `RUNNING` → `COMPLETED`)
- **Angular Signals**: Status updates propagate through `ExecutionStateService`
- **Material UI**: mat-chip displays status, mat-button triggers state transitions
- **WebSocket/Polling**: Real execution would involve backend communication (simulation mode likely mocks this layer)

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Severity | Description |
|-----|----------|-------------|
| **Double-pause protection** | Medium | No test for clicking Pause twice rapidly |
| **Abort during pause** | Medium | Can user abort while run is paused? |
| **Resume after completion** | Low | Resume button should be disabled when status is COMPLETED |
| **Long-running stability** | High | No test waits for significant execution progress before pause |
| **Error state recovery** | High | No test for pause/resume after error injection |
| **UI button state** | Medium | No assertion that Pause is disabled after clicking (until confirmed) |

### Domain Specifics

| Domain | Current Coverage | Gap |
|--------|------------------|-----|
| **Data Integrity** | ❌ Not covered | No validation that run history persists after abort |
| **Simulation vs. Reality** | ⚠️ Partial | Uses `ensureSimulationMode()` but doesn't verify Pyodide worker instantiation |
| **Serialization** | ❌ Not covered | No verification of protocol arguments passed to worker |
| **Error Handling** | ⚠️ Minimal | Only tests happy path abort, no Python exception handling |

**Specific Domain Gaps:**

1. **Run History Persistence**:
   ```typescript
   // After abort, should verify:
   await monitorPage.navigateToHistory();
   const row = await monitorPage.waitForHistoryRow(protocolName);
   expect(row).toContainText('CANCELLED');
   ```

2. **Pyodide Worker State**:
   ```typescript
   // Should verify worker received termination signal:
   await page.evaluate(() => {
     const worker = (window as any).pyodideWorker;
     return worker.executionState === 'TERMINATED';
   });
   ```

3. **Timing Sensitivity**:
   - Current tests wait 15s for button visibility — racing with simulation execution speed
   - If simulation completes in <5s, Pause button may never appear
   - Should add `waitForProgressAtLeast(5)` before pause attempt

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 7/10 | Covers core controls, misses button state assertions |
| **Best Practices** | 6/10 | Good POM/locators, lacks isolation and DRY |
| **Test Value** | 9/10 | Critical user journey, high real-world relevance |
| **Isolation** | 4/10 | No worker DB, duplicate setup, no cleanup |
| **Domain Coverage** | 5/10 | Surface-level state verification, no deep integration |

**Overall**: **6.2/10**
