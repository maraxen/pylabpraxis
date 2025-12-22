import { test, expect } from '@playwright/test';

test.describe('Advanced Protocol Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Bypass login
    await page.addInitScript(() => {
      localStorage.setItem('auth_token', 'fake-token');
      localStorage.setItem('auth_user', JSON.stringify({ username: 'test_user' }));
    });

    // Mock Machines for Asset Selector
    await page.route('/api/v1/machines', async route => {
      await route.fulfill({ json: [
        { accession_id: 'm1', name: 'Opentrons Flex', status: 'idle' },
        { accession_id: 'm2', name: 'Hamilton STAR', status: 'offline' }
      ]});
    });

    const complexProtocol = {
      accession_id: 'p_complex',
      name: 'Complex Protocol', // Trigger complex form logic
      description: 'Tests complex form fields',
      is_top_level: true,
      version: '1.0'
    };

    await page.route('/api/v1/protocols', async route => {
        await route.fulfill({ json: [complexProtocol] });
    });
    
    await page.route('/api/v1/runs', async route => {
        await route.fulfill({ json: { run_id: 'run_complex_123' } });
    });
  });

  test('should render and interact with complex form fields', async ({ page }) => {
    await page.goto('/run?protocolId=p_complex');
    
    await expect(page.locator('h3').first()).toContainText('Selected Protocol: Complex Protocol');
    await page.getByRole('button', { name: 'Next' }).first().click();
    
    // 1. Asset Selector
    // Click the input to trigger autocomplete
    const assetInput = page.getByPlaceholder('Search for a machine');
    await expect(assetInput).toBeVisible();
    await assetInput.click();
    await assetInput.fill('Open'); 
    // Wait for autocomplete panel
    await expect(page.locator('mat-option')).toContainText('Opentrons Flex');
    await page.locator('mat-option').first().click();
    
    // 2. Chips (Single Select)
    await expect(page.getByText('Execution Mode')).toBeVisible();
    await page.getByRole('option', { name: 'Dry Run' }).click();
    
    // 3. Repeat (Array)
    await page.getByRole('button', { name: 'Add Volume' }).click();
    await page.getByLabel('Volume (uL)').fill('100');
    
    // Add another
    await page.getByRole('button', { name: 'Add Volume' }).click();
    await page.getByLabel('Volume (uL)').nth(1).fill('200');
    
    // Remove first
    await page.locator('button[matTooltip="Remove Item"]').first().click();
    // Only one volume input should remain (value 200)
    await expect(page.getByLabel('Volume (uL)')).toHaveCount(1);
    await expect(page.getByLabel('Volume (uL)')).toHaveValue('200');

    // Next
    await page.locator('button').filter({ hasText: 'Next' }).locator('visible=true').click();
    
    // Step 3
    await page.locator('button').filter({ hasText: 'Next' }).locator('visible=true').click();
    
    // Step 4: Run
    await page.getByRole('button', { name: 'Start Execution' }).click();
  });
});