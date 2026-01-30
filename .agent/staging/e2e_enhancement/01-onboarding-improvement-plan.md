# E2E Enhancement Plan: 01-onboarding.spec.ts

**Target:** [01-onboarding.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/01-onboarding.spec.ts)  
**Baseline Score:** 3.8/10  
**Target Score:** 8.0/10  
**Effort Estimate:** Low-Medium (~2-3 hours)

---

## Goals

1. **Reliability** — Eliminate silent error swallowing and brittle selectors
2. **Isolation** — Enable parallel test execution with worker-indexed DB
3. **Domain Coverage** — Verify onboarding state persistence and dashboard content
4. **Maintainability** — Refactor to use consistent POM patterns and user-facing locators

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Import `test` from `../fixtures/worker-db.fixture` instead of `@playwright/test`
- [ ] Pass `testInfo` to `WelcomePage` constructor for DB isolation
- [ ] Use `BasePage.goto()` which includes `?dbName=praxis-worker-{N}&resetdb=1`

**Code Change (Spec):**
```typescript
import { test, expect } from '../fixtures/worker-db.fixture';
import { WelcomePage } from '../page-objects/welcome.page';

test.describe('First-Time User Experience', () => {
    test('should show welcome screen and navigate to dashboard', async ({ page }, testInfo) => {
        const welcomePage = new WelcomePage(page, testInfo);
        // ...
    });
});
```

**Code Change (WelcomePage):**
```typescript
constructor(page: Page, testInfo?: TestInfo) {
    super(page, '/', testInfo);
    // ...
}
```

### 1.2 Remove Duplicative Navigation
- [ ] Remove `beforeEach` block that navigates and reloads
- [ ] Handle localStorage clearing inside `WelcomePage.goto()` or via `addInitScript`

**Rationale:** The current `beforeEach` navigates, clears storage, and reloads. Then the test calls `goto()` again. This is 3 navigations for 1 test.

**Better Pattern:**
```typescript
async goto() {
    // Clear storage before navigation to ensure clean slate
    await this.page.addInitScript(() => {
        localStorage.clear();
    });
    await super.goto(); // BasePage handles mode=browser, resetdb, dbName
}
```

### 1.3 Replace Silent Error Swallowing
- [ ] Remove `try/catch` in `handleSplashScreen()` that swallows splash timeout
- [ ] Use explicit assertion with clear error message

**Before:**
```typescript
try {
    await this.splashScreen.waitFor({ state: 'visible', timeout: 5000 });
    // ...
} catch (e) {
    console.log('Splash screen skipped or not present');
}
```

**After:**
```typescript
// For first-time user, splash MUST appear
await expect(this.splashScreen).toBeVisible({ timeout: 10000 });
await this.dismissSplash();
```

---

## Phase 2: Selector Modernization

### 2.1 Replace CSS Class Selectors with ARIA/Role Locators
- [ ] Replace `.sidebar-rail` with `getByRole('navigation')` or add `data-testid`

**Current (Brittle):**
```typescript
await expect(this.page.locator('.sidebar-rail')).toBeVisible({ timeout: 10000 });
```

**Improved (Semantic):**
```typescript
// Option A: ARIA role (requires role="navigation" on the element)
await expect(this.page.getByRole('navigation', { name: /main/i })).toBeVisible({ timeout: 10000 });

// Option B: Test ID (requires data-testid="sidebar-rail" on the element)
await expect(this.page.getByTestId('sidebar-rail')).toBeVisible({ timeout: 10000 });
```

### 2.2 Add Test IDs to Component (If needed)
- [ ] Add `data-testid="sidebar-rail"` to `unified-shell.component.ts` if ARIA role is not appropriate

---

## Phase 3: Domain Verification

### 3.1 Verify Onboarding State Persistence
- [ ] After dismissing splash, assert that localStorage contains onboarding flag

```typescript
async verifyOnboardingCompleted() {
    const onboardingFlag = await this.page.evaluate(() => 
        localStorage.getItem('praxis_onboarding_completed')
    );
    expect(onboardingFlag).toBe('true');
}
```

### 3.2 Verify Dashboard Content (Beyond Sidebar)
- [ ] Assert presence of key dashboard elements: workcell summary, quick actions, etc.

```typescript
async verifyDashboardLoaded() {
    // Sidebar is visible
    await expect(this.page.getByTestId('sidebar-rail')).toBeVisible({ timeout: 10000 });
    
    // Dashboard content area is populated
    await expect(this.page.getByRole('heading', { name: /Dashboard/i })).toBeVisible();
    
    // At least one widget is visible (e.g., workcell summary or quick action)
    await expect(this.page.getByTestId('dashboard-widget').first()).toBeVisible();
}
```

### 3.3 Add Tutorial Flow Test (New Test Case)
- [ ] Create separate test for "Start Tutorial" path

```typescript
test('should complete tutorial flow when clicking Start Tutorial', async ({ page }, testInfo) => {
    const welcomePage = new WelcomePage(page, testInfo);
    await welcomePage.goto();
    
    await welcomePage.startTutorial();
    await welcomePage.verifyTutorialStep(1, /Welcome/);
    await welcomePage.advanceTutorial();
    await welcomePage.verifyTutorialStep(2, /Assets/);
    // ... verify all tutorial steps
    await welcomePage.completeTutorial();
    await welcomePage.verifyOnboardingCompleted();
});
```

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Negative Test: Returning User Bypass
- [ ] Test that returning user (with onboarding flag set) skips splash entirely

```typescript
test('should bypass splash for returning user', async ({ page }, testInfo) => {
    // Set flag before navigation
    await page.addInitScript(() => {
        localStorage.setItem('praxis_onboarding_completed', 'true');
    });
    
    const welcomePage = new WelcomePage(page, testInfo);
    await welcomePage.gotoNoSplash();
    
    // Splash should NOT appear
    await expect(welcomePage.splashScreen).not.toBeVisible({ timeout: 2000 });
    await welcomePage.verifyDashboardLoaded();
});
```

---

## Verification Plan

### Automated
```bash
# Single test (development)
npx playwright test e2e/specs/01-onboarding.spec.ts --headed

# Parallel execution (CI validation)
npx playwright test e2e/specs/01-onboarding.spec.ts --workers=4
```

### Manual Checklist
- [ ] Run test 5x consecutively to check for flakiness
- [ ] Verify no `console.log` swallowed errors in trace
- [ ] Confirm trace shows single navigation per test

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/01-onboarding.spec.ts` | Refactor | ~20 → ~50 |
| `e2e/page-objects/welcome.page.ts` | Refactor | ~36 → ~60 |
| `src/app/layout/unified-shell.component.ts` | Add TestID | +1 line |

---

## Acceptance Criteria

- [ ] Tests pass with parallel execution (`--workers=4`)
- [ ] Zero silent `catch` blocks that swallow errors
- [ ] Zero CSS class selectors (use ARIA roles or TestIDs)
- [ ] Uses `worker-db.fixture` for isolation
- [ ] Verifies `localStorage` onboarding flag post-dismissal
- [ ] Includes returning-user bypass test
- [ ] Baseline score improves from 3.8 → ≥8.0/10

---

## Priority Order

1. **Phase 1.1** (Worker Isolation) — Enables parallel CI runs
2. **Phase 1.3** (Remove Silent Catch) — Prevents masked failures
3. **Phase 2.1** (Selector Modernization) — Reduces brittleness
4. **Phase 3.1** (State Persistence) — Validates actual onboarding logic
5. **Phase 3.3** (Tutorial Flow) — Expands coverage to critical path
6. **Phase 4.1** (Returning User) — Edge case coverage
