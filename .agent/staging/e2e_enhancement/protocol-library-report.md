# Senior SDET Review: `protocol-library.spec.ts`

**File Under Review:** [`e2e/specs/protocol-library.spec.ts`](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/protocol-library.spec.ts)  
**Review Date:** 2026-01-30  
**Reviewer Role:** Senior SDET / Angular + Playwright Specialist  
**Baseline Score:** **6.0/10** (Functional but Shallow)

---

## 1. Test Scope & Coverage

### What is Tested

This 102-line test file covers the **Protocol Library** page, a standalone management interface for viewing, searching, filtering, and initiating protocols. The component uses Angular Material's `mat-table` for a default table view and `app-protocol-card` components for card view.

| Verification Area | Covered? | Line(s) |
|-------------------|----------|---------|
| **Page Load & Navigation** | ✅ | L12-18, L20-26 |
| **Table Rendering** | ✅ | L17, L25 |
| **Search Filtering by Name** | ✅ | L28-41 |
| **Status Filter Dropdown** | ✅ | L48-77 |
| **Protocol Details Dialog** | ✅ | L79-90 |
| **Run Protocol (Navigation)** | ✅ | L92-100 |
| **Category Filter** | ❌ (FIXME) | L43-47 |
| **Card View Toggle** | ❌ | N/A |
| **Protocol Upload** | ❌ | N/A |
| **Error States (No Results)** | ❌ | N/A |

### Key Assertions (Success Criteria)

| Assertion | Purpose | Mode |
|-----------|---------|------|
| `expect(page.getByRole('heading', { level: 1 })).toContainText(/Protocol/i)` | Verify page title | Text Match |
| `expect(page.locator('tr[mat-row]').first()).toBeVisible()` | At least one protocol row visible | Presence |
| `expect(searchInput).toBeVisible()` | Search input is present | Presence |
| `expect(page.locator('tr[mat-row]').filter({ hasText: 'Kinetic Assay' })).toBeVisible()` | Search filter shows expected result | Presence |
| `expect(page.locator('tr[mat-row]').filter({ hasText: 'Simple Transfer' })).not.toBeVisible()` | Search excludes other protocols | Absence |
| `expect(selectPanel).toBeVisible()` | Status dropdown panel opens | Presence |
| `expect(dialog).toBeVisible()` | Protocol detail dialog opens | Presence |
| `expect(dialog.getByRole('button', { name: /Run Protocol/i })).toBeVisible()` | Dialog has Run button | Presence |
| `expect(page).toHaveURL(/\/run/)` | Navigation to run page | URL Match |

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique: Brittle Patterns Identified

| Issue | Location | Severity | Details |
|-------|----------|----------|---------|
| **Hardcoded `waitForTimeout`** | L53, L72 | 🔴 **Critical** | `page.waitForTimeout(500)` is a **race condition**—should wait for Angular stabilization or a specific DOM change. |
| **Implementation-Detail Selectors** | L17, L25, L35, L63, L81, L85, L95 | 🟡 **Medium** | Heavy reliance on CSS class locators (`tr[mat-row]`, `table[mat-table]`, `.mat-mdc-select-panel`, `mat-dialog-container`). These are Material internal implementation details, not user-facing. |
| **No Page Object Model** | Entire file | 🟡 **Medium** | All DOM interactions are inline—no `ProtocolLibraryPage` abstraction. Limits reusability and maintainability. |
| **FIXME Documented Bug** | L43-47 | 🟡 **Medium** | Category filter testing is explicitly skipped due to a known Angular signal reactivity bug (`categoryOptions()` computed from `protocols()` not propagating to `ViewControlsComponent`). |
| **Unverified Negative Assertions** | L39-40 | 🟡 **Medium** | Uses `not.toBeVisible()` with a 5s timeout. If the element appears briefly then disappears (known in Angular SPA), this could be flaky. |
| **No Console Error Capture** | Entire file | 🟢 **Low** | No `page.on('console')` to catch unexpected warnings/errors during test execution. |

### Modern Standards (2026) Evaluation

| Criterion | Status | Notes |
|-----------|--------|-------|
| **User-Facing Locators** | ⚠️ **Partial** | Uses `getByRole('heading')`, `getByPlaceholder(/Search/i)`, `getByRole('combobox', { name: /Status/i })`, `getByRole('option')` ✅. But uses `tr[mat-row]`, `.mat-mdc-select-panel`, `mat-dialog-container` ❌. |
| **Web-First Assertions** | ✅ **Good** | All assertions use Playwright's auto-waiting `expect()` system with explicit timeouts. |
| **Test Isolation** | ✅ **Good (via Fixture)** | Uses `app.fixture.ts` which provides worker-indexed DB isolation (`praxis-worker-{index}`) and handles welcome dialog dismissal. |
| **Cleanup** | ⚠️ **Implicit** | No explicit cleanup in `afterEach`. Relies on fixture-level DB reset and browser context isolation. |
| **Page Object Model** | ❌ **None** | All 5 tests have inline DOM manipulation. No `ProtocolLibraryPage` POM exists (unlike `protocol.page.ts` which is for the Run Wizard). |
| **Async Angular Handling** | ⚠️ **Partial** | Uses `waitForTimeout(500)` instead of proper Angular stability checks. No `ng.getComponent` deep state verification. |
| **No Hardcoded Waits** | ❌ **Fails** | Lines 53 and 72 use explicit `waitForTimeout(500)`. |

---

## 3. Test Value & Classification

### Scenario Relevance

| Question | Answer |
|----------|--------|
| **Is this a Critical User Journey?** | ⚠️ **Moderate.** Protocol Library is a secondary management interface. The *primary* user journey is the Run Protocol Wizard (`/app/run`). However, power users managing many protocols will use this view frequently. |
| **Happy Path or Edge Case?** | **Happy Path.** All 5 tests verify the ideal scenario: protocols are seeded, UI renders correctly, interactions work as expected. |
| **Would a Real User Perform This?** | ✅ **Yes.** Searching for protocols, filtering by status, opening details, and running them are all realistic user actions. |

### Classification

| Category | Assessment |
|----------|------------|
| **True E2E Test?** | ✅ **Yes.** Uses real SQLite database (seeded via `browser` mode), real Angular routing, real Material dialog. No mocking of ProtocolService or backend. |
| **Interactive Unit Test?** | ❌ No. Not isolated component testing. |
| **Integration Smoke Test?** | ⚠️ **Partially.** Verifies integration (Angular + Material + SQLite + Routing) but lacks depth—no verification of *what* data is displayed, just *that* something displays. |

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered User Workflow

Based **only on the test code**, the intended user experience is:

1. **User navigates to `/app/protocols?mode=browser`.**
   - Tests use `browser` mode, meaning SQLite runs in the browser with seeded data.
   - Fixture handles database isolation and welcome dialog bypass.

2. **Page loads and shows a table of protocols.**
   - Default view is `table` (not `card`).
   - Spinner clears and at least one `<tr mat-row>` is visible.

3. **User searches for a protocol by name.**
   - Types "Kinetic" into the search input.
   - Table filters to show "Kinetic Assay" row.
   - Other protocols (e.g., "Simple Transfer") are hidden.

4. **User filters by status.**
   - Opens the "Status" combobox.
   - Selects "Not Simulated" option.
   - Table shows protocols without simulation results.

5. **User opens protocol details.**
   - Clicks on a table row.
   - A `mat-dialog` opens with a "Run Protocol" button.

6. **User runs a protocol.**
   - Clicks the play button (`mat-icon: play_arrow`) in the Actions column.
   - Browser navigates to `/run` with `protocolId` query param.

### Contextual Fit

The `ProtocolLibraryComponent` is a **CRUD management interface** for protocols:

- It is accessible via the `/app/protocols` route.
- It displays protocols fetched from `ProtocolService`, which reads from the SQLite database.
- It offers search, category/status/type filtering, and sorting.
- The **Detail Dialog** shows protocol metadata and has a "Run Protocol" button.
- The **Run action** navigates to `/run` (the multi-step wizard handled by `ProtocolPage` POM).

This test covers the **read/view** portion of the CRUD lifecycle. It does **not** test:
- **Create**: The `uploadProtocol()` file upload flow.
- **Update**: (If implemented, editing protocol metadata).
- **Delete**: (If implemented, removing protocols).

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Description | Risk |
|-----|-------------|------|
| **Category Filter (Known Bug)** | L43-47 explicitly documents a bug where `categoryOptions()` doesn't populate in E2E. No workaround test exists. | Users cannot filter by category—a key protocol organization feature. |
| **Card View Toggle** | The component supports `viewType: 'card'` but no test toggles the view. | Card view could break silently. |
| **Protocol Upload** | `uploadProtocol()` is a key workflow (allowing users to add new `.py` protocol files). No E2E test. | Upload could fail silently; users may not be able to add new protocols. |
| **Empty State** | When zero protocols match a filter, an empty state is shown. No test verifies this renders correctly. | Empty state message could be wrong or missing. |
| **Dialog Content Verification** | Test opens the detail dialog but only checks for "Run Protocol" button presence. Does not verify protocol name, description, or parameters displayed. | Dialog could show wrong protocol or corrupted data. |
| **Protocol Data Integrity** | Test verifies "Kinetic Assay" appears after filtering, but doesn't verify the row contains correct version/category/description. | Protocols could have wrong metadata. |

### Domain-Specific Verification Gaps

| Domain Area | Covered? | Notes |
|-------------|----------|-------|
| **Data Integrity (`praxis.db`)** | ⚠️ **Implicit** | Test relies on seeded protocols with known names ("Kinetic Assay") but doesn't verify the database content directly. If the seed changes, test interpretations become invalid. |
| **Simulation vs. Reality** | ❌ **Not Tested** | Test filters by "Not Simulated" status but doesn't verify that protocol execution would use a simulated machine or real hardware. |
| **Argument Serialization** | ❌ **Not Tested** | When clicking "Run Protocol", the `protocolId` is passed via query param. Test verifies URL contains `/run` but doesn't verify the `protocolId` value is correct or that parameters are pre-populated. |
| **Error States** | ❌ **Not Tested** | No test for: invalid search term, server error during protocol load, malformed protocol data, or failed `ProtocolService.getProtocols()`. |
| **SQLite Query Verification** | ❌ **Not Tested** | No interception of SQL queries or verification that `ProtocolService` correctly translates signal state to database reads. |

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 5/10 | Covers 5 basic happy-path scenarios but misses upload, card view, empty state, and data verification. |
| **Code Quality** | 6/10 | Uses app fixture correctly; has two `waitForTimeout` anti-patterns; no POM. |
| **Modern Standards** | 6/10 | Mixed locator strategy (some role-based, some CSS-based); good auto-waiting; lacks Angular stability patterns. |
| **Domain Verification** | 4/10 | No verification of actual protocol content, simulation status correctness, or serialization. |
| **True E2E Depth** | 8/10 | Real SQLite, real signals, real service—no mocking. High integration fidelity. |

**Overall Baseline Score: 6.0/10 (Functional but Shallow—verifies presence, not correctness)**

---

## Related Resources

- **Component Under Test:** [`ProtocolLibraryComponent`](file:///Users/mar/Projects/praxis/praxis/web-client/src/app/features/protocols/components/protocol-library/protocol-library.component.ts)
- **App Fixture:** [`app.fixture.ts`](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/fixtures/app.fixture.ts)
- **Existing POM (Run Wizard):** [`protocol.page.ts`](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/page-objects/protocol.page.ts)
- **Protocol Service:** [`protocol.service.ts`](file:///Users/mar/Projects/praxis/praxis/web-client/src/app/features/protocols/services/protocol.service.ts)
- **KI Reference:** [Praxis Testing Knowledge](file:///Users/mar/.local/share/ov/profiles/fast-gemini-flash/.gemini/antigravity/knowledge/praxis_testing_knowledge/artifacts/)
