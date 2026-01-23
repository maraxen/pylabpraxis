/**
 * Async SQLite Repository Implementation (OPFS Worker Backed)
 *
 * Provides Observable-based CRUD operations using the SqliteOpfsService.
 * Extends BaseSqliteRepository to share SQL generation logic.
 */

import { Observable, map, switchMap } from 'rxjs';
import { SqliteOpfsService } from '@core/services/sqlite';
import {
    BaseSqliteRepository,
    type BaseEntity,
    type QueryCriteria,
    type QueryOptions
} from './base-sqlite-repository';

export type { BaseEntity, QueryCriteria, QueryOptions };

export class SqliteAsyncRepository<T extends BaseEntity> extends BaseSqliteRepository<T> {
    constructor(
        protected opfs: SqliteOpfsService,
        tableName: string,
        primaryKey: string = 'accession_id'
    ) {
        super(tableName, primaryKey);
    }

    /**
     * Find all entities in the table
     */
    findAll(options?: QueryOptions<T>): Observable<T[]> {
        const sql = this.buildSelectSql(options);
        return this.executeQuery(sql);
    }

    /**
     * Find a single entity by its primary key
     */
    findById(id: string): Observable<T | null> {
        const sql = `SELECT * FROM ${this.tableName} WHERE ${this.primaryKey} = ?`;
        return this.executeQuery(sql, [id]).pipe(
            map(results => results.length > 0 ? results[0] : null)
        );
    }

    /**
     * Find entities matching the given criteria
     */
    findBy(criteria: QueryCriteria<T>, options?: QueryOptions<T>): Observable<T[]> {
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
    findOneBy(criteria: QueryCriteria<T>): Observable<T | null> {
        return this.findBy(criteria, { limit: 1 }).pipe(
            map(results => results.length > 0 ? results[0] : null)
        );
    }

    /**
     * Count all entities in the table
     */
    count(): Observable<number> {
        const sql = `SELECT COUNT(*) as count FROM ${this.tableName}`;
        return this.opfs.exec(sql, [], 'array').pipe(
            map(result => {
                if (!result.resultRows || result.resultRows.length === 0) return 0;
                return result.resultRows[0][0] as number;
            })
        );
    }

    /**
     * Count entities matching the criteria
     */
    countBy(criteria: QueryCriteria<T>): Observable<number> {
        const { whereClause, params } = this.buildWhereClause(criteria);
        const sql = `SELECT COUNT(*) as count FROM ${this.tableName} WHERE ${whereClause}`;

        return this.opfs.exec(sql, params.map(v => this.serializeValue(v)), 'array').pipe(
            map(result => {
                if (!result.resultRows || result.resultRows.length === 0) return 0;
                return result.resultRows[0][0] as number;
            })
        );
    }

    /**
     * Check if an entity with the given ID exists
     */
    exists(id: string): Observable<boolean> {
        const sql = `SELECT 1 FROM ${this.tableName} WHERE ${this.primaryKey} = ? LIMIT 1`;
        return this.opfs.exec(sql, [id], 'array').pipe(
            map(result => result.resultRows.length > 0)
        );
    }

    /**
     * Create a new entity
     */
    create(entity: Omit<T, 'created_at' | 'updated_at'>): Observable<T> {
        const columns = Object.keys(entity);
        const values = Object.values(entity).map(v => this.serializeValue(v));
        const placeholders = columns.map(() => '?').join(', ');

        const sql = `INSERT INTO ${this.tableName} (${columns.join(', ')}) VALUES (${placeholders})`;
        const id = (entity as Record<string, unknown>)[this.primaryKey] as string;

        return this.opfs.exec(sql, values).pipe(
            switchMap(() => this.findById(id)),
            map(result => {
                if (!result) throw new Error(`Failed to create entity with ID ${id}`);
                return result;
            })
        );
    }

    /**
     * Update an entity by its primary key
     */
    update(id: string, updates: Partial<T>): Observable<T | null> {
        const columns = Object.keys(updates);
        if (columns.length === 0) {
            return this.findById(id);
        }

        const setClause = columns.map(col => `${col} = ?`).join(', ');
        const values = [
            ...Object.values(updates).map(v => this.serializeValue(v)),
            id
        ];

        const sql = `UPDATE ${this.tableName} SET ${setClause} WHERE ${this.primaryKey} = ?`;

        return this.opfs.exec(sql, values).pipe(
            switchMap(() => this.findById(id))
        );
    }

    /**
     * Delete an entity by its primary key
     */
    delete(id: string): Observable<boolean> {
        const sql = `DELETE FROM ${this.tableName} WHERE ${this.primaryKey} = ?`;
        return this.opfs.exec(sql, [id]).pipe(
            map(result => result.changes > 0)
        );
    }

    /**
     * Delete all entities matching the criteria
     */
    deleteBy(criteria: QueryCriteria<T>): Observable<number> {
        const { whereClause, params } = this.buildWhereClause(criteria);
        const sql = `DELETE FROM ${this.tableName} WHERE ${whereClause}`;

        return this.opfs.exec(sql, params.map(v => this.serializeValue(v))).pipe(
            map(result => result.changes)
        );
    }

    /**
     * Execute a raw SQL query
     */
    rawQuery(sql: string, params?: unknown[]): Observable<T[]> {
        return this.executeQuery(sql, params);
    }

    /**
     * Execute a raw SQL statement (INSERT, UPDATE, DELETE)
     */
    rawExecute(sql: string, params?: unknown[]): Observable<number> {
        return this.opfs.exec(sql, params ? params.map(v => this.serializeValue(v)) : undefined).pipe(
            map(result => result.changes)
        );
    }

    // Helper methods

    protected executeQuery(sql: string, params?: unknown[]): Observable<T[]> {
        return this.opfs.exec(sql, params ? params.map(v => this.serializeValue(v)) : undefined, 'object').pipe(
            map(result => {
                if (!result.resultRows || result.resultRows.length === 0) return [];
                return result.resultRows.map(row => this.mapRow(row as Record<string, unknown>));
            })
        );
    }
}

/**
 * Create a typed async repository for a specific entity type
 */
export function createAsyncRepository<T extends BaseEntity>(
    opfs: SqliteOpfsService,
    tableName: string,
    primaryKey: string = 'accession_id'
): SqliteAsyncRepository<T> {
    return new SqliteAsyncRepository<T>(opfs, tableName, primaryKey);
}
