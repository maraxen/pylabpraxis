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
* [ ] **WebBridge I/O Layer**:
  * [ ] Implement messaging bridge between Angular and Pyodide worker.
  * [x] Route `WebBridgeBackend` (Python) signals to `WebSerialService` (Angular) - *Python side implemented*.
  * [ ] Verify End-to-End "Hello World" (Python script moving robot).

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
