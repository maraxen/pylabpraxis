# SDET Static Analysis: interactions/03-asset-forms.spec.ts

**Target File:** [03-asset-forms.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/interactions/03-asset-forms.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist

---

## 1. Test Scope & Coverage

### What is Tested
This test file covers **form validation behavior** within the Asset Wizard component (`app-asset-wizard`). Specifically:

1. **Test 1: Machine Name Validation** (`should validate machine name is required`)
   - Opens the Add Machine dialog
   - Navigates through wizard steps to reach the Configuration step (Step 3/Config)
   - Clears the "Instance Name" input field
   - Verifies the Finish/Save button becomes disabled
   - Fills a valid name and verifies the button becomes enabled

2. **Test 2: JSON Validation** (`should show validation error for invalid JSON in advanced config`)
   - Opens the Add Machine dialog
   - Navigates to the Configuration step
   - Attempts to locate an "Advanced JSON" toggle
   - If found, inputs invalid JSON
   - Expects a `mat-error` to be visible and Finish button disabled

**UI Elements Exercised:**
- Add Machine button
- Category cards (`.category-card`)
- Definition items (`.definition-item`)
- Instance Name input (`getByLabel('Instance Name')` or `getByLabel('Name')`)
- Finish/Save button (`getByRole('button', { name: /Finish|Save/i })`)
- Advanced JSON toggle (conditional)
- `mat-error` validation display

### Assertions (Success Criteria)
| Test | Key Assertions |
|------|----------------|
| `should validate machine name is required` | Dialog visible, Finish button disabled when name empty, Finish button enabled when name filled |
| `should show validation error for invalid JSON` | `mat-error` element visible, Finish button disabled when JSON invalid |

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

#### 🔴 Critical Issues

1. **Incorrect Wizard Step Navigation (Lines 27-31, 54-55)**
   The test uses `.category-card` and `.definition-item` CSS class selectors which **do not exist in the actual wizard HTML**. The wizard uses:
   - `category-card` class within Step 2 (Category Selection)
   - `frontend-card-*` and `backend-card-*` test IDs for Step 3/4
   - No `.definition-item` class exists at all
   
   **Impact:** These tests will likely fail when trying to locate elements.

2. **Step Flow Mismatch (Lines 26-31)**
   The comment says "Move to Step 3 (Configuration)" but the actual wizard flow is:
   - Step 1: Asset Type (MACHINE/RESOURCE)
   - Step 2: Category Selection
   - Step 3: Frontend Selection (Machine Type)
   - Step 4: Backend Selection (Driver)
   - Step 5: Configuration
   - Step 6: Review
   
   The test completely skips the Asset Type step (Step 1) and attempts to navigate directly to category/definition. This flow is incorrect.

3. **Non-Unique Label Matching (Line 34)**
   ```typescript
   const nameInput = page.getByLabel('Instance Name').or(page.getByLabel('Name')).first();
   ```
   Using `.or()` with `.first()` is fragile - the wizard only has "Instance Name" as the label for this field. The fallback to 'Name' suggests uncertainty about the actual UI.

4. **Conditional Test Logic (Lines 58-68)**
   The JSON validation test conditionally runs only `if (await advancedToggle.isVisible())`. This means the test can silently pass without testing anything if the toggle doesn't exist.

#### 🟡 Moderate Issues

1. **CSS Class Selectors Instead of Test IDs**
   Lines 27, 30, 54-55 use `.category-card` and `.definition-item` which are styling classes, not semantic selectors. The wizard actually provides proper `data-testid` attributes like `category-card-{name}`.

2. **No Proper Step Synchronization**
   The test does not use the POM's `waitForStepTransition()` method that handles Material Stepper animations. Direct clicking on cards without waiting for transitions can cause race conditions.

3. **Mixed Selector Strategies**
   The test inconsistently uses:
   - `getByRole()` for dialog and buttons ✓
   - `getByLabel()` for inputs ✓
   - Raw CSS class selectors for cards ✗
   - Regexes with broad matching (`/Finish|Save/i`) rather than exact matches

### Modern Standards (2026) Evaluation

| Criterion | Score | Assessment |
|-----------|-------|------------|
| **User-Facing Locators** | 4/10 | Partial use of `getByRole` and `getByLabel`, but falls back to CSS class selectors (`.category-card`, `.definition-item`) for critical interactions |
| **Test Isolation** | 6/10 | Uses `beforeEach` with WelcomePage setup, but no explicit cleanup in `afterEach`. Relies on `resetdb=1` URL parameter via BasePage |
| **Page Object Model (POM)** | 3/10 | POMs exist (`AssetsPage`, `WelcomePage`) but are underutilized. The test does `assetsPage.goto()` but then manually constructs locators instead of using `assetsPage.createMachine()` flow |
| **Async Angular Handling** | 4/10 | No explicit synchronization for Material Stepper animations. `waitForOverlay()` is called but wizard-specific waiting is missing |

---

## 3. Test Value & Classification

### Scenario Relevance
- **Test 1 (Name Validation):** ⚠️ **Secondary Edge Case** - Form validation is important but typically covered by unit tests for the reactive form. The real user journey test would be "successfully create a machine end-to-end" rather than "verify empty name disables button."
- **Test 2 (JSON Validation):** ⚠️ **Minor Edge Case / Broken Test** - Tests an "Advanced JSON" feature that may not exist. If the feature exists conditionally (e.g., for certain backend types), the test should set up that precondition explicitly.

### Classification
| Aspect | Classification |
|--------|----------------|
| **Type** | **Interactive Unit Test** — Tests form validation logic in isolation |
| **Mocking Level** | **Low** (browser mode with SQLite) but incomplete UI flow |
| **Integration Depth** | **Shallow** — Does not complete the wizard, verify persistence, or validate created asset |

**Verdict:** These are **component behavior tests** dressed as E2E tests. They would be more reliable as Jasmine unit tests using Angular's `TestBed` and form harnesses.

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow

**Test 1: Machine Name Validation**
```
1. User navigates to app root → WelcomePage handles splash
2. User navigates to /assets → AssetsPage loads
3. User waits for any overlay dismissal
4. User clicks "Machines" tab
5. User clicks "Add Machine" button → Dialog opens
6. [INCORRECT STEP] User clicks first .category-card
7. [INCORRECT STEP] User clicks first .definition-item
8. [SHOULD BE] User should go through Type→Category→Frontend→Backend→Config steps
9. User clears Instance Name input
10. User expects Finish button to be disabled
11. User fills "Valid Machine Name"
12. User expects Finish button to be enabled
```

**Test 2: JSON Validation**
```
1-7. Same as Test 1
8. User looks for "Advanced JSON" toggle button
9. IF toggle visible:
   a. Click to expand advanced section
   b. Fill "{ invalid json }" in JSON input
   c. Expect mat-error visible
   d. Expect Finish button disabled
10. IF toggle NOT visible:
   - Test silently passes (no assertion at all)
```

### Contextual Fit
The Asset Wizard is a **core user workflow** in Praxis for adding Machines and Resources to the lab environment. It's a multi-step wizard with:
- Dynamic step rendering based on asset type (Machine vs Resource)
- Category-filtered options
- Frontend/Backend pairing for machines
- Configuration with validation

These tests **attempt** to verify form validation but fail to properly navigate the wizard's actual step structure.

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Severity | Description |
|-----|----------|-------------|
| **Complete Wizard Flow** | 🔴 HIGH | Neither test completes the wizard end-to-end. No asset is actually created. |
| **Step Navigation Verification** | 🔴 HIGH | Tests don't verify correct step progression (Type→Category→Frontend→Backend→Config→Review) |
| **Category-Specific Validation** | 🟡 MEDIUM | Tests only "first available" category/definition without testing specific categories (LiquidHandler, Plate, etc.) |
| **Backend Type Variations** | 🟡 MEDIUM | Hardware vs Simulator backends have different validation requirements (connection_info) |
| **Positive Path Testing** | 🔴 HIGH | No test verifies successful machine creation - only negative validation |

### Domain Specifics

#### Data Integrity
- ❌ **Not Verified:** No check that the machine would be correctly persisted to SQLite
- ❌ **Not Verified:** No validation of `accession_id` generation
- ❌ **Not Verified:** No verification of machine appearing in the assets table after creation

#### Simulation vs. Reality
- ❌ **Not Distinguished:** Tests don't differentiate between simulator and hardware backends, which have different form requirements
- ⚠️ **Implicit:** By clicking `.first()` on cards, tests may randomly select either simulator or hardware backends

#### Serialization
- ❌ **Not Tested:** No verification that `connection_info` or `user_configured_capabilities` are correctly serialized
- ❌ **Not Tested:** The "Advanced JSON" test inputs invalid JSON but doesn't test valid JSON handling

#### Error Handling
- ⚠️ **Partially Covered:** Tests check that invalid input disables the Finish button
- ❌ **Not Covered:** Backend errors during `createAsset()` call
- ❌ **Not Covered:** Network failures
- ❌ **Not Covered:** Duplicate name validation
- ❌ **Not Covered:** Category with no available frontends/backends

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 3/10 | Only tests form field disabling, not the actual wizard flow |
| **Best Practices** | 4/10 | Uses some role-based selectors but relies on incorrect CSS classes; no step synchronization |
| **Test Value** | 2/10 | Edge case validation tests that would be better as unit tests; conditional logic masks failures |
| **Isolation** | 5/10 | Proper beforeEach setup, uses POM, but no afterEach cleanup |
| **Domain Coverage** | 2/10 | Doesn't test machine/resource creation, persistence, or backend-specific flows |

**Overall: 3.2/10** — *Critical Failure (Flaky/Low Coverage)*

---

## Appendix: Selector Mapping

Current test selectors vs. actual wizard HTML:

| Test Selector | Exists? | Actual Selector |
|---------------|---------|-----------------|
| `.category-card` | ✓ | `[data-testid="category-card-{name}"]` preferred |
| `.definition-item` | ❌ | N/A - doesn't exist |
| `getByLabel('Instance Name')` | ✓ | Correct, or use `[data-testid="input-instance-name"]` |
| `getByLabel('Name')` | ❌ | Doesn't exist in wizard |
| `getByRole('button', { name: /Finish|Save/i })` | ⚠️ | Actual button text is "Create Asset" or "Next" |
| `getByRole('button', { name: /Advanced JSON/i })` | ❓ | Not visible in current wizard HTML |
