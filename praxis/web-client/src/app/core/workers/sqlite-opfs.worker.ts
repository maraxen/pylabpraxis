/// <reference lib="webworker" />

import sqlite3InitModule, { Database, Sqlite3Static } from '@sqlite.org/sqlite-wasm';
import {
    SqliteWorkerRequest,
    SqliteWorkerResponse,
    SqliteExecResult,
    SqliteExecRequest,
    SqliteInitRequest,
    SqliteImportRequest,
    SqliteErrorResponse,
    CURRENT_SCHEMA_VERSION
} from './sqlite-opfs.types';

let sqlite3: Sqlite3Static | null = null;
let db: Database | null = null;
let poolUtil: any = null;

/**
 * Handle incoming messages from the main thread
 */
addEventListener('message', async ({ data }: { data: SqliteWorkerRequest }) => {
    const { id, type, payload } = data;

    try {
        switch (type) {
            case 'init':
                await handleInit(id, payload);
                break;
            case 'exec':
                await handleExec(id, payload);
                break;
            case 'export':
                await handleExport(id);
                break;
            case 'import':
                await handleImport(id, payload);
                break;
            case 'status':
                await handleStatus(id);
                break;
            case 'close':
                await handleClose(id);
                break;
            case 'clear':
                await handleClear(id);
                break;
            default:
                sendError(id, `Unknown request type: ${type}`);
        }
    } catch (error: any) {
        console.error(`[SqliteOpfsWorker] Error handling ${type}:`, error);
        sendError(id, error.message || 'Unknown error', error.stack);
    }
});

/**
 * Initialize SQLite and the OPFS SAHPool VFS
 */
async function handleInit(id: string, payload: SqliteInitRequest) {
    if (db) {
        sendResponse(id, 'initialized', { success: true, message: 'Already initialized' });
        return;
    }

    const wasmPath = getWasmPath();
    console.log(`[SqliteOpfsWorker] Initializing SQLite WASM from ${wasmPath}`);

    try {
        sqlite3 = await (sqlite3InitModule as any)({
            print: console.log,
            printErr: console.error,
            locateFile: (file: string) => `${wasmPath}${file}`
        });
    } catch (err) {
        console.error('[SqliteOpfsWorker] Failed to load WASM module:', err);
        throw err;
    }

    if (!sqlite3) {
        throw new Error('Failed to initialize SQLite WASM module');
    }

    console.log('[SqliteOpfsWorker] SQLite module loaded, installing opfs-sahpool...');

    if (typeof (sqlite3 as any).installOpfsSAHPoolVfs !== 'function') {
        throw new Error('OPFS SAHPool is not available in this browser context. Please ensure you are using a supported browser (Chrome 108+, Firefox 111+, Safari 16.4+).');
    }

    // Install opfs-sahpool VFS (SyncAccessHandle Pool)
    // This VFS is preferred for performance and doesn't require SharedArrayBuffer
    // proxyUri must point to our copied asset to avoid Vite's dynamic import issues
    try {
        poolUtil = await (sqlite3 as any).installOpfsSAHPoolVfs({
            name: 'opfs-sahpool', // Standard name used by the library
            directory: 'praxis-data',
            clearOnInit: false,
            proxyUri: `${wasmPath}sqlite3-opfs-async-proxy.js`
        });
    } catch (err) {
        console.error('[SqliteOpfsWorker] Failed to install opfs-sahpool VFS:', err);
        throw err;
    }

    console.log('[SqliteOpfsWorker] opfs-sahpool VFS installed successfully');

    // Open the database using the sahpool VFS
    const dbName = payload.dbName || 'praxis.db';

    // Use the specialized DB class provided by the pool utility if available
    if (poolUtil.OpfsSAHPoolDb) {
        db = new poolUtil.OpfsSAHPoolDb(dbName);
    } else {
        db = new sqlite3.oo1.DB({
            filename: dbName,
            vfs: 'opfs-sahpool'
        });
    }

    console.log(`[SqliteOpfsWorker] Database "${dbName}" opened with opfs-sahpool VFS`);

    // Check schema version for migration handling
    if (!db) {
        throw new Error('Database failed to open');
    }
    const versionResult = db.exec({
        sql: 'PRAGMA user_version',
        rowMode: 'array',
        returnValue: 'resultRows'
    });
    const storedVersion = (versionResult as any)?.[0]?.[0] ?? 0;

    if (storedVersion !== 0 && storedVersion !== CURRENT_SCHEMA_VERSION) {
        console.warn(`[SqliteOpfsWorker] Schema mismatch: stored=${storedVersion}, expected=${CURRENT_SCHEMA_VERSION}`);
        sendResponse(id, 'schema_mismatch', {
            currentVersion: storedVersion,
            expectedVersion: CURRENT_SCHEMA_VERSION
        });
        return;
    }

    sendResponse(id, 'initialized', { success: true });
}

/**
 * Execute SQL statements
 */
async function handleExec(id: string, payload: SqliteExecRequest) {
    if (!db) throw new Error('Database not initialized');

    const { sql, bind, rowMode = 'object', returnValue = 'resultRows' } = payload;

    const columnNames: string[] = [];
    const resultRows = db.exec({
        sql,
        bind,
        rowMode,
        columnNames,
        returnValue
    } as any);

    const result: SqliteExecResult = {
        resultRows: Array.isArray(resultRows) ? resultRows : [],
        columnNames,
        rowCount: Array.isArray(resultRows) ? resultRows.length : 0,
        changes: db.changes(),
        lastInsertRowid: db.selectValue('SELECT last_insert_rowid()') as number
    };

    sendResponse(id, 'execResult', result);
}

/**
 * Export the database to a Uint8Array
 */
async function handleExport(id: string) {
    if (!db || !poolUtil) throw new Error('Database not initialized');

    const dbName = db.filename;
    console.log(`[SqliteOpfsWorker] Exporting database: ${dbName}`);

    // Use the pool utility to export the file directly from OPFS
    const data = await poolUtil.exportFile(dbName);

    if (!data) {
        throw new Error('Failed to export database (no data received)');
    }

    sendResponse(id, 'exportResult', data, [data.buffer]);
}

/**
 * Import database from Uint8Array
 */
async function handleImport(id: string, payload: SqliteImportRequest) {
    if (!sqlite3 || !poolUtil) throw new Error('SQLite not initialized');

    if (db) {
        console.log('[SqliteOpfsWorker] Closing current DB before import');
        db.close();
        db = null;
    }

    const { data } = payload;
    const dbName = 'praxis.db'; // Target name

    console.log(`[SqliteOpfsWorker] Importing database to ${dbName}, size: ${data.byteLength} bytes`);

    // Use the pool utility to import the file directly into OPFS
    await poolUtil.importDb(dbName, data);

    // Re-open the database
    if (poolUtil.OpfsSAHPoolDb) {
        db = new poolUtil.OpfsSAHPoolDb(dbName);
    } else {
        db = new sqlite3.oo1.DB({
            filename: dbName,
            vfs: 'opfs-sahpool'
        });
    }

    console.log(`[SqliteOpfsWorker] Database ${dbName} imported and re-opened`);

    sendResponse(id, 'importResult', { success: true });
}

/**
 * Get the status of the SAHPool VFS
 */
async function handleStatus(id: string) {
    if (!poolUtil) {
        sendResponse(id, 'error', { message: 'Pool utility not initialized' });
        return;
    }

    const capacity = poolUtil.getCapacity ? poolUtil.getCapacity() : -1;
    const fileCount = poolUtil.getFileCount ? poolUtil.getFileCount() : -1;
    const files = poolUtil.getFileNames ? poolUtil.getFileNames() : [];

    sendResponse(id, 'execResult', {
        capacity,
        fileCount,
        files
    });
}

/**
 * Close the database
 */
async function handleClose(id: string) {
    if (db) {
        db.close();
        db = null;
    }
    sendResponse(id, 'closed', {});
}

/**
 * Clear all database files from OPFS (factory reset)
 */
async function handleClear(id: string) {
    console.log('[SqliteOpfsWorker] Clearing database...');

    // Close current database if open
    if (db) {
        db.close();
        db = null;
    }

    // Use pool utility to wipe all managed files if available
    if (poolUtil && typeof poolUtil.wipeFiles === 'function') {
        console.log('[SqliteOpfsWorker] Wiping pool files...');
        await poolUtil.wipeFiles();
    } else if (poolUtil && typeof poolUtil.unlink === 'function') {
        // Try to delete the main database file
        try {
            await poolUtil.unlink('praxis.db');
            console.log('[SqliteOpfsWorker] Deleted praxis.db');
        } catch (err) {
            console.warn('[SqliteOpfsWorker] Could not delete praxis.db:', err);
        }
    }

    console.log('[SqliteOpfsWorker] Database cleared.');
    sendResponse(id, 'closed', {}); // Reuse 'closed' response type
}

/**
 * Helper to send success responses
 */
function sendResponse(id: string, type: SqliteWorkerResponse['type'], payload: any, transfer?: Transferable[]) {
    postMessage({ id, type, payload } as SqliteWorkerResponse, { transfer });
}

/**
 * Helper to send error responses
 */
function sendError(id: string, message: string, stack?: string) {
    postMessage({
        id,
        type: 'error',
        payload: { message, stack } as SqliteErrorResponse
    } as SqliteWorkerResponse);
}

/**
 * Helper to get the WASM path based on the worker's location
 */
function getWasmPath(): string {
    const origin = self.location.origin;
    const path = self.location.pathname;

    // Detect if we are on GitHub Pages (subdirectory /praxis/)
    const isGhPages = path.includes('/praxis/');
    const root = isGhPages ? '/praxis/' : '/';

    return `${origin}${root}assets/wasm/`;
}
