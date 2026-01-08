import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class ExecutionMonitorPage extends BasePage {
    readonly statusIndicator: Locator;
    readonly simulationMachineText: Locator;

    constructor(page: Page) {
        super(page, '/app/monitor'); // or dynamic URL
        this.statusIndicator = page.locator('.status-indicator'); // Adjust selector
        this.simulationMachineText = page.locator('text=Simulation Machine');
    }

    async verifyStatus(statusText: string | RegExp) {
        // Monitor might show "Running", "Completed", etc.
        // Using a broad text search in the monitor area if specific selector is unknown
        await expect(this.page.locator('app-run-detail')).toContainText(statusText, { timeout: 15000 });
    }

    async verifySimulationMachine() {
        await expect(this.simulationMachineText.or(this.page.locator('text=sim-machine'))).toBeVisible();
    }
}
