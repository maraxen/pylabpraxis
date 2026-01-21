import { test, expect } from '@playwright/test';

test.describe('Protocol Library', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/protocols');
    });

    test('should load the protocol library page', async ({ page }) => {
        await expect(page.locator('h1')).toHaveText('Protocol Library');
    });

    test('should search for a protocol by name', async ({ page }) => {
        await page.fill('input[placeholder="Search by name"]', 'e2e-test-protocol');
        await expect(page.locator('mat-card-title')).toHaveText('e2e-test-protocol');
    });

    test('should filter protocols by category', async ({ page }) => {
        await page.click('mat-select[formcontrolname="category"]');
        await page.click('mat-option[value="e2e-test-category"]');
        await expect(page.locator('mat-card-title')).toHaveText('e2e-test-protocol');
    });

    test('should open protocol details', async ({ page }) => {
        await page.click('mat-card:has-text("e2e-test-protocol")');
        await expect(page.locator('h1')).toHaveText('e2e-test-protocol');
    });

    test('should start a protocol run from the library', async ({ page }) => {
        await page.click('mat-card:has-text("e2e-test-protocol") button:has-text("Run")');
        await expect(page.locator('h1')).toHaveText('Run Protocol');
    });
});
