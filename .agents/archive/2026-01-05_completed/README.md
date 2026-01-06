# Archive: 2026-01-05 Completed Items

**Archived**: 2026-01-05
**Reason**: Items completed or superseded by new architecture

---

## Completed Items

### State Snapshot Tracing → Protocol Simulation (Complete)

The original `state_snapshot_tracing.md` has been fully implemented as the hierarchical protocol simulation system:

- **Backend**: Phases 0-7 complete (87 tests passing)
- **Files**: `praxis/backend/core/simulation/`
- **Features**:
  - Tracer execution, PLR method contracts (40+)
  - State-aware tracers, hierarchical pipeline
  - Bounds analyzer, failure mode detector
  - Cloudpickle + graph replay for browser mode

**Successor**: [simulation_ui_integration.md](../backlog/simulation_ui_integration.md) - Phase 8 UI integration

### Visual Well Selection (Complete)

Fully implemented:

- `IndexSelectorComponent` with grid-based selection
- `LinkedSelectorService` for synchronized arguments
- Backend type inference for Well/TipSpot parameters
- Formly integration with protocol metadata

### Tutorial & Demo Mode (Superseded)

The original tutorial system has been implemented but the demo mode toggle is being superseded:

- **Tutorial**: Shepherd.js with 11 steps - still in use
- **Demo Mode Toggle**: Being replaced by "Browser Mode Defaults" architecture
- **Successor**: [browser_mode_defaults.md](../backlog/browser_mode_defaults.md)

The new approach eliminates the separate demo mode - browser mode IS the demo experience with:

- 1 instance of every resource/machine (simulated)
- Infinite consumables (configurable)
- No toggle needed

---

## Files in This Archive

- `state_snapshot_tracing_completed.md` - Original backlog, now complete
- `visual_well_selection_completed.md` - Original backlog, now complete
- `tutorial_demo_mode_superseded.md` - Tutorial still active, demo toggle superseded

---

## Reference

- [DEVELOPMENT_MATRIX.md](../DEVELOPMENT_MATRIX.md) - Current priorities
- [ROADMAP.md](../ROADMAP.md) - Overall roadmap
