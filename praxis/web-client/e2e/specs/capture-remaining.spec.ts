import { test, expect } from '@playwright/test';
import * as path from 'path';
import * as fs from 'fs';

test.describe('Capture remaining dialogs', () => {
    test.setTimeout(120000);

    const screenshotDir = path.join(process.cwd(), 'e2e/screenshots/dialogs');

    test.beforeEach(async ({ page }) => {
        await page.goto('/app/home');
        // Wait for SQLite DB to be ready
        await page.waitForFunction(
            () => (window as any).sqliteService?.isReady$?.getValue() === true,
            null,
            { timeout: 30000 }
        );
        await page.evaluate(() => {
            localStorage.setItem('praxis_onboarding_completed', 'true');
        });
        await page.waitForLoadState('networkidle');
    });

    async function captureDialog(page, name) {
        const dialog = page.getByRole('dialog').or(page.locator('mat-dialog-container'));
        await expect(dialog.first()).toBeVisible({ timeout: 20000 });
        await page.waitForTimeout(1000);
        await page.screenshot({ path: path.join(screenshotDir, name) });
        console.log(`Captured ${name}`);
        await page.keyboard.press('Escape');
    }

    test('13. protocol-upload-dialog.png', async ({ page }) => {
        await page.goto('/app/protocols');
        await page.waitForLoadState('networkidle');
        const uploadBtn = page.locator('[data-tour-id="import-protocol-btn"]');
        await uploadBtn.click();
        await captureDialog(page, 'protocol-upload-dialog.png');
    });

    test('15. hardware-discovery-dialog.png', async ({ page }) => {
        await page.goto('/app/home');
        await page.keyboard.press('Control+k');
        await page.locator('input').fill('Discover');
        await page.waitForTimeout(1000);
        await page.keyboard.press('Enter');
        await captureDialog(page, 'hardware-discovery-dialog.png');
    });

    test('17. welcome-dialog.png', async ({ page }) => {
        await page.goto('/app/home');
        await page.evaluate(() => {
            localStorage.removeItem('praxis_onboarding_completed');
        });
        await page.goto('/app/home?welcome=true');
        await captureDialog(page, 'welcome-dialog.png');
    });
});
