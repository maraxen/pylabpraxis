import { Page, Locator, TestInfo } from '@playwright/test';

/**
 * Base page object for E2E tests with worker-indexed DB isolation.
 * 
 * KEY CHANGE: Supports parallel test execution via worker-specific database files.
 * Each Playwright worker gets its own database (praxis-worker-{index}.db) to prevent
 * OPFS contention between parallel tests.
 */
export abstract class BasePage {
    protected page: Page;
    protected testInfo?: TestInfo;
    readonly url: string;

    /**
     * @param page - Playwright page
     * @param url - Base URL for this page
     * @param testInfo - Optional TestInfo for worker index (enables isolated DBs)
     */
    constructor(page: Page, url: string = '/', testInfo?: TestInfo) {
        this.page = page;
        this.url = url;
        this.testInfo = testInfo;
    }

    /**
     * Navigate to this page with proper mode and database isolation.
     * 
     * Database Isolation Strategy:
     * - If testInfo is provided, uses worker-indexed database name
     * - This prevents race conditions when tests run in parallel
     */
    async goto() {
        let targetUrl = this.url;

        // Ensure mode=browser is set
        if (!targetUrl.includes('mode=')) {
            targetUrl += `${targetUrl.includes('?') ? '&' : '?'}mode=browser`;
        }

        // Add worker-indexed database name for isolation
        if (this.testInfo && !targetUrl.includes('dbName=')) {
            const dbName = `praxis-worker-${this.testInfo.workerIndex}`;
            targetUrl += `${targetUrl.includes('?') ? '&' : '?'}dbName=${dbName}`;
            console.log(`[BasePage] Worker ${this.testInfo.workerIndex} using DB: ${dbName}`);
        }

        // Add resetdb unless explicitly set
        if (!targetUrl.includes('resetdb=')) {
            targetUrl += `${targetUrl.includes('?') ? '&' : '?'}resetdb=1`;
        }

        await this.page.goto(targetUrl, { waitUntil: 'domcontentloaded' });

        // Wait for SqliteService to be ready before returning
        // This is crucial for browser mode where DB init takes time
        if (targetUrl.includes('mode=browser')) {
            await this.page.waitForFunction(
                () => {
                    const sqliteService = (window as any).sqliteService;
                    // Check if service exists and isReady$ has emitted true
                    return sqliteService && sqliteService.isReady$?.getValue() === true;
                },
                null,
                { timeout: 60000 }
            );
        }
    }

    async getTitle(): Promise<string> {
        return await this.page.title();
    }

    async waitForOverlay(options: { timeout?: number; dismissWithEscape?: boolean } = {}): Promise<void> {
        const { timeout = 10000, dismissWithEscape = true } = options;
        const overlay = this.page.locator('.cdk-overlay-backdrop');

        // Try to wait for overlay to disappear naturally
        try {
            await overlay.waitFor({ state: 'hidden', timeout });
        } catch (e) {
            console.log('[Test] Caught (Overlay check):', (e as Error).message);
            // Overlay didn't disappear in time
            if (dismissWithEscape) {
                console.log('[Base] Overlay persisted, attempting Escape key dismiss...');
                await this.page.keyboard.press('Escape');
                // Wait for overlay to hide after escape
                await overlay.waitFor({ state: 'hidden', timeout: 2000 }).catch((e) => {
                    console.log('[Test] Silent catch (Overlay still visible):', e);
                });
            }
        }
    }
}
