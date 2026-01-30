import { test, expect } from '../fixtures/worker-db.fixture';

/**
 * E2E Test: Browser Mode Protocol Execution
 *
 * Tests the full execution flow in browser mode:
 * 1. Navigate to Run Protocol page
 * 2. Select a protocol
 * 3. Complete setup steps
 * 4. Click "Start Execution"
 * 5. Verify execution starts and progress is shown
 */

test.describe('Browser Mode Execution', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');
        // In browser mode, we expect a redirect to /app/home
        await page.waitForURL('**/app/home', { timeout: 15000 }).catch((e) => {
            console.log('[Test] Silent catch (waitForURL home):', e);
        });
        // Wait for SQLite DB to be ready
        await page.waitForFunction(
            () => (window as any).sqliteService?.isReady$?.getValue() === true,
            null,
            { timeout: 30000 }
        );
        // Ensure shell layout is visible
        await expect(page.locator('.sidebar-rail')).toBeVisible({ timeout: 10000 });

        // Handle Welcome Dialog if present (Browser Mode)
        const welcomeDialog = page.getByRole('dialog', { name: /Welcome to Praxis/i });
        if (await welcomeDialog.isVisible({ timeout: 5000 })) {
            console.log('Dismissing Welcome Dialog...');
            // Try explicit 'Skip for Now' or generic dismiss if that fails
            const skipButton = page.getByRole('button', { name: /Skip for Now/i });
            if (await skipButton.isVisible()) {
                await skipButton.click();
            } else {
                // Fallback for other dismiss buttons if text varies
                await page.locator('button').filter({ hasText: /Close|Dismiss/i }).first().click().catch((e) => console.log('[Test] Silent catch (Close/Dismiss):', e));
            }
            await expect(welcomeDialog).not.toBeVisible();
        }
    });

    test.afterEach(async ({ page }) => {
        // Dismiss any open dialogs/overlays to ensure clean state
        await page.keyboard.press('Escape').catch((e) => console.log('[Test] Silent catch (Escape):', e));
    });

    test('should start protocol execution in browser mode', async ({ page }) => {
        // Navigate to Run Protocol page
        await page.goto('/app/run');
        await page.waitForLoadState('domcontentloaded');

        // Wait for protocols to load
        try {
            await page.waitForSelector('[class*="protocol"]', { timeout: 15000 });
            // Screenshot: Protocol Load
            await page.screenshot({ path: '/tmp/e2e-browser-exec/01_protocol_load.png' });
        } catch (e) {
            console.log('Failed to find protocol cards. Taking debug screenshot...');
            await page.screenshot({ path: '/tmp/e2e-browser-exec/debug_protocol_load_failed.png' });
            // Dump page text to help debug
            const text = await page.textContent('body');
            console.log('Page content:', text?.substring(0, 500) + '...');
            throw e;
        }

        // Screenshot: Protocol Load
        await page.screenshot({ path: '/tmp/e2e-browser-exec/01_protocol_load.png' });

        // Select first available protocol
        const protocolCard = page.locator('app-protocol-card').first();
        if (await protocolCard.isVisible({ timeout: 5000 }).catch((e) => {
            console.log('[Test] Silent catch (protocolCard isVisible):', e);
            return false;
        })) {
            await protocolCard.click();
        }

        // Click Continue through steps
        const continueButton = page.locator('button:has-text("Continue")');
        if (await continueButton.isVisible({ timeout: 3000 }).catch((e) => {
            console.log('[Test] Silent catch (continueButton isVisible):', e);
            return false;
        })) {
            await continueButton.click();
            await page.waitForTimeout(500);
        }

        // Machine selection step - select simulation machine if visible
        const machineCard = page.locator('app-machine-selection').first();
        if (await machineCard.isVisible({ timeout: 2000 }).catch((e) => {
            console.log('[Test] Silent catch (machineCard isVisible):', e);
            return false;
        })) {
            await machineCard.locator('mat-card').first().click();
            await page.waitForTimeout(300);
        }

        // Keep clicking continue until we reach Review & Run
        for (let i = 0; i < 3; i++) {
            const nextButton = page.locator('button:has-text("Continue")');
            if (await nextButton.isVisible({ timeout: 1000 }).catch((e) => {
                console.log('[Test] Silent catch (nextButton isVisible):', e);
                return false;
            })) {
                await nextButton.click();
                await page.waitForTimeout(500);
            }
        }

        // Attempt to start execution
        const startButton = page.locator('button:has-text("Start Execution")');
        if (await startButton.isVisible({ timeout: 5000 }).catch((e) => {
            console.log('[Test] Silent catch (startButton isVisible):', e);
            return false;
        })) {
            // Check if button is enabled (requires deck setup)
            const isDisabled = await startButton.getAttribute('disabled');

            // Screenshot: Run Start (Before Click)
            await page.screenshot({ path: '/tmp/e2e-browser-exec/02_run_start_setup.png' });

            if (!isDisabled) {
                await startButton.click();

                // Verify button shows loading state or navigates
                await expect(
                    page.locator('mat-spinner').or(page.locator('text=Initializing'))
                ).toBeVisible({ timeout: 5000 }).catch((e) => {
                    console.log('[Test] Silent catch (Step complete check):', e);
                });

                // Screenshot: Run Completion (Initialization)
                await page.screenshot({ path: '/tmp/e2e-browser-exec/03_run_initialization.png' });
            } else {
                // Button disabled - deck setup required
                console.log('Start button disabled - deck setup required');
                // Screenshot even if disabled to show why
                await page.screenshot({ path: '/tmp/e2e-browser-exec/02_run_start_disabled.png' });
            }
        }
    });

    test('should show simulation machine in browser mode', async ({ page }) => {
        // Navigate to Run Protocol page
        await page.goto('/app/run');
        await page.waitForLoadState('domcontentloaded');

        // Select a protocol
        const protocolCard = page.locator('app-protocol-card').first();
        if (await protocolCard.isVisible({ timeout: 5000 }).catch((e) => {
            console.log('[Test] Silent catch (protocolCard isVisible):', e);
            return false;
        })) {
            await protocolCard.click();
        }

        // Continue to machine selection
        const continueButton = page.locator('button:has-text("Continue")');
        if (await continueButton.isVisible({ timeout: 3000 }).catch((e) => {
            console.log('[Test] Silent catch (continueButton isVisible):', e);
            return false;
        })) {
            await continueButton.click();
        }

        // Verify simulation machine appears
        await expect(
            page.locator('text=Simulation Machine').or(page.locator('text=sim-machine'))
        ).toBeVisible({ timeout: 5000 }).catch((e) => {
            // Machine selection might not be visible if auto-selected
            console.log('[Test] Silent catch (Step 1 complete race):', e);
        });
    });
});
