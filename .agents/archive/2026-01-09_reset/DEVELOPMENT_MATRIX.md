# Praxis Development Matrix

**Last Updated**: 2026-01-09 (Technical Debt Migration)
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

| Difficulty | Description |
|------------|-------------|
| 🔴 **Complex** | Requires careful planning, likely debugging |
| 🟡 **Intricate** | Many parts, but well-specified tasks |
| 🟢 **Easy Win** | Straightforward, minimal ambiguity |

---

## P1 - Critical (Architecture & Core Issues)

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|

---

## P2 - High Priority (New Feature Development)

### Simulation UI Integration (Phase 8) - ✅ Complete (Archived)

### Browser Mode Defaults & Demo Elimination ✅ (Archived 2026-01-06)

### Chip-Based Filter Standardization - ✅ Complete (Archived 2026-01-08)

### JupyterLite REPL ✅ (Archived 2026-01-06)

### Other P2 Items

| **Machine Capabilities Verification** | P2 | M | [browser_mode](./backlog/browser_mode.md) | Hamilton Starlet 96-head/iSwap verification |

| **Hamilton E2E Validation** | P2 | M | [hardware_connectivity](./backlog/hardware_connectivity.md) | Final validation with Starlet |

---

## P2 - Code Quality & Testing

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|

| **Final Visual QA & Test Suite** | P2 | L | [quality_assurance](./backlog/quality_assurance.md) | Automated Playwright tests + manual QA checklist |

### Migrated from Technical Debt - ✅ All Complete (Archived)

---

## P3 - UI/UX Polish & Documentation

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|

---

## Completed ✅ (Recent Sessions)

### UI & UX Standardization (2026-01-08)

- **Asset Management UX**: Resolved Phase 1 regressions in the "Add Machine" dialog (stepper theme sync, backend filtering, dynamic capability forms, and JSON blob editing).
- **Playground Inventory Dialog**: ✅ Complete (Redesigned with tabbed layout, quick add autocomplete, and polished stepper).
- **Deck View Consistency**: Refactored `DeckGeneratorService` and `VisualizerComponent` to use real machine definitions/state instead of hardcoded mock data.
- **UI Visual Tweaks**: Fixed spacing in Registry, alignment in Machines, and implemented themed gradients across cards and list items.

### REPL Enhancements (2026-01-08)

- **REPL Rendering Stability**: Fixed race condition in kernel initialization by implementing a ready signal handshake.

### Documentation & Code Quality (2026-01-07)

- **Systematic Linting Fixes**: Achieved a clean Ruff check (77+ errors resolved via auto-fix, manual correction, and targeted ignores).
- **Protocol Inference "Sharp Bits"**: Created comprehensive documentation for resource inheritance, index mapping, and linked arguments.

### UI & UX Standardization (2026-01-07)

- **No-Deck Protocol Support**: Enabled protocols without Liquid Handler/Deck requirements (e.g., Plate Readers).
- **Capability Dropdown Theme Sync**: Fixed light-theme-only select panels in dark mode.
- **Search Icon Centering**: Aligned search icons vertically across all inputs.
- **Chip Filter Overflow**: Implemented flex-wrap and dropdown collapsing (>5 chips).
- **Resource Filter Chips**: Standardized inventory filters with the new chip pattern.
- **Filter Result Counts**: Implemented delta counting and multi-select result counts for filter chips.
- **State Delta Display**: Integrated simulation state diffs into the operation timeline.
- **Export/Import App State**: Added backup/restore functionality for browser-mode SQLite.
- **REPL Code Generation**: Enhanced with `frontend_fqn` support for Hamilton/PlateReader.
- **Locations & Maintenance**: Implemented `location_label` and maintenance schemas in ORM/Pydantic.
- **Linked Argument UI**: Implemented side-by-side grid selection with synchronization and unlink toggle.
- **Spatial View**: Added `SpatialViewComponent` with filters for Workcell, Machine, Status, and Location search.
- **Location Labels**: Added editable `location_label` to Machine and Resource dialogs.
- **Unique Name Parsing**: Implemented word-based shortening for filter labels with full-name tooltips; integrated across all asset filters.

### Architecture & Hardware (2026-01-07)

- **PLR Frontend/Backend Schema**: Added `frontend_fqn` to track browser-compatible machine types.
- **Serial Driver Generalization**: Built `ISerial` abstraction supporting custom FTDI WebUSB drivers (Phase A).
- **Main Thread Serial Migration**: Moved serial I/O and protocol logic to TypeScript main thread (Phase B).

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
- **Unit Tests - SqliteService**: Implemented robust unit tests with `sql.js` and `IndexedDB` mocks, achieving comprehensive coverage of persistence and initialization flows.
- **87 comprehensive tests**

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

| **Protocol Warnings in Selection** | [simulation_ui_integration](./archive/2026-01-07_completed/simulation_ui_integration.md) | ✅ Complete (2026-01-05) |
| **Machine Filter Chips** | [chip_filter_standardization](./backlog/chip_filter_standardization.md) | ✅ Complete (2026-01-05) |
| **Execution Monitor Filters** | [browser_mode_issues::7](./backlog/browser_mode_issues.md) | ✅ Complete (2026-01-05) |

### REPL Enhancements ✅

- Variables Sidebar, Menu Bar, Save to Protocol, Completion Popup
- Light/Dark Mode theming, Full Python tracebacks, Easy Add Assets
- Protocol Editor disabled state with "Coming Soon" tooltip
- JupyterLite basic integration
- **Asset Menu Search & Filters** (✅ 2026-01-05)
- **Empty State with Link** (✅ 2026-01-05)
- **Inventory Dialog**: Replaced simple addition with guided multi-step wizard (Machine/Resource, Config, Filters).
- [x] **(High) Fix "Buggy" Behavior**: User reported autoselection "seems buggy" (2026-01-08). Investigate failure cases.
- [x] Consider resource `status` (prefer `AVAILABLE_IN_STORAGE` over `IN_USE`)

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

### Backend Refactoring & Stability ✅ (2026-01-06)

- **Service Layer Fixes**: Resolved `DeckTypeDefinitionService` test failures & ORM initialization issues
- **Pydantic Model Refactoring**: Converted `RuntimeAssetRequirement` to pure Pydantic v2 (UUID7 support)
- **API Audit**: Verified `create_crud_router` usage usage across API layer
- **Type Safety**: Resolved Pyright errors in `AssetManager` (Resource Update models)

---

### Archived Cleanup (2026-01-09)

- **PLR Frontend/Backend Schema**: ✅ Complete (Added `frontend_fqn`, updated services/scrapers)
- **Serial/USB Driver Generalization**: ✅ Complete (Implemented `ISerial` abstraction + FTDI driver)
- **Restore Asset Selection Step**: ✅ Complete (verified in code)
- **IndexedDB Persistence**: ✅ Complete (`SqliteService.saveToIndexedDB()`)
- **State Delta Display (Phase 8.4)**: ✅ Complete (Operation timeline state diffs)
- **Core Filter Chip Component**: ✅ Complete
- **Resource Filter Chips**: ✅ Complete (Integrated with Resource Inventory)
- **Disabled Chip UX**: ✅ Complete (shake animation implemented)
- **Unique Name Parsing**: ✅ Complete (Implemented `name-parser.ts` + tooltips)
- **Export/Import App State**: ✅ Complete (SqliteService export/import methods)
- **Chip Filter Overflow**: ✅ Complete (Flex-wrap + dropdown collapsing)
- **Search Icon Centering**: ✅ Complete (CSS fix for alignment)
- **Capability Dropdown Theme**: ✅ Complete (Sync select panels with dark theme)
- **Physical Connection Testing**: ✅ Phase B Complete (Main Thread Migration)
- **Systematic Linting Fixes**: ✅ Complete (77+ bugs/lints resolved, clean check)
- **Code Quality Plan Execution**: ✅ Complete (Systematic quality sweep using `ty`)
- **E2E Tests - Execution**: ✅ Complete (Browser/Simulation execution flow)
- **E2E Tests - Asset Management**: ✅ Complete (5 UI tests passing, CRUD skipped)
- **Unit Tests - SqliteService**: ✅ Complete (Comprehensive coverage, persistence verification)
- **Protocols "Not Analyzed" Status Fix**: ✅ Complete (Fixed persistence of source_hash and simulation results)
- **Frontend Type Safety**: ✅ Complete (Resolved Blob casting and Window mocking)
- **Migrated Tech Debt Items**:
  - SQLite Schema Mismatch, UI Consistency, Asset Management UX, Dataviz & Well Selection
  - Browser Schema Scripts, E2E Data Seeding, JupyterLite, Repo Cleanup
  - Protocol Hydration, Workflow Debugging, Navigation, REPL Theme, Browser DB, Exec Monitor, Well Selector, Schema linkage
  - Asset Management Regressions, Angular ARIA Migration, Settings/Stepper Polish
  - Guided Deck Setup, Simulated Machine Unification, Machine Dialog Fixes
- **UI & Documentation Polish**:
  - Protocol Inference Docs, Example Protocols, Spatial View Filters
  - Diagram Expansion, Footer/Header Layout, Pre-Merge Finalization

---

## Summary by Priority

| Priority | Count | Description |
|----------|-------|-------------|
| **P1** | 0 | All architecture/core issues resolved |
| **P2** | ~4 | Code Quality (QA suite), Hardware testing, Run Persistence |
| **P3** | 2 | UI polish (Firefox, Facets) |

**Total Active Items**: ~6
**Archived This Session (2026-01-09)**: Massive cleanup of completed items from Q1 2026 backlog.
