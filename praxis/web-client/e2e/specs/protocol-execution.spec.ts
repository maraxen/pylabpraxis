import { test, expect } from '@playwright/test';
import { ProtocolPage } from '../page-objects/protocol.page';

test.describe('Protocol Execution Flow', () => {
    let protocolPage: ProtocolPage;

    test.beforeEach(async ({ page }) => {
        protocolPage = new ProtocolPage(page);
    });

    test('should display protocol library', async ({ page }) => {
        await protocolPage.navigateToProtocols();
        await expect(protocolPage.protocolCards.first()).toBeVisible();
        // Verify at least one protocol is available
        expect(await protocolPage.protocolCards.count()).toBeGreaterThan(0);
    });

    test('should complete simulated execution', async ({ page }) => {
        test.setTimeout(120000); // Allow extra time for full flow

        await test.step('Navigate to Protocols', async () => {
            await protocolPage.navigateToProtocols();
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
        });

        await test.step('Start Execution', async () => {
            await protocolPage.startExecution();
            // Status might take a moment to appear
            const status = await protocolPage.getExecutionStatus();
            expect(status).toMatch(/Initializing|Running|Queued|Starting/i);
        });

        await test.step('Monitor Execution Progress', async () => {
            // Wait for running state if not already
            // The monitor page usually shows progress
            await expect(page.locator('mat-progress-bar')).toBeVisible({ timeout: 10000 });
        });

        await test.step('Complete Execution', async () => {
            await protocolPage.waitForCompletion();
            const finalStatus = await protocolPage.getExecutionStatus();
            expect(finalStatus).toMatch(/(Completed|Succeeded|Finished)/i);
        });
    });
});
