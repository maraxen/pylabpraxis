# Browser Mode

**Priority**: P1-P2 (Mixed)
**Owner**: Full Stack
**Created**: 2026-01-06 (consolidated from 3 files)
**Status**: Active

---

## Overview

Browser mode allows Praxis to run entirely in the browser using Pyodide and SQLite. This document tracks remaining issues and improvements.

---

## 1. Critical Issues (P1)

### IndexedDB Persistence ✅ COMPLETE

**Status**: ✅ Implemented (2026-01-07 verified)

SQLite database persists across page reloads via `SqliteService.saveToIndexedDB()`.

- [x] Implement IndexedDB persistence for SQLite
- [x] Handle database migration on schema updates
- [x] Add "Clear Data" option in settings (Implemented via SettingsComponent)
- [x] Implement "Export/Import App State" (Implemented via SqliteService + SettingsComponent)

### DB Sync Issue

**Status**: 🔴 Root Cause

Browser `praxis.db` is sometimes out of sync with feature requirements.

- [ ] Investigate root cause of sync issues
- [ ] Implement validation on load
- [ ] Add schema version checking

### SQLite Schema Mismatch (`inferred_requirements_json`) ✅

**Status**: ✅ Complete (2026-01-08)
**Added**: 2026-01-07

**Issue:** `Error fetching simulation data: Error: no such column: inferred_requirements_json` in `SqliteService`. Column missing from browser-mode schema.

**Action:**

- [x] Update `schema.sql` to include `inferred_requirements_json` column
- [x] Implement migration for existing browser databases in `SqliteService`

---

## 2. Schema Synchronization

### Generate Schema Flow

```bash
# 1. Update ORM models
# 2. Regenerate schema and DB
uv run scripts/generate_browser_schema.py
uv run scripts/generate_browser_db.py
```

### Migration Strategy

For existing user databases:

```typescript
// SqliteService.checkAndMigrate()
async checkAndMigrate(): Promise<void> {
  const version = await this.getSchemaVersion();
  if (version < CURRENT_VERSION) {
    await this.runMigrations(version);
  }
}
```

---

## 3. Deployment Modes

| Mode | Backend | Database | Use Case |
|------|---------|----------|----------|
| Browser | Pyodide | SQLite (IndexedDB) | Demo, offline |
| Lite | Python | SQLite | Development |
| Production | Python | PostgreSQL | Production |

### Detection

```typescript
// ModeService
detectMode(): DeploymentMode {
  if (typeof PyodideGlobal !== 'undefined') return 'browser';
  if (this.apiUrl.includes('localhost')) return 'lite';
  return 'production';
}
```

---

## 4. Known Issues Tracking

| Issue | Priority | Status |
|-------|----------|--------|
| ~~IndexedDB persistence~~ | ~~P1~~ | ✅ (Verified via Unit Tests) |
| DB sync issue | P1 | ⏳ (may be resolved) |
| ~~Export/Import App State~~ | ~~P2~~ | ✅ |
| Machine capabilities verification | P2 | ⏳ |
| Frontend Type Safety (Casts) | P3 | ⏳ |

---

---

## 5. Pending Technical Debt

### Browser Mode Schema - UNIQUE Constraint on Asset Name (P2)

**Status**: Pending
**Issue**: `schema.sql` has `CREATE UNIQUE INDEX ix_assets_name` which prevents valid duplicate asset names (names should not be unique, FQNs should).
**Fix**: update `AssetOrm` model, regenerate schema, add migration.

### Machine Definition Schema Linkage (P1)

**Status**: Pending
**Issue**: `machines` table lacks `machine_definition_accession_id` column.
**Fix**: Update backend ORM, generate schema, add migration.

### Schema Generation Scripts Broken (P2)

**Status**: ✅ Fixed (MATCH-FIX)
**Issue**: `generate_browser_schema.py` and `generate_browser_db.py` are failing due to SQLAlchemy metadata initialization issues.
**Fix**: Scripts fixed and schema mismatch resolved (assets table first).

---

## Related Documents

- [TECHNICAL_DEBT.md](../TECHNICAL_DEBT.md) - Source of these items
