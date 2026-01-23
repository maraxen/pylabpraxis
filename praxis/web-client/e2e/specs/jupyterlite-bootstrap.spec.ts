
import { test, expect } from '@playwright/test';

test.describe('JupyterLite Bootstrap Verification', () => {
    test('Bootstrap code executes successfully and loads shims', async ({ page }) => {
        const consoleLogs: string[] = [];
        const failedRequests: string[] = [];
        const successfulRequests: string[] = [];

        // Capture console logs
        page.on('console', msg => {
            const text = msg.text();
            consoleLogs.push(text);
            // Print critical python errors to test output
            if (text.includes('Error') || text.includes('Exception') || text.includes('Failed')) {
                console.log(`[Browser Console Error] ${text}`);
            }
        });

        // Monitor network
        page.on('response', response => {
            const url = response.url();
            if (response.status() === 404) {
                failedRequests.push(url);
            } else if (response.status() === 200) {
                successfulRequests.push(url);
            }
        });

        // Go to playground (Browser Mode)
        await page.goto('/app/playground?mode=browser&resetdb=1');

        // Wait for JupyterLite frame
        const frameElement = page.locator('iframe.notebook-frame');
        await expect(frameElement).toBeVisible({ timeout: 20000 });

        // Wait for "Ready signal sent" logs or similar indicating success
        // Based on playground.component.ts logs: "✓ Ready signal sent"
        // But these are printed in Python. Where do they go?
        // Usually Pyodide stdout goes to console.log.

        // Wait up to 30s for bootstrap
        try {
            await expect.poll(async () => {
                return consoleLogs.some(log => log.includes('Ready signal sent') || log.includes('✓ Asset injection ready'));
            }, { timeout: 45000, intervals: [1000] }).toBe(true);
        } catch (e) {
            console.log('Timed out waiting for ready signal.');
        }

        // Diagnostic checks

        // 1. Check if shims were loaded
        const shimsLoaded = consoleLogs.some(log => log.includes('PylibPraxis: Loaded web_serial_shim.py'));
        console.log(`Shims Loaded: ${shimsLoaded}`);

        // 2. Check if wheels were installed
        const wheelsInstalled = consoleLogs.some(log => log.includes('Installing pylabrobot from local wheel'));
        console.log(`Wheels Installation Started: ${wheelsInstalled}`);

        // 3. Check for specific Python syntax errors
        const syntaxErrors = consoleLogs.filter(log => log.includes('SyntaxError'));
        if (syntaxErrors.length > 0) {
            console.error('Syntax Errors detected:', syntaxErrors);
        }

        // 4. Verify request statuses for critical assets
        const whlRequest = successfulRequests.find(u => u.includes('.whl'));
        const shimRequest = successfulRequests.find(u => u.includes('web_serial_shim.py'));

        console.log(`Wheel Request Found: ${!!whlRequest}`);
        console.log(`Shim Request Found: ${!!shimRequest}`);

        // Fail if we see "Failed to load" from our bootstrap print statements
        const bootstrapFailures = consoleLogs.filter(log => log.includes('PylibPraxis: Failed to load'));
        expect(bootstrapFailures, `Bootstrap failed to load components: ${bootstrapFailures.join('\n')}`).toHaveLength(0);

        // Fail if no ready signal
        const ready = consoleLogs.some(log => log.includes('Ready signal sent'));
        expect(ready, 'Kernel did not signal ready state').toBe(true);
    });
});
