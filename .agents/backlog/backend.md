# Backend Backlog

**Area Owner**: Backend
**Last Updated**: 2025-12-30

---

## High Priority

### PLR Definitions Sync - ✅ COMPLETE

- [x] Curated demo dataset created (`plr-definitions.ts`)
- [x] Demo interceptor wired for type definitions
- [x] LibCST-based static analysis for machine/resource discovery
- [x] Pyodide runtime with WebBridge integration
- [ ] Disable the "+ Add Definition" button until sync is complete

### Machine Autodiscovery + REPL - ✅ CORE COMPLETE

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
- [ ] Hardware connection UI component (polish)
- [ ] Hardware connection management (Redis state)
- [ ] Full REPL WebSocket interface (Production mode)

### Browser Runtime & Analysis - ✅ COMPLETE

- [x] **LibCST Parsing**:
  - [x] `PLRSourceParser` for machine/backend/resource discovery
  - [x] `ProtocolFunctionVisitor` for protocol extraction
  - [x] `ProtocolRequirementExtractor` for capability inference
- [x] **Pyodide Runtime**:
  - [x] `pylabrobot` mocking and WebBridgeBackend
  - [x] `WebBridgeIO` for generic machine IO
  - [x] CDN package loading (micropip, etc.)

### Protocol Decorator Enhancements

- [ ] Parameterized data views in `@protocol` decorator
- [ ] Example protocols demonstrating data view usage
- [ ] Minimal implementation for demo

### User-Specified Deck Configuration

- [ ] Support fully user-specified deck via functions in protocol file
- [ ] Deck constraint validation
- [ ] Deck constraint validation
- [ ] Override auto-layout with explicit positions

### Full Implementation of VMP Features (Stubs)

- [ ] **Scheduler**: Eliminate ~22% coverage; implement robust scheduling logic (currently VMP). Test files exist but need DB.
- [x] **Persistent Reservations**: ✅ Complete - Now uses `AssetReservationOrm` database storage.
- [ ] **Hardware Scanning**: ⚠️ Stubbed - `discover_network_devices()` returns empty list.
- [ ] **Asset Resolution**: Improve logic for resolving abstract requirements to physical assets.

---

## Medium Priority

### Execution & Scheduling

- [ ] Complete remaining `first_light` track items
- [ ] Asset resolution improvements
- [ ] Simulation mode polish

### Service Layer Coverage

**Validated 2025-12-31:**

- [x] **user.py** - ✅ 25 tests (478 lines) in `test_user_service.py`
- [x] **deck.py** - ✅ 15 tests (303 lines) in `test_deck_service.py`
- [x] **protocol_definition.py** - ✅ 8 tests (238 lines) in `test_protocol_definition_service.py`
- [ ] **scheduler.py** - ~22% coverage (tests exist but need DB)
- [ ] Other services - audit needed

### Dual DB Testing (P2)

- [ ] **SQLite Support**: Ensure test suite runs with SQLite (current).
- [ ] **PostgreSQL Support**: Run test suite against PostgreSQL.
- [ ] **CI Configuration**: Add GitHub Actions matrix for both DBs.
- [ ] **Migration Testing**: Verify Alembic migrations on both DBs.

### Technical Debt (from TECHNICAL_DEBT.md)

- [x] **Persistent asset reservations** - ✅ Complete (uses `AssetReservationOrm`)
- [ ] POST /resources/ API error fix
- [ ] Reservation inspection/clearing APIs
- [ ] Consumables auto-assignment improvements

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

- [x] Protocol discovery via AST parsing → LibCST migration complete
- [x] Backend execution flow (`ExecutionMixin`)
- [x] WebSocket log streaming
- [x] Simulation flag flow through stack
- [x] Orchestrator execution (100% coverage)
- [x] PLR definitions curated dataset (60+ resources, 10+ machines)
- [x] Hardware discovery service foundation
- [x] Hardware API endpoints (discover, connect, disconnect, register, repl)
- [x] Frontend WebSerial/WebUSB service with PLR inference
- [x] LibCST-based PLR static analysis (21 frontends, 70 backends, 15 machine types)
- [x] Pyodide WebBridge with IO layer shimming
- [x] Jedi-based REPL autocompletion

### Cached PLR Definitions for Frontend

- [ ] **Goal**: Allow `DeckGeneratorService` (frontend) to use actual cached PLR definitions for dimensions, rather than hardcoded defaults.
- [ ] **Strategy**:
  - [ ] Ensure `AssetService` can serve full `MachineDefinition` and `ResourceDefinition` objects (including dimensions) from `localStorage` (Browser Mode) or Backend (Production).
  - [ ] Refactor `DeckGeneratorService` to be async or use a synchronized store to access these definitions.
  - [ ] Pre-load definitions on app startup.
