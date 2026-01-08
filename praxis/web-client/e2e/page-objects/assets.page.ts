import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class AssetsPage extends BasePage {
    readonly addMachineButton: Locator;
    readonly addResourceButton: Locator;
    readonly machinesTab: Locator;
    readonly resourcesTab: Locator;
    readonly registryTab: Locator;
    readonly overviewTab: Locator;
    readonly spatialViewTab: Locator;

    constructor(page: Page) {
        super(page, '/assets');
        this.addMachineButton = page.getByRole('button', { name: /Add Machine/i });
        this.addResourceButton = page.getByRole('button', { name: /Add Resource/i });
        this.machinesTab = page.getByRole('tab', { name: /Machines/i });
        this.resourcesTab = page.getByRole('tab', { name: /Resources/i });
        this.registryTab = page.getByRole('tab', { name: /Registry/i });
        this.overviewTab = page.getByRole('tab', { name: /Overview/i });
        this.spatialViewTab = page.getByRole('tab', { name: /Spatial View/i });
    }

    async navigateToOverview() {
        await this.overviewTab.click();
        await this.page.waitForTimeout(300);
    }

    async navigateToSpatialView() {
        await this.spatialViewTab.click();
        await this.page.waitForTimeout(300);
    }

    async navigateToMachines() {
        await this.machinesTab.click();
        await this.page.waitForTimeout(300);
    }

    async navigateToResources() {
        await this.resourcesTab.click();
        await this.page.waitForTimeout(300);
    }

    async navigateToRegistry() {
        await this.registryTab.click();
        await this.page.waitForTimeout(300);
    }

    /** @deprecated Use navigateToOverview instead */
    async navigateToDashboard() {
        await this.navigateToOverview();
    }

    async createMachine(name: string, typeQuery: string = 'Opentrons') {
        await this.addMachineButton.click();

        const dialog = this.page.getByRole('dialog');
        await expect(dialog).toBeVisible();

        // Step 1: Select Category - wait for categories to load from definitions
        // Categories are dynamically loaded, so we need to wait for them
        const categoryCards = this.page.locator('.category-card');
        await expect(categoryCards.first()).toBeVisible({ timeout: 10000 });

        // Try to find 'Liquid Handling' category or fall back to first available
        const liquidCategory = categoryCards.filter({ hasText: /liquid/i }).first();
        if (await liquidCategory.isVisible({ timeout: 1000 })) {
            await liquidCategory.click();
        } else {
            // Click the first available category
            await categoryCards.first().click();
        }

        // Step 2: Select Model - wait for model list to load
        const definitionItems = this.page.locator('.definition-item');
        await expect(definitionItems.first()).toBeVisible({ timeout: 10000 });

        // Search for specific model if query provided
        const searchInput = this.page.getByPlaceholder(/Filter by name/i);
        if (await searchInput.isVisible({ timeout: 2000 })) {
            await searchInput.fill(typeQuery);
            await this.page.waitForTimeout(500);
        }

        // Select first matching definition
        await definitionItems.first().click();

        // Fill the name field
        await this.page.getByLabel('Instance Name').or(this.page.getByLabel('Name')).fill(name);

        // Click Next to go to Step 3
        const nextBtn = this.page.getByRole('button', { name: /Next/i });
        if (await nextBtn.isVisible({ timeout: 1000 })) {
            await nextBtn.click();
        }

        // Click Finish to complete
        const finishBtn = this.page.getByRole('button', { name: /Finish/i });
        if (await finishBtn.isVisible({ timeout: 2000 })) {
            await finishBtn.click();
        } else {
            // Fallback to Save button
            await this.page.getByRole('button', { name: /Save/i }).click();
        }

        await expect(dialog).not.toBeVisible({ timeout: 5000 });
    }

    async createResource(name: string, modelQuery: string = '96') {
        await this.addResourceButton.click();

        const dialog = this.page.getByRole('dialog');
        await expect(dialog).toBeVisible();

        // Step 1: Select Category
        // Try to click 'plate' category or just the first one
        const categoryCard = this.page.locator('.category-card').first();
        await categoryCard.click();

        // Step 2: Select Model
        await expect(this.page.getByLabel('Resource Model')).toBeVisible();
        await this.page.getByLabel('Resource Model').fill(modelQuery);
        await this.page.waitForTimeout(500);
        await this.page.getByRole('option').first().click();

        await this.page.getByLabel('Name').fill(name);
        await this.page.getByRole('button', { name: /Save Resource/i }).click();
        await expect(dialog).not.toBeVisible();
    }

    /**
     * Delete a machine by name. Handles the browser confirm() dialog.
     * Must be called from the Machines tab.
     */
    async deleteMachine(name: string) {
        // Set up dialog handler BEFORE triggering the delete
        this.page.once('dialog', dialog => dialog.accept());

        // Find the row with the machine name and click delete button
        const row = this.page.locator('tr').filter({ hasText: name });
        const deleteBtn = row.getByRole('button', { name: /delete/i }).or(
            row.locator('button[mattooltip*="Delete"]')
        );

        if (await deleteBtn.isVisible({ timeout: 2000 })) {
            await deleteBtn.click();
        } else {
            // Try context menu approach
            const moreBtn = row.getByRole('button').filter({ hasText: /more_vert/i });
            if (await moreBtn.isVisible({ timeout: 1000 })) {
                await moreBtn.click();
                await this.page.getByRole('menuitem', { name: /Delete/i }).click();
            }
        }

        // Wait for the delete operation to complete
        await this.page.waitForTimeout(500);
    }

    /**
     * Delete a resource by name. Handles the browser confirm() dialog.
     * Must be called from the Registry/Resources tab.
     */
    async deleteResource(name: string) {
        // Set up dialog handler BEFORE triggering the delete
        this.page.once('dialog', dialog => dialog.accept());

        // Find the row with the resource name and click delete button
        const row = this.page.locator('tr').filter({ hasText: name });
        const deleteBtn = row.getByRole('button', { name: /delete/i }).or(
            row.locator('button[mattooltip*="Delete"]')
        );

        if (await deleteBtn.isVisible({ timeout: 2000 })) {
            await deleteBtn.click();
        } else {
            // Try context menu approach
            const moreBtn = row.getByRole('button').filter({ hasText: /more_vert/i });
            if (await moreBtn.isVisible({ timeout: 1000 })) {
                await moreBtn.click();
                await this.page.getByRole('menuitem', { name: /Delete/i }).click();
            }
        }

        // Wait for the delete operation to complete
        await this.page.waitForTimeout(500);
    }

    /**
     * Legacy method - use deleteMachine or deleteResource instead
     * @deprecated
     */
    async deleteAsset(name: string) {
        await this.deleteMachine(name);
    }

    // Filter chip interaction
    /**
     * Select a category filter chip by its label text
     */
    async selectCategoryFilter(category: string) {
        const chip = this.page.locator('app-filter-chip').filter({ hasText: new RegExp(category, 'i') });
        await chip.click();
        await this.page.waitForTimeout(300);
    }

    /**
     * Clear all active filters by clicking the clear button
     */
    async clearFilters() {
        const clearBtn = this.page.getByRole('button', { name: /Clear/i }).or(
            this.page.locator('button').filter({ hasText: /clear/i })
        );
        if (await clearBtn.isVisible({ timeout: 1000 })) {
            await clearBtn.click();
            await this.page.waitForTimeout(300);
        }
    }

    /**
     * Type in the search input to filter assets
     */
    async searchAssets(query: string) {
        const searchInput = this.page.getByPlaceholder(/search/i);
        await searchInput.fill(query);
        await this.page.waitForTimeout(300);
    }

    // Count helpers
    /**
     * Get the count of visible machines in the table
     */
    async getMachineCount(): Promise<number> {
        const rows = this.page.locator('table tr').filter({ has: this.page.locator('td') });
        return await rows.count();
    }

    /**
     * Get the count of visible resources in the table
     */
    async getResourceCount(): Promise<number> {
        const rows = this.page.locator('table tr').filter({ has: this.page.locator('td') });
        return await rows.count();
    }

    async verifyAssetVisible(name: string, timeout: number = 5000) {
        await expect(this.page.getByText(name)).toBeVisible({ timeout });
    }

    async verifyAssetNotVisible(name: string, timeout: number = 5000) {
        await expect(this.page.getByText(name)).not.toBeVisible({ timeout });
    }
}
