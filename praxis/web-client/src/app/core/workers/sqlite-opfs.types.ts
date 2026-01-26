/**
 * Types for SQLite OPFS Web Worker communication
 */

export type RowMode = 'array' | 'object';

export interface SqliteWorkerRequest {
    id: string;
    type: 'init' | 'exec' | 'export' | 'import' | 'status' | 'close' | 'clear';
    payload: any;
}

export interface SqliteInitRequest {
    dbName?: string;
}

export interface SqliteExecRequest {
    sql: string;
    bind?: any[];
    rowMode?: RowMode;
    returnValue?: 'this' | 'resultRows' | 'saveSql';
}

export interface SqliteImportRequest {
    data: Uint8Array;
}

export interface SqliteWorkerResponse {
    id: string;
    type: 'initialized' | 'execResult' | 'exportResult' | 'importResult' | 'error' | 'closed' | 'schema_mismatch';
    payload: any;
}

export interface SqliteExecResult {
    resultRows: any[];
    columnNames: string[];
    rowCount: number;
    changes: number;
    lastInsertRowid?: number | bigint;
}

export interface SqliteErrorResponse {
    message: string;
    code?: string;
    stack?: string;
}

export interface SqliteSchemaMismatchPayload {
    currentVersion: number;
    expectedVersion: number;
}

// Schema version constant - bump this when schema changes
export const CURRENT_SCHEMA_VERSION = 1;
