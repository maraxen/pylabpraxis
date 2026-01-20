import { chromium, type FullConfig } from '@playwright/test';

/**
 * Global setup for Playwright tests.
 * Launches a browser to verify the application loads and SqliteService initializes.
 * 
 * NOTE: Tests use resetdb=1 which wipes the database, so global seeding here 
 * would be lost. This setup serves as a smoke test to ensure the environment is ready.
 */
export default async function globalSetup(config: FullConfig) {
    const { baseURL } = config.projects[0].use;
    const targetUrl = baseURL || 'http://localhost:4200';

    console.log(`[Global Setup] Verifying application readiness at ${targetUrl}...`);
    const browser = await chromium.launch();
    const page = await browser.newPage();

    try {
        // Navigate to app home with browser mode param to ensure services load
        // Increased timeout to 60s for CI environments
        await page.goto(targetUrl + '/app/home?mode=browser', { 
            waitUntil: 'networkidle', 
            timeout: 60000 
        });

        // Wait for the application to be stable and SqliteService to be available
        console.log('[Global Setup] Waiting for SqliteService...');
        try {
            await page.waitForFunction(() => (window as any).sqliteService !== undefined, null, { timeout: 60000 });
        } catch (e) {
            throw new Error('[Global Setup] CRITICAL: SqliteService not found! The application failed to initialize properly.');
        }

        // Wait for DB initialization (isReady$)
        console.log('[Global Setup] Waiting for database initialization...');
        const isReady = await page.evaluate(async () => {
            const service = (window as any).sqliteService;
            if (!service) return false;
            
            return new Promise((resolve) => {
                const sub = service.isReady$.subscribe((ready: boolean) => {
                    if (ready) {
                        sub.unsubscribe();
                        resolve(true);
                    }
                });
                
                // Timeout fallback within evaluate
                setTimeout(() => {
                    sub.unsubscribe();
                    resolve(false);
                }, 55000);
            });
        });

        if (!isReady) {
            throw new Error('[Global Setup] CRITICAL: SqliteService failed to reach ready state within timeout.');
        }

        console.log('[Global Setup] Success: Application and database are ready.');

    } catch (error) {
        console.error('[Global Setup] FATAL ERROR during environment setup:');
        console.error(error);
        // Throw error to ensure Playwright aborts the test run
        throw error;
    } finally {
        await browser.close();
    }
}
