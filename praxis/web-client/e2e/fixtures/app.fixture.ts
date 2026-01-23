import { test as base, expect } from '@playwright/test';

/**
 * Custom Playwright fixture that provides a pre-initialized page state.
 * Handles app shell loading, welcome dialog dismissal, tour disabling,
 * and waiting for overlays to clear.
 */
export const test = base.extend({});

test.beforeEach(async ({ page }) => {
    // 1. Set comprehensive localStorage flags BEFORE page load to prevent dialogs/tours
    await page.addInitScript(() => {
        // Welcome dialog / Onboarding flags - set ALL possible variants
        localStorage.setItem('praxis_tour_finished', 'true');
        localStorage.setItem('praxis_onboarding_seen', 'true');
        localStorage.setItem('praxis_onboarding_complete', 'true');
        localStorage.setItem('praxis_welcome_dialog_dismissed', 'true');
        localStorage.setItem('praxis_welcome_shown', 'true');

        // Disable any pending tutorials
        localStorage.removeItem('praxis_pending_tutorial');

        // Common smoke test auth bypass
        if (!localStorage.getItem('auth_token')) {
            localStorage.setItem('auth_token', 'fake-smoke-token');
            localStorage.setItem('auth_user', JSON.stringify({
                username: 'smoke_user',
                email: 'smoke@test.com'
            }));
        }
    });

    // 2. Navigate to root to start the app sequence
    await page.goto('/');

    // 3. Wait for app shell to load (check for .sidebar-rail)
    await expect(page.locator('.sidebar-rail')).toBeVisible({ timeout: 30000 });

    // 4. Robust Welcome Dialog dismissal with retry logic
    // Even with localStorage flags, dialog may appear due to race conditions
    const dismissWelcomeDialog = async (maxRetries = 3): Promise<void> => {
        for (let attempt = 0; attempt < maxRetries; attempt++) {
            // Check for dialog presence with short timeout
            const dialogVisible = await page.getByRole('dialog', { name: /Welcome to Praxis/i })
                .isVisible({ timeout: 1000 })
                .catch(() => false);

            if (!dialogVisible) {
                return; // No dialog, we're good
            }

            console.log(`[Fixture] Dismissing Welcome Dialog (attempt ${attempt + 1})...`);

            // Try multiple button patterns
            const buttonPatterns = [
                page.getByRole('button', { name: /Skip for Now/i }),
                page.getByRole('button', { name: /Close/i }),
                page.getByRole('button', { name: /Get Started/i }),
                page.getByRole('button', { name: /Dismiss/i }),
                page.locator('mat-dialog-actions button').first(),
            ];

            for (const btn of buttonPatterns) {
                if (await btn.isVisible({ timeout: 500 }).catch(() => false)) {
                    await btn.click({ force: true });
                    await page.waitForTimeout(300);
                    break;
                }
            }

            // Verify dialog is gone
            const stillVisible = await page.getByRole('dialog', { name: /Welcome to Praxis/i })
                .isVisible({ timeout: 500 })
                .catch(() => false);

            if (!stillVisible) {
                return; // Successfully dismissed
            }
        }
    };

    await dismissWelcomeDialog();

    // 5. Wait for CDK overlays to clear (prevents click interception)
    await expect(page.locator('.cdk-overlay-backdrop')).not.toBeVisible({ timeout: 10000 });
});

export { expect };
