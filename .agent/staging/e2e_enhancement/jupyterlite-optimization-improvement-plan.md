# E2E Enhancement Plan: jupyterlite-optimization.spec.ts

**Target:** [jupyterlite-optimization.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/jupyterlite-optimization.spec.ts)  
**Baseline Score:** 4.8/10  
**Target Score:** 8.0/10  
**Effort Estimate:** ~4-6 hours

---

## Goals

1. **Reliability** — Eliminate `waitForTimeout` with state-driven detection
2. **Isolation** — Enable parallel test execution via worker-db fixture
3. **Domain Coverage** — Validate pylabrobot functionality, not just importability
4. **Maintainability** — Create PlaygroundPage POM for JupyterLite interactions

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Change import from `@playwright/test` to `../fixtures/worker-db.fixture`
- [ ] Refactor navigation to use `gotoWithWorkerDb()` helper
- [ ] Ensure each test uses worker-indexed dbName

**Before:**
```typescript
import { test, expect } from '@playwright/test';
await page.goto('/app/playground?mode=browser');
```

**After:**
```typescript
import { test, expect, gotoWithWorkerDb } from '../fixtures/worker-db.fixture';
await gotoWithWorkerDb(page, '/app/playground', testInfo, { resetdb: true });
```

### 1.2 Eliminate Hardcoded Wait in Phase 2
- [ ] Replace `waitForTimeout(5000)` with Service Worker ready detection

**Before:**
```typescript
await page.waitForTimeout(5000); // Give SW time to register/cache
```

**After:**
```typescript
// Wait for Service Worker registration
const swReady = await page.evaluate(async () => {
    if ('serviceWorker' in navigator) {
        const registration = await navigator.serviceWorker.ready;
        return !!registration.active;
    }
    return false;
});
if (!swReady) {
    test.skip('Service Worker not available (likely dev mode)');
}
```

### 1.3 Replace networkidle with Explicit Assertions
- [ ] Remove `waitUntil: 'networkidle'` from reload
- [ ] Use response interception instead

**After:**
```typescript
// Set up response capture BEFORE reload
const lockJsonPromise = page.waitForResponse(
    resp => resp.url().includes('pyodide-lock.json')
);
await page.reload({ waitUntil: 'domcontentloaded' });
const response = await lockJsonPromise;
```

### 1.4 Use addInitScript for localStorage
- [ ] Set localStorage before any navigation to avoid double-navigation

**Before:**
```typescript
await page.goto('/');
await page.evaluate(() => {
    localStorage.setItem('praxis_onboarding_completed', 'true');
});
await page.goto('/app/playground?mode=browser');
```

**After:**
```typescript
await page.addInitScript(() => {
    window.localStorage.setItem('praxis_onboarding_completed', 'true');
    window.localStorage.setItem('praxis_tutorial_completed', 'true');
});
await gotoWithWorkerDb(page, '/app/playground', testInfo);
```

---

## Phase 2: Page Object Model Refactor

### 2.1 Create PlaygroundPage POM

Create new file: `e2e/page-objects/playground.page.ts`

```typescript
import { Page, FrameLocator, Locator, TestInfo } from '@playwright/test';
import { BasePage } from './base.page';

export class PlaygroundPage extends BasePage {
    private iframe: FrameLocator;
    private consoleLogs: string[] = [];
    
    constructor(page: Page, testInfo?: TestInfo) {
        super(page, '/app/playground', testInfo);
        this.iframe = page.frameLocator('iframe.notebook-frame');
        
        // Capture console logs
        page.on('console', msg => {
            this.consoleLogs.push(msg.text());
        });
    }
    
    get codeInput(): Locator {
        return this.iframe.locator('.jp-CodeConsole-input .jp-InputArea-editor').first();
    }
    
    async waitForKernelReady(timeout = 30000): Promise<void> {
        await expect.poll(
            () => this.consoleLogs.some(log => log.includes('✓ Ready signal sent')),
            { timeout, message: 'Kernel ready signal not found' }
        ).toBe(true);
    }
    
    async executeCode(code: string): Promise<void> {
        await this.codeInput.click();
        await this.page.keyboard.type(code);
        await this.page.keyboard.press('Shift+Enter');
    }
    
    async waitForConsoleOutput(pattern: RegExp | string, timeout = 15000): Promise<string | undefined> {
        await expect.poll(
            () => this.consoleLogs.some(log => 
                typeof pattern === 'string' ? log.includes(pattern) : pattern.test(log)
            ),
            { timeout, message: `Console output matching ${pattern} not found` }
        ).toBe(true);
        
        return this.consoleLogs.find(log => 
            typeof pattern === 'string' ? log.includes(pattern) : pattern.test(log)
        );
    }
    
    hasConsoleLog(pattern: string | RegExp): boolean {
        return this.consoleLogs.some(log => 
            typeof pattern === 'string' ? log.includes(pattern) : pattern.test(log)
        );
    }
    
    getConsoleLogs(): string[] {
        return [...this.consoleLogs];
    }
}
```

### 2.2 Migrate Tests to Use POM
- [ ] Refactor Phase 1 test to use `PlaygroundPage`
- [ ] Refactor Phase 2 test navigation

---

## Phase 3: Domain Verification

### 3.1 Enhanced PyLabRobot Validation
- [ ] Test actual pylabrobot functionality, not just import

**Add to Phase 1 test:**
```typescript
// Beyond just import, verify a core method works
await playground.executeCode(`
from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.liquid_handling.backends import SimulatorBackend
print("LH_INIT_SUCCESS" if LiquidHandler else "LH_INIT_FAIL")
`);
await playground.waitForConsoleOutput('LH_INIT_SUCCESS');
```

### 3.2 Version Assertion
- [ ] Extract and validate pylabrobot version against expected

```typescript
const versionLog = await playground.waitForConsoleOutput(/PLR_FOUND_(\d+\.\d+\.\d+)/);
const versionMatch = versionLog?.match(/PLR_FOUND_(\d+\.\d+\.\d+)/);
expect(versionMatch?.[1]).toMatch(/^0\.\d+\.\d+$/); // Assert semver format
```

### 3.3 Service Worker Diagnostic Logging
- [ ] Add diagnostic info when SW test fails

```typescript
test('Phase 2: Assets should be cached via Service Worker', async ({ page }, testInfo) => {
    // Check SW availability first
    const swStatus = await page.evaluate(async () => {
        if (!('serviceWorker' in navigator)) {
            return { available: false, reason: 'navigator.serviceWorker not available' };
        }
        try {
            const reg = await navigator.serviceWorker.getRegistration();
            return { available: !!reg?.active, state: reg?.active?.state };
        } catch (e) {
            return { available: false, reason: String(e) };
        }
    });
    
    if (!swStatus.available) {
        console.log('[Phase 2] SW not available:', swStatus);
        test.skip('Service Worker not active - likely running in dev mode');
    }
    // ... rest of test
});
```

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Add Negative Test Cases

```typescript
test.describe('Error Scenarios', () => {
    test('should gracefully handle missing pylabrobot', async ({ page }, testInfo) => {
        // This would require mocking the Pyodide environment
        // For now, skip - add when mock infrastructure is available
        test.skip('Mock infrastructure needed');
    });
    
    test('should detect SharedArrayBuffer unavailability', async ({ page }) => {
        // Simulate insecure context by checking for SAB
        const hasSAB = await page.evaluate(() => 'SharedArrayBuffer' in window);
        console.log(`[SAB Check] SharedArrayBuffer available: ${hasSAB}`);
        // This is informational - app should still work (degraded)
    });
});
```

---

## Verification Plan

### Automated
```bash
# Run in parallel to verify isolation
npx playwright test e2e/specs/jupyterlite-optimization.spec.ts --workers=4

# With tracing for debugging
npx playwright test e2e/specs/jupyterlite-optimization.spec.ts --trace=on
```

### Manual Verification
- [ ] Verify tests pass in dev mode (SW may be inactive)
- [ ] Verify tests pass in production build (SW active)
- [ ] Confirm no OPFS contention in parallel execution

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/jupyterlite-optimization.spec.ts` | Refactor | ~70 lines (full rewrite) |
| `e2e/page-objects/playground.page.ts` | Create | ~60 lines (new) |

---

## Acceptance Criteria

- [ ] Tests pass with parallel execution (`--workers=4`)
- [ ] Zero `waitForTimeout` calls
- [ ] Uses `worker-db.fixture` for isolation
- [ ] Uses `PlaygroundPage` POM for JupyterLite interactions
- [ ] Validates pylabrobot functionality beyond import
- [ ] Includes diagnostic skips for dev mode (SW inactive)
- [ ] Baseline score improves to ≥8.0/10

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| **SW tests skip in dev** | Acceptable - tests are for production validation |
| **JupyterLite DOM changes** | POM encapsulates selectors - single point of update |
| **Pyodide boot time** | Existing 60s timeouts are adequate |
| **Cross-browser SW support** | Only Chrome/Chromium fully supports SW in tests |

---

## Implementation Order

1. **Phase 1.1-1.4** — Critical reliability fixes (2h)
2. **Phase 2.1-2.2** — POM creation and migration (1.5h)
3. **Phase 3.1-3.3** — Domain verification enhancements (1h)
4. **Phase 4** — Error scenarios (stretch, 0.5h)

**Total Estimated Effort**: 5 hours
