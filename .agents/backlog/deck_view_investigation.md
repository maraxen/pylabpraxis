# Deck View Consistency Investigation

**Priority**: P2 (High)
**Owner**: Frontend
**Created**: 2026-01-08
**Status**: ✅ Complete (2026-01-09)

---

## Issue Description

The Deck View in the Workcell/Run Protocol setup was using hardcoded mock data.

**Findings**:

1. **VisualizerComponent** used `createDemoDeck()` mock data exclusively.
2. **DeckGeneratorService** ignored the machine object except for basic type detection, falling back to hardcoded Hamilton/OT-2 layouts.
3. Logic was unified by making both components prioritize `machine.plr_state` or `machine.plr_definition`.

---

## Investigation Tasks

- [x] **Code Audit**: ✅ Complete
  - Audit `DeckViewComponent` usage in "Run Protocol" and "Workcell" views.
  - Identify data sources for deck definitions (Found `createDemoDeck` and `DeckGeneratorService`).
  - Check for hardcoded mock data (Confirmed for both).

- [x] **Collision & Placement Logic**: ✅ Complete
  - Investigate how carrier placement is determined (Confirmed hardcoded in `generateHamiltonDeck`).

- [x] **Component Unification**: ✅ Complete
  - Refactor `DeckGeneratorService` to prioritize machine definitions.
  - Refactor `VisualizerComponent` to inject `AssetService` and fetch real machines.

- [x] **PLR Integration**: ✅ Complete
  - Verify if dimensions and coordinates are coming accurately from PLR type definitions (Verified via `MachineDetailsDialogComponent` pattern).

---

## Resolution

Implemented machine-definition priority in `DeckGeneratorService` and connected `VisualizerComponent` to real machine data. Verified with unit tests and build checks.

---

## References

- [run_protocol_workflow.md](./run_protocol_workflow.md) - Related workflow
