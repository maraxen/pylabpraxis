/**
 * SQLite Persistence Service
 *
 * Provides IndexedDB-based persistence for sql.js databases.
 * This allows the browser-mode database to survive page refreshes and browser restarts.
 *
 * Features:
 * - Save database to IndexedDB
 * - Load database from IndexedDB
 * - Auto-save on changes (debounced)
 * - Export/import database files
 */

import { Injectable, OnDestroy } from '@angular/core';
import { BehaviorSubject, Observable, from, of, Subject } from 'rxjs';
import { catchError, debounceTime, distinctUntilChanged, filter, map, switchMap, takeUntil, tap } from 'rxjs/operators';
import type { Database } from 'sql.js';

const DB_NAME = 'praxis-browser-db';
const STORE_NAME = 'database';
const DB_VERSION = 1;

export interface PersistenceStatus {
    hasPersistedData: boolean;
    lastSavedAt: Date | null;
    sizeBytes: number;
    schemaVersion: string | null;
}

export interface StoredDatabase {
    key: string;
    data: Uint8Array;
    savedAt: Date;
    schemaVersion: string;
    tableCount: number;
}

@Injectable({
    providedIn: 'root'
})
export class SqlitePersistenceService implements OnDestroy {
    private indexedDb: IDBDatabase | null = null;
    private saveSubject = new Subject<Uint8Array>();
    private destroy$ = new Subject<void>();

    private statusSubject = new BehaviorSubject<PersistenceStatus>({
        hasPersistedData: false,
        lastSavedAt: null,
        sizeBytes: 0,
        schemaVersion: null
    });

    public readonly status$ = this.statusSubject.asObservable();

    constructor() {
        this.initIndexedDb().then(() => {
            this.checkExistingData();
        });

        // Set up debounced auto-save
        this.saveSubject.pipe(
            debounceTime(1000), // Wait 1 second after last change before saving
            takeUntil(this.destroy$)
        ).subscribe(data => {
            this.performSave(data);
        });
    }

    ngOnDestroy(): void {
        this.destroy$.next();
        this.destroy$.complete();
        if (this.indexedDb) {
            this.indexedDb.close();
        }
    }

    /**
     * Initialize IndexedDB connection
     */
    private async initIndexedDb(): Promise<void> {
        return new Promise((resolve, reject) => {
            if (!('indexedDB' in window)) {
                console.warn('[SqlitePersistence] IndexedDB not available');
                reject(new Error('IndexedDB not available'));
                return;
            }

            const request = indexedDB.open(DB_NAME, DB_VERSION);

            request.onerror = () => {
                console.error('[SqlitePersistence] Failed to open IndexedDB:', request.error);
                reject(request.error);
            };

            request.onsuccess = () => {
                this.indexedDb = request.result;
                console.log('[SqlitePersistence] IndexedDB connection established');
                resolve();
            };

            request.onupgradeneeded = (event) => {
                const db = (event.target as IDBOpenDBRequest).result;

                // Create object store for database files
                if (!db.objectStoreNames.contains(STORE_NAME)) {
                    const store = db.createObjectStore(STORE_NAME, { keyPath: 'key' });
                    store.createIndex('savedAt', 'savedAt', { unique: false });
                    console.log('[SqlitePersistence] Created object store');
                }
            };
        });
    }

    /**
     * Check if there's existing persisted data
     */
    private async checkExistingData(): Promise<void> {
        try {
            const data = await this.loadDatabaseRaw();
            if (data) {
                this.statusSubject.next({
                    hasPersistedData: true,
                    lastSavedAt: data.savedAt,
                    sizeBytes: data.data.length,
                    schemaVersion: data.schemaVersion
                });
            }
        } catch {
            // No existing data or error reading
        }
    }

    /**
     * Save a sql.js database to IndexedDB
     */
    public async saveDatabase(db: Database, schemaVersion: string = '1.0.0'): Promise<void> {
        const data = db.export();
        const tableCount = this.getTableCount(db);
        await this.save(data, schemaVersion, tableCount);
    }

    /**
     * Queue a database save (debounced)
     */
    public queueSave(data: Uint8Array): void {
        this.saveSubject.next(data);
    }

    /**
     * Perform the actual save operation
     */
    private async performSave(data: Uint8Array, schemaVersion: string = '1.0.0', tableCount: number = 0): Promise<void> {
        await this.save(data, schemaVersion, tableCount);
    }

    /**
     * Save database data to IndexedDB
     */
    private async save(data: Uint8Array, schemaVersion: string, tableCount: number): Promise<void> {
        if (!this.indexedDb) {
            await this.initIndexedDb();
        }

        if (!this.indexedDb) {
            throw new Error('IndexedDB not initialized');
        }

        return new Promise((resolve, reject) => {
            const transaction = this.indexedDb!.transaction([STORE_NAME], 'readwrite');
            const store = transaction.objectStore(STORE_NAME);

            const record: StoredDatabase = {
                key: 'main',
                data: data,
                savedAt: new Date(),
                schemaVersion,
                tableCount
            };

            const request = store.put(record);

            request.onerror = () => {
                console.error('[SqlitePersistence] Failed to save database:', request.error);
                reject(request.error);
            };

            request.onsuccess = () => {
                console.log(`[SqlitePersistence] Database saved (${data.length} bytes)`);
                this.statusSubject.next({
                    hasPersistedData: true,
                    lastSavedAt: record.savedAt,
                    sizeBytes: data.length,
                    schemaVersion
                });
                resolve();
            };
        });
    }

    /**
     * Load database data from IndexedDB
     */
    public async loadDatabase(): Promise<Uint8Array | null> {
        const stored = await this.loadDatabaseRaw();
        return stored?.data ?? null;
    }

    /**
     * Load the full stored database record
     */
    public async loadDatabaseRaw(): Promise<StoredDatabase | null> {
        if (!this.indexedDb) {
            await this.initIndexedDb();
        }

        if (!this.indexedDb) {
            return null;
        }

        return new Promise((resolve, reject) => {
            const transaction = this.indexedDb!.transaction([STORE_NAME], 'readonly');
            const store = transaction.objectStore(STORE_NAME);
            const request = store.get('main');

            request.onerror = () => {
                console.error('[SqlitePersistence] Failed to load database:', request.error);
                reject(request.error);
            };

            request.onsuccess = () => {
                const result = request.result as StoredDatabase | undefined;
                if (result) {
                    console.log(`[SqlitePersistence] Database loaded (${result.data.length} bytes)`);
                    resolve(result);
                } else {
                    console.log('[SqlitePersistence] No persisted database found');
                    resolve(null);
                }
            };
        });
    }

    /**
     * Check if persisted data exists
     */
    public async hasPersistedData(): Promise<boolean> {
        const data = await this.loadDatabaseRaw();
        return data !== null;
    }

    /**
     * Clear persisted data
     */
    public async clearPersistedData(): Promise<void> {
        if (!this.indexedDb) {
            await this.initIndexedDb();
        }

        if (!this.indexedDb) {
            return;
        }

        return new Promise((resolve, reject) => {
            const transaction = this.indexedDb!.transaction([STORE_NAME], 'readwrite');
            const store = transaction.objectStore(STORE_NAME);
            const request = store.delete('main');

            request.onerror = () => {
                console.error('[SqlitePersistence] Failed to clear database:', request.error);
                reject(request.error);
            };

            request.onsuccess = () => {
                console.log('[SqlitePersistence] Persisted database cleared');
                this.statusSubject.next({
                    hasPersistedData: false,
                    lastSavedAt: null,
                    sizeBytes: 0,
                    schemaVersion: null
                });
                resolve();
            };
        });
    }

    /**
     * Export database as downloadable file
     */
    public exportToFile(db: Database, filename: string = 'praxis-browser.db'): void {
        const data = db.export();
        // Create blob from the Uint8Array (cast needed for strict TS)
        const blob = new Blob([data as unknown as BlobPart], { type: 'application/x-sqlite3' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();

        URL.revokeObjectURL(url);
        console.log(`[SqlitePersistence] Database exported as ${filename}`);
    }

    /**
     * Import database from file
     */
    public importFromFile(file: File): Observable<Uint8Array> {
        return new Observable(subscriber => {
            const reader = new FileReader();

            reader.onload = () => {
                const arrayBuffer = reader.result as ArrayBuffer;
                const data = new Uint8Array(arrayBuffer);
                subscriber.next(data);
                subscriber.complete();
            };

            reader.onerror = () => {
                subscriber.error(reader.error);
            };

            reader.readAsArrayBuffer(file);
        });
    }

    /**
     * Get table count from a database
     */
    private getTableCount(db: Database): number {
        try {
            const result = db.exec("SELECT COUNT(*) FROM sqlite_master WHERE type='table'");
            return result.length > 0 ? (result[0].values[0][0] as number) : 0;
        } catch {
            return 0;
        }
    }
}

/**
 * Hook to save database on page unload
 */
export function setupUnloadSave(
    persistenceService: SqlitePersistenceService,
    getDatabase: () => Database | null
): void {
    window.addEventListener('beforeunload', () => {
        const db = getDatabase();
        if (db) {
            // Use synchronous save for beforeunload
            const data = db.export();
            persistenceService.queueSave(data);
        }
    });
}
