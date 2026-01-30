# E2E Enhancement Plan: ghpages-deployment.spec.ts

**Target:** [ghpages-deployment.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/ghpages-deployment.spec.ts)  
**Baseline Score:** 6.6/10  
**Target Score:** 8.5/10  
**Effort Estimate:** ~4 hours

---

## Goals

1. **Reliability** — Eliminate hardcoded waits; use response interceptors
2. **Coverage** — Add kernel execution and error state tests
3. **Maintainability** — Extract constants; consider minimal POM for shared patterns
4. **CI Value** — Maximize deployment confidence with minimal flake risk

---

## Phase 1: Eliminate Hardcoded Waits (Priority: Critical)

### 1.1 Replace `waitForTimeout(8000)` in JupyterLite 404 Test (L39)

**Current:**
```typescript
await page.waitForTimeout(8000);
```

**Replacement Strategy:**
```typescript
// Wait for network to settle + specific resource completion
await page.waitForLoadState('networkidle');
// Or use response consumption:
await page.waitForResponse(resp => 
    resp.url().includes('jupyterlite') && resp.status() === 200
);
```

### 1.2 Replace `waitForTimeout(5000)` in Path Doubling Test (L75)

**Current:**
```typescript
await page.waitForTimeout(5000);
```

**Replacement:**
```typescript
await page.waitForLoadState('networkidle');
```

### 1.3 Extract Timeout Constants

Create constants file or use Playwright config:
```typescript
const TIMEOUTS = {
    PYODIDE_INIT: 60000,
    SHELL_RENDER: 15000,
    NETWORK_SETTLE: 10000,
} as const;
```

---

## Phase 2: Strengthen Locators & Add Minimal POM

### 2.1 Fix Weak Logo Locator (L207)

**Current (too broad):**
```typescript
const logoElements = page.locator('[class*="logo"], img[alt*="Praxis"], svg');
```

**Improved:**
```typescript
// Option A: Add test ID to logo component
const logo = page.getByTestId('praxis-logo');

// Option B: More specific selector
const logo = page.locator('app-unified-shell').getByRole('img', { name: /praxis/i });
```

### 2.2 Create GH Pages Test Utilities (Optional)

Consider a lightweight helper for common patterns:
```typescript
// e2e/utils/ghpages-helpers.ts
export async function collectResourceErrors(page: Page, filter: (url: string) => boolean) {
    const errors: { url: string; status: number }[] = [];
    page.on('response', (resp) => {
        if (resp.status() >= 400 && filter(resp.url())) {
            errors.push({ url: resp.url(), status: resp.status() });
        }
    });
    return errors;
}
```

---

## Phase 3: Add Kernel Execution Smoke Test (Priority: High)

### 3.1 JupyterLite REPL Execution Test

**New test to add:**
```typescript
test('JupyterLite REPL can execute Python code', async ({ page }) => {
    await page.goto('playground');
    
    // Wait for REPL to be ready (look for kernel indicator)
    await expect(page.locator('[data-status="idle"]')).toBeVisible({ timeout: 60000 });
    
    // Find input cell and execute simple code
    const cell = page.locator('.jp-InputArea-editor').first();
    await cell.click();
    await cell.fill('print("GH Pages deployment OK")');
    await page.keyboard.press('Shift+Enter');
    
    // Verify output
    await expect(page.locator('.jp-OutputArea-output')).toContainText('GH Pages deployment OK');
});
```

### 3.2 SQLite Roundtrip Test

**Expand existing SQLite test:**
```typescript
test('SqliteService can execute queries', async ({ page }) => {
    await page.goto('app/home?mode=browser');
    
    // Wait for service readiness
    await page.waitForFunction(
        () => (window as any).sqliteService?.isReady$?.getValue() === true,
        { timeout: 60000 }
    );
    
    // Execute a simple query via exposed test API
    const result = await page.evaluate(() => {
        const svc = (window as any).sqliteService;
        return svc.query('SELECT 1 as test');
    });
    
    expect(result).toBeDefined();
});
```

---

## Phase 4: Error State Tests (Priority: Medium)

### 4.1 Invalid Route 404 Page

```typescript
test('invalid route shows 404 or redirects', async ({ page }) => {
    const response = await page.goto('app/nonexistent-route-xyz');
    // Depending on app behavior:
    expect(response?.status()).toBe(404);
    // OR verify redirect to home:
    expect(page.url()).toContain('/app/home');
});
```

### 4.2 Document Known Bug Explicitly

Replace silent exclusion (L163–168) with tracked skip:
```typescript
test.fixme('sqlite3-opfs-async-proxy.js loads from correct path', async ({ page }) => {
    // Tracked in issue #XXX
    // Currently requests from root instead of /assets/wasm/
});
```

---

## Phase 5: Cross-Browser Coverage (Stretch)

### 5.1 Add Safari Project

In `playwright.ghpages.config.ts`:
```typescript
projects: [
    {
        name: 'ghpages-chromium',
        use: { ...devices['Desktop Chrome'] },
    },
    {
        name: 'ghpages-webkit',
        use: { ...devices['Desktop Safari'] },
    },
],
```

Note: Safari may fail SharedArrayBuffer tests without proper headers—this is the point.

---

## Verification Plan

### Automated
```bash
# Full GH Pages suite
npx playwright test --config=playwright.ghpages.config.ts

# Just this spec
npx playwright test e2e/specs/ghpages-deployment.spec.ts --config=playwright.ghpages.config.ts

# With tracing for debugging
npx playwright test --config=playwright.ghpages.config.ts --trace=on
```

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/ghpages-deployment.spec.ts` | Refactor waits, add tests | ~50 lines modified, ~40 added |
| `e2e/utils/ghpages-helpers.ts` | Create (optional) | ~30 lines new |
| `playwright.ghpages.config.ts` | Add Safari project (stretch) | ~10 lines |
| `src/app/components/shell/*.ts` | Add `data-testid="praxis-logo"` | 1 line |

---

## Acceptance Criteria

- [ ] Tests pass with `--config=playwright.ghpages.config.ts`
- [ ] Zero `waitForTimeout` calls
- [ ] Kernel execution smoke test passes (Pyodide or JupyterLite)
- [ ] SQLite roundtrip test passes
- [ ] Known bugs documented with `test.fixme()` and issue links
- [ ] Timeout constants extracted to named values
- [ ] Baseline score improves to ≥8.5/10

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Kernel execution test too slow | Use 60s timeout; skip in fast CI runs |
| REPL selectors change | Use stable `data-testid` attributes |
| Safari project fails in CI | Gate behind browser matrix flag |
