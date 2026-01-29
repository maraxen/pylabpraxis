# OPFS SQLite Initialization Optimization

## Problem
Cold start takes **~30 seconds** before `isReady$.getValue() === true`, causing E2E test timeouts.

## Root Cause
**N+1 IPC Bottleneck** in `seedDefinitionCatalogs`:
- Fallback to `initializeFromSchema()` when `praxis.db` unavailable (fresh/incognito)
- Sequential `postMessage` for every INSERT (~2000 items × 15ms = 30s)

## Solution: Batch Execution

### Step 1: Update Types
**File**: `src/app/core/workers/sqlite-opfs.types.ts`

```typescript
export interface SqliteBatchExecRequest {
    operations: {
        sql: string;
        bind?: any[];
    }[];
}

// Add to SqliteWorkerRequest union:
| { type: 'execBatch', payload: SqliteBatchExecRequest, id: string }
```

### Step 2: Update Worker
**File**: `src/app/core/workers/sqlite-opfs.worker.ts`

```typescript
// Add case to message handler switch
case 'execBatch':
    await handleExecBatch(id, payload);
    break;

// Add handler function
async function handleExecBatch(id: string, payload: SqliteBatchExecRequest) {
    if (!db) throw new Error('Database not initialized');

    const { operations } = payload;

    try {
        db.exec('BEGIN TRANSACTION');
        for (const op of operations) {
            db.exec({ sql: op.sql, bind: op.bind });
        }
        db.exec('COMMIT');
    } catch (err) {
        try { db.exec('ROLLBACK'); } catch (_) {}
        throw err;
    }

    sendResponse(id, 'execResult', { 
        rowCount: operations.length, 
        resultRows: [],
        changes: 0
    });
}
```

### Step 3: Update Service
**File**: `src/app/core/services/sqlite/sqlite-opfs.service.ts`

```typescript
// Add batch helper method
public execBatch(operations: { sql: string; bind?: any[] }[]): Observable<void> {
    const payload: SqliteBatchExecRequest = { operations };
    return this.sendRequest<void>('execBatch', payload);
}

// Refactor seedDefinitionCatalogs to batch all inserts
private seedDefinitionCatalogs(): Observable<void> {
    console.log('[SqliteOpfsService] Seeding definition catalogs (Batched)...');
    const operations: { sql: string; bind: any[] }[] = [];

    // Collect all inserts into operations array
    for (const def of PLR_RESOURCE_DEFINITIONS) {
        operations.push({ sql: insertResDef, bind: [...] });
    }
    for (const def of PLR_MACHINE_DEFINITIONS) {
        operations.push({ sql: insertMachDef, bind: [...] });
    }
    // ... frontends, backends ...

    // Execute ALL in ONE round-trip
    return this.execBatch(operations).pipe(
        map(() => console.log(`[SqliteOpfsService] Seeded ${operations.length} definitions.`))
    );
}
```

## Verification
1. Add timing: `console.time('DB_INIT_TOTAL')` around init
2. Clear site data, reload → Target: < 1000ms
3. Run E2E tests → No 30s timeout

## Expected Impact
- Before: ~30,000ms
- After: < 1,000ms
