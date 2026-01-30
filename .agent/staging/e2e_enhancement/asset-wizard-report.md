# SDET Static Analysis: asset-wizard.spec.ts

**Target File:** [asset-wizard.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/asset-wizard.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested
This test file verifies the **Asset Wizard Happy Path** for creating a new **Hamilton STAR** liquid handler machine. It tests the multi-step wizard workflow from navigating to the assets page through completing asset creation. Specifically:

1. **Navigation & Initialization**: Navigates to `/assets` with `resetdb=1` and waits for SQLite service readiness.
2. **Welcome Dialog Dismissal**: Attempts to close any welcome/onboarding modal.
3. **Wizard Invocation**: Opens the Asset Wizard via `[data-tour-id="add-asset-btn"]`.
4. **Step 1 - Asset Type Selection**: Selects "Machine" type and "Liquid Handler" category.
5. **Step 2 - Machine Search**: Searches for "STAR" in the definition search and selects the first result.
6. **Step 3 - Backend Verification**: Verifies "Simulated" backend is pre-selected.
7. **Step 4 - Summary Confirmation**: Verifies summary displays "Hamilton STAR".
8. **Asset Creation**: Clicks "Create Asset" and verifies wizard closes and asset appears.

**UI Elements Covered:**
- `[data-tour-id="add-asset-btn"]` button
- `app-asset-wizard` component
- `mat-card` for asset type selection
- Category dropdown (`getByLabel('Category')`)
- Search input (`getByLabel('Search Definitions')`)
- `.result-card` for definition selection
- Backend select display (`getByLabel('Backend (Driver)')`)
- Summary heading and `.review-card`
- Action buttons: "Next", "Create Asset"

**State Changes Verified:**
- Wizard opens
- Wizard navigates through steps
- Asset appears in page after creation (via text assertion)

### Assertions (Success Criteria)

| Assertion | Line | Purpose |
|-----------|------|---------|
| `expect(addAssetBtn).toBeVisible()` | 66 | Add Asset button rendered |
| `expect(wizard).toBeVisible()` | 70 | Wizard dialog opened |
| `expect(backendSelect).toContainText(/Simulated/)` | 91 | Correct default driver |
| `expect(wizard.getByRole('heading', { name: 'Summary' })).toBeVisible()` | 97 | Summary step reached |
| `expect(wizard.locator('.review-card')).toContainText('Hamilton STAR')` | 98 | Correct asset in summary |
| `expect(wizard).not.toBeVisible()` | 104 | Wizard closed after creation |
| `expect(page.getByText('Hamilton STAR')).toBeVisible()` | 105 | Asset appears in page |

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

| Issue | Severity | Lines | Details |
|-------|----------|-------|---------|
| **Hardcoded `waitForTimeout(1000)`** | 🔴 High | 83 | Fixed 1-second wait for search debounce. Should wait for autocomplete results to appear instead. |
| **Ignores `app.fixture.ts` / `worker-db.fixture.ts`** | 🔴 High | 1 | Imports from raw `@playwright/test` instead of the parallel-safe fixture. Tests will conflict in parallel runs—workers share the same OPFS database. |
| **CSS Class Selector: `.result-card`** | 🟡 Medium | 84 | Uses CSS class instead of `data-testid` or semantic locator. Brittle against style refactors. |
| **API Mocking Without Verification** | 🟡 Medium | 17-46 | Mocks API responses but never verifies the UI correctly consumed mock data (e.g., that exactly one definition appeared). |
| **Empty Catch Swallows Errors** | 🟡 Medium | 55-60 | `try/catch` with empty handler silently ignores failures in welcome dialog dismissal—may mask real blocking issues. |
| **No `afterEach` Cleanup** | 🟠 Medium | 11-14 | `afterEach` only presses Escape; doesn't delete created assets. While `resetdb=1` is used, parallel runs may overlap. |
| **Non-Unique Selector: `mat-card` with text filter** | 🟡 Medium | 74 | `.filter({ hasText: /Machine/i })` could match multiple cards if labels overlap. |
| **Screenshot Paths Mixed with Source** | 🟢 Low | 62, 71, 78, 86, 93, 100, 106 | Screenshots saved to `praxis/web-client/e2e/screenshots/` relative path—acceptable but could use `testInfo.outputPath()` for CI. |
| **Magic `15000ms` and `30000ms` Timeouts** | 🟢 Low | 52, 66, 104, 105 | Custom timeouts should be constants for maintainability. |

### Modern Standards (2026) Evaluation

| Criterion | Rating | Notes |
|-----------|--------|-------|
| **User-Facing Locators** | 7/10 | Good usage of `getByRole`, `getByLabel`, `getByText`. However, `.result-card` and `mat-card` are CSS-based. Should prefer `getByTestId('definition-card-...')` as seen in `AssetsPage` POM. |
| **Test Isolation** | 4/10 | Uses `resetdb=1` for DB reset but lacks worker-indexed database isolation. No cleanup of created assets. `afterEach` only dismisses dialogs—insufficient for parallel safety. |
| **Page Object Model (POM)** | 2/10 | **Does NOT use the existing `AssetsPage` POM**. The POM already provides `createMachine()`, `waitForWizard()`, `selectWizardCard()`, `clickNextButton()`, and overlay handling. This test duplicates all that logic inline. |
| **Async Angular Handling** | 5/10 | Uses `waitForFunction()` for SQLite readiness (good), but `waitForTimeout(1000)` for debounce is an anti-pattern. Should wait for `.result-card` to appear instead. |

---

## 3. Test Value & Classification

### Scenario Relevance

| Aspect | Assessment |
|--------|------------|
| **User Journey Type** | **Happy Path** — Tests the primary flow of adding a new machine via the wizard. No edge cases (e.g., invalid input, cancel, empty search results). |
| **Real User Scenario** | ✅ Yes — This is exactly how a lab operator would add a Hamilton STAR machine to their inventory. Core onboarding workflow. |
| **Criticality** | **High** — Asset creation is foundational; without machines, protocols cannot reference hardware. |

### Classification

| Classification | Verdict |
|----------------|---------|
| **True E2E** vs **Interactive Unit** | **Hybrid — Heavy Mocking degrades E2E value**. Mocks both `/facets` and `/definitions` API endpoints, so web doesn't actually fetch from the backend. The SQLite persistence is real (browser-side), but the "definition catalog" is synthetic. |
| **Integration Level** | Partial — Tests Angular UI → SQLite but **not** the machine definition API integration or Pyodide configuration serialization. |

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

```
1. User navigates to /assets?mode=browser&resetdb=1
   ├─ App initializes SQLite OPFS database
   └─ Waits for sqliteService.isReady$ = true

2. [Optional] Welcome dialog appears
   └─ User clicks "Get Started" / "Skip" / "Close"

3. User clicks "Add Asset" button
   └─ Asset Wizard (`app-asset-wizard`) opens in modal/overlay

4. STEP 1: Asset Type Selection
   ├─ User sees type cards (Machine, Resource, etc.)
   ├─ User clicks the "Machine" card
   ├─ User selects "Liquid Handler" from Category dropdown
   └─ User clicks "Next"

5. STEP 2: Search & Select Definition
   ├─ User types "STAR" in search input
   ├─ System (mocked) returns Hamilton STAR definition
   ├─ User clicks the first result card
   └─ User clicks "Next"

6. STEP 3: Backend/Driver Configuration
   ├─ System shows "Simulated" as available backend
   └─ User clicks "Next"

7. STEP 4: Summary Review
   ├─ User sees heading "Summary"
   ├─ Review card displays "Hamilton STAR"
   └─ User clicks "Create Asset"

8. Wizard closes, asset appears in inventory
```

### Contextual Fit

The Asset Wizard is the **primary onboarding entry point** for populating the lab inventory:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Praxis Application                            │
├─────────────────────────────────────────────────────────────────────┤
│  Home  │  Assets ← [Asset Wizard]  │  Protocols  │  Execution       │
├────────┼───────────────────────────┴─────────────┴──────────────────┤
│        │  Machines (Hamilton STAR, OT-2, etc.)                       │
│        │  Resources (Plates, Tubes, Tips)                            │
│        │  Deck Layouts                                               │
├────────┴────────────────────────────────────────────────────────────┤
│  SQLite OPFS (browser-side persistence)                             │
├─────────────────────────────────────────────────────────────────────┤
│  Machine Definition API (mocked in this test)                        │
├─────────────────────────────────────────────────────────────────────┤
│  JupyterLite/Pyodide (Python execution - NOT tested here)           │
└─────────────────────────────────────────────────────────────────────┘
```

**Downstream Dependencies:**
- **Protocol Execution**: References machines by accession_id
- **Deck Setup**: Assigns resources to machine deck slots
- **Simulation Mode**: Uses "Simulated" backend for dry runs

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Impact | Recommendation |
|-----|--------|----------------|
| **Resource Creation Path** | High | Only tests machine; resources use different wizard flow. Should have parallel test. |
| **Edit Flow** | High | No test for editing an existing machine after creation. |
| **Delete Flow** | High | No verification that the machine can be deleted. |
| **Cancel Mid-Wizard** | Medium | User pressing "Cancel" or navigating away is untested. |
| **Empty Search Results** | Medium | What happens when "STAR" matches nothing? Mocking bypasses real behavior. |
| **Validation Errors** | Medium | Empty name, duplicate names, or invalid category selection. |
| **Persistence Verification** | High | No page reload to confirm asset survives (unlike `asset-inventory.spec.ts`). |
| **Backend Selection** | Medium | Only verifies "Simulated" is present; doesn't test selecting alternative backends. |

### Domain Specifics

| Area | Current Coverage | Gap |
|------|------------------|-----|
| **Data Integrity** | ⚠️ Shallow | Asserts text "Hamilton STAR" appears on page, but does NOT verify: (1) Correct `accession_id` stored in SQLite, (2) Machine type and category persisted correctly, (3) Driver configuration serialized. |
| **Simulation vs. Reality** | ⚠️ Mocked | The API is mocked, so we don't test that real machine definitions load from the backend. In production, definitions come from a Python-generated catalog. |
| **Serialization** | ❌ Missing | Does NOT verify that the machine configuration is correctly serialized for Pyodide consumption. The wizard generates a config object; its structure is not validated. |
| **Error Handling** | ❌ Missing | No tests for: API failure during definition fetch, SQLite write failure, invalid backend selection, or quota exceeded errors. |
| **praxis.db Schema** | ❌ Not Verified | Test assumes DB works but never queries SQLite to verify the machine row exists with correct columns. |

### Comparison with `asset-wizard-visual.spec.ts`

The visual variant also:
- Mocks the same API endpoints
- Uses `waitForTimeout(500)` for animation settling
- Does NOT use the POM or fixture
- Focuses on grid layout verification (card counts, screenshots)

**Duplication**: Both tests share ~80% of the wizard navigation logic but are implemented independently. Should be consolidated.

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 6/10 | Covers full wizard happy path; misses CRUD completeness and persistence |
| **Best Practices** | 4/10 | Hardcoded waits, no POM, no fixture, CSS selectors |
| **Test Value** | 6/10 | Critical journey but heavy mocking reduces E2E integration value |
| **Isolation** | 4/10 | Uses `resetdb=1` but no worker DB isolation; cleanup only dismisses dialogs |
| **Domain Coverage** | 3/10 | UI-only assertions; no data integrity, serialization, or error coverage |

**Overall**: **4.6/10**

---

## Priority Improvements

1. **🔴 Critical**: Import from `fixtures/app.fixture` or `fixtures/worker-db.fixture` for parallel-safe DB isolation
2. **🔴 Critical**: Replace `waitForTimeout(1000)` with `expect(resultCard).toBeVisible()` assertion
3. **🔴 Critical**: Refactor to use `AssetsPage` POM—leverage existing `createMachine()` and wizard helpers
4. **🟡 High**: Add persistence verification: reload page and confirm asset survives
5. **🟡 High**: Add SQLite verification via `page.evaluate()` to query the machines table
6. **🟠 Medium**: Add edge case tests: cancel flow, empty search, validation errors
7. **🟠 Medium**: Consider removing or reducing API mocking to test real definition catalog
8. **🟢 Low**: Consolidate with `asset-wizard-visual.spec.ts` to reduce duplication
