import { test, expect } from '@playwright/test';
import { MonitorPage } from '../page-objects/monitor.page';

test.describe('Run Detail View', () => {
  let monitorPage: MonitorPage;

  test.beforeEach(async ({ page }) => {
    monitorPage = new MonitorPage(page);
    await monitorPage.goto();
  });

  test('navigates to the run detail page', async ({ page }) => {
    const firstRun = monitorPage.getFirstRun();
    await expect(firstRun).toBeVisible();

    const runId = await monitorPage.getRunId(firstRun);
    await firstRun.click();

    await monitorPage.verifyRunDetails(runId);
  });

  test('displays an error for an invalid run ID', async ({ page }) => {
    await page.goto('/app/monitor/invalid-run-id');
    await expect(page.getByText('Run not found')).toBeVisible();
  });
});
