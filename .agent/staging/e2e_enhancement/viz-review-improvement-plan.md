# E2E Enhancement Plan: viz-review.spec.ts

**Target:** [viz-review.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/viz-review.spec.ts)  
**Baseline Score:** 1.6/10  
**Target Score:** 7.0/10 (utility suite target, not full E2E)  
**Effort Estimate:** Medium (4-6 hours)

---

## Goals

1. **Reclassify** — Acknowledge this as a visual capture utility, not E2E test
2. **Reliability** — Eliminate flaky patterns (hardcoded waits, force clicks)
3. **Modernization** — Use Playwright's visual comparison features
4. **Isolation** — Enable parallel execution if kept as test

---

## Decision Point: Keep or Reclassify?

Before proceeding, decide the intent of this file:

### Option A: Keep as Visual Capture Utility
- Move to `e2e/utilities/viz-capture.spec.ts`
- Skip in CI via project configuration
- Keep for manual documentation generation

### Option B: Convert to Visual Regression Test
- Use `toHaveScreenshot()` with baselines
- Add to CI with visual comparison thresholds
- More valuable for catching unintended UI changes

### Option C: Convert to Functional E2E Tests
- Add actual assertions for each captured state
- Validate data loading, theme persistence, responsive behavior
- Most effort, highest value

**Recommendation:** Option B provides best value/effort ratio.

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Import from `./fixtures/worker-db.fixture` instead of `@playwright/test`
- [ ] Use `gotoWithWorkerDb()` for navigation
- [ ] Remove `resetdb=0` (anti-pattern for isolation)

```typescript
// Before
import { test, expect } from '@playwright/test';
await page.goto(`${APP_URL}/app/home?${MODE_PARAMS}`);

// After
import { test, expect, gotoWithWorkerDb } from '../fixtures/worker-db.fixture';
await gotoWithWorkerDb(page, '/app/home', testInfo);
```

### 1.2 Eliminate Hardcoded Waits (13 instances)
- [ ] Remove all `waitForTimeout(5000)` calls
- [ ] Remove all `waitForTimeout(2000)` calls
- [ ] Replace with state-driven waits

| Current | Replacement |
|---------|-------------|
| `waitForTimeout(5000)` after navigation | `waitForSqliteReady()` from fixture |
| `waitForTimeout(2000)` before screenshot | `page.locator('.sidebar-rail').waitFor()` |
| `waitForTimeout(500)` after hover | `expect(tooltip).toBeVisible()` |
| `waitForTimeout(1000)` after theme toggle | `expect(body).toHaveClass(/dark-mode/)` |

### 1.3 Replace Force Clicks (3 instances)
- [ ] Line 90: `themeToggle.click({ force: true })`
- [ ] Line 107: `themeToggle.click({ force: true })`
- [ ] Line 108: `themeToggle.click({ force: true })`

**Fix Strategy:**
```typescript
// Before
await themeToggle.click({ force: true });

// After
await page.waitForLoadState('networkidle');
await themeToggle.click();
// Or use BasePage.waitForOverlay() if CDK overlays are the issue
```

### 1.4 Fix Error Swallowing
- [ ] Line 60: Replace `.catch(() => console.log(...))` with proper handling
- [ ] Line 123: Replace `.catch(() => {})` with assertion or skip

```typescript
// Before
await navRail.waitFor({ state: 'visible', timeout: 30000 })
  .catch(() => console.log('Sidebar rail not visible after 30s'));

// After
await navRail.waitFor({ state: 'visible', timeout: 30000 });
// Let test fail if critical element not visible
// OR mark as conditional:
test.skip(!await navRail.isVisible(), 'Nav rail not available in this environment');
```

---

## Phase 2: Convert to Visual Regression (Option B)

### 2.1 Add Visual Comparison
Replace raw screenshots with `toHaveScreenshot()`:

```typescript
// Before
await page.screenshot({ path: path.join(screenshotDir, 'asset-library.png') });

// After
await expect(page).toHaveScreenshot('asset-library.png', {
  maxDiffPixels: 100,  // Allow minor variations
  mask: [page.locator('.dynamic-timestamp')],  // Mask volatile elements
});
```

### 2.2 Create Baseline Snapshots
```bash
npx playwright test e2e/specs/viz-review.spec.ts --update-snapshots
```
Baselines stored in `e2e/specs/viz-review.spec.ts-snapshots/`.

### 2.3 Configure CI Thresholds
```typescript
// playwright.config.ts
export default defineConfig({
  expect: {
    toHaveScreenshot: { maxDiffPixelRatio: 0.01 }
  }
});
```

---

## Phase 3: Page Object Refactor

### 3.1 Use Existing POMs
- [ ] Create `ThemeSwitcherComponent` for theme toggle interactions
- [ ] Use `ProtocolLibraryPage` for protocol navigation
- [ ] Use `WorkcellPage` for simulation interactions

### 3.2 Extract Reusable Helpers
```typescript
// e2e/helpers/screenshot.helpers.ts
export async function captureWithTheme(
  page: Page,
  themeName: 'light' | 'dark',
  screenshotName: string
) {
  const themeToggle = page.locator('[data-tour-id="theme-toggle"]');
  // Toggle to desired theme
  // Verify theme applied
  await expect(page).toHaveScreenshot(screenshotName);
}
```

---

## Phase 4: Add Functional Assertions (Option C - Stretch)

If converting to true E2E:

### 4.1 Asset Library Validation
```typescript
// After navigation, verify data loaded
await page.goto(`${APP_URL}/app/assets?${MODE_PARAMS}`);
await expect(page.getByRole('table')).toBeVisible();
await expect(page.getByRole('row')).toHaveCount.greaterThan(1);
```

### 4.2 Theme Persistence
```typescript
// Toggle to dark mode
await themeToggle.click();
await expect(page.locator('body')).toHaveClass(/dark-theme|theme-dark/);
// Navigate away and back
await page.goto(`${APP_URL}/app/protocols?${MODE_PARAMS}`);
await expect(page.locator('body')).toHaveClass(/dark-theme|theme-dark/);
```

### 4.3 Responsive Behavior
```typescript
await page.setViewportSize({ width: 768, height: 1024 });
await expect(page.locator('.sidebar-rail')).toHaveCSS('width', '64px');
// Or assert collapsed state
await expect(page.locator('.sidebar-expanded')).not.toBeVisible();
```

---

## Phase 5: Mark as Skip in CI (if utility)

If keeping as utility only:

```typescript
test.describe('Visual Review Screenshot Capture', () => {
  // Skip in CI, run only locally for documentation
  test.skip(process.env.CI === 'true', 'Visual capture utility - run locally only');
  
  // Or use tags
  // npx playwright test --grep-invert @visual
```

---

## Verification Plan

### Automated
```bash
# Run with visual comparison
npx playwright test e2e/specs/viz-review.spec.ts --update-snapshots

# Verify parallel execution
npx playwright test e2e/specs/viz-review.spec.ts --workers=4

# Check for hardcoded waits (should return 0)
grep -c "waitForTimeout" praxis/web-client/e2e/specs/viz-review.spec.ts
```

### Manual Checklist
- [ ] All screenshots captured successfully
- [ ] Visual baselines match expected appearance
- [ ] No force clicks remain
- [ ] No waitForTimeout calls remain
- [ ] Tests pass in parallel

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/viz-review.spec.ts` | Refactor | ~100 |
| `e2e/helpers/screenshot.helpers.ts` | Create | ~50 (new) |
| `e2e/page-objects/theme.component.ts` | Create | ~30 (new) |
| `playwright.config.ts` | Update | ~5 |

---

## Acceptance Criteria

- [ ] Tests pass with parallel execution (`--workers=4`)
- [ ] Zero `force: true` clicks
- [ ] Zero `waitForTimeout` calls
- [ ] Uses worker-indexed DB isolation OR is marked as CI-skip utility
- [ ] Either: Uses `toHaveScreenshot()` for regression, OR is reclassified to utilities
- [ ] Error handling is explicit (no swallowed `.catch()`)
- [ ] Baseline score improves to ≥7.0/10 (adjusted target for utility suite)

---

## Priority Ranking

| Task | Priority | Effort | Impact |
|------|----------|--------|--------|
| Remove hardcoded waits | P0 - Critical | Low | High |
| Remove force clicks | P0 - Critical | Low | High |
| Fix error swallowing | P1 - High | Low | Medium |
| Worker DB isolation | P1 - High | Medium | High |
| Convert to toHaveScreenshot | P2 - Medium | Medium | High |
| Add functional assertions | P3 - Low | High | Medium |
| Move to utilities directory | P3 - Low | Low | Low |
