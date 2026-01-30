import { test, expect } from '../fixtures/worker-db.fixture';
import { WelcomePage } from '../page-objects/welcome.page';
import * as path from 'path';
import * as fs from 'fs';

const screenshotDir = path.join(process.cwd(), 'e2e/screenshots/viz-review');

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

test.describe('Visual Review Screenshot Capture', () => {

    test('Capture Page Screenshots', async ({ page }) => {
        test.setTimeout(120000);
        await page.goto(`${APP_URL}/app/home?${MODE_PARAMS}`);
        await handleSplash(page);
        await page.waitForTimeout(5000);

        // 4. asset-library.png
        await page.goto(`${APP_URL}/app/assets?${MODE_PARAMS}`);
        await handleSplash(page);
        await page.waitForTimeout(2000);
        await page.screenshot({ path: path.join(screenshotDir, 'asset-library.png') });
        console.log('Captured asset-library.png');

        // 5. protocol-library.png
        await page.goto(`${APP_URL}/app/protocols?${MODE_PARAMS}`);
        await handleSplash(page);
        await page.waitForTimeout(2000);
        await page.screenshot({ path: path.join(screenshotDir, 'protocol-library.png') });
        console.log('Captured protocol-library.png');

        // 9. run-protocol-config.png
        await page.goto(`${APP_URL}/app/run?${MODE_PARAMS}`);
        await handleSplash(page);
        await page.waitForTimeout(2000);
        await page.screenshot({ path: path.join(screenshotDir, 'run-protocol-config.png') });
        console.log('Captured run-protocol-config.png');
    });

    test('Capture Nav and Responsive Screenshots', async ({ page }) => {
        test.setTimeout(120000);
        await page.goto(`${APP_URL}/app/home?${MODE_PARAMS}`);
        await handleSplash(page);
        await page.waitForTimeout(5000);

        // 6. nav-rail.png
        const navRail = page.locator('.sidebar-rail');
        await navRail.waitFor({ state: 'visible', timeout: 30000 }).catch((e) => console.log('[Test] Silent catch (Sidebar rail):', e));
        if (await navRail.isVisible()) {
            await navRail.screenshot({ path: path.join(screenshotDir, 'nav-rail.png') });
            console.log('Captured nav-rail.png');

            // 7. nav-rail-hover.png
            const firstNavItem = navRail.locator('.nav-item').first();
            await firstNavItem.hover();
            await page.waitForTimeout(500);
            await page.screenshot({ path: path.join(screenshotDir, 'nav-rail-hover.png') });
            console.log('Captured nav-rail-hover.png');
        }

        // 11. sidebar-collapsed.png
        await page.setViewportSize({ width: 768, height: 1024 });
        await page.waitForTimeout(2000);
        await page.screenshot({ path: path.join(screenshotDir, 'sidebar-collapsed.png') });
        console.log('Captured sidebar-collapsed.png');
    });

    test('Capture Theme and Panel Screenshots', async ({ page }) => {
        test.setTimeout(180000);
        await page.goto(`${APP_URL}/app/home?${MODE_PARAMS}`);
        await handleSplash(page);
        await page.waitForTimeout(5000);

        const themeToggle = page.locator('[data-tour-id="theme-toggle"]');

        if (await themeToggle.isVisible({ timeout: 10000 })) {
            // 3. global-dark-mode.png
            await themeToggle.click({ force: true }); // Light -> Dark
            await page.waitForTimeout(1000);
            await page.screenshot({ path: path.join(screenshotDir, 'global-dark-mode.png') });
            console.log('Captured global-dark-mode.png');

            // 1 & 2. deck-view and deck-view-dark
            await page.goto(`${APP_URL}/app/workcell?${MODE_PARAMS}`);
            await handleSplash(page);
            await page.waitForTimeout(2000);
            const simulateBtn = page.locator('button').filter({ hasText: /Simulate/i }).first();
            if (await simulateBtn.isVisible()) {
                await simulateBtn.click();
                await page.waitForTimeout(2000);
                // Currently in Dark mode (from previous toggle)
                await page.screenshot({ path: path.join(screenshotDir, 'deck-view-dark.png') });
                console.log('Captured deck-view-dark.png');

                await themeToggle.click({ force: true }); // Dark -> System
                await themeToggle.click({ force: true }); // System -> Light
                await page.waitForTimeout(1000);
                await page.screenshot({ path: path.join(screenshotDir, 'deck-view.png') });
                console.log('Captured deck-view.png');
                await page.keyboard.press('Escape');
            }
        }

        // 8. protocol-detail-panel.png
        await page.goto(`${APP_URL}/app/protocols?${MODE_PARAMS}`);
        await handleSplash(page);
        await page.waitForTimeout(2000);
        const row = page.locator('tr[mat-row], app-protocol-card').first();
        if (await row.isVisible()) {
            await row.click();
            await page.waitForSelector('.mat-mdc-dialog-container, app-protocol-detail', { timeout: 10000 }).catch((e) => console.log('[Test] Silent catch (Dialog/Detail):', e));
            await page.screenshot({ path: path.join(screenshotDir, 'protocol-detail-panel.png') });
            console.log('Captured protocol-detail-panel.png');
        }
    });
});
