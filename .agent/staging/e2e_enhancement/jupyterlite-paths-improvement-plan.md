# E2E Enhancement Plan: jupyterlite-paths.spec.ts

**Target:** [jupyterlite-paths.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/jupyterlite-paths.spec.ts)  
**Baseline Score:** 4.5/10  
**Target Score:** 7.5/10  
**Effort Estimate:** Medium (3-4 hours)

---

## Goals

1. **Production Coverage** — Enable and execute GH Pages simulation tests
2. **Reliability** — Replace hardcoded waits with network-idle patterns
3. **Completeness** — Assert on failed requests, not just path doubling
4. **Maintainability** — Extract path verification helpers for reuse

---

## Phase 1: Enable Production Mode Tests (Priority: Critical)

### 1.1 Create GH Pages Server Fixture

The GH Pages tests require a server with COOP/COEP headers at `localhost:8080/praxis/`. Create a reusable fixture.

- [ ] **Create fixture:** `e2e/fixtures/ghpages-server.fixture.ts`
  ```typescript
  // Launches a static server simulating GH Pages deployment
  export const test = baseTest.extend<{ ghPagesServer: { port: number; baseUrl: string } }>({
      ghPagesServer: [async ({}, use) => {
          // Use `http-server` or custom Express setup with COOP/COEP
          // Serve from dist/praxis with /praxis/ prefix
          await use({ port: 8080, baseUrl: 'http://localhost:8080/praxis/' });
      }, { scope: 'worker' }]
  });
  ```

- [ ] **Remove `test.describe.skip`** at L103
- [ ] **Use fixture** to conditionally run production tests

### 1.2 Alternative: Playwright Project for GH Pages

Instead of a runtime fixture, define a separate Playwright project.

- [ ] **Update `playwright.config.ts`:**
  ```typescript
  projects: [
      { name: 'dev', use: { baseURL: 'http://localhost:4200' } },
      { name: 'ghpages', use: { baseURL: 'http://localhost:8080/praxis/' } },
  ]
  ```

- [ ] **Run with:** `npx playwright test --project=ghpages`
- [ ] **Modify tests** to use `test.describe` with project-specific conditions

---

## Phase 2: Eliminate Hardcoded Waits (Priority: Critical)

### 2.1 Replace `waitForTimeout` with Network Idle

- [ ] **Replace L72 `waitForTimeout(5000)`** with:
  ```typescript
  // Wait for JupyterLite assets to finish loading
  await page.waitForLoadState('networkidle');
  
  // Additional poll for JupyterLite-specific readiness if needed
  await expect.poll(async () => {
      return doubledPathRequests.length === 0 && failedRequests.length === 0;
  }, { timeout: 15000, message: 'JupyterLite assets should load without path issues' }).toBe(true);
  ```

### 2.2 Use Response Promise Patterns

- [ ] **Collect critical responses** before navigating:
  ```typescript
  const schemaResponse = page.waitForResponse(r => r.url().includes('schemas/all.json'));
  const themeResponse = page.waitForResponse(r => r.url().includes('theme-light-extension/index.css'));
  
  await page.goto('/playground');
  
  await Promise.all([schemaResponse, themeResponse]);
  ```

---

## Phase 3: Assert on Failed Requests (Priority: High)

### 3.1 Fail on Critical 404s

- [ ] **Replace logging with assertion** at L77-80:
  ```typescript
  // Define critical resources that MUST load successfully
  const criticalPatterns = [
      'jupyter-lite.json',
      'all.json',
      'index.css',
      'pyodide.js'
  ];
  
  const criticalFailures = failedRequests.filter(url =>
      criticalPatterns.some(p => url.includes(p))
  );
  
  expect(criticalFailures, `Critical JupyterLite resources failed: ${criticalFailures.join(', ')}`).toHaveLength(0);
  ```

### 3.2 Add Wheel Accessibility Check

- [ ] **Verify `.whl` files accessible:** (new test)
  ```typescript
  test('pylabrobot wheel accessible without path doubling', async ({ page }) => {
      const response = await page.goto('/assets/jupyterlite/pypi/pylabrobot-0.1.6-py3-none-any.whl');
      expect(response?.status()).toBe(200);
      expect(response?.headers()['content-type']).toContain('application/octet-stream');
  });
  ```

---

## Phase 4: Improve Selectors and Add POM

### 4.1 Add Test IDs to Playground Component

- [ ] **Update `playground.component.html`:**
  ```html
  <iframe data-testid="jupyterlite-iframe" ...></iframe>
  ```

- [ ] **Update test locators:**
  ```typescript
  const jupyterIframe = page.getByTestId('jupyterlite-iframe');
  await expect(jupyterIframe).toBeVisible();
  ```

### 4.2 Extract Path Verification Helper

- [ ] **Create utility:** `e2e/helpers/path-verifier.ts`
  ```typescript
  export function createPathDoublingMonitor(page: Page) {
      const failedRequests: string[] = [];
      const doubledPaths: string[] = [];
      
      page.on('response', (response) => {
          const url = response.url();
          if (url.includes('jupyterlite') && response.status() === 404) {
              failedRequests.push(url);
          }
          if (url.match(/\/praxis\/.*\/praxis\//)) {
              doubledPaths.push(url);
          }
      });
      
      return { failedRequests, doubledPaths };
  }
  ```

---

## Phase 5: Add Header Verification (Stretch)

### 5.1 COOP/COEP Headers Check

- [ ] **Verify cross-origin isolation headers:**
  ```typescript
  test('served with required cross-origin headers', async ({ page }) => {
      const response = await page.goto('/playground');
      const headers = response?.headers() ?? {};
      
      expect(headers['cross-origin-opener-policy']).toBe('same-origin');
      expect(headers['cross-origin-embedder-policy']).toBe('require-corp');
  });
  ```

---

## Verification Plan

### Automated

```bash
# Development mode tests
npx playwright test e2e/specs/jupyterlite-paths.spec.ts --workers=1

# With GH Pages project (after Phase 1)
npx playwright test e2e/specs/jupyterlite-paths.spec.ts --project=ghpages --workers=1

# Parallel verification after refactor
npx playwright test e2e/specs/jupyterlite-paths.spec.ts --workers=4
```

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/jupyterlite-paths.spec.ts` | Refactor | ~80 |
| `e2e/helpers/path-verifier.ts` | Create | ~30 |
| `e2e/fixtures/ghpages-server.fixture.ts` | Create (optional) | ~40 |
| `playwright.config.ts` | Update | ~10 |
| `src/.../playground.component.html` | Update (test IDs) | ~5 |

---

## Acceptance Criteria

- [ ] Tests pass in both `dev` and `ghpages` projects
- [ ] Zero `waitForTimeout` calls
- [ ] Production mode tests (`test.describe.skip`) are enabled
- [ ] Failed requests for critical resources cause test failure
- [ ] Path doubling detection uses shared utility
- [ ] Uses `getByTestId` for iframe locator
- [ ] Baseline score improves to ≥7.5/10

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| **GH Pages server setup complexity** | Start with Playwright project config; add fixture only if needed |
| **networkidle may timeout on slow CI** | Add fallback with explicit `waitForResponse` for critical assets |
| **Header verification may vary by environment** | Make COOP/COEP test conditional on project |

---

## Dependencies

- **Requires:** Running dev server (`ng serve`) for dev mode tests
- **Requires:** Build artifacts in `dist/praxis/` for GH Pages tests
- **Blocks:** None—this is an infrastructure test
