
import { test, expect } from '@playwright/test';

test('logo rendering verification', async ({ page }) => {
    await page.goto('http://localhost:8080/praxis/');

    // Wait for the app to load
    await page.waitForSelector('.logo-mark, .logo-image', { timeout: 10000 });

    const logo = page.locator('.logo-mark, .logo-image').first();
    const computedStyle = await logo.evaluate((el) => {
        const style = window.getComputedStyle(el);
        return {
            logoSvg: style.getPropertyValue('--logo-svg'),
            maskImage: style.getPropertyValue('mask-image') || style.getPropertyValue('-webkit-mask-image')
        };
    });

    console.log('Computed Style:', JSON.stringify(computedStyle, null, 2));

    expect(computedStyle.logoSvg).not.toBe('none');
    expect(computedStyle.logoSvg).toContain('url("data:image/svg+xml');

    // Also check if it's NOT 'unsafe:data'
    expect(computedStyle.logoSvg).not.toContain('unsafe:');
});
