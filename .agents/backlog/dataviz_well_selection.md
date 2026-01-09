# Dataviz & Well Selection Bridging

**Priority**: P2 (High)
**Owner**: Full Stack
**Created**: 2026-01-07 (migrated from TECHNICAL_DEBT.md)
**Status**: 🟢 Planned

---

## Goal

Bridge the `WellDataOutput` ORM with frontend Dataviz components, enable user-configured visualizations, and unify the well selection pattern across protocols and dataviz.

---

## Phase 1: Backend Integration

- [ ] Design API endpoints for visualization configuration persistence
- [ ] Leverage existing `WellDataOutput` ORM for data retrieval
- [ ] Create Pydantic models for visualization configurations

## Phase 2: Frontend Visualization

- [x] Refactor `WellSelectorComponent` to use `@angular/aria/grid`:
  - [x] ARIA-compliant grid pattern
  - [x] Click-and-drag selection support
  - [x] Individual cell clicking
  - [x] "Clear Selection" and "Invert Selection" buttons
  - [x] Selection animation rendering
- [ ] Share refactored component with protocol selection
- [ ] Enable user-configurable visualization settings
- [ ] Use rich selection screen pattern (consistent with protocols)

## Phase 3: Data Visualization Enhancement

- [ ] Implement visualization preview for `WellDataOutput` data
- [ ] Add chart type selection (heatmap, scatter, etc.)
- [ ] Enable export of visualization configurations

---

## Notes

Migrated from TECHNICAL_DEBT.md item #10 (Dataviz & Well Selection Bridging). This leverages the existing `WellDataOutput` ORM infrastructure.

---

## References

- [TECHNICAL_DEBT.md](../TECHNICAL_DEBT.md) - Original source
- [visual_well_selection.md](./visual_well_selection.md) - Related existing backlog
- [DEVELOPMENT_MATRIX.md](../DEVELOPMENT_MATRIX.md)
