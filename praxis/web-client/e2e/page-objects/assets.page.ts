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

    /**
     * Helper: Click a result card in the wizard with proper scrolling
     * Uses dialog-context scrolling to handle elements outside viewport
     * 
     * Note: On some viewport sizes, cards can exist in DOM but be outside
     * the visible scroll area of the dialog. We handle this by:
     * 1. Waiting for card count > 0 (not visibility)
     * 2. Using element.scrollIntoView() which respects nested scroll containers
     * 3. Using force click to bypass animation stability checks
     */
    private async selectWizardCard(cardSelector = '.results-grid .praxis-card.result-card', maxRetries = 3): Promise<void> {
        // CRITICAL: Use :visible pseudo-selector to exclude hidden cards from previous wizard steps.
        // The Material Stepper keeps all step content in DOM but hides inactive steps via CSS.
        // Using :visible ensures we only target cards that are actually displayed on screen.
        // This fixes the "Stale Step" locator trap where cards from previous steps are clicked.
        const cards = this.page.locator(`${cardSelector}:visible`);

        // Wait for cards to exist in DOM (not just visible)
        await expect(async () => {
            const count = await cards.count();
            expect(count).toBeGreaterThan(0);
        }).toPass({ timeout: 15000 });

        for (let attempt = 0; attempt < maxRetries; attempt++) {
            try {
                const firstCard = cards.first();

                // Debug: Log the element we're clicking
                const debugInfo = await firstCard.evaluate((el: HTMLElement) => {
                    return {
                        tagName: el.tagName,
                        classList: Array.from(el.classList),
                        hasClickListener: typeof (el as any).onclick === 'function',
                        innerText: el.innerText.substring(0, 50),
                    };
                });
                console.log(`[AssetsPage] Clicking card:`, JSON.stringify(debugInfo));

                // Use native element.click() which Angular handles correctly
                await firstCard.evaluate((el: HTMLElement) => {
                    el.scrollIntoView({ block: 'center', behavior: 'instant' });
                    // Try multiple approaches
                    el.click();  // Native click
                    // Also try dispatching a proper MouseEvent
                    const clickEvent = new MouseEvent('click', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    });
                    el.dispatchEvent(clickEvent);
                });
                await this.page.waitForTimeout(600);

                // Verify selection by checking if Next button is now enabled
                const nextButton = this.page.getByRole('button', { name: /Next/i });
                const isNextEnabled = await nextButton.isEnabled({ timeout: 1000 }).catch(() => false);
                console.log(`[AssetsPage] After click - Next button enabled: ${isNextEnabled}`);
                if (isNextEnabled) {
                    return;
                }

                // If Next is still disabled, try clicking again
                console.log(`[AssetsPage] Card click didn't enable Next (attempt ${attempt + 1}), retrying...`);
            } catch (err) {
                if (attempt === maxRetries - 1) throw err;
                console.log(`[AssetsPage] Card selection error (attempt ${attempt + 1}): ${err}`);
                await this.page.waitForTimeout(500);
            }
        }

        throw new Error(`[AssetsPage] Failed to select card after ${maxRetries} attempts`);
    }

    /**
     * Helper: Click the Next button with stability checks
     */
    private async clickNextButton(): Promise<void> {
        const nextButton = this.page.getByRole('button', { name: /Next/i });
        await expect(nextButton).toBeEnabled({ timeout: 5000 });
        await nextButton.click();
        await this.page.waitForLoadState('domcontentloaded');
        await this.page.waitForTimeout(300); // Allow step transition
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

        // Wait for wizard initialization - the wizard uses setTimeout(0) to auto-advance 
        // when preselectedType is provided, so we need a small delay
        await this.page.waitForTimeout(500);

        // Step 1: Select Asset Type (Machine vs Resource)
        // The type cards have class .type-card - may already be pre-selected
        const machineTypeCard = this.page.locator('.type-card').filter({ hasText: /Machine/i }).first();
        const categoryCards = this.page.locator('.category-card');

        // Check if we're already on Step 2 (Category) - wizard may have auto-advanced
        const alreadyOnCategoryStep = await categoryCards.first().isVisible({ timeout: 1000 }).catch(() => false);

        if (!alreadyOnCategoryStep) {
            // We're on Step 1 - handle type selection
            await expect(machineTypeCard).toBeVisible({ timeout: 10000 });

            // Check if already selected (form may have default value)
            const isAlreadySelected = await machineTypeCard.evaluate(el => el.classList.contains('selected'));
            if (!isAlreadySelected) {
                // Use force:true to bypass stability checks during CSS transitions
                await machineTypeCard.click({ force: true });
            }

            // Click Next to advance to Category selection
            const nextButton = this.page.getByRole('button', { name: /Next/i });
            await expect(nextButton).toBeEnabled({ timeout: 5000 });
            await nextButton.click();
            await this.page.waitForLoadState('domcontentloaded');
            await this.page.waitForTimeout(300); // Allow step transition
        }

        // Step 2: Select Category - wait for categories to load from definitions
        await expect(categoryCards.first()).toBeVisible({ timeout: 15000 });

        // Try to find 'LiquidHandler' category or fall back to first available
        const liquidCategory = categoryCards.filter({ hasText: /liquid|handler/i }).first();
        const hasLiquidCategory = await liquidCategory.isVisible({ timeout: 2000 }).catch(() => false);
        if (hasLiquidCategory) {
            await liquidCategory.click({ force: true });
        } else {
            // Click the first available category
            await categoryCards.first().click({ force: true });
        }

        // Click Next to advance to Machine Type selection
        await this.page.getByRole('button', { name: /Next/i }).click();
        await this.page.waitForLoadState('domcontentloaded');
        await this.page.waitForTimeout(300); // Allow step transition

        // Step 3: Select Machine Type (Frontend) - wait for cards to load
        await this.selectWizardCard();

        // Click Next to advance to Driver/Backend selection
        await this.clickNextButton();

        // Step 4: Select Driver/Backend - select first available
        await this.selectWizardCard();

        // Click Next to advance to Config step
        await this.clickNextButton();
        await this.page.waitForTimeout(300); // Allow step transition

        // Step 5: Fill Configuration
        const nameInput = this.page.getByLabel('Instance Name').or(this.page.getByLabel('Name'));
        await expect(nameInput).toBeVisible({ timeout: 5000 });
        await nameInput.clear();
        await nameInput.fill(name);

        // Click Next to go to Review step
        await this.page.getByRole('button', { name: /Next/i }).click();
        await this.page.waitForLoadState('domcontentloaded');
        await this.page.waitForTimeout(300); // Allow step transition

        // Step 6: Review and Create
        const createBtn = this.page.getByRole('button', { name: /Create Asset/i });
        await expect(createBtn).toBeVisible({ timeout: 5000 });
        await createBtn.click();

        // Wait for dialog to close (asset created)
        await expect(dialog).not.toBeVisible({ timeout: 15000 });
    }

    async createResource(name: string, modelQuery: string = '96') {
        await this.addResourceButton.click();

        const dialog = this.page.getByRole('dialog');
        await expect(dialog).toBeVisible();

        // Step 1: Select Category (Accordion)
        const accordion = this.page.locator('.resource-accordion');
        await expect(accordion).toBeVisible({ timeout: 10000 });

        // Find the "Plates" or "TipRacks" panel
        const platePanel = accordion.locator('mat-expansion-panel-header', { hasText: /Plate/i }).first();

        // If panel exists, click to expand
        if (await platePanel.isVisible()) {
            await platePanel.click();
        } else {
            // Fallback: click first panel
            await accordion.locator('mat-expansion-panel-header').first().click();
        }

        // Wait for content (resource items)
        const resourceItems = this.page.locator('.resource-item');
        await expect(resourceItems.first()).toBeVisible({ timeout: 5000 });

        // Filter/Select Model via search input or clicking item
        // The dialog has a search input at the top
        const searchInput = this.page.locator('.browse-container input[matInput]');
        if (await searchInput.isVisible()) {
            await searchInput.fill(modelQuery);
            await this.page.waitForTimeout(500); // Wait for filter
        }

        // Click first visible item
        await resourceItems.first().click();

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
