# E2E Enhancement Plan: health-check.spec.ts

**Target:** [health-check.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/health-check.spec.ts)  
**Baseline Score:** 8.0/10  
**Target Score:** 9.0/10  
**Effort Estimate:** 30 minutes

---

## Goals

1. **Completeness** — Extend health check to cover more infrastructure layers
2. **Diagnostics** — Improve error messaging for faster debugging
3. **Maintainability** — Keep test lean and focused

---

## Phase 1: Enhanced Infrastructure Verification

### 1.1 Add Seed Data Verification

- [ ] Verify protocol definitions exist in database:
  ```typescript
  console.log('[HealthCheck] Verifying seed data...');
  const seedDataCheck = await page.evaluate(async () => {
      const db = await (window as any).sqliteService.getDatabase();
      const protocols = db.exec("SELECT COUNT(*) FROM protocol_definitions")[0]?.values[0]?.[0] || 0;
      const machines = db.exec("SELECT COUNT(*) FROM machine_definitions")[0]?.values[0]?.[0] || 0;
      return { protocols, machines };
  });
  
  expect(seedDataCheck.protocols, 'Protocol definitions should be seeded').toBeGreaterThan(0);
  expect(seedDataCheck.machines, 'Machine definitions should be seeded').toBeGreaterThan(0);
  ```

### 1.2 Add Browser Mode Verification

- [ ] Confirm app is running in browser (non-machine) mode:
  ```typescript
  console.log('[HealthCheck] Verifying browser mode...');
  const isBrowserMode = await page.evaluate(() => {
      const modeService = (window as any).modeService;
      return modeService?.isBrowserMode?.() ?? false;
  });
  expect(isBrowserMode, 'App should be in browser mode').toBe(true);
  ```

### 1.3 Add Worker-Indexed DB Verification

- [ ] Confirm database name matches worker index:
  ```typescript
  console.log('[HealthCheck] Verifying database isolation...');
  const dbName = await page.evaluate(() => {
      return (window as any).sqliteService?.getDatabaseName?.() || 'unknown';
  });
  expect(dbName).toMatch(/praxis-worker-\d+/);
  ```

---

## Phase 2: Diagnostic Improvements

### 2.1 Add Structured Test Steps

- [ ] Wrap assertions in `test.step` for better reporting:
  ```typescript
  test('should load application and initialize database', async ({ page }) => {
      await test.step('Verify UI shell rendered', async () => {
          await expect(page.locator('.sidebar-rail')).toBeVisible();
      });
      
      await test.step('Verify SQLite service ready', async () => {
          const isReady = await page.evaluate(() => { /* ... */ });
          expect(isReady).toBe(true);
      });
      
      await test.step('Verify seed data loaded', async () => {
          // ...
      });
  });
  ```

### 2.2 Improve Error Context

- [ ] Add diagnostic data collection on failure:
  ```typescript
  test.afterEach(async ({ page }, testInfo) => {
      if (testInfo.status !== 'passed') {
          // Capture diagnostic info
          const diagnostics = await page.evaluate(() => ({
              localStorage: { ...localStorage },
              url: window.location.href,
              sqliteReady: (window as any).sqliteService?.isReady$?.getValue(),
          }));
          console.error('[HealthCheck] Diagnostic data:', JSON.stringify(diagnostics, null, 2));
      }
  });
  ```

---

## Phase 3: Optional Pyodide Check (Stretch)

### 3.1 Add Pyodide Bootstrap Verification

- [ ] Verify Pyodide worker is available (if applicable):
  ```typescript
  await test.step('Verify Pyodide worker (optional)', async () => {
      const pyodideReady = await page.evaluate(() => {
          const pyodideService = (window as any).pyodideService;
          // Some apps lazy-load Pyodide, so this may be null initially
          if (!pyodideService) return 'not-initialized';
          return pyodideService.isReady$?.getValue() === true ? 'ready' : 'pending';
      });
      
      // This is informational, not a hard requirement
      console.log(`[HealthCheck] Pyodide status: ${pyodideReady}`);
      // expect(pyodideReady).toBe('ready'); // Uncomment if Pyodide is critical
  });
  ```

---

## Verification Plan

### Automated

```bash
# Run health check in isolation
npx playwright test e2e/specs/health-check.spec.ts --workers=4

# Run as gate test before full suite
npx playwright test e2e/specs/health-check.spec.ts && npx playwright test
```

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/health-check.spec.ts` | Enhancement | 36 → ~55 |

---

## Acceptance Criteria

- [ ] Seed data verification passes
- [ ] Browser mode verification passes
- [ ] DB name isolation verification passes
- [ ] Test remains under 60 lines
- [ ] Test completes in under 10 seconds
- [ ] Score improves from 8.0/10 to ≥9.0/10

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Seed data queries fail on schema change | Use robust COUNT(*) queries |
| modeService not exposed on window | Check for existence before calling |
| Pyodide not always loaded | Make check informational, not assertive |
