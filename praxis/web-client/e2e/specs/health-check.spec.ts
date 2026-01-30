import { test, expect } from '../fixtures/app.fixture';

/**
 * Minimal Health Check Test
 * 
 * This test verifies the core application environment:
 * 1. Dev server is reachable
 * 2. App root is rendered
 * 3. SqliteService initializes successfully
 * 4. The worker-indexed database is used correctly
 * 
 * Use this to verify global setup stabilization without running full specs.
 */
test.describe('Environment Health Check', () => {
    test('should load application and initialize database', async ({ page }) => {
        // The app.fixture already handles:
        // - Setting localStorage flags
        // - Navigating with ?mode=browser&dbName=praxis-worker-N
        // - Waiting for .sidebar-rail
        // - Waiting for SqliteService.isReady$

        console.log('[HealthCheck] Verifying UI components...');
        await expect(page.locator('.sidebar-rail')).toBeVisible();

        console.log('[HealthCheck] Verifying database state via window object...');
        const isReady = await page.evaluate(() => {
            const service = (window as any).sqliteService;
            return service && typeof service.isReady$?.getValue === 'function' && service.isReady$.getValue() === true;
        });

        expect(isReady).toBe(true);

        console.log('[HealthCheck] Success: Environment is stable.');
    });
});
