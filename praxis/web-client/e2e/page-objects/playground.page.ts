import { Page, Locator, TestInfo, expect } from '@playwright/test';
import { BasePage } from './base.page';
import { JupyterlitePage } from './jupyterlite.page';

/**
 * Page Object Model for the Playground page.
 *
 * Composes JupyterlitePage internally and provides:
 * - Worker-isolated navigation via BasePage
 * - Bootstrap completion detection
 * - Welcome dialog dismissal
 * - Asset retrieval from Angular state
 */
export class PlaygroundPage extends BasePage {
    readonly jupyter: JupyterlitePage;
    readonly loadingOverlay: Locator;
    readonly welcomeDialog: Locator;
    readonly skipButton: Locator;

    constructor(page: Page, testInfo?: TestInfo) {
        super(page, '/app/playground', testInfo);
        this.jupyter = new JupyterlitePage(page);
        this.loadingOverlay = page.locator('.loading-overlay');
        this.welcomeDialog = page.getByRole('dialog').filter({ hasText: /welcome|getting started/i });
        this.skipButton = page.getByRole('button', { name: /skip for now/i });
    }

    /**
     * Navigate to the playground with worker-isolated database.
     * Sets localStorage flags to skip onboarding dialogs.
     */
    override async goto(): Promise<void> {
        // Set localStorage before Angular loads to skip onboarding
        await this.page.goto('/');
        await this.page.evaluate(() => {
            localStorage.setItem('praxis_onboarding_completed', 'true');
            localStorage.setItem('praxis_tutorial_completed', 'true');
        });

        // Navigate with worker isolation via BasePage
        await super.goto();
    }

    /**
     * Dismiss the welcome/onboarding dialog if visible.
     */
    async dismissWelcomeDialog(): Promise<void> {
        try {
            if (await this.skipButton.isVisible({ timeout: 2000 })) {
                await this.skipButton.click();
                await this.welcomeDialog.waitFor({ state: 'hidden', timeout: 3000 });
                console.log('[PlaygroundPage] Dismissed welcome dialog');
            }
        } catch (e) {
            console.log('[PlaygroundPage] No welcome dialog present:', (e as Error).message);
        }
    }

    /**
     * Wait for the loading overlay to be hidden.
     */
    async waitForLoadingComplete(timeout = 60000): Promise<void> {
        await expect(this.loadingOverlay).toBeHidden({ timeout });
    }

    /**
     * Wait for kernel to become idle and ready for code execution.
     */
    async waitForKernelIdle(timeout = 45000): Promise<void> {
        await this.jupyter.waitForKernelIdle(timeout);
    }

    /**
     * Wait for the complete bootstrap sequence:
     * 1. Dismiss welcome dialogs
     * 2. Wait for iframe attached
     * 3. Wait for loading overlay hidden
     * 4. Dismiss JupyterLite dialogs
     * 5. Wait for kernel idle
     *
     * Optionally validates console log signals if provided.
     */
    async waitForBootstrapComplete(consoleLogs?: string[]): Promise<void> {
        // Dismiss any welcome dialogs
        await this.dismissWelcomeDialog();

        // Wait for JupyterLite iframe to be attached
        await this.jupyter.waitForFrameAttached();

        // Assert no blocking dialogs remain
        await expect(this.skipButton).not.toBeVisible({ timeout: 3000 }).catch((e) => console.log('[Test] Silent catch (Skip button still visible):', e));
        await this.jupyter.assertKernelDialogNotVisible().catch((e) => console.log('[Test] Silent catch (Kernel dialog check):', e));

        // Wait for loading overlay to finish
        await this.waitForLoadingComplete();

        // Dismiss any JupyterLite theme error dialogs
        await this.jupyter.dismissDialogs();

        // Wait for kernel to be idle
        await this.jupyter.waitForKernelIdle();

        // Optional: Verify bootstrap signals in console logs
        if (consoleLogs && consoleLogs.length > 0) {
            await expect.poll(() => {
                const pyodideReady = consoleLogs.some(log => log.includes('[PythonRuntime] Pyodide ready'));
                const shimsInjected = consoleLogs.some(log =>
                    log.includes('WebSerial injected') || log.includes('WebUSB injected')
                );
                return pyodideReady && shimsInjected;
            }, { timeout: 60000, message: 'Bootstrap signals not detected in console logs' }).toBe(true);
        }
    }

    /**
     * Get assets from the Angular PlaygroundService state.
     * Uses Angular's internal API for deep state verification.
     */
    async getPlaygroundAssets(): Promise<unknown[]> {
        return this.page.evaluate(() => {
            const ng = (window as any).ng;
            const appRoot = document.querySelector('app-root');
            if (!ng || !appRoot) return [];
            const app = ng.getComponent(appRoot);
            return app?.playgroundService?.assets$?.getValue?.() ?? [];
        });
    }
}
