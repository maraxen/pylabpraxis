import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class SettingsPage extends BasePage {
    readonly exportButton: Locator;
    readonly importButton: Locator;
    readonly importInput: Locator;
    readonly clearDataButton: Locator;

    constructor(page: Page) {
        super(page, '/settings');
        this.exportButton = page.getByRole('button', { name: /Export/i });
        this.importButton = page.getByRole('button', { name: /Import/i });
        this.importInput = page.locator('input[type="file"]');
        this.clearDataButton = page.getByRole('button', { name: /Clear Data/i }); // Verify if this exists or we need to manually clear storage
    }

    async exportDatabase() {
        const downloadPromise = this.page.waitForEvent('download');
        await this.exportButton.click();
        const download = await downloadPromise;
        return await download.path();
    }

    async importDatabase(filePath: string) {
        // Determine if we need to click a button to trigger file input or if input is always there
        // Usually hidden input
        await this.importInput.setInputFiles(filePath);
        // Might need to confirm a dialog
        const confirmBtn = this.page.getByRole('button', { name: /Confirm|Yes|Import/i });
        if (await confirmBtn.isVisible()) {
            await confirmBtn.click();
        }
        await this.page.waitForLoadState('domcontentloaded');
    }

    async resetState() {
        // If there's a UI button
        if (await this.clearDataButton.isVisible()) {
            await this.clearDataButton.click();
            await this.page.getByRole('button', { name: /Confirm/i }).click();
        } else {
            // Manual clear
            await this.page.evaluate(() => {
                localStorage.clear();
                // IndexDB clear is harder via evaluate without specialized code or library
                // But for "Browser Mode Specifics", we might just rely on import overwriting existing data
            });
        }
    }
}
