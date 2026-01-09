# Agent Prompt: 20_browser_schema_unique_constraint

Examine `.agents/README.md` for development context.

**Status:** ✅ Complete  
**Batch:** [260109](./README.md)  
**Backlog:** [browser_mode.md](../../backlog/browser_mode.md)  

---

## Task

Fix the UNIQUE constraint on Asset Name in browser mode schema. Names should not be unique - FQNs should be.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [browser_mode.md](../../backlog/browser_mode.md) | Work item tracking (Section 5) |
| `praxis/web-client/src/assets/data/schema.sql` | Browser schema |
| `praxis/backend/models/orm/assets.py` | Asset ORM model |
| `scripts/generate_browser_schema.py` | Schema generation |

---

## Current Issue

```sql
-- Current (incorrect)
CREATE UNIQUE INDEX ix_assets_name ON assets(name);
```

This prevents valid duplicate asset names (e.g., two "Tip Rack 1" resources).

---

## Implementation

1. **Update ORM Model**:
   - Remove unique constraint from `name` field
   - Ensure `fqn` field remains unique

2. **Regenerate Schema**:

   ```bash
   uv run scripts/generate_browser_schema.py
   ```

3. **Add Migration**:
   - Existing browser DBs need index dropped
   - Add migration in `SqliteService.checkAndMigrate()`

4. **Test**:
   - Verify multiple assets with same name can be created
   - Verify FQN uniqueness enforced

---

## Expected Outcome

- Multiple assets with identical names allowed
- FQN uniqueness constraint remains
- Migration path for existing databases

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
