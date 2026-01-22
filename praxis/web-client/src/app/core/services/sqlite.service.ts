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
    type MachineFrontendDefinitionRepository,
    type MachineBackendDefinitionRepository,
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
import {
    OFFLINE_CAPABILITY_OVERRIDES,
    PLR_MACHINE_DEFINITIONS,
    PLR_RESOURCE_DEFINITIONS,
    PLR_FRONTEND_DEFINITIONS,
    PLR_BACKEND_DEFINITIONS
} from '../../../assets/browser-data/plr-definitions';

import { transformPlrState } from '../utils/state-transform';
import { applyDiff } from '../utils/state-diff';
import { assetUrl, createWasmLocator } from '../utils/asset-url';
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
    public readonly isReady$ = new BehaviorSubject<boolean>(false);

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

        // Sync isReady$ with statusSubject
        this.statusSubject.subscribe(status => {
            this.isReady$.next(status.initialized);
        });
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

    public get machineFrontendDefinitions(): Observable<MachineFrontendDefinitionRepository> {
        return this.getRepositories().pipe(map(r => r.machineFrontendDefinitions));
    }

    public get machineBackendDefinitions(): Observable<MachineBackendDefinitionRepository> {
        return this.getRepositories().pipe(map(r => r.machineBackendDefinitions));
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
                locateFile: createWasmLocator()
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
            const response = await fetch(assetUrl('assets/db/praxis.db'));
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
            const response = await fetch(assetUrl('assets/db/schema.sql'));
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
        // Mock seeding removed.
        // We now rely on generate_browser_db.py to seed real protocols.
        // Runs will be created by the user.
        return;
    }

    /**
     * Seed definition catalogs from PLR definitions
     */
    private seedDefinitionCatalogs(db: Database): void {
        try {
            // Check if catalogs table exists and has data
            let machCount = 0;
            let resCount = 0;
            let frontendCount = 0;
            let backendCount = 0;
            try {
                // UPDATE: Use Correct Table Names (machine_definitions, resource_definitions)
                const machCountRes = db.exec("SELECT COUNT(*) FROM machine_definitions");
                machCount = machCountRes.length > 0 ? (machCountRes[0].values[0][0] as number) : 0;
                const resCountRes = db.exec("SELECT COUNT(*) FROM resource_definitions");
                resCount = resCountRes.length > 0 ? (resCountRes[0].values[0][0] as number) : 0;
                const frontCountRes = db.exec("SELECT COUNT(*) FROM machine_frontend_definitions");
                frontendCount = frontCountRes.length > 0 ? (frontCountRes[0].values[0][0] as number) : 0;
                const backCountRes = db.exec("SELECT COUNT(*) FROM machine_backend_definitions");
                backendCount = backCountRes.length > 0 ? (backCountRes[0].values[0][0] as number) : 0;
            } catch (tableCheck) {
                console.warn('[SqliteService] Definition tables may not exist yet:', tableCheck);
                // Tables don't exist - this is fine, they should be created by schema
                return;
            }

            // if (machCount > 0 && resCount > 0 && frontendCount > 0 && backendCount > 0) {
            //     console.log(`[SqliteService] Definition catalogs already populated (${resCount} resources, ${machCount} machines, ${frontendCount} frontends, ${backendCount} backends)`);
            //     return;
            // }

            // Always try to seed/update definitions to ensure code and DB are in sync
            // INSERT OR IGNORE will skip existing entries, effectively adding only missing ones.
            console.log('[SqliteService] Seeding definition catalogs (merging with existing)...');
            db.exec('BEGIN TRANSACTION');

            // Seed Resources
            // FIXED: Removed is_reusable to align with schema.sql
            const insertResDef = db.prepare(`
                INSERT OR IGNORE INTO resource_definitions
                (accession_id, name, fqn, resource_type, vendor, description, properties_json, is_consumable, num_items, plr_category)
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
                    // def.is_reusable, <-- DROPPED per schema.sql
                    def.num_items || null,
                    def.plr_category // maps to plr_category
                ]);
            }
            insertResDef.free();

            // Seed Machines
            // UPDATE: Include is_simulated_frontend and available_simulation_backends and compatible_backends
            const insertMachDef = db.prepare(`
                INSERT OR IGNORE INTO machine_definitions
                (accession_id, name, fqn, machine_category, manufacturer, description, has_deck, properties_json, capabilities_config, frontend_fqn, is_simulated_frontend, available_simulation_backends, compatible_backends, plr_category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    null, // compatible_backends (defaults to null if not provided in mock data, or could map from backends?)
                    'Machine' // maps to plr_category
                ]);
            }
            insertMachDef.free();

            // Seed Frontend Definitions
            const insertFrontendDef = db.prepare(`
                INSERT OR IGNORE INTO machine_frontend_definitions
                (accession_id, name, fqn, machine_category, description, has_deck, capabilities, capabilities_config, plr_category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            `);
            for (const def of PLR_FRONTEND_DEFINITIONS) {
                insertFrontendDef.run([
                    def.accession_id,
                    def.name,
                    def.fqn,
                    def.machine_category,
                    def.description || null,
                    def.has_deck ? 1 : 0,
                    def.capabilities ? JSON.stringify(def.capabilities) : null,
                    def.capabilities_config ? JSON.stringify(def.capabilities_config) : null,
                    'Machine'
                ]);
            }
            insertFrontendDef.free();

            // Seed Backend Definitions
            const insertBackendDef = db.prepare(`
                INSERT OR IGNORE INTO machine_backend_definitions
                (accession_id, fqn, name, description, backend_type, connection_config, manufacturer, model, frontend_definition_accession_id, is_deprecated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            `);
            for (const def of PLR_BACKEND_DEFINITIONS) {
                insertBackendDef.run([
                    def.accession_id,
                    def.fqn,
                    def.name,
                    def.description || null,
                    def.backend_type,
                    def.connection_config ? JSON.stringify(def.connection_config) : null,
                    def.manufacturer || null,
                    def.model || null,
                    def.frontend_definition_accession_id
                ]);
            }
            insertBackendDef.free();

            db.exec('COMMIT');
            console.log(`[SqliteService] Seeded ${PLR_RESOURCE_DEFINITIONS.length} resource definitions, ${PLR_MACHINE_DEFINITIONS.length} machine definitions, ${PLR_FRONTEND_DEFINITIONS.length} frontends and ${PLR_BACKEND_DEFINITIONS.length} backends`);

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
                console.log('[SqliteService] createMachine called with:', {
                    name: machine.name,
                    plr_backend: machine.plr_backend,
                    connection_type: machine.connection_type
                });
                const now = new Date().toISOString();
                const assetId = crypto.randomUUID();

                try {
                    db.exec('BEGIN TRANSACTION');

                    // 1. Look up definition from multiple sources
                    let defRow: any[] | null = null;
                    let backendDefId: string | null = null;
                    let frontendDefId: string | null = null;

                    if (machine.machine_definition_accession_id) {
                        // Query columns: 0=accession_id, 1=machine_category, 2=compatible_backends, 3=manufacturer, 4=description, 5=name, 6=model
                        const defQuery = db.prepare("SELECT accession_id, machine_category, compatible_backends, manufacturer, description, name, model FROM machine_definitions WHERE accession_id = ?");
                        try {
                            defQuery.bind([machine.machine_definition_accession_id]);
                            if (defQuery.step()) defRow = defQuery.get();
                        } finally { defQuery.free(); }
                    }

                    // Get the original PLR backend FQN (preserve case for code generation)
                    const plrBackendOriginal = machine.plr_backend || machine.connection_info?.plr_backend || '';
                    // Lowercased version for case-insensitive lookups
                    const plrBackendLower = plrBackendOriginal.toLowerCase();

                    // Try machine_definitions first (legacy)
                    if (!defRow && plrBackendLower) {
                        const defQuery = db.prepare("SELECT accession_id, machine_category, compatible_backends, manufacturer, description, name, model FROM machine_definitions WHERE LOWER(fqn) = ?");
                        try {
                            defQuery.bind([plrBackendLower]);
                            if (defQuery.step()) {
                                defRow = defQuery.get();
                            }
                        } finally {
                            defQuery.free();
                        }
                    }

                    // If still not found, check machine_backend_definitions (where hardware backends like CLARIOstar are stored)
                    if (!defRow && plrBackendLower) {
                        console.log(`[SqliteService] Searching backend definitions for: ${plrBackendOriginal}`);
                        // Query backend: 0=accession_id, 1=manufacturer, 2=model, 3=frontend_definition_accession_id, 4=description
                        const backendQuery = db.prepare(`
                            SELECT accession_id, manufacturer, model, frontend_definition_accession_id, description 
                            FROM machine_backend_definitions 
                            WHERE LOWER(fqn) LIKE ?
                        `);
                        try {
                            // Use LIKE with % to handle path variations (e.g. bmg_labtech.clario_star_backend vs clario_star_backend)
                            const backendClass = plrBackendLower.split('.').pop() || '';
                            const pattern = '%' + backendClass.toLowerCase();
                            console.log(`[SqliteService] Backend class: ${backendClass}, pattern: ${pattern}`);
                            backendQuery.bind([pattern]);
                            if (backendQuery.step()) {
                                const backendRow = backendQuery.get() as any[];
                                console.log(`[SqliteService] Found backend row:`, backendRow);
                                backendDefId = backendRow[0];
                                frontendDefId = backendRow[3];

                                // Now get frontend info for the category
                                if (frontendDefId) {
                                    const frontendQuery = db.prepare("SELECT machine_category, name FROM machine_frontend_definitions WHERE accession_id = ?");
                                    try {
                                        frontendQuery.bind([frontendDefId]);
                                        if (frontendQuery.step()) {
                                            const frontendRow = frontendQuery.get() as any[];
                                            console.log(`[SqliteService] Found frontend row:`, frontendRow);
                                            // Build a defRow-compatible array: [accession_id, category, null, manufacturer, description, name, model]
                                            defRow = [
                                                backendDefId,                    // 0: accession_id
                                                frontendRow[0],                  // 1: machine_category from frontend
                                                null,                            // 2: compatible_backends
                                                backendRow[1] || 'Unknown',      // 3: manufacturer from backend
                                                backendRow[4] || `${frontendRow[1]} device`, // 4: description
                                                frontendRow[1],                  // 5: name (frontend name like "PlateReader")
                                                backendRow[2] || backendRow[0]   // 6: model from backend
                                            ];
                                            console.log(`[SqliteService] Found backend definition: ${backendDefId} -> frontend: ${frontendDefId}`);
                                        } else {
                                            console.log(`[SqliteService] No frontend found for ID: ${frontendDefId}`);
                                        }
                                    } finally { frontendQuery.free(); }
                                } else {
                                    console.log(`[SqliteService] Backend has no frontend_definition_accession_id`);
                                }
                            } else {
                                console.log(`[SqliteService] No backend found matching pattern: ${pattern}`);
                            }
                        } finally {
                            backendQuery.free();
                        }
                    }

                    // Defaults if no definition found
                    const _defId = defRow ? defRow[0] : null;
                    const category = defRow ? defRow[1] : 'liquid_handler';
                    const description = defRow ? `User registered instance of ${defRow[4] || machine.name}` : `Registered Machine: ${machine.name}`;

                    // 2. Insert Machine
                    const isSimulated = machine.is_simulated || plrBackendLower.includes('chatterbox') ||
                        plrBackendLower.includes('simulator') ||
                        plrBackendLower.includes('simulated') ||
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
                            plr_backend: plrBackendOriginal, // Store PLR backend FQN for REPL code generation (preserve case!)
                            ...machine.connection_info
                        }),
                        description,
                        defRow ? defRow[3] : 'Unknown', // manufacturer (index 3)
                        defRow ? (defRow[6] || defRow[5] || machine.name) : machine.name, // model (index 6) or name (index 5) or fallback
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
                            requires_deck: p['requires_deck'] === 1 || p['requires_deck'] === true,
                            solo_execution: p['solo_execution'] === 1 || p['solo_execution'] === true,
                            preconfigure_deck: p['preconfigure_deck'] === 1 || p['preconfigure_deck'] === true,
                            parameters: protocolParams,
                            assets: protocolAssets,
                            tags: p['tags'] ? (typeof p['tags'] === 'string' ? p['tags'].split(',') : p['tags']) : [],
                            // Correctly map detailed JSON fields to domain model properties
                            hardware_requirements: p['hardware_requirements_json'] ? JSON.parse(p['hardware_requirements_json'] as string) : {}, // Mapped to hardware_requirements (internal use)
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
                        requires_deck: protocol['requires_deck'] === 1 || protocol['requires_deck'] === true,
                        solo_execution: protocol['solo_execution'] === 1 || protocol['solo_execution'] === true,
                        preconfigure_deck: protocol['preconfigure_deck'] === 1 || protocol['preconfigure_deck'] === true,
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
                    console.log('[SqliteService] getMachines raw result:', res);
                    if (res.length === 0) return [];
                    const machines = this.resultToObjects(res[0]).map(m => ({
                        ...m,
                        properties_json: m['properties_json'] ? JSON.parse(m['properties_json'] as string) : {},
                        connection_info_json: m['connection_info_json'] ? JSON.parse(m['connection_info_json'] as string) : (m['connection_info'] || {})
                    } as unknown as Machine));
                    console.log('[SqliteService] getMachines parsed:', machines.length, machines);
                    return machines;
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
            locateFile: createWasmLocator()
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
                const idb = (event.target as IDBOpenDBRequest).result;
                if (!idb.objectStoreNames.contains('sqlite')) {
                    idb.createObjectStore('sqlite');
                }
            };

            return new Promise((resolve, reject) => {
                request.onsuccess = (event) => {
                    const idb = (event.target as IDBOpenDBRequest).result;

                    if (!idb.objectStoreNames.contains('sqlite')) {
                        idb.close();
                        resolve();
                        return;
                    }

                    const transaction = idb.transaction('sqlite', 'readwrite');
                    const store = transaction.objectStore('sqlite');
                    store.put(data, 'db_dump');

                    transaction.oncomplete = () => {
                        idb.close();
                        resolve();
                    };
                    transaction.onerror = (e) => {
                        idb.close();
                        reject(e);
                    };
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
                const idb = (event.target as IDBOpenDBRequest).result;
                if (!idb.objectStoreNames.contains('sqlite')) {
                    idb.createObjectStore('sqlite');
                }
            };

            request.onsuccess = (event) => {
                const idb = (event.target as IDBOpenDBRequest).result;

                if (!idb.objectStoreNames.contains('sqlite')) {
                    idb.close();
                    resolve(null);
                    return;
                }

                const transaction = idb.transaction('sqlite', 'readonly');
                const store = transaction.objectStore('sqlite');
                const getReq = store.get('db_dump');

                let data: Uint8Array | null = null;
                getReq.onsuccess = () => {
                    data = getReq.result || null;
                };

                transaction.oncomplete = () => {
                    idb.close();
                    resolve(data);
                };

                transaction.onerror = () => {
                    idb.close();
                    resolve(null);
                };
            };

            request.onerror = () => resolve(null);
        });
    }

    /**
     * Clear the persisted database
     */
    public async clearStore(): Promise<void> {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('praxis_db', 1);

            request.onupgradeneeded = (event) => {
                const idb = (event.target as IDBOpenDBRequest).result;
                if (!idb.objectStoreNames.contains('sqlite')) {
                    idb.createObjectStore('sqlite');
                }
            };

            request.onsuccess = (event) => {
                const idb = (event.target as IDBOpenDBRequest).result;

                if (!idb.objectStoreNames.contains('sqlite')) {
                    idb.close();
                    resolve();
                    return;
                }

                try {
                    const transaction = idb.transaction('sqlite', 'readwrite');
                    const store = transaction.objectStore('sqlite');
                    store.clear();

                    transaction.oncomplete = () => {
                        idb.close();
                        resolve();
                    };
                    transaction.onerror = (event) => {
                        idb.close();
                        reject((event.target as IDBRequest).error);
                    };
                } catch (e) {
                    idb.close();
                    reject(e);
                }
            };

            request.onerror = (event) => {
                reject((event.target as IDBOpenDBRequest).error);
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
     * Create a new protocol run (Browser Mode specific)
     */
    public createProtocolRun(run: Partial<ProtocolRun>): Observable<void> {
        return this.db$.pipe(
            map(db => {
                const columns = Object.keys(run);
                const values = Object.values(run);
                const placeholders = columns.map(() => '?').join(', ');

                const sql = `INSERT INTO protocol_runs (${columns.join(', ')}) VALUES (${placeholders})`;
                try {
                    db.run(sql, values as any[]);
                    this.saveToStore(db);
                } catch (err) {
                    console.error('[SqliteService] Failed to create protocol run:', err);
                }
            })
        );
    }

    /**
     * Update an existing protocol run (Browser Mode specific)
     */
    public updateProtocolRun(accessionId: string, run: Partial<ProtocolRun>): Observable<void> {
        return this.db$.pipe(
            map(db => {
                const columns = Object.keys(run);
                const values = Object.values(run);
                const setClause = columns.map(col => `${col} = ?`).join(', ');

                const sql = `UPDATE protocol_runs SET ${setClause} WHERE accession_id = ?`;
                try {
                    db.run(sql, [...values, accessionId] as any[]);
                    this.saveToStore(db);
                } catch (err) {
                    console.error('[SqliteService] Failed to update protocol run:', err);
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


    /**
     * Get state history for a run, reconstructing from diffs if necessary.
     */
    public getRunStateHistory(runId: string): Observable<StateHistory> {
        return this.db$.pipe(
            map(db => {
                // 1. Fetch Run (for initial state)
                const runStmt = db.prepare("SELECT accession_id, initial_state_json FROM protocol_runs WHERE accession_id = ?");
                let runRow: any = null;
                try {
                    runStmt.bind([runId]);
                    if (runStmt.step()) runRow = runStmt.getAsObject();
                } finally { runStmt.free(); }

                if (!runRow) throw new Error(`Run not found: ${runId}`);

                // 2. Fetch Logs
                const logsStmt = db.prepare(`
                    SELECT accession_id, sequence_in_run, name, input_args_json, state_before_json, state_after_json, status, start_time, duration_ms, error_message_text
                    FROM function_call_logs
                    WHERE protocol_run_accession_id = ?
                    ORDER BY sequence_in_run ASC
                `);

                const logs: any[] = [];
                try {
                    logsStmt.bind([runId]);
                    while (logsStmt.step()) {
                        logs.push(logsStmt.getAsObject());
                    }
                } finally { logsStmt.free(); }

                let currentFullState = runRow.initial_state_json ? JSON.parse(runRow.initial_state_json) : {};

                const reconstruct = (current: any, storedJson: string | null) => {
                    if (!storedJson) return current;
                    try {
                        const stored = JSON.parse(storedJson);
                        if (stored && stored._is_diff) {
                            return applyDiff(current, stored.diff);
                        }
                        return stored;
                    } catch (e) {
                        console.warn('[SqliteService] Error parsing state json:', e);
                        return current;
                    }
                };

                const operations: OperationStateSnapshot[] = logs.map(log => {
                    const fullStateBefore = reconstruct(currentFullState, log.state_before_json);
                    currentFullState = fullStateBefore;

                    const fullStateAfter = reconstruct(currentFullState, log.state_after_json);
                    currentFullState = fullStateAfter;

                    return {
                        operation_index: log.sequence_in_run,
                        operation_id: log.accession_id,
                        method_name: log.name || 'unknown',
                        args: log.input_args_json ? JSON.parse(log.input_args_json) : {},
                        state_before: this.wrapStateSnapshot(fullStateBefore) || this.getEmptyState(),
                        state_after: this.wrapStateSnapshot(fullStateAfter) || this.getEmptyState(),
                        timestamp: log.start_time,
                        duration_ms: log.duration_ms,
                        status: (log.status || 'COMPLETED').toLowerCase() as any,
                        error_message: log.error_message_text
                    };
                });

                return {
                    run_id: runId,
                    protocol_name: 'Browser Run',
                    operations,
                    final_state: this.wrapStateSnapshot(currentFullState) || this.getEmptyState()
                };
            })
        );
    }

    /**
     * Prune old run history to keep DB size manageable.
     */
    public pruneRunHistory(keepCount: number = 5): Observable<void> {
        return this.db$.pipe(
            map(db => {
                console.log(`[SqliteService] Pruning run history (keeping last ${keepCount})...`);
                try {
                    db.exec('BEGIN TRANSACTION');

                    // 1. Identify runs to delete
                    const staleRunsStmt = db.prepare(`
                        SELECT accession_id FROM protocol_runs 
                        ORDER BY created_at DESC 
                        LIMIT -1 OFFSET ?
                    `);

                    const runIdsToDelete: string[] = [];
                    try {
                        staleRunsStmt.bind([keepCount]);
                        while (staleRunsStmt.step()) {
                            runIdsToDelete.push(staleRunsStmt.get()[0] as string);
                        }
                    } finally { staleRunsStmt.free(); }

                    if (runIdsToDelete.length > 0) {
                        const idList = runIdsToDelete.map(id => `'${id}'`).join(',');

                        // 2. Delete logs first
                        db.run(`DELETE FROM function_call_logs WHERE protocol_run_accession_id IN (${idList})`);

                        // 3. Delete runs
                        db.run(`DELETE FROM protocol_runs WHERE accession_id IN (${idList})`);

                        console.log(`[SqliteService] Pruned ${runIdsToDelete.length} stale runs and their logs.`);
                    }

                    db.exec('COMMIT');
                    this.saveToStore(db);
                } catch (err) {
                    db.run('ROLLBACK');
                    console.warn('[SqliteService] Failed to prune history:', err);
                }
            })
        );
    }

    private wrapStateSnapshot(plrState: any): StateSnapshot | null {
        if (!plrState) return null;
        const transformed = transformPlrState(plrState);
        if (!transformed) return null;
        return {
            tips: transformed.tips as any,
            liquids: transformed.liquids,
            on_deck: transformed.on_deck,
            raw_plr_state: transformed.raw_plr_state
        };
    }

    private getEmptyState(): StateSnapshot {
        return {
            tips: { tips_loaded: false, tips_count: 0 },
            liquids: {},
            on_deck: [],
        };
    }
}
