import { TestBed } from '@angular/core/testing';
import { SqliteService } from './sqlite.service';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

const { mockDatabase, mockSqlJs } = vi.hoisted(() => {
    const mockDatabase = {
        exec: vi.fn().mockReturnValue([]),
        prepare: vi.fn().mockReturnValue({
            run: vi.fn(),
            free: vi.fn(),
            step: vi.fn(),
            getAsObject: vi.fn()
        }),
        run: vi.fn(),
        close: vi.fn(),
        export: vi.fn().mockReturnValue(new Uint8Array([]))
    };

    const mockSqlJs = {
        Database: vi.fn().mockImplementation(function () { return mockDatabase; })
    };

    return { mockDatabase, mockSqlJs };
});

// Mock the module 'sql.js'
vi.mock('sql.js', () => ({
    default: vi.fn().mockResolvedValue(mockSqlJs)
}));

describe('SqliteService', () => {
    let service: SqliteService;
    let originalFetch: any;

    beforeEach(() => {
        // Mock global fetch
        originalFetch = global.fetch;
        global.fetch = vi.fn().mockReturnValue(
            Promise.resolve(new Response(new ArrayBuffer(10), { status: 200 }))
        );

        TestBed.configureTestingModule({
            imports: [HttpClientTestingModule],
            providers: [SqliteService]
        });
        service = TestBed.inject(SqliteService);
    });

    afterEach(() => {
        global.fetch = originalFetch;
        vi.clearAllMocks();
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    it('should attempt to load prebuilt database', () => new Promise<void>((done) => {
        // Return 1 table to satisfy checking if valid
        mockDatabase.exec.mockReturnValue([{
            columns: ['COUNT(*)'],
            values: [[1]]
        }]);

        const sub = service.status$.subscribe(status => {
            if (status.initialized) {
                expect(global.fetch).toHaveBeenCalledWith('./assets/db/praxis.db');
                expect(status.source).toBe('prebuilt');
                sub.unsubscribe();
                done();
            }
        });
    }));

    it('should fall back to schema if prebuilt db fails', () => new Promise<void>((done) => {
        TestBed.resetTestingModule();

        const fetchMock = vi.fn().mockImplementation((url: string | URL | Request) => {
            const urlStr = url.toString();
            if (urlStr.includes('praxis.db')) {
                return Promise.resolve(new Response(null, { status: 404 }));
            }
            if (urlStr.includes('schema.sql')) {
                return Promise.resolve(new Response('CREATE TABLE test (id INT);', { status: 200 }));
            }
            return Promise.resolve(new Response(new ArrayBuffer(10), { status: 200 }));
        });
        global.fetch = fetchMock;

        // Reset behaviors
        mockDatabase.exec.mockReturnValue([{
            columns: ['COUNT(*)'],
            values: [[1]]
        }]);

        TestBed.configureTestingModule({
            imports: [HttpClientTestingModule],
            providers: [SqliteService]
        });
        const newService = TestBed.inject(SqliteService);

        const sub = newService.status$.subscribe(status => {
            if (status.initialized) {
                expect(fetchMock).toHaveBeenCalledWith('./assets/db/praxis.db');
                expect(fetchMock).toHaveBeenCalledWith('./assets/db/schema.sql');
                expect(status.source).toBe('schema');
                sub.unsubscribe();
                done();
            }
        });
    }));
});
