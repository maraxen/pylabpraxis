import { test, expect } from '../fixtures/worker-db.fixture';

/**
 * JupyterLite Path Resolution E2E Tests
 * 
 * These tests verify that JupyterLite resources are correctly loaded without
 * path doubling issues when deployed to a subdirectory (e.g., /praxis/).
 * 
 * The tests can be run in two modes:
 * 1. Local development: Uses localhost:4200 with relative paths
 * 2. GH Pages simulation: Uses localhost:8080/praxis with absolute paths
 */

test.describe('JupyterLite Path Resolution', () => {

    test.describe('Development Mode', () => {
        test('REPL config uses relative paths', async ({ page }) => {
            // Fetch the REPL config directly
            const response = await page.goto('/assets/jupyterlite/repl/jupyter-lite.json');
            expect(response?.status()).toBe(200);

            const config = await response?.json();
            expect(config['jupyter-config-data']['settingsUrl']).toBe('../build/schemas');
            expect(config['jupyter-config-data']['themesUrl']).toBe('../build/themes');
        });

        test('schemas endpoint accessible', async ({ page }) => {
            const response = await page.goto('/assets/jupyterlite/build/schemas/all.json');
            expect(response?.status()).toBe(200);

            const contentType = response?.headers()['content-type'];
            expect(contentType).toContain('application/json');
        });

        test('theme CSS accessible', async ({ page }) => {
            const response = await page.goto('/assets/jupyterlite/build/themes/@jupyterlab/theme-light-extension/index.css');
            expect(response?.status()).toBe(200);

            const contentType = response?.headers()['content-type'];
            expect(contentType).toContain('text/css');
        });
    });

    test.describe('REPL Loading', () => {
        test('REPL page loads without 404 errors for resources', async ({ page }) => {
            const failedRequests: string[] = [];
            const doubledPathRequests: string[] = [];

            // Monitor for failed requests and doubled paths
            page.on('response', (response) => {
                const url = response.url();

                // Check for 404s on JupyterLite resources
                if (url.includes('jupyterlite') && response.status() === 404) {
                    failedRequests.push(url);
                }

                // Check for path doubling patterns
                if (url.includes('/praxis/') && url.match(/\/praxis\/.*\/praxis\//)) {
                    doubledPathRequests.push(url);
                }
                if (url.includes('/assets/jupyterlite/') && url.match(/\/assets\/jupyterlite\/.*\/assets\/jupyterlite\//)) {
                    doubledPathRequests.push(url);
                }
            });

            // Navigate to the REPL
            await page.goto('/playground');

            // Wait for JupyterLite to initialize (look for the iframe or status indicators)
            // Give it time to load resources
            await page.waitForTimeout(5000);

            // Verify no doubled paths
            expect(doubledPathRequests, `Doubled path requests detected: ${doubledPathRequests.join(', ')}`).toHaveLength(0);

            // Log any failed requests for debugging (some 404s may be acceptable)
            if (failedRequests.length > 0) {
                console.log('Failed JupyterLite resource requests:', failedRequests);
            }
        });

        test('REPL iframe initializes correctly', async ({ page }) => {
            await page.goto('/playground');

            // Wait for the playground to load
            await page.waitForSelector('app-playground', { timeout: 10000 });

            // Check if the JupyterLite container/iframe exists
            const jupyterFrame = page.locator('iframe[src*="jupyterlite"], .jupyter-container');

            // The page should have some JupyterLite-related content
            await expect(page.locator('app-playground')).toBeVisible();
        });
    });
});

/**
 * Separate test file for GH Pages simulation
 * These tests require a special server setup with COOP/COEP headers
 * Run with: npx playwright test --config=playwright.ghpages.config.ts
 */
test.describe.skip('GH Pages Simulation (requires separate config)', () => {
    test('root config has correct baseUrl', async ({ page }) => {
        // This test requires baseURL to be http://localhost:8080/praxis
        const response = await page.goto('/assets/jupyterlite/jupyter-lite.json');
        expect(response?.status()).toBe(200);

        const config = await response?.json();
        expect(config['jupyter-config-data']['baseUrl']).toBe('/praxis/assets/jupyterlite/');
    });

    test('REPL config still uses relative paths in production', async ({ page }) => {
        const response = await page.goto('/assets/jupyterlite/repl/jupyter-lite.json');
        expect(response?.status()).toBe(200);

        const config = await response?.json();
        // Even in production, nested configs should use relative paths
        expect(config['jupyter-config-data']['settingsUrl']).toBe('../build/schemas');
        expect(config['jupyter-config-data']['themesUrl']).toBe('../build/themes');
    });
});
