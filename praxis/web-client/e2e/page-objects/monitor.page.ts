import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

interface RunMeta {
    runName: string;
    runId: string;
}

export class ExecutionMonitorPage extends BasePage {
    private readonly liveHeader: Locator;
    private readonly statusChip: Locator;
    private readonly runInfoCard: Locator;
    private readonly logPanel: Locator;
    private readonly historyTable: Locator;

    constructor(page: Page) {
        super(page, '/app/monitor');
        this.liveHeader = page.getByRole('heading', { name: /Execution Monitor/i }).first();
        this.statusChip = page.locator('mat-chip');
        this.runInfoCard = page.locator('mat-card').filter({ hasText: 'Run ID:' }).first();
        this.logPanel = page.locator('mat-card').filter({ hasText: 'Execution Log' }).locator('.font-mono, .bg-gray-900').first();
        this.historyTable = page.locator('app-run-history-table table');
    }

    async waitForLiveDashboard() {
        await this.liveHeader.waitFor({ state: 'visible', timeout: 20000 });
        await this.runInfoCard.waitFor({ state: 'visible' });
    }

    async captureRunMeta(): Promise<RunMeta> {
        await this.runInfoCard.waitFor({ state: 'visible' });
        const runName = (await this.runInfoCard.locator('mat-card-title').textContent())?.trim() || 'Protocol Run';
        const subtitle = await this.runInfoCard.locator('mat-card-subtitle').innerText();
        const runId = subtitle.replace('Run ID:', '').trim();
        return { runName, runId };
    }

    async waitForStatus(expected: string | RegExp, timeout = 60000) {
        await expect(this.statusChip).toContainText(expected, { timeout });
    }

    async waitForProgressAtLeast(minValue: number) {
        const progressBar = this.page.locator('mat-progress-bar');
        await expect(progressBar).toBeVisible();
        const handle = await progressBar.elementHandle();
        await this.page.waitForFunction(
            (bar, value) => {
                if (!bar) return false;
                const current = parseFloat(bar.getAttribute('aria-valuenow') || '0');
                return current >= value;
            },
            handle,
            minValue,
            { timeout: 60000 }
        );
    }

    async waitForLogEntry(text: string) {
        await expect(this.logPanel).toContainText(text, { timeout: 60000 });
    }

    async navigateToHistory() {
        await this.page.goto('/app/monitor', { waitUntil: 'domcontentloaded' });
        await this.historyTable.waitFor({ state: 'visible', timeout: 20000 });
    }

    async waitForHistoryRow(runName: string): Promise<Locator> {
        const row = this.historyTable.locator('tbody tr').filter({ hasText: runName }).first();
        await expect(row).toBeVisible({ timeout: 30000 });
        return row;
    }

    async reloadHistory() {
        await this.page.reload({ waitUntil: 'domcontentloaded' });
        await this.historyTable.waitFor({ state: 'visible', timeout: 20000 });
    }

    async openRunDetail(runName: string) {
        const row = await this.waitForHistoryRow(runName);
        await row.click();
        await this.page.waitForURL(/\/app\/monitor\/.+$/, { waitUntil: 'domcontentloaded' });
    }

    async openRunDetailById(runId: string) {
        await this.page.goto(`/app/monitor/${runId}`, { waitUntil: 'domcontentloaded' });
    }

    async expectRunDetailVisible(runName: string) {
        const heading = this.page.locator('h1').first();
        await expect(heading).toContainText(runName, { timeout: 20000 });
        await expect(this.page.locator('.timeline-container')).toBeVisible();
    }
}
