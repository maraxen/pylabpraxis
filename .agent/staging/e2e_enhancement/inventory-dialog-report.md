# SDET Static Analysis: inventory-dialog.spec.ts

**Target File:** [inventory-dialog.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/inventory-dialog.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested
The test file claims to verify an "Inventory Dialog" component that supposedly contains:
- Opening the dialog via a button with `aria-label="Open Inventory Dialog"`
- Tab verification: "Quick Add", "Browse & Add", "Current Items"
- A multi-step wizard flow for adding simulated machines:
  - Selecting machine type via `.type-card`
  - Selecting category via `mat-chip-option`
  - Selecting an asset (simulated machine) via `mat-list-option`
  - Confirming and adding via "Add to Inventory" button
- Verification that items appear in "Current Items" tab via `.inventory-card-item`

### Assertions (Success Criteria)
1. **Tab Visibility Test:**
   - `expect(openButton).toBeVisible()` — Open button exists
   - `expect(page.getByRole('tab', { name: 'Quick Add' })).toBeVisible()` — Tab exists
   - `expect(page.getByRole('tab', { name: 'Browse & Add' })).toBeVisible()` — Tab exists  
   - `expect(page.getByRole('tab', { name: 'Current Items' })).toBeVisible()` — Tab exists

2. **Machine Addition Test:**
   - `expect(machineTypeCard).toBeVisible()` — Type card rendered
   - `expect(addButton).toBeVisible()` — Add button available
   - `expect(currentItems.first()).toBeVisible()` — Item appears after add

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

#### 🔴 **CRITICAL: Test Targets Non-Existent UI**
The selectors in this test do **not match** the actual application:

| Test Selector | Actual Application UI |
|--------------|----------------------|
| `aria-label="Open Inventory Dialog"` | Actual buttons: `aria-label="Browse Inventory"`, `aria-label="Add Machine"`, `aria-label="Add Resource"` |
| Tab: "Quick Add" | **Does not exist** — Wizard uses Material Stepper, not tabs |
| Tab: "Browse & Add" | **Does not exist** |
| Tab: "Current Items" | **Does not exist** |
| Button: "Add to Inventory" | Actual: `data-testid="wizard-create-btn"` with text "Create Asset" |
| Class: `.inventory-card-item` | **Does not exist** in codebase |
| Button: "Continue" | Actual: `data-testid="wizard-next-button"` with text "Next" |

**Root Cause:** This test appears to be written against a **speculative or outdated design** that was never implemented. The actual implementation uses `AssetWizard` component with a Material Stepper flow (Type → Category → Machine Type → Driver → Config → Review).

#### 🟡 Hardcoded Waits
```typescript
await page.waitForTimeout(1000);  // Line 11 - arbitrary wait
```
Acceptable in overlay handling context but wasteful if overlays don't appear.

#### 🟡 Brittle CSS Selectors
- `.type-card` — Implementation-specific, though stable (exists in `asset-wizard.html`)
- `mat-chip-option` — Angular Material internal structure (fragile across versions)
- `mat-list-option` — Same issue
- `.inventory-card-item` — Does not exist

#### 🟡 Silent Failures
```typescript
try {
  // overlay handling
} catch (e) {
  // Overlays not visible or already handled
}
```
Silent catch suppresses potential issues without logging.

#### 🟢 Good Practices Present
- Uses `getByRole` for buttons (mostly)
- Uses `getByRole('tab', { name: ... })` pattern
- Conditional click handling with `isVisible()` check

### Modern Standards (2026) Evaluation

- **User-Facing Locators**: Partial. Uses `getByRole` for tabs/buttons but actual app has `data-testid` attributes that would be more reliable.
- **Test Isolation**: No explicit cleanup. Missing `afterEach` for potential state contamination.
- **Page Object Model (POM)**: ❌ Not used. All logic inline despite `base.page.ts` existing.
- **Async Angular Handling**: Uses timeout-based overlay waiting; should use Angular zone stability waiting.

---

## 3. Test Value & Classification

### Scenario Relevance 
**Scenario Intent:** Adding a simulated machine to inventory from the playground.

This **is** a critical user journey for lab automation software. However, the test workflow is fundamentally broken because it matches a non-existent UI:
- The actual UI uses `AssetWizard` opened as a dialog
- The actual flow is: Type → Category → Machine Type (Frontend) → Driver (Backend) → Config → Review → Create
- No tabs exist; wizard uses `mat-stepper`

**Real User Impact:** A scientist would:
1. Click "Add Machine" in the playground header
2. Navigate the AssetWizard stepper
3. Configure machine settings
4. Click "Create Asset"
5. See the machine appear in the machines list

### Classification
**Interactive Unit Test (effectively broken)**: This test cannot pass against the actual application. The selectors target non-existent elements, so it would fail immediately at the first selector lookup beyond navigation.

**Evidence:**
- `Button[aria-label="Open Inventory Dialog"]` → No match (actual: "Browse Inventory")
- `Tab: Quick Add` → No match (no tabs in AssetWizard)
- `Class: .inventory-card-item` → No match in entire codebase

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow
Based on the test code, the **intended** workflow was:
1. Navigate to `/app/playground?mode=browser`
2. Dismiss onboarding overlays/tours
3. Click "Open Inventory Dialog" button
4. Verify tabbed interface with Quick Add, Browse & Add, Current Items
5. Switch to "Browse & Add" tab
6. Select "Machine" type card → Continue
7. Select first category chip → Continue
8. Select "Simulated" machine option (or first available) → Continue
9. Click "Add to Inventory" button
10. Verify item appears in Current Items tab

### Contextual Fit
**Intended Role:** This test should validate the core asset provisioning workflow — a fundamental capability for lab automation where users must configure instruments before running protocols.

**Actual Application Flow:**
1. Playground page loads with JupyterLite notebook
2. User clicks "Add Machine" (opens AssetWizard dialog)
3. Stepper: Type → Category → Machine Type → Driver → Config → Review → Create
4. Dialog closes, machine appears in Direct Control tab's machine list
5. Machine is persisted to SQLite

The test's mental model is completely divorced from the implementation.

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

#### Test is Obsolete — Complete Rewrite Required
All assertions target non-existent selectors. This test provides **zero coverage** of actual application behavior.

#### What Should Be Tested:
1. **AssetWizard Stepper Navigation**
   - Forward/backward navigation through all 5-6 steps
   - Form validation at each step
   - Proper form group state management

2. **Machine Type Selection**
   - Frontend selection (e.g., Hamilton STAR)
   - Backend/driver selection (simulator vs hardware)
   - Connection info requirements for hardware backends

3. **Resource Addition Flow** (separate path)
   - Definition search functionality
   - Resource creation with optional location

4. **Post-Creation Verification**
   - Machine appears in `availableMachines` signal
   - Machine is selectable in Direct Control tab
   - Machine persisted to SQLite (query verification)

### Domain Specifics

- **Data Integrity**: ❌ No verification of SQLite persistence. Test should confirm asset is queryable via `assetService.getMachines()` or direct SQL.

- **Simulation vs. Reality**: 🟡 Test intended to select "Simulated" machine, which is correct for E2E testing context. However, the selector doesn't match the actual "simulator" vs "hardware" backend type badges in the wizard.

- **Serialization**: ❌ Not tested. No verification that:
  - Frontend/backend FQN strings are correct
  - Configuration options are properly serialized
  - Machine instantiation payload is valid

- **Error Handling**: ❌ No coverage for:
  - Invalid category selection
  - Empty machine type results
  - Backend creation failures
  - Form validation errors

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 1/10 | Complete mismatch; tests non-existent UI |
| **Best Practices** | 3/10 | Some good patterns but can't run successfully |
| **Test Value** | 0/10 | Zero coverage of actual app; all selectors fail |
| **Isolation** | 4/10 | No afterEach cleanup but isolated navigation |
| **Domain Coverage** | 0/10 | No database verification, no serialization checks |

**Overall**: **1.6/10**

---

## Recommendation

**DELETE or ARCHIVE this test** and replace with a properly designed test suite that targets the actual `AssetWizard` component. See the improvement plan for the rewrite specification.

This test represents a significant testing gap: the asset provisioning workflow has **zero effective E2E coverage** because this test cannot execute against the real application.
