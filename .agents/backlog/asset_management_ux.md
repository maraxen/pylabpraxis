# Asset Management UX Improvements

**Priority**: P2 (High)
**Owner**: Full Stack
**Created**: 2026-01-07 (migrated from TECHNICAL_DEBT.md)
**Updated**: 2026-01-08 (verified regressions)
**Status**: 🟡 In Progress (Regressions identified)

---

## Goal

Improve the "Add Machine" and "Add Resource" flows with better UX patterns, and enhance the dashboard metrics display to clearly differentiate physical vs simulated backends.

---

## Phase 1: Add Machine Flow Refactor — ⚠️ REGRESSIONS

> [!CAUTION]
> Items marked complete were verified broken on 2026-01-08.

- [ ] ~~Sync stepper theme with application theme~~ → **BROKEN**: Number circles hardcoded white (same in light/dark)
- [ ] ~~Flow: Frontend Category → Backend Selection (hide backends in category view)~~ → **BROKEN**: Backends still listed in categories
- [ ] Fix category toggle (cannot deselect currently selected category)
- [ ] ~~Create proper interface for user-configured capabilities (replace hardcoded JSON)~~ → **BROKEN**: No capability config for liquid handlers; Advanced JSON shows uneditable blob
- [ ] Remove redundant Step 2 backend selection (duplicates Category/Model choice)

## Phase 2: Add Resource Flow Refactor

- [x] Flow: Category → Model selection
- [x] Use cards for selection (distinct from background chips)
- [x] Include filters in selection view

## Phase 3: Dashboard Metrics Enhancement

- [ ] Fix "Needs Attention" section icon visibility/spacing
- [ ] Differentiate physical vs simulated backends in metrics display
- [ ] Example: "0/0 machines online, 73/73 simulated backends"

---

## Notes

Migrated from TECHNICAL_DEBT.md items #8 (Enhanced Asset Management & Metrics) and #9 ("Add Machine" & "Add Resource" Flow Refactor).

**2026-01-08**: User verification revealed Phase 1 items are NOT complete. Issues:

- Stepper theme sync is broken (hardcoded colors)
- Backends appear in category view
- Capability config forms never trigger
- JSON blob display is uneditable

---

## References

- [TECHNICAL_DEBT.md](../TECHNICAL_DEBT.md) - Original source
- [DEVELOPMENT_MATRIX.md](../DEVELOPMENT_MATRIX.md)
