import { test, expect } from '../fixtures/worker-db.fixture';
import { WelcomePage } from '../page-objects/welcome.page';
import { AssetsPage } from '../page-objects/assets.page';
import { SettingsPage } from '../page-objects/settings.page';
import * as fs from 'fs';
import * as path from 'path';

test.describe('Browser Mode Specifics (DB Persistence)', () => {
    test.beforeEach(async ({ page }) => {
        const welcomePage = new WelcomePage(page);
        await welcomePage.goto();
        await welcomePage.handleSplashScreen();
    });

    test('should export and import database preserving data', async ({ page }) => {
        const assetsPage = new AssetsPage(page);
        const settingsPage = new SettingsPage(page);
        const uniqueName = `Persist-${Date.now()}`;

        // 1. Create Data
        await assetsPage.goto();
        await assetsPage.createMachine(uniqueName);
        await assetsPage.verifyAssetVisible(uniqueName);

        // 2. Export DB
        await settingsPage.goto();
        const downloadPath = await settingsPage.exportDatabase();
        expect(downloadPath).toBeTruthy();

        // 3. Clear Data (Reset)
        // We'll simulate a clearing by deleting the asset manually or clearing storage if UI supports it
        // Check if Settings has a "Reset/Clear"
        // If not, creating a new context or clearing IndexedDB manually might be needed
        // For simplicity, let's delete the asset manually to show it's gone
        // Or reload a fresh context? No, persistence is in IndexedDB.

        // Let's assume we can rely on Import overwriting. 
        // To verify Import works, we should delete the asset first.

        // However, we don't have a reliable 'delete' implementation in AssetsPage yet in this iteration
        // Let's clear IndexedDB manually via console
        await page.evaluate(async () => {
            const dbs = await window.indexedDB.databases();
            dbs.forEach(db => window.indexedDB.deleteDatabase(db.name!));
        });
        await page.reload();

        // Verify it's gone
        await assetsPage.goto();
        await assetsPage.machinesTab.click();
        await assetsPage.verifyAssetNotVisible(uniqueName);

        // 4. Import DB
        await settingsPage.goto();
        await settingsPage.importDatabase(downloadPath!);

        // 5. Verify Data Restored
        await assetsPage.goto();
        await assetsPage.machinesTab.click();
        await assetsPage.verifyAssetVisible(uniqueName);
    });
});
