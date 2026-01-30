# SDET Static Analysis: interactive-protocol.spec.ts

**Target File:** [interactive-protocol.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/interactive-protocol.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested
This test verifies the **interactive protocol execution flow** within the JupyterLite/Pyodide-powered playground. Specifically, it tests the bridge between Python code execution and Angular's UI dialog system for three interaction primitives:

1. **`pause(message)`** — Python execution suspends, Angular shows a "Pause" dialog with message, user clicks "Resume" to continue
2. **`confirm(message)`** → `bool` — Python execution suspends, Angular shows a "Confirm" dialog with Yes/No buttons
3. **`input(prompt)`** → `str` — Python execution suspends, Angular shows an "Input" dialog with a text field

**UI Elements Verified:**
- Playground component (`app-playground`)
- JupyterLite iframe (`iframe.notebook-frame`)
- CodeMirror editor within JupyterLite (`.cm-content, .CodeMirror`)
- JupyterLite Run button (`button[data-command="notebook:run-and-advance"]`)
- Output area (`.jp-OutputArea-output`)
- Angular interaction dialog (`app-interaction-dialog`) with Resume/Yes/No/Submit buttons
- Input field within dialog (`input`)

**State Changes Verified:**
- SQLite service initialization (`window.sqliteService.isReady$`)
- Loading overlay dismissal (`.loading-overlay`)
- Python code execution output appearing in JupyterLite
- Dialog appearance and dismissal cycle (3 interaction types)

### Assertions (Success Criteria)
| Assertion | Location (Line) | Purpose |
|-----------|-----------------|---------|
| `loadingOverlay not visible` | 31 | JupyterLite REPL ready |
| `editor toBeVisible` | 52 | CodeMirror cell ready |
| `editor toContainText('from praxis.interactive...')` | 87 | Code typed correctly |
| `editor toContainText('print(f"Hello {name}")')` | 88 | Code typed correctly |
| `outputLocator toBeVisible` (Step 1: Pause) | 118, 126 | Python started executing |
| `dialog toBeVisible` (Pause) | 134 | Pause dialog appeared |
| `dialog toContainText('Check deck')` | 135 | Correct message shown |
| `dialog toBeVisible` (Confirm) | 146 | Confirm dialog appeared |
| `dialog toContainText('Proceed?')` | 147 | Correct message shown |
| `dialog toBeVisible` (Input) | 157 | Input dialog appeared |
| `dialog toContainText('Name?')` | 158 | Correct prompt shown |
| `dialog not toBeVisible` (final) | 168 | Dialog dismissed after input |

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

#### 🔴 Critical Issues

1. **Excessive Hardcoded Waits (7 instances)**
   - Line 43: `waitForTimeout(1000)` — after JupyterLite dialog dismiss
   - Line 55: `waitForTimeout(2000)` — stabilization before editor click
   - Line 57: `waitForTimeout(1000)` — after editor click
   - Line 64: `waitForTimeout(500)` — after clear operation
   - Line 91: `waitForTimeout(1000)` — before running code
   - Line 109, 123: `waitForTimeout(500)` — before Shift+Enter fallback
   - Lines 143, 154: `waitForTimeout(1000)` — after dialog actions

   **Impact:** These 1000ms+ waits add 9+ seconds of guaranteed overhead, making the test slow and still brittle if the delays are insufficient on slower CI runners.

2. **`force: true` Clicks (3 instances)**
   - Line 56: `editor.click({ force: true })` — clicking into CodeMirror
   - Line 105: `runBtn.click({ force: true })` — clicking JupyterLite Run button
   - Line 111: implicit via fixture logic for dialog buttons

   **Impact:** Force clicks bypass visibility/interactability checks, masking timing issues instead of solving them.

3. **No Worker-Indexed Database Isolation**
   - Line 13 uses `resetdb=1` but **not** `dbName=praxis-worker-{index}`
   - The project has `worker-db.fixture.ts` specifically for this purpose, but this test doesn't use it
   
   **Impact:** **Critical parallel execution failure** — multiple workers will clobber each other's database state

4. **Silent Error Swallowing**
   - Lines 22-27, 37-45: try/catch blocks with empty catch or just console.log
   - These hide legitimate initialization failures that should fail the test

#### 🟡 Moderate Issues

5. **Mixed Locator Strategies**
   - Uses `getByRole` for Angular buttons (good: lines 23, 140, 152, 165)
   - Uses CSS class selectors for JupyterLite internals (necessary: iframe content)
   - However, the JupyterLite locators could be more resilient with chained role queries

6. **No Page Object Model**
   - All logic is inline in a single 170-line test function
   - No `PlaygroundPage` exists in the page-objects directory
   - Dialog interactions could be abstracted into an `InteractionDialogHelper`

7. **Cross-Frame Complexity Without Abstraction**
   - Iframe content access (`page.frameLocator('iframe.notebook-frame')`) is repeated inline
   - This should be encapsulated in a `JupyterLiteFrame` page object

### Modern Standards (2026) Evaluation

| Standard | Score | Notes |
|----------|-------|-------|
| **User-Facing Locators** | 6/10 | Uses `getByRole` for Angular, but CSS for JupyterLite (acceptable due to iframe constraints) |
| **Test Isolation** | 2/10 | No `dbName` isolation, single afterEach with Escape key is insufficient cleanup |
| **Page Object Model** | 1/10 | Zero abstraction — entire workflow is inline |
| **Async Angular Handling** | 5/10 | Uses `waitForFunction` for SQLite.isReady$ (good), but relies on hardcoded waits for UI transitions |

---

## 3. Test Value & Classification

### Scenario Relevance
**Critical User Journey ("Happy Path")** — This is THE core workflow for Praxis's interactive lab automation:

1. Lab technicians write Python protocols in the browser
2. Protocols can **pause** for physical checks (e.g., "Check deck alignment")
3. Protocols can **confirm** before destructive operations (e.g., "Proceed with dispense?")
4. Protocols can **input** runtime parameters (e.g., "Enter sample ID")

This test validates the fundamental promise of Praxis: **Python code in the browser can communicate bidirectionally with Angular UI for human-in-the-loop automation**.

**Scenario Realism:** ✅ High — A real user would write exactly this kind of code to automate lab workflows with checkpoints.

### Classification
**True E2E Test** — This test runs:
- Full Angular application shell
- JupyterLite with Pyodide kernel
- SQLite database (OPFS-backed)
- Real Python code execution
- Real Angular Material dialogs

**No mocking detected** — The test exercises the actual frontend → Pyodide → Angular event bridge → dialog → user input → Pyodide resume cycle.

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow
```
User Journey: Interactive Protocol Execution

1. NAVIGATE to Playground
   └─ URL: /app/playground?mode=browser&resetdb=1

2. WAIT for Initialization
   ├─ App shell renders (app-playground)
   ├─ SQLite service becomes ready
   └─ JupyterLite REPL loads (loading overlay disappears)

3. DISMISS Dialogs
   ├─ Welcome dialog (Get Started / Skip / Close)
   └─ JupyterLite theme error dialogs

4. ENTER Python Code
   ├─ Click into last notebook cell editor
   ├─ Select all, delete existing content
   └─ Type interactive protocol code:
       from praxis.interactive import pause, confirm, input
       await pause("Check deck")
       await confirm("Proceed?")
       await input("Name?")

5. EXECUTE Code
   ├─ Click Run button, OR
   └─ Fallback: Shift+Enter

6. INTERACT with Pause Dialog
   ├─ Dialog appears with "Check deck" message
   ├─ Take screenshot for verification
   └─ Click "Resume"

7. INTERACT with Confirm Dialog
   ├─ Dialog appears with "Proceed?" message
   ├─ Take screenshot for verification
   └─ Click "Yes"

8. INTERACT with Input Dialog
   ├─ Dialog appears with "Name?" prompt
   ├─ Take screenshot for verification
   ├─ Type "Tester" into input field
   └─ Click "Submit"

9. VERIFY Completion
   └─ Dialog is no longer visible
```

### Contextual Fit
This test validates the **Playground → Interaction Dialog** integration, which is the centerpiece of Praxis's "browser-native lab automation" value proposition.

**Architectural Position:**
```
┌──────────────────────────────────────────────────────────────┐
│                     Angular App Shell                         │
├──────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────┐  │
│  │              Playground Component                       │  │
│  │  ┌─────────────────────────────────────────────────┐   │  │
│  │  │         JupyterLite (iframe)                     │   │  │
│  │  │  ┌───────────────────────────────────────────┐  │   │  │
│  │  │  │ Pyodide Kernel ───┐                       │  │   │  │
│  │  │  │   praxis.interactive│                      │  │   │  │
│  │  │  │   pause/confirm/input│                    │  │   │  │
│  │  │  └───────────────────────│───────────────────┘  │   │  │
│  │  └──────────────────────────│──────────────────────┘   │  │
│  │                             ▼                          │  │
│  │  ┌─────────────────────────────────────────────────┐   │  │
│  │  │         InteractionDialogComponent              │ ◄─── THIS TEST
│  │  │         (Material Dialog)                       │   │  │
│  │  └─────────────────────────────────────────────────┘   │  │
│  └────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────┤
│                 SQLite Service (OPFS)                         │
└──────────────────────────────────────────────────────────────┘
```

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

#### 🔴 High Priority Gaps

1. **No Python Output Verification**
   - The test checks that `Step 1: Pause` appears, but never verifies:
     - `"Paused done"` (post-resume output)
     - `"Confirmed: True"` (confirm result)
     - `"Hello Tester"` (input result)
   - **Impact:** The test doesn't prove the Python side received the correct values back

2. **No Confirm=No Path**
   - Only tests clicking "Yes" on confirm dialog
   - Never tests clicking "No" and verifying `ans = False`

3. **No Cancel/Escape Handling**
   - What happens if user presses Escape during an input dialog?
   - What happens if user closes the dialog via backdrop click?

4. **No Input Validation**
   - What happens if user submits empty input?
   - What happens if user enters special characters (quotes, newlines)?

5. **No Error State Testing**
   - What if Python code has a syntax error?
   - What if `pause()` is called with None?
   - What if Python raises an exception mid-execution?

### Domain Specifics

| Domain Aspect | Coverage | Gap |
|---------------|----------|-----|
| **Data Integrity** | ❌ None | Test doesn't verify praxis.db state changes (if any persist from interactive sessions) |
| **Simulation vs. Reality** | ✅ Partial | Uses `resetdb=1` for clean state, but no worker isolation |
| **Serialization** | ❌ None | Doesn't verify that Python string arguments are correctly passed to dialog (what about unicode? long strings?) |
| **Error Handling** | ❌ None | No negative test cases |

#### 🟡 Medium Priority Gaps

6. **Timing Race Condition**
   - The test waits for `outputLocator` to show `Step 1: Pause`, then immediately expects `dialog toBeVisible`
   - There's a race condition: Python may not have called `pause()` yet even if print statement completed

7. **No Cleanup of Python State**
   - If test fails mid-execution, the Pyodide kernel may be in a broken state
   - `afterEach` only presses Escape — doesn't reset the kernel

8. **Screenshot Assertions Missing**
   - Takes 4 screenshots but never validates their content
   - Visual regression testing could catch dialog styling issues

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 7/10 | Covers the happy path for all 3 interaction types |
| **Best Practices** | 3/10 | Excessive waits, force clicks, no POM, no isolation |
| **Test Value** | 8/10 | Critical user journey, real E2E with no mocking |
| **Isolation** | 2/10 | Missing `dbName` worker isolation, minimal cleanup |
| **Domain Coverage** | 4/10 | No output verification, no error paths, no confirm=No |

**Overall**: **4.8/10**

---

## Appendix: Detailed Issue Tracker

| Issue ID | Severity | Line(s) | Description | Fix Effort |
|----------|----------|---------|-------------|------------|
| IP-001 | 🔴 Critical | 13 | No worker-indexed dbName | Low |
| IP-002 | 🔴 Critical | All | 9+ seconds of hardcoded waits | Medium |
| IP-003 | 🟡 Medium | 56,105 | force:true clicks | Medium |
| IP-004 | 🟡 Medium | N/A | No PlaygroundPage POM | High |
| IP-005 | 🟡 Medium | 22-27,37-45 | Silent error swallowing | Low |
| IP-006 | 🟠 Low | N/A | No output verification | Medium |
| IP-007 | 🟠 Low | N/A | No confirm=No test | Low |
| IP-008 | 🟠 Low | N/A | No error state tests | High |
