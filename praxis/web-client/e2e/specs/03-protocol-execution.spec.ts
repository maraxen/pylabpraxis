import { test } from '@playwright/test';
import { WelcomePage } from '../page-objects/welcome.page';
import { ProtocolPage } from '../page-objects/protocol.page';
import { ExecutionMonitorPage } from '../page-objects/monitor.page';

test.describe('Protocol Execution Flow', () => {
    test.beforeEach(async ({ page }) => {
        const welcomePage = new WelcomePage(page);
        await welcomePage.goto();
        await welcomePage.handleSplashScreen();
    });

    test('should run a protocol successfully', async ({ page }) => {
        const protocolPage = new ProtocolPage(page);
        const monitorPage = new ExecutionMonitorPage(page);

        // Select Protocol
        // We assume at least one protocol exists (e.g. from seed data or simulation)
        // If not, we might need to create one or mock it, but typically Browser Mode has seed protocols
        await protocolPage.goto();

        // Just pick the first one available
        await page.locator('app-protocol-card').first().waitFor();
        const protocolName = await page.locator('app-protocol-card').first().locator('mat-card-title').innerText();

        await protocolPage.selectProtocol(protocolName);

        // Wizard
        await protocolPage.navigateThroughWizard();

        // Start
        await protocolPage.startExecution();

        // Verify Monitor
        // Should eventually see "Running" or related status
        // Browser Mode execution is fast/simulated usually
        await monitorPage.verifySimulationMachine();

        // Allow some time for execution updates if needed
        await page.waitForTimeout(2000);
    });
});
