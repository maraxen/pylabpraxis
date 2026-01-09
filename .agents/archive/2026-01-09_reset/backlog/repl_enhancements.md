# REPL Enhancements

**Priority**: P2 (High)
**Owner**: Frontend
**Created**: 2026-01-07 (migrated from TECHNICAL_DEBT.md)
**Status**: 🟡 In Progress

---

## Goal

Improve JupyterLite REPL stability, theme synchronization, and hardware discovery integration.

---

## Phase 1: Rendering Stability

- [x] Fix REPL not rendering until "Refresh Kernel" button is pressed
- [x] Investigate race condition in iframe loading vs kernel initialization
- [x] Ensure `praxis_repl` BroadcastChannel communication is robust at startup

## Phase 2: Theme Synchronization

- [x] Implement JupyterLite theme sync (match app dark/light mode) ✅ FIXED
- [x] Inject CSS variables from main app into JupyterLite iframe ✅ FIXED

## Phase 3: Hardware Discovery Integration

- [ ] Add "Instantiate in REPL" button for discovered hardware
- [ ] Generate machine instantiation code from discovery results

## Phase 4: Shim Loading Cleanup (Medium Priority)

- [ ] Refactor browser shim injection (currently uses exec() of fetched Python)
- [ ] Consider dedicated PLR browser adapter package
- [ ] Replace raw string templating with cleaner initialization

## Phase 5: Known Issues & Future Improvements

- [x] **404 Errors for PyLabRobot Paths**: Suppress harmless 404s for virtual filesystem imports (configure `jupyter-lite.json`).
- [x] **Slow Initial Load**: Explore pre-bundling or eager loading to reduce startup time/race conditions.

## Phase 6: Playground Transformation & Inventory Dialog

- [ ] **Rename REPL to Playground**:
  - Update all UI labels, route paths, and documentation from "REPL" to "Playground".
  - Retain "REPL" only where technically accurate (e.g., the underlying kernel interaction).

- [x] **New Inventory Dialog**: ✅ REDESIGNED
  - Redesigned with a tabbed interface ("Quick Add", "Browse & Add", "Current Items").
  - **Features**:
    - Quick Add: Autocomplete search + filter accordion.
    - Browse: Polished 4-step stepper with icons and indicators.
    - Current Items: Dedicated management tab with editable variable names and item count badge.

---

## Notes

Migrated from TECHNICAL_DEBT.md items #5 (JupyterLite Rendering) and #11 (REPL Integration Issues). Phase 4 addresses the "REPL Shim Loading Clean-up" debt item.

---

## References

- [TECHNICAL_DEBT.md](../TECHNICAL_DEBT.md) - Original source
- [archive/2026-01-06_completed/repl_jupyterlite.md](../archive/2026-01-06_completed/repl_jupyterlite.md) - Completed core work
- [DEVELOPMENT_MATRIX.md](../DEVELOPMENT_MATRIX.md)
