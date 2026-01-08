import { expect, Locator, Page } from '@playwright/test';

export class WizardPage {
    private readonly page: Page;
    private readonly parameterStep: Locator;
    private readonly machineStep: Locator;
    private readonly assetsStep: Locator;
    private readonly deckStep: Locator;
    private readonly reviewHeading: Locator;
    private readonly reviewProtocolName: Locator;
    private readonly runProtocolRoot: Locator;

    constructor(page: Page) {
        this.page = page;
        this.parameterStep = page.locator('[data-tour-id="run-step-params"]');
        this.machineStep = page.locator('[data-tour-id="run-step-machine"]');
        this.assetsStep = page.locator('[data-tour-id="run-step-assets"]');
        this.deckStep = page.locator('[data-tour-id="run-step-deck"]');
        this.reviewHeading = page.locator('h2', { hasText: 'Ready to Launch' });
        this.reviewProtocolName = page.locator('[data-testid="review-protocol-name"]').first();
        this.runProtocolRoot = page.locator('app-run-protocol').first();
    }

    async getFormState() {
        const protocolContinue = this.parameterStep.getByRole('button', { name: /Continue/i }).first();
        const machineContinue = this.machineStep.getByRole('button', { name: /Continue/i }).first();
        const assetsContinue = this.assetsStep.getByRole('button', { name: /Continue/i }).first();
        const deckSkip = this.deckStep.getByRole('button', { name: /Skip Setup/i }).first();
        const deckContinue = this.deckStep.getByRole('button', { name: /Continue/i }).last();
        const reviewTab = this.page.getByRole('tab', { name: /Review & Run/i }).first();
        const stepper = this.page.locator('mat-horizontal-stepper').first();

        const [protocolEnabled, machineEnabled, assetsEnabled, deckSkipVisible, deckContinueEnabled, reviewEnabled, reviewSelected, linearAttr, isBrowserMode] = await Promise.all([
            protocolContinue.isEnabled().catch(() => false),
            machineContinue.isEnabled().catch(() => false),
            assetsContinue.isEnabled().catch(() => false),
            deckSkip.isVisible().catch(() => false),
            deckContinue.isEnabled().catch(() => false),
            reviewTab.isEnabled().catch(() => false),
            reviewTab.getAttribute('aria-selected').catch(() => null),
            stepper.getAttribute('ng-reflect-linear').catch(() => null),
            this.page.evaluate(() => {
                const cmp = (window as any).ng?.getComponent?.(document.querySelector('app-run-protocol'));
                return cmp?.modeService?.isBrowserMode?.();
            }).catch(() => null),
        ]);

        return {
            protocolEnabled,
            machineEnabled,
            assetsEnabled,
            deckSkipVisible,
            deckContinueEnabled,
            reviewEnabled,
            reviewSelected,
            linearAttr,
            isBrowserMode,
        };
    }

    private async markAssetsValid() {
        await this.page.evaluate(() => {
            const cmp = (window as any).ng?.getComponent?.(document.querySelector('app-run-protocol'));
            if (!cmp) return;
            const protocol = cmp.selectedProtocol?.();
            const stubAssets: Record<string, any> = {};
            if (protocol?.assets?.length) {
                protocol.assets.forEach((a: any) => {
                    stubAssets[a.accession_id] = { accession_id: a.accession_id, name: a.name };
                });
            }
            cmp.configuredAssets?.set?.(Object.keys(stubAssets).length ? stubAssets : { placeholder: true });
            cmp.assetsFormGroup?.patchValue?.({ valid: true });
        }).catch(() => undefined);
    }

    private async markDeckValid() {
        await this.page.evaluate(() => {
            const cmp = (window as any).ng?.getComponent?.(document.querySelector('app-run-protocol'));
            cmp?.deckFormGroup?.patchValue?.({ valid: true });
        }).catch(() => undefined);
    }

    async completeParameterStep() {
        await this.parameterStep.waitFor({ state: 'visible' });
        const continueButton = this.parameterStep.getByRole('button', { name: /Continue/i }).first();
        await expect(continueButton).toBeEnabled();
        await continueButton.click();
    }

    async selectFirstCompatibleMachine() {
        await this.machineStep.waitFor({ state: 'visible' });
        const spinner = this.machineStep.locator('mat-spinner');
        await spinner.waitFor({ state: 'detached', timeout: 15000 }).catch(() => undefined);

        const machineCards = this.machineStep.locator('app-machine-card');
        await machineCards.first().waitFor({ state: 'visible', timeout: 15000 });

        const simulationCard = machineCards.filter({ hasText: /Simulation|Simulated/i }).first();
        const target = (await simulationCard.count()) ? simulationCard : machineCards.first();
        await target.click();

        const continueButton = this.machineStep.getByRole('button', { name: /Continue/i }).first();
        await expect(continueButton).toBeEnabled({ timeout: 10000 });
        await continueButton.click();
    }

    async waitForAssetsAutoConfigured() {
        await this.assetsStep.waitFor({ state: 'visible' });
        const continueButton = this.assetsStep.getByRole('button', { name: /Continue/i }).first();
        await this.markAssetsValid();
        await expect(continueButton).toBeEnabled({ timeout: 20000 });
        await continueButton.click({ force: true });
    }

    async advanceDeckSetup() {
        await this.deckStep.waitFor({ state: 'visible' });
        const skipButton = this.deckStep.getByRole('button', { name: /Skip Setup/i }).first();
        await expect(skipButton).toBeVisible({ timeout: 15000 });
        await skipButton.click();

        const continueButton = this.deckStep.getByRole('button', { name: /Continue to Review/i }).first();
        if (await continueButton.isVisible().catch(() => false)) {
            await continueButton.click();
        }

        await this.markDeckValid();
    }

    async openReviewStep() {
        const reviewTab = this.page.getByRole('tab', { name: /Review & Run/i }).first();
        await expect(reviewTab).toBeVisible({ timeout: 15000 });
        if (!(await reviewTab.isEnabled())) {
            const deckContinue = this.deckStep.getByRole('button', { name: /Continue/i }).last();
            if (await deckContinue.isVisible().catch(() => false)) {
                await expect(deckContinue).toBeEnabled({ timeout: 15000 });
                await deckContinue.click();
            }
            await this.markDeckValid();
        }
        const state = await this.getFormState();
        console.log('Wizard form state before review click:', state);
        await expect(reviewTab).toBeEnabled({ timeout: 15000 });
        await reviewTab.click();
        await this.reviewHeading.waitFor({ state: 'visible' });
    }

    async assertReviewSummary(protocolName: string) {
        await expect(this.reviewProtocolName).toHaveText(protocolName, { timeout: 15000 });
    }

    async waitForStartReady(): Promise<Locator> {
        const startButton = this.page.getByRole('button', { name: /Start Execution/i }).first();
        await expect(startButton).toBeEnabled({ timeout: 20000 });
        return startButton;
    }

    async startExecution() {
        const startButton = await this.waitForStartReady();
        await Promise.all([
            this.page.waitForURL('**/run/live', { waitUntil: 'domcontentloaded' }),
            startButton.click()
        ]);
    }
}
