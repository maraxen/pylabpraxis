import { Page, Locator } from '@playwright/test';

export abstract class BasePage {
    protected page: Page;
    readonly url: string;

    constructor(page: Page, url: string = '/') {
        this.page = page;
        this.url = url;
    }

    async goto() {
        const hasModeParam = this.url.includes('mode=');
        const hasResetDbParam = this.url.includes('resetdb=');

        let targetUrl = this.url;

        if (!hasModeParam) {
            targetUrl += `${targetUrl.includes('?') ? '&' : '?'}mode=browser`;
        }

        if (!hasResetDbParam) {
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
                { timeout: 30000 }
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
        } catch {
            // Overlay didn't disappear in time
            if (dismissWithEscape) {
                console.log('[Base] Overlay persisted, attempting Escape key dismiss...');
                await this.page.keyboard.press('Escape');
                // Wait for overlay to hide after escape
                await overlay.waitFor({ state: 'hidden', timeout: 2000 }).catch(() => {
                    console.warn('[Base] Overlay still visible after Escape');
                });
            }
        }
    }
}
