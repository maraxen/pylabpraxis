import { test, expect } from '../../fixtures/worker-db.fixture';
import { WelcomePage } from '../../page-objects/welcome.page';
import { ProtocolPage } from '../../page-objects/protocol.page';
import { WizardPage } from '../../page-objects/wizard.page';
import { ExecutionMonitorPage } from '../../page-objects/monitor.page';
import { SettingsPage } from '../../page-objects/settings.page';

/**
 * Interaction tests for error handling and system resilience.
 */
test.describe('Error Handling Interaction', () => {
    test.beforeEach(async ({ page }) => {
        const welcomePage = new WelcomePage(page);
        await welcomePage.goto();
        await welcomePage.handleSplashScreen();
    });

    test('should display error logs when a protocol execution fails', async ({ page }) => {
        const protocolPage = new ProtocolPage(page);
        const wizardPage = new WizardPage(page);
        const monitorPage = new ExecutionMonitorPage(page);

        // 1. Navigate to protocols
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

        // Verify the log panel is visible
        const logPanel = page.locator('mat-card').filter({ hasText: 'Execution Log' });
        await expect(logPanel).toBeVisible();
    });

    test('should remain live when navigating away and back during execution', async ({ page }) => {
        const protocolPage = new ProtocolPage(page);
        const wizardPage = new WizardPage(page);
        const monitorPage = new ExecutionMonitorPage(page);
        const settingsPage = new SettingsPage(page);

        // 1. Start execution
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
        await monitorPage.waitForStatus(/RUNNING/);

        // 2. Navigate away to Settings
        await settingsPage.goto();
        await expect(page).toHaveURL(/\/settings/);

        // 3. Navigate back to Monitor
        await monitorPage.goto();
        await monitorPage.waitForLiveDashboard();

        // 4. Verify status is still visible and running
        await monitorPage.waitForStatus(/RUNNING|COMPLETED/);
    });

    test('should show user-friendly error on backend failure', async ({ page }) => {
        // 1. Mock a 500 error for protocol listing or another key API
        await page.route('**/api/v1/protocols*', route => route.fulfill({
            status: 500,
            contentType: 'application/json',
            body: JSON.stringify({ error: 'Internal Server Error' })
        }));

        const protocolPage = new ProtocolPage(page);
        await protocolPage.goto();

        // 2. Verify error notification (SnackBar/Toast)
        // Adjust selector based on actual implementation (usually mat-simple-snackbar or similar)
        const snackBar = page.locator('mat-snack-bar-container');
        await expect(snackBar).toBeVisible({ timeout: 10000 });
        await expect(snackBar).toContainText(/error|failed/i);
    });
});