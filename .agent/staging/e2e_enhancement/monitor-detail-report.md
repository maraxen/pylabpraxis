# SDET Static Analysis: monitor-detail.spec.ts

**Target File:** [monitor-detail.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/monitor-detail.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested
This minimal test file (27 lines) covers **two** scenarios for the Run Detail View component:
1. **Navigation to Run Detail Page**: Verifies that clicking on the first run in a list navigates to a detail view and displays correct run details.
2. **Error Handling for Invalid Run ID**: Verifies that navigating directly to an invalid run ID displays a "Run not found" error message.

**UI Elements Verified:**
- First run item visibility in list
- Run detail page content after navigation
- Error message display for invalid routes

**State Changes Verified:**
- URL navigation from list to detail view
- Error state rendering

### Assertions (Success Criteria)
| Assertion | Location |
|-----------|----------|
| `expect(firstRun).toBeVisible()` | Line 14 |
| `monitorPage.verifyRunDetails(runId)` | Line 19 (delegated) |
| `expect(page.getByText('Run not found')).toBeVisible()` | Line 24 |

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

#### 🔴 CRITICAL: Broken Import
```typescript
import { MonitorPage } from '../page-objects/monitor.page';
```
**Issue:** The page object file exports `ExecutionMonitorPage`, NOT `MonitorPage`. This test **will not compile**. The import statement does not match any exported class.

#### 🔴 CRITICAL: Missing POM Methods
The test calls methods on `monitorPage` that don't exist in the `ExecutionMonitorPage` class:
- `getFirstRun()` - **Does not exist** in POM
- `getRunId(locator)` - **Does not exist** in POM  
- `verifyRunDetails(runId)` - **Does not exist** in POM

**Impact:** This test is fundamentally broken and cannot run.

#### 🟡 Medium: No Worker Isolation
- Uses `monitorPage.goto()` without passing `testInfo` 
- Does not leverage `worker-db.fixture` pattern for parallel safety
- Base class constructor expects optional `testInfo` but it's never passed

#### 🟡 Medium: No Cleanup
- No `afterEach` hook to handle stray dialogs/overlays
- Could leave modal dialogs open affecting subsequent tests

#### 🟢 Good: Clean Test Structure
- Uses appropriate `beforeEach` setup pattern
- Test names are descriptive and follow conventions
- Short, focused test cases

### Modern Standards (2026) Evaluation

| Category | Rating | Notes |
|----------|--------|-------|
| **User-Facing Locators** | 🟡 6/10 | Uses `getByText`, `getByRole` appropriately but relies on POM methods that don't exist |
| **Test Isolation** | 🔴 2/10 | No worker isolation, no cleanup, no database reset |
| **Page Object Model** | 🔴 1/10 | POM methods referenced don't exist - test is DOA |
| **Async Angular Handling** | 🟡 5/10 | Uses `goto()` which waits for SQLite, but no explicit Angular stability checks |

---

## 3. Test Value & Classification

### Scenario Relevance
**Happy Path + Error Case**: These represent fundamental user journeys:
1. ✅ User viewing run history and drilling into details is a **critical happy path**
2. ✅ Handling malformed URLs gracefully is an important **defensive scenario**

Both are realistic scenarios users would encounter.

### Classification
**⚠️ INDETERMINATE - Test Cannot Run**

If the test could run, it would be a **True E2E Test** (no mocking visible, navigates real app routes).

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

**Test 1: Navigate to Run Detail**
1. User navigates to Monitor page (execution history list)
2. User sees list of previous protocol runs
3. User clicks on the first run in the list
4. System navigates to `/app/monitor/{runId}`
5. User verifies the run details match the clicked run

**Test 2: Invalid Run ID**
1. User (or external link) navigates directly to `/app/monitor/invalid-run-id`
2. System displays "Run not found" error message

### Contextual Fit
The Monitor component is the **observability layer** of Praxis:
- Shows live execution status during protocol runs
- Provides historical view of all past executions
- Enables drill-down into specific runs for debugging/analysis
- Critical for lab operators monitoring instrument status

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths
1. **No data prerequisite setup**: Tests assume runs exist but don't create them
2. **No verification of actual run data**: Just checks visibility, not content accuracy
3. **No live execution monitoring test**: Only tests navigation to completed runs
4. **No timeline/log verification**: The detail view has logs and timelines not tested

### Domain Specifics

| Domain Area | Coverage | Gap |
|-------------|----------|-----|
| **Data Integrity** | 🔴 None | No verification that run data is correctly loaded from SQLite |
| **Simulation vs. Reality** | ⚪ N/A | This view doesn't distinguish execution modes |
| **Serialization** | 🔴 None | Run details include serialized parameters - not verified |
| **Error Handling** | 🟡 Partial | Invalid URL covered; no test for corrupted run data |

### Additional Missing Scenarios
- Empty state (no runs exist)
- Run in progress vs. completed states
- Parameter display accuracy
- Log panel content verification
- Progress bar behavior during execution
- Refresh/reload behavior
- Pagination if many runs exist

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 3/10 | Only 2 basic scenarios, missing core functionality |
| **Best Practices** | 1/10 | Broken import, missing POM methods, no isolation |
| **Test Value** | 6/10 | Good intent, covers real user scenarios |
| **Isolation** | 2/10 | No worker DB, no cleanup hooks |
| **Domain Coverage** | 2/10 | No data integrity, no state verification |

**Overall**: **2.8/10** 🔴

### Immediate Blockers
1. Fix import: `MonitorPage` → `ExecutionMonitorPage`
2. Implement missing POM methods: `getFirstRun()`, `getRunId()`, `verifyRunDetails()`
3. Add prerequisite: Create a run before testing navigation

