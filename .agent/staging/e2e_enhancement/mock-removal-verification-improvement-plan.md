# E2E Enhancement Plan: mock-removal-verification.spec.ts

**Target:** [mock-removal-verification.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/mock-removal-verification.spec.ts)  
**Baseline Score:** 4.8/10  
**Target Score:** 8.0/10  
**Effort Estimate:** 3–4 hours

---

## Goals

1. **Reliability** — Enable parallel execution with worker-indexed database isolation
2. **Isolation** — Use established fixtures for consistent initialization
3. **Domain Coverage** — Verify SQLite state directly, not just UI visibility
4. **Maintainability** — Consolidate inline locators into Page Object Model

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Replace `@playwright/test` import with `import { test, expect } from '../fixtures/worker-db.fixture'`
- [ ] Remove manual `?resetdb=1` from `page.goto()` — fixture handles this
- [ ] Use `gotoWithWorkerDb(page, '/', testInfo)` for proper isolation

**Before:**
```typescript
import { expect, test } from '@playwright/test';
// ...
await page.goto('/?resetdb=1');
```

**After:**
```typescript
import { test, expect, gotoWithWorkerDb } from '../fixtures/worker-db.fixture';
// ...
await gotoWithWorkerDb(page, '/', testInfo);
```

### 1.2 Standardize Page Object Initialization
- [ ] Pass `testInfo` to WelcomePage/ProtocolPage constructors for worker-aware navigation
- [ ] Use `BasePage.goto()` instead of raw `page.goto()` for consistent `mode=browser` and `dbName` handling

---

## Phase 2: Page Object Refactor

### 2.1 Move Inline Locators to POMs
- [ ] Add `ProtocolPage.getProtocolCards()` method (already exists but not used correctly)
- [ ] Add `ExecutionMonitorPage.getEmptyStateIndicator()` method
- [ ] Add `HomePage` POM with `getRecentActivityMessage()` locator

**New HomePage POM (create if not exists):**
```typescript
export class HomePage extends BasePage {
    constructor(page: Page, testInfo?: TestInfo) {
        super(page, '/app/home', testInfo);
    }
    
    readonly recentActivityPlaceholder = this.page.getByText('No recent activity');
    
    async assertNoRecentActivity() {
        await expect(this.recentActivityPlaceholder).toBeVisible();
    }
}
```

### 2.2 Consolidate Mock Data Constants
- [ ] Create `e2e/fixtures/mock-data.constants.ts`:
```typescript
export const LEGACY_MOCK_PROTOCOLS = [
    'Daily System Maintenance',
    'Cell Culture Feed',
    'Evening Shutdown'
];

export const LEGACY_MOCK_RUN_IDS = ['MOCK-RUN-001'];

export const LEGACY_MOCK_RUN_NAMES = [
    'PCR Prep Run #12',
    'Cell Culture Feed Batch A',
    'System Calibration'
];
```

---

## Phase 3: Domain Verification

### 3.1 Add SQLite Query Verification
- [ ] After UI assertions, query the database directly to confirm no mock rows exist:

```typescript
// Add to test: verify mock protocols are absent
const mockProtocolsInDb = await page.evaluate(async () => {
    const db = (window as any).sqliteService?.db;
    if (!db) return null;
    const result = db.exec("SELECT COUNT(*) as cnt FROM protocols WHERE name IN ('Daily System Maintenance', 'Cell Culture Feed', 'Evening Shutdown')");
    return result[0]?.values[0][0] ?? null;
});
expect(mockProtocolsInDb).toBe(0);
```

### 3.2 Verify Real Protocol Exists by Name
- [ ] Instead of just checking `.protocol-card` exists, verify a known real protocol:
```typescript
const realProtocol = page.getByRole('heading', { name: /PCR Prep|Sample Processing/i });
await expect(realProtocol.first()).toBeVisible();
```

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Negative Test Cases
- [ ] Add test: `database reset failure shows error state`
- [ ] Add test: `corrupted seed data displays recovery UI`

---

## Verification Plan

### Automated
```bash
# Run with parallelism to confirm isolation works
npx playwright test e2e/specs/mock-removal-verification.spec.ts --workers=4 --reporter=list

# Run full regression to ensure no cross-test contamination
npx playwright test --workers=4
```

### Manual Validation
1. Inspect OPFS via DevTools → Application → Storage → OPFS
2. Confirm separate `praxis-worker-{0,1,2,3}.db` files exist

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/mock-removal-verification.spec.ts` | Refactor | ~60 (most lines) |
| `e2e/page-objects/home.page.ts` | Create | ~25 (new file) |
| `e2e/fixtures/mock-data.constants.ts` | Create | ~15 (new file) |
| `e2e/page-objects/monitor.page.ts` | Enhance | ~5 (add method) |

---

## Implementation Checklist

### Critical (Must Do)
- [ ] Migrate to `worker-db.fixture` for parallel safety
- [ ] Use `gotoWithWorkerDb()` helper instead of raw `page.goto()`
- [ ] Verify SQLite state directly (not just UI visibility)

### Recommended (Should Do)
- [ ] Create `HomePage` POM
- [ ] Extract mock data literals to constants file
- [ ] Add positive real-protocol verification by name

### Nice-to-Have (Could Do)
- [ ] Add negative test for database reset failure
- [ ] Add screenshot on test failure for debugging

---

## Acceptance Criteria

- [ ] Tests pass with `--workers=4` (parallel execution)
- [ ] Zero raw `page.goto()` calls with manual query params
- [ ] Uses `worker-db.fixture` for all navigation
- [ ] SQLite queries verify absence of mock data (not just UI)
- [ ] All inline locators migrated to POMs
- [ ] Baseline score improves to ≥8.0/10
