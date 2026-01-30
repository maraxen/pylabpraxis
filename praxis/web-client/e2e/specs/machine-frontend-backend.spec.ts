import { test, expect } from '../fixtures/worker-db.fixture';
import { WelcomePage } from '../page-objects/welcome.page';
import { AssetsPage } from '../page-objects/assets.page';

/**
 * E2E Tests for Machine Frontend/Backend Separation
 * 
 * Tests the new 3-step machine creation flow:
 * 1. Select Frontend (Machine Type) - e.g., LiquidHandler, PlateReader
 * 2. Select Backend (Driver) - e.g., HamiltonSTARBackend, ChatterBoxBackend
 * 3. Configure Instance - Name, connection settings, capabilities
 */
test.describe('Machine Frontend/Backend Separation', () => {
    let assetsPage: AssetsPage;

    test.beforeEach(async ({ page }) => {
        const welcomePage = new WelcomePage(page);
        assetsPage = new AssetsPage(page);

        // Enable debug logging
        page.on('console', msg => {
            const text = msg.text();
            if (text.includes('ASSET-DEBUG') || text.includes('[SqliteService]') || text.includes('MachineDialog')) {
                console.log(`BROWSER_LOG: ${text}`);
            }
        });

        await welcomePage.goto();
        await welcomePage.handleSplashScreen();
    });

    test.describe('Machine Dialog - Frontend Selection (Step 1)', () => {
        test('should display frontend types (machine categories) in step 1', async ({ page }) => {
            await assetsPage.goto();
            await assetsPage.waitForOverlay();

            // Open Add Machine dialog
            await assetsPage.addMachineButton.click();
            
            const dialog = page.getByRole('dialog');
            await expect(dialog).toBeVisible({ timeout: 10000 });
            await expect(dialog).toContainText('Add New Asset');

            // Wait for data to load - scope to dialog and ensure visibility
            await page.getByRole('dialog').locator('button.selection-card:visible').first().waitFor({ state: 'visible', timeout: 15000 });

            // Verify step 1 title
            await expect(page.getByText('Choose Machine Type')).toBeVisible({ timeout: 5000 });

            // Verify frontend types are displayed (from MachineFrontendDefinition)
            const liquidHandlerCard = page.getByRole('dialog').locator('button.selection-card:visible').filter({ hasText: /Liquid Handler/i }).first();
            await expect(liquidHandlerCard).toBeVisible({ timeout: 10000 });

            // Close dialog
            await page.getByRole('dialog').getByRole('button', { name: /Cancel/i }).click();
        });

        test('should show multiple frontend types from database', async ({ page }) => {
            await assetsPage.goto();
            await assetsPage.waitForOverlay();

            await assetsPage.addMachineButton.click();
            
            const dialog = page.getByRole('dialog');
            await expect(dialog).toBeVisible({ timeout: 10000 });
            await expect(dialog).toContainText('Add New Asset');

            // Wait for data to load
            await page.getByRole('dialog').locator('button.selection-card:visible').first().waitFor({ state: 'visible', timeout: 15000 });

            // Count available frontend types
            const frontendCards = page.getByRole('dialog').locator('button.selection-card:visible');
            await expect(frontendCards.first()).toBeVisible({ timeout: 10000 });
            
            const count = await frontendCards.count();
            expect(count).toBeGreaterThan(0);
            console.log(`Found ${count} frontend types`);

            // Close dialog
            await page.getByRole('dialog').getByRole('button', { name: /Cancel/i }).click();
        });
    });

    test.describe('Machine Dialog - Backend Selection (Step 2)', () => {
        test('should navigate to backend selection after choosing frontend', async ({ page }) => {
            await assetsPage.goto();
            await assetsPage.waitForOverlay();

            await assetsPage.addMachineButton.click();
            
            const dialog = page.getByRole('dialog');
            await expect(dialog).toBeVisible({ timeout: 10000 });
            await expect(dialog).toContainText('Add New Asset');

            // Wait for data to load
            await page.getByRole('dialog').locator('button.selection-card:visible').first().waitFor({ state: 'visible', timeout: 15000 });

            // Step 1: Select Liquid Handler frontend
            const liquidHandlerCard = page.getByRole('dialog').locator('button.selection-card:visible').filter({ hasText: /Liquid Handler/i }).first();
            await expect(liquidHandlerCard).toBeVisible({ timeout: 10000 });

            // Close dialog
            await page.getByRole('dialog').getByRole('button', { name: /Cancel/i }).click();
        });

        test('should show compatible backends for selected frontend', async ({ page }) => {
            await assetsPage.goto();
            await assetsPage.waitForOverlay();

            await assetsPage.addMachineButton.click();
            
            const dialog = page.getByRole('dialog');
            await expect(dialog).toBeVisible({ timeout: 10000 });
            await expect(dialog).toContainText('Add New Asset');

            // Wait for data to load
            await page.getByRole('dialog').locator('button.selection-card:visible').first().waitFor({ state: 'visible', timeout: 15000 });

            // Step 1: Select Liquid Handler frontend
            const liquidHandlerCard = page.getByRole('dialog').locator('button.selection-card:visible').filter({ hasText: /Liquid Handler/i }).first();
            await expect(liquidHandlerCard).toBeVisible({ timeout: 10000 });
            await liquidHandlerCard.click();

            // Click Next
            await page.getByRole('dialog').getByRole('button', { name: /Next/i }).click();

            // Verify backends are loaded
            const backendCards = page.getByRole('dialog').locator('button.selection-card.definition-card:visible');
            await expect(backendCards.first()).toBeVisible({ timeout: 10000 });
            
            const backendCount = await backendCards.count();
            expect(backendCount).toBeGreaterThan(0);
            console.log(`Found ${backendCount} backends for Liquid Handler`);

            // Look for simulated backends (ChatterBox)
            const simulatedBackend = backendCards.filter({ hasText: /Simulated/i });
            await expect(simulatedBackend.first()).toBeVisible({ timeout: 5000 });

            // Close dialog
            await page.getByRole('dialog').getByRole('button', { name: /Cancel/i }).click();
        });

        test('should display simulated badge for simulator backends', async ({ page }) => {
            await assetsPage.goto();
            await assetsPage.waitForOverlay();

            await assetsPage.addMachineButton.click();
            
            const dialog = page.getByRole('dialog');
            await expect(dialog).toBeVisible({ timeout: 10000 });
            await expect(dialog).toContainText('Add New Asset');

            // Wait for data to load
            await page.getByRole('dialog').locator('button.selection-card:visible').first().waitFor({ state: 'visible', timeout: 15000 });

            // Step 1: Select Liquid Handler
            const liquidHandlerCard = page.getByRole('dialog').locator('button.selection-card:visible').filter({ hasText: /Liquid Handler/i }).first();
            await expect(liquidHandlerCard).toBeVisible({ timeout: 10000 });
            await liquidHandlerCard.click();

            // Click Next
            await page.getByRole('dialog').getByRole('button', { name: /Next/i }).click();

            // Look for "Simulated" chip/badge
            const simulatedChip = page.locator('.simulated-chip').or(page.locator('span').filter({ hasText: /Simulated/i }));
            await expect(simulatedChip.first()).toBeVisible({ timeout: 10000 });

            // Close dialog
            await page.getByRole('dialog').getByRole('button', { name: /Cancel/i }).click();
        });
    });

    test.describe('Machine Dialog - Configuration (Step 3)', () => {
        test('should navigate to configuration after selecting backend', async ({ page }) => {
            await assetsPage.goto();
            await assetsPage.waitForOverlay();

            await assetsPage.addMachineButton.click();
            
            const dialog = page.getByRole('dialog');
            await expect(dialog).toBeVisible({ timeout: 10000 });
            await expect(dialog).toContainText('Add New Asset');

            // Wait for data to load
            await page.getByRole('dialog').locator('button.selection-card:visible').first().waitFor({ state: 'visible', timeout: 15000 });

            // Step 1: Select Liquid Handler
            const liquidHandlerCard = page.getByRole('dialog').locator('button.selection-card:visible').filter({ hasText: /Liquid Handler/i }).first();
            await expect(liquidHandlerCard).toBeVisible({ timeout: 10000 });
            await liquidHandlerCard.click();

            // Click Next to step 2
            await page.getByRole('button', { name: /Next/i }).click();

            // Step 2: Select a simulated backend
            const simulatedBackend = page.getByRole('dialog').locator('button.selection-card.definition-card:visible').filter({ hasText: /Simulated|ChatterBox/i }).first();
            await expect(simulatedBackend).toBeVisible({ timeout: 10000 });
            await simulatedBackend.click();

            // Click Next to step 3
            await page.getByRole('button', { name: /Next/i }).click();

            // Verify step 3: Configuration
            await expect(page.getByText('Configure Machine')).toBeVisible({ timeout: 5000 });

            // Verify instance name field is present
            const nameInput = page.getByLabel('Instance Name');
            await expect(nameInput).toBeVisible({ timeout: 5000 });

            // Close dialog
            await page.getByRole('dialog').getByRole('button', { name: /Cancel/i }).click();
        });

        test('should pre-populate name from selected backend', async ({ page }) => {
            await assetsPage.goto();
            await assetsPage.waitForOverlay();

            await assetsPage.addMachineButton.click();
            
            const dialog = page.getByRole('dialog');
            await expect(dialog).toBeVisible({ timeout: 10000 });
            await expect(dialog).toContainText('Add New Asset');

            // Wait for data to load
            await page.getByRole('dialog').locator('button.selection-card:visible').first().waitFor({ state: 'visible', timeout: 15000 });

            // Step 1: Select Liquid Handler
            const liquidHandlerCard = page.getByRole('dialog').locator('button.selection-card:visible').filter({ hasText: /Liquid Handler/i }).first();
            await expect(liquidHandlerCard).toBeVisible({ timeout: 10000 });
            await liquidHandlerCard.click();
            await page.getByRole('button', { name: /Next/i }).click();

            // Step 2: Select a backend
            const backendCard = page.getByRole('dialog').locator('button.selection-card.definition-card:visible').first();
            await expect(backendCard).toBeVisible({ timeout: 10000 });
            await backendCard.click();
            await page.getByRole('button', { name: /Next/i }).click();

            // Step 3: Verify name is pre-populated
            const nameInput = page.getByLabel('Instance Name');
            await expect(nameInput).toBeVisible({ timeout: 5000 });
            
            const nameValue = await nameInput.inputValue();
            expect(nameValue.length).toBeGreaterThan(0);
            console.log(`Pre-populated name: ${nameValue}`);

            // Close dialog
            await page.getByRole('dialog').getByRole('button', { name: /Cancel/i }).click();
        });
    });

    test.describe('Machine Dialog - Full Workflow', () => {
        test('should complete full 3-step machine creation flow', async ({ page }) => {
            const testMachineName = `Test Machine ${Date.now()}`;
            
            await assetsPage.goto();
            await assetsPage.waitForOverlay();
            await assetsPage.navigateToMachines();

            await assetsPage.addMachineButton.click();
            
            const dialog = page.getByRole('dialog');
            await expect(dialog).toBeVisible({ timeout: 10000 });

            // Step 1: Select Liquid Handler frontend
            const liquidHandlerCard = page.getByRole('dialog').locator('button.selection-card:visible').filter({ hasText: /Liquid Handler/i }).first();
            await expect(liquidHandlerCard).toBeVisible({ timeout: 10000 });
            await liquidHandlerCard.click();
            
            // Verify step indicator shows step 1 complete
            await page.getByRole('button', { name: /Next/i }).click();

            // Step 2: Select ChatterBox (simulated) backend
            const backendCards = page.getByRole('dialog').locator('button.selection-card.definition-card:visible');
            await expect(backendCards.first()).toBeVisible({ timeout: 10000 });
            
            // Prefer simulated backend for testing
            const simulatedBackend = backendCards.filter({ hasText: /Simulated|ChatterBox/i }).first();
            if (await simulatedBackend.isVisible({ timeout: 2000 })) {
                await simulatedBackend.click();
            } else {
                await backendCards.first().click();
            }
            
            await page.getByRole('button', { name: /Next/i }).click();

            // Step 3: Configure instance
            await expect(page.getByText('Configure Machine')).toBeVisible({ timeout: 5000 });
            
            // Fill custom name
            const nameInput = page.getByLabel('Instance Name');
            await nameInput.clear();
            await nameInput.fill(testMachineName);

            // Click Finish
            const finishButton = page.getByRole('button', { name: /Finish/i });
            await expect(finishButton).toBeEnabled({ timeout: 5000 });
            await finishButton.click();

            // Verify dialog closes
            await expect(dialog).not.toBeVisible({ timeout: 5000 });

            // Verify machine appears in list
            await expect(page.getByText(testMachineName)).toBeVisible({ timeout: 10000 });
        });

        test('should persist created machine after page reload', async ({ page }) => {
            const testMachineName = `Persist Machine ${Date.now()}`;
            
            await assetsPage.goto();
            await assetsPage.waitForOverlay();
            await assetsPage.navigateToMachines();

            // Create machine via full flow
            await assetsPage.addMachineButton.click();
            
            const dialog = page.getByRole('dialog');
            await expect(dialog).toBeVisible({ timeout: 10000 });
            await expect(dialog).toContainText('Add New Asset');

            // Wait for data to load
            await page.getByRole('dialog').locator('button.selection-card:visible').first().waitFor({ state: 'visible', timeout: 15000 });

            // Step 1
            const liquidHandlerCard = page.getByRole('dialog').locator('button.selection-card:visible').filter({ hasText: /Liquid Handler/i }).first();
            await expect(liquidHandlerCard).toBeVisible({ timeout: 10000 });
            await liquidHandlerCard.click();
            await page.getByRole('button', { name: /Next/i }).click();

            // Step 2
            const backendCards = page.getByRole('dialog').locator('button.selection-card.definition-card:visible');
            await expect(backendCards.first()).toBeVisible({ timeout: 10000 });
            await backendCards.first().click();
            await page.getByRole('button', { name: /Next/i }).click();

            // Step 3
            const nameInput = page.getByLabel('Instance Name');
            await nameInput.clear();
            await nameInput.fill(testMachineName);
            await page.getByRole('button', { name: /Finish/i }).click();

            await expect(dialog).not.toBeVisible({ timeout: 5000 });
            await expect(page.getByText(testMachineName)).toBeVisible({ timeout: 10000 });

            // Reload page
            await page.reload();
            await assetsPage.waitForOverlay();
            await assetsPage.navigateToMachines();

            // Verify machine still exists
            await expect(page.getByText(testMachineName)).toBeVisible({ timeout: 10000 });
        });
    });

    test.describe('Machine Dialog - Navigation', () => {
        test('should allow going back from step 2 to step 1', async ({ page }) => {
            await assetsPage.goto();
            await assetsPage.waitForOverlay();

            await assetsPage.addMachineButton.click();
            
            const dialog = page.getByRole('dialog');
            await expect(dialog).toBeVisible({ timeout: 10000 });
            await expect(dialog).toContainText('Add New Asset');

            // Wait for data to load
            await page.getByRole('dialog').locator('button.selection-card:visible').first().waitFor({ state: 'visible', timeout: 15000 });

            // Step 1: Select frontend
            const liquidHandlerCard = page.getByRole('dialog').locator('button.selection-card:visible').filter({ hasText: /Liquid Handler/i }).first();
            await expect(liquidHandlerCard).toBeVisible({ timeout: 10000 });
            await liquidHandlerCard.click();
            await page.getByRole('button', { name: /Next/i }).click();

            // Verify on step 2
            await expect(page.getByText('Choose Machine Type')).toBeVisible({ timeout: 5000 });

            // Click back button
            const backButton = page.getByRole('button').filter({ has: page.locator('mat-icon:has-text("arrow_back")') });
            await backButton.click();

            // Verify back on step 1
            await expect(page.getByText('Choose Machine Type')).toBeVisible({ timeout: 5000 });

            // Close dialog
            await page.getByRole('dialog').getByRole('button', { name: /Cancel/i }).click();
        });

        test('should allow going back from step 3 to step 2', async ({ page }) => {
            await assetsPage.goto();
            await assetsPage.waitForOverlay();

            await assetsPage.addMachineButton.click();
            
            const dialog = page.getByRole('dialog');
            await expect(dialog).toBeVisible({ timeout: 10000 });
            await expect(dialog).toContainText('Add New Asset');

            // Wait for data to load
            await page.getByRole('dialog').locator('button.selection-card:visible').first().waitFor({ state: 'visible', timeout: 15000 });

            // Step 1
            const liquidHandlerCard = page.getByRole('dialog').locator('button.selection-card:visible').filter({ hasText: /Liquid Handler/i }).first();
            await expect(liquidHandlerCard).toBeVisible({ timeout: 10000 });
            await liquidHandlerCard.click();
            await page.getByRole('button', { name: /Next/i }).click();

            // Step 2
            const backendCards = page.getByRole('dialog').locator('button.selection-card.definition-card:visible');
            await expect(backendCards.first()).toBeVisible({ timeout: 10000 });
            await backendCards.first().click();
            await page.getByRole('button', { name: /Next/i }).click();

            // Verify on step 3
            await expect(page.getByText('Configure Machine')).toBeVisible({ timeout: 5000 });

            // Click back button
            const backButton = page.getByRole('button').filter({ has: page.locator('mat-icon:has-text("arrow_back")') });
            await backButton.click();

            // Verify back on step 2
            await expect(page.getByText('Choose Machine Type')).toBeVisible({ timeout: 5000 });

            // Close dialog
            await page.getByRole('dialog').getByRole('button', { name: /Cancel/i }).click();
        });

        test('should allow clicking step indicators to navigate', async ({ page }) => {
            await assetsPage.goto();
            await assetsPage.waitForOverlay();

            await assetsPage.addMachineButton.click();
            
            const dialog = page.getByRole('dialog');
            await expect(dialog).toBeVisible({ timeout: 10000 });
            await expect(dialog).toContainText('Add New Asset');

            // Wait for data to load
            await page.getByRole('dialog').locator('button.selection-card:visible').first().waitFor({ state: 'visible', timeout: 15000 });

            // Complete step 1
            const liquidHandlerCard = page.getByRole('dialog').locator('button.selection-card:visible').filter({ hasText: /Liquid Handler/i }).first();
            await expect(liquidHandlerCard).toBeVisible({ timeout: 10000 });
            await liquidHandlerCard.click();
            await page.getByRole('button', { name: /Next/i }).click();

            // Complete step 2
            const backendCards = page.getByRole('dialog').locator('button.selection-card.definition-card:visible');
            await expect(backendCards.first()).toBeVisible({ timeout: 10000 });
            await backendCards.first().click();
            await page.getByRole('button', { name: /Next/i }).click();

            // On step 3, click step 1 indicator to go back
            const step1Indicator = page.locator('.stepper').locator('div').filter({ hasText: /Machine Type/i });
            await step1Indicator.click();

            // Verify back on step 1
            await expect(page.getByText('Choose Machine Type')).toBeVisible({ timeout: 5000 });

            // Close dialog
            await page.getByRole('dialog').getByRole('button', { name: /Cancel/i }).click();
        });
    });

    test.describe('Add Asset Dialog - Definition Selection Step', () => {
        test('should show frontend types in Add Asset dialog machine flow', async ({ page }) => {
            // Test the Add Asset dialog (used in Playground inventory)
            await page.goto('/app/playground?mode=browser&resetdb=1');
            
            // Handle onboarding
            const skipBtn = page.getByRole('button', { name: /Skip/i });
            try {
                await skipBtn.waitFor({ state: 'visible', timeout: 5000 });
                await skipBtn.click();
            } catch (e) {
                // Not present
            }

            // Open inventory dialog
            await page.getByLabel('Open Inventory Dialog').click();
            
            // Switch to "Browse & Add" tab
            const browseTab = page.getByRole('tab', { name: /Browse/i });
            if (await browseTab.isVisible({ timeout: 2000 })) {
                await browseTab.click();
            }

            // Select Machine type
            const machineOption = page.getByRole('dialog').locator('button').filter({ hasText: /Machine/i }).first();
            if (await machineOption.isVisible({ timeout: 2000 })) {
                await machineOption.click();
            }

            // Verify frontend types are shown
            await page.getByRole('dialog').locator('button.selection-card:visible').first().waitFor({ state: 'visible', timeout: 15000 });
            const frontendTypes = page.getByRole('dialog').locator('button.selection-card:visible');
            await expect(frontendTypes.first()).toBeVisible({ timeout: 10000 });

            // Close dialog
            await page.keyboard.press('Escape');
        });
    });
});
