# Praxis Development Matrix

**Last Updated**: 2026-01-05 (Roadmap Restructure)
**Purpose**: Consolidated view of all remaining work items with priority and difficulty ratings.

---

## Priority Legend

| Priority | Description |
|----------|-------------|
| **P1** | Critical - Must fix before demo/release |
| **P2** | High - Core functionality gaps |
| **P3** | Medium - Post-fix enhancements |
| **P4** | Low - Future features |

## Difficulty Legend

| Difficulty | Estimated Effort |
|------------|------------------|
| **S** | Small (< 2 hours) |
| **M** | Medium (2-8 hours) |
| **L** | Large (1-3 days) |
| **XL** | Extra Large (3+ days) |

---

## P1 - Critical (Remaining Browser Mode Issues)

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| **Restore Asset Selection Step** | P1 | M | [run_protocol_workflow](./backlog/run_protocol_workflow.md) | REGRESSION: Re-enable resource selection in run workflow |
| **IndexedDB Persistence** | P1 | M | [browser_mode_issues::10](./backlog/browser_mode_issues.md) | Persist SQLite DB to IndexedDB for data survivability |
| **DB Sync Issue** | P1 | L | [browser_mode_issues::9](./backlog/browser_mode_issues.md) | Root cause for multiple issues |

---

## P2 - High Priority (New Feature Development)

### Simulation UI Integration (Phase 8)

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|

| **State Failure Visualization** | P2 | M | [simulation_ui_integration](./backlog/simulation_ui_integration.md) | Visual indication of state failures in ExecutionMonitor |

### Browser Mode Defaults & Demo Elimination

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| **Default Asset Population** | P2 | M | [browser_mode_defaults](./backlog/browser_mode_defaults.md) | 1 of every resource, 1 of every machine (simulated) |
| **Infinite Consumables** | P2 | M | [browser_mode_defaults](./backlog/browser_mode_defaults.md) | Tips/consumables auto-replenish in simulation |
| **Remove Demo Mode Toggle** | P2 | S | [browser_mode_defaults](./backlog/browser_mode_defaults.md) | Eliminate separate demo mode - browser IS demo |

### Chip-Based Filter Standardization

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| **Core Filter Chip Component** | P2 | M | [chip_filter_standardization](./backlog/chip_filter_standardization.md) | Reusable chip component with states |
| **Resource Filter Chips** | P2 | M | [chip_filter_standardization](./backlog/chip_filter_standardization.md) | Status, Brand, Count, Type, Volume chips |

| **Disabled Chip UX** | P2 | S | [chip_filter_standardization](./backlog/chip_filter_standardization.md) | Shake animation + message on disabled click |
| **Unique Name Parsing** | P2 | M | [chip_filter_standardization](./backlog/chip_filter_standardization.md) | Extract distinguishing name parts |

### JupyterLite REPL

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|

| **Asset Preloading** | P2 | L | [repl_jupyterlite](./backlog/repl_jupyterlite.md) | Auto-inject resources, deck states, machines |

### Other P2 Items

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| **Machine Capabilities Verification** | P2 | M | [browser_mode_issues::14](./backlog/browser_mode_issues.md) | Hamilton Starlet 96-head/iSwap verification |
| **Capability Dropdown Theme Sync** | P2 | S | [browser_mode_issues::14](./backlog/browser_mode_issues.md) | Fix light-theme-only capability menu |

---

## P2 - Code Quality & Testing

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| **Code Quality Plan Execution** | P2 | XL | [code_quality_plan](./backlog/code_quality_plan.md) | Comprehensive quality strategy |
| **E2E Tests - Execution** | P2 | M | [code_quality_plan](./backlog/code_quality_plan.md) | Browser mode execution tests |
| **E2E Tests - Asset Management** | P2 | M | [code_quality_plan](./backlog/code_quality_plan.md) | CRUD operation tests |
| **Unit Tests - SqliteService** | P2 | M | [code_quality_plan](./backlog/code_quality_plan.md) | Browser DB service tests |
| **Final Visual QA & Test Suite** | P2 | L | [final_visual_qa](./backlog/final_visual_qa.md) | Automated Playwright tests + manual QA checklist |

---

## P3 - UI/UX Polish & Documentation

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| **UI Visual Tweaks** | P3 | S | [ui_visual_tweaks](./backlog/ui_visual_tweaks.md) | Spacing fixes in Registry/Machine tabs |
| **Protocol Inference "Sharp Bits" Docs** | P3 | M | [docs](./backlog/docs.md) | Documentation for protocol inference edge cases |
| **Spatial View Filters** | P3 | M | [asset_management::Spatial View](./backlog/asset_management.md) | Sort/Filter by location |
| **Pre-Merge Finalization** | P3 | M | [pre_merge_finalization](./backlog/pre_merge_finalization.md) | Archive docs, cleanup files |

---

## Completed ✅ (Archive: 2026-01-05)

### Simulation UI Integration ✅ (2026-01-05)

- **Deck Setup Requirements**: Requirement indicators, validation, integration with wizard
- **Time Travel Debugging**: Timeline scrubber, inspector component, state display
- **State History Timeline**: Sparkline visualizations of tips/liquids

### State Simulation & Failure Detection ✅ (2026-01-05)

- Hierarchical protocol simulation (Boolean → Symbolic → Exact)
- 40+ PLR method contracts with preconditions/effects
- StatefulTracedMachine extending existing tracer infrastructure
- BoundsAnalyzer for loop iteration counts (items_x × items_y)
- FailureModeDetector with early pruning
- Cloudpickle + Graph Replay (Browser Mode)
- 87 comprehensive tests

### Browser Mode Stabilization ✅ (2026-01-02 - 2026-01-04)

- Asset Manager rendering via SqliteService routing
- Add Resource fixed (multi-table insertion)
- Start Execution via Pyodide worker
- Hardware Discovery Button component
- OT2 slot-based deck rendering
- Deck display consistency (dynamic generation)
- Machine input forms (backend-driven dynamic forms)
- Machine type config expansion
- Button selector checkmark removal
- Simulated Machine Indicators (Badge + Validation)

| **Protocol Warnings in Selection** | [simulation_ui_integration](./backlog/simulation_ui_integration.md) | ✅ Complete (2026-01-05) |
| **Machine Filter Chips** | [chip_filter_standardization](./backlog/chip_filter_standardization.md) | ✅ Complete (2026-01-05) |
| **Execution Monitor Filters** | [browser_mode_issues::7](./backlog/browser_mode_issues.md) | ✅ Complete (2026-01-05) |

### REPL Enhancements ✅

- Variables Sidebar, Menu Bar, Save to Protocol, Completion Popup
- Light/Dark Mode theming, Full Python tracebacks, Easy Add Assets
- Protocol Editor disabled state with "Coming Soon" tooltip
- JupyterLite basic integration
- **Asset Menu Search & Filters** (✅ 2026-01-05)
- **Empty State with Link** (✅ 2026-01-05)

### Tutorial & Demo Mode ✅ (2026-01-05) [Superseded by Browser Mode Defaults]

- Guided Tutorial (Shepherd.js) with 11 steps
- Runtime Demo Mode toggle (to be removed)
- Persistent Onboarding state
- Welcome & Exit Dialogs

### Protocol Computation Graph ✅

- CST → IR graph → preconditions
- Parental resource inference (Well→Plate→Carrier→Deck)
- Container type extraction (list[Well] → element types)

### Visual Index Selection ✅

- Interactive Grid Selection Component (Wells, Tips)
- Linked Argument Synchronization (`LinkedSelectorService`)
- Backend Type Inference for Well/TipSpot parameters
- Formly Integration & Protocol Metadata Updates

### Maintenance System ✅

- Schema (Alembic migration + Pydantic models)
- Per-asset toggle in details dialog
- Maintenance badges component

### Visualizations ✅

- Summary card sparklines
- Execution monitor timeline with phases

### Error Handling & State Resolution ✅ (2026-01-05)

- **State Uncertainty Detection**: Method contract analysis, Pydantic models (UncertainStateChange)
- **State Resolution Dialog**: Angular dialog with quick actions (Success/Fail/Custom)
- **Resolution Audit Logging**: SqliteService (Browser) + SQLAlchemy (Backend)
- **API Integration**: 4 new endpoints in scheduler.py
- **Full Test Coverage**: 30 backend tests + frontend component tests

---

## Summary by Priority

| Priority | Count | Description |
|----------|-------|-------------|
| **P1** | 3 | Critical browser mode issues (Asset Selection, IndexedDB, DB Sync) |
| **P2** | 27 | New features: Simulation UI, Browser Defaults, Error Handling, Filters, Quality |
| **P3** | 4 | UI polish, documentation, finalization |

**Total Active Items**: 34
