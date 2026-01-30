# SDET Static Analysis: mock-removal-verification.spec.ts

**Target File:** [mock-removal-verification.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/mock-removal-verification.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested
This test file verifies the **cleanup of mock/placeholder data** from the application's database and UI. It confirms that:

1. **Mock Protocols are Absent**: Legacy placeholder protocols (`Daily System Maintenance`, `Cell Culture Feed`, `Evening Shutdown`) are no longer displayed in the protocol library.
2. **Real Protocols are Present**: At least one genuine `.praxis-card` protocol card is rendered, indicating that the database was seeded correctly with real protocol data from `generate_browser_db.py` or the prebuilt `praxis.db`.
3. **Run History Starts Empty**: The execution monitor's history table displays an empty state (no prior runs), confirming that mock run records (`MOCK-RUN-001`) are not present.
4. **Home Dashboard is Clean**: The home view shows "No recent activity" and does not display mock run names like `PCR Prep Run #12`, `Cell Culture Feed Batch A`, or `System Calibration`.

**UI Elements Verified:**
- Protocol cards (`.protocol-card`)
- History table with empty state indicators (`.empty-runs-state`, `.no-runs-message`, `:text("No Runs Yet")`)
- Home dashboard "No recent activity" message

**State Changes Verified:**
- Database reset via `?resetdb=1` on initial navigation
- Absence of mock data post-reset

### Assertions (Success Criteria)
| Test | Key Assertions |
|------|----------------|
| `verify mock protocols are absent and real protocols are present` | 3× `expect(...).not.toBeVisible()` for mock protocols; `expect(realProtocolLocator.first()).toBeVisible()` for real protocol |
| `verify run history starts empty` | `expect(emptyState.first()).toBeVisible()`; `expect(...getByText('MOCK-RUN-001')).not.toBeVisible()` |
| `verify home dashboard has no mock runs` | `expect(getByText('No recent activity')).toBeVisible()`; 3× `expect(...).not.toBeVisible()` for mock run names |

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

| Issue | Location | Severity | Details |
|-------|----------|----------|---------|
| **Mixed Locator Strategies** | Lines 34, 43 | Medium | Uses implementation-detail CSS class `.protocol-card` alongside `getByText()`. Inconsistent approach creates maintenance burden. |
| **Fragile Multi-Selector Fallback** | Line 43 | High | The locator `.empty-runs-state, .no-runs-message, :text("No Runs Yet")` chains three unrelated selectors. If DOM changes, this becomes difficult to debug. |
| **No Fixture for Database Isolation** | Lines 9–11 | Medium | Uses raw `page.goto('/?resetdb=1')` instead of the established `worker-db.fixture` pattern. This breaks parallel execution. |
| **No Explicit Test Isolation** | N/A | Medium | No `afterEach` cleanup. Tests assume `resetdb=1` is sufficient, but shared OPFS could still cause flakiness. |
| **Hardcoded String Literals** | Lines 20–24, 58–62 | Low | Mock protocol/run names are duplicated as string arrays. Should be constants or auto-discovered. |
| **Missing Simulation Mode Check** | Line 17 | Low | Calls `ensureSimulationMode()` which is good, but other tests don't. Could be a fixture concern. |

### Modern Standards (2026) Evaluation

| Criterion | Status | Notes |
|-----------|--------|-------|
| **User-Facing Locators** | ⚠️ Mixed | Uses `getByRole('button')` and `getByText()` (good), but also raw CSS selectors `.protocol-card` and `.empty-runs-state` (bad). |
| **Test Isolation** | ❌ Weak | Does not use `worker-db.fixture`. Cannot run in parallel without contention. |
| **Page Object Model (POM)** | ✅ Good | Correctly uses `WelcomePage`, `ProtocolPage`, `ExecutionMonitorPage`. However, inline locators in tests (lines 34, 43, 55) should be moved to POMs. |
| **Async Angular Handling** | ⚠️ Moderate | Uses POM `waitFor` methods, but doesn't wait for Angular signals or route resolution; relies on DOM visibility only. |

---

## 3. Test Value & Classification

### Scenario Relevance
**Classification: Regression Guard (Meta-Test)**

This is **not** a Happy Path user journey. It is a **regression guard** that verifies old mock data was removed after a cleanup effort. It represents a **one-time verification** scenario that was likely added during a data hygiene sprint.

**Real User Relevance:** Low. A real user never checks "are mock protocols absent?" This is developer-facing verification.

### Classification
| Type | Verdict |
|------|---------|
| **True E2E Test** | ✅ Partial — It loads the app in browser mode with SQLite and verifies state. |
| **Interactive Unit Test** | ❌ No — Does not mock; checks real seeded database. |
| **Regression Guard** | ✅ Primary — Guards against reintroduction of removed mock data. |

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

```
Test 1: Mock Protocols Absent
1. Navigate to root with `?resetdb=1` (forces fresh database)
2. Handle splash screen (tutorial skip)
3. Navigate to Protocol page (/app/run)
4. Ensure simulation mode is active
5. Assert: "Daily System Maintenance", "Cell Culture Feed", "Evening Shutdown" NOT visible
6. Assert: At least one `.protocol-card` IS visible

Test 2: Run History Empty
1. (Same db reset from beforeEach)
2. Navigate to /app/monitor history view
3. Assert: Empty state indicator visible
4. Assert: "MOCK-RUN-001" NOT visible

Test 3: Home Dashboard Clean
1. Navigate to /app/home
2. Assert: "No recent activity" visible
3. Assert: Mock run names NOT visible
```

### Contextual Fit
This spec fits into the **database schema/seed evolution** layer of the test pyramid. When the team removed placeholder data from the seeding scripts, this test was added to prevent regression. It is orthogonal to user journeys but critical for data integrity.

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Description | Impact |
|-----|-------------|--------|
| **No Positive Real Protocol Validation** | Asserts "a card exists" but doesn't verify the card contains expected real data (e.g., `PCR Prep` by name). | Could pass with garbage data. |
| **No Database Query Verification** | Only checks UI. SQLite could still contain mock records invisible in UI. | Silent data pollution possible. |
| **No Parallel Safety** | Missing worker-indexed DB fixture. Will fail or flake under `--workers=4`. | Cannot scale. |
| **No Cleanup Verification** | Doesn't confirm that old mock rows were deleted from `protocols` or `runs` tables. | Regression could hide in backend. |

### Domain Specifics

| Domain Aspect | Status | Recommendation |
|---------------|--------|----------------|
| **Data Integrity** | ❌ Not Verified | Should use `page.evaluate()` to query SQLite directly: `SELECT * FROM protocols WHERE name LIKE 'Daily%'` returning 0 rows. |
| **Simulation vs. Reality** | ✅ Addressed | `ensureSimulationMode()` is called, indicating awareness of simulation toggle. |
| **Serialization** | N/A | Not applicable — no protocol execution occurs. |
| **Error Handling** | ❌ Missing | No negative cases (e.g., what happens if `resetdb=1` fails? What if seed script throws?). |

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 6/10 | Covers absence checks well; lacks positive verification |
| **Best Practices** | 5/10 | POM usage good, but isolation/locator strategies weak |
| **Test Value** | 5/10 | Regression guard; not a user journey; one-time value |
| **Isolation** | 4/10 | No worker-indexed fixture; parallel-unsafe |
| **Domain Coverage** | 4/10 | UI-only; no SQLite query verification |

**Overall**: **4.8/10**
