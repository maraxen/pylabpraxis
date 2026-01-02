# Backend Backlog

**Area Owner**: Backend
**Last Updated**: 2026-01-02

---

## High Priority

### PLR Definitions Sync - ✅ COMPLETE

- [x] Curated demo dataset created (`plr-definitions.ts`)
- [x] Demo interceptor wired for type definitions
- [x] LibCST-based static analysis for machine/resource discovery
- [x] Pyodide runtime with WebBridge integration
- [ ] Disable the "+ Add Definition" button until sync is complete

### Machine Autodiscovery + REPL - ✅ COMPLETE (2026-01-02)

- [x] Hardware discovery service (`services/hardware_discovery.py`)
  - [x] `discover_serial_ports()` - List available serial ports
  - [x] `discover_simulators()` - List PLR simulator backends
  - [x] `discover_network_devices()` - mDNS/Zeroconf scanning (Opentrons, Tecan, Hamilton, Beckman, Agilent)
- [x] Hardware API endpoints (`api/hardware.py`)
  - [x] `GET /api/v1/hardware/discover`
  - [x] `POST /api/v1/hardware/connect`
  - [x] `POST /api/v1/hardware/disconnect`
  - [x] `GET /api/v1/hardware/connections`
  - [x] `POST /api/v1/hardware/heartbeat` - NEW: TTL-based connection keepalive
  - [x] `GET /api/v1/hardware/connections/{device_id}` - NEW: Get specific connection
  - [x] `POST /api/v1/hardware/register`
  - [x] `POST /api/v1/hardware/repl`
- [x] Frontend hardware service (`hardware-discovery.service.ts`)
  - [x] WebSerial API integration
  - [x] WebUSB API integration
  - [x] PLR device inference from VID/PID
  - [x] Configuration schema support
  - [x] Backend connection management (connectViaBackend, disconnectViaBackend, sendHeartbeat)
- [x] Hardware connection UI component (polish) - connecting/error states with animations
- [x] Hardware connection management (Redis/SQLite state) - `HardwareConnectionManager` service
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

### Protocol Decorator Enhancements - ✅ COMPLETE (2026-01-02)

- [x] Parameterized data views in `@protocol` decorator
  - [x] `DataViewDefinition` dataclass for defining input data requirements
  - [x] `data_views` parameter added to `protocol_function` decorator
  - [x] `DataViewMetadataModel` Pydantic model for API serialization
  - [x] `data_views_json` column added to `FunctionProtocolDefinitionOrm`
  - [x] Support for PLR state data and function data outputs
  - [x] Schema validation with non-blocking warnings
- [x] Example protocols demonstrating data view usage (documented in decorator)
- [x] Minimal implementation for demo

### User-Specified Deck Configuration - ✅ COMPLETE (2026-01-02)

- [x] Support fully user-specified deck via JSON or functions in protocol file
  - [x] `deck_layout_path` parameter in `@protocol_function` decorator
  - [x] `deck_config.py` module with `DeckLayoutConfig` and `ResourcePlacement` models
  - [x] `load_deck_layout()` function for JSON parsing
  - [x] `build_deck_from_config()` function for deck construction
- [x] Deck constraint validation (`validate_deck_layout_config()`)
- [x] Override auto-layout with explicit positions

### Cached PLR Definitions for Frontend - ✅ COMPLETE (2026-01-02)

- [x] **Goal**: Allow `DeckGeneratorService` (frontend) to use actual cached PLR definitions for dimensions, rather than hardcoded defaults.
- [x] **Strategy**:
  - [x] `SqliteService.resourceDefinitions()` provides typed repository access
  - [x] `DeckGeneratorService.getResourceDimensions()` method for dimension lookup
  - [x] Async `generateDeckForProtocolAsync()` variant using cached dimensions
  - [x] Fallback to `DEFAULT_DIMENSIONS` if lookup fails

### Consumables Auto-Assignment - ✅ COMPLETE (2026-01-02)

- [x] `ConsumableAssignmentService` class in `core/consumable_assignment.py`
  - [x] `find_compatible_consumable()` - Smart matching with scoring
  - [x] `auto_assign_consumables()` - Batch assignment
- [x] Compatibility checking logic:
  - [x] Volume capacity matching
  - [x] Plate type compatibility
  - [x] Availability checking (not reserved)
  - [x] Expiration date scoring
  - [x] Batch/lot number tracking
- [x] Integration into `ProtocolScheduler.analyze_protocol_requirements()`
- [x] `suggested_asset_id` field added to `RuntimeAssetRequirement`
- [ ] Frontend browser-mode equivalent (P3)
- [ ] Unit tests for assignment logic (P3)
- [ ] Integration tests (P3)

### Full Implementation of VMP Features (Stubs)

- [ ] **Scheduler**: Eliminate ~22% coverage; implement robust scheduling logic (currently VMP). Test files exist but need DB.
- [x] **Persistent Reservations**: ✅ Complete - Now uses `AssetReservationOrm` database storage.
- [x] **Hardware Scanning**: ✅ Complete (2026-01-02) - mDNS/Zeroconf discovery for Opentrons, Tecan, Hamilton, Beckman, Agilent.
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

### Dual DB Testing (P2) - ✅ COMPLETE

- [x] **SQLite Support**: Test suite runs with in-memory SQLite via `TEST_DB_TYPE=sqlite`.
- [x] **PostgreSQL Support**: Test suite runs against PostgreSQL (default with Docker).
- [x] **CI Configuration**: GitHub Actions matrix runs both `test-sqlite` and `test-postgresql` jobs.
- [x] **Migration Testing**: Alembic env.py supports `DATABASE_URL` override for both DBs.
- [x] **Markers**: Added `@pytest.mark.postgresql_only` and `@pytest.mark.sqlite_only` markers.
- [x] **Documentation**: Updated DEVELOPMENT_MATRIX.md and backend.md with implementation details.

**Usage**:

```bash
# SQLite (fast, in-memory, no Docker)
TEST_DB_TYPE=sqlite pytest

# PostgreSQL (production-like, requires Docker)
TEST_DATABASE_URL=postgresql+asyncpg://... pytest
```

### Technical Debt (from TECHNICAL_DEBT.md)

- [x] **Persistent asset reservations** - ✅ Complete (uses `AssetReservationOrm`)
- [ ] POST /resources/ API error fix
- [ ] Reservation inspection/clearing APIs
- [x] **Consumables auto-assignment improvements** - ✅ Complete (2026-01-02)
- [ ] Cost optimization for consumables (Deferred to P4)

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
- [x] **Protocol Decorator Data Views** (2026-01-02) - Schema-based input data definitions
- [x] **User-Specified Deck Configuration** (2026-01-02) - JSON/function-based deck layouts
- [x] **Cached PLR Definitions for Frontend** (2026-01-02) - SqliteService integration
- [x] **Consumables Auto-Assignment** (2026-01-02) - Smart assignment with scoring
