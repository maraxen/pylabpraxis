import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class WelcomePage extends BasePage {
    readonly getStartedButton: Locator;
    readonly skipButton: Locator;
    readonly splashScreen: Locator;

    constructor(page: Page) {
        super(page, '/');
        this.getStartedButton = page.getByRole('button', { name: /Start Tutorial/i });
        this.skipButton = page.getByRole('button', { name: /Skip/i });
        this.splashScreen = page.getByRole('heading', { name: /Welcome to Praxis/i });
    }

    async handleSplashScreen() {
        // Wait briefly to see if splash appears
        try {
            await this.splashScreen.waitFor({ state: 'visible', timeout: 5000 });
            // Verifying it appeared, now dismiss it
            if (await this.skipButton.isVisible()) {
                await this.skipButton.click();
            } else if (await this.getStartedButton.isVisible()) {
                await this.getStartedButton.click();
            }
        } catch (e) {
            // Splash might not appear if already visited or not in that mode
            console.log('Splash screen skipped or not present');
        }
    }

    async verifyDashboardLoaded() {
        await expect(this.page.locator('.sidebar-rail')).toBeVisible({ timeout: 10000 });
    }
}
