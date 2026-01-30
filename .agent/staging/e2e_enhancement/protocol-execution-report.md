# SDET Static Analysis: protocol-execution.spec.ts

**Target File:** [protocol-execution.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/protocol-execution.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested
This 101-line test file covers the **Protocol Wizard Flow** - the core user journey for configuring and executing lab automation protocols:

1. **Protocol Library Display**: Verifies protocols are listed and visible
2. **Simulated Execution End-to-End**: Complete flow from protocol selection through execution completion

**UI Elements Verified:**
- Sidebar rail visibility (shell layout loaded)
- Welcome dialog dismissal
- Protocol cards in library view
- Mat-progress-bar during execution
- Status chip with execution state

**State Changes Verified:**
- SQLite database ready state
- URL redirection to `/app/home`
- Wizard step progression
- Execution status transitions (Initializing → Running → Completed)

### Assertions (Success Criteria)
| Assertion | Location | Purpose |
|-----------|----------|---------|
| `expect(page.locator('.sidebar-rail')).toBeVisible()` | Line 26 | Shell layout loaded |
| `expect(welcomeDialog).not.toBeVisible()` | Line 33 | Welcome dialog dismissed |
| `expect(protocolPage.protocolCards.first()).toBeVisible()` | Line 44 | Protocol library displays |
| `expect(protocolCards.count()).toBeGreaterThan(0)` | Line 47 | At least one protocol exists |
| `expect(status).toMatch(/Initializing|Running|.../i)` | Line 82 | Execution started |
| `expect(page.locator('mat-progress-bar')).toBeVisible()` | Line 89 | Progress tracking visible |
| `expect(finalStatus).toMatch(/(Completed|.../i)` | Line 96 | Execution finished successfully |

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

#### 🟡 Medium: No Worker Isolation
```typescript
test.beforeEach(async ({ page }) => {
    protocolPage = new ProtocolPage(page);
    await page.goto('/');  // Not using BasePage.goto()
    ...
});
```
- Direct `page.goto('/')` bypasses the `BasePage` worker isolation pattern
- No `testInfo` passed to enable worker-indexed database
- Risk of OPFS contention in parallel execution

#### 🟡 Medium: Hardcoded Timeouts (but acceptable)
```typescript
await page.waitForFunction(..., { timeout: 30000 });
await page.waitForURL('**/app/home', { timeout: 15000 });
test.setTimeout(120000);
```
- Timeouts are generous but justified for SQLite initialization and full execution flow
- 120s for full execution test is reasonable given Pyodide startup + simulation

#### 🟡 Medium: Swallowed Errors
```typescript
await page.waitForURL('**/app/home', { timeout: 15000 }).catch(() => {
    console.log('Did not redirect to /app/home automatically');
});
```
- Silent catch could mask real failures
- Test continues even if redirect never happens

#### 🟢 Good: Uses `test.step()` for Structured Reporting
```typescript
await test.step('Navigate to Protocols', async () => { ... });
await test.step('Select and Configure Protocol', async () => { ... });
```
Excellent for debugging failed tests - Playwright UI shows step-by-step breakdown.

#### 🟢 Good: Screenshot Capture at Key Points
```typescript
await page.screenshot({ path: '/tmp/e2e-protocol/01-protocol-library.png' });
```
Captures visual evidence at each major step for debugging.

#### 🟢 Good: Proper Dialog Handling
```typescript
const welcomeDialog = page.getByRole('dialog', { name: /Welcome to Praxis/i });
if (await welcomeDialog.isVisible({ timeout: 5000 })) {
    await page.getByRole('button', { name: /Skip for Now/i }).click();
}
```
Uses accessible role selector and handles optional dialog gracefully.

#### 🟢 Good: Has Cleanup Hook
```typescript
test.afterEach(async ({ page }) => {
    await page.keyboard.press('Escape').catch(() => { });
});
```
Dismisses any open dialogs to prevent state leakage.

### Modern Standards (2026) Evaluation

| Category | Rating | Notes |
|----------|--------|-------|
| **User-Facing Locators** | 🟡 7/10 | Mix of `getByRole` and CSS selectors (`.sidebar-rail`) |
| **Test Isolation** | 🟡 5/10 | Has cleanup but no DB isolation for parallel |
| **Page Object Model** | 🟢 8/10 | Good use of `ProtocolPage` and `WizardPage` |
| **Async Angular Handling** | 🟢 8/10 | Proper SQLite readiness check via `waitForFunction` |

---

## 3. Test Value & Classification

### Scenario Relevance
**Critical Happy Path**: This tests the **primary user journey** of Praxis:
1. ✅ Select a protocol from the library
2. ✅ Configure parameters
3. ✅ Execute in simulation mode
4. ✅ Verify completion

This is the **most important workflow** in the application. Every lab run follows this path.

### Classification
**True E2E Test** ✅
- No mocking visible
- Full stack: Angular UI → SQLite → Pyodide worker → Protocol execution
- Tests actual async state transitions

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

**Test 1: Protocol Library Display**
1. User navigates to the protocol runner
2. System displays available protocol cards
3. User confirms protocols are listed

**Test 2: Simulated Execution**
1. User navigates to `/` and is redirected to `/app/home`
2. System initializes SQLite database in browser
3. Welcome dialog appears; user clicks "Skip for Now"
4. User navigates to Protocols section
5. User selects "Simple Transfer" protocol (or first available)
6. User clicks Continue to advance
7. Wizard automatically progresses through:
   - Parameter configuration
   - Machine selection
   - Asset assignment
   - Deck setup
   - Review step
8. User clicks "Start Execution"
9. System shows status chip with "Initializing/Running"
10. Progress bar appears showing execution progress
11. User waits for completion
12. Status changes to "Completed/Succeeded/Finished"

### Contextual Fit
The Protocol Execution Wizard is the **core feature** of Praxis:
- Guides users through complex lab automation setup
- Handles protocol selection, parameterization, machine assignment
- Critical path for all instrument operations
- This test validates the entire workflow is functional

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

1. **No Parameter Verification**: Uses defaults without validating parameter input/output
2. **No Machine Selection Verification**: Doesn't verify correct machine was selected
3. **No Asset Configuration Check**: Doesn't verify deck layout or asset positions
4. **No Data Persistence Verification**: Doesn't check run is stored in SQLite history
5. **No Log/Timeline Verification**: Doesn't verify execution logs are captured

### Domain Specifics

| Domain Area | Coverage | Gap |
|-------------|----------|-----|
| **Data Integrity** | 🟡 Partial | SQLite ready checked, but not run persistence |
| **Simulation vs. Reality** | 🟡 Implicit | Test runs simulation mode but doesn't verify mode |
| **Serialization** | 🔴 None | No verification of protocol args → Pyodide worker |
| **Error Handling** | 🔴 None | No failure scenario tests (invalid params, worker crash) |

### Additional Missing Scenarios
- Protocol not found / empty library
- Invalid parameter values
- Machine unavailable/incompatible
- Execution timeout
- User cancellation mid-run
- Resume interrupted execution
- Multiple concurrent executions

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 7/10 | Covers core flow, but only happy path |
| **Best Practices** | 6/10 | Good structure, missing DB isolation |
| **Test Value** | 9/10 | Critical user journey, high value |
| **Isolation** | 5/10 | Has cleanup but no parallel safety |
| **Domain Coverage** | 5/10 | Hits execution but not data verification |

**Overall**: **6.4/10** 🟡

### Key Improvements Needed
1. Add worker-indexed DB isolation for parallel safety
2. Replace silent `.catch()` with explicit error handling
3. Add post-execution data verification (run exists in history)
4. Verify actual parameter values used in execution
5. Add at least one failure scenario test

