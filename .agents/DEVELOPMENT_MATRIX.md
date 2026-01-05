# Praxis Development Matrix

**Last Updated**: 2026-01-05 (State Simulation Completed)
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
| **Add Resource Not Working** | P1 | M | [browser_mode_issues::2](./backlog/browser_mode_issues.md) | Cannot add resources in browser mode - needs investigation |
| **DB Sync Issue** | P1 | L | [browser_mode_issues::9](./backlog/browser_mode_issues.md) | Root cause for multiple issues |
| **Restore Asset Selection Step** | P1 | M | [run_protocol_workflow](./backlog/run_protocol_workflow.md) | REGRESSION: Re-enable resource selection in run workflow |

---

## P2 - High Priority (New Feature Development)

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| **REPL → JupyterLite Migration** | P2 | XL | [repl_jupyterlite](./backlog/repl_jupyterlite.md) | Replace xterm.js REPL with JupyterLite, preload assets |
| **Hardware Discovery Menu Restoration** | P2 | M | [hardware_discovery_menu](./backlog/hardware_discovery_menu.md) | USB icon buttons, restore discovery menu, exclude simulator |
| ~~**State Snapshot Tracing**~~ | ✅ | XL | [state_snapshot_tracing](./backlog/state_snapshot_tracing.md) | ✅ Completed 2026-01-05 |

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
| **Resource Inventory Filters** | P3 | M | [ui_visual_tweaks](./backlog/ui_visual_tweaks.md) | Add filter chips to Resources tab (match Machines tab pattern) |
| **UI Visual Tweaks** | P3 | S | [ui_visual_tweaks](./backlog/ui_visual_tweaks.md) | Spacing fixes in Registry/Machine tabs |
| **Protocol Inference "Sharp Bits" Docs** | P3 | M | [docs](./backlog/docs.md) | Documentation for protocol inference edge cases |
| **Spatial View Filters** | P3 | M | [asset_management::Spatial View](./backlog/asset_management.md) | Sort/Filter by location |
| **Pre-Merge Finalization** | P3 | M | [pre_merge_finalization](./backlog/pre_merge_finalization.md) | Archive docs, cleanup files |

---

## Completed (Archive: 2026-01-04)

### Browser Mode Stabilization ✅ (2026-01-02 - 2026-01-03)

- Asset Manager rendering, Start Execution, Data Views, Hardware Discovery Button
- OT2 Slot Type rendering, Execution Filters, API Docs (static generation)
- Deck Display consistency, Machine Input forms, Machine Type config
- Button Selector checkmarks, ty Error Deletions verification

### REPL Enhancements ✅

- Variables Sidebar, Menu Bar, Save to Protocol, Completion Popup
- Light/Dark Mode theming, Full Python tracebacks, Easy Add Assets
- Protocol Editor disabled state with "Coming Soon" tooltip

### UI/UX Polish ✅

- Loading Skeletons, Navigation Breadcrumbs, Light Theme, Command Palette
- Execution Filters horizontal flex container

### Core Backend ✅

- Protocol Decorator Data Views, Deck Config, Cached PLR Definitions
- Protocol Computation Graph, Parental Resource Inference, Container Type Extraction

### Hardware Infrastructure ✅

- mDNS Discovery, Connection Persistence, SqliteKeyValueStore, Production Tunneling

### Guided Deck Setup ✅

- Wizard components, Drag & Drop, Slot-based rendering
- Machine Selection Step, Deck Setup inline (not dialog)

### Maintenance System ✅

- Schema (Alembic migration), Per-asset toggle, Maintenance Badges

### Visualizations ✅

- Summary Card Sparklines, Execution Monitor Timeline

### Visual Index Selection ✅

- Interactive Grid Selection Component (Wells, Tips)
- Linked Argument Synchronization (`LinkedSelectorService`)
- Backend Type Inference for Well/TipSpot parameters
- Formly Integration & Protocol Metadata Updates

### State Simulation & Failure Detection ✅ (2026-01-05)

- Hierarchical state simulation (Boolean → Symbolic → Exact)
- 40+ PLR method contracts (LiquidHandler, PlateReader, HeaterShaker, etc.)
- StatefulTracedMachine with precondition checking & effect application
- BoundsAnalyzer for loop iteration counts
- FailureModeDetector with early pruning
- 49 comprehensive tests

---

## Summary by Priority

| Priority | Count | Description |
|----------|-------|-------------|
| **P1** | 3 | Remaining browser mode issues (Add Resource, DB Sync, Asset Selection) |
| **P2** | 6 | New features + code quality + testing (State Simulation completed) |
| **P3** | 5 | UI polish, filters, documentation, finalization |

**Total Active Items**: 14
