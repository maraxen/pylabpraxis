import { test, expect } from '@playwright/test';

test.describe('Smoke Test', () => {
  test.beforeEach(async ({ page }) => {
    // Seed localStorage to bypass login
    await page.addInitScript(() => {
      localStorage.setItem('auth_token', 'fake-smoke-token');
      localStorage.setItem('auth_user', JSON.stringify({ username: 'smoke_user', email: 'smoke@test.com' }));
    });
  });

  test('should load the dashboard', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/PyLabPraxis/);
    await expect(page.locator('app-main-layout')).toBeVisible();
    await expect(page.locator('mat-toolbar').first()).toBeVisible();
  });

  test('should navigate to Assets and display tables', async ({ page }) => {
    await page.goto('/assets');
    await expect(page.locator('app-assets')).toBeVisible();
    
    // Check for Tabs
    await expect(page.locator('mat-tab-group')).toBeVisible();
    await expect(page.locator('.mat-mdc-tab-labels')).toContainText('Machines');
    await expect(page.locator('.mat-mdc-tab-labels')).toContainText('Resources');
    await expect(page.locator('.mat-mdc-tab-labels')).toContainText('Definitions');

    // Check Machine List (default tab)
    await expect(page.locator('app-machine-list')).toBeVisible();
    await expect(page.locator('app-machine-list table')).toBeVisible();
  });

  test('should navigate to Protocols and display library', async ({ page }) => {
    await page.goto('/protocols');
    await expect(page.locator('app-protocol-library')).toBeVisible();
    await expect(page.locator('app-protocol-library h1')).toContainText('Protocol Library');
    await expect(page.locator('app-protocol-library table')).toBeVisible();
  });

  test('should navigate to Run Protocol wizard', async ({ page }) => {
    await page.goto('/run');
    await expect(page.locator('app-run-protocol')).toBeVisible();
    
    // Check Stepper
    await expect(page.locator('mat-stepper')).toBeVisible();
    
    // Use stricter locators to avoid ambiguity
    await expect(page.locator('.mat-step-header').filter({ hasText: 'Select Protocol' })).toBeVisible();
    await expect(page.locator('.mat-step-header').filter({ hasText: 'Configure Parameters' })).toBeVisible();
  });
});