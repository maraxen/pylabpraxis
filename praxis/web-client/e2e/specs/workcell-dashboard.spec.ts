import { test, expect } from '@playwright/test';

test.describe('Workcell Dashboard', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/workcells/1');
    });

    test('should load the dashboard page', async ({ page }) => {
        await expect(page.locator('h1')).toContainText('Workcell Dashboard');
    });

    test('should allow hierarchical explorer navigation', async ({ page }) => {
        await page.locator('tree-node-expander').first().click();
        await expect(page.locator('p').first()).toBeVisible();
    });

    test('should display machine cards', async ({ page }) => {
        await expect(page.locator('app-machine-card').first()).toBeVisible();
    });

    test('should navigate to machine focus view on card click', async ({ page }) => {
        await page.locator('app-machine-card').first().click();
        await expect(page.locator('app-machine-focus')).toBeVisible();
    });

    test('should display deck state visualization in machine focus view', async ({ page }) => {
        await page.locator('app-machine-card').first().click();
        await expect(page.locator('app-deck-state')).toBeVisible();
    });
});
