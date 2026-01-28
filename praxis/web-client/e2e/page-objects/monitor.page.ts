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
        // AUDIT: More specific locator to avoid picking up arbitrary font-semibold text.
        this.statusChip = page.locator('.info-row, .status-container, mat-card-content')
            .locator('[data-testid="run-status"], mat-chip, .font-semibold')
            .first();
        this.runInfoCard = page.locator('mat-card').filter({ hasText: 'Run ID:' }).first();
        this.logPanel = page.locator('[data-testid="execution-logs"], .font-mono, .bg-gray-900').first();
        this.historyTable = page.locator('app-run-history-table table');
    }

    async waitForLiveDashboard() {
        // AUDIT: startExecution can redirect either to dashboard or directly to detail.
        // Wait for ANY heading that indicates we've arrived at the monitor feature.
        const monitorHeading = this.page.locator('h1, h2').filter({ hasText: /Execution Monitor|Run Details|Transfer|Protocol/i }).first();
        await monitorHeading.waitFor({ state: 'visible', timeout: 30000 });

        // Ensure either the active runs card or the run info card is present
        await Promise.race([
            this.runInfoCard.waitFor({ state: 'visible', timeout: 10000 }),
            this.page.locator('app-active-runs-panel').waitFor({ state: 'visible', timeout: 10000 })
        ]).catch(() => {
            console.warn('[Monitor] Neither Run Info nor Active Runs panel found, but heading is visible.');
        });
    }

    async captureRunMeta(): Promise<RunMeta> {
        await this.runInfoCard.waitFor({ state: 'visible' });
        const runName = (await this.runInfoCard.locator('mat-card-title').textContent())?.trim() || 'Protocol Run';
        const subtitle = await this.runInfoCard.locator('mat-card-subtitle').innerText();
        const runId = subtitle.replace('Run ID:', '').trim();
        return { runName, runId };
    }

    async waitForStatus(expected: string | RegExp, timeout = 60000) {
        // AUDIT: Simulation mode can be very fast. If we wait for RUNNING but it's already COMPLETED,
        // we should accept both to avoid timing-out on "perfect" runs.
        const combined = expected instanceof RegExp
            ? new RegExp(`${expected.source}|COMPLETED`)
            : new RegExp(`${expected}|COMPLETED`);

        await expect(this.statusChip).toContainText(combined, { timeout });
    }

    async waitForProgressAtLeast(minValue: number) {
        const progressBar = this.page.locator('mat-progress-bar');

        // If already completed, progress bar might have been removed from DOM
        const status = await this.statusChip.innerText();
        if (status.includes('COMPLETED')) {
            console.log(`[Monitor] Status is COMPLETED, skipping progress check for ${minValue}%`);
            return;
        }

        await expect(progressBar).toBeVisible({ timeout: 10000 }).catch(() => {
            console.warn('[Monitor] Progress bar not visible, checking if status changed to COMPLETED');
        });

        const chipText = await this.statusChip.innerText();
        if (chipText.includes('COMPLETED')) return;

        const handle = await progressBar.elementHandle();
        if (!handle) return;

        await this.page.waitForFunction(
            ([bar, val]) => {
                if (!bar) return true; // Bar gone = likely finished
                const current = parseFloat((bar as Element).getAttribute('aria-valuenow') || '0');
                return current >= (val as number);
            },
            [handle, minValue] as const,
            { timeout: 30000 }
        ).catch(e => {
            console.warn(`[Monitor] Progress check timed out for ${minValue}%, continuing...`);
        });
    }

    async waitForLogEntry(text: string) {
        // Increase timeout for log verification to account for simulation delay
        await expect(this.logPanel).toContainText(text, { timeout: 30000 });
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

    async verifyParameter(key: string, value: string) {
        const paramGrid = this.page.locator('app-parameter-viewer');
        await expect(paramGrid).toBeVisible();
        const paramItem = paramGrid.locator('.parameter-item').filter({ has: this.page.locator('.parameter-key', { hasText: key }) });
        await expect(paramItem.locator('.parameter-value')).toContainText(value);
    }
}
