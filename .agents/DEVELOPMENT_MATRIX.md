# Praxis Development Matrix

**Last Updated**: 2026-01-01  
**Purpose**: Consolidated view of all remaining work items with priority and difficulty ratings.

---

## Priority Legend

| Priority | Description |
|----------|-------------|
| **P1** | Critical - Must fix before merge |
| **P2** | High - MVP → Full implementation |
| **P3** | Medium - Post-merge enhancements |
| **P4** | Low - Future features |

## Difficulty Legend

| Difficulty | Estimated Effort |
|------------|------------------|
| **S** | Small (< 2 hours) |
| **M** | Medium (2-8 hours) |
| **L** | Large (1-3 days) |
| **XL** | Extra Large (3+ days) |

## Status Indicators

| Indicator | Meaning |
|-----------|---------|
| ✅ | Complete |
| ⚠️ | Partial implementation exists |
| ⏳ | Deferred/Blocked |
| 🔮 | Wishlist (future, user-demand driven) |
| ~~strikethrough~~ | Resolved or no longer applicable |

---

## UI/UX

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| ~~Command Palette Selection~~ | ~~P1~~ | ~~S~~ | - | ✅ Resolved 2025-12-31 |
| ~~Light Theme Button Rendering~~ | ~~P1~~ | ~~M~~ | - | ✅ Resolved 2025-12-31 |
| ~~Purple Buttons/Toggles (Light Mode)~~ | ~~P1~~ | ~~S~~ | - | ✅ Resolved 2026-01-01 |
| ~~Asset Dashboard Scrolling~~ | ~~P1~~ | ~~M~~ | - | ✅ Resolved 2026-01-01 |
| ~~Parameter/Deck Selection Scrolling~~ | ~~P1~~ | ~~M~~ | - | ✅ Resolved 2026-01-01 |
| ~~mat-form-field Visual Bug~~ | ~~P1~~ | ~~S~~ | - | ✅ Resolved 2026-01-01 |
| ~~Run Protocol Rendering Fix~~ | ~~P1~~ | ~~M~~ | - | ✅ Resolved 2026-01-01 |
| ~~Stepper Label Responsiveness~~ | ~~P2~~ | ~~S~~ | - | ✅ Resolved 2026-01-01 |
| ~~Light Theme Color Tuning~~ | ~~P2~~ | ~~M~~ | - | ✅ Resolved 2025-12-31 |
| ~~Filter Search Bar Line Bug~~ | ~~P2~~ | ~~S~~ | - | ✅ Resolved 2025-12-31 |
| Activity History Linking | P2 | M | [ui-ux.md](./backlog/ui-ux.md) | Link to Execution Monitor for that protocol |
| ~~Remove Quick Links Section~~ | ~~P2~~ | ~~S~~ | - | ✅ Resolved 2025-12-31 |
| REPL Completion Popup UI | P2 | L | [repl.md](./backlog/repl.md) | ⚠️ Partial: Implemented but verify manual completion |
| REPL Signature Help | P2 | M | [repl_autocompletion.md](./backlog/repl_autocompletion.md) | ✅ Resolved 2026-01-01 |
| ~~REPL Auto-scroll~~ | ~~P2~~ | ~~S~~ | - | ✅ Resolved 2025-12-31 |
| ~~REPL Split Streams~~ | ~~P2~~ | ~~M~~ | - | ✅ Resolved 2026-01-01 |
| **PLR Tooling & IO Shim** | P2 | XL | [repl.md](./backlog/repl.md) | Integrate PLR-specific tooling and verify WebBridgeIO |
| Gentle Gradient Background | P3 | M | [ui-ux.md](./backlog/ui-ux.md) | Subtle gradient for light/dark modes |
| Loading Skeletons | P3 | M | [ui-ux.md](./backlog/ui-ux.md) | Replace spinners with skeleton loaders |
| Command Palette Spacing | P3 | S | [ui-ux.md](./backlog/ui-ux.md) | Keyboard shortcuts + tags spacing |
| Navigation Breadcrumbs | P3 | M | [ui-ux.md](./backlog/ui-ux.md) | ⚠️ Partial: `LocationBreadcrumbComponent` exists |
| Wizard State Persistence & Hydration | P2 | M | [protocol_execution.md](./backlog/protocol_execution.md) | Persist protocol setup forms in LocalStorage |
| ~~Spatial Workcell View~~ | - | - | - | 🔮 *Wishlist* - Defer until user demand |

---

## Deck Visualizer

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| ~~Deck Resource Adding Bug~~ | ~~P1~~ | ~~M~~ | - | ✅ Resolved 2025-12-31 |
| Slot Inference for Deck Rendering | P2 | L | [deck_view.md](./backlog/deck_view.md) | Infer slot types for deck and protocol setup |
| Carrier Inference (Minimum Needed) | P2 | L | [deck_view.md](./backlog/deck_view.md) | Auto-determine minimum carriers for protocol |
| Enhanced Guided Deck Setup | P2 | XL | [deck_view.md](./backlog/deck_view.md) | Step-by-step: "Slide carriers into rails", z-axis ordering, skippable |
| Accurate Rails Rendering | P2 | L | [deck_view.md](./backlog/deck_view.md) | ⚠️ Partial: Basic rails exist, need hardware-spec positions |
| Carriers Visualization | P2 | M | [deck_view.md](./backlog/deck_view.md) | ⚠️ Partial: CSS styling exists |
| Slots/Sites Rendering | P2 | L | [deck_view.md](./backlog/deck_view.md) | Empty/full slot states, visual snapping |
| Tip Status Visualization | P2 | M | [deck_view.md](./backlog/deck_view.md) | ⚠️ Partial: `has_tip` supported |
| Well Status Visualization | P2 | M | [deck_view.md](./backlog/deck_view.md) | ⚠️ Partial: `has_liquid` with volume |
| Itemized Resource Spacing | P2 | M | [deck_view.md](./backlog/deck_view.md) | Proper spacing/rendering in deck display |
| Drag & Drop Resource Placement | P3 | L | [deck_view.md](./backlog/deck_view.md) | Drag labware into slots |
| Hover Details | P3 | S | [deck_view.md](./backlog/deck_view.md) | ⚠️ Partial: Title tooltip exists |
| Resource Properties Inspector | P3 | M | [deck_view.md](./backlog/deck_view.md) | Click to inspect well data |
| Deck Model (Rails/Slots) | P3 | M | [deck_view.md](./backlog/deck_view.md) | Update PlrDeckData model |
| State Sync Optimization | P4 | M | [deck_view.md](./backlog/deck_view.md) | Bitmask vs 96 objects for wells |

---

## Execution Monitor

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| ~~Sidebar Access~~ | ~~P2~~ | ~~S~~ | - | ✅ Resolved 2025-12-31 |
| ~~Active Runs Panel~~ | ~~P2~~ | ~~M~~ | - | ✅ Resolved 2026-01-01 |
| ~~Run History Table~~ | ~~P2~~ | ~~L~~ | - | ✅ Resolved 2026-01-01 |
| Run Filters Component | P2 | M | [execution_monitor.md](./backlog/execution_monitor.md) | Filter by protocol/status/date |
| ~~Run Detail View~~ | ~~P2~~ | ~~L~~ | - | ✅ Resolved 2026-01-01 |
| Filter Runs by Protocol (Data Viz) | P3 | M | [execution_monitor.md](./backlog/execution_monitor.md) | Multi-select filter like protocol picker |
| Run Timeline Visualization | P3 | L | [execution_monitor.md](./backlog/execution_monitor.md) | Visual phase representation |
| Summary Statistics | P3 | M | [execution_monitor.md](./backlog/execution_monitor.md) | Runs/day, success rate, avg duration |

---

## Backend

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| ~~Scheduler Test Coverage~~ | ~~P1~~ | ~~L~~ | - | ✅ Resolved 2026-01-01 |
| Browser SQL with Preloaded DB | P2 | L | [modes_and_deployment.md](./backlog/modes_and_deployment.md) | SQL.js with .db file (caps, all except scheduling) |
| Dual DB Testing (SQLite + PostgreSQL) | P2 | M | [backend.md](./backlog/backend.md) | Run test suite against both databases |
| POST /resources/ API Fix | P2 | M | [TECHNICAL_DEBT.md](./TECHNICAL_DEBT.md) | Endpoint returns 500 errors |
| ~~Service Layer Coverage (user.py)~~ | ~~P3~~ | ~~M~~ | - | ✅ Complete: 25 tests, 478 lines |
| ~~Service Layer Coverage (deck.py)~~ | ~~P3~~ | ~~M~~ | - | ✅ Complete: 15 tests, 303 lines |
| ~~Service Layer Coverage (protocol_definition.py)~~ | ~~P3~~ | ~~M~~ | - | ✅ Complete: 8 tests, 238 lines |
| Hardware Connection UI Polish | P3 | M | [backend.md](./backlog/backend.md) | Complete connection component |
| Hardware Connection Redis State | P3 | L | [backend.md](./backlog/backend.md) | Redis-backed connection state |
| Full REPL WebSocket (Production) | P3 | L | [backend.md](./backlog/backend.md) | Complete production mode REPL |
| Protocol Decorator Enhancements | P3 | M | [backend.md](./backlog/backend.md) | Parameterized data views |
| User-Specified Deck Configuration | P3 | L | [backend.md](./backlog/backend.md) | Override auto-layout |
| Hardware Scanning (mDNS) | P3 | L | [backend.md](./backlog/backend.md) | ⚠️ Stubbed: returns empty list |
| Cached PLR Definitions Frontend | P3 | L | [backend.md](./backlog/backend.md) | DeckGeneratorService uses real dims |
| Disable Add Definition Pre-Sync | P3 | S | [backend.md](./backlog/backend.md) | Disable button until sync complete |
| Consumables Auto-Assignment | P3 | M | [TECHNICAL_DEBT.md](./TECHNICAL_DEBT.md) | Smarter resource selection logic |
| User Permissions for Runs | P4 | M | [TECHNICAL_DEBT.md](./TECHNICAL_DEBT.md) | Admin vs regular user run management |
| Advanced Scheduling (DES) | P4 | XL | [backend.md](./backlog/backend.md) | Discrete event simulation |
| Multi-Workcell Scheduling | P4 | XL | [backend.md](./backlog/backend.md) | Cross-workcell optimization |
| WebSerial Passthrough | P4 | L | [backend.md](./backlog/backend.md) | Remote client hardware access |
| Device Profiles | P4 | M | [backend.md](./backlog/backend.md) | Saved hardware configurations |

---

## Asset Management

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| Deck Setup Debugging | P2 | M | [asset_management.md](./backlog/asset_management.md) | Fix rendering issues in wizard |
| Machine Groupings (Inventory) | P3 | L | [asset_management.md](./backlog/asset_management.md) | PLR type hierarchy, location/capability chips, accordions |
| Machine Groupings (Registry) | P3 | L | [asset_management.md](./backlog/asset_management.md) | Collapsible by machine type, capability chips |
| Resource Groupings (Registry) | P3 | L | [asset_management.md](./backlog/asset_management.md) | Group by type/category with chips |
| Registry vs Inventory Split | P3 | L | [asset_management.md](./backlog/asset_management.md) | Definitions vs Physical Instances |
| Spatial Relationship View | P3 | L | [asset_management.md](./backlog/asset_management.md) | "What's where" spatial view |
| Context-Aware Add Dialogs | P3 | M | [asset_management.md](./backlog/asset_management.md) | Suggest compatible resources |
| Multi-Select Mode | P4 | M | [asset_management.md](./backlog/asset_management.md) | Floating action bar for bulk ops |
| Expert Mode Toggle | P4 | S | [asset_management.md](./backlog/asset_management.md) | Show FQNs, backends, drivers |
| Maintenance Scheduling UI | P4 | L | [asset_management.md](./backlog/asset_management.md) | Schedule machine maintenance |
| Inventory Alerts | P4 | M | [asset_management.md](./backlog/asset_management.md) | Low stock notifications |

---

## Capability & Protocol Inspection

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| Capability Matching Review | P3 | M | [capability_tracking.md](./backlog/capability_tracking.md) | Review all machine methods/capabilities |
| Call Graph Analysis | P4 | L | [protocol_inspection.md](./backlog/protocol_inspection.md) | DAG for protocol execution order |
| Resource Flow Analysis | P4 | L | [protocol_inspection.md](./backlog/protocol_inspection.md) | Track resource usage patterns |
| Protocol Validation (Static) | P4 | L | [protocol_inspection.md](./backlog/protocol_inspection.md) | Validate PLR types at parse time |
| Resource Constraint Matching | P4 | L | [capability_tracking.md](./backlog/capability_tracking.md) | Match protocol needs to inventory |

---

## REPL Enhancements

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| REPL PLR Environment Fix | P2 | L | [repl.md](./backlog/repl.md) | Execute PyLabRobot code (imports, basic calls) |
| REPL PLR Simulation Tests | P2 | M | [repl.md](./backlog/repl.md) | Test with simulation backend |
| REPL Machine Availability Display | P3 | M | [repl.md](./backlog/repl.md) | Show available machines in REPL |
| REPL Security Sandbox | P3 | L | [repl.md](./backlog/repl.md) | Restrict sys/os, secure enclosure |
| REPL Save to Protocol | P3 | L | [repl.md](./backlog/repl.md) | Export session as protocol file |
| REPL ARIA Toolbar/Menubar | P3 | M | [repl.md](./backlog/repl.md) | Angular ARIA patterns for accessibility |
| REPL Protocol Decorator Spec | P4 | M | [repl.md](./backlog/repl.md) | Specify decorator metadata from REPL |

---

## Modes & Deployment

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| Enhanced SqliteService | P2 | XL | [modes_and_deployment.md](./backlog/modes_and_deployment.md) | Full browser backend with real data (TypeScript service layer, schema parity) |
| E2E Hardware Test | P2 | M | [modes_and_deployment.md](./backlog/modes_and_deployment.md) | Test WebBridgeIO with real hardware |
| Browser-Only Add Machine Enforce | P3 | M | [modes_and_deployment.md](./backlog/modes_and_deployment.md) | Disable manual IP/Host in browser |
| Production Tunneling UI | P3 | M | [modes_and_deployment.md](./backlog/modes_and_deployment.md) | Help text for local hardware exposure |
| Mode Validation Docs | P3 | S | [modes_and_deployment.md](./backlog/modes_and_deployment.md) | Document each mode's constraints |

---

## Documentation

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| Mermaid Theming | P2 | M | [docs.md](./backlog/docs.md) | Light/dark mode diagram consistency |
| API Documentation (mkdocstrings) | P2 | L | [docs.md](./backlog/docs.md) | Auto-generated from docstrings |
| Demo Script Documentation | P2 | M | [docs.md](./backlog/docs.md) | Step-by-step demo walkthrough |
| WebSocket Protocol Documentation | P2 | M | [docs.md](./backlog/docs.md) | Detailed WS protocol docs |
| Frontend Architecture Diagrams | P3 | M | [docs.md](./backlog/docs.md) | Component architecture diagrams |
| ~~Deprecate Sphinx Config~~ | P3 | S | [docs.md](./backlog/docs.md) | ⚠️ 17 .rst files remain (moved to Cleanup) |
| Build Pipeline (CI/CD MkDocs) | P3 | M | [docs.md](./backlog/docs.md) | Automated doc builds |
| Audit PyLabPraxis → Praxis | P3 | M | [docs.md](./backlog/docs.md) | ⚠️ 32 refs in docs/ + CONTRIBUTING.md |
| ~~Protocol Authoring Guide~~ | ~~P3~~ | ~~L~~ | - | ✅ Complete: `docs/user-guide/protocols.md` (339 lines) |
| Deck Configuration Guide | P3 | M | [docs.md](./backlog/docs.md) | How to configure decks |
| ~~Contributing Guide~~ | ~~P3~~ | ~~M~~ | - | ✅ Complete: `CONTRIBUTING.md` exists (61 lines) |
| Local Development Setup | P3 | M | [docs.md](./backlog/docs.md) | Dev environment guide |
| "Hello World" Tutorial | P4 | L | [docs.md](./backlog/docs.md) | First protocol tutorial |
| Custom Machine Driver Tutorial | P4 | L | [docs.md](./backlog/docs.md) | Driver development guide |
| Glossary | P4 | S | [docs.md](./backlog/docs.md) | Terms and definitions |

---

## Cleanup & Standards

| Item | Priority | Difficulty | Backlog | Description |
|------|----------|------------|---------|-------------|
| Naming: PyLabPraxis → Praxis | P3 | M | [cleanup.md](./backlog/cleanup.md) | ⚠️ 32 refs in docs/, CONTRIBUTING.md |
| ~~Naming: instruments → machines~~ | ~~P3~~ | ~~M~~ | - | ✅ Complete (0 occurrences) |
| Remove Unused Imports | P3 | S | [cleanup.md](./backlog/cleanup.md) | Dead code cleanup |
| Ruff Formatting | P3 | S | [cleanup.md](./backlog/cleanup.md) | Consistent code formatting |
| Type Annotations Cleanup (ty) | P3 | M | [cleanup.md](./backlog/cleanup.md) | Pyright/ty type checking |
| Dead Code Removal | P3 | S | [cleanup.md](./backlog/cleanup.md) | Commented blocks, unused code |
| Frontend Linting (ESLint) | P3 | M | [cleanup.md](./backlog/cleanup.md) | Ensure ESLint passing |
| DRY Enforcement | P3 | L | [cleanup.md](./backlog/cleanup.md) | Refactor duplicated logic |
| Console.log Cleanup | P3 | S | [cleanup.md](./backlog/cleanup.md) | ⚠️ ~40 console.logs in app/ |
| TODO Comments Audit | P3 | M | [cleanup.md](./backlog/cleanup.md) | Track or resolve TODOs |
| Secrets Check | P3 | S | [cleanup.md](./backlog/cleanup.md) | No secrets in codebase |
| Accessibility Review (ARIA) | P3 | L | [cleanup.md](./backlog/cleanup.md) | ⚠️ Partial: Some ARIA labels exist |
| Error Message Clarity | P3 | M | [cleanup.md](./backlog/cleanup.md) | Improve error messages |
| ~~Empty/Loading State Consistency~~ | ~~P3~~ | ~~M~~ | - | ✅ Complete: `isLoading`, `empty-state` patterns throughout |
| Test Cleanup | P3 | M | [cleanup.md](./backlog/cleanup.md) | Fix skipped tests, consolidate |
| Dependency Audit | P3 | M | [cleanup.md](./backlog/cleanup.md) | Update outdated packages |
| Security Vulnerability Scan | P3 | M | [cleanup.md](./backlog/cleanup.md) | Scan for CVEs |
| Deprecate Sphinx (.rst files) | P3 | S | [cleanup.md](./backlog/cleanup.md) | ⚠️ 17 .rst files in docs/ |
| ~~Lazy Loading Audit~~ | ~~P4~~ | ~~M~~ | - | ✅ Complete: `loadChildren` used for all feature routes |
| Bundle Size Optimization | P4 | L | [cleanup.md](./backlog/cleanup.md) | ~9.3MB total JS (uncompressed dist) |

---

## Summary by Priority

| Priority | Count | Description |
|----------|-------|-------------|
| **P1** | 1 | Critical items blocking merge |
| **P2** | 41 | High priority MVP completions |
| **P3** | 48 | Post-merge enhancements |
| **P4** | 14 | Future feature considerations |
| **Resolved** | 21 | Completed (validated 2026-01-01) |
| **Partial** | ~10 | Have foundational implementation |
| **Wishlist** | 1 | Defer until user demand |
| **Total Active** | **104** | Remaining work items |

---

## Quick Reference: P1 Items (Merge Blockers)

| # | Item | Area | Difficulty |
|---|------|------|------------|
| 1 | Asset Dashboard Scrolling | UI/UX | M |

---

## Recently Resolved (Validated 2025-12-31)

### User-Confirmed Fixes

| Item | Area |
|------|------|
| Command Palette Selection | UI/UX |
| Light Theme Button Rendering | UI/UX |
| Light Theme Color Tuning | UI/UX |
| Deck Resource Adding Bug | Deck |
| Data Visualization Dashboard | UI/UX (not needed) |
| Navigation Rail Hover Menus | UI/UX (not needed) |
| Docs Sidebar & Mermaid Light Mode Fixes | UI/UX |

### Already Implemented (Found During Validation)

| Item | Area | Evidence |
|------|------|----------|
| Naming: instruments → machines | Cleanup | 0 occurrences in frontend |
| Persistent Reservations | Backend | `AssetReservationOrm` used throughout |
| Service Tests: user.py | Backend | 25 tests, 478 lines |
| Service Tests: deck.py | Backend | 15 tests, 303 lines |
| Service Tests: protocol_definition.py | Backend | 8 tests, 238 lines |
| Protocol Authoring Guide | Docs | `docs/user-guide/protocols.md` (339 lines) |
| Contributing Guide | Docs | `CONTRIBUTING.md` (61 lines) |
| Empty/Loading State Consistency | Cleanup | `isLoading`, `empty-state` patterns |
| Lazy Loading | Cleanup | `loadChildren` on all feature routes |

---

## Partial Implementations (⚠️)

These items have foundational code but need polish:

| Item | What Exists | What's Missing |
|------|-------------|----------------|
| Rails Rendering | `getRails()` loop | Hardware-spec positions |
| Carriers Visualization | CSS styling | Physical bar rendering |
| Tip/Well Status | `hasTip()`, `hasLiquid()` helpers | Bitmask support, color coding |
| Split Streams | Backend stdout/stderr types | Frontend visual styling |
| Navigation Breadcrumbs | `LocationBreadcrumbComponent` | App-wide deep nav review |
| Hover Details | Title tooltip on resources | Rich popup with slot ID |
| ARIA Accessibility | Some labels exist | Comprehensive review needed |
| mDNS/Zeroconf | `discover_network_devices()` stub | Actual Zeroconf implementation |

---

*This matrix is validated against the codebase (2025-12-31). See individual backlog files for detailed context.*
