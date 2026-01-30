
import { test, expect, Page } from '../fixtures/worker-db.fixture';

test.describe('JupyterLite Bootstrap Verification', () => {
    test('JupyterLite Seamless Bootstrap Validation', async ({ page }) => {
        const consoleLogs: string[] = [];
        page.on('console', msg => consoleLogs.push(msg.text()));

        // 1. Navigate to origin to set localStorage BEFORE Angular loads
        await page.goto('/');
        await page.evaluate(() => {
            localStorage.setItem('praxis_onboarding_completed', 'true');
            localStorage.setItem('praxis_tutorial_completed', 'true');
        });

        // 2. Navigate to playground - Welcome dialog should be bypassed now
        await page.goto('/app/playground?mode=browser&resetdb=1');

        // 3. ASSERTION: Welcome Dialog should NOT be visible (bypassed via localStorage)
        const skipBtn = page.getByRole('button', { name: 'Skip for Now' });
        await expect(skipBtn).not.toBeVisible({ timeout: 3000 });
        console.log('[Test] Verified: Welcome dialog did NOT appear');

        const jupyterFrame = page.frameLocator('iframe.notebook-frame');

        // Wait for iframe to be attached first
        const frameElement = page.locator('iframe.notebook-frame');
        await expect(frameElement).toBeVisible({ timeout: 20000 });
        console.log('[Test] JupyterLite iframe attached');

        // 4. ASSERTION: Kernel Selection Dialog should NOT appear
        const jpKernelDialog = jupyterFrame.locator('.jp-Dialog').filter({ hasText: /kernel|select/i });
        await expect(jpKernelDialog).not.toBeVisible({ timeout: 5000 });
        console.log('[Test] Verified: Kernel dialog did NOT appear');

        // Wait for Angular loading overlay to disappear
        const loadingOverlay = page.locator('.loading-overlay');
        await expect(loadingOverlay).toBeHidden({ timeout: 60000 });
        console.log('[Test] Loading overlay cleared');

        // Dismiss any dialogs (theme errors, etc.)
        for (let i = 0; i < 3; i++) {
            try {
                const okButton = jupyterFrame.getByRole('button', { name: 'OK' });
                if (await okButton.isVisible({ timeout: 1000 })) {
                    await okButton.click();
                    console.log('[Test] Dismissed dialog (attempt ' + (i + 1) + ')');
                    await page.waitForTimeout(500);
                }
            } catch {
                // No dialog to dismiss
            }
        }

        // 5. VALIDATION: Check for Kernel Readiness
        try {
            await jupyterFrame.locator('.jp-mod-idle').first().waitFor({
                timeout: 45000,
                state: 'visible'
            });
            console.log('[Test] Kernel auto-started successfully');
        } catch (e) {
            console.log('[Test] Warning: Could not confirm kernel idle state');
            console.log('[Test] Last 10 console logs:', consoleLogs.slice(-10));
        }

        // 6. BOOTSTRAP VALIDATION: Verify Praxis-specific shims loaded
        await expect.poll(() => {
            const pyodideReady = consoleLogs.some(log => log.includes('[PythonRuntime] Pyodide ready'));
            const shimsInjected = consoleLogs.some(log => log.includes('WebSerial injected') || log.includes('WebUSB injected'));
            return pyodideReady && shimsInjected;
        }, {
            timeout: 60000,
            message: 'Pyodide ready or WebSerial/WebUSB shims never detected in console'
        }).toBe(true);

        console.log('[Test] Bootstrap complete with zero user intervention.');

        // 7. KERNEL EXECUTION VALIDATION: Execute print('hello world')
        const codeInput = jupyterFrame.locator('.jp-CodeConsole-input .jp-InputArea-editor');
        await expect(codeInput).toBeVisible({ timeout: 10000 });

        // Ensure any dialogs are closed before interacting
        try {
            const okButton = jupyterFrame.getByRole('button', { name: 'OK' });
            if (await okButton.isVisible({ timeout: 500 })) {
                await okButton.click();
            }
        } catch (e) {
            console.log('[Test] Silent catch (ignored - theme error):', e);
        }

        // Type and execute 'print("hello world")'
        await codeInput.click({ force: true });
        await page.keyboard.type('print("hello world")');
        await page.keyboard.press('Shift+Enter');

        // Wait for output containing 'hello world'
        await expect.poll(() => {
            return consoleLogs.some(log => log.includes('hello world'));
        }, {
            timeout: 15000,
            message: 'Expected "hello world" output from kernel'
        }).toBe(true);
        console.log('[Test] Kernel execution validated: print("hello world") succeeded');

        // 8. PYLABROBOT IMPORT VALIDATION
        // Dismiss any dialogs first
        try {
            const okButton = jupyterFrame.getByRole('button', { name: 'OK' });
            if (await okButton.isVisible({ timeout: 500 })) {
                await okButton.click();
            }
        } catch (e) {
            console.log('[Test] Silent catch (ignored - kernel select):', (e as Error).message);
        }

        await codeInput.click({ force: true });
        await page.keyboard.type('import pylabrobot; print(f"PLR v{pylabrobot.__version__}")');
        await page.keyboard.press('Shift+Enter');

        await expect.poll(() => {
            return consoleLogs.some(log => log.includes('PLR v'));
        }, {
            timeout: 15000,
            message: 'Expected pylabrobot version output'
        }).toBe(true);
        console.log('[Test] PyLabRobot import validated');

        // 9. CUSTOM INTERACTIONS VALIDATION (web_bridge)
        try {
            const okButton = jupyterFrame.getByRole('button', { name: 'OK' });
            if (await okButton.isVisible({ timeout: 500 })) {
                await okButton.click();
            }
        } catch (e) {
            console.log('[Test] Silent catch (ignored - welcome dialog):', (e as Error).message);
        }

        await codeInput.click({ force: true });
        await page.keyboard.type('import web_bridge; print("web_bridge:", hasattr(web_bridge, "request_user_interaction"))');
        await page.keyboard.press('Shift+Enter');

        await expect.poll(() => {
            return consoleLogs.some(log => log.includes('web_bridge: True'));
        }, {
            timeout: 15000,
            message: 'Expected web_bridge import to succeed with request_user_interaction'
        }).toBe(true);
        console.log('[Test] Custom interactions (web_bridge) validated');

        // Final assertions
        const pyodideReady = consoleLogs.some(log => log.includes('[PythonRuntime] Pyodide ready'));
        const shimsInjected = consoleLogs.some(log => log.includes('WebSerial injected') || log.includes('WebUSB injected'));
        console.log(`[Test] Pyodide Ready: ${pyodideReady}`);
        console.log(`[Test] Shims Injected: ${shimsInjected}`);

        expect(pyodideReady, 'Pyodide runtime did not signal ready state').toBe(true);
        expect(shimsInjected, 'WebSerial/WebUSB shims were not injected').toBe(true);
    });
});
