# Agent Prompt: 08_asset_management_ux

Examine `.agents/README.md` for development context.

**Status:** ✅ Complete  
**Batch:** [260108](./README.md)  
**Backlog:** [asset_management_ux.md](../../backlog/asset_management_ux.md)  
**Priority:** P2

---

## Task

Refactor the "Add Machine" and "Add Resource" flows with improved UX patterns. Focus on Phase 1 (Add Machine) or Phase 2 (Add Resource) based on current priority.

---

## Implementation Steps

### Phase 1: Add Machine Flow Refactor

1. **Theme Sync**: Ensure stepper component uses application theme variables ✅
2. **Simplify Flow**:
   - Step 1: Frontend Category selection (hide backend details) ✅
   - Step 2: Backend Selection (after category is chosen) ✅
   - Remove redundant steps ✅
3. **Capabilities Interface**: Replace hardcoded JSON with proper UI for capability configuration ✅

### Phase 2: Add Resource Flow Refactor

1. **Flow**: Category → Model selection ✅
2. **Cards for Selection**: Use distinct card components (not background chips) ✅
3. **Include Filters**: Add filter chips in selection view ✅

### Visual Requirements

- Cards should have clear boundaries (themed gradients/outlines)
- Match existing Asset Management card patterns

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [asset_management_ux.md](../../backlog/asset_management_ux.md) | Backlog tracking |
| [add-machine-dialog/](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/assets/components/add-machine-dialog/) | Machine dialog component |
| [add-resource-dialog/](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/assets/components/add-resource-dialog/) | Resource dialog component |

---

## Project Conventions

- **Frontend Tests**: `cd praxis/web-client && npm test`

See [codestyles/typescript.md](../../codestyles/typescript.md) and [html-css.md](../../codestyles/html-css.md) for conventions.

---

## On Completion

- [ ] Commit changes with message: `feat(assets): refactor add machine/resource dialog flow`
- [x] Update [asset_management_ux.md](../../backlog/asset_management_ux.md) - mark completed phase
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
