# SDET Static Analysis: protocol-execution.spec.ts

**Target File:** [protocol-execution.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/protocol-execution.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested

This test file covers the **Protocol Wizard Flow** — the complete happy-path journey from protocol library display through simulated execution completion. Specifically:

1. **Protocol Library Display** (`should display protocol library`)
   - Navigation to `/app/run` via `ProtocolPage.navigateToProtocols()`
   - Visibility of protocol cards (`app-protocol-card` components)
   - Basic count verification (at least one protocol exists)

2. **End-to-End Simulated Execution** (`should complete simulated execution`)
   - Full wizard traversal: Protocol Selection → Parameter Configuration → Machine Selection → Asset Auto-Config → Deck Setup → Review → Execution Start → Monitoring → Completion
   - Uses `ProtocolPage.advanceToReview()` which delegates to `WizardPage` for multi-step advancement
   - Monitors execution via `mat-progress-bar` visibility and status chip text matching

### Assertions (Success Criteria)

| Test | Assertion | Type |
|------|-----------|------|
| Protocol Library | `protocolCards.first().toBeVisible()` | UI Visibility |
| Protocol Library | `protocolCards.count() > 0` | Data Presence |
| Simulated Execution | Status matches `/Initializing\|Running\|Queued\|Starting/i` | State Transition |
| Simulated Execution | `mat-progress-bar` visible during execution | UI Element |
| Simulated Execution | Final status matches `/(Completed\|Succeeded\|Finished)/i` | Terminal State |

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

#### 🔴 Critical Issues

1. **No Worker Database Isolation (Line 1)**
   ```typescript
   import { test, expect } from '@playwright/test';
   ```
   Uses raw Playwright imports instead of `'../fixtures/app.fixture'`. This means:
   - No `dbName=praxis-worker-N` isolation
   - **Will fail in parallel execution** due to OPFS contention
   - No automatic welcome dialog dismissal from fixture

2. **Manual SQLite Ready Polling (Lines 14-18)**
   ```typescript
   await page.waitForFunction(
       () => (window as any).sqliteService?.isReady$?.getValue() === true,
       null,
       { timeout: 30000 }
   );
   ```
   Duplicates logic from `app.fixture.ts:waitForDbReady()`. Violates DRY principle.

3. **Hardcoded Screenshot Paths (Lines 45, 55, 75, etc.)**
   ```typescript
   await page.screenshot({ path: '/tmp/e2e-protocol/01-protocol-library.png' });
   ```
   - Hardcoded `/tmp` path is not portable
   - No cleanup of screenshot artifacts
   - Should use Playwright's built-in artifact handling

4. **Non-Deterministic Protocol Selection (Lines 61-69)**
   ```typescript
   const hasProtocol = await page.getByText(protocolName).isVisible().catch(() => false);
   if (hasProtocol) { ... } else { ... selectFirstProtocol(); }
   ```
   - Falls back to "first available" if "Simple Transfer" not found
   - Test behavior varies based on database state
   - No assertion on which protocol was actually selected

5. **URL Wait with Silent Failure (Lines 21-23)**
   ```typescript
   await page.waitForURL('**/app/home', { timeout: 15000 }).catch(() => {
       console.log('Did not redirect to /app/home automatically');
   });
   ```
   Swallows redirect failures silently — test continues in undefined state.

#### 🟡 Moderate Issues

6. **Inconsistent Stepper State Verification**
   - No assertion that wizard is in the correct step before performing step-specific actions
   - Relies on implicit timing from `WizardPage.advanceToReview()` orchestration

7. **Brittle Welcome Dialog Handling (Lines 29-34)**
   ```typescript
   const welcomeDialog = page.getByRole('dialog', { name: /Welcome to Praxis/i });
   if (await welcomeDialog.isVisible({ timeout: 5000 })) { ... }
   ```
   - Uses visibility check with timeout instead of state-driven approach
   - Duplicates logic already in `app.fixture.ts`

8. **`force: true` Usage in Page Object (protocol.page.ts:60)**
   ```typescript
   await firstCard.click({ force: true });
   ```
   - Bypasses actionability checks
   - Hides real UI issues (overlays, animations)

### Modern Standards (2026) Evaluation

| Standard | Rating | Notes |
|----------|--------|-------|
| **User-Facing Locators** | ⚠️ Partial | Uses `getByRole('dialog')`, `getByRole('button')` but also CSS selectors like `.sidebar-rail`, `mat-progress-bar` |
| **Test Isolation** | ❌ Failing | No worker-indexed DB, no fixture integration, cross-test state leakage possible |
| **Page Object Model** | ✅ Good | Uses `ProtocolPage` which delegates to `WizardPage` and `ExecutionMonitorPage` |
| **Async Angular Handling** | ⚠️ Partial | Uses `waitForFunction` for SQLite, but relies on timeouts elsewhere |
| **Fixture Usage** | ❌ Failing | Imports raw `@playwright/test` instead of project fixture |
| **afterEach Cleanup** | ✅ Present | Dismisses dialogs via Escape key (line 38-40) |

---

## 3. Test Value & Classification

### Scenario Relevance

**Critical Happy Path**: This tests the **primary value proposition** of the application:
1. User visits protocol library
2. User selects and configures a protocol
3. User executes the protocol
4. User monitors execution to completion

This is a **Tier 1 user journey** that directly maps to the core lab automation workflow.

### Classification

| Aspect | Classification | Rationale |
|--------|---------------|-----------|
| **Test Type** | **True E2E Test** | Exercises full stack: UI → Angular Services → SQLite (OPFS) → Pyodide Worker → Simulation Backend |
| **Mocking Level** | **Low** | Uses "Simulation" machine abstraction but within the real execution framework |
| **Integration Depth** | **High** | Traverses 6+ wizard steps, multiple Angular components, database persistence |

⚠️ **However**: The lack of worker isolation means this test cannot run in parallel, limiting its CI value.

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

```
[User opens application]
     ↓
[App redirects to /app/home, SQLite initializes]
     ↓
[Welcome dialog appears → User clicks "Skip for Now"]
     ↓
[User navigates to Protocol Library (/app/run)]
     ↓
[Protocol cards load from database]
     ↓
[User clicks "Simple Transfer" (or first available)]
     ↓
[User advances through wizard:]
   │
   ├─► Parameters Step → Clicks "Continue" (defaults accepted)
   │
   ├─► Machine Step → Selects first compatible (simulation) machine
   │   └─► Handles "Configure Simulation" dialog if presented
   │
   ├─► Assets Step → Auto-configured from machine selection
   │
   ├─► Deck Setup → Clicks "Skip Setup"
   │
   └─► Review Step → Verifies "Ready to Launch" heading
     ↓
[User clicks "Start Execution"]
     ↓
[Browser redirects to /run/live]
     ↓
[Execution Monitor shows progress bar and status]
     ↓
[User observes status: Initializing → Running → Completed]
     ↓
[Test captures screenshots at each stage]
```

### Contextual Fit

This test covers the **Run Protocol** feature, which is the central workflow of the Praxis lab automation platform. It validates:

1. **Protocol Catalog Integration** — Protocols loaded from SQLite definitions
2. **Wizard State Machine** — Multi-step form with conditional steps (wells, deck)
3. **Machine Selection** — Compatibility filtering and simulation mode
4. **Execution Engine** — Pyodide-based simulation with progress tracking
5. **Monitor Dashboard** — Real-time status updates and completion detection

The `ProtocolPage` → `WizardPage` → `ExecutionMonitorPage` chain represents the canonical POM architecture for this feature set.

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Severity | Description |
|-----|----------|-------------|
| **Parameter Validation** | High | No test verifies parameter input constraints or defaulting logic |
| **Machine Compatibility Filtering** | High | No assertion that incompatible machines are filtered out |
| **Well Selection Workflow** | Medium | `wellStep` is conditionally skipped without testing the actual well selection flow |
| **Error Recovery** | High | No test for mid-execution cancellation or pause/resume |
| **Multi-Protocol Queue** | Medium | No test for batch execution scenarios |

### Domain Specifics

#### Data Integrity

| Aspect | Status | Details |
|--------|--------|---------|
| **Database Loading** | ⚠️ Implicit | `waitForFunction(sqliteService.isReady$)` validates initialization but not content |
| **Protocol Schema** | ❌ Not Verified | No assertion that protocol JSON/schema is correctly parsed |
| **Run Record Persistence** | ❌ Not Verified | No check that completed run is persisted to `run_history` table |

#### Simulation vs. Reality

| Aspect | Status | Details |
|--------|--------|---------|
| **Simulation Mode Toggle** | ⚠️ Unused | `ProtocolPage.ensureSimulationMode()` exists but is never called |
| **Chatterbox Backend** | ⚠️ Implicit | Test assumes simulation environment but doesn't verify mode |
| **Timing Characteristics** | ❌ Not Validated | No verification of simulated timing vs. real hardware expectations |

#### Serialization

| Aspect | Status | Details |
|--------|--------|---------|
| **Protocol Arguments** | ❌ Not Verified | No verification that parameters are serialized to Pyodide worker |
| **Machine Configuration** | ❌ Not Verified | No check that machine config JSON is correctly passed |
| **Asset Mappings** | ❌ Not Verified | Auto-configuration occurs but mappings not validated |

#### Error Handling

| Aspect | Status | Details |
|--------|--------|---------|
| **Invalid Protocol** | ❌ Not Tested | No test for malformed protocol definition |
| **Python Syntax Error** | ❌ Not Tested | No test for Pyodide execution failures |
| **Machine Unavailable** | ❌ Not Tested | No test for "no compatible machines" state |
| **Execution Timeout** | ❌ Not Tested | No test for long-running or hung executions |

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 7/10 | Covers core happy path, but lacks negative cases |
| **Best Practices** | 4/10 | No worker isolation, hardcoded paths, duplicated fixture logic |
| **Test Value** | 8/10 | High-value Tier 1 journey, good POM usage |
| **Isolation** | 2/10 | Critical failure: cannot run in parallel |
| **Domain Coverage** | 3/10 | No data integrity, serialization, or error handling verification |

**Overall**: **4.8/10**

---

## Files Reviewed

| File | Purpose | Lines |
|------|---------|-------|
| `e2e/specs/protocol-execution.spec.ts` | Test spec | 101 |
| `e2e/page-objects/protocol.page.ts` | Protocol POM | 149 |
| `e2e/page-objects/wizard.page.ts` | Wizard stepper POM | 344 |
| `e2e/page-objects/monitor.page.ts` | Execution monitor POM | 125 |
| `e2e/fixtures/app.fixture.ts` | (Not used, should be) | 134 |
