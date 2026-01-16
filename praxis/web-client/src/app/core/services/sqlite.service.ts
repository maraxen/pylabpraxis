/**
 * SQLite Service for Browser-Mode Database Operations
 *
 * This service provides a sql.js - based database for browser - only mode.
 * It uses the auto - generated schema from SQLAlchemy ORM models and
 * provides repository - based access to all entities.
 *
 * Key Features:
 * - Loads prebuilt database with PLR definitions(if available)
 * - Falls back to fresh database with schema.sql
* - Provides typed repositories for all entities
    * - Maintains compatibility with existing browser/simulated mode data
        */

import { Injectable } from '@angular/core';
import { BehaviorSubject, from, Observable } from 'rxjs';
import { map, shareReplay, take, tap } from 'rxjs/operators';
import initSqlJs, { Database, SqlJsStatic } from 'sql.js';

// Type imports
import {
    createRepositories,
    type DeckDefinitionRepository,
    type DeckPositionRepository,
    type DeckRepository,
    type MachineDefinitionRepository,
    type MachineRepository,
    type ProtocolDefinitionRepository,
    type ProtocolRunRepository,
    type Repositories,
    type ResourceDefinitionRepository,
    type ResourceRepository,
    type WorkcellRepository,
} from '../db/repositories';
import type {
    FunctionProtocolDefinition,
    FunctionCallLog,
    ProtocolRun,
    Machine,
    Resource,
    MachineDefinition,
    ResourceDefinition,
    ParameterDefinition,
    ProtocolAssetRequirement
} from '../db/schema';

// Legacy mock data imports (for fallback seeding)
import { OFFLINE_CAPABILITY_OVERRIDES, PLR_MACHINE_DEFINITIONS, PLR_RESOURCE_DEFINITIONS } from '../../../assets/browser-data/plr-definitions';
import { MOCK_PROTOCOL_RUNS } from '../../../assets/browser-data/protocol-runs';
import { MOCK_PROTOCOLS } from '../../../assets/browser-data/protocols';
import { transformPlrState } from '../utils/state-transform';
import type { StateHistory, OperationStateSnapshot, StateSnapshot, InferredRequirement, FailureMode, SimulationResult } from '../models/simulation.models';


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
        this.db$ = from(this.initDbWithOptionalReset()).pipe(
            tap(db => {
                this.dbInstance = db;
                this.repositories = createRepositories(db);
            }),
            shareReplay(1)
        );
        if (typeof window !== 'undefined') {
            (window as any).sqliteService = this;
        }
    }

    /**
     * Optional reset hook: if URL has ?resetdb=1 or localStorage 'praxis_reset_db' === '1',
     * clear IndexedDB before initializing. Useful for local regeneration.
     */
    private async initDbWithOptionalReset(): Promise<Database> {
        try {
            if (typeof window !== 'undefined') {
                const url = new URL(window.location.href);
                const shouldReset = url.searchParams.get('resetdb') === '1' ||
                    (typeof localStorage !== 'undefined' && localStorage.getItem('praxis_reset_db') === '1');

                if (shouldReset) {
                    console.warn('[SqliteService] Reset flag detected. Clearing IndexedDB store...');
                    await this.clearStore();
                    if (typeof localStorage !== 'undefined') {
                        localStorage.removeItem('praxis_reset_db');
                    }
                }
            }
        } catch (e) {
            console.warn('[SqliteService] Optional reset failed or unsupported:', e);
        }

        return this.initDb();
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
                    // We check for machine_definitions table which replaces machine_definition_catalog
                    try {
                        db.exec("SELECT 1 FROM machine_definitions LIMIT 1");
                        console.log('[SqliteService] Loaded database from IndexedDB persistence');
                        this.statusSubject.next({
                            initialized: true,
                            source: 'indexeddb',
                            tableCount: this.getTableCount(db)
                        });
                    } catch (e) {
                        console.warn('[SqliteService] Persisted DB looks outdated (missing machine_definitions), forcing refresh');
                        db = null; // Invalidate old DB
                    }
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

            // Seed definition catalogs if empty (important for IndexedDB loaded DBs)
            this.seedDefinitionCatalogs(db);

            // Seed defaults if needed (e.g. if definitions exist but no assets)
            this.seedDefaultAssets(db);

            // Seed default runs for data visualization
            this.seedDefaultRuns(db);

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



    /**
     * Try to load the prebuilt database with PLR definitions
     */
    private async tryLoadPrebuiltDb(SQL: SqlJsStatic): Promise<Database | null> {
        try {
            // Try enabling prebuilt database loading
            const response = await fetch('./assets/db/praxis.db');
            if (!response.ok) {
                console.log('[SqliteService] Prebuilt database (praxis.db) not found, falling back to schema.sql');
                return null;
            }

            const buffer = await response.arrayBuffer();
            const data = new Uint8Array(buffer);
            const db = new SQL.Database(data);

            const tableCount = this.getTableCount(db);
            console.log(`[SqliteService] Loaded prebuilt database with ${tableCount} tables`);

            // Validate vital tables
            try {
                const resCount = db.exec("SELECT COUNT(*) FROM resource_definitions");
                const machCount = db.exec("SELECT COUNT(*) FROM machine_definitions");
                console.log(`[SqliteService] Prebuilt DB stats: ${resCount[0].values[0][0]} resources, ${machCount[0].values[0][0]} machines`);
            } catch (e) {
                console.warn('[SqliteService] Prebuilt DB validation failed, using fresh DB');
                return null;
            }

            this.statusSubject.next({
                initialized: true,
                source: 'prebuilt',
                tableCount: tableCount
            });

            return db;
        } catch (error) {
            console.warn('[SqliteService] Failed to load prebuilt database:', error);
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
     * Seed default protocols and runs if none exist
     */
    private seedDefaultRuns(db: Database): void {
        try {
            // Check if runs exist
            let runCount = 0;
            try {
                const countRes = db.exec("SELECT COUNT(*) FROM protocol_runs");
                runCount = countRes.length > 0 ? (countRes[0].values[0][0] as number) : 0;
            } catch (e) {
                // Table might not exist yet
                return;
            }

            if (runCount > 0) return;

            console.log('[SqliteService] Seeding default protocols and runs...');
            db.exec('BEGIN TRANSACTION');

            // 1. Seed Protocols
            // Check if protocols exist first to avoid duplicates/errors if partially seeded
            // FIXED: Added missing NOT NULL columns (solo_execution, preconfigure_deck, requires_deck)
            const insertProtocol = db.prepare(`
                INSERT OR IGNORE INTO function_protocol_definitions 
                (accession_id, name, description, version, is_top_level, category, source_file_path, 
                 module_name, function_name, fqn, tags, deprecated, 
                 hardware_requirements_json, inferred_requirements_json, failure_modes_json,
                 solo_execution, preconfigure_deck, requires_deck)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            `);

            for (const p of MOCK_PROTOCOLS) {
                insertProtocol.run([
                    p.accession_id,
                    p.name,
                    p.description,
                    p.version,
                    p.is_top_level ? 1 : 0,
                    p.category,
                    p.source_file_path,
                    p.module_name,
                    p.function_name,
                    p.fqn,
                    JSON.stringify(p.tags || []),
                    p.deprecated ? 1 : 0,
                    JSON.stringify({}), // hardware_requirements
                    JSON.stringify([]), // inferred_requirements
                    JSON.stringify([]),  // failure_modes
                    0, // solo_execution
                    0, // preconfigure_deck
                    0  // requires_deck
                ]);
            }
            insertProtocol.free();

            // 2. Seed Runs
            const insertRun = db.prepare(`
                INSERT INTO protocol_runs 
                (accession_id, top_level_protocol_definition_accession_id, name, status, 
                 created_at, updated_at, input_parameters_json, properties_json, start_time, end_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            `);

            for (const r of MOCK_PROTOCOL_RUNS) {
                insertRun.run([
                    r.accession_id,
                    r.protocol_definition_accession_id,
                    r.protocol_name,
                    r.status,
                    r.created_at,
                    r.completed_at || r.created_at, // updated_at
                    JSON.stringify(r.input_parameters_json),
                    JSON.stringify({}),
                    (r as any).started_at || null, // Map started_at -> start_time
                    (r as any).completed_at || null // Map completed_at -> end_time
                ]);
            }
            insertRun.free();

            db.exec('COMMIT');
            console.log(`[SqliteService] Seeded ${MOCK_PROTOCOL_RUNS.length} default runs`);

        } catch (e) {
            try { db.exec('ROLLBACK'); } catch { /* ignore */ }
            console.error('[SqliteService] Failed to seed default runs', e);
        }
    }

    /**
     * Seed definition catalogs from PLR definitions
     */
    private seedDefinitionCatalogs(db: Database): void {
        try {
            // Check if catalogs table exists and has data
            let machCount = 0;
            let resCount = 0;
            try {
                // UPDATE: Use Correct Table Names (machine_definitions, resource_definitions)
                const machCountRes = db.exec("SELECT COUNT(*) FROM machine_definitions");
                machCount = machCountRes.length > 0 ? (machCountRes[0].values[0][0] as number) : 0;
                const resCountRes = db.exec("SELECT COUNT(*) FROM resource_definitions");
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
            // FIXED: Removed is_reusable to align with schema.sql
            const insertResDef = db.prepare(`
                INSERT OR IGNORE INTO resource_definitions
                (accession_id, name, fqn, resource_type, vendor, description, properties_json, is_consumable, num_items)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    // def.is_reusable, <-- DROPPED per schema.sql
                    def.num_items || null
                ]);
            }
            insertResDef.free();

            // Seed Machines
            // UPDATE: Include is_simulated_frontend and available_simulation_backends and compatible_backends
            const insertMachDef = db.prepare(`
                INSERT OR IGNORE INTO machine_definitions
                (accession_id, name, fqn, machine_category, manufacturer, description, has_deck, properties_json, capabilities_config, frontend_fqn, is_simulated_frontend, available_simulation_backends, compatible_backends)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    def.machine_type, // maps to machine_category
                    def.vendor || null, // def uses .vendor, map to manufacturer column
                    def.description || null,
                    def.has_deck ? 1 : 0,
                    JSON.stringify(def.properties_json),
                    capConfig ? JSON.stringify(capConfig) : null,
                    def.frontend_fqn || null,
                    def.is_simulated_frontend ? 1 : 0,
                    def.available_simulation_backends ? JSON.stringify(def.available_simulation_backends) : null,
                    null // compatible_backends (defaults to null if not provided in mock data, or could map from backends?)
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
     * Creates 1 instance of every resource (but NOT machines anymore)
     */
    public seedDefaultAssets(db: Database): void {
        try {
            // 1. Check if we already have resources (user data)
            let resCount = 0;
            try {
                const countRes2 = db.exec("SELECT COUNT(*) FROM resources");
                resCount = countRes2.length > 0 ? (countRes2[0].values[0][0] as number) : 0;
            } catch (e) {
                // Tables might not exist
            }

            if (resCount > 0) {
                console.log('[SqliteService] Resources already exist, skipping default seeding');
                return;
            }

            console.log('[SqliteService] Seeding default resources from definitions...');
            const generateUuid = () => crypto.randomUUID();
            const now = new Date().toISOString();

            // 2. Seed Resources from Definitions
            const resDefQuery = "SELECT accession_id, name, fqn FROM resource_definitions";
            let resDefRows: any[] = [];
            try {
                const q = db.exec(resDefQuery);
                if (q.length > 0) resDefRows = q[0].values;
            } catch (e) {
                console.warn('[SqliteService] Could not query resource definitions for seeding', e);
            }

            db.exec('BEGIN TRANSACTION');

            try {
                const insertResource = db.prepare(`
                    INSERT OR IGNORE INTO resources (accession_id, asset_type, name, fqn, created_at, updated_at, properties_json, resource_definition_accession_id, status)
                    VALUES (?, 'RESOURCE', ?, ?, ?, ?, ?, ?, ?)
                `);

                let totalSeeded = 0;
                for (const row of resDefRows) {
                    const [defId, name, _defFqn] = row;

                    // Create 1 instance per definition
                    // The global infiniteConsumables flag (default: true in browser mode)
                    // automatically shows consumables with ∞ symbol in the UI
                    const assetId = generateUuid();
                    const cleanName = (name as string).replace(/\s+/g, '_').toLowerCase();
                    const instanceFqn = `resources.default.${cleanName}`;

                    insertResource.run([
                        assetId,
                        name,
                        instanceFqn,
                        now,
                        now,
                        JSON.stringify({ is_default: true }),
                        defId,
                        'available'
                    ]);
                    totalSeeded++;
                }
                insertResource.free();

                // Machine Auto-Seeding Removed:
                // We now rely on the "Catalog" model where users instantiate machines from definitions.
                // No machines are seeded by default.

                db.exec('COMMIT');
                console.log(`[SqliteService] Seeded ${totalSeeded} resources`);

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
        plr_backend?: string;
        connection_type?: string;
        connection_info?: any;
        configuration?: any;
        machine_definition_accession_id?: string;
        is_simulated?: boolean;
        simulation_backend_name?: string;
    }): Observable<any> {
        return this.db$.pipe(
            map(db => {
                const now = new Date().toISOString();
                const assetId = crypto.randomUUID();

                try {
                    db.exec('BEGIN TRANSACTION');

                    // 1. Look up definition
                    let defRow: any[] | null = null;

                    if (machine.machine_definition_accession_id) {
                        const defQuery = db.prepare("SELECT accession_id, machine_category, compatible_backends, manufacturer, description FROM machine_definitions WHERE accession_id = ?");
                        try {
                            defQuery.bind([machine.machine_definition_accession_id]);
                            if (defQuery.step()) defRow = defQuery.get();
                        } finally { defQuery.free(); }
                    }

                    const plrBackend = (machine.plr_backend || machine.connection_info?.plr_backend || '').toLowerCase();

                    if (!defRow && plrBackend) {
                        const defQuery = db.prepare("SELECT accession_id, machine_category, compatible_backends, manufacturer, description FROM machine_definitions WHERE fqn = ?");
                        try {
                            defQuery.bind([plrBackend]);
                            if (defQuery.step()) {
                                defRow = defQuery.get();
                            }
                        } finally {
                            defQuery.free();
                        }
                    }

                    // Defaults if no definition found (though it should exist for registered hardware)
                    const _defId = defRow ? defRow[0] : null;
                    const category = defRow ? defRow[1] : 'liquid_handler';
                    const description = defRow ? `User registered instance of ${defRow[4] || machine.name}` : `Registered Machine: ${machine.name}`;

                    // 2. Insert Machine
                    const isSimulated = machine.is_simulated || plrBackend.includes('chatterbox') ||
                        plrBackend.includes('simulator') ||
                        plrBackend.includes('simulated') ||
                        machine.connection_type === 'sim';

                    const insertMachine = db.prepare(`
                        INSERT INTO machines (accession_id, asset_type, name, fqn, created_at, updated_at, properties_json, machine_category, status, connection_info, description, manufacturer, model,
                        maintenance_enabled, maintenance_schedule_json, last_maintenance_json, location_label, is_simulation_override, simulation_backend_name, machine_definition_accession_id)
                        VALUES (?, 'MACHINE', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    `);

                    const fqn = `machines.user.${machine.name.replace(/\s+/g, '_').toLowerCase()}_${assetId.slice(0, 4)}`;

                    insertMachine.run([
                        assetId,
                        machine.name,
                        fqn,
                        now,
                        now,
                        JSON.stringify(machine.configuration || {}),
                        category,
                        'IDLE',
                        JSON.stringify({
                            connection_type: machine.connection_type || 'serial',
                            plr_backend: plrBackend, // Store PLR backend FQN for REPL code generation
                            ...machine.connection_info
                        }),
                        description,
                        defRow ? defRow[3] : 'Unknown', // manufacturer
                        machine.name, // model
                        1, // maintenance_enabled (default true)
                        JSON.stringify({ frequency: 'monthly', last_maintenance: null }), // maintenance_schedule_json default
                        JSON.stringify({}), // last_maintenance_json default
                        'Main Lab', // location_label default
                        isSimulated ? 1 : 0, // is_simulation_override
                        machine.simulation_backend_name || null,
                        _defId
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

    public getProtocols(): Observable<FunctionProtocolDefinition[]> {
        return this.db$.pipe(
            map(db => {
                try {
                    const res = db.exec("SELECT * FROM function_protocol_definitions");
                    if (res.length === 0) return [];

                    const protocols = this.resultToObjects(res[0]);

                    // Fetch Parameters
                    let parameters: ParameterDefinition[] = [];
                    try {
                        const paramRes = db.exec("SELECT * FROM parameter_definitions");
                        if (paramRes.length > 0) {
                            parameters = this.resultToObjects(paramRes[0]) as unknown as ParameterDefinition[];
                        }
                    } catch (e) {
                        console.warn('[SqliteService] Failed to fetch parameters', e);
                    }

                    // Fetch Assets
                    let assets: ProtocolAssetRequirement[] = [];
                    try {
                        const assetRes = db.exec("SELECT * FROM protocol_asset_requirements");
                        if (assetRes.length > 0) {
                            assets = this.resultToObjects(assetRes[0]) as unknown as ProtocolAssetRequirement[];
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
                                constraints: param['constraints_json'] as Record<string, unknown>,
                                ui_hint: param['ui_hint_json'] as Record<string, unknown>,
                                itemized_spec: param['itemized_spec_json'] as Record<string, unknown>
                            }));

                        // Join Assets
                        const protocolAssets = assets
                            .filter(asset => asset['protocol_definition_accession_id'] === p['accession_id'])
                            .map(asset => ({
                                ...asset,
                                constraints: asset['constraints_json'] as Record<string, unknown>,
                                location_constraints: asset['location_constraints_json'] as Record<string, unknown>
                            }));

                        return {
                            ...p,
                            is_top_level: p['is_top_level'] === 1 || p['is_top_level'] === true,
                            parameters: protocolParams,
                            assets: protocolAssets,
                            tags: p['tags'] ? (typeof p['tags'] === 'string' ? p['tags'].split(',') : p['tags']) : [],
                            hardware_requirements_json: p['hardware_requirements_json'] ? JSON.parse(p['hardware_requirements_json'] as string) : {},
                            computation_graph_json: p['computation_graph_json'] ? JSON.parse(p['computation_graph_json'] as string) : undefined,
                            simulation_result_json: p['simulation_result_json'] ? JSON.parse(p['simulation_result_json'] as string) : undefined,
                            inferred_requirements_json: p['inferred_requirements_json'] ? JSON.parse(p['inferred_requirements_json'] as string) : undefined,
                            failure_modes_json: p['failure_modes_json'] ? JSON.parse(p['failure_modes_json'] as string) : undefined,
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
                    let protocolParams: ParameterDefinition[] = [];
                    try {
                        const paramRes = db.exec(
                            `SELECT * FROM parameter_definitions WHERE protocol_definition_accession_id = '${accessionId}'`
                        );
                        if (paramRes.length > 0) {
                            protocolParams = this.resultToObjects(paramRes[0]).map(param => ({
                                ...param,
                                constraints_json: param['constraints_json'] ? JSON.parse(param['constraints_json'] as string) : {},
                                ui_hint_json: param['ui_hint_json'] ? JSON.parse(param['ui_hint_json'] as string) : {},
                                itemized_spec_json: param['itemized_spec_json'] ? JSON.parse(param['itemized_spec_json'] as string) : undefined
                            } as unknown as ParameterDefinition));
                        }
                    } catch (error) {
                        console.warn('[SqliteService] Failed to fetch parameters for protocol', error);
                    }

                    // Fetch Assets
                    let protocolAssets: ProtocolAssetRequirement[] = [];
                    try {
                        const assetRes = db.exec(
                            `SELECT * FROM protocol_asset_requirements WHERE protocol_definition_accession_id = '${accessionId}'`
                        );
                        if (assetRes.length > 0) {
                            protocolAssets = this.resultToObjects(assetRes[0]).map(asset => ({
                                ...asset,
                                constraints_json: asset['constraints_json'] ? JSON.parse(asset['constraints_json'] as string) : {},
                                location_constraints_json: asset['location_constraints_json'] ? JSON.parse(asset['location_constraints_json'] as string) : undefined
                            } as unknown as ProtocolAssetRequirement));
                        }
                    } catch (error) {
                        console.warn('[SqliteService] Failed to fetch assets for protocol', error);
                    }

                    const result = {
                        ...protocol,
                        is_top_level: protocol['is_top_level'] === 1 || protocol['is_top_level'] === true,
                        parameters: protocolParams,
                        assets: protocolAssets,
                        hardware_requirements_json: protocol['hardware_requirements_json'] ? JSON.parse(protocol['hardware_requirements_json'] as string) : {},
                        computation_graph_json: protocol['computation_graph_json'] ? JSON.parse(protocol['computation_graph_json'] as string) : undefined,
                        simulation_result_json: protocol['simulation_result_json'] ? JSON.parse(protocol['simulation_result_json'] as string) : undefined,
                        inferred_requirements_json: protocol['inferred_requirements_json'] ? JSON.parse(protocol['inferred_requirements_json'] as string) : undefined,
                        failure_modes_json: protocol['failure_modes_json'] ? JSON.parse(protocol['failure_modes_json'] as string) : undefined,
                    } as unknown as FunctionProtocolDefinition;

                    resolve(result);
                } catch (error) {
                    console.error('[SqliteService] Error fetching protocol by ID:', error);
                    resolve(null);
                }
            });
        });
    }

    public getProtocolRuns(): Observable<ProtocolRun[]> {
        return this.db$.pipe(
            map(db => {
                const res = db.exec("SELECT * FROM protocol_runs");
                if (res.length === 0) return [];
                return this.resultToObjects(res[0]).map(r => ({
                    ...r,
                    parameters: r['parameters_json'] ? JSON.parse(r['parameters_json'] as string) : null,
                    user_params_json: r['user_params_json'] ? JSON.parse(r['user_params_json'] as string) : null,
                    protocol: { accession_id: r['protocol_accession_id'] || r['top_level_protocol_definition_accession_id'] }
                } as unknown as ProtocolRun));
            })
        );
    }

    public getTransferLogs(runId: string): Observable<FunctionCallLog[]> {
        return this.db$.pipe(
            map(db => {
                try {
                    const res = db.exec(`SELECT * FROM function_call_logs WHERE protocol_run_accession_id = '${runId}' ORDER BY sequence_in_run ASC`);
                    if (res.length === 0) return [];
                    return this.resultToObjects(res[0]) as unknown as FunctionCallLog[];
                } catch (e) {
                    console.warn('[SqliteService] Failed to fetch transfer logs', e);
                    return [];
                }
            })
        );
    }

    public getProtocolRun(id: string): Observable<ProtocolRun | undefined> {
        return this.getProtocolRuns().pipe(
            map(runs => runs.find(r => r.accession_id === id))
        );
    }

    public createProtocolRun(run: ProtocolRun & { protocol_definition_accession_id: string }): Observable<ProtocolRun> {
        return this.db$.pipe(
            map(db => {
                const stmt = db.prepare(`
                    INSERT INTO protocol_runs 
                    (accession_id, top_level_protocol_definition_accession_id, name, status, 
                     created_at, updated_at, input_parameters_json, properties_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                `);
                const now = new Date().toISOString();
                stmt.run([
                    run.accession_id,
                    run.protocol_definition_accession_id,
                    run.name,
                    run.status || 'QUEUED',
                    run.created_at || now,
                    now,
                    JSON.stringify(run.input_parameters_json || {}),
                    JSON.stringify(run.properties_json || {})
                ]);
                stmt.free();
                this.saveToStore(db);  // Persist to IndexedDB
                return run;
            })
        );
    }

    public getResources(): Observable<Resource[]> {
        return this.db$.pipe(
            map(db => {
                try {
                    const res = db.exec("SELECT * FROM resources");
                    if (res.length === 0) return [];
                    return this.resultToObjects(res[0]).map(r => ({
                        ...r,
                        properties_json: r['properties_json'] ? JSON.parse(r['properties_json'] as string) : {}
                    } as unknown as Resource));
                } catch (e) {
                    console.warn('[SqliteService] Failed to fetch resources', e);
                    return [];
                }
            })
        );
    }

    public getMachines(): Observable<Machine[]> {
        return this.db$.pipe(
            map(db => {
                try {
                    const res = db.exec("SELECT * FROM machines");
                    if (res.length === 0) return [];
                    return this.resultToObjects(res[0]).map(m => ({
                        ...m,
                        properties_json: m['properties_json'] ? JSON.parse(m['properties_json'] as string) : {},
                        connection_info_json: m['connection_info_json'] ? JSON.parse(m['connection_info_json'] as string) : (m['connection_info'] || {})
                    } as unknown as Machine));
                } catch (e) {
                    console.warn('[SqliteService] Failed to fetch machines', e);
                    return [];
                }
            })
        );
    }



    public getResourceDefinitions(): Observable<ResourceDefinition[]> {
        return this.db$.pipe(
            map(db => {
                try {
                    const res = db.exec("SELECT * FROM resource_definitions");
                    if (res.length === 0) return [];
                    return this.resultToObjects(res[0]) as unknown as ResourceDefinition[];
                } catch (e) {
                    console.warn('[SqliteService] Failed to fetch resource definitions', e);
                    return [];
                }
            })
        );
    }

    public getMachineDefinitions(): Observable<MachineDefinition[]> {
        return this.db$.pipe(
            map(db => {
                try {
                    const res = db.exec("SELECT * FROM machine_definitions");
                    if (res.length === 0) return [];
                    return this.resultToObjects(res[0]) as unknown as MachineDefinition[];
                } catch (e) {
                    console.warn('[SqliteService] Failed to fetch machine definitions', e);
                    return [];
                }
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
        inferred_requirements: InferredRequirement[];
        failure_modes: FailureMode[];
        simulation_result: SimulationResult | null;
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

    // ============================================
    // Deck State Management
    // ============================================

    public getDeckState(machineId: string): Observable<Record<string, unknown> | null> {
        return this.db$.pipe(
            map(db => {
                try {
                    // Ensure table exists
                    db.run(`
                        CREATE TABLE IF NOT EXISTS deck_states (
                            machine_id CHAR(32) NOT NULL,
                            state_json TEXT NOT NULL,
                            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                            PRIMARY KEY (machine_id),
                            FOREIGN KEY(machine_id) REFERENCES machines (accession_id)
                        )
                    `);

                    const res = db.exec(`SELECT state_json FROM deck_states WHERE machine_id = '${machineId}'`);
                    if (res.length === 0 || res[0].values.length === 0) {
                        return null;
                    }
                    return JSON.parse(res[0].values[0][0] as string);
                } catch (error) {
                    console.error('[SqliteService] Failed to get deck state:', error);
                    return null;
                }
            })
        );
    }

    public saveDeckState(machineId: string, state: Record<string, unknown>): Observable<void> {
        return this.db$.pipe(
            map(db => {
                try {
                    // Ensure table exists (in case it wasn't created by getDeckState)
                    db.run(`
                        CREATE TABLE IF NOT EXISTS deck_states (
                            machine_id CHAR(32) NOT NULL,
                            state_json TEXT NOT NULL,
                            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                            PRIMARY KEY (machine_id),
                            FOREIGN KEY(machine_id) REFERENCES machines (accession_id)
                        )
                    `);

                    const stmt = db.prepare(`
                        INSERT OR REPLACE INTO deck_states (machine_id, state_json, updated_at)
                        VALUES (?, ?, ?)
                    `);

                    stmt.run([
                        machineId,
                        JSON.stringify(state),
                        new Date().toISOString()
                    ]);
                    stmt.free();

                    this.saveToStore(db);
                } catch (error) {
                    console.error('[SqliteService] Failed to save deck state:', error);
                    throw error;
                }
            })
        );
    }

    /**
     * Create a function call log entry.
     */
    public createFunctionCallLog(record: Partial<FunctionCallLog>): Observable<void> {
        return this.db$.pipe(
            map(db => {
                const columns = Object.keys(record);
                const values = Object.values(record);
                const placeholders = columns.map(() => '?').join(', ');

                const sql = `INSERT INTO function_call_logs (${columns.join(', ')}) VALUES (${placeholders})`;
                try {
                    db.run(sql, values as any[]);
                    // Auto-save not strictly required for every log but good for safety
                    // this.saveToStore(db); 
                } catch (err) {
                    console.error('[SqliteService] Failed to insert function call log:', err);
                    // Squelch errors to avoid breaking execution flow for logging
                }
            })
        );
    }

    public getRunStateHistory(runId: string): Observable<StateHistory | null> {
        return this.db$.pipe(
            map(db => {
                try {
                    // Get protocol run info
                    const runResult = db.exec(
                        `SELECT name FROM protocol_runs WHERE accession_id = ?`,
                        [runId]
                    );

                    const protocolName = runResult.length > 0 && runResult[0].values.length > 0
                        ? (runResult[0].values[0][0] as string) || 'Unknown'
                        : 'Unknown';

                    // Get function call logs for this run
                    const logsResult = db.exec(
                        `SELECT
                            accession_id,
                            sequence_in_run,
                            name,
                            status,
                            input_args_json,
                            state_before_json,
                            state_after_json,
                            start_time,
                            end_time,
                            duration_ms,
                            error_message_text
                         FROM function_call_logs
                         WHERE protocol_run_accession_id = ?
                         ORDER BY sequence_in_run ASC`,
                        [runId]
                    );

                    if (logsResult.length === 0 || logsResult[0].values.length === 0) {
                        return null;
                    }

                    const operations: OperationStateSnapshot[] = [];
                    let finalState: StateSnapshot | null = null;
                    let totalDurationMs = 0;

                    for (const row of logsResult[0].values) {
                        const [
                            accessionId,
                            sequenceInRun,
                            name,
                            status,
                            inputArgsJson,
                            stateBeforeJson,
                            stateAfterJson,
                            startTime,
                            endTime,
                            durationMs,
                            errorMessage,
                        ] = row;

                        // Parse and transform states
                        const rawStateBefore = stateBeforeJson
                            ? JSON.parse(stateBeforeJson as string)
                            : null;
                        const rawStateAfter = stateAfterJson
                            ? JSON.parse(stateAfterJson as string)
                            : null;

                        const stateBefore = transformPlrState(rawStateBefore);
                        const stateAfter = transformPlrState(rawStateAfter);

                        // Parse args
                        const args = inputArgsJson
                            ? JSON.parse(inputArgsJson as string)
                            : undefined;

                        // Map status
                        const opStatus: 'completed' | 'failed' | 'skipped' =
                            status === 'COMPLETED' ? 'completed' :
                                status === 'FAILED' ? 'failed' : 'skipped';

                        // Create operation snapshot
                        const operation: OperationStateSnapshot = {
                            operation_index: sequenceInRun as number,
                            operation_id: accessionId as string,
                            method_name: name as string,
                            args,
                            state_before: stateBefore || this.getEmptyState(),
                            state_after: stateAfter || this.getEmptyState(),
                            timestamp: startTime as string,
                            duration_ms: durationMs as number,
                            status: opStatus,
                            error_message: errorMessage as string | undefined,
                        };

                        operations.push(operation);

                        // Track final state and duration
                        if (stateAfter) {
                            finalState = stateAfter;
                        }
                        if (typeof durationMs === 'number') {
                            totalDurationMs += durationMs;
                        }
                    }

                    return {
                        run_id: runId,
                        protocol_name: protocolName,
                        operations,
                        final_state: finalState || this.getEmptyState(),
                        total_duration_ms: totalDurationMs,
                    } as StateHistory;

                } catch (error) {
                    console.warn('[SqliteService] State history retrieval failed:', error);
                    return null;
                }
            })
        );
    }

    private getEmptyState(): StateSnapshot {
        return {
            tips: { tips_loaded: false, tips_count: 0 },
            liquids: {},
            on_deck: [],
        };
    }

}
