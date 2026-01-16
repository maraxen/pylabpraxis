import { chromium, type FullConfig } from '@playwright/test';
import { SEED_RESOURCES, SEED_MACHINES } from './fixtures/seed-data';

/**
 * Global setup for Playwright tests.
 * Launches a browser, navigates to the app, and seeds the SQLite database
 * with test fixtures using the exposed SqliteService.
 */
export default async function globalSetup(config: FullConfig) {
    const { baseURL } = config.projects[0].use;
    const targetUrl = baseURL || 'http://localhost:4200';

    console.log(`[Global Setup] Launching browser to seed database at ${targetUrl}...`);
    const browser = await chromium.launch();
    const page = await browser.newPage();

    try {
        // Navigate to app home to ensure services load and reduce redirect likelihood
        // Note: in browser mode, auth should be bypassed or mocked
        await page.goto(targetUrl + '/app/home');

        // Wait for the application to be stable and SqliteService to be available
        console.log('[Global Setup] Waiting for SqliteService...');
        // Poll for window.sqliteService
        try {
            await page.waitForFunction(() => (window as any).sqliteService !== undefined, null, { timeout: 15000 });
        } catch (e) {
            console.warn('[Global Setup] SqliteService not found within timeout! Seeding might fail or be skipped.');
            // Optional: dump page content or check if we are on error page
            // const title = await page.title();
            // console.log('Current page title:', title);
            // If we continue, the next step (accessing service) will fail.
            // We should probably return/throw here unless we want to assume data exists.
            // Throwing is better to be explicit.
            throw new Error('SqliteService not found on window object. Ensure app is loaded and exposing service.');
        }

        // Wait for DB initialization (isReady$)
        await page.evaluate(async () => {
            const service = (window as any).sqliteService;
            return new Promise((resolve) => {
                const sub = service.isReady$.subscribe((ready: boolean) => {
                    if (ready) {
                        sub.unsubscribe();
                        resolve(true);
                    }
                });
            });
        });

        console.log('[Global Setup] SqliteService ready. Seeding data...');

        // Seed data
        await page.evaluate(async (data) => {
            const service = (window as any).sqliteService;

            // Helper to get DB
            const getDb = () => new Promise<any>((resolve) => {
                service.getDatabase().subscribe((db: any) => resolve(db));
            });

            const db = await getDb();

            // Define seed logic
            db.exec('BEGIN TRANSACTION');

            // 1. Seed Resources
            const insertResDef = db.prepare(`
            INSERT OR IGNORE INTO resource_definitions 
            (accession_id, name, fqn, resource_type, vendor, description, properties_json, is_consumable, num_items)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        `);

            for (const r of data.resources) {
                insertResDef.run([
                    r.accession_id, r.name, r.fqn, r.resource_type, r.vendor, r.description,
                    JSON.stringify(r.properties_json), r.is_consumable ? 1 : 0, null
                ]);
            }
            insertResDef.free();

            // 2. Seed Machines
            const insertMachDef = db.prepare(`
            INSERT OR IGNORE INTO machine_definitions 
            (accession_id, name, fqn, machine_category, manufacturer, description, has_deck, properties_json, compatible_backends, capabilities_config, frontend_fqn)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `);

            for (const m of data.machines) {
                insertMachDef.run([
                    m.accession_id, m.name, m.fqn, m.machine_category, m.manufacturer, m.description,
                    m.has_deck ? 1 : 0, JSON.stringify(m.properties_json), JSON.stringify(m.compatible_backends),
                    null, null
                ]);
            }
            insertMachDef.free();

            db.exec('COMMIT');

            // Explicitly trigger persistence
            // Accessing private method via loose typing
            if (typeof service.saveToStore === 'function') {
                console.log('[Global Setup - Browser] Saving to store...');
                await service.saveToStore(db);
            } else {
                console.warn('[Global Setup - Browser] saveToStore method not found!');
            }

        }, { resources: SEED_RESOURCES, machines: SEED_MACHINES });

        console.log('[Global Setup] Seeding complete.');

    } catch (error) {
        console.error('[Global Setup] Failed to seed database:', error);
        throw error;
    } finally {
        await browser.close();
    }
}
