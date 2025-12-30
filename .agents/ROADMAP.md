# Praxis Development Roadmap

**Last Updated**: 2025-12-30
**Current Phase**: Architecture Refinement & Asset Management

---

## Strategic Goals

1. **Robust Asset Management**
    * Move beyond simple CRUD to deep PLR introspection.
    * Enable "discover hardware" as the primary means of adding machines in Browser Mode.
        * Differentiate between Frontend (PLR capability) and Backend (Driver) clearly.
        * Support complex hardware capabilities (channels, optional modules) via proper metadata.

    1. **Application Modes Strategy**
        * **Browser Mode (Pure)**: Zero-install, runs entirely in browser.
            * **Runtime**: Pyodide (WASM) running the Python Service Layer.
            * **Storage**: SQLite-in-WASM (via SQLAlchemy Repository pattern).
            * **IO Layer**: `WebBridgeBackend` (Python) -> Angular -> WebSerial.
        * **Demo Mode**: Browser Mode + Pre-loaded "fake" assets/protocols.
        * **Lite Mode**: SQLite backend, low resource footprint.
        * **Production Mode**: Full Postgres/Redis/FastAPI stack.

    2. **Static Analysis & Graph Building**
        * **Tooling**: Use `LibCST` (Python) for robust, safe protocol parsing.
        * **Goal**: Extract DAGs and metadata without runtime execution risks.
        * **Decision**: Explicitly NOT rewriting backend in Rust at this stage.

    3. **Visualization Evolution**
        * **REWRITE**: Transition from "Deck Visualizer" to "Workcell Visualizer".
    * Remove legacy PLR visualizer components.
    * Implement configurable, multi-window views for complex workcells.

2. **Interactive REPL**
    * Complete the PLR REPL implementation.
    * Finish the terminal UI and keyboard interaction layer.

---

## Priority Matrix

| Area | Critical Items | Backlog |
|------|----------------|---------|
| **Asset Management** | PLR Inspection, Hardware Discovery, Capabilities | [backlog/asset_management.md](./backlog/asset_management.md) |
| **Modes & Deploy** | Browser Mode State, Routing Logic, Auth Strategy | [backlog/modes_and_deployment.md](./backlog/modes_and_deployment.md) |
| **Visualizer** | Rewrite to Workcell Visualizer | [backlog/ui-ux.md](./backlog/ui-ux.md) |
| **REPL** | Terminal UI, Keyboard events | [backlog/repl.md](./backlog/repl.md) |

---

## High Priority Tasks

### 1. Asset Management & PLR Inspection

* [x] **PLR Assessment**: Enumerate machine types, identifiers, capabilities (channels, pumps).
* [x] **Metadata Parsing**: Parse capabilities into chips (e.g., "8-channel", "96-channel").
* [x] **Machine Types**: Backend vs Frontend differentiation in UI.
* [x] **Collapsible Menus**: Hierarchical view for machine types (Type -> Manufacturer -> Model).

### 2. Browser Runtime & Analysis (New)

* [ ] **LibCST Parsing**: Static analysis for protocol safety and asset extraction.
* [ ] **Pyodide Runtime**: WASM-based Python execution in the browser.
* [ ] **WebBridge Backend**: Python shim to route PLR commands to Angular/WebSerial.

### 3. Application Modes

* [ ] **Browser Mode**: Implement LocalStorage persistence adapter.
* [ ] **No-Login Flow**: Bypass AuthGuard in Browser/Demo modes.
* [ ] **Home Routing**: Redirect Home -> Dashboard (skip landing) depending on auth state.
* [ ] **Tunneling Instructions**: UI for Production mode to expose local hardware.

### 3. Visualizer Rewrite

* [x] **Workcell Visualizer**: New architecture for multi-window deck views.
* [x] **Remove Legacy**: Strip out old iframe/PLR-based visualization components.
* [x] **Configurability**: Allow user to arrange deck views/windows.

### 4. REPL

* [ ] **Terminal UI**: Fix keyboard handling (up/down arrow history) and basic interaction.
* [ ] **Completion**: Implement Jedi-based autocompletion.

### 5. UI/UX Polish

#### Command Palette

* [ ] **Keyboard Nav**: Fix up/down arrow active state and scrolling.
* [ ] **Visuals**: Improve responsiveness for selected items.

#### General

* [ ] **Light Theme**: Fix text contrast and button rendering bugs.
* [ ] **Deck Setup**: Fix rendering issues in setup step. This is related to the deck visualization approach.

---

## Branch Strategy

* **Current Goal**: Prepare `angular_refactor` for merge into `main`.
* **Blockers**: Asset Management refactor, Visualizer rewrite.

---

*For completed items, see [archive/completed_2025_12_30.md](./archive/completed_2025_12_30.md).*
