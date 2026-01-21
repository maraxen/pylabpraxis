# Praxis Development Matrix
<!-- Migrated to MCP database on 2026-01-21 -->

**Last Updated**: 2026-01-20
**Purpose**: Current iteration work items with priority and difficulty ratings.
**Current Batch**: [260119_comprehensive_review](tasks/260119_comprehensive_review/MASTER_PLAN.md)

---

## Legend

### Priority

| Priority | Description                       |
|----------|-----------------------------------|
| **P1**   | Critical - Blocking alpha release |
| **P2**   | High - Required for alpha quality |
| **P3**   | Medium - Should have for alpha    |
| **P4**   | Low - Nice to have / post-alpha   |

### Difficulty

| Difficulty | Description                                          |
|------------|------------------------------------------------------|
| **Hard**   | Complex architecture, multi-system, likely debugging |
| **Medium** | Well-defined but substantial work                   |
| **Easy**   | Straightforward, minimal ambiguity                   |

---

## P1 - Critical (Alpha Blockers)

| Item                  | Difficulty | Backlog                                 | Description                                                          |
|-----------------------|------------|-----------------------------------------|----------------------------------------------------------------------|
| (None currently)      | -          | -                                       | All top blockers resolved for now.                                   |

---

## P2 - High Priority (Alpha Quality)

### Feature Enhancements (Batch 260115)

| Item                           | Difficulty | Task                                                          | Description                                          |
|--------------------------------|------------|---------------------------------------------------------------|------------------------------------------------------|
| Browser Resources Validation   | Easy       | [archive/tasks/260115_feature_enhancements/browser_resources_init](./archive/tasks/260115_feature_enhancements/browser_resources_init/) | Validate 1-of-each labware seeding in browser mode |
|                                |            |                                                               |                                                      |

### Technical Debt (Batch 260115)

| Item                           | Difficulty | Task                                                          | Description                                          |
|--------------------------------|------------|---------------------------------------------------------------|------------------------------------------------------|
| Database & Models Cleanup      | Medium     | [archive/tasks/260115_tech_debt/database_models](./archive/tasks/260115_tech_debt/database_models/) | PostgreSQL verification, SQLModel warnings |
| Backend Test Sync              | Medium     | [archive/tasks/260115_tech_debt/backend_sync](./archive/tasks/260115_tech_debt/backend_sync/)         | Sync tests with schema changes                       |
| Frontend Type Safety           | Medium     | [archive/tasks/260115_tech_debt/frontend_type_safety](./archive/tasks/260115_tech_debt/frontend_type_safety/) | Audit and replace `as any` usage                     |
| Schema Alignment (is_reusable) | Easy       | [archive/tasks/260115_tech_debt/schema_alignment](./archive/tasks/260115_tech_debt/schema_alignment/) | Add is_reusable to ResourceDefinition                |
| Deck Config UX & Validation    | Medium     | [archive/tasks/260115_tech_debt/deck_config_ux](./archive/tasks/260115_tech_debt/deck_config_ux/)     | Validation, Vantage deck, and UX improvements        |
| Missing Production Docs        | Easy       | [archive/tasks/260115_tech_debt/docs_stability](./archive/tasks/260115_tech_debt/docs_stability/)     | Silence 404 snackbar and add missing docs            |
| E2E Data Seeding               | Medium     | [archive/tasks/260115_tech_debt/e2e_data_seeding](./archive/tasks/260115_tech_debt/e2e_data_seeding/) | Fix chart test seeding in browser mode               |

### UI/UX Implementation (from Redesign Artifacts)

| Item                           | Difficulty | Backlog                                                       | Description                                          |
|--------------------------------|------------|---------------------------------------------------------------|------------------------------------------------------|
| (None currently)               | -          | -                                                             | All identified redesigns started/completed           |

### Hardware Validation (Required for Alpha)

| Item                        | Difficulty | Backlog                              | Description                                     |
|-----------------------------|------------|--------------------------------------|-------------------------------------------------|
| Hardware Discovery          | Hard       | [hardware.md](./backlog/hardware.md) | WebSerial/WebUSB device enumeration in browser  |
| Connection Persistence      | Medium     | [hardware.md](./backlog/hardware.md) | Connections persist across sessions             |
| Plate Reader Validation     | Medium     | [hardware.md](./backlog/hardware.md) | Validate plate reader (may need debugging)      |
| Hamilton Starlet Validation | Hard       | [hardware.md](./backlog/hardware.md) | Validate with Hamilton hardware                 |
| Frontend Protocol Execution | Hard       | [hardware.md](./backlog/hardware.md) | Full protocol execution from browser UI (Execute ✅, Pause/Resume ❌, Cancel 🔄) |
| Playground Hardware         | Hard       | [hardware.md](./backlog/hardware.md) | Interactive hardware control from playground    |

---

## P3 - Medium Priority (Should Have for Alpha)

### State & Monitoring

| Item                       | Difficulty | Backlog                                                       | Description                                          |
|----------------------------|------------|---------------------------------------------------------------|------------------------------------------------------|
| Maintenance Tracking Tests | Medium     | [testing.md](./backlog/testing.md)                            | Test maintenance system                              |

### Agentic Infrastructure

| Item                   | Difficulty | Description                                                          |
|------------------------|------------|----------------------------------------------------------------------|
| Agentic Workflow Skill | Medium     | Implement multi-stage (Inspect -> Plan -> Exec) development workflow |

---

## P4 - Low Priority (Post-Alpha / Beta)

| Item                       | Difficulty | Description                                           |
|----------------------------|------------|-------------------------------------------------------|
| Production Mode Validation | Hard       | Document what's needed for full production validation |

---

---

## Completed Items

| Item                                                | Priority | Date       | Description                                                          |
|-----------------------------------------------------|----------|------------|----------------------------------------------------------------------|
| [Batch 260115 Review](./archive/BATCH_260115_SUMMARY.md) | -        | 2026-01-15 | Consolidated summary of archived backlog items                       |
| [Historical Items (Jan 2026)](./archive/COMPLETED_ITEMS_ARCHIVE_JAN_2026.md) | -        | 2026-01-12 | Consolidated archive of previous completions                         |
| Model Unification (SQLModel)                        | P2       | 2026-01-13 | Massive refactor to unified SQLModel domain models                   |
| [Frontend Schema Sync](./archive/backlog/frontend_schema_sync.md) | P1 | 2026-01-13 | Aligned frontend with SQLModel backend                               |
| Monitor State & Parameter Display                   | P2       | 2026-01-13 | Implemented agnostic state diffing and user-friendly parameter viewer |
| Assets View Controls                                | P2       | 2026-01-13 | Implemented unified `ViewControlsComponent`                          |
| Asset Filtering / Registry UI Redesign              | P1/P2    | 2026-01-13 | Standardized filtering and resolved browser-mode registry errors     |
| Add Asset Dialog Unification                        | P2       | 2026-01-13 | Unified 'Add Machine' and 'Add Resource' flow                        |
| Realistic Simulated Data Visualization              | P2       | 2026-01-14 | Refactored DataViz to use persistent SQLite data                     |
| Documentation Fixes (404/Mermaid)                   | P1/P2    | 2026-01-14 | Resolved 404 links, added Mermaid rendering                          |
| Protocol Loading (Browser Mode)                     | P1       | 2026-01-14 | Fixed protocol loading in browser mode                               |
| Tutorial UI & State Fixes                           | P2       | 2026-01-14 | Audited tutorial accuracy and updated Settings UI                    |
| Quick Add Autocomplete                              | P2       | 2026-01-14 | Implemented autocomplete in add dialog                               |
| Playground Theming Quick Wins                       | P3       | 2026-01-14 | Standardized stepper, chip sizes, and loading skeletons              |
| Workcell UX Planning                                | P2       | 2026-01-14 | Completed comprehensive UX audit and redesign plan                   |
| Inventory/Asset Selector Design                     | P2       | 2026-01-14 | Planned unification of playground inventory and protocol asset selection |
| Spatial View UX Analysis                             | P3       | 2026-01-14 | Analyzed purpose and value of Spatial View                           |
| FilterChip Deprecation (A-05)                       | P2       | 2026-01-14 | Replaced `FilterChipComponent` with `PraxisSelect`                   |
| RunProtocol Fix                                     | P2       | 2026-01-14 | Fixed critical `@Component` decorator error in `RunProtocolComponent` |
| Well Selector Performance Optimization (E-02)       | P2       | 2026-01-14 | Batched selection updates to improve click+drag performance          |
| Simulation Frontend Consolidation                   | P2       | 2026-01-14 | Consolidated simulated backends into single definitions per type     |
| Breadcrumb Removal (C-01)                           | P2       | 2026-01-14 | Removed global breadcrumb bar and associated service/component       |
| Well Arguments Cleanup (E-01)                       | P2       | 2026-01-14 | Filtered well parameters from configuration step and added summary   |
| Browser Mode Database Sync                          | P1       | 2026-01-15 | Refactored BrowserMockRouter to use SQLite db, generated full prebuilt DB |
| Protocol Library ViewControls                       | P2       | 2026-01-15 | Adopted ViewControls for Protocol Library filtering/sorting          |
| Playground Theme Sync (D-02)                        | P2       | 2026-01-15 | Resolved theme race condition by delaying iframe mount until AfterViewInit |
| Playground Kernel Load & Loading Overlay (D-01/D-03) | P1/P2    | 2026-01-15 | Implemented loading state with ready signal and timeout fallback |
| WebSerial/WebUSB Shims Fix (D-04)                   | P1       | 2026-01-15 | Injected hardware shims into builtins via async bootstrap          |
| Installation Docs Split (F-01)                      | P3       | 2026-01-15 | Created dedicated guides for Browser, Production, and Lite modes   |
| Deck View Implementation (J-01)                  | P2       | 2026-01-15 | **Tentative Pass** - Logic/Persistence done, awaiting improved Workcell view |
| Workcell View Service (K-02)                  | P1       | 2026-01-15 | Implemented `WorkcellViewService` and extended `AssetService` |
| Workcell Dashboard Container (P1.1)           | P2       | 2026-01-15 | Implemented main dashboard shell with responsive layout and view modes |
| Workcell Hierarchical Explorer (P1.2)        | P2       | 2026-01-15 | Implemented hierarchical tree-based sidebar with search and persistence |
| Machine Status Badge (K-05)                   | P2       | 2026-01-15 | Implemented reusable status badge with pulse animations and state source tags |
| Machine Card Component (K-06)                 | P2       | 2026-01-15 | Implemented main machine status cards with mini-deck view and progress bars |
| Machine Focus View (K-07)                     | P2       | 2026-01-15 | Implemented detailed single-machine view with protocol progress and resource inspector |
| Simulated Deck States (K-08)                  | P2       | 2026-01-15 | Connected DeckView to live/simulated state with liquid and tip visualization |
| Deck State Indicator (K-09)                   | P3       | 2026-01-15 | Implemented source indicator badge (Live/Sim/Offline) for focus views |
| Workcell Polish & Animations (K-10)           | P3       | 2026-01-15 | Applied glassmorphism, animations, and micro-interactions |
| Workcell Route Migration (K-11)               | P3       | 2026-01-15 | Migrated /visualizer to /workcell and updated navigation |
| Machine Simulation Architecture Refactor      | P2       | 2026-01-15 | Refactored simulation to use Factory Pattern and runtime configuration |
| View Controls Filter Chips (FE-03)           | P2       | 2026-01-16 | Unified filter chip bar with icons and tooltips                      |
| State Inspection Backend                            | P2       | 2026-01-20 | Post-run "time travel" for backend executions - COMPLETE with state diffing, transformation layer, and API endpoint |
| Simulation Machine Visibility                       | P2       | 2026-01-20 | Frontend-only sim until instantiation - COMPLETE with is_simulation_override and is_simulated_frontend flags |

---

## Summary

| Priority | Count | Focus                                |
|----------|-------|--------------------------------------|
| **P1**   | 0     | All top blockers resolved            |
| **P2**   | 13    | Features + Tech Debt + Hardware      |
| **P3**   | 2     | Maintenance & Agentic Workflow       |
| **P4**   | 1     | Long-term validation                 |

**Total Active Items**: 16
