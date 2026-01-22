import { expect, test, Page } from '@playwright/test';
import { WelcomePage } from '../page-objects/welcome.page';
import { ProtocolPage } from '../page-objects/protocol.page';
import { ExecutionMonitorPage } from '../page-objects/monitor.page';
import { WizardPage } from '../page-objects/wizard.page';

test.describe.serial('Protocol Execution E2E', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');
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

    test('select protocol from library', async ({ page }) => {
        const protocolPage = new ProtocolPage(page);
        await protocolPage.goto();
        await protocolPage.ensureSimulationMode();
        const protocolName = await protocolPage.selectFirstProtocol();
        await protocolPage.continueFromSelection();
        await expect(page.locator('[data-tour-id="run-step-params"]')).toBeVisible();
        await page.screenshot({ path: '/tmp/e2e-protocol/03-spec-01-selection.png' });
    });

    test('complete setup wizard steps', async ({ page }) => {
        const { protocolName } = await prepareExecution(page);
        await expect(page.getByRole('tab', { name: /Review & Run/i })).toHaveAttribute('aria-selected', 'true');
        await expect(page.locator('button', { hasText: 'Start Execution' })).toBeVisible();
        await expect(page.locator('h2', { hasText: 'Ready to Launch' })).toBeVisible();
        await expect(page.locator('[data-testid="review-protocol-name"]')).toHaveText(protocolName);
        await page.screenshot({ path: '/tmp/e2e-protocol/03-spec-02-wizard-complete.png' });
    });

    test('start execution', async ({ page }) => {
        const { monitor, protocolName, runName } = await launchExecution(page);
        await monitor.waitForStatus(/RUNNING|COMPLETED/);
        expect(runName).toContain(protocolName);
        const meta = await monitor.captureRunMeta();
        expect(meta.runName).toBe(runName);
        await page.screenshot({ path: '/tmp/e2e-protocol/03-spec-03-started.png' });
    });

    test('monitor execution status updates', async ({ page }) => {
        const { monitor } = await launchExecution(page);
        await monitor.waitForStatus(/RUNNING/);
        await monitor.waitForProgressAtLeast(25);
        await monitor.waitForLogEntry('[Browser] Executing protocol');
        await monitor.waitForStatus(/COMPLETED/);
        await monitor.waitForLogEntry('Execution completed successfully');
        await page.screenshot({ path: '/tmp/e2e-protocol/03-spec-04-completed.png' });
    });

    test('view completed execution details', async ({ page }) => {
        const { monitor, runName, runId } = await launchExecution(page);
        await monitor.waitForStatus(/COMPLETED/);
        await monitor.navigateToHistory();
        await monitor.waitForHistoryRow(runName);
        await monitor.reloadHistory();
        await monitor.waitForHistoryRow(runName);
        await monitor.openRunDetailById(runId);
        await monitor.expectRunDetailVisible(runName);
        await page.screenshot({ path: '/tmp/e2e-protocol/03-spec-05-details.png' });
    });
});

async function prepareExecution(page: Page) {
    const protocolPage = new ProtocolPage(page);
    const wizardPage = new WizardPage(page);
    await protocolPage.goto();
    await protocolPage.ensureSimulationMode();
    const protocolName = await protocolPage.selectFirstProtocol();
    await protocolPage.continueFromSelection();
    await wizardPage.completeParameterStep();
    await wizardPage.selectFirstCompatibleMachine();
    await wizardPage.waitForAssetsAutoConfigured();
    await wizardPage.advanceDeckSetup();
    await wizardPage.openReviewStep();
    await wizardPage.assertReviewSummary(protocolName);
    return { protocolName, wizardPage };
}

async function launchExecution(page: Page) {
    const { protocolName, wizardPage } = await prepareExecution(page);
    await wizardPage.startExecution();
    const monitor = new ExecutionMonitorPage(page);
    await monitor.waitForLiveDashboard();
    const meta = await monitor.captureRunMeta();
    return { monitor, protocolName, runName: meta.runName, runId: meta.runId };
}
