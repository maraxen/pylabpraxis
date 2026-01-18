/**
 * Generic SQLite Repository Pattern Implementation
 *
 * Provides type-safe CRUD operations for sql.js database tables.
 * Uses the generated schema interfaces for type safety.
 *
 * @module sqlite-repository
 */

import type { Database, SqlValue } from 'sql.js';

/**
 * Base entity interface that all database entities must satisfy
 */
export interface BaseEntity {
    [key: string]: unknown;
}

/**
 * Query criteria for filtering entities
 */
export type QueryCriteria<T> = Partial<T>;

/**
 * Sort order specification
 */
export interface SortSpec<T> {
    column: keyof T;
    direction: 'ASC' | 'DESC';
}

/**
 * Pagination options
 */
export interface PaginationOptions {
    limit?: number;
    offset?: number;
}

/**
 * Query options combining sorting and pagination
 */
export interface QueryOptions<T> extends PaginationOptions {
    orderBy?: SortSpec<T> | SortSpec<T>[];
}

/**
 * Result of a paginated query
 */
export interface PaginatedResult<T> {
    data: T[];
    total: number;
    limit: number;
    offset: number;
}

/**
 * Generic repository for CRUD operations on SQLite tables.
 *
 * @template T - The entity type (interface from schema.ts)
 */
export class SqliteRepository<T extends BaseEntity> {
    constructor(
        protected db: Database,
        protected tableName: string,
        protected primaryKey: string = 'accession_id'
    ) { }

    /**
     * Find all entities in the table
     */
    findAll(options?: QueryOptions<T>): T[] {
        let sql = `SELECT * FROM ${this.tableName}`;

        if (options?.orderBy) {
            sql += this.buildOrderByClause(options.orderBy);
        }

        if (options?.limit !== undefined) {
            sql += ` LIMIT ${options.limit}`;
        }

        if (options?.offset !== undefined) {
            sql += ` OFFSET ${options.offset}`;
        }

        return this.executeQuery(sql);
    }

    /**
     * Find a single entity by its primary key
     */
    findById(id: string): T | null {
        const sql = `SELECT * FROM ${this.tableName} WHERE ${this.primaryKey} = ?`;
        const results = this.executeQuery(sql, [id]);
        return results.length > 0 ? results[0] : null;
    }

    /**
     * Find entities matching the given criteria
     */
    findBy(criteria: QueryCriteria<T>, options?: QueryOptions<T>): T[] {
        const { whereClause, params } = this.buildWhereClause(criteria);
        let sql = `SELECT * FROM ${this.tableName} WHERE ${whereClause}`;

        if (options?.orderBy) {
            sql += this.buildOrderByClause(options.orderBy);
        }

        if (options?.limit !== undefined) {
            sql += ` LIMIT ${options.limit}`;
        }

        if (options?.offset !== undefined) {
            sql += ` OFFSET ${options.offset}`;
        }

        return this.executeQuery(sql, params);
    }

    /**
     * Find a single entity matching the criteria
     */
    findOneBy(criteria: QueryCriteria<T>): T | null {
        const results = this.findBy(criteria, { limit: 1 });
        return results.length > 0 ? results[0] : null;
    }

    /**
     * Count all entities in the table
     */
    count(): number {
        const sql = `SELECT COUNT(*) as count FROM ${this.tableName}`;
        const result = this.db.exec(sql);
        if (result.length === 0) return 0;
        return result[0].values[0][0] as number;
    }

    /**
     * Count entities matching the criteria
     */
    countBy(criteria: QueryCriteria<T>): number {
        const { whereClause, params } = this.buildWhereClause(criteria);
        const sql = `SELECT COUNT(*) as count FROM ${this.tableName} WHERE ${whereClause}`;
        const stmt = this.db.prepare(sql);
        stmt.bind(params as SqlValue[]);
        stmt.step();
        const count = stmt.get()[0] as number;
        stmt.free();
        return count;
    }

    /**
     * Check if an entity with the given ID exists
     */
    exists(id: string): boolean {
        const sql = `SELECT 1 FROM ${this.tableName} WHERE ${this.primaryKey} = ? LIMIT 1`;
        const stmt = this.db.prepare(sql);
        stmt.bind([id]);
        const exists = stmt.step();
        stmt.free();
        return exists;
    }

    /**
     * Create a new entity
     */
    create(entity: Omit<T, 'created_at' | 'updated_at'>): T {
        const columns = Object.keys(entity);
        const values = Object.values(entity).map(v => this.serializeValue(v)) as SqlValue[];
        const placeholders = columns.map(() => '?').join(', ');

        const sql = `INSERT INTO ${this.tableName} (${columns.join(', ')}) VALUES (${placeholders})`;
        const stmt = this.db.prepare(sql);
        stmt.run(values);
        stmt.free();

        // Return the created entity
        return this.findById((entity as Record<string, unknown>)[this.primaryKey] as string) as T;
    }

    /**
     * Update an entity by its primary key
     */
    update(id: string, updates: Partial<T>): T | null {
        const columns = Object.keys(updates);
        if (columns.length === 0) {
            return this.findById(id);
        }

        const setClause = columns.map(col => `${col} = ?`).join(', ');
        const values = [
            ...Object.values(updates).map(v => this.serializeValue(v)),
            id
        ] as SqlValue[];

        const sql = `UPDATE ${this.tableName} SET ${setClause} WHERE ${this.primaryKey} = ?`;
        const stmt = this.db.prepare(sql);
        stmt.run(values);
        stmt.free();

        return this.findById(id);
    }

    /**
     * Delete an entity by its primary key
     */
    delete(id: string): boolean {
        const sql = `DELETE FROM ${this.tableName} WHERE ${this.primaryKey} = ?`;
        const stmt = this.db.prepare(sql);
        stmt.run([id]);
        const changes = this.db.getRowsModified();
        stmt.free();
        return changes > 0;
    }

    /**
     * Delete all entities matching the criteria
     */
    deleteBy(criteria: QueryCriteria<T>): number {
        const { whereClause, params } = this.buildWhereClause(criteria);
        const sql = `DELETE FROM ${this.tableName} WHERE ${whereClause}`;
        const stmt = this.db.prepare(sql);
        stmt.run(params as SqlValue[]);
        const changes = this.db.getRowsModified();
        stmt.free();
        return changes;
    }

    /**
     * Execute a raw SQL query
     */
    rawQuery(sql: string, params?: unknown[]): T[] {
        return this.executeQuery(sql, params);
    }

    /**
     * Execute a raw SQL statement (INSERT, UPDATE, DELETE)
     */
    rawExecute(sql: string, params?: unknown[]): number {
        const stmt = this.db.prepare(sql);
        if (params) {
            stmt.run(params.map(v => this.serializeValue(v)) as SqlValue[]);
        } else {
            stmt.run();
        }
        const changes = this.db.getRowsModified();
        stmt.free();
        return changes;
    }

    // Helper methods

    protected executeQuery(sql: string, params?: unknown[]): T[] {
        const result = params
            ? this.db.exec(sql, params.map(v => this.serializeValue(v)) as SqlValue[])
            : this.db.exec(sql);

        if (result.length === 0) return [];

        return this.resultToObjects(result[0]);
    }

    protected resultToObjects(result: { columns: string[]; values: unknown[][] }): T[] {
        return result.values.map(row => {
            const obj: Record<string, unknown> = {};
            result.columns.forEach((col, i) => {
                obj[col] = this.deserializeValue(row[i], col);
            });
            return obj as T;
        });
    }

    protected buildWhereClause(criteria: QueryCriteria<T>): { whereClause: string; params: unknown[] } {
        const conditions: string[] = [];
        const params: unknown[] = [];

        for (const [key, value] of Object.entries(criteria)) {
            if (value === null) {
                conditions.push(`${key} IS NULL`);
            } else if (value === undefined) {
                continue;
            } else if (Array.isArray(value)) {
                const placeholders = value.map(() => '?').join(', ');
                conditions.push(`${key} IN (${placeholders})`);
                params.push(...value);
            } else {
                conditions.push(`${key} = ?`);
                params.push(value);
            }
        }

        return {
            whereClause: conditions.length > 0 ? conditions.join(' AND ') : '1=1',
            params
        };
    }

    protected buildOrderByClause(orderBy: SortSpec<T> | SortSpec<T>[]): string {
        const specs = Array.isArray(orderBy) ? orderBy : [orderBy];
        const clauses = specs.map(s => `${String(s.column)} ${s.direction}`);
        return ` ORDER BY ${clauses.join(', ')}`;
    }

    protected serializeValue(value: unknown): unknown {
        if (value === null || value === undefined) {
            return null;
        }
        if (typeof value === 'boolean') {
            return value ? 1 : 0;
        }
        if (typeof value === 'object') {
            return JSON.stringify(value);
        }
        return value;
    }

    protected deserializeValue(value: unknown, columnName: string): unknown {
        if (value === null) return null;

        // Check if column is a JSON column (ends with _json or is properties_json)
        if (columnName.endsWith('_json') && typeof value === 'string') {
            try {
                return JSON.parse(value);
            } catch {
                return value;
            }
        }

        // Handle boolean columns (SQLite stores as 0/1)
        if (typeof value === 'number' && this.isBooleanColumn(columnName)) {
            return value === 1;
        }

        return value;
    }

    protected isBooleanColumn(columnName: string): boolean {
        // Known boolean columns
        const booleanColumns = [
            'is_top_level',
            'solo_execution',
            'preconfigure_deck',
            'deprecated',
            'is_deck_param',
            'optional',
            'is_recursive',
            'auto_sync_enabled',
            'is_consumable',
            'has_deck',
            'is_simulation_override',
            'accepts_tips',
            'accepts_plates',
            'accepts_tubes',
            'maintenance_enabled'
        ];
        return booleanColumns.includes(columnName);
    }
}

/**
 * Create a typed repository for a specific entity type
 */
export function createRepository<T extends BaseEntity>(
    db: Database,
    tableName: string,
    primaryKey: string = 'accession_id'
): SqliteRepository<T> {
    return new SqliteRepository<T>(db, tableName, primaryKey);
}
