/**
 * Base SQLite Repository Abstraction
 *
 * Provides shared logic for SQL generation, serialization, and deserialization.
 * Used by both synchronous (SqliteRepository) and asynchronous (SqliteAsyncRepository) implementations.
 */

export interface BaseEntity {
    [key: string]: unknown;
}

export type QueryCriteria<T> = Partial<T>;

export interface SortSpec<T> {
    column: keyof T;
    direction: 'ASC' | 'DESC';
}

export interface PaginationOptions {
    limit?: number;
    offset?: number;
}

export interface QueryOptions<T> extends PaginationOptions {
    orderBy?: SortSpec<T> | SortSpec<T>[];
}

export interface PaginatedResult<T> {
    data: T[];
    total: number;
    limit: number;
    offset: number;
}

export abstract class BaseSqliteRepository<T extends BaseEntity> {
    constructor(
        protected tableName: string,
        protected primaryKey: string = 'accession_id'
    ) { }

    protected buildWhereClause(criteria: QueryCriteria<T>): { whereClause: string; params: unknown[] } {
        const conditions: string[] = [];
        const params: unknown[] = [];

        for (const [key, value] of Object.entries(criteria)) {
            if (value === null) {
                conditions.push(`${key} IS NULL`);
            } else if (value === undefined) {
                continue;
            } else if (Array.isArray(value)) {
                if (value.length === 0) {
                    // In SQL, "IN ()" is invalid or always false. 1=0 ensures no results.
                    conditions.push('1=0');
                } else {
                    const placeholders = value.map(() => '?').join(', ');
                    conditions.push(`${key} IN (${placeholders})`);
                    params.push(...value);
                }
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

    protected buildSelectSql(options?: QueryOptions<T>): string {
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

        return sql;
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

        // Check if column is a JSON column
        const isJsonColumn = columnName.endsWith('_json') ||
            columnName.endsWith('_config') ||
            [
                'capabilities',
                'compatible_backends',
                'available_simulation_backends',
                'user_configured_capabilities',
                'plr_state',
                'plr_definition',
                'allowed_resource_definition_names',
                'compatible_resource_fqns',
                'tags',
                'connection_info'
            ].includes(columnName);

        if (isJsonColumn && typeof value === 'string') {
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
            'is_simulated_frontend',
            'accepts_tips',
            'accepts_plates',
            'accepts_tubes',
            'requires_deck',
            'maintenance_enabled',
            'is_reusable', // Added back just in case
            'is_deprecated'
        ];
        return booleanColumns.includes(columnName);
    }

    protected mapRow(row: Record<string, unknown>): T {
        const obj: Record<string, unknown> = {};
        for (const [col, val] of Object.entries(row)) {
            obj[col] = this.deserializeValue(val, col);
        }
        return obj as T;
    }
}
