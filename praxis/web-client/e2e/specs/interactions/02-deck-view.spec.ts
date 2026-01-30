import { test, expect } from '../../fixtures/worker-db.fixture';
import { WelcomePage } from '../../page-objects/welcome.page';
import { ProtocolPage } from '../../page-objects/protocol.page';
import { WizardPage } from '../../page-objects/wizard.page';
import { ExecutionMonitorPage } from '../../page-objects/monitor.page';

/**
 * Interaction tests for Deck View (hover, click, resource details).
 */
test.describe('Deck View Interaction', () => {
    test.beforeEach(async ({ page }) => {
        const welcomePage = new WelcomePage(page);
        await welcomePage.goto();
        await welcomePage.handleSplashScreen();
    });

    test('should show resource details when clicking labware in Live View', async ({ page }) => {
        const protocolPage = new ProtocolPage(page);
        const wizardPage = new WizardPage(page);
        const monitorPage = new ExecutionMonitorPage(page);

        // 1. Prepare and launch execution
        await protocolPage.goto();
        await protocolPage.ensureSimulationMode();
        await protocolPage.selectFirstProtocol();
        await protocolPage.continueFromSelection();
        
        await wizardPage.completeParameterStep();
        await wizardPage.selectFirstCompatibleMachine();
        await wizardPage.waitForAssetsAutoConfigured();
        await wizardPage.advanceDeckSetup();
        await wizardPage.openReviewStep();
        await wizardPage.startExecution();

        await monitorPage.waitForLiveDashboard();
        
        // 2. Click a resource in the deck view
        // We look for a .resource-node that is not the root deck
        const resourceNode = page.locator('.resource-node:not(.is-root)').first();
        await expect(resourceNode).toBeVisible({ timeout: 20000 });
        
        const resourceName = await resourceNode.getAttribute('title');
        await resourceNode.click();

        // 3. Verify Resource Inspector Panel updates
        const inspector = page.locator('app-resource-inspector-panel');
        await expect(inspector).toBeVisible();
        if (resourceName) {
            await expect(inspector).toContainText(resourceName);
        }
    });

    test('should show tooltip when hovering over resources', async ({ page }) => {
        const protocolPage = new ProtocolPage(page);
        const wizardPage = new WizardPage(page);
        const monitorPage = new ExecutionMonitorPage(page);

        // 1. Prepare and launch execution
        await protocolPage.goto();
        await protocolPage.ensureSimulationMode();
        await protocolPage.selectFirstProtocol();
        await protocolPage.continueFromSelection();
        
        await wizardPage.completeParameterStep();
        await wizardPage.selectFirstCompatibleMachine();
        await wizardPage.waitForAssetsAutoConfigured();
        await wizardPage.advanceDeckSetup();
        await wizardPage.openReviewStep();
        await wizardPage.startExecution();

        await monitorPage.waitForLiveDashboard();
        
        // 2. Hover over a resource
        const resourceNode = page.locator('.resource-node:not(.is-root)').first();
        await expect(resourceNode).toBeVisible({ timeout: 20000 });
        await resourceNode.hover();

        // 3. Verify tooltip visibility
        const tooltip = page.locator('.resource-tooltip');
        await expect(tooltip).toBeVisible({ timeout: 5000 });
        
        const resourceName = await resourceNode.getAttribute('title');
        if (resourceName) {
            await expect(tooltip.locator('.tooltip-header')).toContainText(resourceName);
        }
    });
});
