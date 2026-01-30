import { test, expect } from '../fixtures/worker-db.fixture';

/**
 * Asset Wizard E2E Test
 * 
 * This test verifies the end-to-end journey of adding a new machine 
 * using the Asset Wizard in the laboratory inventory.
 */
test.describe('Asset Wizard Journey', () => {

    test.afterEach(async ({ page }) => {
        // Dismiss any open dialogs/overlays to ensure clean state
        await page.keyboard.press('Escape').catch((e) => console.log('[Test] Silent catch (Escape):', e));
    });

    test('should guide the user through creating a Hamilton STAR machine', async ({ page }) => {
        // Mock API calls to ensure test stability
        await page.route('**/api/v1/machines/definitions/facets', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    machine_category: [{ value: 'Liquid Handler', count: 1 }],
                    manufacturer: [{ value: 'Hamilton', count: 1 }]
                })
            });
        });

        await page.route('**/api/v1/machines/definitions?*', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify([
                    {
                        accession_id: 'mach_test_001',
                        name: 'Hamilton STAR',
                        fqn: 'pylabrobot.liquid_handling.backends.hamilton.STAR',
                        plr_category: 'Machine',
                        machine_category: 'Liquid Handler',
                        manufacturer: 'Hamilton',
                        description: 'Hamilton STAR liquid handler',
                        available_simulation_backends: ['Simulated']
                    }
                ])
            });
        });

        // 1. Go to /inventory (aliased to /assets)
        await page.goto('/assets?mode=browser&resetdb=1');

        // Wait for SQLite DB to be ready
        await page.waitForFunction(() => (window as any).sqliteService?.isReady$?.getValue() === true, null, { timeout: 30000 });

        // Handle Welcome Dialog
        try {
            const dismissBtn = page.getByRole('button', { name: /Get Started|Skip|Close/i }).first();
            if (await dismissBtn.isVisible({ timeout: 5000 })) {
                await dismissBtn.click();
            }
        } catch (e) { console.log('[Test] Caught:', (e as Error).message); }

        await page.screenshot({ path: 'praxis/web-client/e2e/screenshots/asset-wizard-step1.png' });

        // 2. Click Add Asset
        const addAssetBtn = page.locator('[data-tour-id="add-asset-btn"]');
        await expect(addAssetBtn).toBeVisible({ timeout: 15000 });
        await addAssetBtn.click();

        const wizard = page.locator('app-asset-wizard');
        await expect(wizard).toBeVisible();
        await page.screenshot({ path: 'praxis/web-client/e2e/screenshots/asset-wizard-step2.png' });

        // 3. Select Machine -> Liquid Handler
        await wizard.locator('mat-card').filter({ hasText: /Machine/i }).first().click();
        await wizard.getByLabel('Category').click();
        await page.getByRole('option', { name: /Liquid Handler/i }).first().click();

        await page.screenshot({ path: 'praxis/web-client/e2e/screenshots/asset-wizard-step3.png' });
        await wizard.getByRole('button', { name: 'Next' }).click();

        // 4. Search and Select STAR
        await wizard.getByLabel('Search Definitions').fill('STAR');
        await page.waitForTimeout(1000); // debounce
        await wizard.locator('.result-card').first().click();

        await page.screenshot({ path: 'praxis/web-client/e2e/screenshots/asset-wizard-step4.png' });
        await wizard.getByRole('button', { name: 'Next' }).click();

        // 5. Verify Simulated
        const backendSelect = wizard.getByLabel('Backend (Driver)');
        await expect(backendSelect).toContainText(/Simulated/i);

        await page.screenshot({ path: 'praxis/web-client/e2e/screenshots/asset-wizard-step5.png' });
        await wizard.getByRole('button', { name: 'Next' }).click();

        // 6. Summary and Create
        await expect(wizard.getByRole('heading', { name: 'Summary' })).toBeVisible();
        await expect(wizard.locator('.review-card')).toContainText('Hamilton STAR');

        await page.screenshot({ path: 'praxis/web-client/e2e/screenshots/asset-wizard-step6.png' });
        await wizard.getByRole('button', { name: 'Create Asset' }).click();

        // 7. Verify result
        await expect(wizard).not.toBeVisible({ timeout: 15000 });
        await expect(page.getByText('Hamilton STAR')).toBeVisible({ timeout: 15000 });
        await page.screenshot({ path: 'praxis/web-client/e2e/screenshots/asset-wizard-step7.png' });
    });
});
