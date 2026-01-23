# OPFS-Only Browser Mode Refactor

**Created**: 2026-01-23  
**Status**: In Progress  
**Goal**: Eliminate dual storage paths (sql.js + IndexedDB vs OPFS) and make OPFS the ONLY storage mechanism for browser mode.

## Rationale

The current dual-path architecture creates:

1. **Code complexity** - Two repository systems (`getRepositories()` vs `getAsyncRepositories()`)
2. **Testing burden** - Feature flag permutations, migration edge cases
3. **User confusion** - Toggle in Settings that most users don't understand
4. **Bug surface** - The test failure today stemmed from AssetService calling async repos when OPFS was disabled

Since Praxis is not yet released, we can simplify now without migration concerns.

---

## Architecture Changes

### Before (Dual Path)

```
Browser Mode
├── OPFS Disabled (default)
│   ├── sql.js in-memory DB
│   ├── IndexedDB persistence (SqlitePersistenceService)
│   └── Sync repositories (getRepositories())
└── OPFS Enabled (opt-in)
    ├── sqlite-wasm in Worker
    ├── OPFS persistence (SqliteOpfsService)
    └── Async repositories (getAsyncRepositories())
```

### After (OPFS Only)

```
Browser Mode
└── OPFS (always)
    ├── sqlite-wasm in Worker
    ├── OPFS persistence (SqliteOpfsService)
    └── Async repositories (getAsyncRepositories())
```

---

## Implementation Tasks

### Phase 1: Core Simplification

- [ ] **TASK-1: Remove OPFS Feature Flag**
  - Delete `praxis_use_opfs` localStorage check from `SqliteOpfsService.init()`
  - Remove feature flag from `SqliteOpfsService` entirely
  - Always initialize OPFS when in browser mode
  
- [ ] **TASK-2: Unify Repository Access**
  - In `SqliteService`, remove `getRepositories()` or have it delegate to `getAsyncRepositories()`
  - All browser-mode callers use async repositories exclusively
  
- [x] **TASK-3: Remove Settings Toggle**
  - Delete the OPFS toggle from `SettingsComponent`
  - Remove related persistence preference logic from `ModeService`

### Phase 2: Dead Code Removal

- [ ] **TASK-4: Remove Legacy Persistence**
  - Delete `SqlitePersistenceService` (IndexedDB layer)
  - Remove `saveToStore()`, `loadFromStore()`, `clearStore()` from `SqliteService`
  - Remove `indexeddb` from status source types
  
- [ ] **TASK-5: Remove Migration Service**
  - Delete `OpfsMigrationService` entirely
  - Remove migration calls from `SqliteOpfsService.init()`
  
- [ ] **TASK-6: Remove Sync Repositories**
  - Delete sync repository classes from `repositories.ts` (or keep as base classes only if needed)
  - Update all imports to use async-only

### Phase 3: Schema & Seeding

- [x] **TASK-7: Ensure Fresh DB Initialization**
  - ✅ Prefer prebuilt `praxis.db` from generator (richer data with protocols, decks, backends)
  - ✅ Fallback to `schema.sql` + TypeScript seeding if prebuilt unavailable
  - ✅ Added `resetToDefaults()` method to clear and reload database
  - ✅ Wired up Settings > Reset to Defaults button
  
### Phase 4: Test Updates

- [ ] **TASK-8: Simplify E2E Tests**
  - Remove OPFS toggle steps from `05-opfs-persistence.spec.ts`
  - Tests should assume OPFS is always active in browser mode
  - Simplify `beforeEach` to only clear OPFS directory
  
- [ ] **TASK-9: Verify All E2E Pass**
  - Run full E2E suite to confirm no regressions

---

## Files to Modify

| File | Action |
|------|--------|
| `sqlite-opfs.service.ts` | Remove feature flag check, keep seeding logic |
| `sqlite.service.ts` | Remove IndexedDB methods, unify to async repos |
| `opfs-migration.service.ts` | DELETE entirely |
| `sqlite-persistence.service.ts` | DELETE entirely |
| `settings.component.ts` | Remove OPFS toggle UI |
| `settings.component.html` | Remove OPFS toggle UI |
| `mode.service.ts` | Simplify - remove persistence preference |
| `repositories.ts` | Keep only base classes needed by async repos |
| `05-opfs-persistence.spec.ts` | Simplify test assumptions |

---

## Verification Criteria

1. `npm run start:browser` works with OPFS by default
2. Asset wizard shows machine definitions (seeding works)
3. Data persists across browser reloads
4. All E2E tests pass
5. No references to IndexedDB in browser mode code path

---

## Execution Order

1. TASK-1 → TASK-7 (unblock the current test failure)
2. TASK-8 → TASK-9 (verify fix)
3. TASK-2 → TASK-6 (cleanup)
