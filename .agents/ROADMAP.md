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
| **Capability Tracking** | Classification Fix, Machine Type Coverage, User Config | [backlog/capability_tracking.md](./backlog/capability_tracking.md) |
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

**Known Issues** (see [backlog/capability_tracking.md](./backlog/capability_tracking.md)):

* [x] ~~Classification bug: LiquidHandler misclassified as Resource due to inheritance.~~ FIXED 2025-12-30
* [x] ~~Only 2 machine types covered; PLR has 15+ (HeaterShaker, Centrifuge, Pump, etc.).~~ FIXED 2025-12-30 - Now discovers 21 frontends, 70 backends across 15 machine types
* [x] ~~Backend-frontend mapping broken due to classification issue.~~ FIXED 2025-12-30

### 2. Browser Runtime & Analysis (New)

* [x] **LibCST Parsing**: Static analysis for machine/backend discovery (plr_static_analysis module).
* [x] **Pyodide Runtime**: WASM-based Python execution in browser (WebWorker + python.worker.ts).
* [x] **Basic WebBridge**: web_bridge.py with high-level WebBridgeBackend overrides.

**IO Layer Shimming** (Next Step):

* [ ] **WebBridgeIO Class**: Generic IO shim that replaces `self.io` transport layer on any PLR machine.
* [ ] **Serial/USB Dispatch**: Route raw bytes via `js.postMessage` to Angular's WebSerialService/WebUSB.
* [ ] **Async Read/Write**: Implement WebBridgeIO.write() → JS and WebBridgeIO.read() ← JS patterns.
* [ ] **Generic Patcher**: Helper/decorator to patch any standard PLR machine's IO layer when `is_browser_mode`.
* [ ] **Angular Integration**: PythonRuntimeService listens for RAW_IO_WRITE/READ messages.

### 3. Application Modes

* [x] **ModeService**: Centralized mode detection with computed signals.
* [x] **Browser Mode**: Implemented LocalStorage persistence adapter with state export/import.
* [x] **No-Login Flow**: AuthGuard bypassed in Browser/Demo modes, login/logout hidden in UI.
* [x] **Home Routing**: Splash page auto-redirects to Dashboard in browser mode.
* [ ] **Tunneling Instructions**: UI for Production mode to expose local hardware. (Deferred)

### 3. Visualizer Rewrite

* [x] **Workcell Visualizer**: New architecture for multi-window deck views.
* [x] **Remove Legacy**: Strip out old iframe/PLR-based visualization components.
* [x] **Configurability**: Allow user to arrange deck views/windows (LocalStorage persistence).

**Deck View Improvements** (Needed):

* [ ] **Slots/Rails**: Dynamic rendering of deck slots, rails, and mounting positions.
* [ ] **Itemized Resources**: Show individual wells, tips, tubes within containers.
* [ ] **Dimensions**: Use actual PLR resource dimensions for accurate scaling.
* [ ] **PLR Theming**: Match original PLR visualizer aesthetic while keeping app theme consistency.
* [ ] **Resource Placement**: Fix buggy "add resource to deck" workflow.

### 4. REPL

* [x] **Terminal UI**: Implemented keyboard history (Up/Down) and `Ctrl+L` clearing.
* [ ] **Completion**: Implement Jedi-based autocompletion.

### 5. UI/UX Polish

#### Command Palette

* [ ] **Keyboard Nav**: Fix up/down arrow active state and scrolling.
* [ ] **Visuals**: Improve responsiveness for selected items.

#### Theming

* [ ] **Light/Dark Toggle**: Buttons toggle but background doesn't change in light mode.
* [ ] **Light Theme Contrast**: Fix text contrast and button rendering bugs.

#### Scrolling & Layout

* [ ] **Component Scrolling**: Fix buggy scrolling behavior within components.
* [ ] **Deck Setup**: Fix rendering issues in setup step (related to deck visualization).

### 6. Capability Tracking System (New)

See [backlog/capability_tracking.md](./backlog/capability_tracking.md) for full details.

**Phase 1 - Fix Core Issues (Immediate)**: ✅ COMPLETED 2025-12-30

* [x] Fix classification priority: Machine bases before Resource bases.
* [x] Expand machine type discovery to all 15+ PLR types.
* [x] Fix backend-frontend mapping.

**Phase 2 - Generic Capability Model (Short-term)**:

* [ ] Machine-type-specific capability schemas (not just Hamilton).
* [ ] Extend capability extraction for all machine types.

**Phase 3 - User-Configurable Capabilities (Medium-term)**:

* [ ] Backend config schema for optional capabilities.
* [ ] Frontend dialog for machine setup with capability questions.
* [ ] ORM updates for user-configured capabilities.

**Phase 4 & 5 - Protocol Matching & Inspection (Future)**:

* [ ] Extract protocol asset requirements via LibCST.
* [ ] Match protocol requirements to available hardware capabilities.

---

## Branch Strategy

* **Current Goal**: Prepare `angular_refactor` for merge into `main`.
* **Blockers**: Asset Management refactor, Visualizer rewrite.

---

*For completed items, see [archive/completed_2025_12_30.md](./archive/completed_2025_12_30.md).*
