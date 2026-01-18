import { test, expect } from '@playwright/test';
import { WelcomePage } from '../page-objects/welcome.page';
import { AssetsPage } from '../page-objects/assets.page';
import * as path from 'path';
import * as fs from 'fs';

test('Capture application UI screenshots after polish', async ({ page }) => {
    test.setTimeout(120000);
    const welcomePage = new WelcomePage(page);
    const assetsPage = new AssetsPage(page);
    const screenshotDir = path.join(process.cwd(), 'e2e/screenshots/after');

    if (!fs.existsSync(screenshotDir)) {
        fs.mkdirSync(screenshotDir, { recursive: true });
    }

    // 1. Homepage/Dashboard
    await welcomePage.goto();
    await welcomePage.handleSplashScreen();
    await assetsPage.goto();
    await assetsPage.waitForOverlay();
    await page.screenshot({ path: path.join(screenshotDir, '01-dashboard.png') });
    console.log('Captured 01-dashboard.png');

    // 2. Add Asset dialog (click the Add Asset button)
    await assetsPage.addMachineButton.click();
    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible({ timeout: 10000 });
    await page.screenshot({ path: path.join(screenshotDir, '02-add-asset-dialog.png') });
    console.log('Captured 02-add-asset-dialog.png');

    // 3. Machine selection step (select "Machine" type)
    const machineOption = page.getByRole('dialog').locator('button').filter({ hasText: /Machine/i }).first();
    if (await machineOption.isVisible({ timeout: 5000 })) {
        await machineOption.click();
        console.log('Clicked Machine option');
    }
    
    // Wait for frontend types to load
    await page.getByRole('dialog').locator('button.selection-card:visible').first().waitFor({ state: 'visible', timeout: 15000 });
    await page.screenshot({ path: path.join(screenshotDir, '03-machine-selection.png') });
    console.log('Captured 03-machine-selection.png');

    // 4. Frontend selection step (select any frontend like "Liquid Handler")
    const liquidHandlerCard = page.getByRole('dialog').locator('button.selection-card:visible').filter({ hasText: /Liquid Handler/i }).first();
    await expect(liquidHandlerCard).toBeVisible({ timeout: 10000 });
    await liquidHandlerCard.click();
    
    // Ensure it's selected
    await page.waitForTimeout(1000);
    
    await page.screenshot({ path: path.join(screenshotDir, '04-frontend-selected.png') });
    console.log('Captured 04-frontend-selected.png');

    // Click Next to go to step 2
    const nextButton = page.locator('button').filter({ hasText: /Next/i }).first();
    if (await nextButton.isVisible()) {
        await nextButton.click({ force: true });
    } else {
        await page.getByRole('button', { name: /Next/i }).first().click({ force: true });
    }
    
    await page.waitForTimeout(2000); // Wait for transition

    // 5. Backend selection step (show available backends)
    const backendCards = page.getByRole('dialog').locator('button.selection-card.definition-card:visible');
    try {
        await backendCards.first().waitFor({ state: 'visible', timeout: 10000 });
    } catch (e) {
        console.log('Backend cards did not appear, taking screenshot anyway');
    }
    await page.screenshot({ path: path.join(screenshotDir, '05-backend-selection.png') });
    console.log('Captured 05-backend-selection.png');
});
