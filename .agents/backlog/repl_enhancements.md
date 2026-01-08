# REPL Enhancements

**Priority**: P2 (High)
**Owner**: Frontend
**Created**: 2026-01-07 (migrated from TECHNICAL_DEBT.md)
**Status**: 🟢 Planned

---

## Goal

Improve JupyterLite REPL stability, theme synchronization, and hardware discovery integration.

---

## Phase 1: Rendering Stability

## Phase 1: Rendering Stability

- [x] Fix REPL not rendering until "Refresh Kernel" button is pressed
- [x] Investigate race condition in iframe loading vs kernel initialization
- [x] Ensure `praxis_repl` BroadcastChannel communication is robust at startup

## Phase 2: Theme Synchronization

- [ ] Implement JupyterLite theme sync (match app dark/light mode)
- [ ] Inject CSS variables from main app into JupyterLite iframe

## Phase 3: Hardware Discovery Integration

- [ ] Add "Instantiate in REPL" button for discovered hardware
- [ ] Generate machine instantiation code from discovery results

## Phase 4: Shim Loading Cleanup (Medium Priority)

- [ ] Refactor browser shim injection (currently uses exec() of fetched Python)
- [ ] Consider dedicated PLR browser adapter package
- [ ] Replace raw string templating with cleaner initialization

## Phase 5: Known Issues & Future Improvements

- [ ] **404 Errors for PyLabRobot Paths**: Suppress harmless 404s for virtual filesystem imports (configure `jupyter-lite.json`).
- [ ] **Slow Initial Load**: Explore pre-bundling or eager loading to reduce startup time/race conditions.

---

## Notes

Migrated from TECHNICAL_DEBT.md items #5 (JupyterLite Rendering) and #11 (REPL Integration Issues). Phase 4 addresses the "REPL Shim Loading Clean-up" debt item.

---

## References

- [TECHNICAL_DEBT.md](../TECHNICAL_DEBT.md) - Original source
- [archive/2026-01-06_completed/repl_jupyterlite.md](../archive/2026-01-06_completed/repl_jupyterlite.md) - Completed core work
- [DEVELOPMENT_MATRIX.md](../DEVELOPMENT_MATRIX.md)
