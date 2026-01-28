// Test script to diagnose SQLite OPFS loading
// Run from: cd $SKILL_DIR && node run.js /tmp/playwright-test-db.js

const { chromium } = require('playwright');

const TARGET_URL = 'http://localhost:4200/app/protocols?mode=browser';

(async () => {
    const browser = await chromium.launch({ headless: false, slowMo: 100 });
    const context = await browser.newContext();
    const page = await context.newPage();

    // Capture console logs
    const logs = [];
    page.on('console', msg => {
        const text = msg.text();
        logs.push(`[${msg.type()}] ${text}`);
        if (text.includes('SqliteOpfsService') || text.includes('protocol')) {
            console.log(`BROWSER: ${text}`);
        }
    });

    console.log('Navigating to:', TARGET_URL);
    await page.goto(TARGET_URL, { waitUntil: 'networkidle', timeout: 60000 });

    // Wait for database initialization
    await page.waitForTimeout(5000);

    // Check the protocol count via the service
    const diagnostics = await page.evaluate(async () => {
        const results = {
            sqliteServiceExists: !!window.sqliteService,
            isReady: false,
            protocolCount: 'unknown',
            error: null
        };

        if (window.sqliteService) {
            try {
                results.isReady = window.sqliteService.isReady$.getValue();

                // Get protocols via subscription
                const protocols = await new Promise((resolve, reject) => {
                    const timeout = setTimeout(() => resolve({ count: 'timeout', protocols: [] }), 10000);
                    const sub = window.sqliteService.getProtocols().subscribe({
                        next: (p) => {
                            clearTimeout(timeout);
                            sub.unsubscribe();
                            resolve({ count: p.length, protocols: p.map(pr => pr.name) });
                        },
                        error: (err) => {
                            clearTimeout(timeout);
                            resolve({ count: 'error', error: err.message });
                        }
                    });
                });

                results.protocolCount = protocols.count;
                results.protocolNames = protocols.protocols;
                if (protocols.error) results.error = protocols.error;
            } catch (e) {
                results.error = e.message;
            }
        }

        return results;
    });

    console.log('\n=== Database Diagnostics ===');
    console.log('Service exists:', diagnostics.sqliteServiceExists);
    console.log('Is ready:', diagnostics.isReady);
    console.log('Protocol count:', diagnostics.protocolCount);
    console.log('Protocol names:', diagnostics.protocolNames);
    if (diagnostics.error) console.log('Error:', diagnostics.error);

    // Take screenshot
    await page.screenshot({ path: '/tmp/protocol-debug.png', fullPage: true });
    console.log('\n📸 Screenshot saved to /tmp/protocol-debug.png');

    // Print relevant logs
    console.log('\n=== Relevant Console Logs ===');
    logs.filter(l => l.includes('SqliteOpfsService') || l.includes('protocol') || l.includes('praxis.db'))
        .forEach(l => console.log(l));

    await browser.close();
})();
