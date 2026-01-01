/**
 * Entity-specific Repository Implementations
 *
 * Provides specialized repositories for key entities with custom query methods.
 */

import type { Database } from 'sql.js';
import { SqliteRepository } from './sqlite-repository';
import type {
    Asset,
    ProtocolRun,
    FunctionProtocolDefinition,
    FunctionCallLog,
    Machine,
    MachineDefinitionCatalog,
    Resource,
    ResourceDefinitionCatalog,
    Deck,
    DeckDefinitionCatalog,
    DeckPositionDefinition,
    Workcell,
    FunctionDataOutput,
} from './schema';
import type { ProtocolRunStatus, MachineStatus, ResourceStatus } from './enums';

/**
 * Repository for Protocol Runs with specialized queries
 */
export class ProtocolRunRepository extends SqliteRepository<ProtocolRun> {
    constructor(db: Database) {
        super(db, 'protocol_runs', 'accession_id');
    }

    /**
     * Find protocol runs by status
     */
    findByStatus(statuses: ProtocolRunStatus[]): ProtocolRun[] {
        const placeholders = statuses.map(() => '?').join(', ');
        const sql = `SELECT * FROM ${this.tableName} WHERE status IN (${placeholders}) ORDER BY created_at DESC`;
        return this.executeQuery(sql, statuses);
    }

    /**
     * Find recent protocol runs
     */
    findRecent(limit: number = 10): ProtocolRun[] {
        return this.findAll({
            orderBy: { column: 'created_at', direction: 'DESC' },
            limit
        });
    }

    /**
     * Find protocol runs for a specific protocol definition
     */
    findByProtocolDefinition(protocolDefinitionId: string): ProtocolRun[] {
        return this.findBy(
            { top_level_protocol_definition_accession_id: protocolDefinitionId } as Partial<ProtocolRun>,
            { orderBy: { column: 'created_at', direction: 'DESC' } }
        );
    }

    /**
     * Find running protocol runs
     */
    findRunning(): ProtocolRun[] {
        return this.findByStatus(['running', 'preparing', 'resuming'] as ProtocolRunStatus[]);
    }

    /**
     * Find completed protocol runs in a date range
     */
    findCompletedInRange(startDate: string, endDate: string): ProtocolRun[] {
        const sql = `
            SELECT * FROM ${this.tableName}
            WHERE status = 'completed'
            AND end_time >= ?
            AND end_time <= ?
            ORDER BY end_time DESC
        `;
        return this.executeQuery(sql, [startDate, endDate]);
    }
}

/**
 * Repository for Protocol Definitions
 */
export class ProtocolDefinitionRepository extends SqliteRepository<FunctionProtocolDefinition> {
    constructor(db: Database) {
        super(db, 'function_protocol_definitions', 'accession_id');
    }

    /**
     * Find top-level (executable) protocols
     */
    findTopLevel(): FunctionProtocolDefinition[] {
        return this.findBy({ is_top_level: true } as Partial<FunctionProtocolDefinition>);
    }

    /**
     * Find protocols by category
     */
    findByCategory(category: string): FunctionProtocolDefinition[] {
        return this.findBy({ category } as Partial<FunctionProtocolDefinition>);
    }

    /**
     * Find active (non-deprecated) protocols
     */
    findActive(): FunctionProtocolDefinition[] {
        return this.findBy({ deprecated: false } as Partial<FunctionProtocolDefinition>);
    }

    /**
     * Search protocols by name or description
     */
    search(query: string): FunctionProtocolDefinition[] {
        const sql = `
            SELECT * FROM ${this.tableName}
            WHERE name LIKE ? OR description LIKE ? OR fqn LIKE ?
            ORDER BY name ASC
        `;
        const pattern = `%${query}%`;
        return this.executeQuery(sql, [pattern, pattern, pattern]);
    }
}

/**
 * Repository for Function Call Logs
 */
export class FunctionCallLogRepository extends SqliteRepository<FunctionCallLog> {
    constructor(db: Database) {
        super(db, 'function_call_logs', 'accession_id');
    }

    /**
     * Find logs for a protocol run, ordered by sequence
     */
    findByProtocolRun(protocolRunId: string): FunctionCallLog[] {
        return this.findBy(
            { protocol_run_accession_id: protocolRunId } as Partial<FunctionCallLog>,
            { orderBy: { column: 'sequence_in_run', direction: 'ASC' } }
        );
    }

    /**
     * Find child calls of a parent function call
     */
    findChildren(parentCallId: string): FunctionCallLog[] {
        return this.findBy(
            { parent_function_call_log_accession_id: parentCallId } as Partial<FunctionCallLog>,
            { orderBy: { column: 'sequence_in_run', direction: 'ASC' } }
        );
    }
}

/**
 * Repository for Machines
 */
export class MachineRepository extends SqliteRepository<Machine> {
    constructor(db: Database) {
        super(db, 'machines', 'accession_id');
    }

    /**
     * Find machines by status
     */
    findByStatus(statuses: MachineStatus[]): Machine[] {
        const placeholders = statuses.map(() => '?').join(', ');
        const sql = `SELECT * FROM ${this.tableName} WHERE status IN (${placeholders})`;
        return this.executeQuery(sql, statuses);
    }

    /**
     * Find available machines
     */
    findAvailable(): Machine[] {
        return this.findByStatus(['AVAILABLE'] as MachineStatus[]);
    }

    /**
     * Find machines in a workcell
     */
    findByWorkcell(workcellId: string): Machine[] {
        return this.findBy({ workcell_accession_id: workcellId } as Partial<Machine>);
    }

    /**
     * Find machines by category
     */
    findByCategory(category: string): Machine[] {
        return this.findBy({ machine_category: category } as Partial<Machine>);
    }
}

/**
 * Repository for Machine Definitions (catalog)
 */
export class MachineDefinitionRepository extends SqliteRepository<MachineDefinitionCatalog> {
    constructor(db: Database) {
        super(db, 'machine_definition_catalog', 'accession_id');
    }

    /**
     * Find by fully qualified name
     */
    findByFqn(fqn: string): MachineDefinitionCatalog | null {
        return this.findOneBy({ fqn } as Partial<MachineDefinitionCatalog>);
    }

    /**
     * Find by category
     */
    findByCategory(category: string): MachineDefinitionCatalog[] {
        return this.findBy({ machine_category: category } as Partial<MachineDefinitionCatalog>);
    }

    /**
     * Find machines with decks
     */
    findWithDecks(): MachineDefinitionCatalog[] {
        return this.findBy({ has_deck: true } as Partial<MachineDefinitionCatalog>);
    }
}

/**
 * Repository for Resources
 */
export class ResourceRepository extends SqliteRepository<Resource> {
    constructor(db: Database) {
        super(db, 'resources', 'accession_id');
    }

    /**
     * Find resources by status
     */
    findByStatus(statuses: ResourceStatus[]): Resource[] {
        const placeholders = statuses.map(() => '?').join(', ');
        const sql = `SELECT * FROM ${this.tableName} WHERE status IN (${placeholders})`;
        return this.executeQuery(sql, statuses);
    }

    /**
     * Find resources on a deck
     */
    findByDeck(deckId: string): Resource[] {
        return this.findBy({ deck_accession_id: deckId } as Partial<Resource>);
    }

    /**
     * Find children of a parent resource
     */
    findChildren(parentId: string): Resource[] {
        return this.findBy({ parent_accession_id: parentId } as Partial<Resource>);
    }
}

/**
 * Repository for Resource Definitions (catalog)
 */
export class ResourceDefinitionRepository extends SqliteRepository<ResourceDefinitionCatalog> {
    constructor(db: Database) {
        super(db, 'resource_definition_catalog', 'accession_id');
    }

    /**
     * Find by fully qualified name
     */
    findByFqn(fqn: string): ResourceDefinitionCatalog | null {
        return this.findOneBy({ fqn } as Partial<ResourceDefinitionCatalog>);
    }

    /**
     * Find consumables
     */
    findConsumables(): ResourceDefinitionCatalog[] {
        return this.findBy({ is_consumable: true } as Partial<ResourceDefinitionCatalog>);
    }

    /**
     * Find by PLR category
     */
    findByPlrCategory(category: string): ResourceDefinitionCatalog[] {
        return this.findBy({ plr_category: category } as Partial<ResourceDefinitionCatalog>);
    }

    /**
     * Find by vendor
     */
    findByVendor(vendor: string): ResourceDefinitionCatalog[] {
        return this.findBy({ vendor } as Partial<ResourceDefinitionCatalog>);
    }

    /**
     * Search by name or FQN
     */
    search(query: string): ResourceDefinitionCatalog[] {
        const sql = `
            SELECT * FROM ${this.tableName}
            WHERE name LIKE ? OR fqn LIKE ?
            ORDER BY name ASC
        `;
        const pattern = `%${query}%`;
        return this.executeQuery(sql, [pattern, pattern]);
    }

    /**
     * Find plates by well count
     */
    findPlatesByWellCount(numWells: number): ResourceDefinitionCatalog[] {
        return this.findBy({ num_items: numWells, plr_category: 'Plate' } as Partial<ResourceDefinitionCatalog>);
    }
}

/**
 * Repository for Decks
 */
export class DeckRepository extends SqliteRepository<Deck> {
    constructor(db: Database) {
        super(db, 'decks', 'accession_id');
    }

    /**
     * Find decks for a machine
     */
    findByMachine(machineId: string): Deck[] {
        return this.findBy({ parent_machine_accession_id: machineId } as Partial<Deck>);
    }
}

/**
 * Repository for Deck Definitions (catalog)
 */
export class DeckDefinitionRepository extends SqliteRepository<DeckDefinitionCatalog> {
    constructor(db: Database) {
        super(db, 'deck_definition_catalog', 'accession_id');
    }

    /**
     * Find by fully qualified name
     */
    findByFqn(fqn: string): DeckDefinitionCatalog | null {
        return this.findOneBy({ fqn } as Partial<DeckDefinitionCatalog>);
    }
}

/**
 * Repository for Deck Position Definitions
 */
export class DeckPositionRepository extends SqliteRepository<DeckPositionDefinition> {
    constructor(db: Database) {
        super(db, 'deck_position_definitions', 'accession_id');
    }

    /**
     * Find positions for a deck type
     */
    findByDeckType(deckTypeId: string): DeckPositionDefinition[] {
        return this.findBy({ deck_type_id: deckTypeId } as Partial<DeckPositionDefinition>);
    }
}

/**
 * Repository for Workcells
 */
export class WorkcellRepository extends SqliteRepository<Workcell> {
    constructor(db: Database) {
        super(db, 'workcells', 'accession_id');
    }

    /**
     * Find active workcells
     */
    findActive(): Workcell[] {
        return this.findBy({ status: 'active' } as Partial<Workcell>);
    }
}

/**
 * Repository for Function Data Outputs
 */
export class DataOutputRepository extends SqliteRepository<FunctionDataOutput> {
    constructor(db: Database) {
        super(db, 'function_data_outputs', 'accession_id');
    }

    /**
     * Find outputs for a protocol run
     */
    findByProtocolRun(protocolRunId: string): FunctionDataOutput[] {
        return this.findBy(
            { protocol_run_accession_id: protocolRunId } as Partial<FunctionDataOutput>,
            { orderBy: { column: 'measurement_timestamp', direction: 'ASC' } }
        );
    }

    /**
     * Find outputs for a function call
     */
    findByFunctionCall(functionCallId: string): FunctionDataOutput[] {
        return this.findBy({ function_call_log_accession_id: functionCallId } as Partial<FunctionDataOutput>);
    }
}

/**
 * Repository factory - creates all repositories for a database
 */
export interface Repositories {
    protocolRuns: ProtocolRunRepository;
    protocolDefinitions: ProtocolDefinitionRepository;
    functionCallLogs: FunctionCallLogRepository;
    machines: MachineRepository;
    machineDefinitions: MachineDefinitionRepository;
    resources: ResourceRepository;
    resourceDefinitions: ResourceDefinitionRepository;
    decks: DeckRepository;
    deckDefinitions: DeckDefinitionRepository;
    deckPositions: DeckPositionRepository;
    workcells: WorkcellRepository;
    dataOutputs: DataOutputRepository;
}

/**
 * Create all repositories for a database
 */
export function createRepositories(db: Database): Repositories {
    return {
        protocolRuns: new ProtocolRunRepository(db),
        protocolDefinitions: new ProtocolDefinitionRepository(db),
        functionCallLogs: new FunctionCallLogRepository(db),
        machines: new MachineRepository(db),
        machineDefinitions: new MachineDefinitionRepository(db),
        resources: new ResourceRepository(db),
        resourceDefinitions: new ResourceDefinitionRepository(db),
        decks: new DeckRepository(db),
        deckDefinitions: new DeckDefinitionRepository(db),
        deckPositions: new DeckPositionRepository(db),
        workcells: new WorkcellRepository(db),
        dataOutputs: new DataOutputRepository(db),
    };
}
