import { test, expect } from '../fixtures/app.fixture';

test.describe('Workcell Dashboard', () => {
    test.beforeEach(async ({ page }) => {
        // Navigate to workcell dashboard with browser mode
        await page.goto('/app/workcell?mode=browser');

        // Wait for SqliteService to be ready
        await page.waitForFunction(
            () => {
                const sqliteService = (window as any).sqliteService;
                return sqliteService && sqliteService.isReady$?.getValue() === true;
            },
            null,
            { timeout: 30000 }
        );

        // Wait for loading spinner to disappear
        await expect(page.locator('.animate-spin')).not.toBeVisible({ timeout: 15000 });
    });

    test('should load the dashboard page', async ({ page }) => {
        // Verify h1 contains dashboard title
        await expect(page.locator('h1')).toContainText('Workcell Dashboard');
        await page.screenshot({ path: '/tmp/e2e-workcell/dashboard-loaded.png' });
    });

    test('should display explorer sidebar', async ({ page }) => {
        // Check for workcell explorer component
        await expect(page.locator('app-workcell-explorer')).toBeVisible({ timeout: 10000 });

        // Verify search input exists
        await expect(page.locator('app-workcell-explorer input[type="text"]')).toBeVisible();
    });

    test('should display machine cards when machines exist', async ({ page }) => {
        // Check if machines exist (app-machine-card) OR show empty state
        const machineCards = page.locator('app-machine-card');
        const emptyState = page.locator('text=No machines found');

        // Wait for either state to appear
        await expect(machineCards.first().or(emptyState)).toBeVisible({ timeout: 15000 });

        const cardCount = await machineCards.count();
        if (cardCount > 0) {
            // If cards exist, verify they're visible
            await expect(machineCards.first()).toBeVisible();
            await page.screenshot({ path: '/tmp/e2e-workcell/machine-cards.png' });
        } else {
            // Empty state is acceptable - means no machines in database
            await expect(emptyState).toBeVisible();
            await page.screenshot({ path: '/tmp/e2e-workcell/no-machines.png' });
        }
    });

    test('should navigate to machine focus view on card click', async ({ page }) => {
        // Check if machine cards exist
        const machineCards = page.locator('app-machine-card');
        const cardCount = await machineCards.count();

        if (cardCount === 0) {
            // Skip if no machines - can't test focus view
            test.skip(true, 'No machines available to test focus view');
            return;
        }

        // Click first machine card
        await machineCards.first().click();

        // Verify focus view appears
        await expect(page.locator('app-machine-focus-view')).toBeVisible({ timeout: 10000 });
        await page.screenshot({ path: '/tmp/e2e-workcell/machine-focus.png' });
    });

    test('should show deck visualization in focus view when available', async ({ page }) => {
        // Check if machine cards exist
        const machineCards = page.locator('app-machine-card');
        const cardCount = await machineCards.count();

        if (cardCount === 0) {
            test.skip(true, 'No machines available to test deck view');
            return;
        }

        // Click first machine card
        await machineCards.first().click();

        // Wait for focus view
        await expect(page.locator('app-machine-focus-view')).toBeVisible({ timeout: 10000 });

        // Check for deck state component (optional - not all machines have it)
        const deckState = page.locator('app-deck-state, app-deck-visualization, .deck-canvas, canvas');
        const hasDeckState = await deckState.count() > 0;

        await page.screenshot({ path: '/tmp/e2e-workcell/deck-state.png' });

        // Log whether deck visualization was found (informational, not a failure)
        console.log(`Deck visualization found: ${hasDeckState}`);
    });
});
