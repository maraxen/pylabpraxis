import { test, expect } from '../fixtures/app.fixture';

test.describe('Smoke Test', () => {
  // Common setup (auth, navigation, shell wait, dialog dismissal) is now handled by app.fixture.ts

  // Common setup (auth, navigation, shell wait, dialog dismissal) is now handled by app.fixture.ts


  test('should load the dashboard', async ({ page }) => {
    // page.goto('/') handled in beforeEach, which also handles redirects
    await expect(page).toHaveTitle(/Praxis/);
    await page.waitForLoadState('networkidle');
    await expect(page.locator('app-unified-shell, app-main-layout')).toBeVisible({ timeout: 30000 });
    await expect(page.locator('.sidebar-rail, .nav-rail').first()).toBeVisible();
    await page.screenshot({ path: '/tmp/e2e-smoke/landing_dashboard.png' });
  });

  test('should navigate to Assets and display tables', async ({ page }) => {
    await page.goto('/assets');
    await page.waitForLoadState('networkidle');
    await expect(page.locator('app-assets')).toBeVisible({ timeout: 30000 });

    // Check for Tabs
    await expect(page.locator('mat-tab-group')).toBeVisible();
    await expect(page.locator('.mat-mdc-tab-labels')).toContainText('Machines');
    await expect(page.locator('.mat-mdc-tab-labels')).toContainText('Resources');
    await expect(page.locator('.mat-mdc-tab-labels')).toContainText('Registry');

    // Check Machine List (navigate to tab first)
    await page.getByRole('tab', { name: /Machines/i }).click();
    await expect(page.locator('app-machine-list')).toBeVisible({ timeout: 30000 });
    await expect(page.locator('app-machine-list table')).toBeVisible();
    await page.screenshot({ path: '/tmp/e2e-smoke/assets_list.png' });
  });

  test('should navigate to Protocols and display library', async ({ page }) => {
    await page.goto('/protocols');
    await expect(page.locator('app-protocol-library')).toBeVisible();
    await expect(page.locator('app-protocol-library h1')).toContainText('Protocol Library');
    await expect(page.locator('app-protocol-library table')).toBeVisible();
    await page.screenshot({ path: '/tmp/e2e-smoke/protocol_list.png' });
  });

  test('should navigate to Run Protocol wizard', async ({ page }) => {
    await page.goto('/run');
    await expect(page.locator('app-run-protocol')).toBeVisible();

    // Check Stepper
    await expect(page.locator('mat-stepper')).toBeVisible();

    // Use stricter locators to avoid ambiguity
    await expect(page.locator('.mat-step-header').filter({ hasText: 'Select Protocol' })).toBeVisible();
    await expect(page.locator('.mat-step-header').filter({ hasText: 'Configure Parameters' })).toBeVisible();
    await page.screenshot({ path: '/tmp/e2e-smoke/run_protocol.png' });
  });
});