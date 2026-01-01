# Praxis Development Roadmap

**Last Updated**: 2026-01-01
**Current Phase**: Post-MVP Polish & Merge Preparation

---

## Executive Summary

The `angular_refactor` branch has achieved MVP status for all major features. Remaining work focuses on:

1. **UI/UX Polish** - Production-ready experience
2. **Full Implementations** - Completing VMP (stub) features
3. **Technical Debt** - Critical backend issues
4. **Pre-Merge Cleanup** - Code quality (Linting, Typing, DRY)

> 📊 **See [DEVELOPMENT_MATRIX.md](./DEVELOPMENT_MATRIX.md)** for a complete list of all **105 remaining items** with priority (P1-P4) and difficulty (S/M/L/XL) ratings.

---

## Priority 1: Critical (Must Fix Before Merge)

### Technical Debt - Backend

| Item | Description | Backlog |
|------|-------------|---------|
| ~~**Persistent Reservations**~~ | ~~Asset reservations are in-memory; lost on restart~~ | ✅ Complete |
| **Scheduler Coverage** | ~22% coverage, tests need DB running | [backend.md](./backlog/backend.md) |

### UI/UX Bugs

| Item | Description | Backlog |
|------|-------------|---------|
| ~~**Purple Buttons/Toggles**~~ | ~~Some buttons purple instead of pink in light mode~~ | ✅ Resolved |
| ~~**Asset Dashboard Scrolling**~~ | ~~Scrolling buggy within asset components~~ | ✅ Resolved |
| ~~**Protocol Setup Scrolling**~~ | ~~Parameter/deck selection won't scroll~~ | ✅ Resolved |
| ~~**Run Protocol Rendering**~~ | ~~Blank screen on downstream steps~~ | ✅ Resolved |
| ~~**Form Field Visual Bug**~~ | ~~Vertical line/notch in mat-form-field outlines~~ | ✅ Resolved |
| ~~**Command Palette Selection**~~ | ~~Up/Down selection not visually responsive~~ | ✅ Resolved |
| ~~**Light Theme Buttons**~~ | ~~Rendering anomalies in light mode~~ | ✅ Resolved |
| ~~**Deck Resource Adding**~~ | ~~Buggy behavior when adding resources to deck~~ | ✅ Resolved |

---

## Priority 2: High (MVP → Full Implementation)

### REPL Polish

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| Completion Popup UI | ✅ Done | Replaced inline columns with floating popup (Needs manual polish) | [repl.md](./backlog/repl.md) |
| Signature Help | ✅ Done | Show function params on `(` key | [repl_autocompletion.md](./backlog/repl_autocompletion.md) |
| Auto-scroll | ⚠️ Partial | Terminal scrolls but alignment improved | [repl.md](./backlog/repl.md) |
| Split Streams | ✅ Done | Distinguish stdout/stderr/return | [repl.md](./backlog/repl.md) |
| **PLR Tooling Integration** | ⏳ Pending | Deep PLR integration (autofill, IO shim) | [repl.md](./backlog/repl.md) |

### Capability Configuration

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| **Dynamic Form Generation** | ✅ Done | Conditional visibility, validation, accessibility | [dynamic_form_generation.md](./backlog/dynamic_form_generation.md) |

### Protocol Inspection

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| Requirements Integration | ✅ Done | Link ProtocolRequirementExtractor to discovery | [protocol_inspection.md](./backlog/protocol_inspection.md) |
| ORM Updates | ✅ Done | Add `inferred_requirements` to protocol definitions | [protocol_inspection.md](./backlog/protocol_inspection.md) |

### Documentation & Infrastructure

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| Mermaid Theming | ✅ Done | Consistent Light/Dark mode diagrams | [docs.md](./backlog/docs.md) |
| API Documentation | ⏳ Pending | Auto-generated API docs | [docs.md](./backlog/docs.md) |
| Code Quality | ⏳ Pending | Ruff, Ty, Frontend Linting, DRY | [cleanup.md](./backlog/cleanup.md) |

### Execution Monitor

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| Sidebar Access | ✅ Done | Add Monitor to sidebar navigation | [execution_monitor.md](./backlog/execution_monitor.md) |
| Active Runs Panel | ✅ Done | Real-time view of running protocols | [execution_monitor.md](./backlog/execution_monitor.md) |
| Run History Table | ✅ Done | Paginated history with filtering | [execution_monitor.md](./backlog/execution_monitor.md) |
| Run Detail View | ✅ Done | Detailed view with logs and timeline | [execution_monitor.md](./backlog/execution_monitor.md) |

### Deck Visualizer

| Item | Status | Description | Backlog |
|------|--------|-------------|---------|
| Rails/Carriers/Slots | ⏳ Pending | Semantic rendering of deck structure | [deck_view.md](./backlog/deck_view.md) |
| Tip/Well Status | ⏳ Pending | Individual item visualization | [deck_view.md](./backlog/deck_view.md) |
| **Guided Deck Setup** | ⏳ Pending | Interactive step-by-step physical setup guide | [deck_view.md](./backlog/deck_view.md) |

---

## Priority 3: Medium (Post-Merge Enhancements)

### Backend

| Item | Description | Backlog |
|------|-------------|---------|
| Service Layer Coverage | Increase coverage on deck.py, protocol_definition.py, user.py | [backend.md](./backlog/backend.md) |
| Protocol Decorator Enhancements | Parameterized data views | [backend.md](./backlog/backend.md) |
| User-Specified Deck | Support explicit deck layout in protocol | [backend.md](./backlog/backend.md) |
| **Registry vs Inventory** | Split Definition vs Physical Instance | [asset_management.md](./backlog/asset_management.md) |
| **Full VMP Implementation** | Scheduler, Persistent Reservations, mDNS | [backend.md](./backlog/backend.md) |

### Frontend

| Item | Description | Backlog |
|------|-------------|---------|
| Data Visualization Dashboard | Dedicated route with protocol selector | [ui-ux.md](./backlog/ui-ux.md) |
| Navigation Breadcrumbs | Deep navigation review | [ui-ux.md](./backlog/ui-ux.md) |
| Drag & Drop Deck | Drag resources into deck slots | [deck_view.md](./backlog/deck_view.md) |

### Modes & Deployment

| Item | Description | Backlog |
|------|-------------|---------|
| **Enhanced SqliteService** | Full browser backend with PLR-preloaded DB, TypeScript service layer | [browser_sqlite_schema_sync.md](./backlog/browser_sqlite_schema_sync.md) |
| **Browser DB with PLR Data** | Pre-built .db with all PLR machines, resources, decks | [browser_sqlite_schema_sync.md](./backlog/browser_sqlite_schema_sync.md) |
| E2E Hardware Test | Test WebBridgeIO with real hardware | [modes_and_deployment.md](./backlog/modes_and_deployment.md) |
| Production Tunneling UI | Help text for exposing local hardware | [modes_and_deployment.md](./backlog/modes_and_deployment.md) |

---

## Priority 4: Low (Future)

### Advanced Features

| Item | Description | Backlog |
|------|-------------|---------|
| Protocol DAG Extraction | Call graph and resource flow analysis | [protocol_inspection.md](./backlog/protocol_inspection.md) |
| Resource Constraint Matching | Match protocol needs to inventory | [capability_tracking.md](./backlog/capability_tracking.md) |
| Advanced Scheduling | Discrete event simulation, multi-workcell | [backend.md](./backlog/backend.md) |
| Spatial Workcell View | Physical layout of workcells in space | [ui-ux.md](./backlog/ui-ux.md) |

### Pre-Merge Cleanup

| Item | Description | Backlog |
|------|-------------|---------|
| Naming Consistency | "Praxis" not "PyLabPraxis", "machines" not "instruments" | [cleanup.md](./backlog/cleanup.md) |
| Remove Dead Code | Unused imports, commented blocks | [cleanup.md](./backlog/cleanup.md) |
| Console.log Cleanup | Remove development artifacts | [cleanup.md](./backlog/cleanup.md) |

---

## Completed Features ✅

### Core Infrastructure

- [x] Angular 21 + Material 3 + Tailwind architecture
- [x] FastAPI backend with SQLAlchemy + PostgreSQL
- [x] WebSocket log streaming
- [x] Keycloak authentication (Production mode)

### PLR Integration

- [x] LibCST-based static analysis (21 frontends, 70 backends, 15 machine types)
- [x] Protocol discovery with ProtocolFunctionVisitor
- [x] ProtocolRequirementExtractor for capability inference
- [x] Machine capability schemas (15 types)

### Browser Mode

- [x] Pyodide runtime with WebWorker
- [x] WebBridgeIO for hardware IO shimming
- [x] LocalStorage persistence adapter
- [x] ModeService with no-login flow
- [x] CDN package loading (micropip)

### Visualizer

- [x] Workcell Visualizer architecture
- [x] PLR theming (all resource types)
- [x] Dark/light theme support
- [x] Configurable deck windows

### REPL

- [x] xterm.js terminal UI
- [x] Jedi-based autocompletion (MVP)
- [x] Command history (Up/Down)
- [x] Ctrl+L clear

### Protocol Wizard

- [x] Deck Setup with FQN-based matching
- [x] Autofill indicators
- [x] Capability matching UI
- [x] Machine selection step
- [ ] **Wizard State Persistence** - Form hydration on refresh | [protocol_execution.md](./backlog/protocol_execution.md)

---

## Branch Strategy

- **Current Branch**: `angular_refactor`
- **Target**: Merge into `main` after Priority 1 items resolved
- **Status**: MVP complete, polish phase

---

## Backlog Index

| Document | Focus |
|----------|-------|
| [asset_management.md](./backlog/asset_management.md) | PLR inspection, discovery, bulk operations |
| [backend.md](./backlog/backend.md) | Services, APIs, execution |
| [browser_sqlite_schema_sync.md](./backlog/browser_sqlite_schema_sync.md) | Browser SQLite with PLR data, schema codegen |
| [capability_tracking.md](./backlog/capability_tracking.md) | Machine capabilities, user config, matching |
| [cleanup.md](./backlog/cleanup.md) | Code quality, naming, pre-merge |
| [deck_view.md](./backlog/deck_view.md) | Deck visualizer structure, interaction |
| [docs.md](./backlog/docs.md) | Documentation, guides, tutorials |
| [dynamic_form_generation.md](./backlog/dynamic_form_generation.md) | Capability config forms |
| [execution_monitor.md](./backlog/execution_monitor.md) | Run monitoring, history, filtering |
| [modes_and_deployment.md](./backlog/modes_and_deployment.md) | Browser/Lite/Production modes |
| [protocol_inspection.md](./backlog/protocol_inspection.md) | LibCST protocol analysis |
| [repl.md](./backlog/repl.md) | REPL features, UI polish |
| [repl_autocompletion.md](./backlog/repl_autocompletion.md) | Jedi completion phases |
| [ui-ux.md](./backlog/ui-ux.md) | General UI/UX items |
| [TECHNICAL_DEBT.md](./TECHNICAL_DEBT.md) | Known debt items |

---

*For archived items, see [archive/](./archive/).*
