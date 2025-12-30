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

### State Persistence

- [ ] **LocalStorage Adapter**: Implement a storage adapter for the frontend that mirrors the backend API but saves to browser LocalStorage (for Browser/Demo modes).
* [ ] **State Save/Load**:
  * Ability to export current state to a JSON file.
  * Ability to load state from JSON file (Strudel-like functionality).
  * Essential for "Browser Mode" session management.

### Authentication & Routing

- [ ] **No-Login Flow**:
  * Update `AuthGuard` to allow passthrough if `mode === 'browser' | 'demo'`.
  * Hide "Login/Logout" buttons in UI for these modes.
* [ ] **Routing Logic**:
  * If Browser/Demo: `Root` -> `Dashboard`.
  * If Prod: `Root` -> `Landing` -> `Login` -> `Dashboard`.

### Hardware Discovery

- [ ] **Browser Only**:
  * Disable "Add Machine manually" (IP/Host).
  * Enforce "Discover" workflow via WebSerial.
* [ ] **Production Tunneling**:
  * If adding a machine in Production mode, show help text/modal: "To connect a local machine, run the Praxis Tunnel client..." (Future feature, but UI hook needed).

### Validation

- [ ] **Validation Docs**:
  * Create documentation in `.agents/reference/modes.md` specifically validating each mode's constraints.
  * Verification checklist for each mode release.
