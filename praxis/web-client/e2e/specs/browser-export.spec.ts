import { test, expect } from '../fixtures/worker-db.fixture';
import * as path from 'path';

test.describe('Browser Mode Database Export', () => {
    test.beforeEach(async ({ page }) => {
        // Navigate to Settings page directly
        await page.goto('/app/settings');

    // Handle welcome dialog if it appears
    const welcomeDialog = page.getByRole('dialog', { name: 'Welcome to Praxis' });
    if (await welcomeDialog.isVisible()) {
      await page.getByRole('button', { name: 'Skip for Now' }).click();
    }

        // Ensure the page is loaded by checking for the header
        await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible({ timeout: 15000 });
    });

    test('Export Database triggers download', async ({ page }) => {
        // Locate the Export button
        const exportBtn = page.getByRole('button', { name: 'Export Database' });
        await expect(exportBtn).toBeVisible();

        // Setup download listener before clicking
        const downloadPromise = page.waitForEvent('download');

        // Click export
        await exportBtn.click();

        const download = await downloadPromise;

// Verify filename format (e.g. praxis-backup-YYYY-MM-DD...)
expect(download.suggestedFilename()).toContain('praxis-backup');
        expect(download.suggestedFilename()).toContain('.db');

        // Verify success snackbar
        await expect(page.getByText('Database exported')).toBeVisible();
    });

    // Note: Import test is trickier due to page reload and destructive nature,
    // but we can at least verify the implementation exists and opens the dialog.
    test('Import Database opens confirmation dialog', async ({ page }) => {
        // We can't easily upload a file without a real file input interaction, 
        // but the input is hidden. We can interact with the visible button which triggers the hidden input click.
        // Playwright handles file chooser events.

        // Create a dummy file
        const fileContent = 'dummy db content';
        const fileName = 'test_backup.db';

        // Start waiting for file chooser
        const fileChooserPromise = page.waitForEvent('filechooser');

        // Click the "Import Database" button (which clicks the hidden input)
        await page.getByRole('button', { name: 'Import Database' }).click();

        const fileChooser = await fileChooserPromise;

        // Set files (but don't actually modify the db unless we want to break the test env)
        // IMPORTANT: If we proceed, it will wipe the DB. For this test, we might stop at the dialog.
        // However, the dialog only appears AFTER file selection.

        // We'll proceed with selection but CANCEL the confirmation dialog to be safe.
        await fileChooser.setFiles({
            name: fileName,
            mimeType: 'application/x-sqlite3',
            buffer: Buffer.from(fileContent)
        });

        // Check for confirmation dialog
        const dialog = page.locator('app-confirmation-dialog');
        await expect(dialog).toBeVisible();
        await expect(dialog).toContainText('Import Database?');

        // Cancel
        await page.getByRole('button', { name: 'Cancel' }).click();
        await expect(dialog).toBeHidden();
    });
});
