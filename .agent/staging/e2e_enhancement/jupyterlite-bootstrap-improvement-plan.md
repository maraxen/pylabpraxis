# E2E Enhancement Plan: `jupyterlite-bootstrap.spec.ts`

**Target:** [jupyterlite-bootstrap.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/jupyterlite-bootstrap.spec.ts)  
**SDET Report:** [jupyterlite-bootstrap-report.md](./jupyterlite-bootstrap-report.md)  
**Baseline Score:** 5.5/10  
**Target Score:** 8.5/10  
**Effort Estimate:** ~5 hours

---

## Goals

1. **Reliability** — Eliminate `force: true` clicks, `waitForTimeout`, and silent catches
2. **Isolation** — Enable parallel test execution via worker-indexed databases
3. **Coverage** — Add Phase 2 bootstrap verification, error states, and network validation
4. **Maintainability** — Extract JupyterLite interactions to a reusable Page Object

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration

#### [MODIFY] [jupyterlite-bootstrap.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/jupyterlite-bootstrap.spec.ts)

**Current (L2, L17):**
```typescript
import { test, expect, Page } from '@playwright/test';
// ...
await page.goto('/app/playground?mode=browser&resetdb=1');
```

**Proposed:**
```typescript
import { test, expect } from '../fixtures/worker-db.fixture';
import { PlaygroundPage } from '../page-objects/playground.page';

test('...', async ({ page, workerIndex }) => {
  const playground = new PlaygroundPage(page, workerIndex);
  await playground.goto();
  // ...
});
```

**Changes:**
- Import from worker-db fixture to get `workerIndex`
- Navigation includes `dbName=praxis-worker-{workerIndex}` for isolation
- Remove manual `resetdb=1` (handled by fixture or POM)

---

### 1.2 Eliminate Hardcoded Waits

| Line | Current | Replacement |
|------|---------|-------------|
| L48 | `page.waitForTimeout(500)` | `await jupyterFrame.locator('.jp-Dialog').waitFor({ state: 'hidden', timeout: 3000 }).catch(() => {})` |

**Pattern:**
```typescript
// Wait for dialogs to fully dismiss, not arbitrary time
const dialog = jupyterFrame.locator('.jp-Dialog');
await dialog.waitFor({ state: 'hidden', timeout: 5000 }).catch(() => {
  console.log('[Test] No dialog to dismiss or already hidden');
});
```

---

### 1.3 Remove Force Clicks

| Line | Current | Fix |
|------|---------|-----|
| L92, L114, L134 | `codeInput.click({ force: true })` | Wait for code input to be actionable, then normal click |

**Pattern:**
```typescript
// Before interacting with code input, ensure kernel is idle and no dialogs
await jupyterFrame.locator('.jp-mod-idle').first().waitFor({ timeout: 30000 });
await jupyterFrame.locator('.jp-Dialog').waitFor({ state: 'hidden', timeout: 3000 }).catch(() => {});

const codeInput = jupyterFrame.locator('.jp-CodeConsole-input .jp-InputArea-editor');
await expect(codeInput).toBeVisible();
await codeInput.click(); // No force needed
```

---

### 1.4 Replace Silent Catches with Diagnostic Logging

| Line | Current | Fix |
|------|---------|-----|
| L50-52, L84-89, L107-112, L127-132 | `catch { /* ignore */ }` | `catch (e) { console.log('[Test] Dialog dismiss skipped:', e.message); }` |

**Example:**
```typescript
try {
  const okButton = jupyterFrame.getByRole('button', { name: 'OK' });
  if (await okButton.isVisible({ timeout: 1000 })) {
    await okButton.click();
    console.log('[Test] Dismissed OK dialog');
  }
} catch (e) {
  console.log('[Test] No OK dialog present or timeout:', (e as Error).message);
}
```

---

## Phase 2: Page Object Model (Priority: High)

### 2.1 Create JupyterLite Page Object

#### [CREATE] `e2e/page-objects/jupyterlite.page.ts`

```typescript
import { Page, FrameLocator, Locator, expect } from '@playwright/test';

export class JupyterlitePage {
  readonly page: Page;
  readonly frame: FrameLocator;
  readonly codeInput: Locator;
  readonly kernelIdleIndicator: Locator;

  constructor(page: Page) {
    this.page = page;
    this.frame = page.frameLocator('iframe.notebook-frame');
    this.codeInput = this.frame.locator('.jp-CodeConsole-input .jp-InputArea-editor');
    this.kernelIdleIndicator = this.frame.locator('.jp-mod-idle').first();
  }

  async waitForFrameAttached(timeout = 20000): Promise<void> {
    const frameElement = this.page.locator('iframe.notebook-frame');
    await expect(frameElement).toBeVisible({ timeout });
  }

  async waitForKernelIdle(timeout = 45000): Promise<void> {
    await this.kernelIdleIndicator.waitFor({ timeout, state: 'visible' });
  }

  async dismissDialogs(maxAttempts = 3): Promise<void> {
    for (let i = 0; i < maxAttempts; i++) {
      try {
        const okButton = this.frame.getByRole('button', { name: 'OK' });
        if (await okButton.isVisible({ timeout: 1000 })) {
          await okButton.click();
          await this.frame.locator('.jp-Dialog').waitFor({ state: 'hidden', timeout: 2000 }).catch(() => {});
        }
      } catch {
        break; // No more dialogs
      }
    }
  }

  async executeCode(code: string): Promise<void> {
    await this.dismissDialogs();
    await expect(this.codeInput).toBeVisible();
    await this.codeInput.click();
    await this.page.keyboard.type(code);
    await this.page.keyboard.press('Shift+Enter');
  }

  async assertKernelDialogNotVisible(timeout = 5000): Promise<void> {
    const kernelDialog = this.frame.locator('.jp-Dialog').filter({ hasText: /kernel|select/i });
    await expect(kernelDialog).not.toBeVisible({ timeout });
  }
}
```

### 2.2 Create Playground Page Object

#### [CREATE] `e2e/page-objects/playground.page.ts`

```typescript
import { Page, expect } from '@playwright/test';
import { JupyterlitePage } from './jupyterlite.page';

export class PlaygroundPage {
  readonly page: Page;
  readonly workerIndex: number;
  readonly jupyter: JupyterlitePage;
  readonly loadingOverlay: Locator;

  constructor(page: Page, workerIndex: number = 0) {
    this.page = page;
    this.workerIndex = workerIndex;
    this.jupyter = new JupyterlitePage(page);
    this.loadingOverlay = page.locator('.loading-overlay');
  }

  async goto(): Promise<void> {
    // Set localStorage before Angular loads
    await this.page.goto('/');
    await this.page.evaluate(() => {
      localStorage.setItem('praxis_onboarding_completed', 'true');
      localStorage.setItem('praxis_tutorial_completed', 'true');
    });

    const dbName = `praxis-worker-${this.workerIndex}`;
    await this.page.goto(`/app/playground?mode=browser&dbName=${dbName}&resetdb=1`);
  }

  async waitForBootstrapComplete(consoleLogs: string[]): Promise<void> {
    // Wait for iframe
    await this.jupyter.waitForFrameAttached();

    // Assert no blocking dialogs
    const skipBtn = this.page.getByRole('button', { name: 'Skip for Now' });
    await expect(skipBtn).not.toBeVisible({ timeout: 3000 });
    await this.jupyter.assertKernelDialogNotVisible();

    // Wait for loading complete
    await expect(this.loadingOverlay).toBeHidden({ timeout: 60000 });

    // Dismiss any theme error dialogs
    await this.jupyter.dismissDialogs();

    // Wait for kernel idle
    await this.jupyter.waitForKernelIdle();

    // Verify bootstrap signals
    await expect.poll(() => {
      const pyodideReady = consoleLogs.some(log => log.includes('[PythonRuntime] Pyodide ready'));
      const shimsInjected = consoleLogs.some(log => 
        log.includes('WebSerial injected') || log.includes('WebUSB injected')
      );
      return pyodideReady && shimsInjected;
    }, { timeout: 60000, message: 'Bootstrap signals not detected' }).toBe(true);
  }
}
```

### 2.3 Refactored Test Using POMs

```typescript
import { test, expect } from '../fixtures/worker-db.fixture';
import { PlaygroundPage } from '../page-objects/playground.page';

test.describe('JupyterLite Bootstrap Verification', () => {
  test('JupyterLite Seamless Bootstrap Validation', async ({ page, workerIndex }) => {
    const consoleLogs: string[] = [];
    page.on('console', msg => consoleLogs.push(msg.text()));

    const playground = new PlaygroundPage(page, workerIndex);
    await playground.goto();
    await playground.waitForBootstrapComplete(consoleLogs);

    // Kernel Execution: print("hello world")
    await playground.jupyter.executeCode('print("hello world")');
    await expect.poll(() => consoleLogs.some(log => log.includes('hello world')), {
      timeout: 15000, message: 'Expected "hello world" output'
    }).toBe(true);

    // PyLabRobot Import
    await playground.jupyter.executeCode('import pylabrobot; print(f"PLR v{pylabrobot.__version__}")');
    await expect.poll(() => consoleLogs.some(log => log.includes('PLR v')), {
      timeout: 15000, message: 'Expected pylabrobot version'
    }).toBe(true);

    // web_bridge Validation
    await playground.jupyter.executeCode('import web_bridge; print("web_bridge:", hasattr(web_bridge, "request_user_interaction"))');
    await expect.poll(() => consoleLogs.some(log => log.includes('web_bridge: True')), {
      timeout: 15000, message: 'Expected web_bridge import'
    }).toBe(true);
  });
});
```

---

## Phase 3: Coverage Expansion (Priority: Medium)

### 3.1 Phase 2 Bootstrap Verification

Add explicit check for Phase 2 signals:

```typescript
test('Phase 2 Bootstrap: Full payload received', async ({ page, workerIndex }) => {
  const consoleLogs: string[] = [];
  page.on('console', msg => consoleLogs.push(msg.text()));

  const playground = new PlaygroundPage(page, workerIndex);
  await playground.goto();
  await playground.waitForBootstrapComplete(consoleLogs);

  // Phase 2 specific signals
  await expect.poll(() => {
    const readySignal = consoleLogs.some(log => log.includes('✓ Ready signal sent'));
    const assetInjection = consoleLogs.some(log => log.includes('✓ Asset injection ready'));
    return readySignal && assetInjection;
  }, { timeout: 30000, message: 'Phase 2 signals not detected' }).toBe(true);
});
```

### 3.2 Network Verification: Wheel Installation

```typescript
test('Wheel Installation: pylabrobot.whl fetched successfully', async ({ page, workerIndex }) => {
  const wheelRequests: { url: string; status: number }[] = [];
  
  page.on('response', response => {
    if (response.url().includes('.whl')) {
      wheelRequests.push({ url: response.url(), status: response.status() });
    }
  });

  const playground = new PlaygroundPage(page, workerIndex);
  await playground.goto();
  await playground.waitForBootstrapComplete([]);

  // Verify wheel was fetched successfully
  const pylabrobotWheel = wheelRequests.find(r => r.url.includes('pylabrobot'));
  expect(pylabrobotWheel, 'pylabrobot wheel request not found').toBeDefined();
  expect(pylabrobotWheel!.status).toBe(200);
});
```

### 3.3 Error State: Invalid Python Syntax

```typescript
test('Error Handling: Python syntax error shows traceback', async ({ page, workerIndex }) => {
  const consoleLogs: string[] = [];
  page.on('console', msg => consoleLogs.push(msg.text()));

  const playground = new PlaygroundPage(page, workerIndex);
  await playground.goto();
  await playground.waitForBootstrapComplete(consoleLogs);

  // Execute invalid syntax
  await playground.jupyter.executeCode('print("unclosed');

  // Verify error appears (SyntaxError in console)
  await expect.poll(() => 
    consoleLogs.some(log => log.includes('SyntaxError') || log.includes('EOL while scanning')),
    { timeout: 10000, message: 'Expected SyntaxError in console' }
  ).toBe(true);
});
```

### 3.4 Asset Injection via BroadcastChannel

```typescript
test('Asset Injection: praxis:execute message is processed', async ({ page, workerIndex }) => {
  const consoleLogs: string[] = [];
  page.on('console', msg => consoleLogs.push(msg.text()));

  const playground = new PlaygroundPage(page, workerIndex);
  await playground.goto();
  await playground.waitForBootstrapComplete(consoleLogs);

  // Inject code via BroadcastChannel (simulating Angular host)
  await page.evaluate(() => {
    const channel = new BroadcastChannel('praxis_repl');
    channel.postMessage({
      type: 'praxis:execute',
      code: 'TEST_INJECTION = 42; print("Injected:", TEST_INJECTION)'
    });
  });

  await expect.poll(() => consoleLogs.some(log => log.includes('Injected: 42')), {
    timeout: 10000, message: 'Expected injected code output'
  }).toBe(true);
});
```

---

## Phase 4: Stretch Goals (Priority: Low)

### 4.1 Theme Toggle Test

```typescript
test('Theme Toggle: JupyterLite updates theme mid-session', async ({ page, workerIndex }) => {
  const playground = new PlaygroundPage(page, workerIndex);
  await playground.goto();
  await playground.waitForBootstrapComplete([]);

  // Toggle theme via Angular
  await page.evaluate(() => {
    document.body.classList.toggle('dark-theme');
    // Trigger Angular's theme effect
    window.dispatchEvent(new CustomEvent('themeChange'));
  });

  // Verify JupyterLite iframe reloads with new theme
  // (This may need adjustment based on actual implementation)
  await expect(playground.jupyter.frame.locator('body')).toHaveClass(/jp-theme-dark|jp-theme-light/);
});
```

### 4.2 Kernel Restart Recovery

```typescript
test('Kernel Recovery: Variables restored after kernel restart', async ({ page, workerIndex }) => {
  // This would require more complex state management testing
  // Placeholder for future implementation
});
```

---

## Verification Plan

### Automated

```bash
# Run single test with verbose logging
cd /Users/mar/Projects/praxis/praxis/web-client
npx playwright test e2e/specs/jupyterlite-bootstrap.spec.ts --workers=1 --timeout=180000

# Parallel execution test (verify worker isolation)
npx playwright test e2e/specs/jupyterlite-bootstrap.spec.ts --workers=4 --repeat-each=2
```

### Manual Verification

1. **Watch test execution** with UI mode:
   ```bash
   npx playwright test e2e/specs/jupyterlite-bootstrap.spec.ts --ui
   ```

2. **Verify no force clicks** — Search for `force: true`; should be zero occurrences

3. **Verify no hardcoded waits** — Search for `waitForTimeout`; should be zero occurrences

4. **Verify POM usage** — All JupyterLite interactions should go through `JupyterlitePage`

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/jupyterlite-bootstrap.spec.ts` | Refactor | ~150 lines rewritten |
| `e2e/page-objects/jupyterlite.page.ts` | Create | ~60 lines |
| `e2e/page-objects/playground.page.ts` | Create | ~50 lines |

---

## Acceptance Criteria

- [ ] Tests pass with `--workers=4` (parallel execution)
- [ ] Zero `force: true` clicks
- [ ] Zero `waitForTimeout` calls
- [ ] Uses `PlaygroundPage` and `JupyterlitePage` POMs
- [ ] Verifies Phase 2 bootstrap signals (`✓ Ready signal sent`)
- [ ] Verifies wheel network request returns 200
- [ ] Includes at least one error state test
- [ ] Baseline score improves to ≥8.5/10
