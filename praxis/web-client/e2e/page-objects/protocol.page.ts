import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class ProtocolPage extends BasePage {
    readonly runProtocolLink: Locator;
    readonly protocolList: Locator;
    readonly startExecutionButton: Locator;

    constructor(page: Page) {
        super(page, '/protocols');
        this.runProtocolLink = page.getByRole('link', { name: /Run Protocol/i }); // Adjust based on actual nav, maybe '/app/run' direct?
        // Actually, user might click "Run" from list or go to "Run Protocol" wizard page.
        // Let's assume navigating to /app/protocols then clicking Run on a row, OR /app/run
    }

    async selectProtocol(name: string) {
        // Option 1: Click "Run" on a protocol in the library list
        await this.goto();
        // Assuming table structure
        const row = this.page.locator('tr', { hasText: name });
        await row.locator('button').filter({ hasText: 'play_arrow' }).click(); // Use icon name or similar
    }

    async navigateThroughWizard() {
        // Wizard steps: Protocol -> Parameters -> Deck -> Review
        // We just click "Continue" or "Next" until we see "Start Execution"

        // Wait for wizard to load
        await expect(this.page.locator('app-run-protocol')).toBeVisible();

        // Loop to click "Next" / "Continue"
        // Heuristic: Click visible "Next" or "Continue" buttons
        for (let i = 0; i < 5; i++) {
            // Check if "Start Execution" is visible, if so, break
            // Using catch to handle non-existence without erroring
            if (await this.page.locator('button:has-text("Start Execution")').isVisible()) {
                break;
            }

            const nextBtn = this.page.locator('button').filter({ hasText: /Next|Continue/i }).first();
            if (await nextBtn.isVisible()) {
                await nextBtn.click();
                await this.page.waitForTimeout(500); // Animations
            } else {
                break; // No more next buttons
            }
        }
    }

    async startExecution() {
        const startBtn = this.page.locator('button:has-text("Start Execution")');
        await expect(startBtn).toBeVisible();
        await expect(startBtn).toBeEnabled();
        await startBtn.click();
    }
}
