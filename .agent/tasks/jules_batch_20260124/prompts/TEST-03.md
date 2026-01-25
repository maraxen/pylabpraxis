# TEST-03: Create Workcell Dashboard E2E Test

## Context

**File to Create**: `praxis/web-client/e2e/specs/workcell-dashboard.spec.ts`
**Route**: `/app/workcell`
**Reference**: Look at `smoke.spec.ts` and `monitor-detail.spec.ts` for patterns

## Requirements

Create E2E tests for the workcell dashboard:

```typescript
import { test, expect } from '@playwright/test';

test.describe('Workcell Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/app/workcell');
    // Wait for page load
    await page.waitForLoadState('networkidle');
  });

  test('should display workcell overview', async ({ page }) => {
    // Verify main container loads
    await expect(page.locator('app-workcell')).toBeVisible();
    
    // Take screenshot for visual reference
    await page.screenshot({ path: 'test-results/workcell-overview.png' });
  });

  test('should display workcell cards', async ({ page }) => {
    // Wait for cards to render
    const cards = page.locator('[data-testid="workcell-card"], .workcell-card, mat-card');
    await expect(cards.first()).toBeVisible({ timeout: 10000 });
  });

  test('should navigate to workcell detail on click', async ({ page }) => {
    const firstCard = page.locator('[data-testid="workcell-card"], .workcell-card, mat-card').first();
    await firstCard.click();
    
    // Verify navigation occurred
    await expect(page).toHaveURL(/\/app\/workcell\/.+/);
  });
});
```

Do NOT:

- Modify existing test files
- Add dependencies not already in package.json
- Create page objects (keep simple for now)

## Acceptance Criteria

- [ ] Test file created at specified path
- [ ] At least 3 test cases
- [ ] Screenshots captured for visual reference
- [ ] Tests pass: `npx playwright test workcell-dashboard --project=chromium`
