# E2E Enhancement Plan: functional-asset-selection.spec.ts

**Target:** [functional-asset-selection.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/functional-asset-selection.spec.ts)  
**Baseline Score:** 5.4/10  
**Target Score:** 8.0/10  
**Effort Estimate:** 2-3 hours

---

## Goals

1. **Reliability** — Eliminate flaky patterns and hardcoded waits
2. **Isolation** — Enable parallel test execution with worker-indexed DBs
3. **Domain Coverage** — Verify actual SQLite state changes, not just UI
4. **Maintainability** — Proper cleanup and consistent fixture usage

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Create or import `worker-db.fixture` to provide isolated database per worker
- [ ] Pass `testInfo` to all Page Object constructors:
  ```typescript
  // Before
  const welcomePage = new WelcomePage(page);
  
  // After
  import { test } from '../fixtures/worker-db.fixture';
  
  test.beforeEach(async ({ page }, testInfo) => {
      const welcomePage = new WelcomePage(page, testInfo);
      // ...
  });
  ```
- [ ] Update `WelcomePage`, `AssetsPage`, `ProtocolPage` constructors to accept optional `testInfo`

### 1.2 Eliminate Hardcoded Waits in POMs
- [ ] `assets.page.ts:50` - Replace `waitForTimeout(100)` with step transition assertion
- [ ] `assets.page.ts:60` - Replace `waitForTimeout(150)` with heading visibility check
- [ ] `assets.page.ts:76` - Replace `waitForTimeout(50)` with overlay state check
- [ ] `assets.page.ts:319` - Replace `waitForTimeout(500)` with `waitForResponse` for search

### 1.3 Replace Force Clicks
- [ ] `assets.page.ts:47` - Investigate why `wizard-next-button` requires force click
- [ ] Add explicit `waitForOverlaysToDismiss()` before button clicks
- [ ] Consider using `{ trial: true }` to validate clickability before forcing

---

## Phase 2: Test Cleanup & Isolation

### 2.1 Add Asset Cleanup
```typescript
test.afterEach(async ({ page }) => {
    // Dismiss dialogs
    await page.keyboard.press('Escape').catch(() => {});
    
    // Cleanup created assets (if test succeeded)
    const assetsPage = new AssetsPage(page, testInfo);
    await assetsPage.goto();
    
    // Delete resources created in this test
    await assetsPage.navigateToResources();
    await assetsPage.deleteResource(sourcePlateName).catch(() => {});
    await assetsPage.deleteResource(destPlateName).catch(() => {});
    await assetsPage.deleteResource(tipRackName).catch(() => {});
    
    // Delete machine
    await assetsPage.navigateToMachines();
    await assetsPage.deleteMachine('MyHamilton').catch(() => {});
});
```

### 2.2 Use Scoped Test Variables
- [ ] Move asset names to `test.describe` scope or use fixtures
- [ ] Use `test.info().testId` to generate unique asset names

---

## Phase 3: Domain Verification

### 3.1 Deep SQLite Verification After Asset Creation
```typescript
// After creating assets, verify DB state
const dbAssets = await page.evaluate(async () => {
    const db = (window as any).sqliteService;
    const resources = await db.query('SELECT name, category FROM resources');
    const machines = await db.query('SELECT name, driver_type FROM machines');
    return { resources, machines };
});

expect(dbAssets.resources).toContainEqual(
    expect.objectContaining({ name: sourcePlateName, category: 'Plate' })
);
expect(dbAssets.machines).toContainEqual(
    expect.objectContaining({ name: 'MyHamilton', driver_type: 'Hamilton' })
);
```

### 3.2 Asset Selection Verification
- [ ] After `autoConfigureAssetsManual()`, verify Angular component state:
  ```typescript
  const assetState = await page.evaluate(() => {
      const cmp = (window as any).ng?.getComponent?.(
          document.querySelector('app-asset-selection-step')
      );
      return cmp?.selectedAssets;
  });
  expect(assetState).toHaveProperty('source_plate');
  expect(assetState).toHaveProperty('dest_plate');
  expect(assetState).toHaveProperty('tip_rack');
  ```

### 3.3 Review Step State Verification
- [ ] Verify serialized protocol configuration in review step:
  ```typescript
  const reviewState = await page.evaluate(() => {
      const cmp = (window as any).ng?.getComponent?.(
          document.querySelector('app-protocol-summary')
      );
      return cmp?.protocolConfig;
  });
  expect(reviewState.protocolName).toBe('Simple Transfer');
  expect(reviewState.assets).toHaveLength(3);
  ```

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Negative Test Cases
- [ ] Add test: `should show error when creating asset with duplicate name`
- [ ] Add test: `should disable Continue when required assets are missing`
- [ ] Add test: `should handle machine selection when no compatible machines exist`

### 4.2 Boundary Conditions
- [ ] Test asset name with special characters
- [ ] Test protocol selection with no machines created

---

## Verification Plan

### Automated
```bash
# Single run verification
npx playwright test e2e/specs/functional-asset-selection.spec.ts --headed

# Parallel execution verification (must pass with workers)
npx playwright test e2e/specs/functional-asset-selection.spec.ts --workers=4 --repeat-each=3

# Debug mode for investigating flakes
npx playwright test e2e/specs/functional-asset-selection.spec.ts --debug
```

### Manual Verification Checklist
- [ ] Test passes in headless mode
- [ ] Test passes with `--workers=4`
- [ ] Test passes with `--repeat-each=5` (no flakes in 5 consecutive runs)
- [ ] No assets remain in DB after test run (check via browser console)
- [ ] Test duration < 60s (down from 5 min theoretical max)

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/functional-asset-selection.spec.ts` | Refactor | 103 → ~150 |
| `e2e/page-objects/base.page.ts` | Minor | Add testInfo propagation |
| `e2e/page-objects/assets.page.ts` | Refactor | Remove waitForTimeout calls |
| `e2e/page-objects/welcome.page.ts` | Minor | Accept optional testInfo |
| `e2e/fixtures/worker-db.fixture.ts` | Create/Import | New fixture if not exists |

---

## Acceptance Criteria

- [ ] Tests pass with parallel execution (`--workers=4`)
- [ ] Zero `force: true` clicks in the test file itself
- [ ] Zero `waitForTimeout` calls in the test file itself
- [ ] Uses `worker-db.fixture` for database isolation
- [ ] Includes `afterEach` cleanup that removes created assets
- [ ] Verifies SQLite state after asset creation (not just UI)
- [ ] Verifies Angular component state at review step
- [ ] Baseline score improves from 5.4/10 to ≥8.0/10

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Cleanup may fail if test errors early | Use try/finally in afterEach, log failures |
| DB queries may change structure | Use column-agnostic assertions |
| Angular component API may change | Wrap `ng.getComponent` in helper function |
| Force clicks might be needed for overlay issues | File separate issue to fix overlay z-index |

---

## Dependencies

- [ ] Verify `worker-db.fixture` exists or create it
- [ ] Confirm `sqliteService` is exposed on window in browser mode
- [ ] Verify `ng.getComponent` works in production builds (may need `preserveWhitespaces`)
