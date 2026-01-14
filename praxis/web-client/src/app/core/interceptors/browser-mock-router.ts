/**
 * Browser Mock Router
 * 
 * Centralizes mock data routing for browser mode.
 * Extracts the routing logic from the HTTP interceptor to be reusable
 * by both the interceptor (for HttpClient requests) and the request.ts
 * (for generated API client requests that use native fetch).
 * 
 * IMPORTANT: This class can be used in two contexts:
 * 1. Via Angular DI (when sqliteService is passed in)
 * 2. Via direct instantiation (when called from request.ts outside DI)
 * 
 * In the second case, we lazy-load SqliteService ourselves.
 */

import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { SqliteService } from '../services/sqlite.service';

// Import mock data
import { MOCK_PROTOCOL_RUNS } from '../../../assets/browser-data/protocol-runs';
import { MOCK_RESOURCES, MOCK_RESOURCE_DEFINITIONS } from '../../../assets/browser-data/resources';
import { MOCK_MACHINES } from '../../../assets/browser-data/machines';
import { PLR_RESOURCE_DEFINITIONS, PLR_MACHINE_DEFINITIONS } from '../../../assets/browser-data/plr-definitions';

// Singleton instance for non-DI contexts
let _sqliteServiceInstance: SqliteService | null = null;
function getSqliteService(): SqliteService {
    if (!_sqliteServiceInstance) {
        _sqliteServiceInstance = new SqliteService();
    }
    return _sqliteServiceInstance;
}

@Injectable({
    providedIn: 'root'
})
export class BrowserMockRouter {
    /**
     * Route a request to the appropriate mock handler.
     * Returns null if no handler is found.
     * 
     * @param url - The request URL
     * @param method - The HTTP method
     * @param body - The request body (for POST/PUT)
     * @param sqliteService - SqliteService instance (can be null, will lazy-load)
     */
    route<T>(
        url: string,
        method: string,
        body: unknown,
        sqliteService: SqliteService | null
    ): Observable<T> | null {
        // Lazy-load SqliteService if not provided
        const db = sqliteService ?? getSqliteService();

        // Protocol definitions - return list from SQLite
        if (url.includes('/protocols/definitions') && method === 'GET') {
            return db.getProtocols() as Observable<T>;
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
            return of(activeRuns) as Observable<T>;
        }

        // Protocol run records (history) - return all runs for pagination
        if (url.includes('/protocols/runs/records') && method === 'GET') {
            const recordMatch = url.match(/\/protocols\/runs\/records\/([a-f0-9-]+)$/);
            if (recordMatch) {
                const runId = recordMatch[1];
                const run = MOCK_PROTOCOL_RUNS.find(r => r.accession_id === runId);
                if (run) {
                    return of({
                        ...run,
                        name: run.protocol_name,
                        start_time: (run as Record<string, unknown>)['started_at'],
                        end_time: (run as Record<string, unknown>)['completed_at'],
                        duration_ms: run.status === 'COMPLETED' ? 262000 : null,
                        logs: [
                            'Starting protocol execution...',
                            'Initializing liquid handler...',
                            'Loading deck configuration...',
                            `Executing ${run.protocol_name}...`,
                            run.status === 'COMPLETED' ? 'Protocol completed successfully.' : 'Protocol execution in progress...',
                        ],
                    }) as Observable<T>;
                }
                return of(null) as Observable<T>;
            }
            // Return list with consistent field names
            return of(MOCK_PROTOCOL_RUNS.map(r => ({
                accession_id: r.accession_id,
                name: r.protocol_name,
                status: r.status,
                created_at: r.created_at,
                start_time: (r as Record<string, unknown>)['started_at'],
                end_time: (r as Record<string, unknown>)['completed_at'],
                duration_ms: r.status === 'COMPLETED' ? 262000 : null,
                protocol_name: r.protocol_name,
                protocol_accession_id: r.protocol_definition_accession_id,
            }))) as Observable<T>;
        }

        // Protocol runs - return array from SQLite (legacy fallback)
        if (url.includes('/protocols/runs') && method === 'GET' && !url.match(/\/protocols\/runs\/[a-f0-9-]+$/)) {
            return db.getProtocolRuns() as Observable<T>;
        }

        // Single protocol run by ID
        const singleRunMatch = url.match(/\/protocols\/runs\/([a-f0-9-]+)$/);
        if (singleRunMatch && method === 'GET') {
            const runId = singleRunMatch[1];
            const run = MOCK_PROTOCOL_RUNS.find(r => r.accession_id === runId);
            if (run) {
                return of({
                    ...run,
                    name: run.protocol_name,
                    start_time: (run as Record<string, unknown>)['started_at'],
                    end_time: (run as Record<string, unknown>)['completed_at'],
                    duration_ms: run.status === 'COMPLETED' ? 262000 : null,
                }) as Observable<T>;
            }
            return of(null) as Observable<T>;
        }

        // PLR Resource type definitions (comprehensive list)
        if (url.includes('/resources/type-definitions') && method === 'GET') {
            return of(PLR_RESOURCE_DEFINITIONS) as Observable<T>;
        }

        // Resource definitions (for AssetSelector filtering)
        if (url.includes('/resources/definitions') && method === 'GET') {
            return of([...MOCK_RESOURCE_DEFINITIONS, ...PLR_RESOURCE_DEFINITIONS]) as Observable<T>;
        }

        // Resources - return array directly
        if (url.includes('/resources') && !url.includes('type-definitions') && !url.includes('definitions') && method === 'GET') {
            return of(MOCK_RESOURCES) as Observable<T>;
        }

        // PLR Machine type definitions (comprehensive list)
        if (url.includes('/machines/type-definitions') && method === 'GET') {
            return of(PLR_MACHINE_DEFINITIONS) as Observable<T>;
        }

        // Machines - return array directly
        if (url.includes('/machines') && !url.includes('type-definitions') && !url.includes('definitions') && method === 'GET') {
            return of(MOCK_MACHINES) as Observable<T>;
        }

        // Machine definitions
        if (url.includes('/machines/definitions') && method === 'GET') {
            return of([...MOCK_MACHINES, ...PLR_MACHINE_DEFINITIONS]) as Observable<T>;
        }

        // Discovery - type definitions (trigger sync)
        if (url.includes('/discovery/sync-all') && method === 'POST') {
            return of({
                message: 'Browser mode - PLR definitions loaded',
                synced: true,
                resources: PLR_RESOURCE_DEFINITIONS.length,
                machines: PLR_MACHINE_DEFINITIONS.length,
            }) as Observable<T>;
        }

        // Discovery - get type definitions
        if (url.includes('/discovery/type-definitions') && method === 'GET') {
            return of({
                resources: PLR_RESOURCE_DEFINITIONS,
                machines: PLR_MACHINE_DEFINITIONS,
            }) as Observable<T>;
        }

        // Resource facets
        if (url.includes('/facets')) {
            const categories = [...new Set(PLR_RESOURCE_DEFINITIONS.map(r => r.plr_category))];
            const vendors = [...new Set(PLR_RESOURCE_DEFINITIONS.map(r => r.vendor).filter(Boolean))];
            return of({
                category: categories,
                brand: vendors,
                vendor: vendors,
            }) as Observable<T>;
        }

        // User info
        if (url.includes('/auth/me') || url.includes('/auth/user')) {
            return of({
                id: 'local-user',
                username: 'local',
                email: 'local@praxis.local',
                roles: ['user', 'browser-mode'],
                name: 'Local User',
            }) as Observable<T>;
        }

        // POST protocol run - simulate creation
        if (url.includes('/protocols/runs') && method === 'POST') {
            const newRun = {
                accession_id: crypto.randomUUID(),
                status: 'QUEUED',
                created_at: new Date().toISOString(),
                ...(body as object),
            };
            return db.createProtocolRun(newRun) as Observable<T>;
        }

        // Transfer logs
        const transferLogsMatch = url.match(/\/protocols\/runs\/([a-f0-9-]+)\/transfer-logs$/);
        if (transferLogsMatch && method === 'GET') {
            return db.getTransferLogs(transferLogsMatch[1]) as Observable<T>;
        }

        // Workcell
        if (url.includes('/workcell') && method === 'GET') {
            return of({
                name: 'Default Workcell',
                status: 'AVAILABLE',
                machines: MOCK_MACHINES.slice(0, 2),
            }) as Observable<T>;
        }

        // Scheduler - queue
        if (url.includes('/scheduler/queue') && method === 'GET') {
            return of([]) as Observable<T>;
        }

        // Decks
        if (url.includes('/decks') && method === 'GET') {
            return of([]) as Observable<T>;
        }

        // Hardware discovery
        if (url.includes('/hardware/discover') && method === 'GET') {
            const simulators = PLR_MACHINE_DEFINITIONS
                .filter(m => m.fqn.includes('simulation') || (m.properties_json as Record<string, boolean>)?.['simulated'])
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
            }) as Observable<T>;
        }

        // Hardware connection
        if (url.includes('/hardware/connect') && method === 'POST') {
            return of({
                device_id: (body as { device_id?: string })?.device_id || 'unknown',
                status: 'connected',
                message: 'Connected successfully (browser mode)',
                connection_handle: `local-handle-${Date.now()}`,
            }) as Observable<T>;
        }

        // Hardware connections list
        if (url.includes('/hardware/connections') && method === 'GET') {
            return of([]) as Observable<T>;
        }

        // Hardware registration
        if (url.includes('/hardware/register') && method === 'POST') {
            const payload = body as { device_id?: string; name?: string; plr_backend?: string; connection_type?: string; configuration?: unknown };
            return db.createMachine({
                name: payload?.name || 'Registered Machine',
                plr_backend: payload?.plr_backend || '',
                connection_type: payload?.connection_type,
                configuration: payload?.configuration
            }) as Observable<T>;
        }

        // Protocol compatibility check
        if (url.match(/\/protocols\/[a-f0-9-]+\/compatibility$/) && method === 'GET') {
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
            return of(mockCompatibility) as Observable<T>;
        }

        // Hardware REPL command
        if (url.includes('/hardware/repl') && method === 'POST') {
            const payload = body as { device_id?: string; command?: string };
            return of({
                device_id: payload?.device_id || 'unknown',
                command: payload?.command || '',
                output: `[Browser Playground] Executed: ${payload?.command}\n> OK`,
                success: true,
                error: null,
            }) as Observable<T>;
        }

        // No handler found
        return null;
    }
}
