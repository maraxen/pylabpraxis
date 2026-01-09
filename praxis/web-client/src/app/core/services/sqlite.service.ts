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
// Legacy mock data imports (for fallback seeding)
import { PLR_RESOURCE_DEFINITIONS, PLR_MACHINE_DEFINITIONS, OFFLINE_CAPABILITY_OVERRIDES } from '../../../assets/demo-data/plr-definitions';


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

    /** Observable that emits true when the database is ready to use */
    public readonly isReady$ = this.statusSubject.pipe(
        map(status => status.initialized)
    );

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

                    // VALIDATION: Ensure the loaded database has the new schema
                    db.exec("SELECT 1 FROM function_protocol_definitions LIMIT 1");

                    console.log('[SqliteService] Loaded database from IndexedDB persistence');
                    this.statusSubject.next({
                        initialized: true,
                        source: 'indexeddb',
                        tableCount: this.getTableCount(db)
                    });
                } catch (e) {
                    console.warn('[SqliteService] Failed to load persisted DB or schema invalid, fallback to prebuilt/fresh', e);
                    db = null;
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

            // Seed definition catalogs if empty (important for IndexedDB loaded DBs)
            this.seedDefinitionCatalogs(db);

            // Seed defaults if needed (e.g. loaded from prebuilt but empty assets)
            this.seedDefaultAssets(db);

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
                },
                {
                    version: 2,
                    name: 'add_protocol_inferred_requirements',
                    run: (d: Database) => {
                        this.safeAddColumn(d, 'function_protocol_definitions', 'inferred_requirements_json', 'TEXT');
                    }
                },
                {
                    version: 3,
                    name: 'add_protocol_failure_modes',
                    run: (d: Database) => {
                        this.safeAddColumn(d, 'function_protocol_definitions', 'failure_modes_json', 'TEXT');
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

            // Seed definition catalogs (IMPORTANT: Must happen before asset seeding)
            this.seedDefinitionCatalogs(db);

            // Seed with mock data for development
            // Seed defaults if needed (e.g. if definitions exist but no assets)
            this.seedDefaultAssets(db);

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
        this.seedDefaultAssets(db);
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

    // Seeding logic moved to seedDefaultAssets


    /**
     * Seed definition catalogs from PLR definitions
     */
    private seedDefinitionCatalogs(db: Database): void {
        try {
            // Check if catalogs table exists and has data
            let machCount = 0;
            let resCount = 0;
            try {
                const machCountRes = db.exec("SELECT COUNT(*) FROM machine_definition_catalog");
                machCount = machCountRes.length > 0 ? (machCountRes[0].values[0][0] as number) : 0;
                const resCountRes = db.exec("SELECT COUNT(*) FROM resource_definition_catalog");
                resCount = resCountRes.length > 0 ? (resCountRes[0].values[0][0] as number) : 0;
            } catch (tableCheck) {
                console.warn('[SqliteService] Definition tables may not exist yet:', tableCheck);
                // Tables don't exist - this is fine, they should be created by schema
                return;
            }

            if (machCount > 0 && resCount > 0) {
                console.log(`[SqliteService] Definition catalogs already populated (${resCount} resources, ${machCount} machines)`);
                return;
            }

            console.log('[SqliteService] Seeding definition catalogs...');
            db.exec('BEGIN TRANSACTION');

            // Seed Resources
            const insertResDef = db.prepare(`
                INSERT OR IGNORE INTO resource_definition_catalog 
                (accession_id, name, fqn, resource_type, vendor, description, properties_json, is_consumable, is_reusable, num_items)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            `);

            for (const def of PLR_RESOURCE_DEFINITIONS) {
                insertResDef.run([
                    def.accession_id,
                    def.name,
                    def.fqn,
                    def.plr_category, // maps to resource_type
                    def.vendor || null,
                    def.description || null,
                    JSON.stringify(def.properties_json),
                    def.is_consumable ? 1 : 0,
                    def.is_reusable ? 1 : 0,
                    def.num_items || null
                ]);
            }
            insertResDef.free();

            // Seed Machines
            const insertMachDef = db.prepare(`
                INSERT OR IGNORE INTO machine_definition_catalog 
                (accession_id, name, fqn, machine_category, manufacturer, description, has_deck, properties_json, capabilities_config, frontend_fqn)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            `);

            for (const def of PLR_MACHINE_DEFINITIONS) {
                // Merge dynamic capabilities config
                let capConfig = def.capabilities_config;
                if (!capConfig && OFFLINE_CAPABILITY_OVERRIDES[def.fqn]) {
                    capConfig = OFFLINE_CAPABILITY_OVERRIDES[def.fqn];
                }

                insertMachDef.run([
                    def.accession_id,
                    def.name,
                    def.fqn,
                    def.machine_type, // maps to machine_category (enum string match ideally)
                    def.vendor || null, // def uses .vendor, map to manufacturer column
                    def.description || null,
                    def.has_deck ? 1 : 0,
                    JSON.stringify(def.properties_json),
                    capConfig ? JSON.stringify(capConfig) : null,
                    def.frontend_fqn || null
                ]);
            }
            insertMachDef.free();

            db.exec('COMMIT');
            console.log(`[SqliteService] Seeded ${PLR_RESOURCE_DEFINITIONS.length} resource definitions and ${PLR_MACHINE_DEFINITIONS.length} machine definitions`);

        } catch (err) {
            try { db.exec('ROLLBACK'); } catch { /* ignore rollback errors */ }
            console.error('[SqliteService] Failed to seed definition catalogs', err);
            // Don't throw, allow continuing with empty catalogs if needed
        }
    }

    /**
     * Seed default assets if none exist
     * Creates 1 instance of every resource and machine definition
     */
    public seedDefaultAssets(db: Database): void {
        try {
            // 1. Check if we already have assets (user data)
            const countRes = db.exec("SELECT COUNT(*) FROM assets WHERE asset_type IN ('RESOURCE', 'MACHINE')");
            const assetCount = countRes.length > 0 ? (countRes[0].values[0][0] as number) : 0;

            if (assetCount > 0) {
                console.log('[SqliteService] Assets already exist, skipping default seeding');
                return;
            }

            console.log('[SqliteService] Seeding default assets from definitions...');
            const generateUuid = () => crypto.randomUUID();
            const now = new Date().toISOString();

            // 2. Seed Resources from Definitions
            // Query all resource definitions (schema uses resource_type, not kind_of_resource)
            const resDefQuery = "SELECT accession_id, name, fqn, resource_type, is_consumable FROM resource_definition_catalog";
            let resDefRows: any[] = [];
            try {
                const q = db.exec(resDefQuery);
                if (q.length > 0) resDefRows = q[0].values;
            } catch (e) {
                console.warn('[SqliteService] Could not query resource definitions for seeding', e);
            }

            db.exec('BEGIN TRANSACTION');

            try {
                const insertAsset = db.prepare(`
                    INSERT OR IGNORE INTO assets (accession_id, asset_type, name, fqn, created_at, updated_at, properties_json)
                    VALUES (?, 'RESOURCE', ?, ?, ?, ?, ?)
                `);

                const insertResource = db.prepare(`
                    INSERT OR IGNORE INTO resources (accession_id, resource_definition_accession_id, status)
                    VALUES (?, ?, ?)
                `);

                for (const row of resDefRows) {
                    const [defId, name, defFqn] = row;
                    const assetId = generateUuid();
                    const cleanName = (name as string).replace(/\s+/g, '_').toLowerCase();
                    const instanceFqn = `resources.default.${cleanName}`;

                    insertAsset.run([
                        assetId,
                        name, // Keep original name
                        instanceFqn,
                        now,
                        now,
                        JSON.stringify({ is_default: true }) // Mark as default
                    ]);

                    insertResource.run([
                        assetId,
                        defId,
                        'available'
                    ]);
                }
                insertAsset.free();
                insertResource.free();

                // 3. Seed Machines from Definitions
                // Schema: machine_definition_catalog (accession_id, name, fqn, compatible_backends, ...)
                const machDefQuery = "SELECT accession_id, name, fqn, compatible_backends, machine_category FROM machine_definition_catalog";
                let machDefRows: any[] = [];
                try {
                    const q = db.exec(machDefQuery);
                    if (q.length > 0) machDefRows = q[0].values;
                } catch (e) {
                    console.warn('[SqliteService] Could not query machine definitions for seeding', e);
                }

                const insertMachineAsset = db.prepare(`
                    INSERT OR IGNORE INTO assets (accession_id, asset_type, name, fqn, created_at, updated_at, properties_json)
                    VALUES (?, 'MACHINE', ?, ?, ?, ?, ?)
                `);

                const insertMachine = db.prepare(`
                    INSERT OR IGNORE INTO machines (accession_id, machine_category, status, is_simulation_override, connection_info, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                `);

                for (const row of machDefRows) {
                    const [defId, name, defFqn, compatibleBackendsStr, category] = row;
                    const assetId = generateUuid();

                    // Logic to check simulation
                    const isSimulated = true; // Default to true as per requirements
                    // "If definition has 'Simulator' or 'Chatterbox' in compatible_backends, use it"
                    // compatible_backends is JSON string
                    let backends: string[] = [];
                    try {
                        if (compatibleBackendsStr) {
                            const parsed = JSON.parse(compatibleBackendsStr as string);
                            if (Array.isArray(parsed)) backends = parsed;
                        }
                    } catch { /* Ignore JSON parse error */ }

                    const isNativeSim = backends.some(b => b.includes('Simulator') || b.includes('Chatterbox'));
                    // "Otherwise, patch out the IO layer" -> effectively just setting is_simulation_override=true covers our logic helper?
                    // The prompt implies we should set it.

                    const simName = `${name} (Sim)`;
                    const cleanName = (name as string).replace(/\s+/g, '_').toLowerCase();
                    const instanceFqn = `machines.default.${cleanName}`;

                    insertMachineAsset.run([
                        assetId,
                        simName,
                        instanceFqn,
                        now,
                        now,
                        JSON.stringify({ is_default: true })
                    ]);

                    insertMachine.run([
                        assetId,
                        category,
                        'IDLE',
                        1, // is_simulation_override = true
                        JSON.stringify({ backend: isNativeSim ? 'native_simulator' : 'patched_io' }),
                        `Default simulated instance of ${name}`
                    ]);
                }

                insertMachineAsset.free();
                insertMachine.free();

                db.exec('COMMIT');
                console.log(`[SqliteService] Seeded ${resDefRows.length} resources and ${machDefRows.length} machines`);

            } catch (err) {
                db.exec('ROLLBACK');
                console.error('[SqliteService] Failed to seed default assets', err);
                throw err;
            }

        } catch (error) {
            console.warn('[SqliteService] Error seeding default assets:', error);
        }
    }

    /**
     * Create a new machine asset (Browser Mode specific).
     * Mimics backend registration.
     */
    public createMachine(machine: {
        name: string;
        plr_backend: string;
        connection_type?: string;
        connection_info?: any;
        configuration?: any
    }): Observable<any> {
        return this.db$.pipe(
            map(db => {
                const now = new Date().toISOString();
                const assetId = crypto.randomUUID();

                try {
                    db.exec('BEGIN TRANSACTION');

                    // 1. Look up definition by PLR Backend (FQN)
                    const defQuery = db.prepare("SELECT accession_id, machine_category, compatible_backends, manufacturer, description FROM machine_definition_catalog WHERE fqn = ?");
                    let defRow: any[] | null = null;
                    try {
                        defQuery.bind([machine.plr_backend]);
                        if (defQuery.step()) {
                            defRow = defQuery.get();
                        }
                    } finally {
                        defQuery.free();
                    }

                    // Defaults if no definition found (though it should exist for registered hardware)
                    const defId = defRow ? defRow[0] : null;
                    const category = defRow ? defRow[1] : 'liquid_handler';
                    const description = defRow ? `User registered instance of ${defRow[4] || machine.name}` : `Registered Machine: ${machine.name}`;

                    // 2. Insert Asset
                    const insertAsset = db.prepare(`
                        INSERT INTO assets (accession_id, asset_type, name, fqn, created_at, updated_at, properties_json)
                        VALUES (?, 'MACHINE', ?, ?, ?, ?, ?)
                    `);
                    const fqn = `machines.user.${machine.name.replace(/\s+/g, '_').toLowerCase()}_${assetId.slice(0, 4)}`;

                    insertAsset.run([
                        assetId,
                        machine.name,
                        fqn,
                        now,
                        now,
                        JSON.stringify(machine.configuration || {})
                    ]);
                    insertAsset.free();

                    // 3. Insert Machine
                    // Detect if this is a simulated machine
                    const plrBackend = (machine.plr_backend || '').toLowerCase();
                    const isSimulated = plrBackend.includes('chatterbox') ||
                        plrBackend.includes('simulator') ||
                        plrBackend.includes('simulated') ||
                        machine.connection_type === 'sim';

                    const insertMachine = db.prepare(`
                        INSERT INTO machines (accession_id, machine_category, status, connection_info, description, manufacturer, model,
                        maintenance_enabled, maintenance_schedule_json, last_maintenance_json, location_label, is_simulation_override)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    `);

                    insertMachine.run([
                        assetId,
                        category,
                        'IDLE',
                        JSON.stringify({
                            connection_type: machine.connection_type || 'serial',
                            plr_backend: machine.plr_backend, // Store PLR backend FQN for REPL code generation
                            ...machine.connection_info
                        }),
                        description,
                        defRow ? defRow[3] : 'Unknown', // manufacturer
                        machine.name, // model
                        1, // maintenance_enabled (default true)
                        JSON.stringify({ frequency: 'monthly', last_maintenance: null }), // maintenance_schedule_json default
                        JSON.stringify({}), // last_maintenance_json default
                        'Main Lab', // location_label default
                        isSimulated ? 1 : 0 // is_simulation_override
                    ]);
                    insertMachine.free();

                    db.exec('COMMIT');

                    // Persist immediately
                    this.saveToStore(db);

                    console.log(`[SqliteService] Created machine: ${machine.name} (${assetId})`);

                    return {
                        accession_id: assetId,
                        name: machine.name,
                        status: 'registered',
                        fqn: fqn
                    };

                } catch (err) {
                    db.exec('ROLLBACK');
                    console.error('[SqliteService] Failed to create machine:', err);
                    throw err;
                }
            })
        );
    }

    /**
     * Reset database assets to defaults
     * Deletes all current resources and machines, then re-seeds defaults.
     */
    public resetToDefaults(): void {
        const db = this.dbInstance;
        if (!db) {
            console.error('[SqliteService] Cannot reset, DB not initialized');
            return;
        }

        try {
            console.log('[SqliteService] Resetting to defaults...');
            db.exec('BEGIN TRANSACTION');

            // 1. Delete all resources and machines instances (not definitions)
            db.run("DELETE FROM resources");
            db.run("DELETE FROM machines");

            // Delete from assets table
            db.run("DELETE FROM assets WHERE asset_type IN ('RESOURCE', 'MACHINE')");

            db.exec('COMMIT');

            // 2. Reseed
            this.seedDefaultAssets(db);

            // Update status
            const tableCount = this.getTableCount(db);
            this.statusSubject.next({
                ...this.statusSubject.value,
                tableCount
            });

            // Persist
            this.saveToStore(db);

            console.log('[SqliteService] Reset complete');

        } catch (err) {
            db.exec('ROLLBACK');
            console.error('[SqliteService] Failed to reset to defaults', err);
            throw err;
        }
    }

    // ============================================
    // Legacy API (backwards compatibility)
    // ============================================

    public getProtocols(): Observable<any[]> {
        return this.db$.pipe(
            map(db => {
                try {
                    const res = db.exec("SELECT * FROM function_protocol_definitions");
                    if (res.length === 0) return [];

                    const protocols = this.resultToObjects(res[0]);

                    // Fetch Parameters
                    let parameters: any[] = [];
                    try {
                        const paramRes = db.exec("SELECT * FROM parameter_definitions");
                        if (paramRes.length > 0) {
                            parameters = this.resultToObjects(paramRes[0]);
                        }
                    } catch (e) {
                        console.warn('[SqliteService] Failed to fetch parameters', e);
                    }

                    // Fetch Assets
                    let assets: any[] = [];
                    try {
                        const assetRes = db.exec("SELECT * FROM protocol_asset_requirements");
                        if (assetRes.length > 0) {
                            assets = this.resultToObjects(assetRes[0]);
                        }
                    } catch (e) {
                        console.warn('[SqliteService] Failed to fetch assets', e);
                    }

                    return protocols.map(p => {
                        // Join Parameters
                        const protocolParams = parameters
                            .filter(param => param['protocol_definition_accession_id'] === p['accession_id'])
                            .map(param => ({
                                ...param,
                                constraints: param['constraints'] ? JSON.parse(param['constraints'] as string) : {},
                                ui_hint: param['ui_hint'] ? JSON.parse(param['ui_hint'] as string) : {},
                                itemized_spec: param['itemized_spec'] ? JSON.parse(param['itemized_spec'] as string) : undefined
                            }));

                        // Join Assets
                        const protocolAssets = assets
                            .filter(asset => asset['protocol_definition_accession_id'] === p['accession_id'])
                            .map(asset => ({
                                ...asset,
                                constraints: asset['constraints'] ? JSON.parse(asset['constraints'] as string) : {},
                                location_constraints: asset['location_constraints'] ? JSON.parse(asset['location_constraints'] as string) : undefined
                            }));

                        return {
                            ...p,
                            is_top_level: p['is_top_level'] === 1 || p['is_top_level'] === true,
                            parameters: protocolParams,
                            assets: protocolAssets,
                            hardware_requirements: p['hardware_requirements_json'] ? JSON.parse(p['hardware_requirements_json'] as string) : {},
                            computation_graph: p['computation_graph_json'] ? JSON.parse(p['computation_graph_json'] as string) : undefined,
                            simulation_result: p['simulation_result_json'] ? JSON.parse(p['simulation_result_json'] as string) : undefined,
                            inferred_requirements: p['inferred_requirements_json'] ? JSON.parse(p['inferred_requirements_json'] as string) : undefined,
                            failure_modes: p['failure_modes_json'] ? JSON.parse(p['failure_modes_json'] as string) : undefined,
                        } as unknown as FunctionProtocolDefinition;
                    });
                } catch (e) {
                    console.error('[SqliteService] Error fetching protocols:', e);
                    return [];
                }
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
                    const res = db.exec(
                        `SELECT * FROM function_protocol_definitions WHERE accession_id = '${accessionId}'`
                    );
                    if (res.length === 0 || res[0].values.length === 0) {
                        resolve(null);
                        return;
                    }

                    const protocol = this.resultToObjects(res[0])[0];

                    // Fetch Parameters
                    let protocolParams: any[] = [];
                    try {
                        const paramRes = db.exec(
                            `SELECT * FROM parameter_definitions WHERE protocol_definition_accession_id = '${accessionId}'`
                        );
                        if (paramRes.length > 0) {
                            protocolParams = this.resultToObjects(paramRes[0]).map(param => ({
                                ...param,
                                constraints: param['constraints'] ? JSON.parse(param['constraints'] as string) : {},
                                ui_hint: param['ui_hint'] ? JSON.parse(param['ui_hint'] as string) : {},
                                itemized_spec: param['itemized_spec'] ? JSON.parse(param['itemized_spec'] as string) : undefined
                            }));
                        }
                    } catch (error) {
                        console.warn('[SqliteService] Failed to fetch parameters for protocol', error);
                    }

                    // Fetch Assets
                    let protocolAssets: any[] = [];
                    try {
                        const assetRes = db.exec(
                            `SELECT * FROM protocol_asset_requirements WHERE protocol_definition_accession_id = '${accessionId}'`
                        );
                        if (assetRes.length > 0) {
                            protocolAssets = this.resultToObjects(assetRes[0]).map(asset => ({
                                ...asset,
                                constraints: asset['constraints'] ? JSON.parse(asset['constraints'] as string) : {},
                                location_constraints: asset['location_constraints'] ? JSON.parse(asset['location_constraints'] as string) : undefined
                            }));
                        }
                    } catch (error) {
                        console.warn('[SqliteService] Failed to fetch assets for protocol', error);
                    }

                    const result = {
                        ...protocol,
                        is_top_level: protocol['is_top_level'] === 1 || protocol['is_top_level'] === true,
                        parameters: protocolParams,
                        assets: protocolAssets,
                        hardware_requirements: protocol['hardware_requirements_json'] ? JSON.parse(protocol['hardware_requirements_json'] as string) : {},
                        computation_graph: protocol['computation_graph_json'] ? JSON.parse(protocol['computation_graph_json'] as string) : undefined,
                        simulation_result: protocol['simulation_result_json'] ? JSON.parse(protocol['simulation_result_json'] as string) : undefined,
                        inferred_requirements: protocol['inferred_requirements_json'] ? JSON.parse(protocol['inferred_requirements_json'] as string) : undefined,
                        failure_modes: protocol['failure_modes_json'] ? JSON.parse(protocol['failure_modes_json'] as string) : undefined,
                    } as unknown as FunctionProtocolDefinition;

                    resolve(result);
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
    // Simulation Data Access (Browser Mode)
    // ============================================

    /**
     * Get protocol simulation data for browser mode.
     * Returns inferred requirements, failure modes, and simulation result.
     */
    public getProtocolSimulationData(protocolId: string): Observable<{
        inferred_requirements: any[];
        failure_modes: any[];
        simulation_result: any | null;
    } | null> {
        return this.db$.pipe(
            map(db => {
                try {
                    const res = db.exec(
                        `SELECT inferred_requirements_json, failure_modes_json, simulation_result_json
                         FROM function_protocol_definitions 
                         WHERE accession_id = '${protocolId}'`
                    );

                    if (res.length === 0 || res[0].values.length === 0) {
                        return null;
                    }

                    const row = res[0].values[0];
                    return {
                        inferred_requirements: row[0] ? JSON.parse(row[0] as string) : [],
                        failure_modes: row[1] ? JSON.parse(row[1] as string) : [],
                        simulation_result: row[2] ? JSON.parse(row[2] as string) : null,
                    };
                } catch (error) {
                    console.error('[SqliteService] Error fetching simulation data:', error);
                    return null;
                }
            })
        );
    }

    /**
     * Get state history for a protocol run (time travel debugging).
     * In browser mode, state history is stored in the protocol_runs table.
     */
    public getRunStateHistory(runId: string): Observable<any | null> {
        return this.db$.pipe(
            map(db => {
                try {
                    // Check if state_history_json column exists
                    const res = db.exec(
                        `SELECT state_history_json, name 
                         FROM protocol_runs 
                         WHERE accession_id = '${runId}'`
                    );

                    if (res.length === 0 || res[0].values.length === 0) {
                        return null;
                    }

                    const row = res[0].values[0];
                    const stateHistoryJson = row[0];
                    const protocolName = row[1] as string || 'Unknown';

                    if (!stateHistoryJson) {
                        // Return mock state history for demo purposes
                        return this.createMockStateHistory(runId, protocolName);
                    }

                    return JSON.parse(stateHistoryJson as string);
                } catch (error) {
                    console.warn('[SqliteService] State history not available, using mock:', error);
                    // Return mock for demo
                    return this.createMockStateHistory(runId, 'Demo Protocol');
                }
            })
        );
    }

    /**
     * Create a mock state history for demo/testing purposes.
     */
    private createMockStateHistory(runId: string, protocolName: string): any {
        const operations = [];
        let tipsLoaded = false;
        let tipsCount = 0;
        const wellVolumes: Record<string, number> = { A1: 500, A2: 500, A3: 500 };

        const methodSequence = [
            { method: 'pick_up_tips', resource: 'tip_rack' },
            { method: 'aspirate', resource: 'source_plate' },
            { method: 'dispense', resource: 'dest_plate' },
            { method: 'aspirate', resource: 'source_plate' },
            { method: 'dispense', resource: 'dest_plate' },
            { method: 'drop_tips', resource: 'tip_rack' },
        ];

        for (let i = 0; i < methodSequence.length; i++) {
            const { method, resource } = methodSequence[i];

            const stateBefore = {
                tips: { tips_loaded: tipsLoaded, tips_count: tipsCount },
                liquids: { source_plate: { ...wellVolumes } },
                on_deck: ['tip_rack', 'source_plate', 'dest_plate'],
            };

            // Update state based on operation
            if (method === 'pick_up_tips') {
                tipsLoaded = true;
                tipsCount = 8;
            } else if (method === 'drop_tips') {
                tipsLoaded = false;
                tipsCount = 0;
            } else if (method === 'aspirate') {
                wellVolumes['A1'] = Math.max(0, wellVolumes['A1'] - 50);
            }

            const stateAfter = {
                tips: { tips_loaded: tipsLoaded, tips_count: tipsCount },
                liquids: { source_plate: { ...wellVolumes } },
                on_deck: ['tip_rack', 'source_plate', 'dest_plate'],
            };

            operations.push({
                operation_index: i,
                operation_id: `op_${i}`,
                method_name: method,
                resource,
                state_before: stateBefore,
                state_after: stateAfter,
                timestamp: new Date(Date.now() + i * 1000).toISOString(),
                duration_ms: 500 + Math.random() * 1000,
                status: 'completed',
            });
        }

        return {
            run_id: runId,
            protocol_name: protocolName,
            operations,
            final_state: operations.length > 0
                ? operations[operations.length - 1].state_after
                : { tips: { tips_loaded: false, tips_count: 0 }, liquids: {}, on_deck: [] },
            total_duration_ms: operations.reduce((sum: number, op: any) => sum + (op.duration_ms || 0), 0),
        };
    }

    // ============================================
    // Database Export/Import
    // ============================================

    /**
     * Export the current database as a downloadable file
     */
    public async exportDatabase(): Promise<void> {
        if (!this.dbInstance) {
            throw new Error('Database not initialized');
        }

        const data = this.dbInstance.export();
        const blob = new Blob([data.buffer as ArrayBuffer], { type: 'application/x-sqlite3' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `praxis-backup-${new Date().toISOString().slice(0, 10)}.db`;
        a.click();

        URL.revokeObjectURL(url);
    }

    /**
     * Import a database file, replacing current data
     */
    public async importDatabase(file: File): Promise<void> {
        const buffer = await file.arrayBuffer();
        const data = new Uint8Array(buffer);

        const SQL = await initSqlJs({
            locateFile: file => `./assets/wasm/${file}`
        });

        // Close current database
        if (this.dbInstance) {
            this.dbInstance.close();
        }

        // Initialize with imported data
        this.dbInstance = new SQL.Database(data);
        this.repositories = createRepositories(this.dbInstance);

        // Save to IndexedDB
        await this.saveToStore(this.dbInstance);

        // Update status
        const tableCount = this.getTableCount(this.dbInstance);
        this.statusSubject.next({
            initialized: true,
            source: 'indexeddb',
            tableCount
        });

        console.log('[SqliteService] Database imported successfully');
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
            const data = db.export();
            const request = indexedDB.open('praxis_db', 1);

            request.onupgradeneeded = (event) => {
                const db = (event.target as IDBOpenDBRequest).result;
                if (!db.objectStoreNames.contains('sqlite')) {
                    db.createObjectStore('sqlite');
                }
            };

            return new Promise((resolve, reject) => {
                request.onsuccess = (event) => {
                    const db = (event.target as IDBOpenDBRequest).result;
                    const transaction = db.transaction('sqlite', 'readwrite');
                    const store = transaction.objectStore('sqlite');
                    store.put(data, 'db_dump');

                    transaction.oncomplete = () => resolve();
                    transaction.onerror = (e) => reject(e);
                };
                request.onerror = (e) => reject(e);
            });
        } catch (error) {
            console.error('[SqliteService] Failed to save to IndexedDB', error);
        }
    }

    /**
     * Load persisted database from IndexedDB
     */
    private async loadFromStore(): Promise<Uint8Array | null> {
        return new Promise((resolve) => {
            const request = indexedDB.open('praxis_db', 1);

            request.onupgradeneeded = (event) => {
                const db = (event.target as IDBOpenDBRequest).result;
                if (!db.objectStoreNames.contains('sqlite')) {
                    db.createObjectStore('sqlite');
                }
            };

            request.onsuccess = (event) => {
                const db = (event.target as IDBOpenDBRequest).result;
                const transaction = db.transaction('sqlite', 'readonly');
                const store = transaction.objectStore('sqlite');
                const getReq = store.get('db_dump');

                getReq.onsuccess = () => {
                    if (getReq.result) {
                        resolve(getReq.result);
                    } else {
                        resolve(null);
                    }
                };

                getReq.onerror = () => resolve(null);
            };

            request.onerror = () => resolve(null);
        });
    }

    /**
     * Clear the persisted database
     */
    public async clearStore(): Promise<void> {
        return new Promise((resolve) => {
            const request = indexedDB.open('praxis_db', 1);
            request.onsuccess = (event) => {
                const db = (event.target as IDBOpenDBRequest).result;
                const transaction = db.transaction('sqlite', 'readwrite');
                const store = transaction.objectStore('sqlite');
                store.clear();
                transaction.oncomplete = () => resolve();
            };
        });
    }

    // ============================================
    // State Resolution (Browser Mode)
    // ============================================

    /**
     * Save a state resolution for audit purposes.
     * Creates the resolution table if it doesn't exist and stores the resolution.
     */
    public saveStateResolution(runId: string, resolution: any): Observable<void> {
        return this.db$.pipe(
            map(db => {
                try {
                    // Ensure table exists
                    db.run(`
                        CREATE TABLE IF NOT EXISTS state_resolution_log (
                            id TEXT PRIMARY KEY,
                            run_id TEXT NOT NULL,
                            operation_id TEXT NOT NULL,
                            operation_description TEXT,
                            resolution_type TEXT NOT NULL,
                            action_taken TEXT NOT NULL,
                            resolved_values_json TEXT,
                            notes TEXT,
                            resolved_by TEXT DEFAULT 'user',
                            resolved_at TEXT NOT NULL,
                            created_at TEXT NOT NULL
                        )
                    `);

                    // Insert resolution
                    const stmt = db.prepare(`
                        INSERT INTO state_resolution_log 
                        (id, run_id, operation_id, operation_description, resolution_type, 
                         action_taken, resolved_values_json, notes, resolved_by, resolved_at, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    `);

                    const now = new Date().toISOString();
                    stmt.run([
                        crypto.randomUUID(),
                        runId,
                        resolution.operation_id,
                        resolution.operation_description || '',
                        resolution.resolution_type,
                        resolution.action,
                        JSON.stringify(resolution.resolved_values || {}),
                        resolution.notes || null,
                        'user',
                        now,
                        now
                    ]);
                    stmt.free();

                    // Persist changes
                    this.saveToStore(db);

                    console.log('[SqliteService] State resolution saved for run:', runId);
                } catch (error) {
                    console.error('[SqliteService] Failed to save state resolution:', error);
                    throw error;
                }
            })
        );
    }

    /**
     * Get state resolution history for a run.
     */
    public getStateResolutions(runId: string): Observable<any[]> {
        return this.db$.pipe(
            map(db => {
                try {
                    const res = db.exec(
                        `SELECT * FROM state_resolution_log WHERE run_id = '${runId}' ORDER BY resolved_at DESC`
                    );

                    if (res.length === 0) return [];
                    return this.resultToObjects(res[0]).map(r => ({
                        ...r,
                        resolved_values: r['resolved_values_json']
                            ? JSON.parse(r['resolved_values_json'] as string)
                            : {}
                    }));
                } catch {
                    // Table might not exist yet
                    return [];
                }
            })
        );
    }

    /**
     * Update protocol run status.
     * Used after state resolution to resume or abort a run.
     */
    public updateProtocolRunStatus(runId: string, status: string): Observable<void> {
        return this.db$.pipe(
            map(db => {
                try {
                    const now = new Date().toISOString();
                    db.run(
                        `UPDATE protocol_runs SET status = ?, updated_at = ? WHERE accession_id = ?`,
                        [status, now, runId]
                    );

                    // Persist changes
                    this.saveToStore(db);

                    console.log(`[SqliteService] Updated run ${runId} status to ${status}`);
                } catch (error) {
                    console.error('[SqliteService] Failed to update run status:', error);
                    throw error;
                }
            })
        );
    }
}
