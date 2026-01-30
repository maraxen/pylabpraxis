# E2E Enhancement Plan: protocol-execution.spec.ts

**Target:** [protocol-execution.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/protocol-execution.spec.ts)  
**Baseline Score:** 4.8/10  
**Target Score:** 8.0/10  
**Effort Estimate:** 4-6 hours

---

## Goals

1. **Reliability** — Eliminate flaky patterns and enable parallel execution
2. **Isolation** — Integrate worker-indexed database fixture
3. **Domain Coverage** — Verify serialization, persistence, and error states
4. **Maintainability** — Consolidate duplicated fixture logic into reusable patterns

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration

**File:** `protocol-execution.spec.ts`

- [ ] Replace import statement:
  ```diff
  - import { test, expect } from '@playwright/test';
  + import { test, expect } from '../fixtures/app.fixture';
  ```

- [ ] Remove manual SQLite polling (lines 14-18) — fixture handles this automatically:
  ```diff
  - await page.waitForFunction(
  -     () => (window as any).sqliteService?.isReady$?.getValue() === true,
  -     null,
  -     { timeout: 30000 }
  - );
  ```

- [ ] Remove manual welcome dialog handling (lines 29-34) — fixture handles this:
  ```diff
  - const welcomeDialog = page.getByRole('dialog', { name: /Welcome to Praxis/i });
  - if (await welcomeDialog.isVisible({ timeout: 5000 })) {
  -     console.log('Dismissing Welcome Dialog...');
  -     await page.getByRole('button', { name: /Skip for Now/i }).click();
  -     await expect(welcomeDialog).not.toBeVisible();
  - }
  ```

### 1.2 Eliminate Hardcoded Screenshot Paths

- [ ] Replace hardcoded `/tmp` paths with Playwright's artifact system:
  ```diff
  - await page.screenshot({ path: '/tmp/e2e-protocol/01-protocol-library.png' });
  + // Use Playwright's testInfo for proper artifact handling
  + await test.info().attach('protocol-library', {
  +     body: await page.screenshot(),
  +     contentType: 'image/png'
  + });
  ```

- [ ] Alternatively, use relative paths within the test output directory:
  ```typescript
  const screenshotPath = path.join(test.info().outputDir, 'protocol-library.png');
  await page.screenshot({ path: screenshotPath });
  ```

### 1.3 Fix Silent URL Wait Failure

- [ ] Replace swallowed exception with explicit assertion:
  ```diff
  - await page.waitForURL('**/app/home', { timeout: 15000 }).catch(() => {
  -     console.log('Did not redirect to /app/home automatically');
  - });
  + // Fixture navigates with proper initialization
  + await expect(page).toHaveURL(/\/app\/home/, { timeout: 15000 });
  ```

### 1.4 Remove `force: true` from Page Object

**File:** `e2e/page-objects/protocol.page.ts`

- [ ] Replace force click with proper overlay wait:
  ```diff
  - await firstCard.click({ force: true });
  + await this.dismissOverlays();
  + await firstCard.click();
  ```

---

## Phase 2: Page Object Refactor

### 2.1 Use Existing POMs Consistently

- [ ] Ensure `ProtocolPage.goto()` is used instead of custom navigation:
  ```typescript
  // In test:
  await protocolPage.goto(); // Uses POM's navigation with proper waits
  ```

### 2.2 Add Deterministic Protocol Selection

- [ ] Add method to assert specific protocol availability before selection:
  ```typescript
  async assertProtocolAvailable(name: string): Promise<void> {
      const card = this.protocolCards.filter({ hasText: name }).first();
      await expect(card, `Protocol "${name}" should exist`).toBeVisible();
  }
  ```

- [ ] Modify test to fail explicitly if expected protocol is missing:
  ```typescript
  await protocolPage.assertProtocolAvailable('Simple Transfer');
  await protocolPage.selectProtocol('Simple Transfer');
  ```

### 2.3 Add Wizard Step Verification

**File:** `e2e/page-objects/wizard.page.ts`

- [ ] Add explicit step verification before step actions:
  ```typescript
  async assertOnStep(stepName: 'protocol' | 'params' | 'machine' | 'assets' | 'deck' | 'review'): Promise<void> {
      const stepMap = {
          protocol: '[data-tour-id="run-step-protocol"]',
          params: '[data-tour-id="run-step-params"]',
          machine: '[data-tour-id="run-step-machine"]',
          assets: '[data-tour-id="run-step-assets"]',
          deck: '[data-tour-id="run-step-deck"]',
          review: '[data-tour-id="run-step-ready"]'
      };
      const stepLocator = this.page.locator(stepMap[stepName]);
      await expect(stepLocator).toHaveClass(/selected|active/, { timeout: 5000 });
  }
  ```

---

## Phase 3: Domain Verification

### 3.1 Post-Execution Persistence Verification

- [ ] Verify run record exists in SQLite after completion:
  ```typescript
  await test.step('Verify run persisted to database', async () => {
      const runRecord = await page.evaluate(async () => {
          const db = await (window as any).sqliteService.getDatabase();
          const result = db.exec("SELECT id, status FROM run_history ORDER BY created_at DESC LIMIT 1");
          return result[0]?.values[0];
      });
      expect(runRecord).toBeTruthy();
      expect(runRecord[1]).toMatch(/COMPLETED|SUCCEEDED/i);
  });
  ```

### 3.2 Parameter Serialization Verification

- [ ] Verify parameters were serialized to execution:
  ```typescript
  await test.step('Verify parameter serialization', async () => {
      const runParams = await page.evaluate(async () => {
          const db = await (window as any).sqliteService.getDatabase();
          const result = db.exec("SELECT parameters FROM run_history ORDER BY created_at DESC LIMIT 1");
          return result[0]?.values[0]?.[0];
      });
      expect(runParams).toBeTruthy();
      const parsed = JSON.parse(runParams);
      // Verify expected structure exists
      expect(parsed).toHaveProperty('protocol');
  });
  ```

### 3.3 Ensure Simulation Mode

- [ ] Add explicit simulation mode verification:
  ```typescript
  test.beforeEach(async ({ page }) => {
      // ... existing setup
      await protocolPage.ensureSimulationMode();
  });
  ```

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Add Negative Test Cases

- [ ] Test for "No Compatible Machines" state:
  ```typescript
  test('should handle no compatible machines gracefully', async ({ page }) => {
      // Select a protocol that requires hardware not available in simulation
      await protocolPage.selectProtocol('Hardware-Only Protocol');
      
      const noMachinesState = page.locator('.no-machines-state, .empty-state');
      await expect(noMachinesState).toBeVisible();
      
      // Verify Continue is disabled
      const continueBtn = page.getByRole('button', { name: /Continue/i });
      await expect(continueBtn).toBeDisabled();
  });
  ```

### 4.2 Test Execution Cancellation

- [ ] Add test for mid-execution abort:
  ```typescript
  test('should handle execution cancellation', async ({ page }) => {
      // Start execution
      await protocolPage.startExecution();
      
      // Wait for running state
      await expect(page.locator('[data-testid="run-status"]')).toContainText(/RUNNING/i);
      
      // Click abort button
      await page.getByRole('button', { name: /Abort|Cancel|Stop/i }).click();
      
      // Confirm in dialog
      await page.getByRole('button', { name: /Confirm/i }).click();
      
      // Verify aborted state
      await expect(page.locator('[data-testid="run-status"]')).toContainText(/ABORTED|CANCELLED/i);
  });
  ```

---

## Verification Plan

### Automated

```bash
# Single worker execution (current state)
npx playwright test e2e/specs/protocol-execution.spec.ts --workers=1

# Parallel execution (after Phase 1 completion)
npx playwright test e2e/specs/protocol-execution.spec.ts --workers=4

# Full suite regression
npx playwright test --grep "Protocol Wizard"
```

### Manual Verification Checklist

- [ ] Test passes with `--workers=4` without OPFS contention errors
- [ ] Screenshots appear as test artifacts in Playwright report
- [ ] No `console.log('Did not redirect...')` warnings in output
- [ ] Execution monitor correctly reflects run status

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/protocol-execution.spec.ts` | Major Refactor | 101 → ~85 |
| `e2e/page-objects/protocol.page.ts` | Minor Mod | ~5 lines |
| `e2e/page-objects/wizard.page.ts` | Enhancement | +20 lines |

---

## Acceptance Criteria

- [ ] Tests pass with parallel execution (`--workers=4`)
- [ ] Zero `force: true` clicks in test or POM
- [ ] Zero `waitForTimeout` calls (except fixture stabilization)
- [ ] Uses `app.fixture.ts` for initialization
- [ ] Verifies run record persistence in SQLite
- [ ] Verifies parameter serialization
- [ ] Baseline score improves from 4.8/10 to ≥8.0/10

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Fixture changes break other tests | Run full suite after changes |
| SQLite queries fail on schema changes | Use robust column selection |
| Simulation timing varies | Use generous timeouts with status-based waits |
| Protocol "Simple Transfer" not in seed data | Add to `seed-data.ts` or use fixture seeding |

---

## Dependencies

- `app.fixture.ts` must properly export `buildIsolatedUrl`
- `WizardPage` must be importable from `ProtocolPage`
- `run_history` table must exist with expected schema
