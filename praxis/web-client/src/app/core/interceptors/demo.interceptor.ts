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

    // Resource definitions (for AssetSelector filtering) - must come before /resources
    if (url.includes('/resources/definitions') && method === 'GET') {
        return of(MOCK_RESOURCE_DEFINITIONS);
    }

    // Resources - return array directly
    if (url.includes('/resources') && !url.includes('type-definitions') && !url.includes('definitions') && method === 'GET') {
        return of(MOCK_RESOURCES);
    }

    // Machines - return array directly
    if (url.includes('/machines') && !url.includes('type-definitions') && !url.includes('definitions') && method === 'GET') {
        return of(MOCK_MACHINES);
    }

    // Machine definitions
    if (url.includes('/machines/definitions') && method === 'GET') {
        return of(MOCK_MACHINES);
    }

    // Discovery - type definitions
    if (url.includes('/discovery/type-definitions') || url.includes('/discovery/sync-all')) {
        return of({ message: 'Demo mode - discovery simulated', synced: true });
    }

    // Resource facets
    if (url.includes('/facets')) {
        return of({
            category: ['Plate', 'TipRack', 'Reservoir'],
            brand: ['Corning', 'Greiner', 'Opentrons', 'Agilent'],
        });
    }

    // User info
    if (url.includes('/auth/me') || url.includes('/auth/user')) {
        return of({
            id: 'demo-user',
            username: 'demo',
            email: 'demo@pylabpraxis.example',
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
