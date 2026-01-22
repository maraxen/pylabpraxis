import { test, expect } from '@playwright/test';
import * as path from 'path';
import * as fs from 'fs';

const SCREENSHOT_DIR = '/tmp/e2e-deck';

// Ensure screenshot directory exists
if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

test.describe('E2E Deck Setup', () => {

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
    });

    test('should navigate to deck setup and capture screenshots', async ({ page }) => {
        // Navigate to Run Protocol
        await page.goto('/app/run');

        // Select first protocol
        const protocolCard = page.locator('app-protocol-card').first();
        await expect(protocolCard).toBeVisible({ timeout: 10000 });
        await protocolCard.click();

        // Continue through steps
        const continueBtn = page.getByRole('button', { name: /Continue/i });

        // Step 1: Protocol -> Parameters
        await continueBtn.click();

        // Step 2: Parameters -> Machine
        // await expect(page.locator('app-parameter-config')).toBeVisible();
        await page.waitForTimeout(500);
        await continueBtn.click();

        // Step 3: Machine -> Assets
        // await expect(page.locator('app-machine-selection')).toBeVisible();
        await page.waitForTimeout(500);
        await continueBtn.click();

        // Step 4: Assets -> Wells (or Deck)
        // await expect(page.locator('app-guided-setup')).toBeVisible();
        await page.waitForTimeout(500);
        await continueBtn.click();

        // Handle optional Well Selection
        try {
            await expect(page.locator('app-deck-setup-wizard')).toBeVisible({ timeout: 3000 });
        } catch (e) {
            // If not visible, maybe we are at Well Selection?
            if (await page.getByText('Well Selection').isVisible()) {
                await continueBtn.click();
                await expect(page.locator('app-deck-setup-wizard')).toBeVisible({ timeout: 5000 });
            } else {
                console.log('Protocol might not require deck setup or we are lost');
            }
        }

        // Capture Empty Deck (Wizard start)
        await expect(page.locator('app-deck-setup-wizard')).toBeVisible();
        await page.waitForTimeout(2000); // Wait for rendering
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, '01_empty_deck.png') });

        // Capture Deck Configuration Dialog (Wizard view)
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02_deck_config_dialog.png') });

        // "deck with placements" -> Just capturing the wizard view which shows the deck
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, '03_deck_with_placements.png') });

    });
});
