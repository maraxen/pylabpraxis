# E2E Enhancement Plan: screenshot_recon.spec.ts

**Target:** [screenshot_recon.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/screenshot_recon.spec.ts)  
**Baseline Score:** 1.0/10  
**Target Score:** 8.0/10 (if Option C) OR N/A (if reclassified as utility)  
**Effort Estimate:** Variable by option (5 min to 4+ hours)

---

## Strategic Decision Required

This file is a **debugging utility**, not a test. Three enhancement paths are available:

| Option | Action | Effort | Result |
|--------|--------|--------|--------|
| **A** | Reclassify as Utility | 15 min | Removed from CI, kept for debugging |
| **B** | Visual Regression Test | 2-4 hours | Integrated with Percy/Argos for diff |
| **C** | Full E2E Conversion | 4+ hours | Production-grade wizard test |

**Recommended Path:** Option A (immediate) + Option C (backlog priority)

---

## Option A: Reclassify as Utility (Immediate Action)

### Goals
1. **Remove from CI gate** — Stop false-positive test counts
2. **Preserve debugging value** — Keep for manual screenshot capture
3. **Document purpose** — Add clear utility header

### A.1 File Restructure (5 minutes)
- [ ] Rename file to `screenshot-recon.util.ts`
- [ ] Move to `e2e/utils/` directory (or create if needed)

### A.2 Configuration Update (5 minutes)
- [ ] Update `playwright.config.ts` to ignore utility files:
```typescript
export default defineConfig({
  testDir: './e2e/specs',
  testIgnore: ['**/utils/**', '**/*.util.ts'],
  // ...
});
```

### A.3 Documentation (5 minutes)
- [ ] Add header comment to file:
```typescript
/**
 * UTILITY SCRIPT (Not a Test)
 * 
 * Purpose: Capture screenshots of Protocol Runner wizard for debugging.
 * Usage: npx playwright test e2e/utils/screenshot-recon.util.ts --headed
 * 
 * Note: This file is excluded from CI runs. No assertions are performed.
 */
```

**Verification:**
```bash
# Confirm file is excluded from normal test runs
npx playwright test --list | grep -i screenshot
# Should return empty

# Manual run for debugging
npx playwright test e2e/utils/screenshot-recon.util.ts --headed
```

---

## Option B: Visual Regression Test (Medium Priority)

### Goals
1. **Automated visual diff** — Detect UI regressions via image comparison
2. **CI integration** — Baseline screenshots + PR diff workflow
3. **Snapshot management** — Version-controlled baselines

### B.1 Framework Selection
| Framework | Pros | Cons |
|-----------|------|------|
| **Playwright Built-in** | No external deps | Manual baseline management |
| **Percy** | Cloud storage, PR comments | SaaS cost |
| **Argos** | OSS, GitHub integration | Self-hosted option |

**Recommendation:** Start with Playwright built-in, migrate to Argos if volume increases.

### B.2 Implementation (2-4 hours)
- [ ] Replace `page.screenshot({ path: '/tmp/...' })` with:
```typescript
await expect(page).toHaveScreenshot('step1-protocol-selection.png', {
  maxDiffPixelRatio: 0.2,
  animations: 'disabled',
});
```

- [ ] Generate baseline snapshots:
```bash
npx playwright test screenshot-recon.spec.ts --update-snapshots
```

- [ ] Add to separate test project in `playwright.config.ts`:
```typescript
projects: [
  {
    name: 'visual-regression',
    testMatch: '**/visual/*.spec.ts',
    use: { ...devices['Desktop Chrome'] },
  },
]
```

### B.3 CI Workflow Update
- [ ] Add visual regression job to GitHub Actions
- [ ] Configure snapshot artifact upload
- [ ] Set up approval workflow for diff review

---

## Option C: Full E2E Conversion (Backlog Priority)

This converts the utility into a production-grade E2E test of the Protocol Runner wizard.

### Goals
1. **Reliability** — Eliminate flaky patterns
2. **Isolation** — Enable parallel test execution
3. **Domain Coverage** — Verify actual state changes
4. **Maintainability** — Use Page Object Model consistently

---

### Phase 1: Infrastructure & Reliability (Priority: Critical)

#### 1.1 Worker Isolation Integration
- [ ] Import and use `test` from `app.fixture.ts`:
```typescript
// Replace:
import { test, expect } from '@playwright/test';

// With:
import { test, expect, buildIsolatedUrl } from '../fixtures/app.fixture';
```

- [ ] Remove hardcoded URL, use relative path:
```typescript
// Replace:
await page.goto('http://localhost:4200/app/run?mode=browser', ...);

// With:
const url = buildIsolatedUrl('/app/run', testInfo);
await page.goto(url, { waitUntil: 'networkidle' });
```

#### 1.2 Eliminate Hardcoded Waits (6 occurrences)
Replace all `waitForTimeout(500)` with state-driven assertions:

| Current | Replacement |
|---------|-------------|
| Line 16: After dialog dismiss | `await expect(page.getByRole('heading', { name: /Execute Protocol/i })).toBeVisible()` |
| Line 31: After protocol select | `await expect(page.locator('.protocol-card.selected')).toBeVisible()` |
| Line 37: After Continue to Params | `await expect(page.getByText('Parameters')).toBeVisible()` |
| Line 42: After Continue to Machines | `await expect(page.getByText('Select Machine')).toBeVisible()` |
| Line 47: After Continue to Assets | `await expect(page.getByText('Assign Assets')).toBeVisible()` |
| Line 52: After Continue to Review | `await expect(page.getByText('Ready to Launch')).toBeVisible()` |

---

### Phase 2: Page Object Refactor

#### 2.1 Use WizardPage POM
The existing `wizard.page.ts` already has methods for most wizard interactions:

```typescript
import { WizardPage } from '../page-objects/wizard.page';

test('protocol runner wizard navigation', async ({ page }, testInfo) => {
  const wizard = new WizardPage(page);
  
  // Use POM methods instead of inline locators
  await wizard.completeParameterStep();
  await wizard.selectFirstCompatibleMachine();
  await wizard.waitForAssetsAutoConfigured();
  await wizard.advanceDeckSetup();
  await wizard.openReviewStep();
});
```

- [ ] Migrate protocol card selection to `ProtocolPage` or extend `WizardPage`
- [ ] Migration inline Continue clicks to POM method calls
- [ ] Use `WizardPage.getFormState()` for step state verification

---

### Phase 3: Domain Verification

#### 3.1 Add Step Assertions (Required for Real Test)
Add assertions that verify actual wizard state, not just UI presence:

```typescript
test('protocol wizard captures all wizard steps', async ({ page }, testInfo) => {
  // ... navigation ...

  // Step 1: Protocol Selection
  const protocolCards = page.locator('app-protocol-card');
  await expect(protocolCards.first()).toBeVisible();
  const cardCount = await protocolCards.count();
  expect(cardCount).toBeGreaterThan(0);
  // Capture screenshot AFTER assertion
  await page.screenshot({ path: '/tmp/step1_protocol_selection.png', fullPage: true });

  // Step 2: After selection - verify selected state
  await protocolCards.first().click();
  await expect(protocolCards.first()).toHaveClass(/selected/);
  await page.screenshot({ path: '/tmp/step1_protocol_selected.png', fullPage: true });

  // Continue through steps with verification...
});
```

#### 3.2 SQLite State Verification (Stretch)
Verify that wizard form state persists to database:

```typescript
const protocolState = await page.evaluate(async () => {
  const ng = (window as any).ng;
  const component = ng.getComponent(document.querySelector('app-run-protocol'));
  return {
    selectedProtocol: component.selectedProtocol?.name,
    stepIndex: component.stepper?.selectedIndex,
    isValid: component.form?.valid,
  };
});

expect(protocolState.selectedProtocol).toBeDefined();
expect(protocolState.stepIndex).toBe(0);
```

---

### Phase 4: Error State Coverage (Stretch)

#### 4.1 Empty Protocol List Handling
```typescript
test('handles empty protocol list gracefully', async ({ page }, testInfo) => {
  // Mock empty DB state
  await page.evaluate(async () => {
    const repos = await (window as any).sqliteService.getAsyncRepositories().toPromise();
    // Clear protocols for this test
    await repos.protocols.clear().toPromise();
  });

  await page.goto('/app/run?mode=browser');
  
  // Expect empty state UI
  await expect(page.getByText(/No protocols available/i)).toBeVisible();
});
```

#### 4.2 Continue Button Disabled State
```typescript
// Verify Continue is disabled when required fields missing
await expect(page.getByRole('button', { name: /Continue/i })).toBeDisabled();
```

---

## Verification Plan

### Automated
```bash
# After reclassification (Option A)
npx playwright test --list | grep -i screenshot  # Should be empty

# After E2E conversion (Option C)
npx playwright test e2e/specs/screenshot_recon.spec.ts --workers=4

# Visual regression (Option B)
npx playwright test --project=visual-regression --update-snapshots
```

### Manual Checklist (Option C)
- [ ] Test passes in isolation
- [ ] Test passes with `--workers=4`
- [ ] No `waitForTimeout` calls remain
- [ ] All wizard steps have assertions
- [ ] Screenshots saved to consistent location

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/screenshot_recon.spec.ts` | Refactor or Move | All (56 lines) |
| `e2e/utils/screenshot-recon.util.ts` | Create (Option A) | ~60 lines |
| `playwright.config.ts` | Update testIgnore | 2-3 lines |
| `e2e/page-objects/wizard.page.ts` | Extend (if needed) | 10-20 lines |

---

## Acceptance Criteria

### Option A (Reclassify)
- [ ] File excluded from `npx playwright test --list`
- [ ] File moved to `e2e/utils/` or renamed with `.util.ts`
- [ ] Documentation header added

### Option C (Full E2E)
- [ ] Tests pass with parallel execution (`--workers=4`)
- [ ] Zero `waitForTimeout` calls
- [ ] Uses `WizardPage` and/or `ProtocolPage` POMs
- [ ] Uses `app.fixture.ts` for worker isolation
- [ ] Has assertions at each wizard step
- [ ] Baseline score improves to ≥8.0/10

---

## Priority Matrix

| Action | Priority | Effort | Impact |
|--------|----------|--------|--------|
| Add `.skip` to exclude from CI | P0 | 1 min | Prevents false CI metric |
| Option A: Reclassify | P0 | 15 min | Correct categorization |
| Option C Phase 1 | P1 | 1 hour | Reliability foundation |
| Option C Phase 2 | P2 | 1 hour | Maintainability |
| Option C Phase 3 | P2 | 1-2 hours | Value upgrade |
| Option B: Visual Regression | P3 | 2-4 hours | Enhanced monitoring |
