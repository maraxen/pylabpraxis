import { test, expect } from '@playwright/test';
import { WelcomePage } from '../../page-objects/welcome.page';

/**
 * E2E tests for Deck Simulation and Machine Instantiation flow.
 * FE-04: Simulation Machine Visibility & Custom Deck Integration.
 */
test.describe('Simulation & Instantiation Flow', () => {
    test.beforeEach(async ({ page }) => {
        const welcomePage = new WelcomePage(page);
        await welcomePage.goto();
        await welcomePage.handleSplashScreen();
    });

    test('should allow creating a custom deck and using it for a new machine', async ({ page }) => {
        // 1. Navigate to Workcell Dashboard
        await page.getByRole('link', { name: 'Workcell' }).click();
        await expect(page).toHaveURL(/.*workcell/);

        // 2. Open Simulation Dialog
        await page.getByRole('button', { name: 'Simulate' }).first().click();
        await expect(page.locator('app-deck-simulation-dialog')).toBeVisible();

        // 3. Configure Deck (select Hamilton STAR)
        await page.getByLabel('Deck Type').click();
        await page.getByRole('option', { name: 'Hamilton STAR' }).click();

        // 4. Name the configuration
        const configName = `Custom E2E Deck ${Date.now()}`;
        await page.getByLabel('Configuration Name').fill(configName);

        // 5. Add a carrier to test interaction logic
        await page.getByLabel(/Target Rail/).fill('5');
        await page.getByRole('button', { name: /Plate Carrier/i }).first().click();

        // 6. Save Configuration
        await page.getByRole('button', { name: 'Save Configuration' }).click();
        await expect(page.locator('app-deck-simulation-dialog')).not.toBeVisible();

        // 7. Open Playground/Inventory to use the new config
        await page.getByRole('link', { name: 'Playground' }).click();
        await page.getByRole('button', { name: 'Open Inventory Dialog' }).click();
        await expect(page.locator('app-inventory-dialog')).toBeVisible();

        // 8. Select Hamilton STAR as a simulation template
        // Note: We need to find the Hamilton STAR entry in the simulation list
        await page.getByText('Hamilton STAR').first().click();

        // 9. Verify the custom configuration appears in the dropdown
        const select = page.locator('mat-select[formcontrolname="deckConfigId"]');
        await select.click();

        const option = page.getByRole('option', { name: configName });
        await expect(option).toBeVisible();
        await option.click();

        // 10. Finalize addition
        await page.getByRole('button', { name: 'Add to Inventory' }).click();

        // Check for success snackbar
        await expect(page.locator('mat-snack-bar-container')).toContainText('Inserted');
    });
});
