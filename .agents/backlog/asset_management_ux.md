# Asset Management UX Improvements

**Priority**: P2 (High)
**Owner**: Full Stack
**Created**: 2026-01-07 (migrated from TECHNICAL_DEBT.md)
**Status**: 🟢 Planned

---

## Goal

Improve the "Add Machine" and "Add Resource" flows with better UX patterns, and enhance the dashboard metrics display to clearly differentiate physical vs simulated backends.

---

## Phase 1: Add Machine Flow Refactor

- [ ] Sync stepper theme with application theme
- [ ] Flow: Frontend Category → Backend Selection (hide backends in category view)
- [ ] Remove redundant Step 2
- [ ] Create proper interface for user-configured capabilities (replace hardcoded JSON)

## Phase 2: Add Resource Flow Refactor

- [ ] Flow: Category → Model selection
- [ ] Use cards for selection (distinct from background chips)
- [ ] Include filters in selection view

## Phase 3: Dashboard Metrics Enhancement

- [ ] Fix "Needs Attention" section icon visibility/spacing
- [ ] Differentiate physical vs simulated backends in metrics display
- [ ] Example: "0/0 machines online, 73/73 simulated backends"

---

## Notes

Migrated from TECHNICAL_DEBT.md items #8 (Enhanced Asset Management & Metrics) and #9 ("Add Machine" & "Add Resource" Flow Refactor).

---

## References

- [TECHNICAL_DEBT.md](../TECHNICAL_DEBT.md) - Original source
- [DEVELOPMENT_MATRIX.md](../DEVELOPMENT_MATRIX.md)
