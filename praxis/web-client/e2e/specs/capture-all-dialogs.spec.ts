import { test, expect } from '@playwright/test';
import { WelcomePage } from '../page-objects/welcome.page';
import { AssetsPage } from '../page-objects/assets.page';
import { ProtocolPage } from '../page-objects/protocol.page';
import * as path from 'path';
import * as fs from 'fs';

test.describe('Capture all dialogs', () => {
    test.setTimeout(300000);

    let welcomePage: WelcomePage;
    let assetsPage: AssetsPage;
    let protocolPage: ProtocolPage;
    const screenshotDir = path.join(process.cwd(), 'e2e/screenshots/dialogs');

    test.beforeAll(async () => {
        if (!fs.existsSync(screenshotDir)) {
            fs.mkdirSync(screenshotDir, { recursive: true });
        }
    });

    test.beforeEach(async ({ page }) => {
        welcomePage = new WelcomePage(page);
        assetsPage = new AssetsPage(page);
        protocolPage = new ProtocolPage(page);
        
        await page.goto('/app/home');
        await page.evaluate(() => {
            localStorage.setItem('praxis_onboarding_completed', 'true');
        });
        await page.waitForLoadState('networkidle');
    });

    async function captureDialog(page, name) {
        const dialog = page.getByRole('dialog').or(page.locator('mat-dialog-container'));
        await expect(dialog.first()).toBeVisible({ timeout: 20000 });
        await page.waitForTimeout(1000);
        const screenshotPath = path.join(screenshotDir, name);
        await page.screenshot({ path: screenshotPath });
        console.log(`Captured ${name}`);
        await page.keyboard.press('Escape');
        await page.waitForTimeout(500);
        if (await dialog.first().isVisible()) {
             await page.getByRole('button', { name: /close|cancel|dismiss/i }).first().click().catch(() => {});
             await page.waitForTimeout(500);
        }
    }

    test('1. command-palette.png', async ({ page }) => {
        await page.keyboard.press('Control+k');
        if (!(await page.getByRole('dialog').isVisible({ timeout: 2000 }))) {
            await page.keyboard.press('Meta+k');
        }
        await captureDialog(page, 'command-palette.png');
    });

    test('2. add-asset-dialog.png', async ({ page }) => {
        await page.goto('/app/assets');
        await page.getByRole('button', { name: /Add Asset/i }).or(page.getByRole('button', { name: /Add Machine/i })).first().click();
        await captureDialog(page, 'add-asset-dialog.png');
    });

    test('4. resource-dialog.png', async ({ page }) => {
        await page.goto('/app/assets');
        await page.getByRole('tab', { name: /Resources/i }).click();
        const addBtn = page.getByRole('button', { name: /Add Resource/i }).first();
        await addBtn.waitFor({ state: 'visible' });
        await addBtn.click();
        await captureDialog(page, 'resource-dialog.png');
    });

    test('5. resource-instances-dialog.png', async ({ page }) => {
        await page.goto('/app/assets');
        await page.getByRole('tab', { name: /Resources/i }).click();
        const item = page.locator('.definition-item').first();
        await item.waitFor({ state: 'visible', timeout: 30000 });
        await item.click();
        await captureDialog(page, 'resource-instances-dialog.png');
    });

    test('6. machine-details-dialog.png', async ({ page }) => {
        await page.goto('/app/assets');
        await page.getByRole('tab', { name: /Machines/i }).click();
        const machineItem = page.locator('.praxis-card, tr[mat-row], .machine-item-list, app-machine-card').first();
        await machineItem.waitFor({ state: 'visible', timeout: 30000 });
        await machineItem.click();
        await captureDialog(page, 'machine-details-dialog.png');
    });

    test('8. guided-setup.png', async ({ page }) => {
        await page.goto('/app/run');
        const protocolCard = page.locator('app-protocol-card').first();
        await protocolCard.waitFor({ state: 'visible', timeout: 30000 });
        await protocolCard.click();
        await page.getByRole('button', { name: /Continue/i }).click();
        const machineCard = page.locator('app-machine-card').first();
        await machineCard.waitFor({ state: 'visible', timeout: 15000 });
        await machineCard.click();
        await page.getByRole('button', { name: /Continue/i }).click();
        const assetsContinue = page.getByRole('button', { name: /Continue/i });
        await assetsContinue.waitFor({ state: 'visible', timeout: 15000 });
        await assetsContinue.click();
        const guidedSetup = page.locator('app-guided-setup');
        await guidedSetup.waitFor({ state: 'visible', timeout: 15000 });
        await page.waitForTimeout(1000);
        await page.screenshot({ path: path.join(screenshotDir, 'guided-setup.png') });
    });

    test('9. simulation-config-dialog.png', async ({ page }) => {
        await page.goto('/app/run');
        const protocolCard = page.locator('app-protocol-card').first();
        await protocolCard.waitFor({ state: 'visible', timeout: 30000 });
        await protocolCard.click();
        await page.getByRole('button', { name: /Continue/i }).click();
        const simTemplate = page.locator('app-machine-card').filter({ hasText: /Simulation|Simulated/i }).first();
        await simTemplate.waitFor({ state: 'visible', timeout: 30000 });
        await simTemplate.click();
        await captureDialog(page, 'simulation-config-dialog.png');
    });

    test('10. deck-simulation-dialog.png', async ({ page }) => {
        await page.goto('/app/workcell');
        const simulateBtn = page.getByRole('button', { name: /Simulate/i });
        await simulateBtn.waitFor({ state: 'visible', timeout: 30000 });
        await simulateBtn.click();
        await captureDialog(page, 'deck-simulation-dialog.png');
    });

    test('12. inventory-dialog.png', async ({ page }) => {
        await page.goto('/app/playground');
        const inventoryBtn = page.getByRole('button', { name: /Inventory/i });
        await inventoryBtn.waitFor({ state: 'visible', timeout: 30000 });
        await inventoryBtn.click();
        await captureDialog(page, 'inventory-dialog.png');
    });

    test('13. protocol-upload-dialog.png', async ({ page }) => {
        await page.goto('/app/protocols');
        const uploadBtn = page.locator('[data-tour-id="import-protocol-btn"]').or(page.getByRole('button', { name: /Upload/i }));
        await uploadBtn.waitFor({ state: 'visible', timeout: 30000 });
        await uploadBtn.click({ force: true });
        await captureDialog(page, 'protocol-upload-dialog.png');
    });

    test('14. protocol-detail-dialog.png', async ({ page }) => {
        await page.goto('/app/protocols');
        const protocolRow = page.locator('tr[mat-row], app-protocol-card').first();
        await protocolRow.waitFor({ state: 'visible', timeout: 30000 });
        const infoBtn = protocolRow.locator('button').filter({ has: page.locator('mat-icon:text("info")') });
        if (await infoBtn.isVisible()) {
            await infoBtn.click();
        } else {
            await protocolRow.hover();
            if (await infoBtn.isVisible()) {
                await infoBtn.click();
            } else {
                await protocolRow.click();
            }
        }
        await captureDialog(page, 'protocol-detail-dialog.png');
    });

    test('15. hardware-discovery-dialog.png', async ({ page }) => {
        await page.goto('/app/home');
        await page.keyboard.press('Control+k');
        await page.locator('input').fill('Discover');
        await page.waitForTimeout(1000);
        await page.keyboard.press('Enter');
        await captureDialog(page, 'hardware-discovery-dialog.png');
    });

    test('17. welcome-dialog.png', async ({ page }) => {
        await page.goto('/app/home');
        await page.evaluate(() => {
            localStorage.removeItem('praxis_onboarding_completed');
        });
        await page.goto('/app/home?welcome=true');
        await captureDialog(page, 'welcome-dialog.png');
    });

    test('18. confirmation-dialog.png', async ({ page }) => {
        await page.goto('/app/assets');
        await page.getByRole('tab', { name: /Machines/i }).click();
        const machineItem = page.locator('.praxis-card, tr[mat-row], .machine-item-list, app-machine-card').first();
        await machineItem.waitFor({ state: 'visible', timeout: 30000 });
        const deleteBtn = machineItem.locator('button[mattooltip*="Delete"]').or(machineItem.locator('button').filter({ has: page.locator('mat-icon:text("delete")') }));
        if (await deleteBtn.isVisible()) {
            await deleteBtn.click();
        } else {
            const moreBtn = machineItem.locator('button').filter({ has: page.locator('mat-icon:text("more_vert")') });
            await moreBtn.click();
            await page.getByRole('menuitem', { name: /Delete/i }).click();
        }
        await captureDialog(page, 'confirmation-dialog.png');
    });

    test('16. well-selector-dialog.png', async ({ page }) => {
        await page.goto('/app/run');
        const searchInput = page.getByPlaceholder(/Search protocols/i);
        await searchInput.waitFor({ state: 'visible' });
        await searchInput.fill('Selective Transfer');
        await page.waitForTimeout(1000);
        const protocolCard = page.locator('app-protocol-card').first();
        await protocolCard.waitFor({ state: 'visible', timeout: 30000 });
        await protocolCard.click();
        await page.getByRole('button', { name: /Continue/i }).click();
        const machineCard = page.locator('app-machine-card').first();
        await machineCard.waitFor({ state: 'visible', timeout: 15000 });
        await machineCard.click();
        await page.getByRole('button', { name: /Continue/i }).click();
        const openWellBtn = page.getByRole('button', { name: /Select Wells/i }).first();
        if (!(await openWellBtn.isVisible({ timeout: 10000 }))) {
             await page.getByRole('button', { name: /Continue/i }).click();
        }
        await openWellBtn.waitFor({ state: 'visible', timeout: 15000 });
        await openWellBtn.click();
        await captureDialog(page, 'well-selector-dialog.png');
    });
});
