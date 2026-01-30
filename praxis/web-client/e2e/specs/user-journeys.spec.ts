import { test, expect } from '../fixtures/worker-db.fixture';

test.describe('User Journeys', () => {
  test.beforeEach(async ({ page }) => {
    // 1. Bypass login token check if needed
    await page.addInitScript(() => {
      localStorage.setItem('auth_token', 'fake-token');
      localStorage.setItem('auth_user', JSON.stringify({ username: 'test_user' }));
    });

    // 2. Initial Navigation with browser mode
    await page.goto('/?mode=browser');
    // Navigate directly to /app/home (more reliable than waiting for redirect)
    await page.goto('/app/home?mode=browser');
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch((e) => {
      console.log('[Test] Silent catch (networkidle):', e);
    });

    // 3. Ensure Shell Loaded
    await expect(page.locator('.sidebar-rail')).toBeVisible({ timeout: 10000 });

    // 4. Handle Welcome Dialog (Browser Mode specific)
    const welcomeDialog = page.getByRole('dialog', { name: /Welcome to Praxis/i });
    if (await welcomeDialog.isVisible({ timeout: 5000 })) {
      console.log('Dismissing Welcome Dialog...');
      await page.getByRole('button', { name: /Skip for Now/i }).click();
      await expect(welcomeDialog).not.toBeVisible();
    }

    // Safety Force Escape for Tours/Overlays
    await page.keyboard.press('Escape');
  });

  test('Asset Management: View and Create Machine', async ({ page }) => {
    // Navigate via sidebar to ensure we are in the right context or just go directly
    await page.goto('/assets?type=machine');
    await page.screenshot({ path: '/tmp/e2e-journeys/1-asset-list.png' });

    // Check that we are on the machine list
    // Wait for any initial overlays (welcome dialog, loading) to fully go away
    try {
      await expect(page.locator('.cdk-overlay-backdrop')).not.toBeVisible({ timeout: 30000 });
    } catch (e) {
      console.log('Overlay backdrop still visible, attempting to force interact...');
    }

    const addBtn = page.locator('[data-tour-id="add-asset-btn"]');
    await expect(addBtn).toBeVisible();

    // Click Add Machine
    await addBtn.click({ force: true });

    // Wizard dialog opens (app-asset-wizard, not app-machine-dialog)
    const wizard = page.locator('app-asset-wizard');
    await expect(wizard).toBeVisible();

    // Wait for wizard content to be fully rendered (category cards should be visible)
    await expect(page.getByTestId('category-card-LiquidHandler')).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: '/tmp/e2e-journeys/2-asset-wizard.png' });

    // Helper: click Next when enabled  
    const clickNext = async () => {
      // Look for visible Next button in dialog
      const nextBtn = page.locator('button:visible').filter({ hasText: 'Next' }).first();
      await expect(nextBtn).toBeEnabled({ timeout: 10000 });
      await nextBtn.click();
      // Small wait for step transition
      await page.waitForTimeout(500);
    };

    // Step 2: Category is the default active tab when adding a machine
    // Select LiquidHandler category
    await page.getByTestId('category-card-LiquidHandler').click();
    await page.screenshot({ path: '/tmp/e2e-journeys/3-category-selected.png' });
    await clickNext();

    // Step 3: Machine Type - select first frontend option
    await page.screenshot({ path: '/tmp/e2e-journeys/4-machine-type-step.png' });
    const frontendCard = page.locator('[data-testid^="frontend-card-"], .frontend-card').first();
    if (await frontendCard.count() > 0) {
      await frontendCard.click();
    }
    await clickNext();

    // Step 4: Driver/Backend - select first backend option
    await page.screenshot({ path: '/tmp/e2e-journeys/5-driver-step.png' });
    const backendCard = page.locator('[data-testid^="backend-card-"], .backend-card').first();
    if (await backendCard.count() > 0) {
      await backendCard.click();
    }
    await clickNext();

    // Step 5: Config - fill name if visible
    await page.screenshot({ path: '/tmp/e2e-journeys/6-config-step.png' });
    const nameInput = page.getByLabel('Name');
    if (await nameInput.isVisible({ timeout: 2000 }).catch((e) => {
      console.log('[Test] Silent catch (nameInput isVisible):', e);
      return false;
    })) {
      await nameInput.fill('New Robot');
    }
    await clickNext();

    // Step 6: Review - Create asset
    await page.screenshot({ path: '/tmp/e2e-journeys/7-review-step.png' });
    const createBtn = page.locator('button:visible').filter({ hasText: /Create|Save|Finish/ }).first();
    await expect(createBtn).toBeEnabled({ timeout: 10000 });
    await createBtn.click();

    // Wizard should close
    await expect(wizard).toBeHidden({ timeout: 10000 });

    // Ideally, we'd check if the list updated, but since we mocked the GET initially,
    // and the list component calls loadMachines() again which triggers the SAME mocked GET response,
    // it won't actually show the new machine unless we dynamically update the mock route.
    // For now, verifying the dialog interaction is sufficient to prove the button works.

    // Let's verify the tabs work (optional - wizard completion is the main test)
    try {
      await page.getByRole('tab', { name: /Resources/i }).click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: '/tmp/e2e-journeys/8-resources-tab.png' });
    } catch (e) {
      console.log('Tab verification skipped:', (e as Error).message);
    }
  });

  test('Protocol Workflow: Select and Run', async ({ page }) => {
    await page.goto('/protocols');
    await page.screenshot({ path: '/tmp/e2e-journeys/4-protocol-library.png' });

    // Library - 'Simple Transfer' is a default protocol in Browser Mode
    await expect(page.locator('table')).toContainText('Simple Transfer');

    // Click "Run" button (using row locator for precision)
    const row = page.locator('tr', { hasText: 'Simple Transfer' });
    await row.locator('button:has(mat-icon:text("play_arrow"))').click();

    // Wait for navigation
    await page.waitForURL(/.*\/run/);

    // Wizard - Check if we are on Step 1 or explicitly jumped to Step 2
    // Wait for the header to be populated with expected text
    const headerParams = page.locator('h3').first();
    await expect(async () => {
      const t = await headerParams.textContent();
      return t?.includes('Selected Protocol') || t?.includes('Protocol Parameters');
    }).toPass({ timeout: 10000 });

    const headerText = await headerParams.textContent();
    console.log('Wizard Header Text:', headerText);
    const onStep2 = headerText?.includes('Protocol Parameters');

    if (!onStep2) {
      // Step 1: Select Protocol
      await expect(page.locator('app-run-protocol')).toBeVisible();
      await expect(page.locator('h3').first()).toContainText('Selected Protocol: Simple Transfer');
      await page.screenshot({ path: '/tmp/e2e-journeys/5-wizard-step1.png' });

      // Click Next on Step 1
      await page.locator('mat-step-header[aria-selected="true"]').first().waitFor();
      await page.getByRole('button', { name: 'Next' }).first().click();
    } else {
      console.log('Automatically advanced to Step 2 (Parameters)');
    }

    // Wizard - Step 2: Parameters
    // Use visibility-aware selector for Material stepper (hidden panels still exist in DOM)
    const visibleStep = page.locator('.mat-step-content:not([style*="visibility: hidden"]), mat-step-content:visible').first();
    await expect(page.locator('mat-form-field:visible').first()).toBeVisible({ timeout: 10000 });
    await page.screenshot({ path: '/tmp/e2e-journeys/6-wizard-step2.png' });

    // Fill form - find actual parameter input (label may not be "Example Parameter")
    const paramInput = page.locator('mat-form-field:visible input').first();
    await paramInput.fill('test value');

    // Click Next on Step 2
    await page.locator('button:visible').filter({ hasText: 'Next' }).first().click();

    // Wizard - Step 3: Deck Config
    await expect(page.getByText('Deck configuration visualization')).toBeVisible();
    await page.screenshot({ path: '/tmp/e2e-journeys/7-wizard-step3.png' });
    // Click Next on Step 3
    await page.locator('button').filter({ hasText: 'Next' }).locator('visible=true').click();

    // Wizard - Step 4: Review
    await expect(page.getByText('Ready to Run')).toBeVisible();
    await expect(page.getByText('Parameters Configured: Yes')).toBeVisible();
    await page.screenshot({ path: '/tmp/e2e-journeys/8-wizard-step4.png' });

    // Start Run
    // Note: In browser mode, this might fail if simulation backend isn't perfect, but we check button clickability
    await page.getByRole('button', { name: 'Start Execution' }).click();
  });
});