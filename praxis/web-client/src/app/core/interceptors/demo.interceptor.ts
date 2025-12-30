import { HttpRequest, HttpHandlerFn, HttpEvent, HttpResponse } from '@angular/common/http';
import { Observable, of, delay, switchMap, map } from 'rxjs';
import { inject } from '@angular/core';
import { environment } from '../../../environments/environment';
import { SqliteService } from '../services/sqlite.service';

// Import mock data for fallback
import { MOCK_PROTOCOLS } from '../../../assets/demo-data/protocols';
import { MOCK_PROTOCOL_RUNS } from '../../../assets/demo-data/protocol-runs';
import { MOCK_RESOURCES, MOCK_RESOURCE_DEFINITIONS } from '../../../assets/demo-data/resources';
import { MOCK_MACHINES } from '../../../assets/demo-data/machines';
import { PLR_RESOURCE_DEFINITIONS, PLR_MACHINE_DEFINITIONS } from '../../../assets/demo-data/plr-definitions';

const LATENCY_MS = 150;

/**
 * Check if demo mode is enabled
 */
function isDemoMode(): boolean {
    return (environment as { demo?: boolean }).demo === true;
}

/**
 * Get mock response for a given URL and method
 */
function getMockResponse(req: HttpRequest<unknown>, sqliteService: SqliteService): Observable<unknown> {
    const url = req.url;
    const method = req.method;

    // Protocol definitions - return array from SQLite
    if (url.includes('/protocols/definitions') && method === 'GET') {
        return sqliteService.getProtocols();
    }

    // Protocol runs - return array from SQLite
    if (url.includes('/protocols/runs') && method === 'GET' && !url.match(/\/protocols\/runs\/[a-f0-9-]+$/)) {
        return sqliteService.getProtocolRuns();
    }

    // Single protocol run (parse ID from URL)
    if (url.match(/\/protocols\/runs\/[a-f0-9-]+$/) && method === 'GET') {
        const id = url.split('/').pop();
        return sqliteService.getProtocolRun(id!);
    }

    // PLR Resource type definitions (comprehensive list)
    if (url.includes('/resources/type-definitions') && method === 'GET') {
        return of(PLR_RESOURCE_DEFINITIONS);
    }

    // Resource definitions (for AssetSelector filtering) - must come before /resources
    if (url.includes('/resources/definitions') && method === 'GET') {
        // Combine curated definitions with comprehensive PLR definitions
        return of([...MOCK_RESOURCE_DEFINITIONS, ...PLR_RESOURCE_DEFINITIONS]);
    }

    // Resources - return array directly
    if (url.includes('/resources') && !url.includes('type-definitions') && !url.includes('definitions') && method === 'GET') {
        return of(MOCK_RESOURCES);
    }

    // PLR Machine type definitions (comprehensive list)
    if (url.includes('/machines/type-definitions') && method === 'GET') {
        return of(PLR_MACHINE_DEFINITIONS);
    }

    // Machines - return array directly
    if (url.includes('/machines') && !url.includes('type-definitions') && !url.includes('definitions') && method === 'GET') {
        return of(MOCK_MACHINES);
    }

    // Machine definitions
    if (url.includes('/machines/definitions') && method === 'GET') {
        return of([...MOCK_MACHINES, ...PLR_MACHINE_DEFINITIONS]);
    }

    // Discovery - type definitions (trigger sync - in demo mode just return success)
    if (url.includes('/discovery/sync-all') && method === 'POST') {
        return of({
            message: 'Demo mode - PLR definitions loaded',
            synced: true,
            resources: PLR_RESOURCE_DEFINITIONS.length,
            machines: PLR_MACHINE_DEFINITIONS.length,
        });
    }

    // Discovery - get type definitions
    if (url.includes('/discovery/type-definitions') && method === 'GET') {
        return of({
            resources: PLR_RESOURCE_DEFINITIONS,
            machines: PLR_MACHINE_DEFINITIONS,
        });
    }

    // Resource facets - dynamically generated from PLR definitions
    if (url.includes('/facets')) {
        const categories = [...new Set(PLR_RESOURCE_DEFINITIONS.map(r => r.plr_category))];
        const vendors = [...new Set(PLR_RESOURCE_DEFINITIONS.map(r => r.vendor).filter(Boolean))];
        return of({
            category: categories,
            brand: vendors,
            vendor: vendors,
        });
    }

    // User info
    if (url.includes('/auth/me') || url.includes('/auth/user')) {
        return of({
            id: 'demo-user',
            username: 'demo',
            email: 'demo@praxis.example',
            roles: ['user', 'demo'],
            name: 'Demo User',
        });
    }

    // POST protocol run - simulate creation
    if (url.includes('/protocols/runs') && method === 'POST') {
        const newRun = {
            accession_id: crypto.randomUUID(),
            status: 'QUEUED',
            created_at: new Date().toISOString(),
            ...(req.body as object),
        };
        return sqliteService.createProtocolRun(newRun);
    }

    // Workcell
    if (url.includes('/workcell') && method === 'GET') {
        return of({
            name: 'Demo Workcell',
            status: 'AVAILABLE',
            machines: MOCK_MACHINES.slice(0, 2),
        });
    }

    // Scheduler - queue
    if (url.includes('/scheduler/queue') && method === 'GET') {
        return of([]);
    }

    // Decks
    if (url.includes('/decks') && method === 'GET') {
        return of([]);
    }

    // Hardware discovery
    if (url.includes('/hardware/discover') && method === 'GET') {
        const simulators = PLR_MACHINE_DEFINITIONS
            .filter(m => m.fqn.includes('simulation') || m.properties_json?.['simulated'])
            .map(m => ({
                id: `sim-${m.accession_id}`,
                name: m.name,
                connection_type: 'simulator',
                status: 'available',
                manufacturer: m.vendor || 'PyLabRobot',
                model: m.name,
                plr_backend: m.fqn,
                properties: m.properties_json,
            }));

        // Add demo hardware entries
        const demoDevices = [
            ...simulators,
            {
                id: 'demo-ot2',
                name: 'Opentrons OT-2 (Demo)',
                connection_type: 'network',
                status: 'available',
                ip_address: '192.168.1.100',
                manufacturer: 'Opentrons',
                model: 'OT-2',
                plr_backend: 'pylabrobot.liquid_handling.backends.opentrons.OT2',
                properties: { demo: true },
            },
            {
                id: 'demo-star',
                name: 'Hamilton STAR (Demo)',
                connection_type: 'serial',
                status: 'available',
                port: '/dev/ttyUSB0',
                manufacturer: 'Hamilton',
                model: 'STAR',
                plr_backend: 'pylabrobot.liquid_handling.backends.hamilton.STAR',
                properties: { demo: true },
            },
        ];

        return of({
            devices: demoDevices,
            total: demoDevices.length,
            serial_count: 1,
            simulator_count: simulators.length,
            network_count: 1,
        });
    }

    // Hardware connection (demo mode - always succeed)
    if (url.includes('/hardware/connect') && method === 'POST') {
        return of({
            device_id: (req.body as { device_id?: string })?.device_id || 'unknown',
            status: 'connected',
            message: 'Connected successfully (demo mode)',
            connection_handle: `demo-handle-${Date.now()}`,
        });
    }

    // Hardware connections list
    if (url.includes('/hardware/connections') && method === 'GET') {
        return of([]);
    }

    // Hardware registration
    if (url.includes('/hardware/register') && method === 'POST') {
        const body = req.body as { device_id?: string; name?: string; plr_backend?: string };
        return of({
            accession_id: crypto.randomUUID(),
            name: body?.name || 'Registered Machine',
            status: 'registered',
            message: `Machine '${body?.name}' registered successfully (demo mode)`,
        });
    }

    // Hardware REPL command
    if (url.includes('/hardware/repl') && method === 'POST') {
        const body = req.body as { device_id?: string; command?: string };
        return of({
            device_id: body?.device_id || 'unknown',
            command: body?.command || '',
            output: `[Demo REPL] Executed: ${body?.command}\n> OK`,
            success: true,
            error: null,
        });
    }

    return of(null);
}

/**
 * Demo HTTP Interceptor (functional style)
 *
 * In demo mode, intercepts API requests and returns mock data instead of
 * making actual network requests. This enables the application to run
 * entirely client-side without a backend.
 */
export const demoInterceptor = (req: HttpRequest<unknown>, next: HttpHandlerFn): Observable<HttpEvent<unknown>> => {
    // Only intercept in demo mode
    if (!isDemoMode()) {
        return next(req);
    }

    // Only intercept API requests
    if (!req.url.includes('/api/')) {
        return next(req);
    }

    const sqliteService = inject(SqliteService);
    const url = req.url;
    const method = req.method;

    console.log(`[DemoInterceptor] Intercepting: ${method} ${url}`);

    // Route to mock handlers
    return getMockResponse(req, sqliteService).pipe(
        delay(LATENCY_MS),
        switchMap(response => {
            if (response !== null) {
                console.log(`[DemoInterceptor] Returning mock data for: ${method} ${url}`);
                return of(new HttpResponse({
                    status: 200,
                    body: response,
                }));
            }
            // If no mock handler, log warning and return empty response
            console.warn(`[DemoInterceptor] No mock handler for: ${method} ${url}`);
            return of(new HttpResponse({
                status: 200,
                body: { message: 'Demo mode - endpoint not mocked', url, method },
            }));
        })
    );
};
