import { test, expect } from '@playwright/test';
import { WelcomePage } from '../../page-objects/welcome.page';
import { ProtocolPage } from '../../page-objects/protocol.page';
import { WizardPage } from '../../page-objects/wizard.page';
import { ExecutionMonitorPage } from '../../page-objects/monitor.page';

/**
 * Interaction tests for execution controls (Pause, Resume, Abort).
 */
test.describe('Execution Controls Interaction', () => {
    test.beforeEach(async ({ page }) => {
        const welcomePage = new WelcomePage(page);
        await welcomePage.goto();
        await welcomePage.handleSplashScreen();
    });

    test('should pause and resume a simulated run', async ({ page }) => {
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
        
        // 2. Click Pause
        const pauseBtn = page.getByRole('button', { name: /pause/i }).first();
        await expect(pauseBtn).toBeVisible({ timeout: 15000 });
        await pauseBtn.click();

        // 3. Verify status changes to PAUSED
        await monitorPage.waitForStatus(/PAUSED/);
        
        // 4. Click Resume
        const resumeBtn = page.getByRole('button', { name: /resume/i }).first();
        await expect(resumeBtn).toBeVisible({ timeout: 15000 });
        await resumeBtn.click();

        // 5. Verify status returns to RUNNING or progresses to COMPLETED
        await monitorPage.waitForStatus(/RUNNING|COMPLETED/);
    });

    test('should abort a simulated run', async ({ page }) => {
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
        
        // 2. Click Abort/Stop
        const abortBtn = page.getByRole('button', { name: /stop|abort|cancel/i }).filter({ hasText: /Stop|Abort|Cancel/i }).first();
        await expect(abortBtn).toBeVisible({ timeout: 15000 });
        await abortBtn.click();

        // 3. Handle confirmation if any
        const confirmBtn = page.getByRole('button', { name: /confirm|yes|abort/i }).first();
        if (await confirmBtn.isVisible({ timeout: 2000 })) {
            await confirmBtn.click();
        }

        // 4. Verify status changes to CANCELLED/FAILED
        await monitorPage.waitForStatus(/CANCELLED|FAILED/);
    });
});
