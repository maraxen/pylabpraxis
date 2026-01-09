# Praxis Development Roadmap

**Last Updated**: 2026-01-08 (Backlog Archiving)
**Current Phase**: Feature Development & Quality Assurance

---

## Executive Summary

The backend simulation infrastructure is **complete** (87 tests passing). Focus now shifts to:

1. **Simulation UI Integration** - Surface cached simulation results in the UI (mostly complete)
2. **Browser Mode Defaults** - ✅ Complete (archived 2026-01-06)
3. **Error Handling & State Resolution** - ✅ Complete (archived 2026-01-06)
4. **JupyterLite REPL** - ✅ Core complete (archived 2026-01-06)
5. **Chip-Based Filter Standardization** - Unified filter UX across all surfaces
6. **Quality Assurance** - ✅ SqliteService Unit Tests complete, Playwright E2E pending.

---

## Priority 1: Critical - Architecture & Core Issues

**Goal**: Resolve foundational architecture issues

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **PLR Frontend/Backend Schema** | ✅ Done | Add `frontend_fqn` to machine definitions | [TECHNICAL_DEBT.md](./TECHNICAL_DEBT.md) |
| **Serial/USB Driver Generalization** | ✅ Done | Generalize CLARIOstar pattern to all serial devices | [hardware_connectivity.md](./backlog/hardware_connectivity.md) |
| ~~Restore Asset Selection Step~~ | ✅ Done | Asset selection step verified in code | [run_protocol_workflow.md](./backlog/run_protocol_workflow.md) |
| ~~IndexedDB Persistence~~ | ✅ Done | `SqliteService.saveToIndexedDB()` implemented | [browser_mode.md](./backlog/browser_mode.md) |

---

## Priority 2: High - Simulation UI Integration (Phase 8)

**Goal**: Surface simulation results to users in the UI

**Backend Status**: ✅ Complete (Phases 0-7)

- Tracer Execution, PLR Method Contracts (40+), State-Aware Tracers
- Hierarchical Simulation Pipeline, Bounds Analyzer, Failure Mode Detector
- Integration & Caching, Cloudpickle + Graph Replay
- **87 tests passing**

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **Protocol Warnings** | ✅ Done | Show failure mode warnings in protocol selection | [simulation_ui_integration.md](./archive/2026-01-07_completed/simulation_ui_integration.md) |
| **Deck Setup Requirements** | ✅ Done | Surface requirements in deck setup wizard | [simulation_ui_integration.md](./archive/2026-01-07_completed/simulation_ui_integration.md) |
| **State Delta Display (8.4)** | ✅ Done | Show state at each operation in Execution Monitor | [simulation_ui_integration.md](./archive/2026-01-07_completed/simulation_ui_integration.md) |
| **Time Travel Debugging** | ✅ Done | Inspect state at any operation step | [simulation_ui_integration.md](./archive/2026-01-07_completed/simulation_ui_integration.md) |
| **State History Timeline** | ✅ Done | Visual timeline of state changes | [simulation_ui_integration.md](./archive/2026-01-07_completed/simulation_ui_integration.md) |

---

## Priority 2: High - Browser Mode Defaults & Demo Elimination ✅ COMPLETE

**Goal**: Make browser mode the primary experience with sensible defaults

> ✅ **ARCHIVED** - All items completed 2026-01-06. See `archive/2026-01-06_completed/browser_mode_defaults.md`

---

## Priority 2: High - Chip-Based Filter Standardization ✅ COMPLETE

**Goal**: Unified chip-based filter UX across all surfaces

> ✅ **ARCHIVED** - All items completed 2026-01-08. See `archive/2026-01-08_completed/chip_filter_standardization.md`

| Item | Status | Description |
|------|--------|-------------|
| **Core Filter Chip Component** | ✅ Done | Reusable chip with active/inactive/disabled states |
| **Resource Filter Chips** | ✅ Done | Integrated Categories, Brands, Status |
| **Machine Filter Chips** | ✅ Done | Category, Simulated, Status, Backend |
| **Disabled Chip UX** | ✅ Done | Shake animation + message on disabled click |
| **Unique Name Parsing** | ✅ Done | Extract distinguishing name parts |
| **Chip Filter Overflow** | ✅ Done | flex-wrap + collapse >5 into dropdown |

---

## Priority 2: High - JupyterLite REPL ✅ COMPLETE

**Goal**: Complete JupyterLite migration with search and filters

> ✅ **ARCHIVED** - Core integration complete 2026-01-06. See `archive/2026-01-06_completed/repl_jupyterlite.md`
> Asset Preloading remains as future enhancement.

---

## Priority 2: Code Quality & Testing

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **Code Quality Audit** | ✅ Partial | 12 fixed (Ruff) + `crud_base.py` | [quality_assurance.md](./backlog/quality_assurance.md) |
| **E2E Test Suite** | ⏳ Todo | Critical flow coverage with Playwright | [quality_assurance.md](./backlog/quality_assurance.md) |
| **Unit Test Coverage** | ✅ Done | SqliteService persistence and lifecycle tests | [quality_assurance.md](./backlog/quality_assurance.md) |
| **Final Visual QA** | ⏳ Todo | Automated + manual review | [quality_assurance.md](./backlog/quality_assurance.md) |

---

## Priority 2: Other Items

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **Export/Import App State** | ✅ Done | Backup/Restore browser database | [browser_mode.md](./backlog/browser_mode.md) |
| **Search Icon Centering** | ✅ Done | CSS fix for search input alignment | [chip_filter_standardization.md](./backlog/chip_filter_standardization.md) |
| **Chip Filter Overflow** | ✅ Done | Flex-wrap and collapse chips (>5) | [chip_filter_standardization.md](./backlog/chip_filter_standardization.md) |
| **Capability Dropdown Theme** | ✅ Done | Fix light-theme capability menu in dark mode | [chip_filter_standardization.md](./backlog/chip_filter_standardization.md) |
| **Machine Capabilities Verification** | ⏳ Todo | Hamilton Starlet 96-head/iSwap verification | [browser_mode_issues.md](./backlog/browser_mode_issues.md) |
| **Serial Driver Migration (B)** | ✅ Done | Move FTDI/WebSerial I/O to main thread | [hardware_connectivity.md](./backlog/hardware_connectivity.md) |
| **Hamilton E2E Validation** | ⏳ Todo | Final validation with physical Starlet | [hardware_connectivity.md](./backlog/hardware_connectivity.md) |

### Migrated from Technical Debt (2026-01-07)

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **SQLite Schema Mismatch** | ✅ Done | Add `inferred_requirements_json` column | [browser_mode.md](./backlog/browser_mode.md) |
| **REPL Rendering Stability** | ✅ Done | Fix kernel refresh race condition | [repl_enhancements.md](./backlog/repl_enhancements.md) |
| **UI Consistency** | ✅ Partial | Standardized dropdown chips (Phase 1 & 3 done) | [ui_consistency.md](./backlog/ui_consistency.md) |
| **Asset Management UX** | ✅ Partial | Refactored Add Machine/Resource flows (Phase 1-2 done) | [asset_management_ux.md](./backlog/asset_management_ux.md) |
| **Dataviz & Well Selection** | ⏳ Todo | Bridge WellDataOutput with visualization | [dataviz_well_selection.md](./backlog/dataviz_well_selection.md) |

---

## Priority 3: UI/UX Polish & Documentation

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **UI Visual Tweaks** | ✅ Done | Spacing on registry/machine tabs | [ui_standardization_q1_2026.md](./archive/2026-01-08_completed/ui_standardization_q1_2026.md) |
| **Protocol Inference "Sharp Bits"** | ✅ Done | Documentation for edge cases/gotchas | [cleanup_finalization.md](./backlog/cleanup_finalization.md) |
| ~~Spatial View Filters~~ | ✅ Done | Sorting/Filtering by location, name, workcell | [asset_management.md](./backlog/asset_management.md) |
| **Pre-Merge Finalization** | ⏳ Todo | Archive docs, cleanup files | [cleanup_finalization.md](./backlog/cleanup_finalization.md) |

---

## Recently Completed ✅ (2026-01-07)

### Architecture & Hardware

- **PLR Frontend/Backend Schema**: Standardized machine type detection for browser mode.
- **Serial Driver Generalization**: Built `ISerial` abstraction supporting custom FTDI WebUSB drivers (Phase A).
- **Main Thread Serial Migration**: Moved serial I/O and protocol logic to TypeScript main thread (Phase B).

### UI Standardization & Polish

- **No-Deck Protocol Support**: Enabled standalone machine protocols (Plate Readers, etc.) bypassing deck setup.
- **Capability Dropdown Theme Sync**: Fixed Material Select panels theaming in dark mode.
- **Search Icon Centering**: Unified search bar alignment across all features.
- **Chip-Based Filters**: Completed standardization for Resources, Machines and Runs.
- **Filter Result Counts**: Implemented dynamic result counts and delta counting for filter options.
- **Filter Overflow**: Optimized filter bar for many categories (flexbox + collapse).
- **State Delta Display**: Visualized state changes (volumes, tips) per operation.

### Browser Mode Features

- **Export/Import Database**: Implemented full state backup/restore for browser-mode users.
- **REPL Code Generation**: Optimized Python generation using `frontend_fqn` for machines.
- **Location & Maintenance Schema**: Unified `location_label` and maintenance fields across Models/DB.
- **Linked Argument UI**: Implemented side-by-side grid selection with synchronization and unlink toggle.
- **Protocol Inference "Sharp Bits"**: Documented resource inheritance, index mapping, and linked arguments.
- **Protocol Inference "Sharp Bits"**: Documented resource inheritance, index mapping, and linked arguments.
- **Systematic Linting (Phase 1)**: Executed Ruff auto-fixes (12 fixed) and addressed `crud_base.py`.
- **Spatial View Filters**: Integrated `AssetFiltersComponent` with location/workcell search into new "Spatial View".
- **Location & Description**: Added editable fields for physical location labeling and descriptions.
- **SqliteService Unit Tests**: Implemented comprehensive `sql.js` and `IndexedDB` mocks to verify persistence and initialization.

---

## Previous Accomplishments ✅ (2026-01-05)

### Simulation UI Integration (2026-01-05)

- **Deck Requirements Surface**: RequirementIndicator/Panel in Wizard
- **Time Travel Debugging**: StateInspector, StateDisplay, Timeline Scrubbing
- **State Visualizations**: History Timeline Component, Sparklines
- **Browser Mode**: Full integration with SqliteService

### State Simulation & Failure Detection (2026-01-05)

- Hierarchical protocol simulation (Boolean → Symbolic → Exact)
- 40+ PLR method contracts with preconditions/effects
- StatefulTracedMachine extending existing tracer infrastructure
- BoundsAnalyzer for loop iteration counts (items_x × items_y)
- FailureModeDetector with early pruning
- Cloudpickle + Graph Replay (Browser Mode)
- 87 comprehensive tests

### Browser Mode Stabilization

- Asset Manager rendering via SqliteService routing
- Add Resource fixed (multi-table insertion)
- Start Execution via Pyodide worker
- Hardware Discovery Button component
- OT2 slot-based deck rendering
- Deck display consistency (dynamic generation)
- Machine input forms (backend-driven dynamic forms)

### REPL Enhancements

- Light/Dark mode CSS variable theming
- Full Python tracebacks (browser + backend)
- Easy Add Assets (inventory tab with inject code)
- JupyterLite basic integration

### Protocol Computation Graph

- CST → IR graph → preconditions
- Parental resource inference (Well→Plate→Carrier→Deck)
- Container type extraction (list[Well] → element types)

### Visual Index Selection

- Interactive Grid Selection Component (Wells, Tips)
- Linked Argument Synchronization
- Backend Type Inference for Well/TipSpot parameters

### Error Handling & State Resolution ✅ (2026-01-05)

- **State Uncertainty Detection**: Method contract analysis
- **State Resolution Dialog**: UI for resolving failed operations
- **Resolution Audit Logging**: Full audit trail (Browser + Backend)
- **API Integration**: Resume/Abort run flows implemented
- **Full Test Coverage**: 30 backend tests + frontend component tests

### Maintenance System

- Schema (Alembic migration + Pydantic models)
- Per-asset toggle, Maintenance badges

### Visualizations

- Summary card sparklines
- Execution monitor timeline with phases

### Tutorial (Superseded by Browser Mode Defaults)

- Shepherd.js guided tutorial (11 steps)
- Welcome & Exit dialogs
- Note: Demo mode toggle will be removed per new architecture

---

## Priority 4: Future Enhancements

| Item | Description |
|------|-------------|
| Cost Optimization | Optimize consumable selection by cost |
| Advanced DES Scheduling | Discrete event simulation engine |
| Multi-workcell Scheduling | Cross-workcell resource sharing |
| Device Profiles | Per-device calibration profiles |
| Real-time Collaboration | Multi-user protocol editing |

---

## Related Documents

- [DEVELOPMENT_MATRIX.md](./DEVELOPMENT_MATRIX.md) - Detailed item tracking with priorities
- [TECHNICAL_DEBT.md](./TECHNICAL_DEBT.md) - Known debt items
- [backlog/](./backlog/) - Detailed feature backlogs
