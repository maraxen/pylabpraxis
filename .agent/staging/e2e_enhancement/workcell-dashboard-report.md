# SDET Static Analysis: workcell-dashboard.spec.ts

**Target File:** [workcell-dashboard.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/workcell-dashboard.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested
This spec file tests the **Workcell Dashboard** feature—a central operational view displaying machine inventory and real-time status. The tests verify:

| Test | Functionality Verified |
|------|------------------------|
| `should load the dashboard page` | Dashboard loads with correct `<h1>` title text |
| `should display explorer sidebar` | `<app-workcell-explorer>` component renders with a search input |
| `should display machine cards when machines exist` | `<app-machine-card>` elements appear OR an empty "No machines found" state |
| `should navigate to machine focus view on card click` | Clicking a machine card opens `<app-machine-focus-view>` |
| `should show deck visualization in focus view when available` | Focus view may contain deck/canvas visualization components |

### Assertions (Success Criteria)
- **Page title** contains "Workcell Dashboard"
- **Sidebar component** (`app-workcell-explorer`) is visible with a text input for search
- **Machine cards** OR empty state message are visible
- **Focus view navigation** succeeds after card click
- **Deck visualization** presence is *logged* (informational, not asserted)

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

| Issue | Location | Severity | Description |
|-------|----------|----------|-------------|
| **Direct window access** | L9-16 (`waitForFunction`) | 🔴 High | Relies on `window.sqliteService.isReady$?.getValue()` — tightly couples test to internal Angular service implementation. If service is renamed or `isReady$` becomes a Signal, tests break. |
| **CSS class selector for loading** | L19 (`.animate-spin`) | 🟡 Medium | Not user-facing; relies on Tailwind utility class. Vulnerable to CSS framework changes. |
| **Component tag selectors** | L30, 38, 71, 89, 92 | 🟡 Medium | Uses `app-*` component tags which are implementation details, not user-facing. |
| **Text matching for empty state** | L39 (`text=No machines found`) | 🟢 Low | Acceptable as user-visible copy, but may break with i18n changes. |
| **Screenshot side effects** | L25, 48, 52, 72, 95 | ⚪ Info | Screenshots to `/tmp/e2e-workcell/` accumulate across runs without cleanup. |
| **Conditional logic in tests** | L45-53, L61-64, L80-83, L93-98 | 🟡 Medium | Tests contain branching logic for presence/absence of machines. This makes the test outcome unpredictable and reduces value. |
| **`test.skip()` inside test body** | L63, L81 | 🟡 Medium | Dynamic skipping inside test body is an anti-pattern. Should use `test.skip` annotation or fixture-based skip logic. |

### Modern Standards (2026) Evaluation

| Criterion | Status | Notes |
|-----------|--------|-------|
| **User-Facing Locators** | ❌ Poor | Heavy reliance on component selectors (`app-*`), CSS classes (`.animate-spin`), and internal `<h1>` tags. Should use `getByRole('heading')`, `getByRole('searchbox')`, `getByRole('listitem')`. |
| **Test Isolation** | ⚠️ Partial | Uses `app.fixture.ts` with worker-indexed DB isolation (`dbName=praxis-worker-{index}`), which is excellent. However, the test navigates with hardcoded `/app/workcell?mode=browser` instead of using `buildIsolatedUrl()` from the fixture. This **bypasses DB isolation**. |
| **Page Object Model (POM)** | ❌ Missing | No `workcell.page.ts` exists. All selectors are inline, creating duplication risk across specs and maintenance burden. |
| **Async Angular Handling** | ⚠️ Mixed | Good: Waits for `sqliteService.isReady$`. Bad: Still uses `waitForTimeout(300)` is avoided here but `page.waitForFunction()` coupled to internal BehaviorSubject is fragile. Should use Angular-aware matchers or stability signals. |

---

## 3. Test Value & Classification

### Scenario Relevance
**Happy Path with Conditional Fallbacks.** These tests cover the primary "load and view machines" workflow, which is a **critical user journey** for lab operators. However, the conditional logic ("if machines exist... else...") weakens the test value because:
1. Pass/fail outcome depends on database state
2. "Empty state" path is tested opportunistically, not intentionally
3. No setup creates machines, so coverage is accidental

### Classification
| Type | Assessment |
|------|------------|
| **True E2E** | ⚠️ Partial — Tests against real Angular app with live SQLite OPFS, but... |
| **Isolation Issue** | ❌ **Critical Flaw**: Test navigates to `/app/workcell?mode=browser` without `dbName` parameter, meaning it does NOT use the worker-isolated database set up by the fixture. All workers share the same default database, causing potential race conditions. |

**Verdict:** This is a **flawed E2E test** due to the isolation gap. The fixture sets up `praxis-worker-{index}` DB, but the test ignores it.

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

```
1. User navigates to /app/workcell (Workcell Dashboard)
2. System initializes SQLite OPFS database 
3. User sees loading spinner → resolves
4. Dashboard header "Workcell Dashboard" appears
5. Left sidebar shows WorkcellExplorer with search input
6. Main content area shows:
   a. Machine cards (if machines exist) → User clicks card → Focus view opens
   b. OR Empty state message "No machines found"
7. Focus view may display deck/canvas visualization for liquid handlers
```

### Contextual Fit

The **Workcell Dashboard** is the operational control center for lab automation:
- **Role**: Real-time monitoring of connected/simulated lab instruments
- **Ecosystem Position**: Entry point after asset creation (from Asset Wizard)
- **Dependencies**: 
  - `SqliteService` for persistence
  - `WorkcellViewService` for machine runtime state
  - `MachineCard` / `MachineFocusView` / `DeckState` components
- **Downstream**: Clicking a machine leads to protocol execution context

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Severity | Description |
|-----|----------|-------------|
| **No machine seeding** | 🔴 Critical | Tests don't create machines before running. Relies on pre-existing DB state, making tests non-deterministic. |
| **No DB isolation in navigation** | 🔴 Critical | Uses wrong URL pattern; bypasses fixture's DB isolation. |
| **No search/filter testing** | 🟡 Medium | Explorer has search input but it's never typed into or validated. |
| **No view mode switching** | 🟡 Medium | Component has `grid`, `list`, `focus` modes but only one path is tested. |
| **No error state testing** | 🟡 Medium | What if DB fails to load? Service errors? Network issues? |
| **Deck visualization is informational only** | 🟡 Medium | L98 logs whether deck is found but doesn't assert expected behavior. |

### Domain Specifics

| Domain Concern | Coverage | Assessment |
|----------------|----------|------------|
| **Data Integrity** | ❌ Not covered | No validation that machine records are correctly loaded from SQLite. Test just checks if `app-machine-card` is visible—could be an empty card. |
| **Simulation vs. Reality** | ❌ Not covered | No verification that machines are marked as "simulated" vs. "connected". The `MachineWithRuntime` model has runtime state that's never asserted. |
| **Serialization** | ❌ Not applicable | This spec doesn't involve protocol execution or Pyodide communication. |
| **Error Handling** | ❌ Not covered | No tests for: DB initialization failure, malformed machine records, service subscription errors. |

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 4/10 | Covers basic visibility checks but no functional depth |
| **Best Practices** | 3/10 | No POM, component selectors, DB isolation bypassed |
| **Test Value** | 4/10 | Happy path with conditional fallbacks reduces determinism |
| **Isolation** | 3/10 | Fixture provides isolation but test ignores it |
| **Domain Coverage** | 2/10 | No data integrity, no error states, no state verification |

**Overall**: **3.2/10**

---

## Recommended Actions (Priority Order)

1. **🔴 Fix DB Isolation** - Change `goto('/app/workcell?mode=browser')` to use `buildIsolatedUrl('/app/workcell', testInfo)` or equivalent
2. **🔴 Seed Test Data** - Create a machine via API/fixture before testing machine-dependent flows
3. **🟡 Create WorkcellPage POM** - Encapsulate selectors and common actions
4. **🟡 Replace Component Selectors** - Use `getByRole`, `getByTestId` where component tags are unavoidable
5. **🟡 Remove Conditional Logic** - Split into separate test blocks: one for populated state, one for empty state
6. **🟢 Add Error State Tests** - Simulate DB failures, network issues
7. **🟢 Add Search/Filter Tests** - Type in explorer search, verify filtering
