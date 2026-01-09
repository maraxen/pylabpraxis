# Deck View Consistency Investigation

**Priority**: P2 (High)
**Owner**: Frontend
**Created**: 2026-01-08
**Status**: 🟢 Planned

---

## Issue Description

The Deck View in the Workcell/Run Protocol setup is always the same hardcoded layout (plate, tip, trough), regardless of the actual machine definition or protocol requirements.

**Questions to Answer**:

1. Is the layout hardcoded?
2. Why are there always plate, tip, trough items?
3. What is the logic for placing carriers (how do we avoid collisions when guiding users in setup)?
4. Are we using PyLabRobot (PLR) dimensions?
5. Are workcell view decks using the same `deck-view` component as the standalone view, rendering from the database?

---

## Investigation Tasks

- [ ] **Code Audit**:
  - Audit `DeckViewComponent` usage in "Run Protocol" and "Workcell" views.
  - Identify data sources for deck definitions in these contexts.
  - Check for hardcoded mock data or fallback logic.

- [ ] **Collision & Placement Logic**:
  - Investigate how carrier placement is determined.
  - Check if collision detection logic exists or if we rely on PLR.

- [ ] **Component Unification**:
  - Determine if a single `DeckViewComponent` can verify all use cases (Standalone, Run Protocol, Workcell).
  - Plan refactor to unify if currently divergent.

- [ ] **PLR Integration**:
  - Verify if dimensions and coordinates are coming accurately from PLR type definitions.

---

## References

- [run_protocol_workflow.md](./run_protocol_workflow.md) - Related workflow
