# Agent Prompt: 02_asset_autoselection_fix

Examine `.agents/README.md` for development context.

**Status:** ✅ Complete  
**Batch:** [260109](./README.md)  
**Backlog:** [run_protocol_workflow.md](../../backlog/run_protocol_workflow.md)  

---

## Task

Fix the "buggy" asset autoselection behavior in the Run Protocol workflow. Users report that autoselection does not reliably pick appropriate resources.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [run_protocol_workflow.md](../../backlog/run_protocol_workflow.md) | Work item tracking |
| [TECHNICAL_DEBT.md](../../TECHNICAL_DEBT.md) | Issue reference |
| `praxis/web-client/src/app/shared/formly-types/asset-selector.component.ts` | Asset selector UI |
| `praxis/web-client/src/app/features/run-protocol/components/parameter-config/` | Parameter configuration |
| `praxis/backend/core/consumable_assignment.py` | Backend assignment logic |

---

## Issues to Address

1. **Current behavior**: Naive selection picks Nth item from filtered list
2. **Improvements needed**:
   - Consider resource `status` (prefer `AVAILABLE_IN_STORAGE` over `IN_USE`)
   - Check remaining capacity for consumables (partial tip racks, plates)
   - Handle case where not enough unique resources exist
   - UI indication when resources must be shared or duplicated

---

## Implementation

1. **Frontend**: Update `asset-selector.component.ts` to implement smart ranking
2. **Backend (Optional)**: Consider `/api/v1/assets/suggest` endpoint with ranked suggestions
3. **Validation**: Add tests for edge cases (no resources, all in use, partial consumables)

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
