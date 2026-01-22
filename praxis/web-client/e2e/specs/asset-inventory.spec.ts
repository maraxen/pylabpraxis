import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Asset Inventory Persistence
 * 
 * These tests verify that Machines and Resources created in the UI persist
 * across page reloads, simulating the JupyterLite environment reading from
 * the browser-side SQLite database.
 */
test.describe('Asset Inventory Persistence', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');

        // In browser mode, we expect a redirect to /app/home
        await page.waitForURL('**/app/home', { timeout: 15000 }).catch(() => {
            console.log('Did not redirect to /app/home automatically');
        });

        // Ensure shell layout is visible
        await expect(page.locator('.sidebar-rail')).toBeVisible({ timeout: 10000 });

        // Handle Welcome Dialog if present (Browser Mode)
        const welcomeDialog = page.getByRole('dialog', { name: /Welcome to Praxis/i });
        if (await welcomeDialog.isVisible({ timeout: 5000 })) {
            console.log('Dismissing Welcome Dialog...');
            await page.getByRole('button', { name: /Skip for Now/i }).click();
            await expect(welcomeDialog).not.toBeVisible();
        }

        page.on('console', msg => {
            const text = msg.text();
            if (text.includes('ASSET-DEBUG') || text.includes('[SqliteService]')) {
                console.log(`BROWSER_LOG: ${text}`);
            }
        });
    });

    test('should persist created machine across reloads', async ({ page }) => {
        const machineName = `E2E Machine ${Date.now()}`;

        console.log('Navigating to Assets...');
        // 1. Navigate to Assets via sidebar
        // Use CSS selector as backup if accessible name 'Assets' is missing/hidden
        const assetsLink = page.locator('.sidebar-rail a[href="/app/assets"]');
        await expect(assetsLink).toBeVisible();
        await assetsLink.click();

        // Wait for Quick Actions to load
        await expect(page.getByText('Quick Actions')).toBeVisible({ timeout: 10000 });

        // SCREENSHOT: Asset List View
        await page.screenshot({ path: '/tmp/e2e-asset/asset-list_initial.png' });

        console.log('Looking for Add Machine button...');
        // 2. Click "Add Machine" 
        const addMachineBtn = page.getByRole('button', { name: /Add Machine/i });
        if (await addMachineBtn.isVisible()) {
            console.log('Add Machine button found, clicking...');
            await addMachineBtn.click();
        } else {
            console.log('Add Machine button NOT found!');
            await page.screenshot({ path: '/tmp/e2e-asset/debug_no_add_machine.png' });
            // print all buttons
            const buttons = await page.getByRole('button').allInnerTexts();
            console.log('Available buttons:', buttons);
        }

        // 3. Wait for dialog (title: "Add New Machine")
        await expect(page.getByRole('heading', { name: /Add New Machine/i })).toBeVisible({ timeout: 5000 });

        // 4. Machine dialog requires searching for a machine type first
        // Fill the "Search Machine Type" autocomplete
        const machineTypeInput = page.getByPlaceholder(/Search by name, manufacturer/i);
        await machineTypeInput.fill('Opentrons');
        await page.waitForTimeout(500); // Wait for autocomplete

        // SCREENSHOT: Filter Interactions
        await page.screenshot({ path: '/tmp/e2e-asset/filter-interaction.png' });

        // Select first option in the autocomplete dropdown
        const optionLocator = page.getByRole('option').first();
        if (await optionLocator.isVisible({ timeout: 3000 })) {
            await optionLocator.click();
        } else {
            // If no specific Opentrons exists, try a more generic search
            await machineTypeInput.clear();
            await machineTypeInput.fill('Hamilton');
            await page.waitForTimeout(500);
            await page.screenshot({ path: '/tmp/e2e-asset/filter-fallback.png' });
            await page.getByRole('option').first().click();
        }

        // 5. Now fill the "Name" field
        await page.getByLabel('Name').fill(machineName);

        // SCREENSHOT: Asset Detail View (Creation Dialog)
        await page.screenshot({ path: '/tmp/e2e-asset/asset-detail_creation-dialog.png' });

        // 6. Save
        await page.getByRole('button', { name: /Save/i }).click();

        // 7. Wait for dialog to close
        await expect(page.getByRole('heading', { name: /Add New Machine/i })).not.toBeVisible({ timeout: 5000 });

        // 8. Navigate to Machines tab to verify it was added
        await page.getByRole('tab', { name: /Machines/i }).click();
        await expect(page.getByText(machineName)).toBeVisible({ timeout: 10000 });

        // SCREENSHOT: Asset List View (With Data)
        await page.screenshot({ path: '/tmp/e2e-asset/asset-list_with-machine.png' });

        // 9. Reload page to test persistence
        await page.reload();

        // Navigate back to assets and machines tab
        await page.locator('.sidebar-rail a[href="/app/assets"]').click();
        await expect(page.getByText('Quick Actions')).toBeVisible({ timeout: 10000 });
        await page.getByRole('tab', { name: /Machines/i }).click();

        // Verify machine is still there
        await expect(page.getByText(machineName)).toBeVisible({ timeout: 10000 });
    });

    test('should persist created resource across reloads', async ({ page }) => {
        const resourceName = `E2E Resource ${Date.now()}`;

        console.log('Navigating to Assets (Resource Test)...');
        // 1. Navigate to Assets via sidebar
        await page.locator('.sidebar-rail a[href="/app/assets"]').click();
        await expect(page.getByText('Quick Actions')).toBeVisible({ timeout: 10000 });

        // 2. Click "Add Resource"
        await page.getByRole('button', { name: /Add Resource/i }).click();

        // 3. Wait for dialog (title shows "Select Resource Category")
        await expect(page.getByRole('heading', { name: /Select Resource Category/i })).toBeVisible({ timeout: 5000 });

        // 4. Resource dialog requires selecting a CATEGORY first (it's a multi-step dialog)
        // Click on a category card - we'll try "plate" or the first available
        const plateCategory = page.locator('.category-card').filter({ hasText: /plate/i }).first();
        if (await plateCategory.isVisible({ timeout: 2000 })) {
            await plateCategory.click();
        } else {
            // Just click the first category card
            await page.locator('.category-card').first().click();
        }

        // 5. Now we're in Step 2 - fill "Resource Model" autocomplete
        await expect(page.getByLabel('Resource Model')).toBeVisible({ timeout: 5000 });
        const modelInput = page.getByLabel('Resource Model');
        await modelInput.fill('96');
        await page.waitForTimeout(500);

        // Select first matching definition
        const defOption = page.getByRole('option').first();
        if (await defOption.isVisible({ timeout: 3000 })) {
            await defOption.click();
        }

        // 6. Fill the "Name" field
        await page.getByLabel('Name').fill(resourceName);

        // 7. Save
        await page.getByRole('button', { name: /Save Resource/i }).click();

        // 8. Wait for dialog to close
        await expect(page.getByRole('heading', { name: /Add New/i })).not.toBeVisible({ timeout: 5000 });

        // 9. Navigate to Registry tab to verify
        await page.getByRole('tab', { name: /Registry/i }).click();
        await expect(page.getByText(resourceName)).toBeVisible({ timeout: 10000 });

        // 10. Reload page to test persistence
        await page.reload();

        // Navigate back
        await page.locator('.sidebar-rail a[href="/app/assets"]').click();
        await expect(page.getByText('Quick Actions')).toBeVisible({ timeout: 10000 });
        await page.getByRole('tab', { name: /Registry/i }).click();

        // Verify resource is still there
        await expect(page.getByText(resourceName)).toBeVisible({ timeout: 10000 });
    });
});
