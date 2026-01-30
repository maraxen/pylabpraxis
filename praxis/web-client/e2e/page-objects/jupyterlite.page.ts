import { Page, FrameLocator, Locator, expect } from '@playwright/test';

/**
 * Page Object Model for JupyterLite iframe interactions.
 *
 * Handles the embedded JupyterLite notebook iframe including:
 * - Frame attachment and kernel readiness
 * - Dialog dismissal (theme errors, kernel select, etc.)
 * - Code execution via the console input
 */
export class JupyterlitePage {
    readonly page: Page;
    readonly frame: FrameLocator;
    readonly codeInput: Locator;
    readonly kernelIdleIndicator: Locator;
    readonly dialog: Locator;

    constructor(page: Page) {
        this.page = page;
        this.frame = page.frameLocator('iframe.notebook-frame');
        this.codeInput = this.frame.locator('.jp-CodeConsole-input .jp-InputArea-editor');
        this.kernelIdleIndicator = this.frame.locator('.jp-mod-idle').first();
        this.dialog = this.frame.locator('.jp-Dialog');
    }

    /**
     * Wait for the JupyterLite iframe to be attached and visible.
     */
    async waitForFrameAttached(timeout = 20000): Promise<void> {
        const frameElement = this.page.locator('iframe.notebook-frame');
        await expect(frameElement).toBeVisible({ timeout });
    }

    /**
     * Wait for the kernel to become idle (ready for execution).
     */
    async waitForKernelIdle(timeout = 45000): Promise<void> {
        await this.kernelIdleIndicator.waitFor({ timeout, state: 'visible' });
    }

    /**
     * Dismiss any visible JupyterLite dialogs (theme errors, kernel selection, etc.).
     * Uses state-driven waits, not hardcoded timeouts.
     */
    async dismissDialogs(maxAttempts = 3): Promise<void> {
        for (let i = 0; i < maxAttempts; i++) {
            try {
                const okButton = this.frame.getByRole('button', { name: 'OK' });
                if (await okButton.isVisible({ timeout: 1000 })) {
                    await okButton.click();
                    console.log('[JupyterlitePage] Dismissed dialog');
                    await this.dialog.waitFor({ state: 'hidden', timeout: 2000 }).catch((e) => console.log('[Test] Silent catch (Dialog waitFor hidden):', e));
                } else {
                    break; // No visible dialog
                }
            } catch (e) {
                console.log('[Test] Caught (Dismiss dialogs):', (e as Error).message);
                break; // No more dialogs or timeout
            }
        }
    }

    /**
     * Execute code in the JupyterLite console.
     * Dismisses dialogs first and waits for code input to be ready.
     */
    async executeCode(code: string): Promise<void> {
        await this.dismissDialogs();
        await expect(this.codeInput).toBeVisible();
        await this.codeInput.click();
        await this.page.keyboard.type(code);
        await this.page.keyboard.press('Shift+Enter');
    }

    /**
     * Assert that no kernel selection dialog is visible.
     * Useful for verifying seamless bootstrap.
     */
    async assertKernelDialogNotVisible(timeout = 5000): Promise<void> {
        const kernelDialog = this.dialog.filter({ hasText: /kernel|select/i });
        await expect(kernelDialog).not.toBeVisible({ timeout });
    }
}
