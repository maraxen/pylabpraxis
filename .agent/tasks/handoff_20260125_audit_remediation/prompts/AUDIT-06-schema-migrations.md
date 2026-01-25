# AUDIT-06: Implement OPFS SQLite Schema Migrations

## Problem

No schema versioning or migration path for OPFS SQLite. Schema changes will break existing users.

## Target Files

- `praxis/web-client/src/app/core/workers/sqlite-opfs.worker.ts`
- `praxis/web-client/src/app/core/services/sqlite/sqlite-opfs.service.ts`
- `praxis/web-client/src/app/core/services/sqlite/sqlite.service.ts`

## Requirements

### 1. Define Schema Version Constant

In `sqlite.service.ts` or a shared constants file:

```typescript
export const CURRENT_SCHEMA_VERSION = 1;
```

### 2. Check Version on Init

In `sqlite-opfs.worker.ts`, after opening the database:

```typescript
// Check schema version
const result = db.exec('PRAGMA user_version');
const currentVersion = result[0]?.values[0]?.[0] ?? 0;

if (currentVersion !== EXPECTED_VERSION) {
  self.postMessage({
    type: 'schema_mismatch',
    currentVersion,
    expectedVersion: EXPECTED_VERSION
  });
  return;
}
```

### 3. Handle Mismatch in Service

In `sqlite-opfs.service.ts`:

```typescript
private handleWorkerMessage(event: MessageEvent) {
  if (event.data.type === 'schema_mismatch') {
    this.showMigrationDialog(event.data.currentVersion, event.data.expectedVersion);
  }
}

private showMigrationDialog(current: number, expected: number) {
  // Show dialog explaining the need to reset
  // Offer "Factory Reset" button that calls resetToDefaults()
}
```

### 4. Add Init Timeout

In `sqlite.service.ts` init():

```typescript
init(): Observable<boolean> {
  return race(
    this.opfsService.init(),
    timer(10000).pipe(
      switchMap(() => throwError(() => new Error('Database initialization timed out')))
    )
  ).pipe(
    catchError(err => {
      this.showInitError(err.message);
      return of(false);
    })
  );
}
```

### 5. Set Version After Schema Creation

When creating schema from scratch:

```sql
PRAGMA user_version = 1;
```

## Architecture Reference

See `docs/audits/AUDIT-06-persistence.md` for initialization sequence diagram.

## Verification

```bash
npm run test --prefix praxis/web-client
```

Manual verification:

1. Clear OPFS in DevTools > Application > Storage
2. Load app, verify database initializes
3. Manually change user_version in DevTools
4. Reload, verify migration dialog appears
