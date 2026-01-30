import { test } from '../fixtures/worker-db.fixture';
import { WelcomePage } from '../page-objects/welcome.page';

test.describe('First-Time User Experience', () => {
    test.beforeEach(async ({ page }) => {
        // Clear storage to simulate first-time user
        await page.goto('/');
        await page.evaluate(() => localStorage.clear());
        await page.reload();
    });

    test('should show welcome screen and navigate to dashboard', async ({ page }) => {
        const welcomePage = new WelcomePage(page);

        await welcomePage.goto();
        await welcomePage.handleSplashScreen();
        await welcomePage.verifyDashboardLoaded();
    });
});
