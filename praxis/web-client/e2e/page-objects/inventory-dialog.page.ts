import { Page, Locator, expect } from '@playwright/test';

/**
 * Page Object Model for the Inventory Dialog.
 *
 * Handles the "Browse & Add" workflow for adding assets to the playground:
 * - Type selection (Machine, Consumable, etc.)
 * - Category filtering
 * - Asset list navigation
 */
export class InventoryDialogPage {
    readonly page: Page;
    readonly dialog: Locator;
    readonly browseTab: Locator;
    readonly machineTypeCard: Locator;
    readonly consumableTypeCard: Locator;
    readonly continueButton: Locator;
    readonly categoryChips: Locator;
    readonly assetList: Locator;
    readonly emptyState: Locator;
    readonly addButton: Locator;

    constructor(page: Page) {
        this.page = page;
        this.dialog = page.getByRole('dialog').filter({ hasText: /inventory/i });
        this.browseTab = page.getByRole('tab', { name: /browse.*add/i });
        this.machineTypeCard = page.getByRole('button', { name: /machine/i });
        this.consumableTypeCard = page.getByRole('button', { name: /consumable/i });
        this.continueButton = page.getByRole('button', { name: /continue/i });
        this.categoryChips = page.getByRole('listbox').locator('[role="option"]');
        this.assetList = page.getByRole('listbox', { name: /assets/i });
        this.emptyState = page.locator('[data-testid="empty-state"], .empty-state');
        this.addButton = page.getByRole('button', { name: /^add$/i });
    }

    /**
     * Wait for the dialog to be visible and ready.
     */
    async waitForReady(timeout = 10000): Promise<void> {
        await expect(this.dialog).toBeVisible({ timeout });
    }

    /**
     * Select the "Browse & Add" tab.
     */
    async selectBrowseTab(): Promise<void> {
        await this.browseTab.click();
        // Wait for type cards to appear
        await expect(this.machineTypeCard.or(this.consumableTypeCard).first()).toBeVisible({ timeout: 5000 });
    }

    /**
     * Select the Machine asset type.
     */
    async selectMachineType(): Promise<void> {
        await this.machineTypeCard.click();
        await expect(this.continueButton).toBeEnabled({ timeout: 5000 });
    }

    /**
     * Select the Consumable asset type.
     */
    async selectConsumableType(): Promise<void> {
        await this.consumableTypeCard.click();
        await expect(this.continueButton).toBeEnabled({ timeout: 5000 });
    }

    /**
     * Get all available category names.
     */
    async getCategories(): Promise<string[]> {
        await expect(this.categoryChips.first()).toBeVisible({ timeout: 5000 });
        return this.categoryChips.allInnerTexts();
    }

    /**
     * Select a category by name.
     */
    async selectCategory(name: string): Promise<void> {
        const chip = this.categoryChips.filter({ hasText: name });
        await chip.click();
    }

    /**
     * Click the Continue button to advance to the next step.
     */
    async continue(): Promise<void> {
        await expect(this.continueButton).toBeEnabled({ timeout: 5000 });
        await this.continueButton.click();
    }

    /**
     * Wait for the asset list to be visible.
     */
    async waitForAssetList(timeout = 10000): Promise<void> {
        await expect(this.assetList).toBeVisible({ timeout });
    }

    /**
     * Select an asset by name from the asset list.
     */
    async selectAsset(assetName: string | RegExp): Promise<void> {
        const asset = this.page.getByRole('option', { name: assetName });
        await asset.click();
    }

    /**
     * Add the currently selected asset.
     */
    async addSelectedAsset(): Promise<void> {
        await expect(this.addButton).toBeEnabled({ timeout: 5000 });
        await this.addButton.click();
    }

    /**
     * Assert that the empty state is visible (no assets found).
     */
    async assertEmptyState(): Promise<void> {
        await expect(this.emptyState).toBeVisible({ timeout: 5000 });
    }

    /**
     * Close the dialog (via Escape or close button).
     */
    async close(): Promise<void> {
        await this.page.keyboard.press('Escape');
        await expect(this.dialog).toBeHidden({ timeout: 3000 });
    }
}
