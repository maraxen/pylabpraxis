# SDET Static Analysis: 02-asset-management.spec.ts

**Target File:** [02-asset-management.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/02-asset-management.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested

This test file exercises the **Asset Management** module in **Browser Mode**, specifically:

| #   | Scope                    | Details                                                                                      |
| --- | ------------------------ | -------------------------------------------------------------------------------------------- |
| 1   | **Navigation**           | Routing to `/assets` page, visibility of four tab headers (Overview, Machines, Resources, Registry) |
| 2   | **Tab Switching**        | Sequential navigation between all four tabs with `aria-selected` state verification         |
| 3   | **Add Machine Dialog**   | Opening dialog via button click, verifying title/heading, step indicator, Cancel button dismissal |
| 4   | **Add Resource Dialog**  | Opening dialog via button click, verifying title, search input presence, close via `mat-dialog-close` |
| 5   | **CRUD – Create Machine**| Full wizard flow: Category → Frontend → Backend → Config → Review → Create                  |
| 6   | **CRUD – Create Resource**| Full wizard flow: Category → Search/Select Definition → Config → Create                    |
| 7   | **CRUD – Delete Machine**| Create → verify visible → delete → verify not visible                                       |
| 8   | **Persistence**          | Create machine → page reload → verify asset still visible                                   |

**UI Elements Verified:**
- Tab buttons (`mat-tab*`)
- Action buttons ("Add Machine", "Add Resource", "Cancel")
- Wizard stepper headings (`h3` in Material Stepper)
- Search placeholder input
- Dialog presence/absence (`getByRole('dialog')`)
- Table rows containing created asset names

**State Changes Verified:**
- Tab selection state (`aria-selected='true'`)
- Dialog visibility (open/close)
- Asset list content changes (creation/deletion)
- SQLite persistence across page reloads

### Assertions (Success Criteria)

| Assertion Pattern                    | Usage Count | Purpose                                    |
| ------------------------------------ | ----------- | ------------------------------------------ |
| `toBeVisible()`                      | 18          | Primary visibility checks for elements     |
| `not.toBeVisible()`                  | 4           | Dialog dismissal, element removal          |
| `toHaveAttribute('aria-selected')`   | 5           | Tab activation verification                |
| `toHaveClass(/selected/)`            | Indirect*   | Wizard card selection (in POM)             |
| `toBeEnabled()`                      | Indirect*   | Button interactability (in POM)            |

*"Indirect" = assertion logic encapsulated in `AssetsPage` POM methods.

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

#### 🔴 Critical Issues

| Issue | Location | Description |
|-------|----------|-------------|
| **Hardcoded timeout** | Line 111 | `page.waitForTimeout(500)` is a brittle anti-pattern. The test waits for "content to load" without any condition to check. This timer may be insufficient under load or waste time in fast runs. |
| **Inconsistent cleanup** | Entire file | No `afterEach` hook exists. Tests in the CRUD block create assets that persist across tests. The `deleteMachine` test creates then deletes, but `createMachine`, `createResource`, and `persistMachine` leave artifacts. |
| **No isolation via Fixtures** | `beforeEach` | Tests use plain `test()` without leveraging Playwright Fixtures for service readiness or database state reset. The `BasePage.goto()` *does* append `resetdb=1`, but this is not leveraged for CRUD isolation. |
| **Timestamp-based naming collision risk** | Lines 118, 127, 136, 147 | Using `Date.now()` provides "unique" names but can collide if two tests run in the same millisecond (parallel workers). Additionally, artifacts accumulate if persistence test fails mid-run. |

#### 🟡 Moderate Concerns

| Issue | Location | Description |
|-------|----------|-------------|
| **Defensive timeouts in POM** | `assets.page.ts:50, 60, 76` | The POM uses `waitForTimeout(100)`, `waitForTimeout(150)`, and `waitForTimeout(50)` to "wait for animations". While necessary for Material Stepper quirks, these should be documented as technical debt with a TODO to replace with animation completion detection. |
| **Mixed locator strategies in POM** | `assets.page.ts:197-199` | `deleteMachine()` uses both `getByRole` and `locator('button[mattooltip*="Delete"]')` as fallback. The attribute selector depends on Angular implementation details that may change. |
| **Silent warning in assertion** | `assets.page.ts:324-326` | `verifyAssetVisible` logs a warning instead of failing if the asset isn't found. This weakens test reliability—verification should fail explicitly. |
| **Dialog close uses `.or()`** | Line 78 | `page.locator('button[mat-dialog-close]').or(...)` is good defensive coding, but indicates unstable UI patterns across dialogs. |

### Modern Standards (2026) Evaluation

#### ✅ User-Facing Locators

**Excellent use of semantic locators:**
```typescript
// Good examples from assets.page.ts
this.addMachineButton = page.getByRole('button', { name: /Add Machine/i });
this.machinesTab = page.getByRole('tab', { name: /Machines/i });
page.getByRole('heading', { name: /Add New Machine/i })
page.getByPlaceholder(/Search resources/i)
```

**Minor violations:**
- `page.locator('button[mat-dialog-close]')` — CSS attribute selector
- `page.locator('.cdk-overlay-backdrop')` — CSS class for framework internals
- `wizard.locator('[data-testid^="backend-card-"]').first()` — `data-testid` is acceptable, but `.first()` is non-deterministic

**Score: 8/10** — Strong adherence with minor framework-specific exceptions.

#### 🟡 Test Isolation

| Aspect | Status | Notes |
|--------|--------|-------|
| Fresh browser context | ✅ | Playwright default behavior |
| Database reset | ⚠️ | `resetdb=1` in URL, but not verified; CRUD tests accumulate state |
| No `afterEach` cleanup | ❌ | Created assets persist between tests |
| Worker-indexed DB | ✅ | `BasePage` supports `dbName=praxis-worker-N`, but **not utilized** (no `testInfo` passed to constructors in this spec) |

**Score: 5/10** — Isolation infrastructure exists but isn't leveraged.

#### ✅ Page Object Model (POM)

**Strengths:**
- Clean abstraction of wizard flows (`createMachine`, `createResource`)
- Helper methods for overlay management (`waitForOverlaysToDismiss`)
- Proper encapsulation of Material Stepper transition logic
- Deprecated methods marked with `@deprecated` annotations

**Weaknesses:**
- `verifyAssetVisible` navigates to Registry tab implicitly—side effect is hidden from test code
- No return values from verification methods; all assertions are side-effects
- Two competing verification approaches: search + text presence vs. row visibility

**Score: 7/10** — Well-structured with room for improvement in method contracts.

#### ⚠️ Async Angular Handling

| Pattern | Implementation | Assessment |
|---------|----------------|------------|
| SQLite readiness | `waitForFunction` on `sqliteService.isReady$` | ✅ Excellent |
| Tab selection | `toHaveAttribute('aria-selected')` polling | ✅ Correct |
| Dialog appearance | `toBeVisible({ timeout: 5000 })` | ✅ Adequate |
| Wizard step transitions | Explicit `waitForTimeout` + heading visibility | ⚠️ Works but fragile |
| Animation completion | Hardcoded `150ms` delay | ❌ Should use `animationend` events |

**Score: 6/10** — Core async patterns are correct; animation handling is suboptimal.

---

## 3. Test Value & Classification

### Scenario Relevance

**Critical User Journey: ✅ YES**

This test covers the **core asset management workflow**—the foundational capability users need before they can execute protocols. The hierarchy of tested actions:

1. **Navigation** → Prerequisite for all asset operations
2. **Viewing assets** → User's starting point
3. **Adding machines/resources** → Essential setup for lab automation
4. **Deleting assets** → Lifecycle management
5. **Persistence** → Data integrity guarantee

**Real-World Fidelity:** The CRUD operations closely mirror what a lab operator would perform:
- "I need to add my Hamilton STAR liquid handler"
- "I need to add a 96-well plate"
- "I need to remove an old machine"

**Edge Cases Covered:** Minimal. No tests for:
- Invalid inputs
- Duplicate names
- Concurrent modifications
- Large asset lists (pagination)

### Classification

| Classification | Assessment |
|----------------|------------|
| **True E2E Test** | ✅ **YES** |
| **Interactive Unit Test** | ❌ NO |

**Rationale:**
- Tests run against a **live Angular application served by `npm run start:browser`**
- Uses **real OPFS-backed SQLite database** (browser mode)
- No network mocking—database operations go through the full service layer
- Wizard flows exercise complete component trees (Stepper + Cards + Forms + Dialog management)

**However:** There is no *backend server* involved. This is browser-mode testing against a client-side SQLite store. It's E2E within the **frontend stack** but doesn't validate server synchronization.

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

```
SCENARIO: Lab Manager Onboarding Asset Setup

GIVEN: User has completed initial splash screen
AND: Application is in browser mode with seeded PLR definitions

Test 1: Verify Assets Page Navigation
  1. User navigates to /assets
  2. User sees four tabs: Overview, Machines, Resources, Registry
  → SUCCESS: All tab headers are visible

Test 2: Explore Add Machine Dialog
  1. User clicks "Add Machine" button
  2. User sees dialog titled "Add New Machine"
  3. User sees first step "Select Machine Category"
  4. User clicks Cancel to dismiss
  → SUCCESS: Dialog closes cleanly

Test 3: Explore Add Resource Dialog
  1. User clicks "Add Resource" button
  2. User sees dialog titled "Add Resource"
  3. User sees search input for resources
  4. User clicks close button
  → SUCCESS: Dialog closes cleanly

Test 4: Navigate Between Tabs
  1. User clicks Machines tab → activated
  2. User clicks Resources tab → activated
  3. User clicks Registry tab → activated
  4. User clicks Overview tab → activated
  → SUCCESS: Tab navigation works bidirectionally

Test 5: (Stub) Search Resources
  1. User navigates to Resources tab
  2. (Incomplete: just waits 500ms)
  → SUCCESS: No assertion, just loads

Test 6: Create Machine via Wizard
  1. User navigates to Machines tab
  2. User clicks "Add Machine"
  3. User selects category: LiquidHandler
  4. User selects frontend: (first available)
  5. User selects driver: (first available)
  6. User enters name: "Test Machine {timestamp}"
  7. User confirms on Review step
  → SUCCESS: Machine appears in Registry

Test 7: Create Resource via Wizard
  1. User navigates to Resources tab
  2. User clicks "Add Resource"
  3. User selects category: Plate
  4. User searches for "96" and selects first result
  5. User enters name: "Test Resource {timestamp}"
  6. User confirms
  → SUCCESS: Resource appears in Registry

Test 8: Delete Machine
  1. User creates a machine via wizard
  2. User locates machine row in table
  3. User clicks delete button (or context menu)
  4. User confirms browser dialog
  → SUCCESS: Machine no longer visible

Test 9: Persistence Across Reload
  1. User creates a machine
  2. User reloads the page
  3. User navigates to Machines tab
  → SUCCESS: Machine still visible (OPFS-backed SQLite persisted)
```

### Contextual Fit

This component is a **prerequisite gate** in the application flow:

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│   Onboarding │ ──▶ │  Asset Management │ ──▶ │  Protocol Execution │
│   (01-*)     │     │  (02-*)          │     │  (03-*)             │
└──────────────┘     └──────────────────┘     └─────────────────────┘
                            │
                            ▼
                     ┌────────────────┐
                     │ Browser SQLite │
                     │ (OPFS Backend) │
                     └────────────────┘
```

**Dependencies:**
- **Upstream:** `01-onboarding.spec.ts` must pass (app loads)
- **Downstream:** `03-protocol-execution.spec.ts` needs machines/resources to exist

**Database State:** Tests depend on "seeded PLR definitions" (as noted in comment line 9). The wizard card selection relies on these definitions existing.

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap Category | Missing Scenario | Risk Level |
|--------------|------------------|------------|
| **Validation** | No test for empty name submission | 🔴 High |
| **Validation** | No test for duplicate asset names | 🔴 High |
| **Validation** | No test for special characters in names | 🟡 Medium |
| **Error States** | No test for wizard cancellation mid-flow | 🟡 Medium |
| **Error States** | No test for database write failures | 🔴 High |
| **Concurrency** | No test for parallel wizard instances | 🟡 Medium |
| **Edge Cases** | No test for editing existing assets | 🟡 Medium |
| **Edge Cases** | No test for pagination/scrolling in large lists | 🟡 Medium |
| **Filtering** | No assertion on category filter behavior | 🟡 Medium |
| **Search** | No assertion on search functionality | 🟡 Medium |

### Domain Specifics

#### 🔴 Data Integrity

**Current State:**
- Tests verify assets are "visible" by searching Registry tab
- `verifyAssetVisible()` uses text matching, not structured verification
- No validation of asset **properties** (category, definition, configuration)

**Missing Verification:**
```typescript
// What's tested:
await assetsPage.verifyAssetVisible(machineName);

// What's NOT tested:
await assetsPage.verifyMachineProperties({
  name: machineName,
  category: 'LiquidHandler',
  frontend: 'HamiltonSTAR',
  driver: 'HamiltonVenusBridge'
});
```

**Risk:** Asset could be created with wrong category/definition and test would pass.

#### 🟡 Simulation vs. Reality

**Current State:**
- Tests run in **browser mode** with OPFS-backed SQLite
- No backend server connectivity tested
- Wizard uses "seeded PLR definitions" — seed integrity is assumed

**Questions Unanswered:**
1. Are the seeded definitions complete? (No validation)
2. Does machine creation generate valid Python-compatible configuration?
3. Are created assets compatible with protocol execution?

**Recommendation:** Add a "round-trip" test that creates an asset, then uses it in a protocol context.

#### 🔴 Serialization

**Critical Gap:** The test does NOT verify:
- Asset configuration is correctly serialized to SQLite
- Retrieved assets match inserted data
- Machine/Resource can be serialized for Python worker consumption

The `createMachine` flow ends with wizard dismissal. There's no:
```typescript
// Missing verification
const savedMachine = await page.evaluate(() => 
  window.sqliteService.getMachine(id)
);
expect(savedMachine.config).toMatchObject({ ... });
```

#### 🔴 Error Handling

**0% Coverage of Failure States:**

| Scenario | Coverage |
|----------|----------|
| Network failure during save | ❌ Not tested |
| SQLite OPFS write failure | ❌ Not tested |
| Invalid form submission | ❌ Not tested |
| Missing required fields | ❌ Not tested |
| Wizard back navigation | ❌ Not tested |
| Browser dialog rejection on delete | ❌ Not tested |

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 7/10 | Covers primary CRUD flows; missing validation and edge cases |
| **Best Practices** | 6/10 | Good locators, weak isolation, hardcoded waits |
| **Test Value** | 8/10 | Critical user journey; true E2E within frontend stack |
| **Isolation** | 4/10 | Worker DB exists but unused; no cleanup hooks |
| **Domain Coverage** | 4/10 | No serialization, data integrity, or error path testing |

**Overall**: **5.8/10**

---

## Recommendations Summary

### Priority 1: Critical (Implement Immediately)

1. **Enable Worker-Indexed DB Isolation**
   - Pass `testInfo` to `WelcomePage` and `AssetsPage` constructors
   - Prevents parallel test interference

2. **Add `afterEach` Cleanup**
   - Delete created assets or use unique worker-scoped DB reset

3. **Replace `waitForTimeout(500)`** (Line 111)
   - Wait for a specific UI condition or remove the no-op test

### Priority 2: Important (Next Sprint)

4. **Add Data Integrity Verification**
   - After creation, query SQLite directly and verify properties

5. **Add Validation Error Tests**
   - Empty name, duplicate name, invalid configuration

6. **Add Delete Confirmation Rejection Test**
   - Verify asset remains when user cancels delete dialog

### Priority 3: Enhancement (Backlog)

7. **Add Protocol Integration Smoke Test**
   - Create asset → Use in protocol config → Verify serialization

8. **Convert Timeout Waits to Animation Listeners**
   - Reduce flakiness and test execution time
