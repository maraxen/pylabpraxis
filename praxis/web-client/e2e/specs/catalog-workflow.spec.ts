
import { test, expect } from '@playwright/test';

test.describe('Catalog to Inventory Workflow', () => {
    test.beforeEach(async ({ page }) => {
        // Go to playground with resetdb to ensure clean slate (no machines)
        await page.goto('/app/playground?resetdb=1');
        // Wait for SQLite DB to be ready
        await page.waitForFunction(
            () => (window as any).sqliteService?.isReady$?.getValue() === true,
            null,
            { timeout: 30000 }
        );
    });

    test('should show catalog tab and add simulated machine', async ({ page }) => {
        // Handle onboarding splash if present
        const skipBtn = page.getByRole('button', { name: /Skip/i });
        try {
            await skipBtn.waitFor({ state: 'visible', timeout: 5000 });
            await skipBtn.click();
        } catch (e) {
            // Not present, continue
        }

        // Open Inventory Dialog using the correct aria-label in Playground
        await page.getByLabel('Open Inventory Dialog').click();

        // Check for Catalog tab
        await expect(page.getByRole('tab', { name: 'Catalog' })).toBeVisible();

        // If machines are empty, Catalog might be selected by default?
        // We didn't implement auto-select logic explicitly in the component, defaulting to index 0.
        // If I prepended Catalog, it is index 0.

        await expect(page.getByRole('tab', { name: 'Catalog' })).toHaveAttribute('aria-selected', 'true');

        // Check for definitions
        await page.locator('mat-card-title').first().waitFor({ state: 'visible', timeout: 15000 });
        await expect(page.locator('mat-card-title').first()).toBeVisible();

        // Click Add Simulated
        await page.getByRole('button', { name: 'Add Simulated' }).first().click();

        // Should switch to "Browse & Add" (tab index 2) or something?
        // We set activeTab.set(2) in the code.
        // Index 2 is "Browse & Add" in the NEW structure?
        // Structure: 0=Catalog, 1=Quick Add, 2=Browse & Add, 3=Current Items?
        // Wait, original was: 0=Quick Add, 1=Browse & Add, 2=Current Items.
        // I added Catalog at start. So:
        // 0=Catalog, 1=Quick Add, 2=Browse & Add, 3=Current Items.

        // So switching to 2 goes to "Browse & Add".
        // Let's verify we are on "Browse & Add" tab.
        await expect(page.getByRole('tab', { name: 'Browse & Add' })).toHaveAttribute('aria-selected', 'true');

        // And type should be 'machine' and category selected.
        // We can verify this by checking if the stepper is showing assets.
    });
});
