# Application Modes & Deployment Backlog

**Priority**: High
**Owner**: DevOps / Full Stack
**Last Updated**: 2025-12-30

---

## 1. Mode Definitions

### Browser Mode (Pure)

* **Concept**: Zero-infrastructure, runs entirely in the client browser.
* **State**: `LocalStorage` (adapters needed).
* **Auth**: **No Login**. Direct access.
* **Hardware**: "Discover Hardware" (WebSerial/WebUSB) is the *only* means of adding machines.
* **Routing**: Redirects `Home` -> `Dashboard`. No Landing Page.

### Demo Mode

* **Concept**: Browser Mode + Pre-loaded Content.
* **Assets**: Fake resources and simple simulated machines.
* **Use Case**: "Try it out" without connecting anything.
* **Implementation**: A specific configuration of Browser Mode.

### Lite Mode

* **Concept**: Low-weight server deployment.
* **Backend**: Local Python server.
* **DB**: SQLite.
* **Auth**: Optional/Single User.

### Production Mode

* **Concept**: Full laboratory deployment.
* **Backend**: Scalable Python server.
* **DB**: Postgres + Redis.
* **Auth**: Keycloak / Full Auth.
* **Hardware**: Tunneling instructions provided to expose local hardware to server.

---

## 2. Tasks

### Browser Runtime Implementation (New)

* [x] **Pyodide Integration**:
  * [x] Add `pyodide` script/package to `praxis/web-client`.
  * [x] Create `PythonRuntimeService` (Angular) to manage WASM worker.
  * [x] Resolve dependencies (`micropip.install('pylabrobot')`) or create mocks.
  * [x] WebWorker (`python.worker.ts`) handles EXEC and INSTALL commands.
* [x] **Basic WebBridge**:
  * [x] `web_bridge.py` with high-level `WebBridgeBackend` overriding LiquidHandlerBackend methods.

#### IO Layer Shimming: ✅ COMPLETED 2025-12-30

**Goal**: Generic IO shim that works for ALL PLR machines by replacing their transport layer.

* [x] **1. Identify IO Point**: Found `self.io` attribute using `IOBase` interface (`write()`, `read()`, `setup()`, `stop()`).
* [x] **2. WebBridgeIO Class**: Implemented in `web_bridge.py` with full PLR-compatible interface.
* [x] **3. Async Read/Write**: UUID-based request correlation with `asyncio.Future` for async reads.
* [x] **4. Generic Patcher**: `patch_io_for_browser(machine, port_id)` + `create_browser_machine()` factory.
* [x] **5. Angular Integration**:
  * `python.worker.ts`: RAW_IO and RAW_IO_RESPONSE message handling.
  * `PythonRuntimeService.handleRawIO()`: Routes commands to `HardwareDiscoveryService`.
  * `HardwareDiscoveryService`: Added `openPort()`, `closePort()`, `writeToPort()`, `readFromPort()`, `readLineFromPort()`.
* [ ] **6. E2E Test**: Pending hardware testing - **⏳ Deferred (user unavailable)**

### Browser SQL with Preloaded DB (P2)

* [ ] **SQL.js Configuration**:
  * Use Pyodide SQL.js with a preloaded `.db` file.
  * Load from persistent file in the repo.
  * Helps with GitHub Pages deployment.

* [ ] **Database Contents**:
  * Capability type definitions (synced from PLR).
  * All production data EXCEPT scheduling.
  * Protocol definitions, resources, machines, decks.

* [ ] **Implementation**:
  * Create script to generate production-like `.db` file.
  * Load on browser mode initialization.
  * Ensure CST (capability schema types) are validated and up-to-date.

### Enhanced SqliteService - Full Browser Backend (P2)

**Goal**: Expand `SqliteService` to provide full backend functionality in browser mode without relying on mock data.

* [ ] **Database Schema Parity (Automated)**:
  * **Single Source of Truth**: Use Python SQLAlchemy ORM models as the definition.
  * **Codegen Pipeline**: Create a build script that:
    1. Introspects SQLAlchemy models to generate a `schema.sql` (SQLite DDL).
    2. Generates TypeScript interfaces (`schema.d.ts`) matching the ORM models.
  * Update `SqliteService` to initialize from this generated `schema.sql`.

* [ ] **TypeScript Service Layer**:
  * Implement CRUD operations for all entities (`createProtocolRun`, `updateMachine`, etc.).
  * Port essential business logic from Python services to TypeScript.
  * Must handle relationships (e.g., protocol runs → protocol definitions).

* [ ] **Real Data Flow**:
  * When user starts a protocol in browser mode, create actual `ProtocolRun` record.
  * Track run status updates in sql.js.
  * Execution Monitor reads from sql.js instead of mock data.

* [ ] **Persistence**:
  * Export sql.js database to IndexedDB for cross-session persistence.
  * Auto-load on app startup.
  * Optional: Export/Import database files.

* [ ] **Testing**:
  * Unit tests for TypeScript service layer.
  * E2E tests for browser mode data flow.

### State Persistence

* [x] **LocalStorage Adapter**: Implemented `LocalStorageAdapter` service with CRUD operations for protocols, runs, resources, machines.

* [x] **State Save/Load**:
  * `exportState()` exports current state to JSON string.
  * `importState(json, merge)` loads state from JSON (with optional merge).
  * Essential for "Browser Mode" session management.

### Authentication & Routing

* [x] **ModeService**: Centralized mode detection (`ModeService`) with `isBrowserMode()`, `requiresAuth()` signals.
* [x] **No-Login Flow**:
  * `AuthGuard` now checks `ModeService` to allow passthrough in browser/demo modes.
  * Login/Logout buttons hidden in UI for these modes, replaced with mode badge.

* [x] **Routing Logic**:
  * If Browser/Demo: `Root` -> `Dashboard` (via SplashComponent auto-redirect).
  * If Prod: `Root` -> `Landing` -> `Login` -> `Dashboard`.

### Hardware Discovery

* [ ] **Browser Only**:
  * Disable "Add Machine manually" (IP/Host).
  * Enforce "Discover" workflow via WebSerial.

* [ ] **Production Tunneling**:
  * If adding a machine in Production mode, show help text/modal: "To connect a local machine, run the Praxis Tunnel client..." (Future feature, but UI hook needed).

### Validation

* [ ] **Validation Docs**:
  * Create documentation in `.agents/reference/modes.md` specifically validating each mode's constraints.
  * Verification checklist for each mode release.
