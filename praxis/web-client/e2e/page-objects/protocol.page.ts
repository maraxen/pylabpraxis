import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class ProtocolPage extends BasePage {
    readonly protocolStep: Locator;
    readonly protocolCards: Locator;
    readonly summaryTitle: Locator;

    constructor(page: Page) {
        super(page, '/app/run');
        this.protocolStep = page.locator('[data-tour-id="run-step-protocol"]');
        this.protocolCards = page.locator('app-protocol-card');
        this.summaryTitle = this.protocolStep.locator('h2');
    }

    private async dismissOverlays() {
        const dismissButtons = this.page
            .locator('.cdk-overlay-container button')
            .filter({ hasText: /Close|Dismiss|Got it|OK|Continue/i });
        if (await dismissButtons.count()) {
            await dismissButtons.first().click({ timeout: 2000 }).catch(() => undefined);
        }
        await this.page.keyboard.press('Escape').catch(() => undefined);
    }

    async goto() {
        await super.goto();
        await this.protocolStep.waitFor({ state: 'visible' });
        await this.protocolCards.first().waitFor({ state: 'visible', timeout: 30000 });
    }

    async ensureSimulationMode() {
        const simulationToggle = this.page.getByRole('button', { name: /^Simulation$/i }).first();
        if (await simulationToggle.count()) {
            const pressed = await simulationToggle.getAttribute('aria-pressed');
            if (pressed !== 'true') {
                await simulationToggle.click();
            }
        }
    }

    async selectProtocolByName(name: string): Promise<string> {
        const card = this.protocolCards.filter({ hasText: name }).first();
        await expect(card, `Protocol card for ${name} should be visible`).toBeVisible({ timeout: 15000 });
        await card.click();
        await this.assertProtocolSelected(name);
        return name;
    }

    async selectFirstProtocol(): Promise<string> {
        const firstCard = this.protocolCards.first();
        await firstCard.waitFor({ state: 'visible' });
        const name = (await firstCard.locator('mat-card-title').textContent())?.trim() || 'Protocol';
        await this.dismissOverlays();
        await firstCard.click({ trial: true }).catch(() => undefined);
        await firstCard.click({ force: true });
        await this.assertProtocolSelected(name);
        return name;
    }

    async assertProtocolSelected(expectedName: string) {
        await expect(this.summaryTitle, 'Selected protocol summary should appear').toContainText(expectedName, {
            timeout: 15000
        });
    }

    async continueFromSelection() {
        const continueButton = this.protocolStep.getByRole('button', { name: /Continue/i }).last();
        await expect(continueButton).toBeEnabled({ timeout: 15000 });
        await continueButton.click();
    }
}
