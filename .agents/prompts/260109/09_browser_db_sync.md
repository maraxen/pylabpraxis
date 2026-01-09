# Agent Prompt: 09_browser_db_sync

Examine `.agents/README.md` for development context.

**Status:** ✅ Complete  
**Batch:** [260109](./README.md)  
**Backlog:** [browser_mode.md](../../backlog/browser_mode.md)  

---

## Task

Investigate and fix the browser DB sync issue where `praxis.db` is sometimes out of sync with feature requirements. Implement validation on load and schema version checking.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [browser_mode.md](../../backlog/browser_mode.md) | Work item tracking |
| `praxis/web-client/src/app/core/services/sqlite.service.ts` | SQLite service |
| `praxis/web-client/src/assets/data/schema.sql` | Browser schema |

---

## Implementation

1. **Root Cause Investigation**:
   - Identify when DB becomes out of sync
   - Check IndexedDB persistence timing
   - Verify migrations run on schema updates

2. **Validation on Load**:
   - Add schema validation when loading from IndexedDB
   - Check required tables and columns exist
   - Log validation errors for debugging

3. **Schema Version Checking**:
   - Add `PRAGMA user_version` tracking
   - Implement version comparison on load
   - Trigger migration if version mismatch

4. **Migration Framework**:

   ```typescript
   async checkAndMigrate(): Promise<void> {
     const version = await this.getSchemaVersion();
     if (version < CURRENT_VERSION) {
       await this.runMigrations(version);
     }
   }
   ```

---

## Expected Outcome

- DB schema validated on every load
- Automatic migration when schema updates
- Clear error messages for schema mismatches
- No more "column not found" errors

---

## Project Conventions

- **Frontend Tests**: `cd praxis/web-client && npm test`

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
