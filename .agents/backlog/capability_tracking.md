# Capability Tracking System Backlog

**Priority**: HIGH
**Owner**: Full Stack
**Created**: 2025-12-30
**Status**: Phase 1-4 MVP Complete

---

## Overview

A comprehensive system for tracking hardware capabilities across all PLR machine types, enabling:

1. **Discovery**: Automatically identify capabilities from PLR source via LibCST
2. **User Configuration**: Allow users to specify optional/configurable capabilities during setup
3. **Protocol Matching**: Match protocol requirements to available hardware capabilities

---

## Current State Issues

### 1. Classification Bug - ✅ FIXED (2025-12-30)

- ~~`LiquidHandler` inherits from both `Resource` and `Machine`~~
- ~~Current classifier prioritizes `Resource` base, misclassifying frontends~~
- **Fix Applied**: Classification now checks `base_set_with_self` and prioritizes machine bases before resource bases

### 2. Limited Machine Coverage - ✅ FIXED (2025-12-30)

Now covers all 15 machine types with 21 frontends and 70 backends discovered:

- [x] LiquidHandler
- [x] PlateReader (includes Imager, ImageReader)
- [x] HeaterShaker
- [x] Shaker
- [x] Centrifuge
- [x] Pump, PumpArray
- [x] Thermocycler
- [x] TemperatureController
- [x] Incubator
- [x] Sealer
- [x] Peeler
- [x] PowderDispenser
- [x] Fan
- [x] SCARA Arms (ExperimentalSCARA)

### 3. Hamilton-Specific Capabilities - ⏳ PHASE 2

Current capability model is Hamilton-centric:

- `has_iswap`, `has_core96` - Hamilton liquid handler specific
- `channels` - Only relevant for liquid handlers

Need generic, machine-type-specific capability schemas.

### 4. Backend-Frontend Mapping - ✅ FIXED (2025-12-30)

- ~~Frontends not being assigned `compatible_backends`~~
- **Fix Applied**: Classification priority fixed, backends now correctly mapped

### 5. No User-Configurable Capabilities - ⏳ PHASE 3

- Users cannot specify optional capabilities during machine setup
- Example: "Does your STAR have iSWAP installed?" should be asked during setup

---

## Phase 1: Fix Core Issues (Immediate) - ✅ COMPLETED 2025-12-30

### 1.1 Fix Classification Priority ✅

- Updated `ClassDiscoveryVisitor` to check machine bases before resource bases
- Added `ALL_MACHINE_FRONTEND_BASES` and `ALL_MACHINE_BACKEND_BASES` sets
- Classification now uses `base_set_with_self` to also match the class name itself
- Classification order: Machine backends → Machine frontends → Infrastructure → Resources

### 1.2 Expand Machine Type Discovery ✅

Implemented in `class_discovery.py`:

- Added 15 frontend base class sets (LIQUID_HANDLER_BASES, HEATER_SHAKER_BASES, etc.)
- Added 15 backend base class sets (LH_BACKEND_BASES, HS_BACKEND_BASES, etc.)
- Added `ALL_MACHINE_FRONTEND_BASES` and `ALL_MACHINE_BACKEND_BASES` combined sets
- Updated `PLRClassType` enum with all 15 machine types and their backends
- Added `MACHINE_FRONTEND_TYPES`, `MACHINE_BACKEND_TYPES`, `FRONTEND_TO_BACKEND_MAP` for type checking
- Expanded `MACHINE_PATTERNS` in parser.py from 7 to 15 directories

**Results**: Now discovers 21 machine frontends and 70 backends across 15 machine types.

### 1.3 Fix Backend-Frontend Mapping ✅

- Classification priority fixed (backends → frontends → infrastructure → resources)
- `compatible_backends` population works correctly with new classification

---

## Phase 2: Generic Capability Model (Short-term) - ✅ COMPLETED 2025-12-30

### 2.1 Machine-Type Specific Capability Schemas ✅

Implemented 15 machine-type-specific capability schemas in `models.py`:

- `LiquidHandlerCapabilities` - channels, iswap, core96, hepa
- `PlateReaderCapabilities` - absorbance, fluorescence, luminescence, imaging
- `HeaterShakerCapabilities` - temperature, speed, cooling
- `ShakerCapabilities` - speed, orbit diameter
- `TemperatureControllerCapabilities` - temperature range, cooling
- `CentrifugeCapabilities` - rpm, g-force, temperature control
- `ThermocyclerCapabilities` - temperature, ramp rate, heated lid
- `PumpCapabilities` - flow rate, reversible, channels
- `FanCapabilities` - speed, variable control
- `SealerCapabilities` - temperature, seal time
- `PeelerCapabilities` - (no configurable capabilities)
- `PowderDispenserCapabilities` - dispense range
- `IncubatorCapabilities` - temperature, CO2, humidity
- `ScaraCapabilities` - reach, payload
- `GenericMachineCapabilities` - raw capability dict fallback

Added `MachineCapabilities` union type and `machine_capabilities` field on `DiscoveredClass`.

### 2.2 Update Capability Extraction ✅

Extended `CapabilityExtractorVisitor` in `capability_extractor.py`:

- Added `class_type` parameter to constructor for type-specific detection
- Implemented `_signals` dict for collecting type-specific capabilities
- Added `_extract_typed_param()` for **init** parameter extraction
- Extended `_detect_capabilities_from_method_name()` with patterns for:
  - PlateReader: absorbance, fluorescence, luminescence, imaging
  - HeaterShaker/TempController: cooling methods
  - Pump: reversible flow
  - Incubator: CO2/humidity control
  - Thermocycler: heated lid
  - Fan: variable speed
- Added `build_machine_capabilities()` method to construct typed capability schemas
- Updated `parser.py` to pass class_type and build machine_capabilities

### 2.3 Testing & Documentation ✅

- Added 8 new tests in `test_plr_static_analysis.py`:
  - `TestMachineCapabilitySchemas` (6 tests) - unit tests for Pydantic models
  - `TestCapabilityExtraction` (2 tests) - integration tests for extraction
- Created `plr-capability-update.md` prompt for maintaining capability tracking

---

## Phase 3: User-Configurable Capabilities (Medium-term) - ✅ MVP COMPLETED 2025-12-30

### 3.1 Backend: Capability Configuration Schema ✅

Implemented in `models.py`:

```python
class CapabilityConfigField(BaseModel):
    field_name: str
    display_name: str
    field_type: Literal["boolean", "number", "select", "multiselect"]
    default_value: Any
    options: list[str] | None = None
    help_text: str | None = None
    depends_on: str | None = None

class MachineCapabilityConfigSchema(BaseModel):
    machine_type: str
    machine_fqn_pattern: str | None = None
    config_fields: list[CapabilityConfigField]
```

Added `capabilities_config` field to `DiscoveredClass` for carrying schema through discovery.

### 3.2 ORM Updates ✅

- Added `user_configured_capabilities` JSON field to `MachineOrm`
- Added `capabilities_config` JSON field to `MachineDefinitionOrm`
- Updated `MachineBase`, `MachineUpdate`, `MachineDefinitionBase`, `MachineDefinitionUpdate` Pydantic models

### 3.3 Frontend: Machine Setup Dialog Enhancement ✅ (MVP)

- Updated `machine-dialog.component.ts` with JSON capability input field
- Added TypeScript interfaces for `MachineCapabilityConfigSchema` and `CapabilityConfigField`
- User can specify `user_configured_capabilities` as JSON during machine creation

### 3.4 Dynamic Form Generation ✅ COMPLETED 2025-12-30

> **See**: [dynamic_form_generation.md](./dynamic_form_generation.md) for full implementation plan.

Replace JSON textarea with auto-generated forms:

- [x] Backend: Create capability config templates per machine type
- [x] Backend: Generate schemas during PLR static analysis
- [x] Frontend: Create `DynamicCapabilityFormComponent`
- [x] Frontend: Integrate into MachineDialogComponent

---

## Phase 4: Protocol Capability Matching - ✅ MVP COMPLETED 2025-12-30

### 4.1 Protocol Asset Requirements ✅

- Implemented `ProtocolRequirementExtractor` (LibCST visitor)
- Extract required capabilities from protocols via LibCST
- Example: Protocol uses `lh.pick_up_tips96()` → requires `has_core96=True`
- Added `hardware_requirements_json` to `FunctionProtocolDefinitionOrm`

### 4.2 Capability Matching Service ✅

- Created `CapabilityMatcherService`:

  ```python
  class CapabilityMatcherService:
      def match_protocol_to_machine(self, protocol, machine) -> CapabilityMatchResult
  ```

- Supports matching against discovered AND user-configured capabilities
- Returns detailed match result with missing capabilities and warnings
- [ ] **Backlog**: Review all machine methods/capabilities to ensure general support (not just `has_core96` but generic "96-channel head", etc.)

### 4.3 UI Integration - ✅ COMPLETED 2025-12-30

- Show capability mismatches during protocol setup
- Machine Selection step added to Run Protocol Wizard
- Visual indicators (Green/Red/Yellow) for compatibility status
- Suggest alternative machines if requirements not met

---

## Phase 5: Deep Protocol Inspection - ✅ PHASE 1 COMPLETE 2025-12-30

> **Note**: This phase is now aligned with [protocol_inspection.md](./protocol_inspection.md). See that document for detailed implementation status.

### 5.1 Protocol Function Parser ✅ COMPLETE

Implemented in `praxis/backend/utils/plr_static_analysis/visitors/protocol_discovery.py`:

- [x] `ProtocolFunctionVisitor(cst.CSTVisitor)` for LibCST-based parsing
- [x] Handle `@protocol_function` decorator detection (simple name, call, attribute)
- [x] Extract function parameters with type hints
- [x] Extract function docstrings
- [x] Identify PLR asset parameters vs regular parameters
- [x] Build `ProtocolFunctionInfo` Pydantic model
- [x] Discovery service updated to use LibCST (replaced AST-based `ProtocolVisitor`)

### 5.2 Requirements Integration ✅ COMPLETED 2025-12-30

Link protocol discovery to capability matching (see [protocol_inspection.md](./protocol_inspection.md) Phase 2):

- [x] After extracting function metadata, run `ProtocolRequirementExtractor` on function body
- [x] Store `ProtocolRequirements` in `ProtocolFunctionInfo`
- [x] ORM: Add `hardware_requirements_json` JSONB field to `FunctionProtocolDefinitionOrm`
- [x] Add `machine_type` to protocol definition (inferred from requirements)

### 5.3 Call Graph Analysis (Future)

- [ ] Extract function calls within protocol body
- [ ] Identify nested protocol function calls
- [ ] Build dependency DAG for protocol execution order

### 5.4 Resource Flow Analysis (Future)

- [ ] Track PLR resource usage through function body
- [ ] Identify resource allocation/deallocation patterns
- [ ] Detect potential resource conflicts

---

## Phase 6: Resource Capability & Constraint Matching (Future)

### 6.1 Resource Requirement Extraction

- Extract specific resource constraints from protocols (e.g., `num_wells`, `well_volume`, `bottom_type`).
- Infer required resource capabilities (e.g., "must be pierceable", "must be stackable").

### 6.2 Inventory Matching Service

- Match extracted protocol resource requirements against available Lab Assets (inventory).
- Validate if physical assets assigned to a protocol run satisfy the technical constraints of the protocol.

### 6.3 Placement Validation

- Real-time validation of resource placement on deck based on physical constraints and protocol needs.

```

---

## Implementation Order

| Phase | Effort | Priority | Dependencies | Status |
|-------|--------|----------|--------------|--------|
| 1.1 Fix Classification | S | Immediate | None | ✅ Done |
| 1.2 Expand Machine Types | M | Immediate | 1.1 | ✅ Done |
| 1.3 Fix Backend-Frontend Map | S | Immediate | 1.1 | ✅ Done |
| 2.1 Capability Schemas | M | Short-term | 1.x | ✅ Done |
| 2.2 Capability Extraction | M | Short-term | 2.1 | ✅ Done |
| 3.1 Config Schema | M | Medium-term | 2.x | ✅ Done |
| 3.2 Frontend Dialog | L | Medium-term | 3.1 | ✅ MVP Done |
| 3.3 ORM Updates | S | Medium-term | 3.1 | ✅ Done |
| 4.1 Requirement Extraction | M | Medium-term | 2.x | ✅ Done |
| 4.2 Capability Matcher | M | Medium-term | 4.1 | ✅ Done |
| 4.3 UI Integration | L | Future | 4.2 | ✅ Done |
| 5.x Protocol Inspection | L | Future | 2.x | Deferred |
| 6.x Resource Matching | L | Future | 5.x | Pending |

---

## Related Files

**Backend:**

- `praxis/backend/utils/plr_static_analysis/visitors/class_discovery.py`
- `praxis/backend/utils/plr_static_analysis/visitors/capability_extractor.py`
- `praxis/backend/utils/plr_static_analysis/models.py`
- `praxis/backend/models/orm/machine.py`
- `praxis/backend/models/pydantic_internals/machine.py`

**Frontend:**

- `praxis/web-client/src/app/features/assets/components/machine-dialog.component.ts`
- `praxis/web-client/src/app/features/assets/models/asset.models.ts`

---

## Consumable Matching Improvements ✅ COMPLETE (2026-01-02)

**Module**: `praxis/backend/core/consumable_assignment.py`

The `ConsumableAssignmentService` provides intelligent consumable assignment based on:

### Scoring Factors

| Factor | Weight | Description |
|--------|--------|-------------|
| **Volume Match** | 1.0 | Capacity meets or exceeds requirement |
| **Type Match** | 1.0 | Exact FQN > Partial > Keyword |
| **Availability** | 1.0 | Not reserved by another run |
| **Expiration** | 1.0 | Days until expiration (0 if expired) |
| **Batch Tracking** | 1.0 | Has batch/lot number, dates |

### Integration Points

- `ProtocolScheduler.analyze_protocol_requirements()` - Auto-suggests consumables
- `RuntimeAssetRequirement.suggested_asset_id` - Carries suggestion to frontend
- Frontend browser-mode equivalent (pending)

### Supported Consumable Types

- Plates (well plates, microplates)
- Tip racks
- Troughs/reservoirs
- Tubes
- Generic wells

---

## Success Metrics

1. ✅ All 15+ PLR machine types discoverable (21 frontends, 70 backends across 15 types)
2. ✅ Backend-frontend mapping 100% accurate (classification priority fixed)
3. ✅ User can configure optional capabilities during machine setup (Phase 3 Complete)
4. ✅ Protocol requirements match to available hardware (Phase 4 - Complete)
5. ✅ Deep Protocol Inspection (Phase 5 - Phase 1 & 2 Complete)
6. ✅ Consumable auto-assignment with scoring (2026-01-02)
