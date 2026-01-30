# E2E Enhancement Plan: workcell-dashboard.spec.ts

**Target:** [workcell-dashboard.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/workcell-dashboard.spec.ts)  
**Baseline Score:** 3.2/10  
**Target Score:** 8.0/10  
**Effort Estimate:** Medium (4-6 hours)

---

## Goals

1. **Reliability** — Fix DB isolation bypass, eliminate conditional test logic
2. **Isolation** — Enable true parallel test execution with worker-indexed DBs
3. **Domain Coverage** — Verify machine data loads correctly from SQLite, test view modes
4. **Maintainability** — Create WorkcellPage POM, use semantic locators

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Fix DB Isolation (🔴 Blocking)

**Problem:** Test navigates to `/app/workcell?mode=browser` but fixture sets up `dbName=praxis-worker-{index}`. This bypasses isolation.

**Solution:**
```typescript
// Before (L6):
await page.goto('/app/workcell?mode=browser');

// After:
import { buildIsolatedUrl } from '../fixtures/app.fixture';
// In test:
await page.goto(buildIsolatedUrl('/app/workcell', testInfo));
```

- [ ] Import `buildIsolatedUrl` helper
- [ ] Update `beforeEach` to use isolated URL pattern
- [ ] Remove redundant `waitForFunction` for SqliteService (handled by fixture)

### 1.2 Create Machine Seeding Fixture

**Problem:** Tests depend on pre-existing machine data. Non-deterministic.

**Solution:** Create a fixture that seeds a test machine before tests run.

```typescript
// fixtures/workcell.fixture.ts
import { test as base } from './app.fixture';

export const test = base.extend({
    testMachine: async ({ page }, use, testInfo) => {
        // Seed a simulated machine via evaluate() or API
        await page.evaluate(async () => {
            const sqlite = (window as any).sqliteService;
            await sqlite.run(`
                INSERT INTO machines (id, name, type, backend, is_simulated)
                VALUES ('test-machine-${Date.now()}', 'Test Liquid Handler', 'LiquidHandler', 'ChatterBox', 1)
            `);
        });
        await use({ id: 'test-machine-...', name: 'Test Liquid Handler' });
    }
});
```

- [ ] Create `workcell.fixture.ts` with machine seeding
- [ ] Inject `testMachine` into tests that need populated state
- [ ] Separate empty-state tests into distinct describe block

### 1.3 Eliminate Conditional Test Logic

**Problem:** Tests contain `if (cardCount > 0) ... else ...` which makes outcomes unpredictable.

**Solution:** Split into separate test files or describe blocks:

```typescript
test.describe('Workcell Dashboard - Populated State', () => {
    test.use({ testMachine: true }); // Use seeding fixture
    
    test('should display machine cards', async ({ page }) => {
        // Now we KNOW machines exist
    });
});

test.describe('Workcell Dashboard - Empty State', () => {
    // No machine fixture
    test('should display empty state message', async ({ page }) => {
        // Now we KNOW no machines exist
    });
});
```

- [ ] Remove `if/else` branching from test bodies
- [ ] Remove `test.skip()` calls from inside test body
- [ ] Create separate describe blocks for each state

---

## Phase 2: Page Object Refactor

### 2.1 Create WorkcellPage POM

**Problem:** All selectors are inline. No `workcell.page.ts` exists.

**Solution:**

```typescript
// page-objects/workcell.page.ts
import { Locator, Page } from '@playwright/test';
import { BasePage } from './base.page';

export class WorkcellPage extends BasePage {
    readonly heading: Locator;
    readonly explorer: Locator;
    readonly searchInput: Locator;
    readonly machineCards: Locator;
    readonly emptyStateMessage: Locator;
    readonly focusView: Locator;

    constructor(page: Page) {
        super(page);
        this.heading = page.getByRole('heading', { name: /Workcell Dashboard/i });
        this.explorer = page.locator('app-workcell-explorer');
        this.searchInput = page.getByRole('searchbox').or(page.locator('app-workcell-explorer input[type="text"]'));
        this.machineCards = page.locator('app-machine-card');
        this.emptyStateMessage = page.getByText(/No machines found/i);
        this.focusView = page.locator('app-machine-focus-view');
    }

    async goto(testInfo: { workerIndex: number }) {
        await this.page.goto(buildIsolatedUrl('/app/workcell', testInfo));
        await this.waitForDbReady();
    }

    async waitForLoad() {
        await this.heading.waitFor({ state: 'visible', timeout: 15000 });
    }

    async selectMachine(index = 0) {
        await this.machineCards.nth(index).click();
        await this.focusView.waitFor({ state: 'visible', timeout: 10000 });
    }

    async searchMachines(query: string) {
        await this.searchInput.fill(query);
        await this.page.waitForTimeout(300); // Debounce
    }
}
```

- [ ] Create `workcell.page.ts` in `page-objects/`
- [ ] Define semantic locators using `getByRole` where possible
- [ ] Add `goto()`, `waitForLoad()`, `selectMachine()`, `searchMachines()` methods
- [ ] Migrate inline selectors from spec to POM

### 2.2 Replace Component Selectors

| Current | Replacement |
|---------|-------------|
| `page.locator('h1')` | `page.getByRole('heading', { level: 1 })` |
| `page.locator('.animate-spin')` | `page.getByRole('progressbar')` or add `data-testid="loading"` |
| `page.locator('app-workcell-explorer input[type="text"]')` | `page.getByRole('searchbox')` or `getByPlaceholder('Search...')` |

- [ ] Update component selectors to semantic alternatives
- [ ] Add `data-testid` attributes in Angular components where roles unavailable
- [ ] Document any selectors that must remain as component tags

---

## Phase 3: Domain Verification

### 3.1 Verify Data Integrity

**Problem:** Tests only check visibility, not data content.

**Solution:** Assert machine data appears correctly:

```typescript
test('should display machine name and type', async ({ page, testMachine }) => {
    const card = workcellPage.machineCards.first();
    await expect(card).toContainText(testMachine.name);
    await expect(card).toContainText('Liquid Handler');
    await expect(card.locator('.simulated-badge')).toBeVisible();
});
```

- [ ] Assert machine name appears in card
- [ ] Assert machine type/category is displayed
- [ ] Assert simulated badge for simulated machines

### 3.2 Test View Mode Switching

**Problem:** Component supports `grid`, `list`, `focus` modes but none are tested.

**Solution:**

```typescript
test('should switch between view modes', async ({ page }) => {
    const gridBtn = page.getByRole('button', { name: /Grid/i });
    const listBtn = page.getByRole('button', { name: /List/i });
    
    await listBtn.click();
    await expect(page.locator('.list-view')).toBeVisible();
    
    await gridBtn.click();
    await expect(page.locator('.grid-view')).toBeVisible();
});
```

- [ ] Add test for view mode toggle buttons
- [ ] Verify layout changes when mode switches

### 3.3 Test Explorer Search/Filter

```typescript
test('should filter machines by search query', async ({ page, testMachine }) => {
    await workcellPage.searchMachines('Liquid');
    await expect(workcellPage.machineCards).toHaveCount(1);
    
    await workcellPage.searchMachines('nonexistent');
    await expect(workcellPage.emptyStateMessage).toBeVisible();
});
```

- [ ] Add search input interaction test
- [ ] Verify filtering reduces visible cards

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Database Failure Simulation

```typescript
test('should handle database initialization failure gracefully', async ({ page }) => {
    // Navigate without resetdb to trigger potential stale state
    await page.goto('/app/workcell?mode=browser&simulateDbError=1');
    await expect(page.getByText(/Unable to load/i)).toBeVisible();
});
```

- [ ] Add error boundary test
- [ ] Verify graceful degradation message

---

## Verification Plan

### Automated
```bash
# Run with parallel workers to verify isolation
npx playwright test e2e/specs/workcell-dashboard.spec.ts --workers=4

# Run full suite to check for regressions
npx playwright test --workers=4
```

### Manual Checklist
- [ ] All tests pass with `--workers=4`
- [ ] No test depends on another test's side effects
- [ ] Screenshots are deterministic (same machine appears in each)

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/workcell-dashboard.spec.ts` | Refactor | ~100 |
| `e2e/page-objects/workcell.page.ts` | Create | ~60 |
| `e2e/fixtures/workcell.fixture.ts` | Create | ~30 |
| `src/app/...workcell-dashboard.component.ts` | Add data-testids | ~5 |

---

## Acceptance Criteria

- [ ] Tests pass with `--workers=4` (parallel execution)
- [ ] Zero conditional `if/else` logic in test bodies
- [ ] Zero `test.skip()` calls inside test body
- [ ] Uses `WorkcellPage` POM for all interactions
- [ ] Uses `buildIsolatedUrl()` for navigation
- [ ] Seeded test data for populated-state tests
- [ ] At least one data integrity assertion (machine name displayed)
- [ ] Baseline score improves from 3.2/10 to ≥8.0/10

---

## Dependencies

- `app.fixture.ts` must export `buildIsolatedUrl` (✅ already exists)
- Component may need `data-testid` additions for loading spinner
- Machine seeding requires understanding of SQLite schema

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Machine seeding fails silently | Tests flaky | Add seed verification assertion |
| View mode buttons don't exist | Tests fail | Check component template first |
| Search debounce causes race | Flaky filter test | Use `page.waitForFunction` to wait for filter |
