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

    async waitForOverlay() {
        const overlay = this.page.locator('.cdk-overlay-backdrop');
        if (await overlay.isVisible()) {
            await overlay.waitFor({ state: 'hidden', timeout: 10000 });
        }
    }
}
