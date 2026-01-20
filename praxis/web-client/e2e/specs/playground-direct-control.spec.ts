import { test, expect } from '@playwright/test';

test('should allow adding a machine and using direct control', async ({ page }) => {
    // Mock API calls - these might be bypassed in Browser Mode but good to have
    await page.route('**/api/v1/machines/definitions/facets', async route => {
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
                machine_category: [{ value: 'LiquidHandler', count: 1 }],
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
                    machine_category: 'LiquidHandler',
                    manufacturer: 'Hamilton',
                    description: 'Hamilton STAR liquid handler',
                    available_simulation_backends: ['Simulated']
                }
            ])
        });
    });

    page.on('console', msg => console.log(`BROWSER LOG: ${msg.text()}`));

    // 1. Go to /app/playground
    await page.goto('/app/playground?mode=browser&resetdb=1');
    
    // Wait for SQLite DB to be ready
    await page.waitForFunction(() => (window as any).sqliteService?.isReady$?.getValue() === true, null, { timeout: 45000 });

    // Handle Welcome Dialog
    try {
        const dismissBtn = page.getByRole('button', { name: /Get Started|Skip|Close/i }).first();
        if (await dismissBtn.isVisible({ timeout: 5000 })) {
            await dismissBtn.click();
        }
    } catch (e) {}

    await page.screenshot({ path: 'e2e/screenshots/direct-control-step1.png' });

    // 2. Open Inventory from Playground (using the header action button)
    // Wait for header to be visible
    await expect(page.locator('.repl-header')).toBeVisible({ timeout: 25000 });
    
    const inventoryBtn = page.locator('button').filter({ has: page.locator('mat-icon', { hasText: 'inventory_2' }) });
    await expect(inventoryBtn).toBeVisible();
    await inventoryBtn.click();

    const wizard = page.locator('app-asset-wizard');
    await expect(wizard).toBeVisible();

    // 3. Add Machine (simplified flow based on asset-wizard.spec.ts)
    const machineCard = wizard.locator('mat-card').filter({ hasText: 'Machine' }).first();
    await expect(machineCard).toBeVisible();
    await machineCard.click({ force: true });
    
    await page.waitForTimeout(1000); // Wait for transition
    
    const categorySelect = wizard.getByRole('combobox', { name: 'Category' });
    await expect(categorySelect).toBeEnabled();
    await categorySelect.click();
    
    await page.waitForTimeout(1000); // Wait for animation
    
    // Try to find LiquidHandler or any first option
    const option = page.getByRole('option').first();
    await expect(option).toBeVisible();
    await option.click();
    
    await wizard.getByRole('button', { name: 'Next' }).click();

    await wizard.getByLabel('Search Definitions').fill('STAR');
    await page.waitForTimeout(2000); 
    
    // Click first result
    const resultCard = wizard.locator('.result-card').first();
    await expect(resultCard).toBeVisible();
    await resultCard.click();
    
    await wizard.getByRole('button', { name: 'Next' }).click();

    await wizard.getByRole('button', { name: 'Next' }).click(); // Skip config

    await wizard.getByRole('button', { name: 'Create Asset' }).click();

    await expect(wizard).not.toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'e2e/screenshots/direct-control-step2.png' });

    // 4. Verify Machine is selected
    const directControlTab = page.getByRole('tab', { name: 'Direct Control' });
    await directControlTab.click();

    // Verify Direct Control is active
    const directControl = page.locator('app-direct-control');
    await expect(directControl).toBeVisible({ timeout: 10000 });

    await page.screenshot({ path: 'e2e/screenshots/direct-control-step3.png' });

    // Capture final screenshot
    await page.screenshot({ path: 'e2e/screenshots/direct-control-final.png' });
});
