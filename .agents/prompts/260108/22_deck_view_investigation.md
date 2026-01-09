# Agent Prompt: 22_deck_view_investigation

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Batch:** [260108](./README.md)
**Backlog:** [deck_view_investigation.md](../../backlog/deck_view_investigation.md)
**Priority:** P2

---

## Task

Investigate why the "Workcell" and "Run Protocol" deck views always render a generic static layout (plate, tip, trough) instead of the actual machine definition.

### Investigation Steps

1. **Audit Component Usage**:
   - Locate where `deck-view` (or similar component) is used in `RunProtocolComponent` and related children.
   - Check the inputs passed to the component. Are they hardcoded mock data?

2. **Trace Data Source**:
   - Follow the `machine` or `deck` data from the parent component down to the view.
   - Check if `DeckGeneratorService` is being used correctly to generate the deck state from the PLR definition.

3. **Analyze Carrier Placement Logic**:
   - Determine how carriers are currently placed. Is there collision detection?
   - If hardcoded, document where this logic resides.

4. **Compare with Standalone View**:
   - Compare implementation with the working `DeckViewComponent` (used in Assets/Monitor).
   - Identify discrepancies in rendering logic.

### Output

- Create a report in `deck_view_investigation.md` (or update the backlog item) with findings.
- Propose a fix or refactor plan to unify the deck views.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [deck_view_investigation.md](../../backlog/deck_view_investigation.md) | Backlog tracking |
| [run-protocol.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/run-protocol/) | Protocol run flow |

---

## Project Conventions

- **Frontend Build**: `cd praxis/web-client && npx ng build`

---

## On Completion

- [ ] Update [deck_view_investigation.md](../../backlog/deck_view_investigation.md) with findings
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
