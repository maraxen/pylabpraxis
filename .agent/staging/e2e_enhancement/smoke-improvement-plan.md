# E2E Enhancement Plan: smoke.spec.ts

**Target:** [smoke.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/smoke.spec.ts)  
**Baseline Score:** 5.4/10  
**Target Score:** 8.0/10  
**Effort Estimate:** 2-3 hours

---

## Goals

1. **Reliability** — Replace brittle locators and anti-patterns
2. **Accessibility** — Use user-facing locators exclusively
3. **Domain Coverage** — Verify actual data presence, not just UI shells
4. **Maintainability** — Migrate common locators to Page Objects

---

## Phase 1: Locator Modernization (Priority: Critical)

### 1.1 Replace Material Internal Selectors

**Current (Brittle):**
```typescript
await expect(page.locator('.mat-mdc-tab-labels')).toContainText('Machines');
await expect(page.locator('.mat-step-header').filter({ hasText: 'Select Protocol' })).toBeVisible();
```

**Target (User-Facing):**
```typescript
await expect(page.getByRole('tab', { name: /Machines/i })).toBeVisible();
await expect(page.getByRole('listitem', { name: /Select Protocol/i })).toBeVisible();
// OR use accessible step label if stepper has proper ARIA
await expect(page.locator('mat-step-header').filter({ has: page.getByText('Select Protocol') })).toBeVisible();
```

**Files Changed:**
- [ ] Lines 25-27: Tab label assertions
- [ ] Lines 52-53: Stepper header assertions

### 1.2 Remove `waitForLoadState('networkidle')`

**Current (Anti-Pattern):**
```typescript
await page.waitForLoadState('networkidle');
```

**Target (State-Based):**
```typescript
// Wait for specific component readiness instead
await expect(page.locator('app-unified-shell')).toBeVisible();
// Or for data-dependent views:
await expect(page.locator('app-machine-list table tbody tr').first()).toBeVisible();
```

**Files Changed:**
- [ ] Line 12: Dashboard test
- [ ] Line 20: Assets test

### 1.3 Reduce Timeout Overrides

**Current:**
```typescript
await expect(page.locator('app-unified-shell')).toBeVisible({ timeout: 30000 });
```

**Target:**
```typescript
// Rely on global timeout in playwright.config.ts (default 30s)
// If component-specific delays needed, document why
await expect(page.locator('app-unified-shell')).toBeVisible();
```

**Note:** Only keep explicit timeouts where there's a documented reason (e.g., Pyodide cold-start).

---

## Phase 2: Page Object Migration

### 2.1 Create SmokePage POM

Create `e2e/pages/smoke.page.ts`:

```typescript
import { BasePage } from './base.page';
import { expect } from '@playwright/test';

export class SmokePage extends BasePage {
  // Dashboard
  get appShell() {
    return this.page.locator('app-unified-shell, app-main-layout');
  }
  
  get navRail() {
    return this.page.locator('.sidebar-rail, .nav-rail').first();
  }

  // Assets
  get assetsComponent() {
    return this.page.locator('app-assets');
  }
  
  get machinesTab() {
    return this.page.getByRole('tab', { name: /Machines/i });
  }
  
  get resourcesTab() {
    return this.page.getByRole('tab', { name: /Resources/i });
  }
  
  get registryTab() {
    return this.page.getByRole('tab', { name: /Registry/i });
  }
  
  get machineTable() {
    return this.page.locator('app-machine-list table');
  }

  // Protocols
  get protocolLibrary() {
    return this.page.locator('app-protocol-library');
  }
  
  get protocolTable() {
    return this.page.locator('app-protocol-library table');
  }

  // Run Wizard
  get runProtocolComponent() {
    return this.page.locator('app-run-protocol');
  }
  
  get stepper() {
    return this.page.locator('mat-stepper');
  }
  
  stepHeader(name: string) {
    return this.page.locator('mat-step-header').filter({ hasText: name });
  }

  // Verification helpers
  async verifyDashboardLoaded() {
    await expect(this.appShell).toBeVisible();
    await expect(this.navRail).toBeVisible();
  }
  
  async verifyMachineTableHasData() {
    await expect(this.machineTable.locator('tbody tr').first()).toBeVisible();
  }
}
```

### 2.2 Refactor Spec to Use POM

```typescript
import { test, expect } from '../fixtures/app.fixture';
import { SmokePage } from '../pages/smoke.page';

test.describe('Smoke Test', () => {
  test('should load the dashboard', async ({ page }) => {
    const smoke = new SmokePage(page);
    await expect(page).toHaveTitle(/Praxis/);
    await smoke.verifyDashboardLoaded();
    await page.screenshot({ path: '/tmp/e2e-smoke/landing_dashboard.png' });
  });
  
  // ... refactor other tests similarly
});
```

---

## Phase 3: Domain Verification

### 3.1 Add Data Presence Assertions

**Dashboard Test:**
```typescript
// Verify navigation items exist (not just sidebar visibility)
await expect(page.getByRole('link', { name: /Assets/i })).toBeVisible();
await expect(page.getByRole('link', { name: /Protocols/i })).toBeVisible();
```

**Assets Test:**
```typescript
// Verify table has rows (not just table visibility)
await smoke.machinesTab.click();
await expect(smoke.machineTable.locator('tbody tr').first()).toBeVisible();
// Optionally verify row count
const rowCount = await smoke.machineTable.locator('tbody tr').count();
expect(rowCount).toBeGreaterThan(0);
```

**Protocols Test:**
```typescript
// Verify at least one protocol exists
await expect(smoke.protocolTable.locator('tbody tr').first()).toBeVisible();
```

### 3.2 Add Empty State Test (Stretch)

```typescript
test('should show empty state when no machines exist', async ({ page }) => {
  // Navigate with a fresh DB that has no seed data
  await page.goto('/assets?mode=browser&dbName=empty-test&resetdb=1&noSeed=1');
  await expect(page.getByText(/No machines found/i)).toBeVisible();
});
```

---

## Phase 4: Error Scenario Coverage (Stretch)

### 4.1 Invalid Route Test

```typescript
test('should handle invalid routes gracefully', async ({ page }) => {
  await page.goto('/nonexistent-route');
  // Verify redirect to dashboard OR 404 component
  await expect(page.locator('app-not-found, app-unified-shell')).toBeVisible();
});
```

### 4.2 DB Initialization Failure (If Testable)

```typescript
test('should show error when SQLite fails', async ({ page }) => {
  // This would require a way to inject failure - may need app support
  // Placeholder for future implementation
  test.skip();
});
```

---

## Verification Plan

### Automated
```bash
# Run smoke tests with parallelism to verify isolation
npx playwright test e2e/specs/smoke.spec.ts --workers=4

# Run with tracing for debugging
npx playwright test e2e/specs/smoke.spec.ts --trace on
```

### Manual Checklist
- [ ] Confirm no `waitForLoadState('networkidle')` calls remain
- [ ] Confirm no `.mat-mdc-*` selectors remain (use getByRole)
- [ ] Confirm SmokePage POM is imported and used
- [ ] Confirm data presence assertions exist for tables

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/smoke.spec.ts` | Refactor | All (56 lines) |
| `e2e/pages/smoke.page.ts` | Create | ~60 lines new |
| `e2e/pages/index.ts` | Update | Add export |

---

## Acceptance Criteria

- [ ] Tests pass with `--workers=4` (parallel execution)
- [ ] Zero `waitForLoadState('networkidle')` calls
- [ ] Zero `.mat-mdc-*` or `.mat-step-header` CSS selectors
- [ ] All locators use `getByRole`, `getByLabel`, or component tags
- [ ] SmokePage POM encapsulates all locators
- [ ] Data presence verified (row counts > 0)
- [ ] Baseline score improves from 5.4/10 to ≥8.0/10

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Material component ARIA labels may not exist | Check actual DOM; may need app changes for accessibility |
| Empty state UI may not be implemented | Defer Phase 3.2 if no `noSeed` support exists |
| Stepper accessibility may be poor | Use filter pattern with text match as fallback |

---

## Implementation Order

1. **Phase 1.2** — Remove `networkidle` (5 min)
2. **Phase 1.1** — Replace Material selectors (20 min)
3. **Phase 2.1** — Create SmokePage POM (30 min)
4. **Phase 2.2** — Refactor spec to use POM (20 min)
5. **Phase 3.1** — Add data presence assertions (20 min)
6. **Verification** — Run with workers=4 (10 min)
7. **Phase 4** — Error scenarios (optional, 30 min)

**Total Core Work:** ~1.5 hours  
**With Stretch Goals:** ~2.5 hours
