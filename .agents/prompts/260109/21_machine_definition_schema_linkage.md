# Agent Prompt: 21_machine_definition_schema_linkage

Examine `.agents/README.md` for development context.

**Status:** ✅ Complete  
**Batch:** [260109](./README.md)  
**Backlog:** [browser_mode.md](../../backlog/browser_mode.md)  

---

## Task

Add missing `machine_definition_accession_id` column to the `machines` table in browser mode schema.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [browser_mode.md](../../backlog/browser_mode.md) | Work item tracking (Section 5) |
| `praxis/web-client/src/assets/data/schema.sql` | Browser schema |
| `praxis/backend/models/orm/assets.py` | Asset ORM model |

---

## Current Issue

The `machines` table lacks `machine_definition_accession_id` column which links machines to their type definitions.

---

## Implementation

1. **Update Backend ORM (if needed)**:
   - Verify `machine_definition_accession_id` exists in `MachineOrm`
   - Add if missing

2. **Regenerate Schema**:

   ```bash
   uv run scripts/generate_browser_schema.py
   ```

3. **Add Migration**:

   ```sql
   ALTER TABLE machines ADD COLUMN machine_definition_accession_id TEXT;
   ```

4. **Frontend Service Update**:
   - Ensure `SqliteService` populates this field
   - Link new machines to their definitions

---

## Expected Outcome

- Machines correctly linked to type definitions
- Schema in sync between backend and browser mode
- Existing databases migrated

---

## Project Conventions

- **Commands**: Use `uv run` for all Python commands

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
