# Agent Prompt: 01_schema_mismatch_fix

Examine `.agents/README.md` for development context.

**Status:** ✅ Complete  
**Completed:** 2026-01-07  
**Batch:** [260108](./README.md)  
**Backlog:** [browser_mode.md](../../backlog/browser_mode.md)  
**Priority:** CRITICAL (Resolved)

---

## Task

Fix the SQLite schema mismatch for `inferred_requirements_json` column that causes browser mode simulation data fetching to fail.

**Error:** `Error fetching simulation data: Error: no such column: inferred_requirements_json`

---

## Implementation Steps

### 1. Update Browser Schema

In `praxis/web-client/src/assets/browser-db/schema.sql`:

- Add `inferred_requirements_json TEXT` column to the appropriate table (likely `function_protocol_definitions` or `simulation_results`)

### 2. Add SqliteService Migration

In `praxis/web-client/src/app/core/services/sqlite.service.ts`:

- Increment schema version
- Add migration logic in `checkAndMigrate()` to add the column for existing databases:

  ```sql
  ALTER TABLE [table_name] ADD COLUMN inferred_requirements_json TEXT;
  ```

### 3. Regenerate Browser DB

```bash
uv run scripts/generate_browser_schema.py
uv run scripts/generate_browser_db.py
```

### 4. Verify

- Clear browser IndexedDB
- Reload application
- Navigate to protocol with simulation data
- Confirm no column errors in console

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [browser_mode.md](../../backlog/browser_mode.md) | Backlog tracking |
| [TECHNICAL_DEBT.md](../../TECHNICAL_DEBT.md) | Issue documentation |
| [schema.sql](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/assets/browser-db/schema.sql) | Browser DB schema |
| [sqlite.service.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/core/services/sqlite.service.ts) | Migration logic |
| [generate_browser_schema.py](file:///Users/mar/Projects/pylabpraxis/scripts/generate_browser_schema.py) | Schema generation |

---

## Project Conventions

- **Commands**: Use `uv run` for all Python commands
- **Frontend Tests**: `cd praxis/web-client && npm test`

---

## On Completion

- [x] Update [TECHNICAL_DEBT.md](../../TECHNICAL_DEBT.md) - mark item resolved
- [x] Update [browser_mode.md](../../backlog/browser_mode.md)
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [x] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
