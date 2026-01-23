/**
 * SQLite Service Status Interface
 * 
 * Represents the initialization state of the SQLite database layer.
 */
export interface SqliteStatus {
    initialized: boolean;
    source: 'opfs' | 'none';
    tableCount: number;
    error?: string;
}

/**
 * Database export metadata
 */
export interface DatabaseExportMeta {
    exportedAt: string;
    tableCount: number;
    version: string;
}
