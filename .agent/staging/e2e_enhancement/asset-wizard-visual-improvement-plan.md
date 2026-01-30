# E2E Enhancement Plan: asset-wizard-visual.spec.ts

**Target:** [asset-wizard-visual.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/asset-wizard-visual.spec.ts)  
**Baseline Score:** 2.2/10  
**Target Score:** 8.0/10  
**Effort Estimate:** Medium (4-6 hours) — Significant refactor needed + visual baseline generation

---

## Goals

1. **Visual Regression** — Convert from screenshot capture to proper visual regression testing with baselines
2. **Reliability** — Eliminate force clicks and hardcoded waits
3. **Isolation** — Enable parallel test execution with worker-indexed DB
4. **Consolidation** — Reduce duplication with asset-wizard.spec.ts via shared POM

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Replace raw `@playwright/test` import with `fixtures/worker-db.fixture`
- [ ] Use `gotoWithWorkerDb()` helper for navigation
- [ ] Add `testInfo` parameter for worker index access

**Current:**
```typescript
import { test, expect } from '@playwright/test';
// ...
await page.goto('/assets?mode=browser&resetdb=1');
```

**Target:**
```typescript
import { test, expect, gotoWithWorkerDb } from '../fixtures/worker-db.fixture';
// ...
await gotoWithWorkerDb(page, '/assets', testInfo, { resetdb: true });
```

### 1.2 Eliminate Force Clicks
- [ ] Remove `force: true` from Add Asset button click (line 58)
- [ ] Add proper overlay dismissal before click:
  ```typescript
  await expect(page.locator('.cdk-overlay-backdrop')).not.toBeVisible();
  await addAssetBtn.click();
  ```
- [ ] If overlays persist, investigate and fix in `app.fixture.ts` welcome dialog handling

### 1.3 Replace Hardcoded Waits
- [ ] Remove `waitForTimeout(500)` at line 98
- [ ] Replace with animation completion check:
  ```typescript
  // Wait for any CSS animations to complete
  await page.waitForFunction(() => !document.querySelector('.result-card.animating'));
  // Or use stable locator assertion
  await expect(wizard.locator('.result-card').first()).toBeVisible();
  ```

### 1.4 Add Cleanup Hook
- [ ] Add `afterEach` to close wizard and reset state:
  ```typescript
  test.afterEach(async ({ page }) => {
      await page.keyboard.press('Escape');
      await expect(page.locator('app-asset-wizard')).not.toBeVisible({ timeout: 5000 }).catch(() => {});
  });
  ```

---

## Phase 2: Visual Regression Conversion (Priority: High)

### 2.1 Replace Screenshot Capture with Visual Assertions
- [ ] Convert all `page.screenshot({ path: ... })` to `expect(page).toHaveScreenshot()`
- [ ] Generate baseline images on first run

**Current (3 locations):**
```typescript
await page.screenshot({ path: 'praxis/web-client/e2e/screenshots/new-wizard-step1-types.png' });
```

**Target:**
```typescript
await expect(page).toHaveScreenshot('wizard-step1-types.png', {
    maxDiffPixels: 100,
    mask: [page.locator('.timestamp')], // Mask dynamic content
});
```

### 2.2 Configure Visual Regression Thresholds
- [ ] Add visual comparison config to `playwright.config.ts`:
  ```typescript
  expect: {
      toHaveScreenshot: {
          maxDiffPixels: 100,
          threshold: 0.1,
      },
  },
  ```

### 2.3 Generate Golden Baselines
- [ ] Run test with `--update-snapshots` flag to generate baseline images
- [ ] Commit baseline images to `e2e/screenshots/asset-wizard-visual.spec.ts-snapshots/`

---

## Phase 3: Assertion Strengthening (Priority: High)

### 3.1 Mock Data Verification
- [ ] Assert exact card counts matching mock data:

**Current (weak):**
```typescript
expect(catCount).toBeGreaterThan(0);
expect(resultCount).toBeGreaterThan(0);
```

**Target (strong):**
```typescript
// Step 2: Categories - mock provides 5 categories
await expect(wizard.locator('.category-card')).toHaveCount(5);

// Step 3: Results - mock provides 5 LiquidHandler machines
await expect(wizard.locator('.result-card')).toHaveCount(5);
```

### 3.2 Remove Fallback Logic
- [ ] Delete fallback to first card (lines 81-85)
- [ ] Fail explicitly if mocked data not rendered:

**Current (masks failures):**
```typescript
let lhCard = wizard.locator('.category-card').filter({ hasText: 'LiquidHandler' }).first();
if (!(await lhCard.isVisible())) {
    lhCard = wizard.locator('.category-card').first();
}
```

**Target (explicit):**
```typescript
const lhCard = wizard.locator('.category-card').filter({ hasText: 'LiquidHandler' });
await expect(lhCard).toBeVisible({ timeout: 5000 }); // Fail if mock not applied
await lhCard.click();
```

### 3.3 Replace Empty Catch Blocks
- [ ] Remove `catch (e) {}` and replace with explicit handling:

**Current:**
```typescript
try {
    // ... welcome dismissal
} catch (e) { }
```

**Target:**
```typescript
// Use fixture's built-in welcome dismissal or explicit timeout handling
const dismissBtn = page.getByRole('button', { name: /Get Started|Skip|Close/i }).first();
await dismissBtn.click({ timeout: 3000 }).catch(() => {
    console.log('[Test] No welcome dialog to dismiss');
});
```

---

## Phase 4: Selector Modernization (Priority: Medium)

### 4.1 Add data-testid Attributes (Frontend Change)
- [ ] Add data-testid to asset type cards:
  ```html
  <div class="type-card" data-testid="asset-type-machine">...</div>
  ```
- [ ] Add data-testid to category cards:
  ```html
  <div class="category-card" data-testid="category-liquid-handler">...</div>
  ```
- [ ] Add data-testid to result cards:
  ```html
  <div class="result-card" data-testid="definition-hamilton-star">...</div>
  ```

### 4.2 Update Selectors in Test
- [ ] Replace CSS class selectors with testid selectors:

**Current:**
```typescript
wizard.locator('.type-card')
wizard.locator('.category-card')
wizard.locator('.result-card')
```

**Target:**
```typescript
wizard.getByTestId('asset-type-machine')
wizard.getByTestId(/^category-/) // Matches all category cards
wizard.getByTestId(/^definition-/) // Matches all definition cards
```

---

## Phase 5: Responsive Grid Testing (Stretch Goal)

### 5.1 Add Viewport Tests
- [ ] Create parameterized test for multiple viewports:
  ```typescript
  const viewports = [
      { name: 'desktop', width: 1920, height: 1080 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'mobile', width: 375, height: 667 },
  ];

  for (const vp of viewports) {
      test(`grid layout at ${vp.name} viewport`, async ({ page }) => {
          await page.setViewportSize({ width: vp.width, height: vp.height });
          // ... navigation and assertions
          await expect(page).toHaveScreenshot(`wizard-step3-grid-${vp.name}.png`);
      });
  }
  ```

### 5.2 Grid Column Verification
- [ ] Add computed style assertions for grid layout:
  ```typescript
  const gridColumns = await page.evaluate(() => {
      const grid = document.querySelector('.results-grid');
      return getComputedStyle(grid).gridTemplateColumns;
  });
  expect(gridColumns).toMatch(/repeat\(auto-fill/); // Verify responsive grid
  ```

---

## Phase 6: Consolidation with asset-wizard.spec.ts (Optional)

### 6.1 Create Shared WizardPage POM
- [ ] Create `e2e/pages/wizard.page.ts` with shared navigation methods
- [ ] Extract `navigateToStep3()` helper for both tests

### 6.2 Parameterize Screenshot Capture
- [ ] Add screenshot option to functional test:
  ```typescript
  test.use({ captureScreenshots: true }); // Enable for visual test project
  ```

---

## Verification Plan

### Automated (Post-Refactor)
```bash
# Run single file with visual regression
npx playwright test e2e/specs/asset-wizard-visual.spec.ts --update-snapshots

# Verify parallel safety
npx playwright test e2e/specs/asset-wizard-visual.spec.ts --workers=4

# Run with trace for debugging
npx playwright test e2e/specs/asset-wizard-visual.spec.ts --trace on
```

### Manual Verification
- [ ] Confirm baseline images generated in `e2e/specs/asset-wizard-visual.spec.ts-snapshots/`
- [ ] Verify no `force: true` clicks remain
- [ ] Verify no `waitForTimeout` calls remain
- [ ] Confirm wizard closes properly after test

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/asset-wizard-visual.spec.ts` | Major Refactor | ~80 lines → ~100 lines |
| `e2e/pages/wizard.page.ts` | Create (Optional) | ~50 new lines |
| `playwright.config.ts` | Add visual config | ~10 lines |
| Frontend component files | Add data-testid | ~6 lines if selector modernization applied |

---

## Acceptance Criteria

- [ ] All tests pass with `--workers=4` (parallel execution)
- [ ] Zero `force: true` clicks in test file
- [ ] Zero `waitForTimeout` calls in test file
- [ ] Uses `worker-db.fixture` for isolation
- [ ] Uses `expect(page).toHaveScreenshot()` for visual regression
- [ ] Baseline images committed to repository
- [ ] Explicit assertions for mock data (card counts match mock)
- [ ] No empty catch blocks
- [ ] Test score improves from 2.2/10 to ≥8.0/10

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Baseline image churn | Use masking for dynamic content (timestamps, animations) |
| CI environment differences | Pin browser versions, use containerized Playwright |
| Mock data dependency | Consider splitting into pure visual test (with mocks) and integration visual test (real data) |
| Frontend selector changes | Coordinate data-testid additions with frontend team |

---

## Decision Point: Test Retention vs. Deletion

Given the 70% overlap with `asset-wizard.spec.ts`, consider whether this test should:

**Option A: Enhance & Keep**
- Convert to true visual regression
- Add responsive viewport testing
- Value: Catches visual regressions in grid layout

**Option B: Merge & Delete**
- Add screenshot checkpoints to `asset-wizard.spec.ts`
- Delete `asset-wizard-visual.spec.ts`
- Value: Reduces maintenance burden, single source of truth

**Recommendation**: **Option A** if grid layout is actively being optimized. **Option B** if grid design is stable and maintenance burden is a concern.
