# Praxis Development Roadmap

**Last Updated**: 2026-01-05 (State Simulation Completed)
**Current Phase**: Feature Development & Quality Assurance

---

## Executive Summary

Browser mode stabilization is largely complete. The focus now shifts to **new feature development** (interactive well selection, JupyterLite REPL, hardware discovery UX) and **quality assurance** (comprehensive test suite, visual QA review).

---

## Priority 1: Critical - Remaining Browser Mode Issues

**Goal**: Resolve final blocking issues in browser mode

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **Add Resource Not Working** | 🔴 Broken | Cannot add resources in browser mode - needs investigation | [browser_mode_issues.md](./backlog/browser_mode_issues.md) |
| **DB Sync Issue** | 🔴 Root Cause | Browser praxis.db out of sync with features | [browser_mode_issues.md](./backlog/browser_mode_issues.md) |
| **Restore Asset Selection Step** | 🔴 Regression | Asset selection step missing from workflow | [run_protocol_workflow.md](./backlog/run_protocol_workflow.md) |

---

## Priority 2: High - New Feature Development

### State Snapshot Tracing

**Goal**: Generic state tracking system to predict protocol failures (volume, tips, etc.) via simulation

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **Traced Workcell** | ⏳ Todo | Serializable state snapshot wrapper | [state_snapshot_tracing.md](./backlog/state_snapshot_tracing.md) |
| **State Validator** | ⏳ Todo | Generic predicate system for preconditions | [state_snapshot_tracing.md](./backlog/state_snapshot_tracing.md) |
| **State Recorder** | ⏳ Todo | Record state deltas for every operation | [state_snapshot_tracing.md](./backlog/state_snapshot_tracing.md) |
| **Visualization** | ⏳ Todo | Show state failures in Execution Monitor | [state_snapshot_tracing.md](./backlog/state_snapshot_tracing.md) |

### Visual Index Selection for Itemized Resources

**Goal**: Interactive UI for selecting indices in itemized resources (wells, tips, tubes, etc.) using `items_x` × `items_y` grid

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **IndexSelectorComponent** | ⏳ Todo | Grid-based click/drag selection using `items_x` × `items_y` | [visual_well_selection.md](./backlog/visual_well_selection.md) |
| **Linked Arguments** | ⏳ Todo | Shared indices for tips ↔ wells, source ↔ dest | [visual_well_selection.md](./backlog/visual_well_selection.md) |
| **Type Inference Integration** | ⏳ Todo | Auto-detect Well, TipSpot, Sequence[Well], etc. | [visual_well_selection.md](./backlog/visual_well_selection.md) |
| **Backend Formly Integration** | ⏳ Todo | Protocol decorator → index_selector field type | [visual_well_selection.md](./backlog/visual_well_selection.md) |

### REPL → JupyterLite Migration

**Goal**: Replace xterm.js REPL with full JupyterLite notebook environment

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **JupyterLite Integration** | ⏳ Todo | Embed JupyterLite in REPL panel | [repl_jupyterlite.md](./backlog/repl_jupyterlite.md) |
| **Shared Pyodide Kernel** | ⏳ Todo | Use same kernel as rest of app (browser mode) | [repl_jupyterlite.md](./backlog/repl_jupyterlite.md) |
| **Preload Assets** | ⏳ Todo | Auto-inject resources, deck states, machines | [repl_jupyterlite.md](./backlog/repl_jupyterlite.md) |
| **Quick Add Support** | ⏳ Todo | Insert variable names from inventory panel | [repl_jupyterlite.md](./backlog/repl_jupyterlite.md) |
| **Remove xterm.js REPL** | ⏳ Todo | Full replacement, not addition | [repl_jupyterlite.md](./backlog/repl_jupyterlite.md) |

### Hardware Discovery Menu Restoration

**Goal**: Unified hardware discovery UX across the application

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **USB Icon Buttons** | ⏳ Todo | Replace magnifying glass with USB symbol on all discovery triggers | [hardware_discovery_menu.md](./backlog/hardware_discovery_menu.md) |
| **Restore Discovery Menu** | ⏳ Todo | Quick-link in Asset Management + Command Palette | [hardware_discovery_menu.md](./backlog/hardware_discovery_menu.md) |
| **Exclude Simulator Backend** | ⏳ Todo | Simulator should be always-available, not in discovery list | [hardware_discovery_menu.md](./backlog/hardware_discovery_menu.md) |

---

## Priority 2: Code Quality & Testing

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **Code Quality Plan** | ⏳ Planning | Comprehensive strategy execution | [code_quality_plan.md](./backlog/code_quality_plan.md) |
| **E2E Test Suite** | ⏳ Todo | Critical flow coverage with Playwright | [code_quality_plan.md](./backlog/code_quality_plan.md) |
| **Unit Test Coverage** | ⏳ Todo | Service layer tests (SqliteService, etc.) | [code_quality_plan.md](./backlog/code_quality_plan.md) |
| **Final Visual QA** | ⏳ Todo | Automated + manual review | [final_visual_qa.md](./backlog/final_visual_qa.md) |

---

## Priority 3: UI/UX Polish & Documentation

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **Resource Inventory Filters** | ⏳ Todo | Add filter chips to Resources tab (match Machines tab) | [ui_visual_tweaks.md](./backlog/ui_visual_tweaks.md) |
| **UI Visual Tweaks** | ⏳ Todo | Spacing on registry/machine tabs | [ui_visual_tweaks.md](./backlog/ui_visual_tweaks.md) |
| **Protocol Inference "Sharp Bits"** | ⏳ Todo | Documentation for edge cases/gotchas | [docs.md](./backlog/docs.md) |
| **Spatial View Filters** | ⏳ Todo | Asset location sorting/filtering | [asset_management.md](./backlog/asset_management.md) |
| **Pre-Merge Finalization** | ⏳ Todo | Archive docs, cleanup files | [pre_merge_finalization.md](./backlog/pre_merge_finalization.md) |

---

## Recently Completed ✅ (2026-01-02 - 2026-01-05)

### State Simulation & Failure Detection (2026-01-05)

- Hierarchical protocol simulation (Boolean → Symbolic → Exact)
- 40+ PLR method contracts with preconditions/effects
- StatefulTracedMachine extending existing tracer infrastructure
- BoundsAnalyzer for loop iteration counts (items_x × items_y)
- FailureModeDetector with early pruning
- 59 comprehensive tests

### Simulation Integration & Caching (2026-01-05)

- ProtocolSimulator facade class for unified access
- SimulationService for running and caching simulations
- Database schema: simulation_result_json, inferred_requirements_json, failure_modes_json
- Alembic migration for simulation cache columns
- Integration with DiscoveryService (auto-simulation on protocol discovery)
- Pydantic models for API response (FunctionProtocolDefinitionResponse)

### Browser Mode Stabilization

- Asset Manager rendering via SqliteService routing
- Start Execution via Pyodide worker
- Data Views field in frontend ProtocolDefinition
- Hardware Discovery Button component
- OT2 slot-based deck rendering
- Execution Monitor filters (browser mode)
- API Docs static generation
- Deck display consistency (dynamic generation)
- Machine input forms (backend-driven dynamic forms)
- Machine type config expansion
- Button selector checkmark removal

### REPL Enhancements

- Light/Dark mode CSS variable theming
- Full Python tracebacks (browser + backend)
- Easy Add Assets (inventory tab with inject code)
- Protocol Editor disabled state

### Protocol Computation Graph

- CST → IR graph → preconditions
- Parental resource inference (Well→Plate→Carrier→Deck)
- Container type extraction (list[Well] → element types)

### Maintenance System

- Schema (Alembic migration + Pydantic models)
- Per-asset toggle in details dialog
- Maintenance badges component

### Visualizations

- Summary card sparklines
- Execution monitor timeline with phases

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
