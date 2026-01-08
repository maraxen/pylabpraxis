import { Page, Locator } from '@playwright/test';

export abstract class BasePage {
    protected page: Page;
    readonly url: string;

    constructor(page: Page, url: string = '/') {
        this.page = page;
        this.url = url;
    }

    async goto() {
        await this.page.goto(this.url, { waitUntil: 'domcontentloaded' });
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
