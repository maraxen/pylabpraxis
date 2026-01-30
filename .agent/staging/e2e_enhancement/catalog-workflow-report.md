# SDET Static Analysis: catalog-workflow.spec.ts

**Target File:** [catalog-workflow.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/catalog-workflow.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested
This test file validates the **Catalog to Inventory Workflow**, specifically:

1. **Catalog Tab Visibility**: Confirms the "Catalog" tab is present and rendered in the Inventory Dialog
2. **Default Tab Selection**: Verifies the Catalog tab is auto-selected (aria-selected="true") when inventory is empty
3. **Machine Definition Display**: Checks that at least one machine catalog definition (mat-card-title) is visible
4. **"Add Simulated" Action**: Clicking "Add Simulated" button on a catalog definition
5. **Tab Navigation Side-Effect**: After adding a simulated machine, verifies the UI switches to the "Browse & Add" tab (tab index 2)

### Assertions (Success Criteria)

| Assertion | Type | Purpose |
|-----------|------|---------|
| `page.getByRole('tab', { name: 'Catalog' }).toBeVisible()` | Presence | Catalog tab rendered |
| `Catalog tab.toHaveAttribute('aria-selected', 'true')` | State | Default selection verification |
| `mat-card-title.first().toBeVisible()` | Content | At least one catalog item rendered |
| `'Browse & Add' tab.toHaveAttribute('aria-selected', 'true')` | Navigation | Tab switch after action |

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

#### 🔴 Critical Issues

1. **No Worker-Indexed DB Isolation (Lines 7-13)**
   ```typescript
   await page.goto('/app/playground?resetdb=1');
   ```
   - **Problem**: Uses direct `page.goto()` without worker-indexed database isolation
   - **Impact**: Will fail or cause flaky behavior when running with `--workers > 1` due to OPFS race conditions
   - **Fix**: Import and use `gotoWithWorkerDb()` from `worker-db.fixture.ts` or extend from `BasePage`

2. **Brittle `try-catch` Pattern for Onboarding (Lines 18-24)**
   ```typescript
   try {
       await skipBtn.waitFor({ state: 'visible', timeout: 5000 });
       await skipBtn.click();
   } catch (e) {
       // Not present, continue
   }
   ```
   - **Problem**: Uses exception handling for control flow, which is an anti-pattern
   - **Impact**: Slow (always waits 5s when splash isn't shown); hides real errors
   - **Fix**: Use Playwright's conditional patterns or a proper `if/else` with `isVisible()`

3. **Hardcoded `mat-card-title` Selector (Lines 39-40)**
   ```typescript
   await page.locator('mat-card-title').first().waitFor({ state: 'visible', timeout: 15000 });
   ```
   - **Problem**: Uses Angular Material implementation detail (`mat-card-title`) instead of user-facing locator
   - **Impact**: Brittle if Angular Material version changes or component markup evolves
   - **Fix**: Use `getByRole('heading')` or add `data-testid` for catalog item titles

#### 🟡 Warnings

4. **Incomplete "Add Simulated" Workflow Verification (Line 43)**
   - Only clicks the button and checks tab switch
   - Does NOT verify:
     - The simulated machine was actually created
     - The machine name/type is correct
     - The machine appears in the inventory

5. **Excessive Code Comments About Internal Tab Indices (Lines 45-54)**
   - Comments explain tab index logic extensively, indicating fragile implementation coupling
   - Tests should verify *behavior*, not internal index assignments

### Modern Standards (2026) Evaluation

| Category | Score | Assessment |
|----------|-------|------------|
| **User-Facing Locators** | 5/10 | Mixed: Uses `getByRole` and `getByLabel` correctly for tabs/buttons, but falls back to `locator('mat-card-title')` for content |
| **Test Isolation** | 2/10 | **Critical Gap**: No worker-indexed DB; uses global `resetdb=1` which conflicts in parallel execution |
| **Page Object Model (POM)** | 1/10 | **Not used at all**: All logic is inline in the test file. No abstraction for Inventory Dialog or Catalog reusability |
| **Async Angular Handling** | 6/10 | Uses `waitForFunction` correctly for SQLite readiness, but catalog item wait uses hardcoded 15s timeout instead of state-driven assertion |

---

## 3. Test Value & Classification

### Scenario Relevance

**Medium-High Relevance**: This tests a critical user journey for lab operators:
- Adding simulated/virtual machines to the inventory is essential for:
  - Offline development without physical lab hardware
  - Protocol testing before live execution
  - Training new users

**However**, the test is incomplete—it only verifies UI navigation, not the actual result of adding a machine.

### Classification

**Interactive Unit Test (Border Case)**

Reasoning:
- ✅ Tests real UI components in a real browser
- ✅ Uses real Angular application
- ✅ Triggers real SQLite database via `resetdb=1`
- ❌ Does NOT verify the machine was persisted to SQLite
- ❌ Does NOT verify machine appears in "Current Items" (final inventory state)
- ❌ Does NOT reload the page to confirm persistence

**Upgrade Path**: Add a final assertion that:
1. Switches to "Current Items" tab
2. Verifies the simulated machine appears
3. Optionally: Navigates away and back to confirm persistence

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    CATALOG TO INVENTORY FLOW                     │
└─────────────────────────────────────────────────────────────────┘

1. Navigate to Playground (/app/playground?resetdb=1)
   └── Wait for SQLite database to initialize (30s timeout)

2. Handle Onboarding Splash (if present)
   └── Click "Skip" button to dismiss

3. Open Inventory Dialog
   └── Click element with aria-label "Open Inventory Dialog"

4. Verify Catalog Tab UI State
   ├── Assert "Catalog" tab is visible
   └── Assert "Catalog" tab is selected (aria-selected="true")

5. Verify Catalog Content Loaded
   └── Wait for first `mat-card-title` to be visible (15s)

6. Trigger "Add Simulated" Action
   └── Click first "Add Simulated" button

7. Verify Navigation Side-Effect
   └── Assert "Browse & Add" tab is now selected
```

### Contextual Fit

**Role in Application Ecosystem:**

```
┌───────────────────────────────────────────────────────────────┐
│               PRAXIS MACHINE MANAGEMENT FLOW                   │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  CATALOG (This Test)              INVENTORY                   │
│  ┌─────────────────┐       ┌─────────────────────────────┐   │
│  │ Machine Defs    │──────▶│ Workspace Machines          │   │
│  │ (Read-Only)     │       │ (User-Owned Instances)      │   │
│  │                 │       │                             │   │
│  │ • OT-2          │       │ • "My OT-2" (192.168.1.10)  │   │
│  │ • Flex          │       │ • "Simulation-1" (virtual)  │   │
│  │ • Chatterbox    │       │                             │   │
│  └─────────────────┘       └─────────────────────────────┘   │
│                                       │                       │
│                                       ▼                       │
│                            ┌─────────────────────────────┐   │
│                            │ PROTOCOL EXECUTION          │   │
│                            │ (Select machine from inv)   │   │
│                            └─────────────────────────────┘   │
└───────────────────────────────────────────────────────────────┘
```

This test validates the **entry point** of the machine provisioning flow but does not verify the **exit state** (machine in inventory) or downstream usability (machine selectable in protocols).

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Severity | Description |
|-----|----------|-------------|
| **No Machine Creation Verification** | 🔴 Critical | After clicking "Add Simulated", no assertion verifies the machine was actually created |
| **No Persistence Check** | 🔴 Critical | SQLite database state is never validated |
| **No "Current Items" Tab Check** | 🟡 High | Should verify machine appears in final inventory list |
| **No Cross-Tab State** | 🟡 High | Doesn't verify "Browse & Add" tab receives the correct type/category context |
| **No Error State Testing** | 🟡 Medium | What if catalog loading fails? No error handling coverage |
| **No Multiple Machine Types** | 🟢 Low | Only tests one definition (first); doesn't verify different machine types |

### Domain Specifics

#### Data Integrity
- **Database Validation**: ❌ **Not Tested**
  - The test uses `waitForFunction` to confirm SQLite is *ready*, but never verifies:
    - Machine definition data loaded correctly into catalog
    - Created machine persisted to `machines` table
    - Machine configuration/simulation flags stored correctly

- **Catalog Data Source**: Unknown
  - Are catalog definitions loaded from SQLite? Static JSON? API?
  - No validation of catalog item structure/schema

#### Simulation vs. Reality
- ✅ **Correctly Uses Simulated Environment**: The test explicitly targets simulated machine creation
- ❌ **No Simulation Configuration Verification**:
  - When adding a simulated machine, parameters may need configuration
  - The `WizardPage.handleConfigureSimulationDialog()` pattern exists but isn't used here

#### Serialization
- ❌ **Not Applicable to This Test**
  - This test doesn't involve Pyodide or protocol parameter serialization
  - However, if adding a simulated machine triggers background worker initialization, that state should be verified

#### Error Handling
- ❌ **No Negative Test Cases**:
  - What happens if catalog definitions fail to load?
  - What if "Add Simulated" fails due to pre-existing machine with same name?
  - What if SQLite write fails?

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 4/10 | Tests navigation but misses outcome verification |
| **Best Practices** | 3/10 | No POM, no worker isolation, brittle selectors |
| **Test Value** | 5/10 | Medium value—core flow but incomplete assertion |
| **Isolation** | 2/10 | **Critical**: Will fail in parallel execution |
| **Domain Coverage** | 2/10 | No data integrity, persistence, or error handling |

**Overall**: **3.2/10**

---

## Recommended Priority Actions

1. **[P0] Add worker-indexed DB fixture** to enable parallel execution
2. **[P0] Verify machine creation outcome** in "Current Items" tab
3. **[P1] Extract Inventory Dialog POM** for reusability
4. **[P1] Replace `mat-card-title` with user-facing locator**
5. **[P2] Add SQLite state verification** using `page.evaluate()`
6. **[P2] Add error state test case** for failed catalog load
