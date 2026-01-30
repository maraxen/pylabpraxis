# E2E Enhancement Plan: interactive-protocol.spec.ts

**Target:** [interactive-protocol.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/interactive-protocol.spec.ts)  
**Baseline Score:** 4.8/10  
**Target Score:** 8.0/10  
**Effort Estimate:** 2-3 days

---

## Goals

1. **Reliability** — Eliminate 9+ seconds of hardcoded waits; replace with state-driven assertions
2. **Isolation** — Integrate worker-indexed DB fixture for parallel test execution
3. **Domain Coverage** — Verify Python output values, add confirm=No path, test error states
4. **Maintainability** — Extract PlaygroundPage and InteractionDialogHelper POMs

---

## Phase 1: Infrastructure & Reliability (Priority: Critical)

### 1.1 Worker Isolation Integration
- [ ] Import from `worker-db.fixture` instead of `@playwright/test`
- [ ] Use `gotoWithWorkerDb(page, '/app/playground', testInfo)` for navigation
- [ ] Remove manual `resetdb=1` handling (fixture handles it)

**Before:**
```typescript
import { test, expect } from '@playwright/test';
// ...
await page.goto('/app/playground?mode=browser&resetdb=1');
```

**After:**
```typescript
import { test, expect, gotoWithWorkerDb } from '../fixtures/worker-db.fixture';
// ...
await gotoWithWorkerDb(page, '/app/playground', testInfo);
```

### 1.2 Eliminate Hardcoded Waits
Replace each `waitForTimeout` with a state observation:

| Current (Line) | Replacement Strategy |
|----------------|---------------------|
| L43: `waitForTimeout(1000)` after dialog dismiss | `expect(jupyterDialog).not.toBeVisible()` |
| L55: `waitForTimeout(2000)` before editor click | `editor.waitFor({ state: 'stable' })` or use Playwright auto-wait |
| L57: `waitForTimeout(1000)` after click | Remove — covered by `pressSequentially` wait |
| L64: `waitForTimeout(500)` after clear | `expect(editor).toHaveText('')` or minimal content check |
| L91: `waitForTimeout(1000)` before run | Remove — Playwright auto-waits on click |
| L109/123: `waitForTimeout(500)` for fallback | Keep as minimal retry delay (reduce to 200ms) |
| L143/154: `waitForTimeout(1000)` after dialog action | `expect(outputArea).toContainText('next expected output')` |

### 1.3 Replace Force Clicks
- [ ] **Editor click (L56):** Replace with focused click sequence:
  ```typescript
  await editor.waitFor({ state: 'visible' });
  await editor.scrollIntoViewIfNeeded();
  await editor.click();
  ```
- [ ] **Run button (L105):** Add explicit wait for button state:
  ```typescript
  await runBtn.waitFor({ state: 'visible' });
  await expect(runBtn).toBeEnabled();
  await runBtn.click();
  ```

### 1.4 Robust Error Handling
- [ ] Replace silent catches with conditional assertions:
  ```typescript
  // Instead of try/catch with empty block
  const welcomeDialog = page.getByRole('dialog', { name: /Welcome/i });
  if (await welcomeDialog.isVisible({ timeout: 3000 }).catch(() => false)) {
    await welcomeDialog.getByRole('button', { name: /Skip|Close|Get Started/i }).click();
    await expect(welcomeDialog).not.toBeVisible();
  }
  ```

---

## Phase 2: Page Object Refactor

### 2.1 Create PlaygroundPage POM
**File:** `e2e/page-objects/playground.page.ts`

```typescript
import { Page, FrameLocator, Locator } from '@playwright/test';
import { BasePage } from './base.page';

export class PlaygroundPage extends BasePage {
    readonly jupyterFrame: FrameLocator;
    readonly loadingOverlay: Locator;
    
    constructor(page: Page, testInfo?: any) {
        super(page, '/app/playground', testInfo);
        this.jupyterFrame = page.frameLocator('iframe.notebook-frame');
        this.loadingOverlay = page.locator('.loading-overlay');
    }
    
    async waitForJupyterReady(): Promise<void> {
        await expect(this.loadingOverlay).not.toBeVisible({ timeout: 60000 });
    }
    
    get lastCell(): Locator {
        return this.jupyterFrame.locator('.jp-Cell').last();
    }
    
    get editor(): Locator {
        return this.lastCell.locator('.cm-content, .CodeMirror').first();
    }
    
    get runButton(): Locator {
        return this.jupyterFrame.locator('button[data-command="notebook:run-and-advance"]')
            .or(this.jupyterFrame.locator('button[title*="Run"]'))
            .first();
    }
    
    async typeCode(code: string): Promise<void> {
        await this.editor.click();
        const modifier = process.platform === 'darwin' ? 'Meta' : 'Control';
        await this.editor.press(`${modifier}+A`);
        await this.editor.press('Backspace');
        await this.editor.pressSequentially(code, { delay: 10 });
    }
    
    async runCode(): Promise<void> {
        if (await this.runButton.isVisible()) {
            await this.runButton.click();
        } else {
            await this.editor.click();
            await this.page.keyboard.press('Shift+Enter');
        }
    }
    
    async waitForOutput(text: string): Promise<void> {
        const output = this.jupyterFrame.locator('.jp-OutputArea-output').filter({ hasText: text });
        await expect(output).toBeVisible({ timeout: 15000 });
    }
}
```

### 2.2 Create InteractionDialogHelper
**File:** `e2e/page-objects/interaction-dialog.helper.ts`

```typescript
import { Page, Locator, expect } from '@playwright/test';

export class InteractionDialogHelper {
    readonly dialog: Locator;
    
    constructor(page: Page) {
        this.dialog = page.locator('app-interaction-dialog');
    }
    
    async waitForPause(expectedMessage: string): Promise<void> {
        await expect(this.dialog).toBeVisible({ timeout: 60000 });
        await expect(this.dialog).toContainText(expectedMessage);
        await expect(this.dialog.getByRole('button', { name: 'Resume' })).toBeVisible();
    }
    
    async resume(): Promise<void> {
        await this.dialog.getByRole('button', { name: 'Resume' }).click();
        // Wait for dialog to start dismissing (don't wait for full hide yet)
    }
    
    async waitForConfirm(expectedMessage: string): Promise<void> {
        await expect(this.dialog).toBeVisible({ timeout: 30000 });
        await expect(this.dialog).toContainText(expectedMessage);
    }
    
    async confirmYes(): Promise<void> {
        await this.dialog.getByRole('button', { name: 'Yes' }).click();
    }
    
    async confirmNo(): Promise<void> {
        await this.dialog.getByRole('button', { name: 'No' }).click();
    }
    
    async waitForInput(expectedPrompt: string): Promise<void> {
        await expect(this.dialog).toBeVisible({ timeout: 30000 });
        await expect(this.dialog).toContainText(expectedPrompt);
    }
    
    async submitInput(value: string): Promise<void> {
        await this.dialog.locator('input').fill(value);
        await this.dialog.getByRole('button', { name: 'Submit' }).click();
    }
    
    async expectDismissed(): Promise<void> {
        await expect(this.dialog).not.toBeVisible({ timeout: 10000 });
    }
}
```

---

## Phase 3: Domain Verification

### 3.1 Python Output Verification
Add assertions for Python-side output after each interaction:

```typescript
// After Resume
await playground.waitForOutput('Paused done');

// After Confirm Yes
await playground.waitForOutput('Confirmed: True');

// After Input Submit
await playground.waitForOutput('Hello Tester');
```

### 3.2 Add Confirm=No Test Case
- [ ] Create separate test: `should handle confirm with No response`
  ```typescript
  test('should handle confirm rejection', async ({ page }, testInfo) => {
      // ... setup code ...
      
      const pythonCode = `
  from praxis.interactive import confirm
  ans = await confirm("Delete all samples?")
  print(f"User confirmed: {ans}")
  `;
      
      // ... type and run code ...
      
      await dialogHelper.waitForConfirm('Delete all samples?');
      await dialogHelper.confirmNo();
      
      await playground.waitForOutput('User confirmed: False');
  });
  ```

### 3.3 Add Input Edge Cases
- [ ] Test empty input submission
- [ ] Test input with special characters (quotes, newlines, unicode)

---

## Phase 4: Error State Coverage (Stretch)

### 4.1 Python Syntax Error
```typescript
test('should display error for invalid Python syntax', async ({ page }, testInfo) => {
    // Type broken code
    await playground.typeCode('await pause("test" invalid syntax');
    await playground.runCode();
    
    // Verify error appears in output area (not as dialog)
    await playground.waitForOutput('SyntaxError');
});
```

### 4.2 Dialog Cancel Behavior
```typescript
test('should handle Escape key during input dialog', async ({ page }, testInfo) => {
    // ... setup pause/confirm/input code ...
    
    await dialogHelper.waitForInput('Name?');
    await page.keyboard.press('Escape');
    
    // Verify behavior (error? default value? dialog persists?)
    // Note: Requires understanding of expected behavior
});
```

---

## Verification Plan

### Automated
```bash
# Single test run
npx playwright test e2e/specs/interactive-protocol.spec.ts --headed

# Parallel isolation test (4 workers)
npx playwright test e2e/specs/interactive-protocol.spec.ts --workers=4 --repeat-each=3

# Full regression
npx playwright test --grep "interactive"
```

### Manual Verification
- [ ] Run test 5x in parallel and confirm no OPFS contention errors
- [ ] Review screenshots for dialog styling consistency
- [ ] Confirm Python output values match expected

---

## Files Changed

| File | Action | Lines Affected |
|------|--------|----------------|
| `e2e/specs/interactive-protocol.spec.ts` | Refactor | 170 → ~80 (with POMs) |
| `e2e/page-objects/playground.page.ts` | Create | ~60 new |
| `e2e/page-objects/interaction-dialog.helper.ts` | Create | ~50 new |

---

## Acceptance Criteria

- [ ] Tests pass with `--workers=4` parallel execution
- [ ] Zero `force: true` clicks
- [ ] Zero `waitForTimeout` calls (except ≤200ms retry delays)
- [ ] Uses `PlaygroundPage` and `InteractionDialogHelper` POMs
- [ ] Verifies Python output values (not just dialog appearance)
- [ ] Includes at least one confirm=No test case
- [ ] Baseline score improves to ≥8.0/10

---

## Risk Assessment

| Risk | Probability | Mitigation |
|------|------------|------------|
| JupyterLite iframe timing unpredictable | High | Use output-based assertions, not time-based |
| Editor focus issues persist after removing force clicks | Medium | Add explicit focus sequence with scroll |
| Pyodide kernel state leaks between tests | Low | Each test navigates with `resetdb=1` |

---

## Phase Implementation Order

```
Phase 1.1 (Worker Isolation) ──┐
                               ├─► Phase 2 (POMs) ──► Phase 3 (Domain) ──► Phase 4 (Errors)
Phase 1.2-1.4 (Reliability) ───┘
```

**Estimated Timeline:**
- Phase 1: 4 hours
- Phase 2: 4 hours  
- Phase 3: 3 hours
- Phase 4: 2 hours (stretch goal)
