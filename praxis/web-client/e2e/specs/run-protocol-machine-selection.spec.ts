import { test, expect } from '../fixtures/worker-db.fixture';

test.describe('Run Protocol - Machine Selection', () => {
    test.beforeEach(async ({ page }) => {
        // Clear storage to ensure clean state and simulate first-time browser mode user
        await page.goto('/');
        await page.evaluate(() => {
            localStorage.clear();
            // Optional: force browser mode in storage as well
            localStorage.setItem('praxis_mode', 'browser');
            localStorage.setItem('praxis_mode_override', 'browser');
        });
    });

    test('should navigate to run-protocol and select a simulated machine', async ({ page }) => {
        // 1. Navigating to run-protocol page (/run-protocol)
        // Use browser mode: ?mode=browser
        await page.goto('/run-protocol?mode=browser', { waitUntil: 'networkidle' });

        // Handle splash screens/onboarding
        // The welcome dialog often appears for first-time users in browser mode
        const welcomeHeading = page.getByRole('heading', { name: /Welcome to Praxis/i });
        if (await welcomeHeading.isVisible({ timeout: 5000 }).catch((e) => {
            console.log('[Test] Silent catch (welcomeHeading isVisible):', e);
            return false;
        })) {
            await page.getByRole('button', { name: /Skip/i }).click();
        }

        // 2. Verifying machine selection step is visible
        // First, we must select a protocol to advance through the stepper
        const protocolCard = page.locator('app-protocol-card').first();
        await expect(protocolCard).toBeVisible({ timeout: 15000 });
        await protocolCard.click();

        // Move from Step 1 (Protocol) to Step 2 (Parameters)
        const continueToParams = page.getByRole('button', { name: /Continue/i }).last();
        await expect(continueToParams).toBeVisible();
        await continueToParams.click();

        // Move from Step 2 (Parameters) to Step 3 (Machine Selection)
        const continueToMachine = page.getByRole('button', { name: /Continue/i }).last();
        await expect(continueToMachine).toBeVisible();
        await continueToMachine.click();

        // Verify machine selection step is visible
        const machineStep = page.locator('[data-tour-id="run-step-machine"]');
        await expect(machineStep).toBeVisible();
        await expect(page.getByText(/Select Execution Machine/i)).toBeVisible();

        // 3. Checking that simulated machines show "Simulated" indicator
        // In browser mode, machines are mocked as simulated
        const simulatedIndicator = page.getByText('Simulated').first();
        await expect(simulatedIndicator).toBeVisible();

        // 4. Selecting a machine for protocol execution
        // Click a machine card that is simulated
        const machineCard = page.locator('app-machine-card').filter({ hasText: /Simulated/i }).first();
        await machineCard.click();

        // Verify selection visual feedback (class border-primary is added on selection)
        await expect(machineCard).toHaveClass(/border-primary/);

        // Verify the "Continue" button for the machine step is now enabled
        const continueFromMachine = machineStep.getByRole('button', { name: /Continue/i });
        await expect(continueFromMachine).toBeEnabled();
    });
});
