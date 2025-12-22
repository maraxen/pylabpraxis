import { Page, Locator } from '@playwright/test';

export abstract class BasePage {
    protected page: Page;
    readonly url: string;

    constructor(page: Page, url: string = '/') {
        this.page = page;
        this.url = url;
    }

    async goto() {
        await this.page.goto(this.url);
    }

    async getTitle(): Promise<string> {
        return await this.page.title();
    }

    // Common elements
    get header(): Locator {
        return this.page.locator('mat-toolbar');
    }
}
