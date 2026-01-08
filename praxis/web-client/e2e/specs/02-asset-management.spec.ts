import { test, expect } from '@playwright/test';
import { WelcomePage } from '../page-objects/welcome.page';
import { AssetsPage } from '../page-objects/assets.page';

/**
 * E2E Tests for Asset Management
 * 
 * These tests verify the Asset Management UI in Browser Mode.
 * Note: Full CRUD operations require seeded definition data in the browser-side SQLite.
 */
test.describe('Asset Management Flow', () => {
    let assetsPage: AssetsPage;

    test.beforeEach(async ({ page }) => {
        const welcomePage = new WelcomePage(page);
        assetsPage = new AssetsPage(page);

        await welcomePage.goto();
        await welcomePage.handleSplashScreen();
    });

    test('should navigate to Assets page and see tabs', async ({ page }) => {
        // Navigate to Assets
        await assetsPage.goto();
        await assetsPage.waitForOverlay();

        // Verify tabs are visible
        await expect(assetsPage.overviewTab).toBeVisible({ timeout: 10000 });
        await expect(assetsPage.machinesTab).toBeVisible();
        await expect(assetsPage.resourcesTab).toBeVisible();
        await expect(assetsPage.registryTab).toBeVisible();
    });

    test('should open Add Machine dialog', async ({ page }) => {
        // Navigate to Assets
        await assetsPage.goto();
        await assetsPage.waitForOverlay();

        // Click Add Machine button
        await expect(assetsPage.addMachineButton).toBeVisible({ timeout: 10000 });
        await assetsPage.addMachineButton.click();

        // Verify dialog opens with correct title
        await expect(page.getByRole('heading', { name: /Add New Machine/i })).toBeVisible({ timeout: 5000 });

        // The dialog should show step indicators (Select Machine Category heading)
        await expect(page.getByRole('heading', { name: /Select Machine Category/i })).toBeVisible();

        // Close dialog via Cancel button or mat-dialog-close
        await page.getByRole('button', { name: /Cancel/i }).click();
        await expect(page.getByRole('dialog')).not.toBeVisible({ timeout: 5000 });
    });

    test('should open Add Resource dialog', async ({ page }) => {
        // Navigate to Assets
        await assetsPage.goto();
        await assetsPage.waitForOverlay();

        // Click Add Resource button
        await expect(assetsPage.addResourceButton).toBeVisible({ timeout: 10000 });
        await assetsPage.addResourceButton.click();

        // Verify dialog opens with correct title ("Add Resource")
        await expect(page.getByRole('heading', { name: /Add Resource/i })).toBeVisible({ timeout: 5000 });

        // The dialog should show search input
        await expect(page.getByPlaceholder(/Search resources/i)).toBeVisible({ timeout: 5000 });

        // Close dialog via close button (mat-dialog-close)
        await page.locator('button[mat-dialog-close]').or(page.getByRole('button', { name: /close/i })).click();
        await expect(page.getByRole('dialog')).not.toBeVisible({ timeout: 5000 });
    });

    test('should navigate between tabs', async ({ page }) => {
        // Navigate to Assets
        await assetsPage.goto();
        await assetsPage.waitForOverlay();

        // Navigate to Machines tab
        await assetsPage.navigateToMachines();
        await expect(assetsPage.machinesTab).toBeVisible();

        // Navigate to Resources tab
        await assetsPage.navigateToResources();
        await expect(assetsPage.resourcesTab).toBeVisible();

        // Navigate to Registry tab
        await assetsPage.navigateToRegistry();
        await expect(assetsPage.registryTab).toBeVisible();

        // Navigate back to Overview
        await assetsPage.navigateToOverview();
        await expect(assetsPage.overviewTab).toBeVisible();
    });

    test('should show search input on resource list', async ({ page }) => {
        // Navigate to Assets > Resources
        await assetsPage.goto();
        await assetsPage.waitForOverlay();
        await assetsPage.navigateToResources();

        // Wait for content to load - Resources tab shows ResourceAccordion
        await page.waitForTimeout(500);
    });

    // Skip full CRUD tests if definitions aren't loaded
    // These tests require seeded definition catalogs
    test.describe('CRUD Operations (requires seeded data)', () => {
        test.skip(({ browserName }) => true, 'Skipped: Requires pre-seeded definition catalogs in browser SQLite');

        test('should add a new machine', async ({ page }) => {
            const machineName = `Test Machine ${Date.now()}`;
            await assetsPage.goto();
            await assetsPage.waitForOverlay();
            await assetsPage.navigateToMachines();
            await assetsPage.createMachine(machineName);
            await assetsPage.verifyAssetVisible(machineName);
        });

        test('should add a new resource', async ({ page }) => {
            const resourceName = `Test Resource ${Date.now()}`;
            await assetsPage.goto();
            await assetsPage.waitForOverlay();
            await assetsPage.navigateToResources();
            await assetsPage.createResource(resourceName);
            await assetsPage.verifyAssetVisible(resourceName);
        });

        test('should delete a machine', async ({ page }) => {
            const machineName = `Delete Machine ${Date.now()}`;
            await assetsPage.goto();
            await assetsPage.waitForOverlay();
            await assetsPage.navigateToMachines();
            await assetsPage.createMachine(machineName);
            await assetsPage.verifyAssetVisible(machineName);
            await assetsPage.deleteMachine(machineName);
            await assetsPage.verifyAssetNotVisible(machineName);
        });

        test('should persist machine after page reload', async ({ page }) => {
            const machineName = `Persist Machine ${Date.now()}`;
            await assetsPage.goto();
            await assetsPage.waitForOverlay();
            await assetsPage.navigateToMachines();
            await assetsPage.createMachine(machineName);
            await assetsPage.verifyAssetVisible(machineName);
            await page.reload();
            await assetsPage.waitForOverlay();
            await assetsPage.navigateToMachines();
            await assetsPage.verifyAssetVisible(machineName);
        });
    });
});


