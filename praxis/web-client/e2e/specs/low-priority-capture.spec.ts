import { test, expect } from '../fixtures/worker-db.fixture';
import { WelcomePage } from '../page-objects/welcome.page';
import * as path from 'path';
import * as fs from 'fs';

const screenshotDir = path.join(process.cwd(), 'e2e/screenshots/low-priority');

test.beforeAll(async () => {
    if (!fs.existsSync(screenshotDir)) {
        fs.mkdirSync(screenshotDir, { recursive: true });
    }
});

const APP_URL = 'http://localhost:4200';
const MODE_PARAMS = 'mode=browser';

async function handleSplash(page) {
    const welcomePage = new WelcomePage(page);
    await welcomePage.handleSplashScreen();
}

test.describe('Low Priority Screenshot Capture', () => {
    test.setTimeout(60000);

    test('Settings Page and Snackbar', async ({ page }) => {
        // 1. Navigate to Settings Page
        await page.goto(`${APP_URL}/app/settings?${MODE_PARAMS}`);
        await handleSplash(page);
        await page.waitForTimeout(2000);
        
        // Capture screenshot: settings-page.png
        await page.screenshot({ path: path.join(screenshotDir, 'settings-page.png') });
        console.log('Captured settings-page.png');

        // 2. Snackbars
        // Find the "Export Database" button (icon: download)
        const exportButton = page.getByRole('button', { name: 'Export Database' });
        await expect(exportButton).toBeVisible({ timeout: 10000 });
        await exportButton.click();

        // Wait for the snackbar to appear (any snackbar)
        const snackbar = page.locator('.mat-mdc-snack-bar-container, .mdc-snackbar__surface').first();
        await expect(snackbar).toBeVisible({ timeout: 10000 });
        
        // Capture screenshot: snackbar-toast.png
        await page.screenshot({ path: path.join(screenshotDir, 'snackbar-toast.png') });
        console.log('Captured snackbar-toast.png');
    });
});
