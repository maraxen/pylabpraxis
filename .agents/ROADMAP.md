# Praxis Development Roadmap

**Last Updated**: 2026-01-05 (Roadmap Restructure)
**Current Phase**: Feature Development & Quality Assurance

---

## Executive Summary

The backend simulation infrastructure is **complete** (87 tests passing). Focus now shifts to:

1. **Simulation UI Integration** - Surface cached simulation results in the UI
2. **Browser Mode Defaults** - Eliminate demo mode, make browser mode the default experience
3. **Error Handling & State Resolution** - ✅ Complete (Backend + Frontend)
4. **Browser Mode Defaults** - Eliminate demo mode, make browser mode the default experience
5. **Chip-Based Filter Standardization** - Unified filter UX across all surfaces
6. **Quality Assurance** - Comprehensive test suite and visual QA

---

## Priority 1: Critical - Remaining Browser Mode Issues

**Goal**: Resolve final blocking issues in browser mode

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **Restore Asset Selection Step** | 🔴 Regression | Asset selection step missing from workflow | [run_protocol_workflow.md](./backlog/run_protocol_workflow.md) |
| **IndexedDB Persistence** | 🔴 Missing | SQLite DB must persist across page reloads | [browser_mode_issues.md](./backlog/browser_mode_issues.md) |
| **DB Sync Issue** | 🔴 Root Cause | Browser praxis.db out of sync with features | [browser_mode_issues.md](./backlog/browser_mode_issues.md) |

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
| **Protocol Warnings** | ⏳ Todo | Show failure mode warnings in protocol selection | [simulation_ui_integration.md](./backlog/simulation_ui_integration.md) |
| **Deck Setup Requirements** | ✅ Done | Surface requirements in deck setup wizard | [simulation_ui_integration.md](./backlog/simulation_ui_integration.md) |
| **State Failure Visualization** | ⏳ Todo | Show state at each operation in Execution Monitor | [simulation_ui_integration.md](./backlog/simulation_ui_integration.md) |
| **Time Travel Debugging** | ✅ Done | Inspect state at any operation step | [simulation_ui_integration.md](./backlog/simulation_ui_integration.md) |
| **State History Timeline** | ✅ Done | Visual timeline of state changes | [simulation_ui_integration.md](./backlog/simulation_ui_integration.md) |

---

## Priority 2: High - Browser Mode Defaults & Demo Elimination

**Goal**: Make browser mode the primary experience with sensible defaults

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **Default Asset Population** | ⏳ Todo | 1 of every resource, 1 of every machine (simulated) | [browser_mode_defaults.md](./backlog/browser_mode_defaults.md) |
| **Simulated Machine Indicator** | ⏳ Todo | Show "Simulated" chip on all sim-backend machines | [browser_mode_defaults.md](./backlog/browser_mode_defaults.md) |
| **Infinite Consumables** | ⏳ Todo | Tips/consumables auto-replenish in simulation | [browser_mode_defaults.md](./backlog/browser_mode_defaults.md) |
| **Remove Demo Mode Toggle** | ⏳ Todo | Eliminate separate demo mode - browser IS demo | [browser_mode_defaults.md](./backlog/browser_mode_defaults.md) |

---

## Priority 2: High - Chip-Based Filter Standardization

**Goal**: Unified chip-based filter UX across all surfaces

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **Core Filter Chip Component** | ⏳ Todo | Reusable chip with active/inactive/disabled states | [chip_filter_standardization.md](./backlog/chip_filter_standardization.md) |
| **Resource Filter Chips** | ⏳ Todo | Status, Brand, Count, Type, Volume | [chip_filter_standardization.md](./backlog/chip_filter_standardization.md) |
| **Machine Filter Chips** | ⏳ Todo | Category, Simulated, Status, Backend | [chip_filter_standardization.md](./backlog/chip_filter_standardization.md) |
| **Disabled Chip UX** | ⏳ Todo | Shake animation + message on disabled click | [chip_filter_standardization.md](./backlog/chip_filter_standardization.md) |
| **Unique Name Parsing** | ⏳ Todo | Extract distinguishing name parts | [chip_filter_standardization.md](./backlog/chip_filter_standardization.md) |

---

## Priority 2: High - JupyterLite REPL Enhancements

**Goal**: Complete JupyterLite migration with search and filters

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **Asset Menu Search & Filters** | ⏳ Todo | Search bar and filter chips in asset sidebar | [repl_jupyterlite.md](./backlog/repl_jupyterlite.md) |
| **Empty State with Link** | ⏳ Todo | Link to Assets page when inventory empty | [repl_jupyterlite.md](./backlog/repl_jupyterlite.md) |
| **Asset Preloading** | ⏳ Todo | Auto-inject resources, deck states, machines | [repl_jupyterlite.md](./backlog/repl_jupyterlite.md) |

---

## Priority 2: Code Quality & Testing

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **Code Quality Plan** | ⏳ Planning | Comprehensive strategy execution | [code_quality_plan.md](./backlog/code_quality_plan.md) |
| **E2E Test Suite** | ⏳ Todo | Critical flow coverage with Playwright | [code_quality_plan.md](./backlog/code_quality_plan.md) |
| **Unit Test Coverage** | ⏳ Todo | Service layer tests (SqliteService, etc.) | [code_quality_plan.md](./backlog/code_quality_plan.md) |
| **Final Visual QA** | ⏳ Todo | Automated + manual review | [final_visual_qa.md](./backlog/final_visual_qa.md) |

---

## Priority 2: Other Items

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **Machine Capabilities Verification** | ⏳ Todo | Hamilton Starlet 96-head/iSwap verification | [browser_mode_issues.md](./backlog/browser_mode_issues.md) |
| **Capability Dropdown Theme Sync** | ⏳ Todo | Fix light-theme-only capability menu | [browser_mode_issues.md](./backlog/browser_mode_issues.md) |
| **Execution Monitor Filters** | ⏳ Todo | Make filters actually filter run list | [browser_mode_issues.md](./backlog/browser_mode_issues.md) |

---

## Priority 3: UI/UX Polish & Documentation

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **UI Visual Tweaks** | ⏳ Todo | Spacing on registry/machine tabs | [ui_visual_tweaks.md](./backlog/ui_visual_tweaks.md) |
| **Protocol Inference "Sharp Bits"** | ⏳ Todo | Documentation for edge cases/gotchas | [docs.md](./backlog/docs.md) |
| **Spatial View Filters** | ⏳ Todo | Asset location sorting/filtering | [asset_management.md](./backlog/asset_management.md) |
| **Pre-Merge Finalization** | ⏳ Todo | Archive docs, cleanup files | [pre_merge_finalization.md](./backlog/pre_merge_finalization.md) |

---

## Recently Completed ✅ (2026-01-02 - 2026-01-05)

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
