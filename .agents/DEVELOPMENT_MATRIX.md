# Praxis Development Matrix

**Last Updated**: 2026-01-15 (Batch 260115 Planning)
**Purpose**: Current iteration work items with priority and difficulty ratings.
**Current Batch**: [260115_dev_cycle](prompts/260115_dev_cycle/README.md)

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
| WebSerial "NameError" | Medium     | [playground.md](./backlog/playground.md) | Top blocker: WebSerial not correctly defined in Pyodide/REPL builtins |

---

## P2 - High Priority (Alpha Quality)

### UI/UX Implementation (from Redesign Artifacts)

| Item                           | Difficulty | Backlog                                                       | Description                                          |
|--------------------------------|------------|---------------------------------------------------------------|------------------------------------------------------|
| Workcell Hierarchical Explorer | Hard       | [workcell_ux_redesign.md](./artifacts/workcell_ux_redesign.md) | Implement tree-based sidebar and status cards        |
| Unified Asset Selector         | Medium     | [inventory_ux_design.md](./artifacts/inventory_ux_design.md)   | Implement shared browsing for Playground and Protocol |

### Hardware Validation (Required for Alpha)

| Item                        | Difficulty | Backlog                              | Description                                     |
|-----------------------------|------------|--------------------------------------|-------------------------------------------------|
| Hardware Discovery          | Hard       | [hardware.md](./backlog/hardware.md) | WebSerial/WebUSB device enumeration in browser  |
| Connection Persistence      | Medium     | [hardware.md](./backlog/hardware.md) | Connections persist across sessions             |
| Plate Reader Validation     | Medium     | [hardware.md](./backlog/hardware.md) | Validate plate reader (may need debugging)      |
| Hamilton Starlet Validation | Hard       | [hardware.md](./backlog/hardware.md) | Validate with Hamilton hardware                 |
| Frontend Protocol Execution | Hard       | [hardware.md](./backlog/hardware.md) | Full protocol execution from browser UI         |
| Playground Hardware         | Hard       | [hardware.md](./backlog/hardware.md) | Interactive hardware control from playground    |

---

## P3 - Medium Priority (Should Have for Alpha)

### State & Monitoring

| Item                       | Difficulty | Backlog                                                       | Description                                          |
|----------------------------|------------|---------------------------------------------------------------|------------------------------------------------------|
| Live Deck State Overlays   | Medium     | [workcell_ux_redesign.md](./artifacts/workcell_ux_redesign.md) | Render liquid and tips on deck view from `plr_state` |
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
| Deck View Implementation (J-01)                    | P2       | 2026-01-15 | **Tentative Pass** - Logic/Persistence done, awaiting improved Workcell view |

---

## Summary

| Priority | Count | Focus                                |
|----------|-------|--------------------------------------|
| **P1**   | 1     | Alpha blockers (WebSerial)           |
| **P2**   | 8     | Implementation & Hardware validation |
| **P3**   | 3     | UI Enhancements & Maintenance        |
| **P4**   | 1     | Long-term validation                 |

**Total Active Items**: 13
