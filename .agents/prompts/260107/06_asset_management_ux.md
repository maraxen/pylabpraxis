# Agent Prompt: 06_asset_management_ux

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Batch:** [260107](./README.md)
**Backlog:** [asset_management_ux.md](../../backlog/asset_management_ux.md)

---

## Task

Refactor the "Add Machine" and "Add Resource" flows for improved UX, including theme synchronization, clearer step progression, and card-based selection.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [asset_management_ux.md](../../backlog/asset_management_ux.md) | Work item tracking |
| [add-machine/](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/assets/components/add-machine/) | Add Machine components |
| [add-resource/](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/assets/components/add-resource/) | Add Resource components |
| [assets.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/assets/assets.component.ts) | Asset management root |

---

## Implementation Details

### Phase 1: Add Machine Flow Refactor

1. **Sync stepper theme** with application dark/light mode
2. **Simplify flow**: Frontend Category → Backend Selection
   - Hide backends in category view (show only after category selected)
3. **Remove redundant Step 2** if applicable
4. **Create capabilities interface** (replace hardcoded JSON)

### Phase 2: Add Resource Flow Refactor

1. **Flow**: Category → Model selection
2. **Use cards** for selection (distinct from background chips)
3. **Include filters** in selection view

### Phase 3: Dashboard Metrics Enhancement

1. **Fix "Needs Attention"** section icon visibility/spacing
2. **Differentiate physical vs simulated** backends in metrics
   - Example: "0/0 machines online, 73/73 simulated backends"

---

## Design Guidelines

- Use consistent card patterns from Asset Registry
- Ensure responsive design (tablet-friendly)
- Follow Material Design stepper guidelines

---

## Project Conventions

- **Frontend Dev**: `cd praxis/web-client && npm start`
- **Frontend Tests**: `cd praxis/web-client && npm test`

See [codestyles/typescript.md](../../codestyles/typescript.md) for guidelines.

---

## On Completion

- [ ] Add Machine flow uses themed stepper
- [ ] Add Resource uses card-based selection
- [ ] Dashboard shows physical vs simulated counts
- [ ] Update [asset_management_ux.md](../../backlog/asset_management_ux.md)
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md) "Asset Management UX"
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md)
- [TECHNICAL_DEBT.md](../../TECHNICAL_DEBT.md) - Original source items #8, #9
