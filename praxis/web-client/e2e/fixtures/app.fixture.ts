import { test as base, expect } from '@playwright/test';

/**
 * Custom Playwright fixture that provides a pre-initialized page state.
 * Handles app shell loading, welcome dialog dismissal, tour disabling,
 * and waiting for overlays to clear.
 */
export const test = base.extend({});

test.beforeEach(async ({ page }) => {
    // 4. Sets localStorage flags to disable tours and seed auth
    await page.addInitScript(() => {
        localStorage.setItem('praxis_tour_finished', 'true');
        localStorage.setItem('praxis_onboarding_seen', 'true');
        // Common smoke test auth bypass
        if (!localStorage.getItem('auth_token')) {
            localStorage.setItem('auth_token', 'fake-smoke-token');
            localStorage.setItem('auth_user', JSON.stringify({
                username: 'smoke_user',
                email: 'smoke@test.com'
            }));
        }
    });

    // Navigate to root to start the app sequence
    // If the test has its own goto, it will follow this one.
    await page.goto('/');

    // 1. Wait for app shell to load (check for .sidebar-rail)
    // This ensures the Angular app is bootstrapped and the layout is ready.
    await expect(page.locator('.sidebar-rail')).toBeVisible({ timeout: 30000 });

    // 2. Detect and dismiss "Welcome to Praxis" dialog if present
    const welcomeDialog = page.getByRole('dialog', { name: /Welcome to Praxis/i });
    try {
        // Use a short timeout to check for existence without stalling
        if (await welcomeDialog.isVisible({ timeout: 5000 })) {
            console.log('[Fixture] Dismissing Welcome Dialog...');
            // Try to click any button that looks like a dismissal
            const dismissButton = page.getByRole('button', { name: /Skip for Now|Close|Get Started|Dismiss/i }).first();
            await dismissButton.click();
            await expect(welcomeDialog).not.toBeVisible();
        }
    } catch (e) {
        // Dialog might not be present or already gone
    }

    // 3. Wait for CDK overlays to clear
    // Important for preventing click interception errors in subsequent steps
    await expect(page.locator('.cdk-overlay-backdrop')).not.toBeVisible({ timeout: 10000 });
});

export { expect };
