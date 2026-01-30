import { test, expect } from '../../fixtures/worker-db.fixture';
import { WelcomePage } from '../../page-objects/welcome.page';
import { AssetsPage } from '../../page-objects/assets.page';

/**
 * Interaction tests for Asset/Machine/Resource forms and validation.
 */
test.describe('Asset Forms Interaction', () => {
    test.beforeEach(async ({ page }) => {
        const welcomePage = new WelcomePage(page);
        await welcomePage.goto();
        await welcomePage.handleSplashScreen();
    });

    test('should validate machine name is required', async ({ page }) => {
        const assetsPage = new AssetsPage(page);
        await assetsPage.goto();
        await assetsPage.waitForOverlay();
        await assetsPage.navigateToMachines();

        // Open Add Machine dialog
        await assetsPage.addMachineButton.click();
        const dialog = page.getByRole('dialog');
        await expect(dialog).toBeVisible();

        // Move to Step 3 (Configuration) - assuming first available type/backend
        const categoryCards = page.locator('.category-card');
        await categoryCards.first().click();
        
        const definitionItems = page.locator('.definition-item');
        await definitionItems.first().click();

        // Clear name and verify Finish is disabled
        const nameInput = page.getByLabel('Instance Name').or(page.getByLabel('Name')).first();
        await nameInput.clear();
        
        const finishBtn = page.getByRole('button', { name: /Finish|Save/i });
        await expect(finishBtn).toBeDisabled();

        // Fill name and verify Finish is enabled
        await nameInput.fill('Valid Machine Name');
        await expect(finishBtn).toBeEnabled();
    });

    test('should show validation error for invalid JSON in advanced config', async ({ page }) => {
        const assetsPage = new AssetsPage(page);
        await assetsPage.goto();
        await assetsPage.waitForOverlay();
        await assetsPage.navigateToMachines();

        await assetsPage.addMachineButton.click();
        
        // Advance to Step 3
        await page.locator('.category-card').first().click();
        await page.locator('.definition-item').first().click();

        // Open Advanced JSON section
        const advancedToggle = page.getByRole('button', { name: /Advanced JSON/i }).first();
        if (await advancedToggle.isVisible()) {
            await advancedToggle.click();
            
            const jsonInput = page.getByLabel(/Connection Info|User Configured Capabilities/i).first();
            await jsonInput.fill('{ invalid json }');
            
            // Should show mat-error
            await expect(page.locator('mat-error')).toBeVisible();
            await expect(page.getByRole('button', { name: /Finish|Save/i })).toBeDisabled();
        }
    });
});