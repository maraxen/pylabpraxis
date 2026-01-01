import { test, expect } from '@playwright/test';

test.describe('REPL Enhancements', () => {
    test.beforeEach(async ({ page }) => {
        // Navigate to the REPL page
        await page.goto('/app/repl');

        // Wait for the REPL component to load
        await page.waitForSelector('app-repl', { timeout: 30000 });

        // Wait for the terminal to be visible
        await page.waitForSelector('.xterm-rows', { timeout: 30000 });

        // Wait for Pyodide to initialize (look for "Runtime connected" message or prompt)
        // We use a regex to be flexible about whitespace/splitting
        await expect(page.locator('.xterm-rows')).toContainText('>>>', { timeout: 60000 });

        // Click the terminal to focus
        await page.click('.xterm-screen');
    });

    test('Split Streams Styling', async ({ page }) => {
        const terminalRows = page.locator('.xterm-rows');

        // Helper to type into xterm reliably
        const typeInTerminal = async (text: string) => {
            // Target the hidden textarea that xterm uses for capturing input
            const textarea = page.locator('.xterm-helper-textarea');
            await textarea.focus();
            await page.keyboard.type(text);
            await page.keyboard.press('Enter');
        };

        // Helper to get full terminal text
        const getTerminalText = async () => {
            return await terminalRows.evaluate((el: HTMLElement) => el.innerText);
        };

        // Execute code that produces stdout
        await typeInTerminal('print("Hello Stdout")');

        // Wait for the output and prompt
        await expect(async () => {
            const text = await getTerminalText();
            // Check for output and the reappearance of prompt
            expect(text).toContain('Hello Stdout');
            // We need to count prompts or just ensure it appears after our command
            expect(text).toMatch(/Hello Stdout.*>>>/s);
        }).toPass({ timeout: 10000 });

        // Execute code that produces stderr
        await typeInTerminal('import sys; sys.stderr.write("Hello Stderr\\n")');

        // Wait for output
        await expect(async () => {
            const text = await getTerminalText();
            expect(text).toContain('Hello Stderr');
            expect(text).toMatch(/Hello Stderr.*>>>/s);
        }).toPass({ timeout: 10000 });
    });

    test('Completion Popup', async ({ page }) => {
        const textarea = page.locator('.xterm-helper-textarea');
        await textarea.focus();

        // Type a common module to trigger completion
        await page.keyboard.type('import os');
        await page.keyboard.press('Enter');

        // Wait for prompt
        await expect(page.locator('.xterm-rows')).toContainText('>>>', { timeout: 10000 });

        // Type 'os.' and trigger completion
        await page.keyboard.type('os.');
        await page.keyboard.press('Tab');

        // Expect completion popup to appear
        const popup = page.locator('app-completion-popup');
        await expect(popup).toBeVisible({ timeout: 15000 });

        // Check for items
        const items = popup.locator('.completion-item');
        await expect(items.first()).toBeVisible();

        // Test navigation
        await page.keyboard.press('ArrowDown');
        await expect(items.nth(1)).toHaveClass(/selected/);

        // Select an item
        await page.keyboard.press('Enter');
        await expect(popup).toBeHidden();
    });

    test('Signature Help', async ({ page }) => {
        const textarea = page.locator('.xterm-helper-textarea');
        await textarea.focus();

        // Type a function call
        await page.keyboard.type('print(');

        // Expect signature help to appear
        const sigPopup = page.locator('app-signature-help');
        await expect(sigPopup).toBeVisible({ timeout: 15000 });

        // Check content (flexible match)
        await expect(sigPopup).toContainText(/print/);

        // Close via Escape
        await page.keyboard.press('Escape');
        await expect(sigPopup).toBeHidden();
    });
});
