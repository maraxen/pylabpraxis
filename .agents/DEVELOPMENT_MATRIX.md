# Praxis Development Matrix

**Last Updated**: 2026-01-08 (REPL Stability Fixed)
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
| ~~PLR Frontend/Backend Schema~~ | ~~P1~~ | ~~M~~ | [TECHNICAL_DEBT](./TECHNICAL_DEBT.md) | ✅ Complete (Added `frontend_fqn`, updated services/scrapers) |
| ~~Serial/USB Driver Generalization~~ | ~~P1~~ | ~~L~~ | [hardware_connectivity](./backlog/hardware_connectivity.md) | ✅ Complete (Implemented `ISerial` abstraction + FTDI driver) |
| ~~Restore Asset Selection Step~~ | ~~P1~~ | | [run_protocol_workflow](./backlog/run_protocol_workflow.md) | ✅ Complete (verified in code) |
| ~~IndexedDB Persistence~~ | ~~P1~~ | | [browser_mode](./backlog/browser_mode.md) | ✅ Complete (`SqliteService.saveToIndexedDB()`) |

---

## P2 - High Priority (New Feature Development)

### Simulation UI Integration (Phase 8) - ✅ Complete

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| ~~State Delta Display (Phase 8.4)~~ | ~~P2~~ | ~~M~~ | [simulation_ui_integration](./archive/2026-01-07_completed/simulation_ui_integration.md) | ✅ Complete (Operation timeline state diffs) |

### Browser Mode Defaults & Demo Elimination ✅ (ARCHIVED)

> All items completed and archived to `archive/2026-01-06_completed/browser_mode_defaults.md`

### Chip-Based Filter Standardization - Mostly Complete

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| ~~Core Filter Chip Component~~ | ~~P2~~ | ~~M~~ | [chip_filter_standardization](./backlog/chip_filter_standardization.md) | ✅ Complete |
| ~~Resource Filter Chips~~ | ~~P2~~ | ~~M~~ | [chip_filter_standardization](./backlog/chip_filter_standardization.md) | ✅ Complete (Integrated with Resource Inventory) |
| ~~Disabled Chip UX~~ | ~~P2~~ | ~~S~~ | [chip_filter_standardization](./backlog/chip_filter_standardization.md) | ✅ Complete (shake animation implemented) |
| ~~Unique Name Parsing~~ | ~~P2~~ | ~~M~~ | [chip_filter_standardization](./backlog/chip_filter_standardization.md) | ✅ Complete (Implemented `name-parser.ts` + tooltips) |

### JupyterLite REPL ✅ (ARCHIVED)

> Core integration completed. Archived to `archive/2026-01-06_completed/repl_jupyterlite.md`.
> Remaining: Asset Preloading is future enhancement (tracked in TECHNICAL_DEBT.md).

### Other P2 Items

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| ~~Export/Import App State~~ | ~~P2~~ | ~~M~~ | [browser_mode](./backlog/browser_mode.md) | ✅ Complete (SqliteService export/import methods) |
| ~~Chip Filter Overflow~~ | ~~P2~~ | ~~S~~ | [chip_filter_standardization](./backlog/chip_filter_standardization.md) | ✅ Complete (Flex-wrap + dropdown collapsing) |
| ~~Search Icon Centering~~ | ~~P2~~ | ~~S~~ | [chip_filter_standardization](./backlog/chip_filter_standardization.md) | ✅ Complete (CSS fix for alignment) |
| ~~Capability Dropdown Theme~~ | ~~P2~~ | ~~S~~ | [chip_filter_standardization](./backlog/chip_filter_standardization.md) | ✅ Complete (Sync select panels with dark theme) |
| **Machine Capabilities Verification** | P2 | M | [browser_mode](./backlog/browser_mode.md) | Hamilton Starlet 96-head/iSwap verification |
| ~~Physical Connection Testing~~ | ~~P2~~ | ~~L~~ | [hardware_connectivity](./backlog/hardware_connectivity.md) | ✅ Phase B Complete (Main Thread Migration) |
| **Hamilton E2E Validation** | P2 | M | [hardware_connectivity](./backlog/hardware_connectivity.md) | Final validation with Starlet |

---

## P2 - Code Quality & Testing

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| ~~Systematic Linting Fixes~~ | ~~P2~~ | ~~L~~ | [quality_assurance](./backlog/quality_assurance.md) | ✅ Complete (77+ bugs/lints resolved, clean check) |
| **Code Quality Plan Execution** | P2 | XL | [quality_assurance](./backlog/quality_assurance.md) | Comprehensive quality strategy (using `ty`) |
| **E2E Tests - Execution** | P2 | M | [quality_assurance](./backlog/quality_assurance.md) | Browser mode execution tests |
| ~~E2E Tests - Asset Management~~ | ~~P2~~ | ~~M~~ | [quality_assurance](./backlog/quality_assurance.md) | ✅ Complete (5 UI tests passing, CRUD skipped) |
| ~~Unit Tests - SqliteService~~ | ~~P2~~ | ~~M~~ | [quality_assurance](./backlog/quality_assurance.md) | ✅ Complete (Comprehensive coverage, persistence verification) |
| **Final Visual QA & Test Suite** | P2 | L | [quality_assurance](./backlog/quality_assurance.md) | Automated Playwright tests + manual QA checklist |
| **Frontend Type Safety** | P3 | S | [TECHNICAL_DEBT](./TECHNICAL_DEBT.md) | Resolve `any` casts in SqliteService/Settings |

### Migrated from Technical Debt (2026-01-07)

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| ~~SQLite Schema Mismatch~~ | ~~P1~~ | ~~🟢 Easy~~ | [browser_mode](./backlog/browser_mode.md) | ✅ Complete (Added `inferred_requirements_json` column) |
| ~~UI Consistency - Exec Monitor~~ | ~~P2~~ | ~~🟡 Intricate~~ | [ui_consistency](./backlog/ui_consistency.md) | ✅ Complete (Standardized chips; menus N/A) |
| ~~Asset Management UX~~ | ~~P2~~ | ~~🟡 Intricate~~ | [asset_management_ux](./backlog/asset_management_ux.md) | ✅ Complete (Resolved Phase 1 regressions) |
| **Dataviz & Well Selection** | P2 | 🔴 Complex | [dataviz_well_selection](./backlog/dataviz_well_selection.md) | Bridge WellDataOutput with visualization |
| ~~Skipped Tests Investigation~~ | ~~P2~~ | ~~🟢 Easy~~ | [quality_assurance](./backlog/quality_assurance.md) | ✅ Complete (Fixed Orchestrator tests, cleaned frontend dead code) |
| **Factory ORM Integration** | P2 | 🟡 Intricate | [quality_assurance](./backlog/quality_assurance.md) | Fix Factory Boy FK population |

### Migrated from Technical Debt (2026-01-08)

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| ~~Browser Schema Scripts~~ | ~~P2~~ | ~~🟡 Intricate~~ | [browser_mode](./backlog/browser_mode.md) | ✅ Complete (Fixed generate_browser_db.py schema logic) |
| **E2E Data Seeding** | P2 | 🟡 Intricate | [quality_assurance](./backlog/quality_assurance.md) | Pre-populate DB for Playwright Asset tests |
| **Frontend Type Safety** | P3 | 🟢 Easy | [quality_assurance](./backlog/quality_assurance.md) | Fix Blob casting and Window mocking |
| **JupyterLite 404s/Load** | P3 | 🟡 Intricate | [repl_enhancements](./backlog/repl_enhancements.md) | Suppress 404s, optimize startup |
| **Repo Cleanup** | P3 | 🟢 Easy | [cleanup_finalization](./backlog/cleanup_finalization.md) | Remove .pymon, debug files |

### Added from User Verification (2026-01-08)

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| ~~Asset Management UX Regressions~~ | ~~P2~~ | ~~🟡 Intricate~~ | [asset_management_ux](./backlog/asset_management_ux.md) | ✅ Complete (Verified fixed) |
| ~~Angular ARIA Migration~~ | ~~P2~~ | ~~🔴 Complex~~ | [angular_aria_migration](./backlog/angular_aria_migration.md) | ✅ Phase 1 Complete (Multiselect/Select components implemented & integrated) |
| ~~Settings & Stepper Polish~~ | ~~P3~~ | ~~🟡 Intricate~~ | [ui_consistency](./backlog/ui_consistency.md) | ✅ Complete (Icons fixed, theme selector refined) |
| **Guided Deck Setup UI** | P3 | S | [ui_consistency](./backlog/ui_consistency.md) | ⚠️ Items 1,3,4 fixed; Item 2 (Confirm button) remains broken |
| ~~Simulated Machine Unification~~ | ~~P2~~ | ~~M~~ | [browser_mode](./backlog/browser_mode.md) | ✅ Complete (Unified Simulated/Chatterbox UI & logic) |
| ~~Machine Dialog Fixes~~ | ~~P1~~ | ~~M~~ | [browser_mode](./backlog/browser_mode.md) | ✅ Complete (Fixed schema mismatch & NOT NULL error) |

---

## P3 - UI/UX Polish & Documentation

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| **Protocol Inference "Sharp Bits" Docs** | ~~P3~~ | ~~M~~ | [cleanup_finalization](./backlog/cleanup_finalization.md) | ✅ Complete (Created `protocol_inference_sharp_bits.md`) |
| ~~Spatial View Filters~~ | ~~P3~~ | ~~M~~ | [asset_management](./backlog/asset_management.md) | ✅ Complete (Implemented `SpatialViewComponent` with location search) |
| ~~Pre-Merge Finalization~~ | ~~P3~~ | ~~M~~ | [cleanup_finalization](./backlog/cleanup_finalization.md) | ✅ Complete (Archive docs, cleanup files) |

---

## Completed ✅ (Recent Sessions)

### UI & UX Standardization (2026-01-08)

- **Asset Management UX**: Resolved Phase 1 regressions in the "Add Machine" dialog (stepper theme sync, backend filtering, dynamic capability forms, and JSON blob editing).
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

## Summary by Priority

| Priority | Count | Description |
|----------|-------|-------------|
| **P1** | 0 | All architecture/core issues resolved |
| **P2** | ~7 | Code Quality (QA suite), Hardware testing |
| **P3** | 4 | UI polish, documentation, finalization |

**Total Active Items**: ~11
**Archived This Session**: Prompts 01-10 from `250106` (All items completed), `plr_static_analysis_debugging.md`, `10_sqliteservice_unit_tests.md`
