import { TestBed } from '@angular/core/testing';
import { SqliteService } from './sqlite.service';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

// --- Mocks Setup ---

// 1. Mock sql.js Database and Module
const { MockDatabase, mockSqlJsModule } = vi.hoisted(() => {
    class MockStmt {
        private _binds: any[] = [];
        run = vi.fn((params) => { this._binds = params; });
        free = vi.fn();
        step = vi.fn().mockReturnValue(true); // Default to one step success
        get = vi.fn().mockReturnValue([1, 'Mock Result']); // Default result
        getAsObject = vi.fn().mockReturnValue({ col: 'val' });
        // Add bind support
        bind = vi.fn((params) => { this._binds = params; return true; });
    }

    class MockDatabase {
        exec = vi.fn().mockImplementation((sql: string) => {
            // Basic SQL matching for specific tests
            if (sql.includes('COUNT(*)')) {
                // Return 1 table to simulate valid DB
                return [{ columns: ['COUNT(*)'], values: [[1]] }];
            }
            if (sql.includes('PRAGMA table_info')) {
                // Return dummy columns to pass migration checks
                return [{ columns: ['name'], values: [['id'], ['accession_id']] }];
            }
            if (sql.includes('SELECT * FROM function_protocol_definitions')) {
                return [{
                    columns: ['accession_id', 'is_top_level', 'hardware_requirements_json'],
                    values: [['proto_123', 1, '{}']]
                }];
            }
            if (sql.includes('SELECT * FROM protocols')) { // Legacy
                return [{
                    columns: ['accession_id', 'is_top_level', 'parameters_json'],
                    values: [['legacy_proto', 1, '{}']]
                }];
            }
            if (sql.includes('simulation_result_json')) {
                return [{
                    columns: ['inferred_requirements_json', 'failure_modes_json', 'simulation_result_json'],
                    values: [['[]', '[]', '{"sim": true}']]
                }];
            }
            return [];
        });
        prepare = vi.fn().mockReturnValue(new MockStmt());
        run = vi.fn();
        close = vi.fn();
        export = vi.fn().mockReturnValue(new Uint8Array([1, 2, 3]));
        create_function = vi.fn();
    }

    const mockSqlJsModule = {
        Database: vi.fn(function (data?: any) { return new MockDatabase(); })
    };

    return { MockDatabase, mockSqlJsModule };
});

vi.mock('sql.js', () => ({
    default: vi.fn().mockResolvedValue(mockSqlJsModule)
}));

// 2. Mock IndexedDB
const mockIDBStore = {
    put: vi.fn().mockImplementation(() => {
        const req = { result: undefined, onsuccess: null, onerror: null } as any;
        // Async trigger
        setTimeout(() => req.onsuccess && req.onsuccess({ target: { result: undefined } }), 0);
        return req;
    }),
    get: vi.fn().mockImplementation(() => {
        const req = { result: undefined, onsuccess: null, onerror: null } as any;
        setTimeout(() => req.onsuccess && req.onsuccess({ target: { result: req.result } }), 0);
        return req;
    }),
    clear: vi.fn().mockImplementation(() => {
        const req = { result: undefined, onsuccess: null, onerror: null } as any;
        setTimeout(() => req.onsuccess && req.onsuccess({ target: { result: undefined } }), 0);
        return req;
    })
};

const mockIDBTransaction = {
    objectStore: vi.fn().mockReturnValue(mockIDBStore),
    oncomplete: null as any,
    onerror: null as any,
};

const mockIDBDatabase = {
    objectStoreNames: {
        contains: vi.fn().mockReturnValue(false)
    },
    createObjectStore: vi.fn(),
    transaction: vi.fn().mockImplementation(() => {
        // Return a new tx object or reusable one, but must handle oncomplete
        const tx = { ...mockIDBTransaction };
        // In real IDB, oncomplete fires after all requests are done.
        // Here we simulate it firing next tick for simple transactions
        setTimeout(() => tx.oncomplete && tx.oncomplete(), 0);
        return tx;
    }),
};

// Use a factory for open request to allow separate event binding
const mockIndexedDB = {
    open: vi.fn().mockImplementation(() => {
        const req = {
            result: mockIDBDatabase,
            onupgradeneeded: null as any,
            onsuccess: null as any,
            onerror: null as any,
        };
        // Async trigger of success
        setTimeout(() => {
            if (req.onupgradeneeded) {
                req.onupgradeneeded({ target: req }); // Only if version change, but usually we just want success for existing DB
            }
            if (req.onsuccess) {
                req.onsuccess({ target: req });
            }
        }, 0);
        return req;
    })
};

Object.defineProperty(global, 'indexedDB', {
    value: mockIndexedDB
});

// 3. Mock DOM APIs (URL, Blob, Anchor)
global.URL.createObjectURL = vi.fn();
global.URL.revokeObjectURL = vi.fn();

describe('SqliteService', () => {
    let service: SqliteService;
    let originalFetch: any;

    // Helper to wait for DB instance explicitly to avoid race condition
    const waitForDb = async (srv: SqliteService) => {
        return new Promise<void>((resolve, reject) => {
            const sub = srv.db$.subscribe({
                next: () => {
                    resolve();
                    sub.unsubscribe();
                },
                error: (e) => reject(e)
            });
        });
    };

    beforeEach(() => {
        vi.clearAllMocks();

        // Reset specific mock behaviors per test needs
        // Default behavior: return no data
        mockIDBStore.get.mockImplementation(() => {
            const req = { result: null, onsuccess: null } as any;
            setTimeout(() => req.onsuccess && req.onsuccess({ target: { result: null } }), 0);
            return req;
        });

        // Robust Fetch Mock
        originalFetch = global.fetch;
        global.fetch = vi.fn().mockImplementation((url: string) => {
            const mockText = async () => 'CREATE TABLE foo (id INT);';
            const mockArrayBuffer = async () => new ArrayBuffer(10);
            const mockArrayBufferLarge = async () => new ArrayBuffer(100);

            if (url.includes('notfound') || url.includes('schema.sql') === false && url.includes('praxis.db') === false) {
                // Default to something generic or failure if strict
            }

            // specific cases handled in tests by overriding implementation
            // But default here for safety:
            return Promise.resolve({
                ok: true,
                status: 200,
                text: mockText,
                arrayBuffer: mockArrayBuffer
            });
        });

        TestBed.configureTestingModule({
            imports: [HttpClientTestingModule],
            providers: [SqliteService]
        });
        service = TestBed.inject(SqliteService);
    });

    afterEach(() => {
        global.fetch = originalFetch;
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    // --- Lifecycle & Initialization Tests ---

    it('should initialize from prebuilt database if available', async () => {
        // Setup IDB to return null (no Persistence)
        mockIDBStore.get.mockImplementation(() => {
            const req = { result: null, onsuccess: null } as any;
            setTimeout(() => req.onsuccess && req.onsuccess({ target: { result: null } }), 0);
            return req;
        });

        // Setup Fetch to succeed for praxis.db
        (global.fetch as any).mockImplementation((url: string) => {
            const mockAB = new ArrayBuffer(100);
            if (url.includes('praxis.db')) return Promise.resolve({ ok: true, status: 200, arrayBuffer: async () => mockAB, text: async () => '' });
            return Promise.resolve({ ok: false, status: 404, arrayBuffer: async () => new ArrayBuffer(0), text: async () => '' });
        });

        await waitForDb(service);
        expect(service.status$.value.source).toBe('prebuilt');
    });

    it('should fall back to schema.sql if prebuilt fails', async () => {
        // IDB null
        mockIDBStore.get.mockReturnValue({ result: null, onsuccess: () => { } } as any);

        // Fetch schema success, praxis.db fail
        (global.fetch as any).mockImplementation((url: string) => {
            if (url.includes('praxis.db')) return Promise.resolve({ ok: false, status: 404, arrayBuffer: async () => new ArrayBuffer(0) });
            if (url.includes('schema.sql')) return Promise.resolve({ ok: true, status: 200, text: async () => 'CREATE TABLE foo (id INT);', arrayBuffer: async () => new ArrayBuffer(0) });
            return Promise.resolve({ ok: false });
        });

        const status = await new Promise<any>((resolve, reject) => {
            service.status$.subscribe(s => {
                if (s.initialized && s.source === 'schema') resolve(s);
                if (s.error) reject('Init Failed: ' + s.error);
            });
        });

        expect(status.source).toBe('schema');
        expect(mockSqlJsModule.Database).toHaveBeenCalled();
    });

    it('should fall back to legacy if both prebuilt and schema fail', async () => {
        (global.fetch as any).mockReturnValue(Promise.resolve({ ok: false, status: 404, text: async () => '', arrayBuffer: async () => new ArrayBuffer(0) }));

        const status = await new Promise<any>((resolve, reject) => {
            service.status$.subscribe(s => {
                if (s.initialized && s.source === 'legacy') resolve(s);
                if (s.error) reject('Init Failed: ' + s.error);
            });
        });

        expect(status.source).toBe('legacy');
    });

    it('should load from IndexedDB persistence if available', async () => {
        // Setup IDB to return data
        const dummyData = new Uint8Array([9, 9, 9]);
        mockIDBStore.get.mockImplementation(() => {
            const req = { result: dummyData, onsuccess: null } as any;
            setTimeout(() => req.onsuccess && req.onsuccess({ target: { result: req.result } }), 0);
            return req;
        });

        await waitForDb(service);
        expect(service.status$.value.source).toBe('indexeddb');
        expect(mockSqlJsModule.Database).toHaveBeenCalledWith(dummyData);
    });

    // --- Persistence Tests ---

    it('should save to IndexedDB on request', async () => {
        // Wait for init
        await waitForDb(service);

        await service.save();

        expect(mockIDBDatabase.transaction).toHaveBeenCalledWith('sqlite', 'readwrite');
        expect(mockIDBStore.put).toHaveBeenCalled();
        const dbInstance = (service as any).dbInstance;
        expect(dbInstance.export).toHaveBeenCalled();
    });

    it('should clear store on clearStore', async () => {
        await service.clearStore();
        expect(mockIDBStore.clear).toHaveBeenCalled();
    });

    // --- CRUD & Features Tests ---

    it('should create a machine and persist', async () => {
        await waitForDb(service);

        const machineData = {
            name: 'Test Machine',
            plr_backend: 'pylabrobot.scales.MettlerToledo',
            connection_type: 'usb'
        };

        const result = await new Promise<any>((resolve, reject) => {
            service.createMachine(machineData).subscribe({
                next: resolve,
                error: reject
            });
        });

        expect(result).toBeDefined();
        expect(result.name).toBe('Test Machine');

        // Verify DB interactions
        const db = (service as any).dbInstance;
        expect(db.exec).toHaveBeenCalledWith('BEGIN TRANSACTION');
        expect(db.prepare).toHaveBeenCalledTimes(3);
        expect(db.exec).toHaveBeenCalledWith('COMMIT');

        // Verify persistence triggered
        expect(db.export).toHaveBeenCalled();
    });

    it('should list protocols from both new and legacy tables', async () => {
        await waitForDb(service);

        const protocols = await new Promise<any[]>(resolve => {
            service.getProtocols().subscribe(resolve);
        });

        expect(protocols).toBeTruthy();
        expect(protocols.length).toBeGreaterThan(0);
        expect(protocols[0].is_top_level).toBe(true);
    });

    it('should get protocol simulation data', async () => {
        await waitForDb(service);

        const data = await new Promise<any>(resolve => {
            service.getProtocolSimulationData('123').subscribe(resolve);
        });

        expect(data).not.toBeNull();
        expect(data?.simulation_result).toEqual({ sim: true });
    });

    // --- Import / Export Tests ---

    it('should export database to file', async () => {
        await waitForDb(service);

        const mockAnchor = {
            href: '',
            download: '',
            click: vi.fn(),
            remove: vi.fn()
        };
        const createElementSpy = vi.spyOn(document, 'createElement').mockReturnValue(mockAnchor as any);

        await service.exportDatabase();

        expect(createElementSpy).toHaveBeenCalledWith('a');
        expect(mockAnchor.download).toContain('praxis-backup');
        expect(mockAnchor.click).toHaveBeenCalled();
        expect(global.URL.createObjectURL).toHaveBeenCalled();
    });

    it('should import database from file', async () => {
        const file = {
            arrayBuffer: () => Promise.resolve(new ArrayBuffer(8)),
            name: 'backup.db'
        } as any;

        await service.importDatabase(file);

        // Should re-init DB with new data
        expect(mockSqlJsModule.Database).toHaveBeenCalled();
        // Should save to store
        expect(mockIDBStore.put).toHaveBeenCalled();
    });

    // --- Error Handling ---

    it('should handle initialization errors gracefully', async () => {
        // Force sql.js failure
        vi.mocked(mockSqlJsModule.Database).mockImplementationOnce(() => { throw new Error('Init Failed'); });

        // Reset
        TestBed.resetTestingModule();
        TestBed.configureTestingModule({
            imports: [HttpClientTestingModule],
            providers: [SqliteService]
        });

        const failService = TestBed.inject(SqliteService);

        await new Promise<void>(resolve => {
            failService.status$.subscribe(s => {
                if (s.error) {
                    expect(s.initialized).toBe(false);
                    expect(s.error).toContain('Init Failed');
                    resolve();
                }
            });
        });
    });
});
