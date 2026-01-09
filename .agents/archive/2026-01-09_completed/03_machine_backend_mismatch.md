# Agent Prompt: 03_machine_backend_mismatch

Examine `.agents/README.md` for development context.

**Status:** ✅ Complete  
**Batch:** [260109](./README.md)  
**Backlog:** [asset_management_ux.md](../../backlog/asset_management_ux.md)  

---

## Task

Fix the machine backend mismatch where "Add Machine" dialog lists 0 backends but logs show 73 simulated backends loaded. Likely caused by excessive simulated frontends per category.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [asset_management_ux.md](../../backlog/asset_management_ux.md) | Work item tracking |
| [TECHNICAL_DEBT.md](../../TECHNICAL_DEBT.md) | Issue reference |
| `praxis/backend/services/machine_type_definition.py` | Machine type service |
| `praxis/web-client/src/app/features/assets/dialogs/add-machine-dialog/` | Add Machine dialog |

---

## Investigation Steps

1. **Verify Backend Loading**:
   - Confirm 73 backends are loaded in console
   - Trace where backends are filtered before display

2. **Category-Backend Association**:
   - Check if simulated backends are correctly categorized
   - Verify frontend-backend matching logic

3. **Singleton Pattern**:
   - Investigate if multiple simulated frontends per category causes issues
   - Implement singleton pattern for simulated frontends if needed

4. **DB vs Processing**:
   - Determine if issue is in database storage or UI processing

---

## Expected Outcome

- "Add Machine" dialog shows appropriate backends after category selection
- No duplicate simulated frontends per category
- Clean console logs without backend loading errors

---

## Project Conventions

- **Commands**: Use `uv run` for all Python commands
- **Backend Tests**: `uv run pytest tests/ -v`
- **Frontend Tests**: `cd praxis/web-client && npm test`

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
