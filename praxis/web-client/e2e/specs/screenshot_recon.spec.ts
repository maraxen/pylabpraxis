
import { test, expect } from '@playwright/test';

test('capture protocol runner screenshots', async ({ page }) => {
    console.log('Navigating to Protocol Runner...');
    await page.goto('http://localhost:4200/app/run?mode=browser', { waitUntil: 'networkidle' });

    // Wait for the main heading
    await page.waitForSelector('h1:has-text("Execute Protocol")', { timeout: 30000 });

    // Dismiss welcome dialog if present
    const skipBtn = page.getByRole('button', { name: /Skip for Now/i });
    if (await skipBtn.isVisible()) {
        console.log('Dismissing welcome dialog...');
        await skipBtn.click();
        await page.waitForTimeout(500);
    }

    console.log('Taking screenshot of selection step...');
    await page.screenshot({ path: '/tmp/step1_protocol_selection.png', fullPage: true });

    // Check if any protocols are listed
    const protocolCount = await page.locator('app-protocol-card').count();
    console.log(`Found ${protocolCount} protocol cards`);

    if (protocolCount > 0) {
        const firstCard = page.locator('app-protocol-card').first();
        await firstCard.click();
        console.log('Selected first protocol');

        await page.waitForTimeout(500);
        await page.screenshot({ path: '/tmp/step1_protocol_selected.png', fullPage: true });

        // Click Continue
        await page.getByRole('button', { name: /Continue/i }).click();
        console.log('Clicked Continue to Parameters');
        await page.waitForTimeout(500);
        await page.screenshot({ path: '/tmp/step2_parameters.png', fullPage: true });

        await page.getByRole('button', { name: /Continue/i }).click();
        console.log('Clicked Continue to Machines');
        await page.waitForTimeout(500);
        await page.screenshot({ path: '/tmp/step3_machines.png', fullPage: true });

        await page.getByRole('button', { name: /Continue/i }).click();
        console.log('Clicked Continue to Assets');
        await page.waitForTimeout(500);
        await page.screenshot({ path: '/tmp/step4_assets.png', fullPage: true });

        await page.getByRole('button', { name: /Continue/i }).click();
        console.log('Clicked Continue to Deck/Review');
        await page.waitForTimeout(500);
        await page.screenshot({ path: '/tmp/step5_review.png', fullPage: true });
    }
});
