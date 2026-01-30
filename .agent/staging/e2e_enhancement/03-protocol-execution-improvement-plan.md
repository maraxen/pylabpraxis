# E2E Enhancement Plan: 03-protocol-execution.spec.ts

**Target:** [03-protocol-execution.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/03-protocol-execution.spec.ts)  
**Baseline Score:** 5.6/10  
**Target Score:** 8.0/10  
**Effort Estimate:** 3-4 hours

---

## Goals

1. **Reliability** — Eliminate serial execution pattern and flaky patterns
2. **Isolation** — Enable parallel test execution with worker-indexed databases
3. **Domain Coverage** — Verify SQLite persistence and Pyodide serialization
4. **Maintainability** — Modernize locators and leverage POM patterns consistently

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Replace `import { expect, test, Page } from '@playwright/test'` with `import { test, expect } from '../fixtures/worker-db.fixture'`
- [ ] Pass `testInfo` to all Page Object constructors
- [ ] Use `BasePage.goto()` consistently (or `gotoWithWorkerDb` helper)

```typescript
// BEFORE
test('select protocol from library', async ({ page }) => {
    const protocolPage = new ProtocolPage(page);
    await protocolPage.goto();
    
// AFTER  
test('select protocol from library', async ({ page }, testInfo) => {
    const protocolPage = new ProtocolPage(page, testInfo);
    await protocolPage.goto();
```

### 1.2 Remove Serial Execution Pattern
- [ ] Change `test.describe.serial` to `test.describe`
- [ ] Make each test fully independent by duplicating setup steps
- [ ] Refactor `launchExecution()` helper to encapsulate full workflow

**Rationale:** Serial tests block CI parallelism. Each test taking 30s = 2 minutes total (serial) vs 30s (parallel with 4 workers).

### 1.3 Eliminate Force Clicks
- [ ] Fix `protocol.page.ts:60` - `await firstCard.click({ force: true })`
- [ ] Root cause: CDK overlay or animation blocking clickability
- [ ] Solution: Add `waitForOverlaysToDismiss()` before click

```typescript
// BEFORE
await firstCard.click({ force: true });

// AFTER
await this.page.locator('.cdk-overlay-backdrop').waitFor({ state: 'hidden', timeout: 2000 }).catch(() => {});
await firstCard.click();
```

### 1.4 Replace Silent Error Suppression
- [ ] Remove `.catch(() => {})` patterns that swallow errors
- [ ] Use conditional checks with explicit logging instead

```typescript
// BEFORE
await page.waitForURL('**/app/home', { timeout: 15000 }).catch(() => {
    console.log('Did not redirect to /app/home automatically');
});

// AFTER
const currentUrl = page.url();
if (!currentUrl.includes('/app/home')) {
    console.log('[Setup] Not on /app/home, navigating explicitly...');
    await page.goto('/app/home');
}
```

---

## Phase 2: Locator Modernization

### 2.1 Replace CSS Class Selectors

| Current | Replacement |
|---------|-------------|
| `.sidebar-rail` | `getByRole('navigation')` or `getByTestId('sidebar-rail')` |
| `.praxis-card` | `getByTestId('protocol-card')` |
| `h3.card-title` | `getByRole('heading', { level: 3 })` or `getByTestId('card-title')` |
| `mat-card` filters | `getByTestId('run-info-card')` |

### 2.2 Update Page Objects

**ProtocolPage updates:**
```typescript
// BEFORE
this.protocolCards = page.locator('app-protocol-card');

// AFTER
this.protocolCards = page.getByTestId('protocol-card-list').locator('[data-testid="protocol-card"]');
```

**MonitorPage updates:**
```typescript
// BEFORE
this.runInfoCard = page.locator('mat-card').filter({ hasText: 'Run Information' }).first();

// AFTER
this.runInfoCard = page.getByTestId('run-info-card');
```

### 2.3 Add Missing Test IDs to Angular Components
- [ ] `protocol-card.component.html` - add `data-testid="protocol-card"`
- [ ] `shell.component.html` - add `data-testid="sidebar-rail"` to navigation
- [ ] `run-detail.component.html` - add `data-testid="run-info-card"`

---

## Phase 3: Domain Verification

### 3.1 SQLite State Verification
- [ ] Add helper to verify run persistence directly in database

```typescript
// Add to ExecutionMonitorPage
async verifyRunInDatabase(runId: string): Promise<boolean> {
    return await this.page.evaluate(async (id) => {
        const service = (window as any).sqliteService;
        const result = await service.db.exec(`SELECT * FROM runs WHERE id = '${id}'`);
        return result[0]?.values?.length > 0;
    }, runId);
}
```

### 3.2 Pyodide Serialization Verification
- [ ] Add parameter capture at execution time

```typescript
// Add to test: 'parameter values reach execution'
// After starting execution, before navigation to history:
const executedParams = await page.evaluate(() => {
    const lastExecution = (window as any).jupyterLiteService?.lastExecutionArgs;
    return lastExecution?.params;
});
expect(executedParams?.volume_ul).toBe(123.45);
```

### 3.3 Log Content Structure Verification
- [ ] Verify log entries have expected structure, not just text containment

```typescript
// BEFORE
await monitor.waitForLogEntry('Execution completed successfully');

// AFTER
const logEntry = await monitor.getLogEntry('Execution completed successfully');
expect(logEntry.level).toBe('INFO');
expect(logEntry.timestamp).toBeDefined();
```

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Invalid Parameter Test
```typescript
test('rejects invalid parameter values', async ({ page }, testInfo) => {
    // Setup...
    await protocolPage.configureParameter('volume_ul', '-50'); // Negative
    await wizardPage.completeParameterStep();
    
    // Expect validation error
    await expect(page.getByText(/Volume must be positive/i)).toBeVisible();
    await expect(continueButton).toBeDisabled();
});
```

### 4.2 Python Execution Error Test
```typescript
test('handles Python syntax error gracefully', async ({ page }, testInfo) => {
    // Select a protocol with known syntax error (or inject via mock)
    // Verify error state appears in monitor
    await expect(monitor.statusChip).toContainText('FAILED');
    await expect(monitor.logPanel).toContainText(/SyntaxError/);
});
```

### 4.3 Cancellation Test
```typescript
test('can cancel running execution', async ({ page }, testInfo) => {
    // Launch long-running protocol
    await monitor.waitForStatus(/RUNNING/);
    
    // Cancel
    await page.getByRole('button', { name: /Cancel/i }).click();
    await expect(page.getByRole('dialog')).toContainText('Are you sure');
    await page.getByRole('button', { name: /Confirm/i }).click();
    
    // Verify cancelled state
    await expect(monitor.statusChip).toContainText('CANCELLED');
});
```

---

## Phase 5: Screenshot Management

### 5.1 Use testInfo.outputPath()
```typescript
// BEFORE
await page.screenshot({ path: '/tmp/e2e-protocol/03-spec-01-selection.png' });

// AFTER
await page.screenshot({ path: testInfo.outputPath('protocol-selection.png') });
```

---

## Verification Plan

### Automated
```bash
# Single file (should complete in <2 minutes)
npx playwright test e2e/specs/03-protocol-execution.spec.ts

# Parallel execution proof (requires worker-db fixture)
npx playwright test e2e/specs/03-protocol-execution.spec.ts --workers=4

# Full regression
npx playwright test --grep "Protocol Execution"
```

### Manual Verification
- [ ] Observe no `force: true` warnings in trace viewer
- [ ] Confirm database isolation via worker-indexed DB names in logs
- [ ] Verify screenshots appear in `test-results/` not `/tmp/`

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/03-protocol-execution.spec.ts` | Refactor | ~85 (fixture import, testInfo passing, serial removal) |
| `e2e/page-objects/protocol.page.ts` | Refactor | ~20 (force click removal, testInfo support) |
| `e2e/page-objects/monitor.page.ts` | Enhance | ~30 (DB verification, structured log parsing) |
| `e2e/page-objects/wizard.page.ts` | Minor | ~10 (consistent locator patterns) |
| `src/app/core/components/protocol-card/` | Add test IDs | ~5 |
| `src/app/shell/` | Add test IDs | ~3 |

---

## Acceptance Criteria

- [ ] Tests pass with parallel execution (`--workers=4`)
- [ ] Zero `force: true` clicks in any POM
- [ ] Zero `waitForTimeout` calls
- [ ] All locators use `getByRole`, `getByTestId`, or `getByLabel`
- [ ] `test.describe.serial` removed
- [ ] SQLite persistence verified for at least one test
- [ ] Screenshots saved via `testInfo.outputPath()`
- [ ] Baseline score improves from 5.6/10 to ≥8.0/10

---

## Score Improvement Projection

| Category | Before | After | Gain |
|----------|--------|-------|------|
| **Test Scope** | 7/10 | 8/10 | +1 (error scenarios) |
| **Best Practices** | 4/10 | 8/10 | +4 (fixture, locators, isolation) |
| **Test Value** | 9/10 | 9/10 | 0 (already high) |
| **Isolation** | 3/10 | 8/10 | +5 (worker-db, independent tests) |
| **Domain Coverage** | 5/10 | 7/10 | +2 (DB/Pyodide verification) |
| **Overall** | **5.6/10** | **8.0/10** | **+2.4** |
