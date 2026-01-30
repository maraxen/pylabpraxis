
import { test, expect } from '../fixtures/worker-db.fixture';

test.describe('JupyterLite Optimization Validation', () => {
    test('Security Headers: Should have COOP and COEP enabled', async ({ request }) => {
        const response = await request.get('/');
        const headers = response.headers();

        console.log('[Header Test] Headers found:', JSON.stringify(headers, null, 2));

        expect(headers['cross-origin-opener-policy'], 'COOP header missing or incorrect').toBe('same-origin');
        expect(headers['cross-origin-embedder-policy'], 'COEP header missing or incorrect').toBe('require-corp');
    });

    test('Phase 1: PyLabRobot should be pre-loaded (No manual install log)', async ({ page }) => {
        const consoleLogs: string[] = [];
        page.on('console', msg => {
            const text = msg.text();
            consoleLogs.push(text);
            if (text.includes('Installing pylabrobot') || text.includes('✓ Ready')) {
                console.log(`[REPL Log] ${text}`);
            }
        });

        // Skip onboarding/tutorial
        await page.goto('/');
        await page.evaluate(() => {
            localStorage.setItem('praxis_onboarding_completed', 'true');
            localStorage.setItem('praxis_tutorial_completed', 'true');
        });

        await page.goto('/app/playground?mode=browser');

        // Wait for ready signal
        await expect(page.locator('.loading-overlay')).toBeHidden({ timeout: 60000 });

        // WAIT for the custom "✓ Ready signal sent" from our bootstrap
        await expect.poll(() => {
            return consoleLogs.some(log => log.includes('✓ Ready signal sent'));
        }, { timeout: 30000, message: 'Kernel ready signal not found' }).toBe(true);

        // ASSERTION: Pylabrobot should be importable
        const jupyterFrame = page.frameLocator('iframe.notebook-frame');
        const codeInput = jupyterFrame.locator('.jp-CodeConsole-input .jp-InputArea-editor').first();
        await expect(codeInput).toBeVisible({ timeout: 10000 });

        await codeInput.click();
        await page.keyboard.type('import pylabrobot; print(f"PLR_FOUND_{pylabrobot.__version__}")');
        await page.keyboard.press('Shift+Enter');

        await expect.poll(() => {
            return consoleLogs.some(log => log.includes('PLR_FOUND_'));
        }, { timeout: 15000, message: 'PyLabRobot check failed' }).toBe(true);

        // CRITICAL ASSERTION (Fail Condition for RED phase):
        // We should NOT see "Installing pylabrobot from local wheel..." in the logs
        // because it should have been pre-installed via the lockfile/system library.
        const manualInstallLog = consoleLogs.find(log => log.includes('Installing pylabrobot from local wheel...'));
        expect(manualInstallLog, 'Manual installation of pylabrobot detected! It should be pre-loaded via lockfile.').toBeUndefined();
    });

    test('Phase 2: Assets should be cached via Service Worker', async ({ page }) => {
        // Note: This might require the application to be built with Service Worker enabled.
        // If running in dev mode, Service Worker might not be active by default.

        await page.goto('/app/playground?mode=browser');
        await page.waitForTimeout(5000); // Give SW time to register/cache

        // Second load - monitor responses
        const [response] = await Promise.all([
            page.waitForResponse(resp => resp.url().includes('pyodide-lock.json')),
            page.reload({ waitUntil: 'networkidle' })
        ]);

        console.log(`[Phase 2 Test] Request: ${response.url()}`);
        console.log(`[Phase 2 Test] From SW: ${response.fromServiceWorker()}`);

        expect(response.fromServiceWorker(), 'pyodide-lock.json should be served from Service Worker').toBe(true);
    });
});
