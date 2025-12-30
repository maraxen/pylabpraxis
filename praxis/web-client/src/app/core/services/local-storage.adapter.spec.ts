import { TestBed } from '@angular/core/testing';
import { LocalStorageAdapter } from './local-storage.adapter';
import { describe, beforeEach, afterEach, it, expect, vi, MockInstance } from 'vitest';
import { firstValueFrom } from 'rxjs';

describe('LocalStorageAdapter', () => {
    let adapter: LocalStorageAdapter;
    let localStorageMock: Record<string, string>;
    let setItemSpy: MockInstance;
    let getItemSpy: MockInstance;
    let removeItemSpy: MockInstance;

    beforeEach(() => {
        // Clear and setup localStorage mock
        localStorageMock = {};

        const storageMock = {
            getItem: vi.fn((key: string) => localStorageMock[key] || null),
            setItem: vi.fn((key: string, value: string) => {
                localStorageMock[key] = value;
            }),
            removeItem: vi.fn((key: string) => {
                delete localStorageMock[key];
            }),
            clear: vi.fn(() => {
                localStorageMock = {};
            })
        };

        Object.defineProperty(window, 'localStorage', {
            value: storageMock,
            writable: true
        });

        setItemSpy = window.localStorage.setItem as unknown as MockInstance;
        getItemSpy = window.localStorage.getItem as unknown as MockInstance;
        removeItemSpy = window.localStorage.removeItem as unknown as MockInstance;

        // Mock crypto.randomUUID
        Object.defineProperty(window, 'crypto', {
            value: {
                randomUUID: () => 'mock-uuid-' + Date.now()
            },
            writable: true
        });

        TestBed.configureTestingModule({
            providers: [LocalStorageAdapter]
        });

        adapter = TestBed.inject(LocalStorageAdapter);
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('should be created', () => {
        expect(adapter).toBeTruthy();
    });

    describe('Initialization', () => {
        it('should initialize storage with version on first load', () => {
            expect(setItemSpy).toHaveBeenCalled();
        });
    });

    describe('Protocols CRUD', () => {
        it('should create and retrieve a protocol', async () => {
            const protocol = { name: 'Test Protocol', description: 'A test' };

            const created = await firstValueFrom(adapter.createProtocol(protocol));

            expect(created).toBeDefined();
            expect(created.name).toBe('Test Protocol');
            expect(created.accession_id).toBeDefined();
        });

        it('should get protocol by ID', async () => {
            const protocol = { accession_id: 'test-id', name: 'Test' };
            await firstValueFrom(adapter.createProtocol(protocol));

            const retrieved = await firstValueFrom(adapter.getProtocol('test-id'));

            expect(retrieved).toBeDefined();
            expect(retrieved?.name).toBe('Test');
        });

        it('should return null for non-existent protocol', async () => {
            const retrieved = await firstValueFrom(adapter.getProtocol('non-existent'));
            expect(retrieved).toBeNull();
        });

        it('should update a protocol', async () => {
            const protocol = { accession_id: 'update-test', name: 'Original' };
            await firstValueFrom(adapter.createProtocol(protocol));

            const updated = await firstValueFrom(adapter.updateProtocol('update-test', { name: 'Updated' }));

            expect(updated).toBeDefined();
            expect(updated?.name).toBe('Updated');
        });

        it('should delete a protocol', async () => {
            const protocol = { accession_id: 'delete-test', name: 'To Delete' };
            await firstValueFrom(adapter.createProtocol(protocol));

            const deleted = await firstValueFrom(adapter.deleteProtocol('delete-test'));
            expect(deleted).toBe(true);

            const retrieved = await firstValueFrom(adapter.getProtocol('delete-test'));
            expect(retrieved).toBeNull();
        });
    });

    describe('Resources CRUD', () => {
        it('should create and retrieve a resource', async () => {
            const resource = { name: 'Test Resource', type: 'plate' };

            const created = await firstValueFrom(adapter.createResource(resource));

            expect(created).toBeDefined();
            expect(created.name).toBe('Test Resource');
        });

        it('should delete a resource', async () => {
            const resource = { accession_id: 'res-delete', name: 'To Delete' };
            await firstValueFrom(adapter.createResource(resource));

            const deleted = await firstValueFrom(adapter.deleteResource('res-delete'));
            expect(deleted).toBe(true);
        });
    });

    describe('Machines CRUD', () => {
        it('should create and retrieve a machine', async () => {
            const machine = { name: 'Test Machine', type: 'liquid_handler' };

            const created = await firstValueFrom(adapter.createMachine(machine));

            expect(created).toBeDefined();
            expect(created.name).toBe('Test Machine');
        });

        it('should delete a machine', async () => {
            const machine = { accession_id: 'mach-delete', name: 'To Delete' };
            await firstValueFrom(adapter.createMachine(machine));

            const deleted = await firstValueFrom(adapter.deleteMachine('mach-delete'));
            expect(deleted).toBe(true);
        });
    });

    describe('Protocol Runs', () => {
        it('should create a protocol run with defaults', async () => {
            const run = { protocol_definition_accession_id: 'proto-1' };

            const created = await firstValueFrom(adapter.createProtocolRun(run));

            expect(created).toBeDefined();
            expect(created.status).toBe('QUEUED');
            expect(created.created_at).toBeDefined();
        });

        it('should update a protocol run status', async () => {
            const run = { accession_id: 'run-1', status: 'QUEUED' };
            await firstValueFrom(adapter.createProtocolRun(run));

            const updated = await firstValueFrom(adapter.updateProtocolRun('run-1', { status: 'COMPLETED' }));

            expect(updated?.status).toBe('COMPLETED');
        });
    });

    describe('State Export/Import', () => {
        it('should export state as JSON string', async () => {
            await firstValueFrom(adapter.createProtocol({ name: 'Export Test' }));

            const exported = adapter.exportState();

            expect(typeof exported).toBe('string');
            const parsed = JSON.parse(exported);
            expect(parsed.version).toBeDefined();
            expect(parsed.protocols).toBeInstanceOf(Array);
        });

        it('should import state and replace existing data', () => {
            const stateToImport = JSON.stringify({
                version: 1,
                protocols: [{ accession_id: 'imported-1', name: 'Imported Protocol' }],
                protocolRuns: [],
                resources: [],
                machines: []
            });

            const result = adapter.importState(stateToImport, false);

            expect(result).toBe(true);
        });

        it('should reject invalid state import', () => {
            const result = adapter.importState('invalid json{{{', false);
            expect(result).toBe(false);
        });

        it('should reject state without version', () => {
            const result = adapter.importState(JSON.stringify({ protocols: [] }), false);
            expect(result).toBe(false);
        });
    });

    describe('Storage Management', () => {
        it('should clear all data', async () => {
            await firstValueFrom(adapter.createProtocol({ name: 'To Clear' }));

            adapter.clearAll();

            expect(removeItemSpy).toHaveBeenCalled();
        });

        it('should return storage stats', () => {
            const stats = adapter.getStorageStats();

            expect(stats).toBeDefined();
            expect(typeof stats.used).toBe('number');
            expect(typeof stats.quota).toBe('number');
            expect(typeof stats.percentage).toBe('number');
        });
    });
});
