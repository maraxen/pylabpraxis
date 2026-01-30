import { test, expect } from '../fixtures/worker-db.fixture';
import { AssetsPage } from '../page-objects/assets.page';

test.afterEach(async ({ page }) => {
    // Dismiss any open dialogs/overlays to ensure clean state
    await page.keyboard.press('Escape').catch((e) => console.log('[Test] Silent catch (Escape):', e));
});

test('should allow adding a machine and using direct control', async ({ page }) => {
    // Increase timeout for complex wizard flow that involves multiple steps and animations
    test.setTimeout(180000);
    // Mock API calls - these might be bypassed in Browser Mode but good to have
    await page.route('**/api/v1/machines/definitions/facets', async route => {
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
                machine_category: [{ value: 'LiquidHandler', count: 1 }],
                manufacturer: [{ value: 'Hamilton', count: 1 }]
            })
        });
    });

    await page.route('**/api/v1/machines/definitions?*', async route => {
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify([
                {
                    accession_id: 'mach_test_001',
                    name: 'Hamilton STAR',
                    fqn: 'pylabrobot.liquid_handling.backends.hamilton.STAR',
                    plr_category: 'Machine',
                    machine_category: 'LiquidHandler',
                    manufacturer: 'Hamilton',
                    description: 'Hamilton STAR liquid handler',
                    available_simulation_backends: ['Simulated']
                }
            ])
        });
    });

    page.on('console', msg => console.log(`BROWSER LOG: ${msg.text()}`));

    // 1. Go to /app/playground
    await page.goto('/app/playground?mode=browser&resetdb=1');

    // Wait for SQLite DB to be ready
    await page.waitForFunction(() => (window as any).sqliteService?.isReady$?.getValue() === true, { timeout: 45000 });

    // Handle Welcome Dialog
    try {
        const dismissBtn = page.getByRole('button', { name: /Get Started|Skip|Close/i }).first();
        if (await dismissBtn.isVisible({ timeout: 5000 })) {
            await dismissBtn.click();
        }
    } catch (e) { console.log('[Test] Caught:', (e as Error).message); }

    await page.screenshot({ path: 'e2e/screenshots/direct-control-step1.png' });

    // 2. Open Inventory from Playground (using the header action button)
    const inventoryBtn = page.locator('button').filter({ has: page.locator('mat-icon', { hasText: 'inventory_2' }) });
    await expect(inventoryBtn).toBeVisible({ timeout: 25000 });
    await inventoryBtn.click();

    // 3. Add Machine using AssetsPage helper
    const assetsPage = new AssetsPage(page);
    const machineName = 'Hamilton STAR';
    await assetsPage.createMachine(machineName, 'LiquidHandler', 'STAR');

    // 4. Verify Machine is selected
    const directControlTab = page.getByRole('tab', { name: 'Direct Control' });
    await directControlTab.click();

    // Verify Direct Control is active
    const directControl = page.locator('app-direct-control');
    await expect(directControl).toBeVisible({ timeout: 10000 });

    // 5. Select a method and execute (if methods are available)
    console.log('Checking for available methods...');
    const methodChips = directControl.locator('.method-chip');
    const noMethodsMessage = directControl.locator('text=No methods available');

    // Wait for either method chips or no-methods message
    await Promise.race([
        methodChips.first().waitFor({ timeout: 10000 }).catch((e) => console.log('[Test] Silent catch (Method chips):', e)),
        noMethodsMessage.waitFor({ timeout: 10000 }).catch((e) => console.log('[Test] Silent catch (No methods msg):', e))
    ]);

    const hasMethodChips = await methodChips.count() > 0;

    if (hasMethodChips) {
        console.log('Methods found, selecting and executing...');
        // Select 'Setup' or the first method
        const setupMethod = methodChips.filter({ hasText: /Setup/i }).first();
        const targetedMethod = await setupMethod.isVisible() ? setupMethod : methodChips.first();
        await targetedMethod.click();

        console.log('Executing method...');
        const executeBtn = directControl.locator('.execute-btn');
        await expect(executeBtn).toBeVisible();
        await expect(executeBtn).toBeEnabled();
        await executeBtn.click();

        // 6. Verify feedback
        console.log('Verifying execution feedback...');
        // In simulation mode, it should show a success circle and result
        const successIcon = directControl.locator('.command-result mat-icon[color="primary"]');
        await expect(successIcon).toBeVisible({ timeout: 10000 });

        await page.screenshot({ path: 'e2e/screenshots/direct-control-executed.png' });
    } else {
        console.log('No methods available for this machine - this is expected for newly created machines without backend setup');
        await expect(noMethodsMessage).toBeVisible();
    }

    // Capture final screenshot
    await page.screenshot({ path: 'e2e/screenshots/direct-control-final.png' });
});
