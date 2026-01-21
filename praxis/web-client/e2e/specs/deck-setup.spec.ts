
import { test, expect } from '@playwright/test';

test('deck setup placeholder', async ({ page }) => {
    await page.goto('/assets');
    await expect(page.locator('h1')).toContainText('Asset Management');
});
