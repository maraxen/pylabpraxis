# Agent Prompt: 21_playground_enhancements

Examine `.agents/README.md` for development context.

**Status:** 🟡 In Progress
**Batch:** [260108](./README.md)
**Backlog:** [repl_enhancements.md](../../backlog/repl_enhancements.md)
**Priority:** P2

---

## Task

Rename "REPL" to "Playground" across the application and implement a new guided inventory dialog.

### Phase 1: Rename REPL to Playground

1. **Update UI**: Rename sidebar item, page headers, and button tooltips.
2. **Update Routing**: Change route from `/repl` to `/playground` (setup redirect if needed).
3. **Update Documentation**: Rename mentions in user-facing text.
4. **Update UI**: Rename sidebar item, page headers, and button tooltips.
5. **Update Routing**: Change route from `/repl` to `/playground` (setup redirect if needed).
6. **Update Documentation**: Rename mentions in user-facing text.
7. **Codebase**: Rename components and variables where appropriate (e.g., `ReplComponent` -> `PlaygroundComponent`), but keep `repl` in variable names if referring strictly to the Jupyter kernel connection.

### Phase 2: Inventory Dialog Implementation

> **Status:** ✅ Complete

Create a new `InventoryDialogComponent` that guides the user through adding assets to the playground.

**Workflow**:

1. **Asset Type**: Select "Machine" or "Resource" (Card-based selection).
2. **Category**: Filter by category (Liquid Handler, Plate Reader, etc.).
3. **Selection**:
   - If Machine: Select Backend (Simulated, ChatterBox, etc.).
   - If Resource: Select specific model.
4. **Specifications**:
   - **Custom Variable Name**: Input field for the variable name to be used in Python.
   - **Count**: Number of instances to add (for resources).
5. **Action**: "Add to List" button (allows adding multiple items before closing).

**Technical Requirements**:

- Use `MatDialog` or similar overlay.
- Use `MatStepper` or a custom step-based flow.
- Ensure "Add to List" caches the selection but keeps the dialog open for more additions.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [repl_enhancements.md](../../backlog/repl_enhancements.md) | Backlog tracking |
| [repl-layout.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/repl/components/repl-layout/) | Current REPL layout |

---

## Project Conventions

- **Frontend Build**: `cd praxis/web-client && npx ng build`
- **Frontend Tests**: `cd praxis/web-client && npm test`

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update [repl_enhancements.md](../../backlog/repl_enhancements.md)
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
