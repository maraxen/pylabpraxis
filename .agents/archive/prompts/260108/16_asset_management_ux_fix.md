# Agent Prompt: 16_asset_management_ux_fix

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed (2026-01-08)
**Batch:** [260108](./README.md)
**Backlog:** [asset_management_ux.md](../../backlog/asset_management_ux.md)

---

## Task

Fix regressions in the Add Machine dialog. User verification on 2026-01-08 confirmed these issues:

1. **Backends in Categories**: Backends (e.g., `HamiltonBackend`) appear in the initial category list. They should only appear in Step 2 after category selection.
2. **Category Toggle Bug**: Cannot deselect a selected category—clicking toggles incorrectly.
3. **Stepper Theme Sync**: Number circles are hardcoded white regardless of light/dark theme. Use Material Design 3 CSS variables.
4. **Redundant Step 2**: Backend selection in Step 2 duplicates Category/Model choice from Step 1. Consolidate or clarify.
5. **Capability Config Forms**: No dynamic capability form renders for liquid handlers with Hamilton backend. The `DynamicCapabilityFormComponent` should trigger.
6. **Advanced JSON Blob**: After expanding "Advanced JSON", the textarea shows an uneditable blob instead of editable JSON text.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [asset_management_ux.md](../../backlog/asset_management_ux.md) | Work item tracking |
| [machine-dialog.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/assets/components/machine-dialog.component.ts) | Main implementation target |
| [dynamic-capability-form.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/assets/components/dynamic-capability-form.component.ts) | Capability form component |

---

## Project Conventions

- **Commands**: Use `uv run` for all Python commands
- **Frontend Build**: `cd praxis/web-client && npx ng build`
- **Frontend Tests**: `cd praxis/web-client && npm test`

See [codestyles/](../../codestyles/) for language-specific guidelines.

---

## On Completion

- [x] Commit changes with descriptive message referencing the backlog item
- [x] Update backlog item status in `asset_management_ux.md`
- [x] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [x] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
- [TECHNICAL_DEBT.md](../../TECHNICAL_DEBT.md) - Known issues
