# SDET Static Analysis: asset-inventory.spec.ts

**Target File:** [asset-inventory.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/asset-inventory.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested
This test file verifies **browser-side SQLite persistence** for lab assets (Machines and Resources). Specifically:

1. **Machine Creation & Persistence**: Creates a machine via a multi-step dialog (autocomplete search for machine type → naming → save), navigates to the Machines tab to verify, then reloads the page to confirm persistence.
2. **Resource Creation & Persistence**: Creates a resource via a category-selection wizard (Select Category → Select Resource Model via autocomplete → naming → save), navigates to the Registry tab to verify, then reloads to confirm persistence.

**UI Elements Covered:**
- Sidebar navigation (`a[href="/app/assets"]`)
- Welcome dialog dismissal
- "Add Machine" / "Add Resource" buttons
- Autocomplete inputs (machine type, resource model)
- Tab navigation (`Machines`, `Registry`)
- Dialog headings for wizard steps

**State Changes Verified:**
- Asset appearance in correct tab after creation
- Asset survival after full page reload (SQLite OPFS persistence)

### Assertions (Success Criteria)
| Assertion | Purpose |
|-----------|---------|
| `expect(sidebar-rail).toBeVisible()` | App shell loaded |
| `expect(welcomeDialog).not.toBeVisible()` | Modal dismissed |
| `expect(heading: "Add New Machine").toBeVisible()` | Machine dialog opened |
| `expect(heading: "Add New Machine").not.toBeVisible()` | Dialog closed post-save |
| `expect(machineName).toBeVisible()` (×2) | Machine created & persisted after reload |
| `expect(heading: "Select Resource Category").toBeVisible()` | Resource dialog opened |
| `expect(heading: "Add New").not.toBeVisible()` | Dialog closed post-save |
| `expect(resourceName).toBeVisible()` (×2) | Resource created & persisted after reload |

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

| Issue | Severity | Lines | Details |
|-------|----------|-------|---------|
| **Hardcoded `waitForTimeout()`** | 🔴 High | 75, 88, 152 | Uses fixed 500ms sleeps for autocomplete debounce. Brittle—will fail on slow CI or succeed spuriously on fast machines. |
| **Ignores `app.fixture.ts`** | 🔴 High | 1 | Imports from raw `@playwright/test` instead of `../fixtures/app.fixture` which provides worker-indexed DB isolation (`dbName=praxis-worker-N`). **Tests will conflict in parallel runs.** |
| **CSS selector reliance** | 🟡 Medium | 20, 44, 116, 129, 140, 145, 177 | Uses `.sidebar-rail`, `.category-card` instead of role/label locators. Fragile against style refactors. |
| **Implicit catch swallows failure** | 🟡 Medium | 15-17 | `waitForURL().catch(() => console.log(...))` silently ignores redirect failures—test continues in undefined state. |
| **Non-unique heading locator** | 🟡 Medium | 167 | `heading: /Add New/i` is ambiguous—could match "Add New Machine" or other dialogs. |
| **No test isolation / cleanup** | 🟠 Medium | — | Creates assets but never deletes them. Subsequent runs could fail due to stale data (though `resetdb=1` would mitigate if used). |
| **Console logging without structured output** | 🟢 Low | 30-35, 41, 54, 58, 61, 127 | Inline `console.log` debugging—acceptable for exploration but adds noise in CI logs. |

### Modern Standards (2026) Evaluation

| Criterion | Rating | Notes |
|-----------|--------|-------|
| **User-Facing Locators** | 6/10 | Mix of `getByRole('button')`, `getByRole('tab')`, `getByLabel()` (good) with `.sidebar-rail a[href=...]`, `.category-card` (CSS-based). Should use `data-testid` or `getByRole('link', { name: 'Assets' })`. |
| **Test Isolation** | 3/10 | No `afterEach()` cleanup. Does not use worker-indexed fixture. If run in parallel, both workers will write to the same OPFS DB causing race conditions. |
| **Page Object Model (POM)** | 2/10 | **Does not use `AssetsPage` POM** even though it exists and provides `createMachine()`, `createResource()`, `deleteMachine()`, `deleteResource()`. All logic is inline—severe missed opportunity for reuse and maintenance. |
| **Async Angular Handling** | 4/10 | Uses `waitForTimeout(500)` instead of waiting for Angular signals (autocomplete options rendering). Should use `await optionLocator.waitFor({ state: 'visible' })` or Playwright's auto-waiting with more precise locators. |

---

## 3. Test Value & Classification

### Scenario Relevance
| Aspect | Assessment |
|--------|------------|
| **User Journey Type** | **Happy Path** — tests the primary flow of adding assets and verifying persistence. No validation edge cases, errors, or cancel flows. |
| **Real User Scenario** | ✅ Yes — a lab operator would absolutely add machines/resources and expect them to persist. This is a core workflow. |
| **Criticality** | **High** — persistence is foundational; if this breaks, the app is unusable. |

### Classification
| Classification | Verdict |
|----------------|---------|
| **True E2E** vs **Interactive Unit** | **True E2E Test** — interacts with the full stack: Angular UI → SQLite OPFS → page reload → data retrieval. No mocking. |
| **Integration Level** | Tests serialization pipeline (form → service → DB) and deserialization (DB → service → UI). Does **not** test Python/Pyodide integration. |

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

**Test 1: `should persist created machine across reloads`**
1. Navigate to `/` → redirect to `/app/home`
2. Dismiss Welcome Dialog if present
3. Click Assets link in sidebar → navigate to `/app/assets`
4. Verify "Quick Actions" section visible (confirms asset dashboard loaded)
5. Click "Add Machine" button
6. In "Add New Machine" dialog:
   - Enter "Opentrons" in machine type autocomplete (falls back to "Hamilton" if no results)
   - Select first autocomplete option
   - Fill "Name" field with unique timestamp-based name
   - Click "Save"
7. Verify dialog closes
8. Click "Machines" tab
9. Verify new machine name appears in table
10. **Reload page** (explicit persistence test)
11. Re-navigate to Assets → Machines tab
12. Verify machine name still visible

**Test 2: `should persist created resource across reloads`**
1. (Same app init steps)
2. Click Assets link → verify Quick Actions
3. Click "Add Resource" button
4. In "Select Resource Category" dialog:
   - Click a category card (prefers "plate", falls back to first)
5. In Step 2:
   - Fill Resource Model autocomplete with "96"
   - Select first matching definition
   - Fill "Name" field with unique name
   - Click "Save Resource"
6. Verify dialog closes
7. Click "Registry" tab
8. Verify new resource name appears
9. **Reload page**
10. Re-navigate → verify resource persists

### Contextual Fit
This test validates **Asset Inventory** as part of the larger Praxis lab automation ecosystem:

```
┌─────────────────────────────────────────────────────────────┐
│                     Praxis Application                      │
├─────────────────────────────────────────────────────────────┤
│  Home  │  Assets ← THIS TEST  │  Protocols  │  Execution   │
├────────┴────────────────────────┴─────────────┴─────────────┤
│  SQLite OPFS (Browser-Side Persistence)                     │
├─────────────────────────────────────────────────────────────┤
│  JupyterLite/Pyodide (Python Execution)                     │
└─────────────────────────────────────────────────────────────┘
```

Assets (Machines, Resources) are prerequisites for:
- **Protocol Configuration**: Protocols reference deck layouts with resources
- **Protocol Execution**: Python code controls machines
- **Deck Setup**: Spatial arrangement of resources and machines

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Impact | Recommendation |
|-----|--------|----------------|
| **Edit Flow** | High | No test for editing an existing machine/resource |
| **Delete Flow** | High | No test for deletion (POM supports `deleteMachine()`) |
| **Validation Errors** | Medium | No test for submitting empty name, duplicate names, or malformed data |
| **Autocomplete Empty State** | Medium | No test for when no matching machine types/resources exist |
| **Multi-Tab Sync** | Medium | No test for Browser Tab A creates asset, Tab B sees it (SharedWorker/OPFS sync) |
| **Cancel Flow** | Low | No test for user clicking Cancel mid-wizard |

### Domain Specifics

| Area | Current Coverage | Gap |
|------|------------------|-----|
| **Data Integrity** | ⚠️ Partial | Tests only that *a name appears* after save. Does **not** verify: correct machine type was stored, all form fields persisted, correct category saved, or that SQLite row structure is valid. |
| **Simulation vs. Reality** | ⚠️ None | Tests create "Opentrons" or "Hamilton" machines but never verify the machine driver configuration. In real use, machines connect to physical hardware; here we only test the metadata layer. |
| **Serialization** | ⚠️ None | Does **not** verify that form data is correctly serialized for Pyodide consumption (e.g., `JSON.stringify` of config params). Only UI-level assertion. |
| **Error Handling** | ❌ Missing | No tests for: DB write failure, network error simulation, quota exceeded, or corrupt autocomplete response. |
| **praxis.db Parsing** | ❌ Not Tested | Tests assume DB works but never verify schema migrations, table structure, or that `SqliteService.isReady$` emitted correctly. |

### Recommended Test Additions
```typescript
// Example: Validate stored data structure
test('created machine has correct schema in DB', async ({ page }) => {
  // Create machine via UI...
  // Then query DB directly
  const dbData = await page.evaluate(() => {
    return window.sqliteService.query('SELECT * FROM machines WHERE name = ?', [machineName]);
  });
  expect(dbData[0].type).toBe('Hamilton');
  expect(dbData[0].driver_config).toBeDefined();
});
```

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 6/10 | Covers core persistence happy path; misses delete/edit/validation |
| **Best Practices** | 4/10 | Hardcoded waits, no POM usage, CSS selectors, no fixture import |
| **Test Value** | 8/10 | Critical user journey, true E2E, high ROI |
| **Isolation** | 3/10 | No cleanup, no worker DB isolation, will fail in parallel |
| **Domain Coverage** | 3/10 | UI-only assertions; no data integrity, serialization, or error tests |

**Overall**: **4.8/10**

---

## Priority Improvements

1. **🔴 Critical**: Import from `fixtures/app.fixture` instead of `@playwright/test` for worker DB isolation
2. **🔴 Critical**: Replace `waitForTimeout(500)` with explicit waits for autocomplete options
3. **🟡 High**: Refactor to use `AssetsPage` POM for `createMachine()` and `createResource()`
4. **🟡 High**: Add `afterEach()` cleanup using `AssetsPage.deleteMachine()/deleteResource()`
5. **🟠 Medium**: Add data integrity assertions via `page.evaluate()` SQLite queries
6. **🟠 Medium**: Add error path tests (validation, DB failures)
