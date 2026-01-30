# SDET Static Analysis: browser-export.spec.ts

**Target File:** [browser-export.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/browser-export.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested

This test file focuses on the **Data Management** section of the Settings page, specifically:

1. **Export Database functionality** - Verifies that clicking "Export Database" triggers a browser download with the expected filename format (`praxis-backup-YYYY-MM-DD.db`) and shows a success snackbar.

2. **Import Database dialog flow** - Verifies that the user can initiate a file selection, the confirmation dialog appears with proper text, and the user can cancel the import operation.

**UI Elements Covered:**
- Settings page header/navigation
- Export Database button
- Import Database button  
- Hidden file input for import
- Confirmation dialog (`app-confirmation-dialog`)
- Success/feedback snackbar

**State Changes Verified:**
- Download event triggered
- Confirmation dialog visibility toggle
- Welcome dialog dismissal (onboarding flow)

### Assertions (Success Criteria)

| Test | Assertions |
|------|------------|
| Export Database | 1. Export button visible<br>2. Download triggered<br>3. Filename contains `praxis-backup`<br>4. Filename contains `.db`<br>5. Snackbar shows "Database exported" |
| Import Database | 1. File chooser opened<br>2. Confirmation dialog visible<br>3. Dialog contains text "Import Database?"<br>4. Cancel dismisses dialog |

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

#### ✅ Strengths

1. **User-Facing Locators**: Excellent use of `getByRole()` for buttons and `getByText()` for snackbar content.
2. **Event-Driven Assertions**: Uses `page.waitForEvent('download')` and `page.waitForEvent('filechooser')` for async events.
3. **No Hardcoded Timeouts**: Uses visibility-based assertions instead of `waitForTimeout`.
4. **Safe Import Test**: Correctly cancels the destructive import operation to preserve test environment.

#### ⚠️ Issues

| Issue | Severity | Line | Description |
|-------|----------|------|-------------|
| **No POM usage** | Medium | 19-38 | Test uses raw `page.getByRole()` calls instead of the existing `SettingsPage` page object |
| **Direct `/app/settings` navigation** | Medium | 7 | Does not use `BasePage.goto()`, missing `mode=browser` and worker isolation |
| **CSS selector for dialog** | Low | 71 | Uses `page.locator('app-confirmation-dialog')` instead of `getByRole('dialog')` |
| **No async welcome dialog check** | Low | 11 | Uses sync `if (await welcomeDialog.isVisible())` which may race with Angular rendering |
| **Missing snackbar wait** | Low | 37 | Snackbar assertion has no explicit timeout, may flake on slow CI |
| **Timeout magic number** | Low | 16 | Uses `timeout: 15000` without explaining why 15s is needed |

### Modern Standards (2026) Evaluation

| Criterion | Status | Notes |
|-----------|--------|-------|
| **User-Facing Locators** | ✅ Good | Uses `getByRole('button')`, `getByRole('dialog')`, `getByRole('heading')` |
| **Test Isolation** | ⚠️ Partial | No `afterEach` cleanup; does not use worker-isolated DB; welcome dialog handling implies shared state |
| **Page Object Model** | ❌ Missing | `SettingsPage` exists with `exportDatabase()` and `importDatabase()` methods but is NOT used |
| **Async Angular Handling** | ⚠️ Partial | Good event-based waits; missing `waitForFunction` for SqliteService readiness in browser mode |

---

## 3. Test Value & Classification

### Scenario Relevance

**Critical Journey (Happy Path)**: ✅ Yes

Data export/import is a **critical user journey** for:
- Backup before destructive operations
- Migrating data between devices
- Disaster recovery

This is a realistic scenario users would perform. The test captures the core happy path for export and the "cancel" path for import.

### Classification

**True E2E Test**: ⚠️ Partial

| Aspect | Classification | Reason |
|--------|----------------|--------|
| Export flow | True E2E | Triggers real `SqliteService.exportDatabase()` → Blob download |
| Import flow | Interactive Unit | Cancels before actual import; does NOT test the actual database restore |

The import test is incomplete—it verifies the dialog appears but not that:
1. The file is correctly parsed
2. The database is replaced
3. The page reloads with new data

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

```
1. User navigates to /app/settings
2. [OPTIONAL] If first visit, dismisses "Welcome to Praxis" dialog
3. User sees Settings page with "Settings" heading

--- EXPORT FLOW ---
4. User clicks "Export Database" button
5. Browser initiates download of praxis-backup-YYYY-MM-DD.db
6. Snackbar confirms "Database exported"

--- IMPORT FLOW (CANCEL PATH) ---
7. User clicks "Import Database" button
8. File chooser opens
9. User selects a .db file
10. Confirmation dialog appears: "Import Database?"
11. User clicks "Cancel"
12. Dialog closes without importing
```

### Contextual Fit

This component fits into the **Data Management** section of the application:

```
┌─────────────────────────────────────────────────┐
│  Settings Page                                  │
├────────────────────┬────────────────────────────┤
│  Appearance        │  Theme toggle              │
│  Features          │  Maintenance, Consumables  │
│  Onboarding        │  Tutorial controls         │
│  Remote Hardware   │  Agent installation guide  │
│  About             │  Version info              │
│  Data Management   │  ← THIS TEST SCOPE         │
│    ├── Export      │  Download backup           │
│    ├── Import      │  Restore from file         │
│    └── Reset       │  Clear to defaults         │
└────────────────────┴────────────────────────────┘
```

The export/import functionality directly interfaces with `SqliteService`, which manages browser-mode SQLite (OPFS/IndexedDB).

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Priority | Description |
|-----|----------|-------------|
| **Import confirmation path** | P1 | Test cancels import; does not verify actual database replacement works |
| **Export content validation** | P1 | Verifies filename but not that the downloaded file is a valid SQLite DB |
| **Multi-worker isolation** | P2 | Test runs without `BasePage` isolation; will fail in parallel execution |
| **Reset to Defaults flow** | P2 | Same card has "Reset Asset Inventory" but no coverage |
| **Error state coverage** | P2 | No tests for failed export/import (e.g., disk full, corrupted file) |
| **Mode enforcement** | P3 | Does not verify `mode=browser` behavior; may pass incorrectly in server mode |

### Domain Specifics

#### Data Integrity
| Aspect | Status | Notes |
|--------|--------|-------|
| Export produces valid SQLite | ❌ Not tested | Only checks filename pattern |
| Import parses file correctly | ❌ Not tested | Cancelled before import |
| Post-import state verification | ❌ Not tested | Should verify assets/protocols restored |

#### Simulation vs. Reality
| Aspect | Status | Notes |
|--------|--------|-------|
| Browser mode enforcement | ⚠️ Implicit | Goes to `/app/settings` without `?mode=browser` |
| OPFS vs IndexedDB backend | ❌ Not tested | Settings page has OPFS toggle; not covered |

#### Serialization
| Aspect | Status | Notes |
|--------|--------|-------|
| Uint8Array → Blob conversion | ⚠️ Implicit | Not verified; assumes component works |
| File → ArrayBuffer → import | ❌ Not tested | Cancelled before execution |

#### Error Handling
| Aspect | Status | Notes |
|--------|--------|-------|
| Export failure snackbar | ❌ Not tested | Component has `catch` → "Export failed" |
| Invalid file format | ❌ Not tested | What happens with a PDF instead of .db? |
| Corrupted database file | ❌ Not tested | Import may fail silently or crash |
| Import network timeout | ❌ Not tested | Page reload after import could fail |

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 5/10 | Covers export happy path but import is incomplete |
| **Best Practices** | 6/10 | Good locators; missing POM usage and isolation |
| **Test Value** | 6/10 | Critical journey but shallow depth |
| **Isolation** | 3/10 | No worker isolation; shared welcome dialog state |
| **Domain Coverage** | 3/10 | No data integrity, error handling, or content validation |

**Overall: 4.6/10**

---

## Appendix: Related Files

| File | Purpose |
|------|---------|
| `e2e/page-objects/settings.page.ts` | Existing POM with `exportDatabase()`, `importDatabase()` methods |
| `e2e/page-objects/base.page.ts` | Worker isolation via `testInfo.workerIndex`, mode=browser enforcement |
| `src/app/features/settings/components/settings.component.ts` | Implementation with `exportData()`, `importData()` methods |
| `src/app/core/services/sqlite.ts` | `SqliteService` with `exportDatabase()`, `importDatabase()` observables |
