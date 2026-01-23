import { test, expect } from '@playwright/test';

test('should handle pause, confirm, and input interactions', async ({ page }) => {
    test.setTimeout(120000);
    page.on('console', msg => console.log(`BROWSER LOG: ${msg.text()}`));
    // 1. Navigate to /app/playground?mode=browser
    // We add resetdb=1 to ensure a clean state if needed
    await page.goto('/app/playground?mode=browser&resetdb=1');

    // 2. Wait for initialization
    await page.waitForSelector('app-playground', { timeout: 30000 });

    // Wait for SQLite/Pyodide to be ready
    await page.waitForFunction(() => (window as any).sqliteService?.isReady$?.getValue() === true, null, { timeout: 45000 });

    // Handle Welcome Dialog if it appears
    try {
        const dismissBtn = page.getByRole('button', { name: /Get Started|Skip|Close/i }).first();
        if (await dismissBtn.isVisible({ timeout: 5000 })) {
            await dismissBtn.click();
        }
    } catch (e) { }

    // Wait for JupyterLite/REPL to be ready (spinner to disappear)
    const loadingOverlay = page.locator('.loading-overlay');
    await expect(loadingOverlay).not.toBeVisible({ timeout: 60000 });

    const iframe = page.frameLocator('iframe.notebook-frame');

    // Handle potential JupyterLite initialization dialogs (e.g. "Error Loading Theme")
    // which can block interaction with the editor.
    try {
        const jupyterDialogBtn = iframe.locator('.jp-Dialog-button.jp-mod-accept').first()
            .or(iframe.getByRole('button', { name: 'OK' }));
        if (await jupyterDialogBtn.isVisible({ timeout: 10000 })) {
            console.log('Dismissing Jupyter dialog...');
            await jupyterDialogBtn.click();
            await page.waitForTimeout(1000);
        }
    } catch (e) { }

    // 3. Type code into the editor
    // Target the last cell (which should be the new empty one) and its editor
    const editor = iframe.locator('.jp-Cell').last().locator('.cm-content, .CodeMirror').first();

    console.log('Waiting for editor...');
    await expect(editor).toBeVisible({ timeout: 60000 });
    console.log('Clicking editor...');
    // Ensure the editor handle is stable
    await page.waitForTimeout(2000);
    await editor.click({ force: true });
    await page.waitForTimeout(1000);

    // Clear and type - use editor methods instead of page.keyboard since editor is in iframe
    const isMac = process.platform === 'darwin';
    const modifier = isMac ? 'Meta' : 'Control';
    await editor.press(`${modifier}+A`);
    await editor.press('Backspace');
    await page.waitForTimeout(500);

    const pythonCode = `from praxis.interactive import pause, confirm, input
import time

print("Step 1: Pause")
await pause("Check deck")
print("Paused done")

print("Step 2: Confirm")
ans = await confirm("Proceed?")
print(f"Confirmed: {ans}")

print("Step 3: Input")
name = await input("Name?")
print(f"Hello {name}")
`;

    // Use pressSequentially on the editor locator to ensure input goes into the iframe
    console.log('Inserting Python code...');
    await editor.pressSequentially(pythonCode, { delay: 10 });

    // Verify code was typed correctly
    await expect(editor).toContainText('from praxis.interactive import pause');
    await expect(editor).toContainText('print(f"Hello {name}")');

    // 4. Run the code
    await page.waitForTimeout(1000);

    // Debug: Take screenshot before running
    await page.screenshot({ path: 'e2e/screenshots/debug-before-run.png' });

    // Try clicking the Run button in the toolbar specifically
    // Use reliable selector found by research, plus fallbacks
    const runBtn = iframe.locator('button[data-command="notebook:run-and-advance"]')
        .or(iframe.locator('button[title*="Run"]'))
        .or(iframe.getByRole('button', { name: /Run/i }))
        .first();

    if (await runBtn.isVisible()) {
        console.log('Clicking Run button');
        await runBtn.click({ force: true });
    } else {
        console.log('Falling back to Shift+Enter');
        await editor.click();
        await page.waitForTimeout(500);
        await page.keyboard.press('Shift+Enter');
    }

    // Wait for Python to actually start executing
    try {
        // Wait for the text to appear in the notebook output area
        // We look for .jp-OutputArea-output to ensure we match output, not source code
        const outputLocator = iframe.locator('.jp-OutputArea-output').filter({ hasText: 'Step 1: Pause' });
        await expect(outputLocator).toBeVisible({ timeout: 10000 });
    } catch (e) {
        // Retry with Shift+Enter if first attempt failed
        await editor.click();
        await page.waitForTimeout(500);
        await page.keyboard.press('Shift+Enter');

        const outputLocator = iframe.locator('.jp-OutputArea-output').filter({ hasText: 'Step 1: Pause' });
        await expect(outputLocator).toBeVisible({ timeout: 10000 });
    }

    // 5. Verify Pause

    // 5. Verify Pause
    const dialog = page.locator('app-interaction-dialog');
    // Increased timeout for slow initialization
    await expect(dialog).toBeVisible({ timeout: 60000 });
    await expect(dialog).toContainText('Check deck');

    // Capture screenshot of Pause dialog
    await page.screenshot({ path: 'e2e/screenshots/interactive-pause.png' });

    await dialog.getByRole('button', { name: 'Resume' }).click();

    // Small wait for execution to proceed
    await page.waitForTimeout(1000);

    // 6. Verify Confirm
    await expect(dialog).toBeVisible({ timeout: 10000 });
    await expect(dialog).toContainText('Proceed?');

    // Capture screenshot of Confirm dialog
    await page.screenshot({ path: 'e2e/screenshots/interactive-confirm.png' });

    await dialog.getByRole('button', { name: 'Yes' }).click();

    await page.waitForTimeout(1000);

    // 7. Verify Input
    await expect(dialog).toBeVisible({ timeout: 10000 });
    await expect(dialog).toContainText('Name?');

    // Capture screenshot of Input dialog
    await page.screenshot({ path: 'e2e/screenshots/interactive-input.png' });

    const inputField = dialog.locator('input');
    await inputField.fill('Tester');
    await dialog.getByRole('button', { name: 'Submit' }).click();

    // Verify dialog is gone
    await expect(dialog).not.toBeVisible({ timeout: 10000 });

    // Final screenshot
    await page.screenshot({ path: 'e2e/screenshots/interactive-final.png' });
});
