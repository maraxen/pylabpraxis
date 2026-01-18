import { expect, test } from '@playwright/test';
import { WelcomePage } from '../page-objects/welcome.page';
import { ProtocolPage } from '../page-objects/protocol.page';
import { ExecutionMonitorPage } from '../page-objects/monitor.page';

test.describe('Mock Protocols Removal Verification', () => {
    test.beforeEach(async ({ page }) => {
        const welcomePage = new WelcomePage(page);
        // Force database reset
        await page.goto('/?resetdb=1');
        await welcomePage.handleSplashScreen();
    });

    test('verify mock protocols are absent and real protocols are present', async ({ page }) => {
        const protocolPage = new ProtocolPage(page);
        await protocolPage.goto();
        await protocolPage.ensureSimulationMode();

        // These were the mock protocols
        const mockProtocols = [
            'Daily System Maintenance',
            'Cell Culture Feed',
            'Evening Shutdown'
        ];

        for (const name of mockProtocols) {
            await expect(page.getByText(name)).not.toBeVisible();
        }

        // PCR Prep is a known real protocol from generate_browser_db.py / assets
        // We expect at least one real protocol to be visible if the database seeded correctly
        // from the prebuilt praxis.db or schema + real protocols.
        // NOTE: If the environment is totally fresh, this might fail, but let's see.
        const realProtocolLocator = page.locator('.protocol-card');
        await expect(realProtocolLocator.first()).toBeVisible();
    });

    test('verify run history starts empty', async ({ page }) => {
        const monitor = new ExecutionMonitorPage(page);
        await monitor.navigateToHistory();

        // Use a container check for empty state
        const emptyState = page.locator('.empty-runs-state, .no-runs-message, :text("No Runs Yet")');
        await expect(emptyState.first()).toBeVisible();

        // These were mock runs
        await expect(page.getByText('MOCK-RUN-001')).not.toBeVisible();
    });

    test('verify home dashboard has no mock runs', async ({ page }) => {
        // Navigate to home
        await page.goto('/app/home');

        // Check for "No recent activity" message
        await expect(page.getByText('No recent activity')).toBeVisible();

        // Ensure mock run names are not visible
        const mockRunNames = [
            'PCR Prep Run #12',
            'Cell Culture Feed Batch A',
            'System Calibration'
        ];

        for (const name of mockRunNames) {
            await expect(page.getByText(name)).not.toBeVisible();
        }
    });
});
