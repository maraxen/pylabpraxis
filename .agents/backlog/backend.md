# Backend Backlog

**Area Owner**: Backend
**Last Updated**: 2025-12-29

---

## High Priority

### PLR Definitions Sync

- [x] Curated demo dataset created (`plr-definitions.ts`)
- [x] Demo interceptor wired for type definitions
- [ ] Disable the "+ Add Definition" button until sync is complete
- [ ] Dynamic backend introspection (optional for demo)

### Machine Autodiscovery + REPL

- [x] Hardware discovery service (`services/hardware_discovery.py`)
  - [x] `discover_serial_ports()` - List available serial ports
  - [x] `discover_simulators()` - List PLR simulator backends
  - [x] `discover_network_devices()` - mDNS/Zeroconf scanning (stub)
- [x] Hardware API endpoints (`api/hardware.py`)
  - [x] `GET /api/v1/hardware/discover`
  - [x] `POST /api/v1/hardware/connect`
  - [x] `POST /api/v1/hardware/disconnect`
  - [x] `GET /api/v1/hardware/connections`
  - [x] `POST /api/v1/hardware/register`
  - [x] `POST /api/v1/hardware/repl`
- [x] Frontend hardware service (`hardware-discovery.service.ts`)
  - [x] WebSerial API integration
  - [x] WebUSB API integration
  - [x] PLR device inference from VID/PID
  - [x] Configuration schema support
- [ ] Hardware connection UI component
- [ ] Hardware connection management (Redis state)
- [ ] Full REPL WebSocket interface

### Protocol Decorator Enhancements

- [ ] Parameterized data views in `@protocol` decorator
- [ ] Example protocols demonstrating data view usage
- [ ] Minimal implementation for demo

### Browser Runtime & Analysis (New)

- [ ] **LibCST Parsing**:
  - [ ] Prototype script to parse `simple_transfer.py` via `LibCST`.
  - [ ] Extract asset requirements and parameter types safely.
- [ ] **Pyodide Spike**:
  - [ ] Verify `pylabrobot` installation in WASM environment.
  - [ ] Create `WebBridgeBackend` Python shim for IO interception.

### User-Specified Deck Configuration

- [ ] Support fully user-specified deck via functions in protocol file
- [ ] Deck constraint validation
- [ ] Override auto-layout with explicit positions

---

## Medium Priority

### Execution & Scheduling

- [ ] Complete remaining `first_light` track items
- [ ] Asset resolution improvements
- [ ] Simulation mode polish

### Service Layer Coverage

- [ ] `services/scheduler.py` - 0% coverage
- [ ] `services/user.py` - 0% coverage
- [ ] `services/deck.py` - 26% coverage
- [ ] `services/protocol_definition.py` - 21% coverage

### Technical Debt (from TECHNICAL_DEBT.md)

- [ ] Persistent asset reservations (currently in-memory)
- [ ] POST /resources/ API error fix
- [ ] Reservation inspection/clearing APIs

---

## Low Priority

### Advanced Scheduling

- [ ] Discrete event simulation engine
- [ ] Multi-workcell scheduling
- [ ] Resource-constrained optimization

### Hardware Bridge Full

- [ ] WebSerial passthrough for remote clients
- [ ] Driver routing/multiplexing
- [ ] Device profiles (saved configurations)

---

## Completed (Archive Reference)

- [x] Protocol discovery via AST parsing
- [x] Backend execution flow (`ExecutionMixin`)
- [x] WebSocket log streaming
- [x] Simulation flag flow through stack
- [x] Orchestrator execution (100% coverage)
- [x] PLR definitions curated dataset (60+ resources, 10+ machines)
- [x] Hardware discovery service foundation
- [x] Hardware API endpoints (discover, connect, disconnect, register, repl)
- [x] Frontend WebSerial/WebUSB service with PLR inference

### Cached PLR Definitions for Frontend

- [ ] **Goal**: Allow `DeckGeneratorService` (frontend) to use actual cached PLR definitions for dimensions, rather than hardcoded defaults.
- [ ] **Strategy**:
  - [ ] Ensure `AssetService` can serve full `MachineDefinition` and `ResourceDefinition` objects (including dimensions) from `localStorage` (Browser Mode) or Backend (Production).
  - [ ] Refactor `DeckGeneratorService` to be async or use a synchronized store to access these definitions.
  - [ ] Pre-load definitions on app startup.
