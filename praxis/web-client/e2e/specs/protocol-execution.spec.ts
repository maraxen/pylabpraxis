import { test, expect } from '@playwright/test';
import { ProtocolPage } from '../page-objects/protocol.page';

test.describe('Protocol Wizard Flow', () => {
    let protocolPage: ProtocolPage;

    test.beforeEach(async ({ page }) => {
        protocolPage = new ProtocolPage(page);

        // Ensure clean state starting from root
        await page.goto('/');

        // Wait for SQLite DB to be ready
        await page.waitForFunction(
            () => (window as any).sqliteService?.isReady$?.getValue() === true,
            null,
            { timeout: 30000 }
        );

        // In browser mode, we expect a redirect to /app/home
        await page.waitForURL('**/app/home', { timeout: 15000 }).catch(() => {
            console.log('Did not redirect to /app/home automatically');
        });

        // Ensure shell layout is visible
        await expect(page.locator('.sidebar-rail')).toBeVisible({ timeout: 10000 });

        // Handle Welcome Dialog if present (Browser Mode)
        const welcomeDialog = page.getByRole('dialog', { name: /Welcome to Praxis/i });
        if (await welcomeDialog.isVisible({ timeout: 5000 })) {
            console.log('Dismissing Welcome Dialog...');
            await page.getByRole('button', { name: /Skip for Now/i }).click();
            await expect(welcomeDialog).not.toBeVisible();
        }
    });

    test.afterEach(async ({ page }) => {
        // Dismiss any open dialogs/overlays to ensure clean state
        await page.keyboard.press('Escape').catch(() => { });
    });

    test('should display protocol library', async ({ page }) => {
        await protocolPage.navigateToProtocols();
        await expect(protocolPage.protocolCards.first()).toBeVisible();
        await page.screenshot({ path: '/tmp/e2e-protocol/01-protocol-library.png' });
        // Verify at least one protocol is available
        expect(await protocolPage.protocolCards.count()).toBeGreaterThan(0);
    });

    test('should complete simulated execution', async ({ page }) => {
        test.setTimeout(120000); // Allow extra time for full flow

        await test.step('Navigate to Protocols', async () => {
            await protocolPage.navigateToProtocols();
            await page.screenshot({ path: '/tmp/e2e-protocol/02-navigate-protocols.png' });
        });

        await test.step('Select and Configure Protocol', async () => {
            // Find a protocol, preferably "Simple Transfer" or just the first one
            const protocolName = 'Simple Transfer';
            const hasProtocol = await page.getByText(protocolName).isVisible().catch(() => false);

            if (hasProtocol) {
                await protocolPage.selectProtocol(protocolName);
            } else {
                console.log(`Protocol ${protocolName} not found, selecting first available.`);
                await protocolPage.selectFirstProtocol();
                await protocolPage.continueFromSelection();
            }

            // Configure Minimal Parameters (if any are required/visible)
            // For Simple Transfer, defaults might be fine.
            // We'll advance through the wizard using the helper we added
            await protocolPage.advanceToReview();
            await page.screenshot({ path: '/tmp/e2e-protocol/03-review-step.png' });
        });

        await test.step('Start Execution', async () => {
            await protocolPage.startExecution();
            // Status might take a moment to appear
            const status = await protocolPage.getExecutionStatus();
            expect(status).toMatch(/Initializing|Running|Queued|Starting/i);
            await page.screenshot({ path: '/tmp/e2e-protocol/04-execution-started.png' });
        });

        await test.step('Monitor Execution Progress', async () => {
            // Wait for running state if not already
            // The monitor page usually shows progress
            await expect(page.locator('mat-progress-bar')).toBeVisible({ timeout: 10000 });
            await page.screenshot({ path: '/tmp/e2e-protocol/05-execution-progress.png' });
        });

        await test.step('Complete Execution', async () => {
            await protocolPage.waitForCompletion();
            const finalStatus = await protocolPage.getExecutionStatus();
            expect(finalStatus).toMatch(/(Completed|Succeeded|Finished)/i);
            await page.screenshot({ path: '/tmp/e2e-protocol/06-execution-completed.png' });
        });
    });
});
