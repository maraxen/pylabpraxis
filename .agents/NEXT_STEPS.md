# PyLabPraxis - Next Steps & Lessons Learned

**Created**: 2025-12-21
**Last Updated**: 2025-12-21

---

## 📚 Lessons Learned (Dec 21, 2025 Session)

### API Endpoint Mismatches
Several frontend services were calling incorrect backend API endpoints:

| Service | Incorrect Endpoint | Correct Endpoint | Status |
|---------|-------------------|------------------|--------|
| `ProtocolService.getProtocols()` | `/api/v1/protocols` | `/api/v1/protocols/definitions` | ✅ Fixed |
| `AssetService.getMachineDefinitions()` | `/api/v1/discovery/machines` | `/api/v1/assets/definitions?type=machine` | ✅ Fixed |
| `AssetService.getResourceDefinitions()` | `/api/v1/discovery/resources` | `/api/v1/assets/definitions?type=resource` | ✅ Fixed |

**Key Insight**: Always verify frontend API calls against the backend's OpenAPI spec at `http://localhost:8000/docs`.

### Discovery Service Configuration
The `/api/v1/discovery/sync-all` endpoint was failing because `praxis_config` was not attached to `app.state`.

**Fix**: Added `app.state.praxis_config = praxis_config` in `main.py` lifespan.

### Database Schema Issue
The `name` field in PLR type definition tables (`resource_definition_catalog`, `machine_definition_catalog`, `deck_definition_catalog`) had a `unique=True` constraint, but multiple PyLabRobot classes share the same short name (e.g., "Plate" exists in many modules).

**Fix**:
1. Changed `unique=True` → `unique=False` in `praxis/backend/models/orm/plr_sync.py`
2. Created migration `577d92edf9a5_remove_unique_from_name.py` to drop and recreate indexes without uniqueness

### PyLabRobot Import Errors
Some deprecated PLR modules (e.g., `pylabrobot.resources.falcon`) raise exceptions when imported.

**Fix**: Changed `except ImportError` → `except Exception` in `resource_type_definition.py` to catch all import-related exceptions.

### Discovery Filtering Issue (KNOWN ISSUE)
The current discovery service syncs generic base classes (e.g., `Plate`, `TipRack`, `TubeCarrier`) instead of concrete implementations (e.g., `Azenta360uLPlate`, `HTF_L_SBS`, `Cos_96_EZWash`).

**Problem**:
- Abstract base classes are being included when they should be excluded
- Generic class names appear multiple times from different modules
- Users need specific, instantiable resource definitions, not base classes

**Required Fix** (in `resource_type_definition.py`):
1. Expand `EXCLUDED_BASE_CLASSES` to include more abstract types
2. Filter to only include classes that have a concrete `__init__` (not just inherited)
3. Prefer the "furthest down the chain" class names - concrete implementations
4. Consider filtering by module pattern (e.g., include only from vendor-specific modules like `pylabrobot.resources.azenta.*`, `pylabrobot.resources.corning.*`)

### Theme Toggle Not Working (KNOWN ISSUE)
The light/dark mode toggle in the frontend does not function correctly.

**Symptoms**: Clicking the theme toggle does not switch between light and dark themes.

**To Investigate**:
- Check `ThemeService` or theme-related code in `praxis/web-client/src/app/`
- Verify CSS custom properties are being updated
- Check localStorage persistence of theme preference
- Ensure Material 3 theme variables are toggled correctly

---

## 🎯 Next Steps Roadmap

### Phase 0: Fix PLR Discovery Filtering ✅ COMPLETE (Dec 21, 2025)
The discovery service now syncs concrete, instantiable resource definitions.

- [x] **Expanded exclusion list**: Added 26 base classes to `EXCLUDED_BASE_CLASSES`:
  - `Plate`, `TipRack`, `Trough`, `Tube`, `TubeRack`, `Carrier`, `TipCarrier`, `PlateCarrier`, `TroughCarrier`, `TubeCarrier`, `MFXCarrier`, `Trash`, `PetriDish`, `PetriDishHolder`, `Lid`, `Well`, `TipSpot`, etc.
- [x] **Filter by name**: Added name-based exclusion to handle classes imported via different paths
- [x] **Added factory function discovery**: Factory functions (e.g., `Cor_96_wellplate_360ul_Fb`) from vendor modules are now synced as resource definitions
- [x] **Vendor module patterns**: Added `VENDOR_MODULE_PATTERNS` for hamiton, opentrons, tecan, corning, azenta, alpaqua, greiner, thermo, revvity, porvair
- [x] **Re-ran discovery sync**: Verified **374 resource definitions** synced (vs ~100 generic base classes before)

**Result**: Database now contains concrete resources like `TecanPlate`, `HamiltonSTARDeck`, `Cor_96_wellplate_360ul_Fb`, `DiTi_500ul_LiHa`, `AB_Plate_96_Well`, etc.

---

### Phase 1: Protocol Library & Simulation Mode ✅ COMPLETE (Dec 21, 2025)

#### 1.1 Example Protocol Library ✅
Created 3 demo protocols with PLR-compatible type hints that work with the discovery service.

- [x] Created `praxis/protocol/protocols/` directory with example protocols:
  - [x] `simple_transfer.py` - Basic liquid transfer between wells (3 assets, 4 params)
  - [x] `serial_dilution.py` - Serial dilution across a plate (2 assets, 7 params)
  - [x] `plate_preparation.py` - Prepare a 96-well plate with fill patterns (2 assets, 6 params)
- [x] All protocols use `@protocol_function` decorator with proper metadata
- [x] Protocols use generic PLR types (`Plate`, `TipRack`, `Trough`) for asset parameters
- [x] Discovery service syncs protocols via AST parsing

#### 1.2 Simulation Mode Support ✅
Added `is_simulation` parameter throughout the execution chain.

- [x] Added `is_simulation: bool = False` to `IOrchestrator` interface
- [x] Updated `ProtocolExecutionService.execute_protocol_immediately()` to accept `is_simulation`
- [x] Updated `ProtocolExecutionService.schedule_protocol_execution()` to accept `is_simulation`
- [x] Updated `ExecutionMixin.execute_protocol()` and `execute_existing_protocol_run()` to log simulation status

#### 1.3 Protocol Discovery & Verification ✅
Fixed multiple issues to enable end-to-end protocol discovery.

- [x] Fixed `configure.py:default_protocol_dir` path resolution
- [x] Added `visit_AsyncFunctionDef` to `ProtocolVisitor` for async protocol functions
- [x] Added `@protocol_function` decorator detection via AST analysis
- [x] Fixed asset field names (`type_hint_str`, `accession_id`) in discovery extraction
- [x] Added `protocol_definition_service` to `DiscoveryService` initialization in `main.py`
- [x] Fixed `ProtocolDefinitionCRUDService.create()` to convert param/asset dicts to ORM objects
- [x] Verified 3 protocols appear in `/api/v1/protocols/definitions` API

---

### Phase 2: Asset Management Enhancements ✅ COMPLETE (Dec 21, 2025)

#### 2.1 PLR Type Autofill for Assets ✅
Enhanced "Add Machine" and "Add Resource" dialogs to use PLR type definitions.

- [x] Add autocomplete/dropdown for `Machine Type` using synced machine definitions
- [x] Add autocomplete/dropdown for `Resource Type` using synced resource definitions
- [x] Auto-populate fields (model, manufacturer, description) when type is selected
- [x] Add `machine_definition_accession_id` to `MachineCreate` model
- [x] Add `fqn` field to `MachineDefinition` and `ResourceDefinition` interfaces

#### 2.2 Display Improvements ✅
- [x] Show factory function name (last part of FQN) as primary display name
- [x] Show module path in smaller, lighter styled text
- [x] Fixed inline styling for proper visual spacing

#### 2.3 Theme Toggle Fix ✅
- [x] Fixed `AppStore.setTheme()` to properly add `light-theme` class
- [x] Theme now correctly switches between light and dark modes

---

### Phase 2.5: Resource Definition UX Improvements ✅ COMPLETE (Dec 22, 2025)

- [x] Vendor-prefixed display names: `[Vendor] FunctionName` format
- [x] Category filter chips (All, Plates, Tip Racks, Troughs, Tubes, Carriers)
- [x] Natural language search across name, FQN, vendor, specs
- [x] Selected definition preview with badges (wells, volume, plate type)
- [x] Enhanced autocomplete with metadata tags

---

### Phase 2.7: AI-Powered Resource Selection (HIGH PRIORITY)

**Goal**: Create a unified, intelligent resource selection interface that works for both asset management and protocol resource binding.

#### 2.7.1 Object Attribute Parsing
Parse actual PLR object attributes into filterable properties instead of just metadata.

- [ ] Extract all PLR resource class attributes (size_x, size_y, size_z, num_items, well_volume, etc.)
- [ ] Store structured properties in `properties_json` field during discovery
- [ ] Create backend API to expose all unique property keys and value ranges
- [ ] Build property-to-chip mapping for dynamic filter generation

#### 2.7.2 Dynamic Chip-Based Filtering
Replace static category chips with dynamically populated filter chips on carousels.

- [ ] Create horizontal carousel component for chip groups
- [ ] Group chips by property category (Type, Vendor, Capacity, Dimensions, etc.)
- [ ] Chips should be toggleable and show result counts
- [ ] Support multi-select within categories (OR logic) and cross-category (AND logic)
- [ ] Animate chip selections for visual feedback

#### 2.7.3 AI-Powered Search Bar
Use client-side Gemma model to process natural language queries into filter chips.

- [ ] Integrate `@anthropic-ai/sdk` or `@anthropic/gemma` for browser-based inference
- [ ] Parse queries like "96 well plate around 200uL from corning" into chips
- [ ] Show suggested chip combinations as user types
- [ ] Fallback to keyword search if AI unavailable
- [ ] Consider using WebLLM or Transformers.js for local inference

#### 2.7.4 Protocol Resource Binding Integration
Reuse the same dialog for selecting resources when configuring protocol runs.

- [ ] When protocol specifies constraints (e.g., `Plate` type hint, `min_volume=100`), pre-apply as locked chips
- [ ] Show locked/required chips in a different color (disabled state)
- [ ] Allow user to refine selection within constraints
- [ ] Validate selected resource meets protocol requirements
- [ ] Share component between asset creation and protocol wizard

#### 2.7.5 UI/UX Polish
- [ ] Large search bar at top of dialog (prominent, centered)
- [ ] Chip carousels below search bar (scrollable horizontally)
- [ ] Results grid/list below chips (virtualized for performance)
- [ ] Smooth animations for chip add/remove
- [ ] Dark mode support

---

### Phase 2.8: Machine Selection Enhancement (MEDIUM)

Apply the same pattern from 2.7 to machine selection.

#### 2.8.1 Machine Attribute Parsing
- [ ] Extract machine class attributes during discovery
- [ ] Store structured properties (deck_size, pipette_channels, tip_types, etc.)

#### 2.8.2 Dynamic Machine Filtering
- [ ] Chip carousels for: Machine Type, Manufacturer, Deck Layout, Pipette Config
- [ ] Same AI-powered search bar integration

#### 2.8.3 Protocol Machine Binding
- [ ] When protocol specifies machine requirements, show as locked chips
- [ ] Validate machine compatibility with protocol

---

### Phase 2.9: Browser-Based Instrument Detection (EXPERIMENTAL)

Automatically detect connected lab instruments via browser APIs.

#### 2.9.1 USB/Serial Detection
- [ ] Use WebUSB API to enumerate connected USB devices
- [ ] Use Web Serial API for serial port instruments
- [ ] Match VID/PID against known instrument database

#### 2.9.2 Instrument Identification
- [ ] Query detected devices for identity strings
- [ ] Infer PLR machine type from device signatures
- [ ] Suggest matching MachineDefinition from catalog

#### 2.9.3 One-Click Connection
- [ ] Auto-populate connection_info from detected device
- [ ] Create machine asset with detected parameters
- [ ] Test connection via PLR backend
- [ ] Show connection status badge on machine cards

---

### Phase 3: Deck Visualizer (MEDIUM)

#### 3.1 Visualizer Integration
Get the deck visualizer working in the frontend.

- [ ] Review existing `DeckVisualizerComponent` implementation
- [ ] Verify backend provides deck layout data endpoint
- [ ] Implement WebSocket updates for real-time deck state changes
- [ ] Add drag-and-drop functionality for resource placement
- [ ] Test with simulated deck configurations

#### 3.2 Interactive Deck Configuration
Allow users to configure deck layouts before protocol execution.

- [ ] Implement deck position selection UI
- [ ] Add resource assignment to deck positions
- [ ] Save/load deck configurations
- [ ] Validate deck configuration against protocol requirements

---

### Phase 4: Backend & Infrastructure (LOW)

#### 4.1 Backend Token Validation
Complete Keycloak integration on the backend.

- [ ] Implement JWT validation middleware
- [ ] Extract user info from Keycloak tokens
- [ ] Apply auth guards to protected endpoints
- [ ] Add user context to protocol runs and logs

#### 4.2 WebSocket Improvements
Enhance real-time communication.

- [ ] Implement reconnection logic on frontend
- [ ] Add heartbeat mechanism
- [ ] Ensure proper cleanup on disconnect
- [ ] Add TypeScript types for all WS message types

#### 4.3 Test Coverage
Improve test coverage for new features.

- [ ] Add unit tests for fixed services
- [ ] Add integration tests for discovery sync
- [ ] Add E2E tests for protocol run flow (when Playwright works)

---

## 🔧 Development Commands Reference

### Start All Services
```bash
# Terminal 1: Database
make db-test

# Terminal 2: Keycloak
docker-compose up keycloak

# Terminal 3: Backend
PRAXIS_DB_DSN="postgresql+asyncpg://test_user:test_password@localhost:5433/test_db" \
  uv run uvicorn main:app --reload --port 8000

# Terminal 4: Frontend
cd praxis/web-client && npm start
```

### Discovery Sync
```bash
# Sync PLR type definitions to database
curl -X POST http://localhost:8000/api/v1/discovery/sync-all

# Verify definitions synced
curl http://localhost:8000/api/v1/assets/definitions | python3 -c "import sys,json; print(f'{len(json.load(sys.stdin))} definitions')"
```

### Database Operations
```bash
# Run migrations
PRAXIS_DB_DSN="postgresql+asyncpg://test_user:test_password@localhost:5433/test_db" \
  uv run alembic upgrade head

# Generate new migration
PRAXIS_DB_DSN="postgresql+asyncpg://test_user:test_password@localhost:5433/test_db" \
  uv run alembic revision --autogenerate -m "description"
```

---

## 📦 Files Modified (Dec 21, 2025)

### Phase 1 Changes (Protocol Library & Simulation Mode)

| File | Change |
|------|--------|
| `praxis/protocol/protocols/simple_transfer.py` | NEW: Example protocol for basic liquid transfer |
| `praxis/protocol/protocols/serial_dilution.py` | NEW: Example protocol for serial dilution |
| `praxis/protocol/protocols/plate_preparation.py` | NEW: Example protocol for plate preparation |
| `praxis/protocol/protocols/__init__.py` | NEW: Package init exporting protocols |
| `praxis/backend/core/protocols/orchestrator.py` | Added `is_simulation` param to `IOrchestrator` |
| `praxis/backend/core/protocol_execution_service.py` | Added `is_simulation` param to execution methods |
| `praxis/backend/core/orchestrator/execution.py` | Added `is_simulation` param to `ExecutionMixin` |
| `praxis/backend/configure.py` | Fixed `default_protocol_dir` path resolution |
| `praxis/backend/services/discovery_service.py` | Added async function support, decorator detection, asset field fixes |
| `praxis/backend/services/protocol_definition.py` | Fixed ORM object conversion for params/assets |
| `main.py` | Added `protocol_definition_service` to `DiscoveryService` init |

### Earlier Changes (API Fixes & Discovery)

| File | Change |
|------|--------|
| `praxis/web-client/src/app/features/protocols/services/protocol.service.ts` | Fixed endpoint to `/protocols/definitions` |
| `praxis/web-client/src/app/features/assets/services/asset.service.ts` | Fixed definition endpoints |
| `praxis/web-client/src/app/features/assets/services/asset.service.spec.ts` | Updated test expectations |
| `praxis/web-client/src/app/features/protocols/services/protocol.service.spec.ts` | Updated test expectations |
| `praxis/backend/services/resource_type_definition.py` | Changed `ImportError` to `Exception` |
| `praxis/backend/models/orm/plr_sync.py` | Removed unique constraint from `name` |
| `main.py` | Added `praxis_config` to app.state |
| `alembic/versions/577d92edf9a5_remove_unique_from_name.py` | NEW: Migration for unique constraint |

---

## 🔗 Related Documentation

- [FRONTEND_DEV.md](./FRONTEND_DEV.md) - Frontend development phases
- [BACKEND_STATUS.md](./BACKEND_STATUS.md) - Backend task tracking
- [GEMINI.md](/GEMINI.md) - Agent instructions and architecture overview
