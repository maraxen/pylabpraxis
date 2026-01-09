import { HttpRequest, HttpHandlerFn, HttpEvent, HttpResponse } from '@angular/common/http';
import { Observable, of, delay, switchMap } from 'rxjs';
import { inject } from '@angular/core';
import { ModeService } from '../services/mode.service';
import { SqliteService } from '../services/sqlite.service';

// Import mock data for fallback
import { MOCK_PROTOCOL_RUNS } from '../../../assets/browser-data/protocol-runs';
import { MOCK_RESOURCES, MOCK_RESOURCE_DEFINITIONS } from '../../../assets/browser-data/resources';
import { MOCK_MACHINES } from '../../../assets/browser-data/machines';
import { PLR_RESOURCE_DEFINITIONS, PLR_MACHINE_DEFINITIONS } from '../../../assets/browser-data/plr-definitions';

const LATENCY_MS = 150;

/**
 * Get mock response for a given URL and method
 */
function getMockResponse(req: HttpRequest<unknown>, sqliteService: SqliteService): Observable<unknown> {
    const url = req.url;
    const method = req.method;

    // Protocol definitions - return list from SQLite
    if (url.includes('/protocols/definitions') && method === 'GET') {
        return sqliteService.getProtocols();
    }

    // Protocol run queue - return active/running runs
    if (url.includes('/protocols/runs/queue') && method === 'GET') {
        const activeRuns = MOCK_PROTOCOL_RUNS.filter(r =>
            ['PENDING', 'PREPARING', 'QUEUED', 'RUNNING'].includes(r.status)
        ).map(r => ({
            accession_id: r.accession_id,
            name: r.protocol_name,
            status: r.status,
            created_at: r.created_at,
            protocol_name: r.protocol_name,
        }));
        return of(activeRuns);
    }

    // Protocol run records (history) - return all runs for pagination
    if (url.includes('/protocols/runs/records') && method === 'GET') {
        // Check if this is a single record request
        const recordMatch = url.match(/\/protocols\/runs\/records\/([a-f0-9-]+)$/);
        if (recordMatch) {
            const runId = recordMatch[1];
            const run = MOCK_PROTOCOL_RUNS.find(r => r.accession_id === runId);
            if (run) {
                return of({
                    ...run,
                    name: run.protocol_name,
                    start_time: (run as any).started_at,
                    end_time: (run as any).completed_at,
                    duration_ms: run.status === 'COMPLETED' ? 262000 : null,
                    logs: [
                        'Starting protocol execution...',
                        'Initializing liquid handler...',
                        'Loading deck configuration...',
                        `Executing ${run.protocol_name}...`,
                        run.status === 'COMPLETED' ? 'Protocol completed successfully.' : 'Protocol execution in progress...',
                    ],
                });
            }
            return of(null);
        }
        // Return list with consistent field names
        return of(MOCK_PROTOCOL_RUNS.map(r => ({
            accession_id: r.accession_id,
            name: r.protocol_name,
            status: r.status,
            created_at: r.created_at,
            start_time: (r as any).started_at,
            end_time: (r as any).completed_at,
            duration_ms: r.status === 'COMPLETED' ? 262000 : null,
            protocol_name: r.protocol_name,
            protocol_accession_id: r.protocol_definition_accession_id,
        })));
    }

    // Protocol runs - return array from SQLite (legacy fallback)
    if (url.includes('/protocols/runs') && method === 'GET' && !url.match(/\/protocols\/runs\/[a-f0-9-]+$/)) {
        return sqliteService.getProtocolRuns();
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

    // Discovery - type definitions (trigger sync - in browser mode just return success)
    if (url.includes('/discovery/sync-all') && method === 'POST') {
        return of({
            message: 'Browser mode - PLR definitions loaded',
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
            id: 'local-user',
            username: 'local',
            email: 'local@praxis.local',
            roles: ['user', 'browser-mode'],
            name: 'Local User',
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
            name: 'Default Workcell',
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

        // Add simulated hardware entries
        const simulatedDevices = [
            ...simulators,
            {
                id: 'sim-ot2',
                name: 'Opentrons OT-2 (Simulated)',
                connection_type: 'network',
                status: 'available',
                ip_address: '192.168.1.100',
                manufacturer: 'Opentrons',
                model: 'OT-2',
                plr_backend: 'pylabrobot.liquid_handling.backends.opentrons.OT2',
                properties: { simulated: true },
            },
            {
                id: 'sim-star',
                name: 'Hamilton STAR (Simulated)',
                connection_type: 'serial',
                status: 'available',
                port: '/dev/ttyUSB0',
                manufacturer: 'Hamilton',
                model: 'STAR',
                plr_backend: 'pylabrobot.liquid_handling.backends.hamilton.STAR',
                properties: { simulated: true },
            },
        ];

        return of({
            devices: simulatedDevices,
            total: simulatedDevices.length,
            serial_count: 1,
            simulator_count: simulators.length,
            network_count: 1,
        });
    }

    // Hardware connection (browser mode - always succeed)
    if (url.includes('/hardware/connect') && method === 'POST') {
        return of({
            device_id: (req.body as { device_id?: string })?.device_id || 'unknown',
            status: 'connected',
            message: 'Connected successfully (browser mode)',
            connection_handle: `local-handle-${Date.now()}`,
        });
    }

    // Hardware connections list
    if (url.includes('/hardware/connections') && method === 'GET') {
        return of([]);
    }

    // Hardware registration
    if (url.includes('/hardware/register') && method === 'POST') {
        const body = req.body as { device_id?: string; name?: string; plr_backend?: string; connection_type?: string; configuration?: any };
        return sqliteService.createMachine({
            name: body?.name || 'Registered Machine',
            plr_backend: body?.plr_backend || '',
            connection_type: body?.connection_type,
            configuration: body?.configuration
        });
    }

    // Protocol compatibility check - return compatible machines
    if (url.match(/\/protocols\/[a-f0-9-]+\/compatibility$/) && method === 'GET') {
        // Return mock compatibility data with available machines
        // Filter to liquid handlers only for browser mode
        const liquidHandlers = MOCK_MACHINES.filter(m => m.type === 'liquid_handler');
        const mockCompatibility = liquidHandlers.map(machine => ({
            machine: {
                accession_id: machine.accession_id,
                name: machine.name,
                machine_type: machine.type || 'liquid_handler',
            },
            compatibility: {
                is_compatible: true,
                missing_capabilities: [],
                matched_capabilities: ['liquid_handling', 'pipetting'],
                warnings: [],
            }
        }));
        return of(mockCompatibility);
    }

    // Hardware REPL command
    if (url.includes('/hardware/repl') && method === 'POST') {
        const body = req.body as { device_id?: string; command?: string };
        return of({
            device_id: body?.device_id || 'unknown',
            command: body?.command || '',
            output: `[Browser Playground] Executed: ${body?.command}\n> OK`,
            success: true,
            error: null,
        });
    }

    return of(null);
}

/**
 * Browser Mode HTTP Interceptor (functional style)
 *
 * In browser mode, intercepts API requests and returns mock data instead of
 * making actual network requests. This enables the application to run
 * entirely client-side without a backend.
 */
export const browserModeInterceptor = (req: HttpRequest<unknown>, next: HttpHandlerFn): Observable<HttpEvent<unknown>> => {
    const modeService = inject(ModeService);

    // Only intercept in browser modes
    if (!modeService.isBrowserMode()) {
        return next(req);
    }

    // Only intercept API requests (exclude assets)
    if (!req.url.includes('/api/') || req.url.includes('assets/')) {
        return next(req);
    }

    const sqliteService = inject(SqliteService);
    const url = req.url;
    const method = req.method;

    // Route to mock handlers
    return getMockResponse(req, sqliteService).pipe(
        delay(LATENCY_MS),
        switchMap(response => {
            if (response !== null) {
                return of(new HttpResponse({
                    status: 200,
                    body: response,
                }));
            }
            // If no mock handler, log warning and return empty response
            console.warn(`[BrowserModeInterceptor] No mock handler for: ${method} ${url}`);
            return of(new HttpResponse({
                status: 200,
                body: { message: 'Browser mode - endpoint not mocked', url, method },
            }));
        })
    );
};
