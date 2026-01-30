# SDET Static Analysis: 01-execution-controls.spec.ts

**Target File:** [01-execution-controls.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/interactions/01-execution-controls.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested
This test file validates the **execution control buttons** available during a simulated protocol run:
- **Pause/Resume Flow**: Tests clicking the Pause button, verifying the status transitions to `PAUSED`, clicking Resume, and verifying recovery to `RUNNING` or `COMPLETED`
- **Abort Flow**: Tests clicking the Abort/Stop button, handling a confirmation dialog if present, and verifying the status transitions to `CANCELLED` or `FAILED`

**UI Elements Verified:**
- Pause button (`getByRole('button', { name: /pause/i })`)
- Resume button (`getByRole('button', { name: /resume/i })`)
- Abort/Stop/Cancel button (compound filter)
- Confirmation dialog button (for abort flow)
- Run status chip (via `monitorPage.waitForStatus()`)

**State Changes Verified:**
- Status transition: `→ PAUSED` (after pause)
- Status transition: `PAUSED → RUNNING | COMPLETED` (after resume)
- Status transition: `→ CANCELLED | FAILED` (after abort)

### Assertions (Success Criteria)
1. **Pause button visible** within 15s of dashboard load
2. **Status contains `PAUSED`** after clicking pause (60s timeout via POM)
3. **Resume button visible** within 15s after pause
4. **Status contains `RUNNING | COMPLETED`** after clicking resume
5. **Abort button visible** within 15s of dashboard load
6. **Status contains `CANCELLED | FAILED`** after abort confirmation

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

#### ✅ Strengths
| Pattern | Evidence |
|---------|----------|
| **Uses user-facing locators** | `getByRole('button', { name: /pause/i })` throughout |
| **POM abstraction** | Uses `WelcomePage`, `ProtocolPage`, `WizardPage`, `ExecutionMonitorPage` |
| **No hardcoded `waitForTimeout`** | All waits are state-driven or assertion timeouts |
| **Regex-based status matching** | `/RUNNING|COMPLETED/` handles race conditions gracefully |
| **Confirmation dialog handling** | Graceful conditional check with `.catch(() => false)` timeout |

#### ⚠️ Concerns
| Issue | Location | Severity |
|-------|----------|----------|
| **No worker-indexed DB isolation** | `beforeEach` uses `WelcomePage.goto()` but `WelcomePage` doesn't pass `testInfo` | **Medium** - Parallel flakiness risk |
| **Uses generic Playwright `test` import** | Line 1 - Missing custom fixture for DB isolation | **Medium** |
| **Abort button selector overspecified** | Line 75: `.filter({ hasText: /Stop|Abort|Cancel/i })` after `name:` is redundant | **Low** |
| **Missing cleanup/teardown** | No explicit `afterEach` to ensure execution terminates | **Low** - Simulation auto-terminates |
| **Linear step repetition** | Both tests repeat wizard flow identically (27 lines × 2) | **Low** - Maintainability |

### Modern Standards (2026) Evaluation

| Criterion | Status | Notes |
|-----------|--------|-------|
| **User-Facing Locators** | ✅ **Excellent** | `getByRole`, `getByTestId` via POM |
| **Test Isolation** | ⚠️ **Incomplete** | No worker-indexed DB, no explicit teardown |
| **Page Object Model (POM)** | ✅ **Good** | Effective use of 4 POMs |
| **Async Angular Handling** | ✅ **Good** | Uses `waitFor`, `waitForStatus` with state-driven assertions |
| **Fixture Integration** | ❌ **Missing** | Not using project's worker-db fixture |

---

## 3. Test Value & Classification

### Scenario Relevance
| Factor | Assessment |
|--------|------------|
| **User Journey Type** | **Critical Path** - Pause/Resume/Abort are essential execution controls |
| **Realistic Scenario** | ✅ Yes - Users frequently pause to inspect state or abort failed runs |
| **Edge Case Coverage** | ⚠️ Partial - Only tests happy paths (button click → expected status) |

### Classification
**True E2E Test** - This test executes the full wizard → execution → monitor flow with minimal mocking:
- Launches from `/app/run` with real URL navigation
- Executes the complete 6-step wizard (protocols → params → machine → assets → deck → review)
- Starts actual simulation execution
- Interacts with live execution monitor dashboard

**Integration Level:** Full-stack browser mode (uses Pyodide/SQL.js for client-side execution)

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

**Test 1: Pause and Resume**
```
1. User navigates to Welcome page → Skip splash
2. User navigates to /app/run (protocol selector)
3. User enables Simulation mode
4. User selects first protocol → Continue
5. User completes parameter step → Continue
6. User selects first compatible machine (prefers Simulation/Chatterbox) → Continue
7. User waits for assets auto-configuration → Continue
8. User skips/advances deck setup → Continue
9. User opens Review & Run tab
10. User clicks "Start Execution"
11. --- Redirect to /run/live ---
12. User waits for live dashboard to load
13. User clicks "Pause" button
14. ✓ ASSERT: Status chip shows "PAUSED"
15. User clicks "Resume" button  
16. ✓ ASSERT: Status chip shows "RUNNING" or "COMPLETED"
```

**Test 2: Abort Execution**
```
Steps 1-12: Same as Test 1
13. User clicks "Stop/Abort/Cancel" button
14. (If confirmation dialog appears) User clicks confirm
15. ✓ ASSERT: Status chip shows "CANCELLED" or "FAILED"
```

### Contextual Fit
This component fits into the **Execution Lifecycle** domain:
- **Upstream dependencies:** Protocol Library, Wizard Configuration, Machine/Asset Selection
- **Downstream verification:** Run History, Data Persistence
- **Parallel concerns:** Real-time telemetry, Log streaming, Progress tracking

The Execution Controls are critical for:
- **Lab safety:** Ability to halt robotic operations
- **Error recovery:** Abort and retry after failures
- **Debugging:** Pause to inspect mid-execution state

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Impact | Priority |
|-----|--------|----------|
| **No state persistence verification** | After pause/resume, doesn't verify progress is maintained | **High** |
| **No telemetry continuity check** | After resume, doesn't verify telemetry stream resumes | **Medium** |
| **No abort confirmation edge cases** | Only tests happy path (confirm clicked) | **Medium** |
| **No abort during pause test** | User might abort while paused | **Medium** |
| **No rapid click stress test** | Pause → Resume → Pause in quick succession | **Low** |
| **No button state verification** | Pause button should disable/hide after click | **Low** |

### Domain Specifics

| Area | Assessment |
|------|------------|
| **Data Integrity** | ⚠️ **Not verified** - No check that run history records pause/resume events with timestamps |
| **Simulation vs. Reality** | ✅ **Uses simulation mode** via `ensureSimulationMode()` - correct for E2E tests |
| **Serialization** | ❌ **Not tested** - No verification that pause state is serialized to worker or DB |
| **Error Handling** | ⚠️ **Minimal** - No test for: (1) pause during initialization, (2) abort fails, (3) network drop during abort |

### Recommended Additional Test Cases
1. **Pause at 0% progress** - Can we pause immediately after start?
2. **Resume after navigation** - Pause, navigate away, return, resume
3. **Abort rejection** - Click Abort → Cancel confirmation → verify still running
4. **Pause persistence** - Pause, refresh browser, verify state is restored
5. **Run history audit** - After abort, verify run appears in history with `CANCELLED` status

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 7/10 | Clear focus on execution controls; missing edge cases |
| **Best Practices** | 7/10 | Good locators/POM; missing worker isolation fixture |
| **Test Value** | 8/10 | Critical user journey with realistic flow |
| **Isolation** | 5/10 | No DB isolation; no explicit cleanup |
| **Domain Coverage** | 5/10 | Happy paths only; no state persistence verification |

**Overall**: **6.4/10**

---

## Appendix: Technical Debt Items

1. **TD-001:** Migrate from `@playwright/test` to custom fixture with worker-indexed DB
2. **TD-002:** Extract wizard flow to shared helper to reduce duplication
3. **TD-003:** Add post-action state snapshots for debugging flaky failures
4. **TD-004:** Simplify abort button selector (remove redundant `.filter()`)
