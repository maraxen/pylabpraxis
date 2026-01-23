# SQLite Service Refactor: Migration Notes

**Refactored**: 2026-01-23
**Status**: Core refactor complete, consumers need updates

## What Changed

The `sqlite.service.ts` was reduced from **1900 lines** to **~250 lines** by:

- Removing all legacy sql.js sync DB code (`dbInstance`, `sqlite3`, `db$`)
- Removing IndexedDB persistence (`saveToStore`, `loadFromStore`, `clearStore`)
- Removing legacy initialization (`tryLoadPrebuiltDb`, `tryLoadSchemaDb`, `createLegacyDb`)
- Removing legacy seeding (now handled by `SqliteOpfsService.ensureSchemaAndSeeds()`)
- Removing legacy CRUD methods that used sync `db.exec()`

All database operations now delegate to `SqliteOpfsService` via async repositories.

---

## Removed Methods (Consumers Need Updates)

### High Priority - Used in Components/Services

| Method | Location | Action Required |
|--------|----------|-----------------|
| `createMachine()` | AssetService? | Use `machines.create()` via async repo |
| `createResource()` | AssetService? | Use `resources.create()` via async repo |
| `resetToDefaults()` | SettingsComponent? | Re-implement in consumer or remove feature |
| `save()` | Multiple callers | DELETE - OPFS auto-persists |
| `clearStore()` | Settings/Tests | Use OPFS clear or remove feature |

### Medium Priority - State Management

| Method | Action Required |
|--------|-----------------|
| `saveStateResolution()` | Move to state service or async repo |
| `getStateResolutions()` | Move to state service or async repo |
| `updateProtocolRunStatus()` | Use `protocolRuns.update()` |
| `getDeckState()` / `saveDeckState()` | Move to dedicated deck state service |
| `createProtocolRun()` | Use `protocolRuns.create()` |
| `updateProtocolRun()` | Use `protocolRuns.update()` |
| `createFunctionCallLog()` | Use `functionCallLogs.create()` |
| `getRunStateHistory()` | Move to run history service |
| `pruneRunHistory()` | Move to maintenance service |

### Low Priority - Already Migrated

These methods exist in the new file and delegate to async repos:

- `getProtocols()`, `getProtocolById()`, `getProtocolRuns()`
- `getMachines()`, `getResources()`
- `getMachineDefinitions()`, `getResourceDefinitions()`
- `getTransferLogs()`, `getProtocolRun()`
- `getProtocolSimulationData()`

---

## Files Likely Affected

Run this to find callers of removed methods:

```bash
grep -rn "createMachine\|createResource\|resetToDefaults\|\.save()\|clearStore\|saveStateResolution\|getDeckState\|saveDeckState\|createProtocolRun\|updateProtocolRun\|createFunctionCallLog\|getRunStateHistory\|pruneRunHistory" --include="*.ts" praxis/web-client/src/
```

Known affected files (verify):

- `asset.service.ts` - Machine/Resource CRUD
- `run-history.service.ts` - Protocol run operations
- `execution.service.ts` - Function call logging
- `settings.component.ts` - Reset functionality
- E2E tests using legacy methods

---

## Next Steps

1. [ ] Run TypeScript compiler to find all broken imports
2. [ ] Search for usages of removed methods
3. [ ] Update each consumer to use async repositories
4. [ ] Update or delete the sqlite.service.spec.ts (currently tests legacy code)
5. [ ] Run E2E tests to verify functionality
