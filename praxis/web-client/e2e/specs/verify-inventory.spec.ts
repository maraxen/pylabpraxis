import { test, expect } from '@playwright/test';

test.describe('Inventory Dialog Verification', () => {
  test.beforeEach(async ({ page }) => {
    page.on('console', msg => {
        if (msg.type() === 'error' || msg.text().includes('[SqliteService]')) {
            console.log(`[BROWSER] ${msg.text()}`);
        }
    });
    
    // Prevent Welcome Dialog from blocking the UI via localStorage
    await page.addInitScript(() => {
      localStorage.setItem('praxis_onboarding_completed', 'true');
    });
  });

  test('should load definitions and allow filtering by machine category', async ({ page }) => {
    // 1. Navigate to playground
    console.log("Navigating to playground...");
    await page.goto('/app/playground', { waitUntil: 'networkidle' });
    
    // 2. Open inventory dialog
    console.log("Opening inventory dialog...");
    const dialogBtn = page.getByRole('button', { name: 'Open Inventory Dialog' });
    await dialogBtn.waitFor({ state: 'visible', timeout: 30000 });
    await dialogBtn.click();
    
    // 3. Wait for dialog to appear
    console.log("Waiting for dialog...");
    const dialogTitle = page.getByRole('heading', { name: 'Playground Inventory' });
    await expect(dialogTitle).toBeVisible({ timeout: 10000 });
    console.log("Inventory dialog opened.");
    
    // 4. Click "Browse & Add" tab
    console.log("Clicking 'Browse & Add' tab...");
    const browseTab = page.locator('.mdc-tab').filter({ hasText: 'Browse & Add' });
    await browseTab.waitFor({ state: 'visible', timeout: 5000 });
    await browseTab.click();
    
    // 5. Select "Machine" type
    console.log("Selecting 'Machine' type...");
    const machineCard = page.locator('.type-card').filter({ hasText: 'Machine' });
    await machineCard.waitFor({ state: 'visible', timeout: 5000 });
    await machineCard.click();
    
    // 6. Click Continue
    console.log("Clicking Continue...");
    const continueBtn = page.getByRole('button', { name: 'Continue' });
    await expect(continueBtn).toBeEnabled({ timeout: 5000 });
    await continueBtn.click();
    
    // 7. Verify categories are present (Wait for DB load if needed)
    console.log("Waiting for categories...");
    
    // Check if we hit the empty state
    const emptyState = page.locator('.empty-state');
    const chipList = page.locator('mat-chip-listbox');
    
    try {
        await chipList.waitFor({ state: 'visible', timeout: 10000 });
    } catch (e) {
        if (await emptyState.isVisible()) {
            const text = await emptyState.innerText();
            console.error(`ERROR: Inventory Dialog showed empty state: "${text}"`);
            
            // Log available definitions for debugging
            const defs = await page.evaluate(() => {
                return (window as any).sqliteService?.getDatabase()
                    .then((db: any) => {
                        try {
                            const res = db.exec("SELECT count(*) FROM machine_definitions");
                            return res[0].values[0][0];
                        } catch(err) { return "Query Failed: " + err; }
                    });
            });
            console.log(`[DEBUG] DB Machine Definitions count: ${defs}`);
        }
        throw e;
    }
    
    // Verify specific categories exist (Differentiating definitions)
    // We expect "Liquid Handler" (frontend) and potentially backend ones if not filtered
    // But primarily we want to ensure we have *some* categories
    const chips = page.locator('mat-chip-option');
    await expect(chips.first()).toBeVisible({ timeout: 5000 });
    
    const categories = await chips.allInnerTexts();
    console.log(`Machine categories found: ${categories.join(', ')}`);
    
    expect(categories.length).toBeGreaterThan(0);
    expect(categories.some(c => c.includes('Liquid Handler'))).toBeTruthy();
    
    // 8. Select a category (e.g. Liquid Handler)
    const lhChip = chips.filter({ hasText: 'Liquid Handler' }).first();
    if (await lhChip.isVisible()) {
        await lhChip.click();
        await continueBtn.click();
        
        // 9. Verify assets list is populated
        console.log("Waiting for asset list...");
        const list = page.locator('mat-selection-list');
        await list.waitFor({ state: 'visible', timeout: 10000 });
        const items = await page.locator('mat-list-option').allInnerTexts();
        console.log(`Assets found: ${items.length}`);
        expect(items.length).toBeGreaterThan(0);
        
        // Check for template badge (differentiation check)
        const templates = page.locator('.template-badge');
        if (await templates.count() > 0) {
            console.log("✅ Templates detected (Frontend definitions differentiated)");
        } else {
            console.log("⚠️ No templates visible - check if definitions loaded correctly");
        }
    }
            
    console.log("Frontend UI verification successful!");
  });
});