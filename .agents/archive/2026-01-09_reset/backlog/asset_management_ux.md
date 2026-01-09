# Asset Management UX Improvements

**Priority**: P2 (High)
**Owner**: Full Stack
**Created**: 2026-01-07 (migrated from TECHNICAL_DEBT.md)
**Updated**: 2026-01-08 (verified regressions)
**Status:** 🟢 Completed (Phase 1 Refactor & Regressions)

---

## Goal

Improve the "Add Machine" and "Add Resource" flows with better UX patterns, and enhance the dashboard metrics display to clearly differentiate physical vs simulated backends.

---

## Phase 1: Add Machine Flow Refactor — ⚠️ REGRESSIONS

> [!CAUTION]
> Items marked complete were verified broken on 2026-01-08.

- [x] ~~Sync stepper theme with application theme~~ ✅ Fixed (2026-01-08)
- [x] ~~Flow: Frontend Category → Backend Selection~~ ✅ Fixed (cleaned up filtering logic)
- [x] Fix category toggle (cannot deselect currently selected category)
- [x] Create proper interface for user-configured capabilities (replace hardcoded JSON)
- [x] ~~Remove redundant Step 2 backend selection~~ ✅ Fixed (Unified Simulated/ChatterBox)

## Phase 2: Add Resource Flow Refactor

- [x] Flow: Category → Model selection
- [x] Use cards for selection (distinct from background chips)
- [x] Include filters in selection view

## Phase 3: Dashboard Metrics Enhancement

- [ ] Fix "Needs Attention" section icon visibility/spacing
- [ ] Differentiate physical vs simulated backends in metrics display
- [ ] Example: "0/0 machines online, 73/73 simulated backends"

---

## Phase 4: Backend Consistency Investigation

- [x] Investigate why 0 backends are listed in "Add Machine" despite 73 simulated loaded. ✅ FIXED
- [x] Enforce singleton pattern for simulated frontends per category to reduce noise (73 is too many). ✅ FIXED

---

## Notes

Migrated from TECHNICAL_DEBT.md items #8 (Enhanced Asset Management & Metrics) and #9 ("Add Machine" & "Add Resource" Flow Refactor).

**2026-01-08**: Phase 1 regressions resolved:

- Stepper theme sync fixed (using Material Design 3 variables)
- Filtered backends correctly in category view
- Capability config forms trigger correctly for Hamilton backends
- JSON blob display is now editable text

---

## References

- [TECHNICAL_DEBT.md](../TECHNICAL_DEBT.md) - Original source
- [DEVELOPMENT_MATRIX.md](../DEVELOPMENT_MATRIX.md)
