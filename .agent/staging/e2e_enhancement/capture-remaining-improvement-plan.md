# E2E Enhancement Plan: capture-remaining.spec.ts

**Target:** [capture-remaining.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/capture-remaining.spec.ts)  
**Baseline Score:** 1.8/10  
**Target Score:** 6.0/10 (or Reclassify as Visual Utility)  
**Effort Estimate:** 2-3 hours (Option A) or 30 min reclassification (Option B)

---

## Goals

1. **Reclassify** — Determine if this should be a test or a utility script
2. **Reliability** — Eliminate hardcoded waits and fragile selectors
3. **Isolation** — Enable parallel test execution with worker-indexed DB
4. **Maintainability** — Apply Page Object Model for dialog interactions

---

## Decision Point: Test vs. Utility Script

### Option A: Convert to Functional E2E Tests
If these dialogs are critical to verify functionally, convert them to real tests with assertions about dialog content.

### Option B: Reclassify as Visual Capture Script (Recommended)
Move to a dedicated `e2e/visual-capture/` directory and exclude from CI. Run on-demand for documentation.

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Replace `import { test, expect } from '@playwright/test'` with `import { test, expect } from '../fixtures/worker-db.fixture'`
- [ ] Pass `testInfo` to navigation helpers for worker-indexed DB names

**Current:**
```typescript
import { test, expect } from '@playwright/test';
// ...
await page.goto('/app/home');
```

**Target:**
```typescript
import { test, expect } from '../fixtures/worker-db.fixture';
import { gotoWithWorkerDb } from '../fixtures/worker-db.fixture';
// ...
await gotoWithWorkerDb(page, '/app/home', testInfo, { resetdb: true });
```

### 1.2 Eliminate Hardcoded Waits
- [ ] Remove `waitForTimeout(1000)` in `captureDialog()` — trust Playwright's auto-wait
- [ ] Remove `waitForTimeout(1000)` before pressing Enter in hardware discovery test

**Current:**
```typescript
await page.waitForTimeout(1000);
await page.screenshot({ path: ... });
```

**Target:**
```typescript
// No arbitrary wait; dialog visibility already asserted above
await page.screenshot({ path: ... });
```

### 1.3 Fix Fragile Command Palette Selector
- [ ] Replace `page.locator('input')` with a scoped or role-based selector

**Current:**
```typescript
await page.locator('input').fill('Discover');
```

**Target:**
```typescript
// Option 1: Use Command Palette specific selector
const commandInput = page.getByRole('combobox', { name: /command/i })
  .or(page.locator('[data-testid="command-palette-input"]'));
await commandInput.fill('Discover');

// Option 2: Wait for command palette dialog then scope
const palette = page.getByRole('dialog');
await palette.locator('input').fill('Discover');
```

### 1.4 Use `addInitScript` for LocalStorage
- [ ] Replace `page.evaluate` localStorage manipulation with `addInitScript`

**Current:**
```typescript
test.beforeEach(async ({ page }) => {
    await page.goto('/app/home');
    // Wait for SQLite...
    await page.evaluate(() => {
        localStorage.setItem('praxis_onboarding_completed', 'true');
    });
});
```

**Target:**
```typescript
test.beforeEach(async ({ page }, testInfo) => {
    // Set localStorage BEFORE page loads
    await page.addInitScript(() => {
        window.localStorage.setItem('praxis_onboarding_completed', 'true');
    });
    await gotoWithWorkerDb(page, '/app/home', testInfo, { resetdb: true });
});
```

---

## Phase 2: Selector Improvements

### 2.1 Replace Implementation Details with User-Facing Locators
- [ ] Replace `[data-tour-id="import-protocol-btn"]` with role-based locator

**Current:**
```typescript
const uploadBtn = page.locator('[data-tour-id="import-protocol-btn"]');
```

**Target:**
```typescript
const uploadBtn = page.getByRole('button', { name: /import|upload protocol/i });
```

### 2.2 Type the Helper Function
- [ ] Add TypeScript types to `captureDialog`

**Current:**
```typescript
async function captureDialog(page, name) {
```

**Target:**
```typescript
async function captureDialog(page: Page, name: string): Promise<void> {
```

---

## Phase 3: Logical Flow Cleanup

### 3.1 Fix Contradictory Welcome Test
- [ ] Remove redundant localStorage set in `beforeEach` (or use test-specific hook)

**Issue:** `beforeEach` sets `praxis_onboarding_completed: true`, then the welcome test removes it. This is wasteful and confusing.

**Target:**
```typescript
test('17. welcome-dialog.png', async ({ page }, testInfo) => {
    // Don't set onboarding in addInitScript for this test
    await page.addInitScript(() => {
        window.localStorage.removeItem('praxis_onboarding_completed');
    });
    await gotoWithWorkerDb(page, '/app/home?welcome=true', testInfo, { resetdb: true });
    await captureDialog(page, 'welcome-dialog.png');
});
```

---

## Phase 4: Optional — Convert to Functional Tests

If keeping as E2E tests, add content assertions:

### 4.1 Protocol Upload Dialog
- [ ] Assert dialog title exists
- [ ] Assert file input or drop zone exists
- [ ] Assert cancel/submit buttons exist

```typescript
const dialog = page.getByRole('dialog');
await expect(dialog).toBeVisible();
await expect(dialog.getByRole('heading')).toContainText(/upload|import/i);
await expect(dialog.getByRole('button', { name: /cancel/i })).toBeVisible();
```

### 4.2 Hardware Discovery Dialog
- [ ] Assert dialog shows discovery UI
- [ ] Assert loading/scanning indicator or device list exists

### 4.3 Welcome Dialog
- [ ] Assert welcome message text
- [ ] Assert "Get Started" or onboarding CTA exists

---

## Phase 5: Reclassification (Alternative Path)

If these remain screenshot utilities:

### 5.1 Move to Dedicated Directory
- [ ] Create `e2e/visual-capture/` directory
- [ ] Move `capture-remaining.spec.ts` to `e2e/visual-capture/dialogs.capture.ts`

### 5.2 Exclude from CI
- [ ] Update `playwright.config.ts` to exclude `visual-capture/**` from default runs

```typescript
// playwright.config.ts
export default defineConfig({
  testDir: './e2e/specs', // Excludes visual-capture
  projects: [
    {
      name: 'visual-capture',
      testDir: './e2e/visual-capture',
      testMatch: '*.capture.ts',
      // Run manually: npx playwright test --project=visual-capture
    }
  ]
});
```

### 5.3 Add Documentation
- [ ] Add `README.md` in `e2e/visual-capture/` explaining purpose and usage

---

## Verification Plan

### Automated
```bash
# Single worker (isolated)
npx playwright test e2e/specs/capture-remaining.spec.ts --workers=1

# Parallel (requires fixture migration)
npx playwright test e2e/specs/capture-remaining.spec.ts --workers=4
```

### Manual
- Verify screenshots are generated in `e2e/screenshots/dialogs/`
- Confirm no `Error: strict mode violation` from non-unique selectors

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/capture-remaining.spec.ts` | Refactor | ~40 (imports, waits, selectors) |
| `playwright.config.ts` | Update (if reclassifying) | ~5 |
| `e2e/visual-capture/README.md` | Create (if reclassifying) | ~20 |

---

## Acceptance Criteria

- [ ] Zero `waitForTimeout` calls
- [ ] Uses `worker-db.fixture` OR is moved out of CI path
- [ ] Command palette selector is scoped/unique
- [ ] Uses `addInitScript` for localStorage
- [ ] TypeScript types applied to helper functions
- [ ] Baseline score improves to ≥6.0/10 (if kept as test)

---

## Priority Matrix

| Task | Impact | Effort | Priority |
|------|--------|--------|----------|
| Remove hardcoded waits | High | Low | P0 |
| Worker isolation fixture | High | Medium | P0 |
| Fix command palette selector | High | Low | P0 |
| addInitScript migration | Medium | Low | P1 |
| Reclassify to visual-capture | Medium | Low | P1 |
| Add functional assertions | Medium | High | P2 |
