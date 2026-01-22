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
            .locator('.cdk-overlay-container button, .mat-mdc-dialog-container button')
            .filter({ hasText: /Close|Dismiss|Got it|OK|Continue|Skip|Start/i });
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
        await this.dismissOverlays();
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

    async navigateToProtocols() {
        await this.goto();
    }

    async selectProtocol(name: string) {
        await this.selectProtocolByName(name);
        await this.continueFromSelection();
    }

    async configureParameter(name: string, value: string) {
        // Assuming we are on the parameters step
        const paramInput = this.page.getByLabel(name).or(this.page.locator(`input[name="${name}"]`)).first();
        if (await paramInput.isVisible()) {
            await paramInput.fill(value);
        } else {
            console.log(`Parameter ${name} not found or not visible, skipping.`);
        }
    }

    async advanceToReview() {
        // This is a helper to move through the wizard steps
        // We might need to import WizardPage or duplicate some logic here if we want to be strictly independent,
        // but ideally we should reuse. Since I cannot easily inject WizardPage here without changing the constructor signature significantly 
        // or instantiating it internally, I'll instantiate it internally.
        const { WizardPage } = await import('./wizard.page');
        const wizard = new WizardPage(this.page);

        await wizard.completeParameterStep();
        await wizard.selectFirstCompatibleMachine();
        await wizard.waitForAssetsAutoConfigured();
        await wizard.advanceDeckSetup();
        await wizard.openReviewStep();
    }

    async startExecution() {
        const { WizardPage } = await import('./wizard.page');
        const wizard = new WizardPage(this.page);
        await wizard.startExecution();
    }

    async getExecutionStatus(): Promise<string> {
        const { ExecutionMonitorPage } = await import('./monitor.page');
        const monitor = new ExecutionMonitorPage(this.page);
        // We assume we are on the monitor page now
        const statusChip = this.page.locator('mat-chip'); // Using locator from monitor page logic
        return await statusChip.textContent() || '';
    }

    async waitForCompletion(timeout: number = 300000) { // 5 minutes default
        const { ExecutionMonitorPage } = await import('./monitor.page');
        const monitor = new ExecutionMonitorPage(this.page);
        await monitor.waitForStatus(/(Completed|Succeeded|Finished)/i, timeout);
    }

    async continueFromSelection() {
        const continueButton = this.protocolStep.getByRole('button', { name: /Continue/i }).last();
        await expect(continueButton).toBeEnabled({ timeout: 15000 });
        await continueButton.click();
    }
}
