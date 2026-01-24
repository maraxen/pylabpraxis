import { TestBed } from '@angular/core/testing';
import { SqliteOpfsService } from './sqlite-opfs.service';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

describe('SqliteOpfsService', () => {
    let service: SqliteOpfsService;
    let mockWorker: any;
    let originalFetch: any;

    beforeEach(() => {
        // Mock Worker
        mockWorker = {
            postMessage: vi.fn(),
            onmessage: null,
            terminate: vi.fn(),
            addEventListener: vi.fn(),
            removeEventListener: vi.fn()
        };

        class MockWorkerClass {
            constructor() { return mockWorker; }
        }
        (window as any).Worker = MockWorkerClass;

        // Mock Fetch
        vi.stubGlobal('fetch', vi.fn());

        TestBed.configureTestingModule({
            imports: [HttpClientTestingModule],
            providers: [SqliteOpfsService]
        });
        service = TestBed.inject(SqliteOpfsService);
    });

    afterEach(() => {
        vi.unstubAllGlobals();
        vi.restoreAllMocks();
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    it('should initialize and load prebuilt DB if available', async () => {
        // Setup Fetch for prebuilt DB success
        const mockAB = new ArrayBuffer(10);
        vi.mocked(fetch).mockImplementation((url: any) => {
            if (url.includes('praxis.db')) {
                return Promise.resolve({
                    ok: true,
                    status: 200,
                    arrayBuffer: () => Promise.resolve(mockAB)
                });
            }
            return Promise.reject('Not Found');
        });

        // Start Init
        const initPromise = service.init().toPromise();

        // Expect INIT message to worker
        expect(mockWorker.postMessage).toHaveBeenCalledWith(expect.objectContaining({ type: 'init' }));
        const initCall = mockWorker.postMessage.mock.calls.find((c: any) => c[0].type === 'init');
        const initId = initCall[0].id;

        // Respond to INIT
        mockWorker.onmessage({ data: { id: initId, type: 'result', payload: {} } });

        // Service proceeds to check schema (count tables)
        // Wait for microtasks?
        await new Promise(r => setTimeout(r, 0));

        // Expect EXEC check (count tables)
        const execCalls = mockWorker.postMessage.mock.calls.filter((c: any) => c[0].type === 'exec');
        // The first exec call should be the count check
        const countCheck = execCalls[0];
        expect(countCheck[0].payload.sql).toContain('COUNT(*)');

        // Respond: Empty DB (count 0)
        mockWorker.onmessage({
            data: {
                id: countCheck[0].id,
                type: 'result',
                payload: { resultRows: [{ count: 0 }] }
            }
        });

        await new Promise(r => setTimeout(r, 0));

        // Expect IMPORT message (loading prebuilt)
        const importCall = mockWorker.postMessage.mock.calls.find((c: any) => c[0].type === 'import');
        expect(importCall).toBeDefined();

        // Respond to IMPORT
        mockWorker.onmessage({ data: { id: importCall[0].id, type: 'result', payload: {} } });

        await initPromise;
    });

    it('should fall back to schema if prebuilt DB is missing', async () => {
        // Setup Fetch: prebuilt fails, schema succeeds
        vi.mocked(fetch).mockImplementation((url: any) => {
            if (url.includes('praxis.db')) return Promise.resolve({ ok: false, status: 404 } as Response);
            if (url.includes('schema.sql')) return Promise.resolve({
                ok: true,
                text: () => Promise.resolve('CREATE TABLE foo (id INT);')
            } as Response);
            return Promise.reject('Not Found');
        });

        const initPromise = service.init().toPromise();

        // 1. INIT
        const initCall = mockWorker.postMessage.mock.calls.find((c: any) => c[0].type === 'init');
        mockWorker.onmessage({ data: { id: initCall[0].id, type: 'result', payload: {} } });

        await new Promise(r => setTimeout(r, 0));

        // 2. Count Check
        const countCheck = mockWorker.postMessage.mock.calls.find((c: any) => c[0].type === 'exec' && c[0].payload.sql.includes('COUNT'));
        mockWorker.onmessage({ data: { id: countCheck[0].id, type: 'result', payload: { resultRows: [{ count: 0 }] } } });

        await new Promise(r => setTimeout(r, 0));

        // 3. Should NOT Import (prebuilt failed), should Exec schema
        const importCall = mockWorker.postMessage.mock.calls.find((c: any) => c[0].type === 'import');
        expect(importCall).toBeUndefined();

        const schemaExec = mockWorker.postMessage.mock.calls.find((c: any) => c[0].type === 'exec' && c[0].payload.sql.includes('CREATE TABLE foo'));
        expect(schemaExec).toBeDefined();

        // Respond to schema exec
        mockWorker.onmessage({ data: { id: schemaExec[0].id, type: 'result', payload: {} } });

        // It will then seed catalogs (lots of inserts). Just resolve them all.
        // We can't easily wait for all promises, but we can verify the fallback path triggered.
    });
});
