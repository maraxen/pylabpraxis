import { test, expect } from '../fixtures/worker-db.fixture';
import { WelcomePage } from '../page-objects/welcome.page';
import { ProtocolPage } from '../page-objects/protocol.page';
import { WizardPage } from '../page-objects/wizard.page';
import * as path from 'path';
import * as fs from 'fs';

const screenshotDir = path.join(process.cwd(), 'e2e/screenshots/medium-priority');

test.beforeAll(async () => {
    if (!fs.existsSync(screenshotDir)) {
        fs.mkdirSync(screenshotDir, { recursive: true });
    }
});

const APP_URL = 'http://localhost:4200';
const MODE_PARAMS = 'mode=browser&resetdb=0';

async function handleSplash(page) {
    const welcomePage = new WelcomePage(page);
    await welcomePage.handleSplashScreen();
}

test.describe('Medium Priority Screenshot Capture', () => {

    test('Capture Empty States', async ({ page }) => {
        test.setTimeout(120000);

        // Empty protocol library - use filter that returns no results
        await page.goto(`${APP_URL}/app/protocols?${MODE_PARAMS}`);
        await handleSplash(page);
        await page.waitForTimeout(2000);

        // Try to trigger empty state via search
        const searchInput = page.locator('input[placeholder*="Search"], input[type="search"]').first();
        if (await searchInput.isVisible()) {
            await searchInput.fill('xyznonexistent123');
            await page.waitForTimeout(1000);
        }
        await page.screenshot({ path: path.join(screenshotDir, 'empty-protocol-library.png') });
        console.log('Captured empty-protocol-library.png');

        // Empty assets - similar approach
        await page.goto(`${APP_URL}/app/assets?${MODE_PARAMS}`);
        await handleSplash(page);
        await page.waitForTimeout(2000);
        const assetSearch = page.locator('input[placeholder*="Search"], input[type="search"]').first();
        if (await assetSearch.isVisible()) {
            await assetSearch.fill('xyznonexistent123');
            await page.waitForTimeout(1000);
        }
        await page.screenshot({ path: path.join(screenshotDir, 'empty-assets.png') });
        console.log('Captured empty-assets.png');

        // Workcell page
        await page.goto(`${APP_URL}/app/workcell?${MODE_PARAMS}`);
        await handleSplash(page);
        await page.waitForTimeout(2000);
        await page.screenshot({ path: path.join(screenshotDir, 'workcell-dashboard.png') });
        console.log('Captured workcell-dashboard.png');
    });

    test('Capture Loading States', async ({ page }) => {
        test.setTimeout(60000);

        // Capture initial load of workcell (loading spinner)
        await page.goto(`${APP_URL}/app/workcell?${MODE_PARAMS}`);
        // Don't wait for splash - capture loading state
        await page.waitForTimeout(500);
        await page.screenshot({ path: path.join(screenshotDir, 'workcell-loading.png') });
        console.log('Captured workcell-loading.png');

        // Login page - Normal State
        await page.goto(`${APP_URL}/login?forceLogin=true`);
        await page.waitForTimeout(1000);
        await page.screenshot({ path: path.join(screenshotDir, 'login-page.png') });
        console.log('Captured login-page.png');

        // Login page - Error State
        await page.goto(`${APP_URL}/login?forceLogin=true&mockError=Invalid+Credentials`);
        await page.waitForTimeout(1000);
        await page.screenshot({ path: path.join(screenshotDir, 'login-error.png') });
        console.log('Captured login-error.png');

        // Login page - Loading State
        await page.goto(`${APP_URL}/login?forceLogin=true&mockLoading=true`);
        await page.waitForTimeout(1000);
        await page.screenshot({ path: path.join(screenshotDir, 'login-loading.png') });
        console.log('Captured login-loading.png');
    });

    test('Capture Charts and Visualizations', async ({ page }) => {
        test.setTimeout(180000);

        const protocolPage = new ProtocolPage(page);
        const wizardPage = new WizardPage(page);

        // 1. Navigates to /app/run (with browser mode params - reset DB to ensure protocols exist)
        await page.goto(`${APP_URL}/app/run?mode=browser&resetdb=true`);
        await handleSplash(page);
        console.log('Wizard Step: Selection started');

        // 2. Selects the first protocol
        await protocolPage.protocolCards.first().waitFor({ state: 'visible', timeout: 30000 });
        await protocolPage.ensureSimulationMode();
        await protocolPage.selectFirstProtocol();
        await protocolPage.continueFromSelection();
        await page.waitForTimeout(1000);
        console.log('Wizard Step: Selection complete');

        // 3. Clicks through the wizard steps ("Next" / "Continue") until "Start Execution"
        await wizardPage.completeParameterStep();
        await page.waitForTimeout(1000);
        console.log('Wizard Step: Parameters complete');

        await wizardPage.selectFirstCompatibleMachine();
        await page.waitForTimeout(1000);
        console.log('Wizard Step: Machine selection complete');

        await wizardPage.waitForAssetsAutoConfigured();
        await page.waitForTimeout(1000);
        console.log('Wizard Step: Assets complete');

        await wizardPage.advanceDeckSetup();
        await page.waitForTimeout(1000);
        console.log('Wizard Step: Deck setup complete');

        await wizardPage.openReviewStep();
        await page.waitForTimeout(1000);
        console.log('Wizard Step: Review complete');

        // 4. Clicks "Start Execution" and 5. Waits for the redirect to the live dashboard
        await wizardPage.waitForStartReady();
        await wizardPage.startExecution();
        console.log('Execution started, waiting for dashboard');

        // 6. Waits for app-telemetry-chart to be visible and have data (wait 3s)
        const telemetryChart = page.locator('app-telemetry-chart, .telemetry-chart').first();
        await expect(telemetryChart).toBeVisible({ timeout: 30000 });

        // Wait for data to populate/animations to settle
        await page.waitForTimeout(3000);

        // 7. Captures the screenshot telemetry-chart.png
        await telemetryChart.screenshot({ path: path.join(screenshotDir, 'telemetry-chart.png') });
        console.log('Captured telemetry-chart.png');

        // Optional: Look for plate heatmap
        const plateHeatmap = page.locator('app-plate-heatmap, .plate-heatmap').first();
        if (await plateHeatmap.isVisible({ timeout: 5000 }).catch((e) => {
            console.log('[Test] Silent catch (plateHeatmap isVisible):', e);
            return false;
        })) {
            await plateHeatmap.screenshot({ path: path.join(screenshotDir, 'plate-heatmap.png') });
            console.log('Captured plate-heatmap.png');
        }

        // Full workcell view
        await page.screenshot({ path: path.join(screenshotDir, 'workcell-full.png') });
        console.log('Captured workcell-full.png');
    });
});
