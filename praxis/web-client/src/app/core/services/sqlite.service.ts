/**
 * SQLite Service for Browser-Mode Database Operations
 *
 * This service provides a sql.js-based database for browser-only mode.
 * It uses the auto-generated schema from SQLAlchemy ORM models and
 * provides repository-based access to all entities.
 *
 * Key Features:
 * - Loads prebuilt database with PLR definitions (if available)
 * - Falls back to fresh database with schema.sql
 * - Provides typed repositories for all entities
 * - Maintains compatibility with existing mock data
 */

import { Injectable } from '@angular/core';
import initSqlJs, { Database, SqlJsStatic } from 'sql.js';
import { BehaviorSubject, from, Observable, of } from 'rxjs';
import { catchError, filter, map, shareReplay, switchMap, take, tap } from 'rxjs/operators';

// Type imports
import type {
    Asset,
    ProtocolRun,
    FunctionProtocolDefinition,
    Machine,
    Resource,
    Workcell,
} from '../db/schema';
import {
    createRepositories,
    type Repositories,
    type ProtocolRunRepository,
    type ProtocolDefinitionRepository,
    type MachineRepository,
    type MachineDefinitionRepository,
    type ResourceRepository,
    type ResourceDefinitionRepository,
    type DeckRepository,
    type DeckDefinitionRepository,
    type DeckPositionRepository,
    type WorkcellRepository,
} from '../db/repositories';

// Legacy mock data imports (for fallback seeding)
import { MOCK_PROTOCOLS } from '../../../assets/demo-data/protocols';
import { MOCK_PROTOCOL_RUNS } from '../../../assets/demo-data/protocol-runs';
import { MOCK_RESOURCES } from '../../../assets/demo-data/resources';
import { MOCK_MACHINES } from '../../../assets/demo-data/machines';

export interface SqliteStatus {
    initialized: boolean;
    source: 'prebuilt' | 'schema' | 'legacy' | 'indexeddb' | 'none';
    tableCount: number;
    error?: string;
}

@Injectable({
    providedIn: 'root'
})
export class SqliteService {
    private db$: Observable<Database>;
    private dbInstance: Database | null = null;
    private repositories: Repositories | null = null;
    private statusSubject = new BehaviorSubject<SqliteStatus>({
        initialized: false,
        source: 'none',
        tableCount: 0
    });

    public readonly status$ = this.statusSubject.asObservable();

    constructor() {
        this.db$ = from(this.initDb()).pipe(
            tap(db => {
                this.dbInstance = db;
                this.repositories = createRepositories(db);
            }),
            shareReplay(1)
        );
    }

    /**
     * Get the database instance (async)
     */
    public getDatabase(): Observable<Database> {
        return this.db$;
    }

    /**
     * Get repositories for typed database access
     */
    public getRepositories(): Observable<Repositories> {
        return this.db$.pipe(
            map(() => {
                if (!this.repositories) {
                    throw new Error('Repositories not initialized');
                }
                return this.repositories;
            })
        );
    }

    // ============================================
    // Repository Accessors (for convenience)
    // ============================================

    public get protocolRuns(): Observable<ProtocolRunRepository> {
        return this.getRepositories().pipe(map(r => r.protocolRuns));
    }

    public get protocolDefinitions(): Observable<ProtocolDefinitionRepository> {
        return this.getRepositories().pipe(map(r => r.protocolDefinitions));
    }

    public get machines(): Observable<MachineRepository> {
        return this.getRepositories().pipe(map(r => r.machines));
    }

    public get machineDefinitions(): Observable<MachineDefinitionRepository> {
        return this.getRepositories().pipe(map(r => r.machineDefinitions));
    }

    public get resources(): Observable<ResourceRepository> {
        return this.getRepositories().pipe(map(r => r.resources));
    }

    public get resourceDefinitions(): Observable<ResourceDefinitionRepository> {
        return this.getRepositories().pipe(map(r => r.resourceDefinitions));
    }

    public get decks(): Observable<DeckRepository> {
        return this.getRepositories().pipe(map(r => r.decks));
    }

    public get deckDefinitions(): Observable<DeckDefinitionRepository> {
        return this.getRepositories().pipe(map(r => r.deckDefinitions));
    }

    public get deckPositions(): Observable<DeckPositionRepository> {
        return this.getRepositories().pipe(map(r => r.deckPositions));
    }

    public get workcells(): Observable<WorkcellRepository> {
        return this.getRepositories().pipe(map(r => r.workcells));
    }

    // ============================================
    // Database Initialization
    // ============================================

    private async initDb(): Promise<Database> {
        try {
            const SQL = await initSqlJs({
                locateFile: file => `./assets/wasm/${file}`
            });

            // Try loading prebuilt database first
            let db: Database | null = null;

            // 1. Try loading from IndexedDB persistence (browser refresh survival)
            const persistedData = await this.loadFromStore();
            if (persistedData) {
                try {
                    db = new SQL.Database(persistedData);
                    console.log('[SqliteService] Loaded database from IndexedDB persistence');
                    this.statusSubject.next({
                        initialized: true,
                        source: 'indexeddb',
                        tableCount: this.getTableCount(db)
                    });
                } catch (e) {
                    console.warn('[SqliteService] Failed to load persisted DB, fallback to prebuilt/fresh', e);
                }
            }

            // 2. Try loading prebuilt database if no persistence
            if (!db) {
                db = await this.tryLoadPrebuiltDb(SQL);
            }

            if (!db) {
                // Fall back to fresh database with generated schema
                db = await this.tryLoadSchemaDb(SQL);
            }

            if (!db) {
                // Final fallback: legacy inline schema with mock data
                db = this.createLegacyDb(SQL);
            }

            // --- MVP Schema Sync ---
            this.checkAndMigrate(db);
            // -----------------------

            // Save immediately to ensure persistence initialized
            this.saveToStore(db);

            const tableCount = this.getTableCount(db);
            console.log(`[SqliteService] Database initialized with ${tableCount} tables`);

            return db;
        } catch (error) {
            console.error('[SqliteService] Failed to initialize database:', error);
            this.statusSubject.next({
                initialized: false,
                source: 'none',
                tableCount: 0,
                error: error instanceof Error ? error.message : 'Unknown error'
            });
            throw new Error(`SQLite initialization failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }

    // ============================================
    // Schema Migration (MVP)
    // ============================================

    private checkAndMigrate(db: Database): void {
        try {
            // 1. Ensure version table exists
            db.run(`CREATE TABLE IF NOT EXISTS local_schema_versions (version INTEGER PRIMARY KEY)`);

            // 2. Get current version
            const res = db.exec(`SELECT MAX(version) FROM local_schema_versions`);
            let currentVersion = 0;
            if (res.length > 0 && res[0].values.length > 0 && res[0].values[0][0] !== null) {
                currentVersion = res[0].values[0][0] as number;
            }

            console.log(`[SqliteService] Current DB Schema Version: ${currentVersion}`);

            // 3. Define Migrations
            // NOTE: Keep distinct from backend revisions. This is for browser-db specifically.
            // Ideally we align version numbers or use timestamp-based IDs similar to alembic.
            // For MVP, simple integer increment is sufficient.
            const MIGRATIONS = [
                {
                    version: 1,
                    name: 'add_maintenance_and_location',
                    run: (d: Database) => {
                        this.safeAddColumn(d, 'machines', 'location_label', 'TEXT');
                        this.safeAddColumn(d, 'machines', 'maintenance_enabled', 'BOOLEAN DEFAULT 1');
                        this.safeAddColumn(d, 'machines', 'maintenance_schedule_json', 'TEXT');
                        this.safeAddColumn(d, 'machines', 'last_maintenance_json', 'TEXT');
                        this.safeAddColumn(d, 'resources', 'location_label', 'TEXT');
                    }
                }
            ];

            // 4. Run pending migrations
            let migratedCount = 0;
            MIGRATIONS.sort((a, b) => a.version - b.version);

            for (const m of MIGRATIONS) {
                if (m.version > currentVersion) {
                    console.log(`[SqliteService] Applying migration v${m.version}: ${m.name}`);
                    try {
                        m.run(db);
                        db.run(`INSERT INTO local_schema_versions (version) VALUES (?)`, [m.version]);
                        migratedCount++;
                    } catch (err) {
                        console.error(`[SqliteService] Migration v${m.version} failed:`, err);
                        // Decide whether to halt or continue. For now, log and continue might be safer for partial loads,
                        // but risky for data integrity. Halting is strictly safer.
                        throw err;
                    }
                }
            }

            if (migratedCount > 0) {
                console.log(`[SqliteService] applied ${migratedCount} migrations successfully.`);
            }

        } catch (error) {
            console.error('[SqliteService] Schema Migration Error:', error);
            // Non-blocking for now, as broken DB might be better than no DB for some users
        }
    }

    private safeAddColumn(db: Database, table: string, column: string, type: string) {
        try {
            // Check if column exists first
            const res = db.exec(`PRAGMA table_info(${table})`);
            const columns = res[0].values.map(v => v[1]); // Index 1 is name
            if (!columns.includes(column)) {
                db.run(`ALTER TABLE ${table} ADD COLUMN ${column} ${type}`);
                console.log(`[SqliteService] Added column ${table}.${column}`);
            }
        } catch (e) {
            // Log but don't crash if table missing etc (though that shouldn't happen here)
            console.warn(`[SqliteService] Failed to add column ${table}.${column}`, e);
        }
    }

    /**
     * Try to load the prebuilt database with PLR definitions
     */
    private async tryLoadPrebuiltDb(SQL: SqlJsStatic): Promise<Database | null> {
        try {
            const response = await fetch('./assets/db/praxis.db');
            if (!response.ok) {
                console.log('[SqliteService] Prebuilt database not available');
                return null;
            }

            const arrayBuffer = await response.arrayBuffer();
            const dbArray = new Uint8Array(arrayBuffer);
            const db = new SQL.Database(dbArray);

            // Verify the database is valid
            const tables = this.getTableCount(db);
            if (tables > 0) {
                console.log('[SqliteService] Loaded prebuilt database with PLR definitions');
                this.statusSubject.next({
                    initialized: true,
                    source: 'prebuilt',
                    tableCount: tables
                });
                return db;
            }

            db.close();
            return null;
        } catch {
            console.log('[SqliteService] Could not load prebuilt database, trying schema.sql');
            return null;
        }
    }

    /**
     * Try to create database using generated schema.sql
     */
    private async tryLoadSchemaDb(SQL: SqlJsStatic): Promise<Database | null> {
        try {
            const response = await fetch('./assets/db/schema.sql');
            if (!response.ok) {
                console.log('[SqliteService] schema.sql not available');
                return null;
            }

            const schema = await response.text();
            const db = new SQL.Database();

            // Execute schema
            db.run(schema);

            // Seed with mock data for development
            this.seedMockData(db);

            const tables = this.getTableCount(db);
            console.log('[SqliteService] Created database from schema.sql');
            this.statusSubject.next({
                initialized: true,
                source: 'schema',
                tableCount: tables
            });

            return db;
        } catch (error) {
            console.warn('[SqliteService] Could not create database from schema.sql:', error);
            return null;
        }
    }

    /**
     * Create legacy database with inline schema (fallback)
     */
    private createLegacyDb(SQL: SqlJsStatic): Database {
        const db = new SQL.Database();
        this.seedLegacyDatabase(db);
        const tables = this.getTableCount(db);
        this.statusSubject.next({
            initialized: true,
            source: 'legacy',
            tableCount: tables
        });
        return db;
    }

    private getTableCount(db: Database): number {
        const result = db.exec("SELECT COUNT(*) FROM sqlite_master WHERE type='table'");
        return result.length > 0 ? (result[0].values[0][0] as number) : 0;
    }

    // ============================================
    // Mock Data Seeding
    // ============================================

    private seedMockData(db: Database): void {
        try {
            // Generate UUIDs for mock data
            const generateUuid = () => crypto.randomUUID();
            const now = new Date().toISOString();

            // Seed protocol definitions
            MOCK_PROTOCOLS.forEach(p => {
                const stmt = db.prepare(`
                    INSERT OR IGNORE INTO function_protocol_definitions
                    (accession_id, name, fqn, description, is_top_level, version, created_at, updated_at, properties_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                `);
                stmt.run([
                    p.accession_id || generateUuid(),
                    p.name,
                    `demo.protocols.${p.name.replace(/\s+/g, '_').toLowerCase()}`,
                    (p as any).description || null,
                    p.is_top_level ? 1 : 0,
                    (p as any).version || '1.0.0',
                    now,
                    now,
                    JSON.stringify({})
                ]);
                stmt.free();
            });

            // Seed protocol runs - need valid protocol definition references
            const protocolDefs = db.exec('SELECT accession_id FROM function_protocol_definitions LIMIT 1');
            if (protocolDefs.length > 0 && protocolDefs[0].values.length > 0) {
                const defaultProtocolId = protocolDefs[0].values[0][0] as string;

                MOCK_PROTOCOL_RUNS.forEach(r => {
                    const stmt = db.prepare(`
                        INSERT OR IGNORE INTO protocol_runs
                        (accession_id, top_level_protocol_definition_accession_id, status, created_at, updated_at, properties_json, name)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    `);
                    stmt.run([
                        r.accession_id || generateUuid(),
                        (r as any).protocol_definition_accession_id || defaultProtocolId,
                        r.status || 'pending',
                        r.created_at || now,
                        now,
                        JSON.stringify({}),
                        `Run ${r.accession_id?.slice(-6) || 'unknown'}`
                    ]);
                    stmt.free();
                });
            }

            // Seed assets, machines, and resources require more complex setup
            // For now, seed basic machine data into assets table
            MOCK_MACHINES.forEach(m => {
                const assetId = m.accession_id || generateUuid();

                // Insert into assets table first
                const assetStmt = db.prepare(`
                    INSERT OR IGNORE INTO assets
                    (accession_id, asset_type, name, fqn, created_at, updated_at, properties_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                `);
                assetStmt.run([
                    assetId,
                    'MACHINE',
                    m.name,
                    (m as any).fqn || `machines.${m.name.replace(/\s+/g, '_').toLowerCase()}`,
                    now,
                    now,
                    JSON.stringify({})
                ]);
                assetStmt.free();

                // Insert into machines table
                // NOTE: 'machines' table does not have created_at, updated_at, properties_json, name, asset_type, fqn
                // These are in 'assets' table.
                const machineStmt = db.prepare(`
                    INSERT OR IGNORE INTO machines
                    (accession_id, machine_category, status, description)
                    VALUES (?, ?, ?, ?)
                `);
                machineStmt.run([
                    assetId,
                    (m as any).type || 'Unknown',
                    (m as any).status || 'OFFLINE',
                    'Mock Machine'
                ]);
                machineStmt.free();
            });

            // Seed resources
            MOCK_RESOURCES.forEach(r => {
                const assetId = r.accession_id || generateUuid();

                // Insert into assets table first
                const assetStmt = db.prepare(`
                    INSERT OR IGNORE INTO assets
                    (accession_id, asset_type, name, fqn, created_at, updated_at, properties_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                `);
                assetStmt.run([
                    assetId,
                    'RESOURCE',
                    r.name,
                    (r as any).fqn || `resources.${r.name.replace(/\s+/g, '_').toLowerCase()}`,
                    now,
                    now,
                    JSON.stringify({})
                ]);
                assetStmt.free();

                // Insert into resources table
                // NOTE: 'resources' table does not have created_at, updated_at, properties_json, name, asset_type, fqn
                const resourceStmt = db.prepare(`
                    INSERT OR IGNORE INTO resources
                    (accession_id, status)
                    VALUES (?, ?)
                `);
                resourceStmt.run([
                    assetId,
                    (r as any).status || 'unknown'
                ]);
                resourceStmt.free();
            });

            console.log('[SqliteService] Mock data seeded successfully');
        } catch (error) {
            console.warn('[SqliteService] Error seeding mock data:', error);
        }
    }

    /**
     * Legacy database setup (inline schema for fallback)
     */
    private seedLegacyDatabase(db: Database): void {
        // Create tables
        db.run(`
            CREATE TABLE IF NOT EXISTS protocols (
                accession_id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                is_top_level BOOLEAN,
                version TEXT,
                parameters_json TEXT
            );
        `);

        db.run(`
            CREATE TABLE IF NOT EXISTS protocol_runs (
                accession_id TEXT PRIMARY KEY,
                protocol_accession_id TEXT,
                status TEXT,
                created_at TEXT,
                parameters_json TEXT,
                user_params_json TEXT
            );
        `);

        db.run(`
            CREATE TABLE IF NOT EXISTS resources (
                accession_id TEXT PRIMARY KEY,
                name TEXT,
                type TEXT,
                properties_json TEXT
            );
        `);

        db.run(`
            CREATE TABLE IF NOT EXISTS machines (
                accession_id TEXT PRIMARY KEY,
                name TEXT,
                type TEXT,
                properties_json TEXT
            );
        `);

        // Seed Data
        const insertProtocol = db.prepare("INSERT INTO protocols VALUES (?, ?, ?, ?, ?, ?)");
        MOCK_PROTOCOLS.forEach(p => {
            const params = (p as any).parameters ? JSON.stringify((p as any).parameters) : null;
            insertProtocol.run([
                p.accession_id,
                p.name,
                (p as any).description || null,
                p.is_top_level ? 1 : 0,
                (p as any).version || null,
                params
            ]);
        });
        insertProtocol.free();

        const insertRun = db.prepare("INSERT INTO protocol_runs VALUES (?, ?, ?, ?, ?, ?)");
        MOCK_PROTOCOL_RUNS.forEach(r => {
            const params = (r as any).parameters ? JSON.stringify((r as any).parameters) : null;
            const userParams = (r as any).user_params ? JSON.stringify((r as any).user_params) : null;
            insertRun.run([
                r.accession_id,
                (r as any).protocol_definition_accession_id || null,
                r.status || null,
                r.created_at || null,
                params,
                userParams
            ]);
        });
        insertRun.free();

        const insertResource = db.prepare("INSERT INTO resources VALUES (?, ?, ?, ?)");
        MOCK_RESOURCES.forEach(r => {
            insertResource.run([
                r.accession_id,
                r.name,
                (r as any).type || 'unknown',
                JSON.stringify(r)
            ]);
        });
        insertResource.free();

        const insertMachine = db.prepare("INSERT INTO machines VALUES (?, ?, ?, ?)");
        MOCK_MACHINES.forEach(m => {
            insertMachine.run([
                m.accession_id,
                m.name,
                (m as any).type || null,
                JSON.stringify(m)
            ]);
        });
        insertMachine.free();

        console.log('[SqliteService] Legacy database seeded with mock data');
    }

    // ============================================
    // Legacy API (backwards compatibility)
    // ============================================

    public getProtocols(): Observable<any[]> {
        return this.db$.pipe(
            map(db => {
                // Try new schema first
                try {
                    const res = db.exec("SELECT * FROM function_protocol_definitions");
                    if (res.length > 0) {
                        return this.resultToObjects(res[0]).map(p => ({
                            ...p,
                            is_top_level: p['is_top_level'] === 1 || p['is_top_level'] === true,
                            parameters: p['hardware_requirements_json'] ? JSON.parse(p['hardware_requirements_json'] as string) : null
                        }));
                    }
                } catch {
                    // Fall back to legacy table
                }

                const res = db.exec("SELECT * FROM protocols");
                if (res.length === 0) return [];
                return this.resultToObjects(res[0]).map(p => ({
                    ...p,
                    is_top_level: p['is_top_level'] === 1 || p['is_top_level'] === 'true',
                    parameters: p['parameters_json'] ? JSON.parse(p['parameters_json'] as string) : null
                }));
            })
        );
    }

    /**
     * Get a protocol definition by its accession ID
     */
    public async getProtocolById(accessionId: string): Promise<FunctionProtocolDefinition | null> {
        return new Promise((resolve) => {
            this.db$.pipe(take(1)).subscribe(db => {
                try {
                    // Try new schema first
                    const res = db.exec(
                        `SELECT * FROM function_protocol_definitions WHERE accession_id = '${accessionId}'`
                    );
                    if (res.length > 0 && res[0].values.length > 0) {
                        const protocols = this.resultToObjects(res[0]);
                        resolve(protocols[0] as FunctionProtocolDefinition);
                        return;
                    }

                    // Fall back to legacy table
                    const legacyRes = db.exec(
                        `SELECT * FROM protocols WHERE accession_id = '${accessionId}'`
                    );
                    if (legacyRes.length > 0 && legacyRes[0].values.length > 0) {
                        const protocols = this.resultToObjects(legacyRes[0]);
                        resolve(protocols[0] as FunctionProtocolDefinition);
                        return;
                    }

                    resolve(null);
                } catch (error) {
                    console.error('[SqliteService] Error fetching protocol by ID:', error);
                    resolve(null);
                }
            });
        });
    }

    public getProtocolRuns(): Observable<any[]> {
        return this.db$.pipe(
            map(db => {
                const res = db.exec("SELECT * FROM protocol_runs");
                if (res.length === 0) return [];
                return this.resultToObjects(res[0]).map(r => ({
                    ...r,
                    parameters: r['parameters_json'] ? JSON.parse(r['parameters_json'] as string) : null,
                    user_params: r['user_params_json'] ? JSON.parse(r['user_params_json'] as string) : null,
                    protocol: { accession_id: r['protocol_accession_id'] || r['top_level_protocol_definition_accession_id'], name: 'Unknown' }
                }));
            })
        );
    }

    public getProtocolRun(id: string): Observable<any> {
        return this.getProtocolRuns().pipe(
            map(runs => runs.find(r => r.accession_id === id))
        );
    }

    public createProtocolRun(run: any): Observable<any> {
        return this.db$.pipe(
            map(db => {
                // Try new schema first
                try {
                    const protocolDefs = db.exec('SELECT accession_id FROM function_protocol_definitions LIMIT 1');
                    if (protocolDefs.length > 0 && protocolDefs[0].values.length > 0) {
                        const stmt = db.prepare(`
                            INSERT INTO protocol_runs
                            (accession_id, top_level_protocol_definition_accession_id, status, created_at, updated_at, properties_json, name)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        `);
                        const now = new Date().toISOString();
                        stmt.run([
                            run.accession_id,
                            run.protocol_definition_accession_id || protocolDefs[0].values[0][0],
                            run.status || 'QUEUED',
                            run.created_at || now,
                            now,
                            JSON.stringify({}),
                            run.name || `Run ${run.accession_id.slice(-6)}`
                        ]);
                        stmt.free();
                        return run;
                    }
                } catch {
                    // Fall back to legacy
                }

                const stmt = db.prepare("INSERT INTO protocol_runs VALUES (?, ?, ?, ?, ?, ?)");
                const params = run.parameters ? JSON.stringify(run.parameters) : null;
                const userParams = run.user_params ? JSON.stringify(run.user_params) : null;
                const protocolId = run.protocol_definition_accession_id || run.protocol_accession_id || null;

                stmt.run([
                    run.accession_id,
                    protocolId,
                    run.status || 'QUEUED',
                    run.created_at || new Date().toISOString(),
                    params,
                    userParams
                ]);
                stmt.free();
                return run;
            })
        );
    }

    private resultToObjects(res: { columns: string[], values: any[][] }): Record<string, any>[] {
        return res.values.map(row => {
            const obj: Record<string, any> = {};
            res.columns.forEach((col, i) => {
                obj[col] = row[i];
            });
            return obj;
        });
    }

    // ============================================
    // Database Export/Import
    // ============================================

    /**
     * Export the current database as a Uint8Array
     */
    public exportDatabase(): Observable<Uint8Array> {
        return this.db$.pipe(
            map(db => db.export())
        );
    }

    /**
     * Import a database from a Uint8Array
     */
    public async importDatabase(data: Uint8Array): Promise<void> {
        const SQL = await initSqlJs({
            locateFile: file => `./assets/wasm/${file}`
        });

        if (this.dbInstance) {
            this.dbInstance.close();
        }

        this.dbInstance = new SQL.Database(data);
        this.repositories = createRepositories(this.dbInstance);

        const tableCount = this.getTableCount(this.dbInstance);
        this.statusSubject.next({
            initialized: true,
            source: 'prebuilt',
            tableCount
        });
    }

    // ============================================
    // Persistence (IndexedDB)
    // ============================================

    /**
     * Public method to trigger a save of the current DB state to IndexedDB
     */
    public async save(): Promise<void> {
        if (this.dbInstance) {
            await this.saveToStore(this.dbInstance);
            console.debug('[SqliteService] Database saved to IndexedDB');
        }
    }

    private async saveToStore(db: Database): Promise<void> {
        try {
            const binary = db.export();
            console.debug(`[SqliteService] Exporting database for persistence (${binary.length} bytes)`);
            return new Promise((resolve, reject) => {
                const request = indexedDB.open('praxis_browser_db', 2);
                request.onupgradeneeded = (event: any) => {
                    console.debug('[SqliteService] IndexedDB upgrade needed');
                    const db = event.target.result;
                    if (!db.objectStoreNames.contains('sqlite_store')) {
                        db.createObjectStore('sqlite_store');
                    }
                };
                request.onsuccess = (event: any) => {
                    const idb = event.target.result;
                    const tx = idb.transaction('sqlite_store', 'readwrite');
                    const store = tx.objectStore('sqlite_store');
                    const putReq = store.put(binary, 'db_snapshot');
                    putReq.onsuccess = () => console.debug('[SqliteService] Database snapshot saved successfully');
                    putReq.onerror = () => console.error('[SqliteService] Failed to save snapshot', putReq.error);

                    tx.oncomplete = () => resolve();
                    tx.onerror = () => reject(tx.error);
                };
                request.onerror = () => reject(request.error);
            });
        } catch (e) {
            console.error('[SqliteService] Error saving to IndexedDB', e);
        }
    }

    private async loadFromStore(): Promise<Uint8Array | null> {
        console.debug('[SqliteService] Attempting to load database from IndexedDB');
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('praxis_browser_db', 2);
            request.onupgradeneeded = (event: any) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains('sqlite_store')) {
                    db.createObjectStore('sqlite_store');
                }
            };
            request.onsuccess = (event: any) => {
                const idb = event.target.result;
                if (!idb.objectStoreNames.contains('sqlite_store')) {
                    console.debug('[SqliteService] Store not found, skipping load');
                    resolve(null);
                    return;
                }
                const tx = idb.transaction('sqlite_store', 'readonly');
                const store = tx.objectStore('sqlite_store');
                const getReq = store.get('db_snapshot');
                getReq.onsuccess = () => {
                    if (getReq.result) {
                        console.debug(`[SqliteService] Database snapshot found (${getReq.result.length} bytes)`);
                        resolve(getReq.result);
                    } else {
                        console.debug('[SqliteService] Database snapshot is empty');
                        resolve(null);
                    }
                };
                getReq.onerror = () => {
                    console.error('[SqliteService] Error reading snapshot', getReq.error);
                    resolve(null);
                };
            };
            request.onerror = () => {
                console.warn('[SqliteService] Error opening IndexedDB', request.error);
                resolve(null);
            };
        });
    }
}
