# Track A: Operation "First Light" – End-to-End Protocol Execution

**Goal**: Users can run `simple_transfer.py` successfully from start to finish.

**Last Updated**: 2025-12-22

---

## 🎯 Success Criteria

A user can:

1. Navigate to Protocol Library → Select `simple_transfer` protocol
2. Complete the Protocol Wizard with **real resource binding**
3. Click "Start Execution"
4. See protocol run to completion (simulation mode)
5. View execution logs and results

---

## 📋 Current State Analysis

### ✅ What Works Today

| Component | Status | Notes |
|-----------|--------|-------|
| Protocol Discovery | ✅ | 3 protocols synced via AST parsing |
| Protocol Library UI | ✅ | `ProtocolLibraryComponent` lists protocols |
| Protocol Wizard Base | ✅ | 4-step stepper in `RunProtocolComponent` |
| Parameter Config | ✅ | Dynamic Formly-based rendering |
| `asset-selector` Type | ⚠️ | Exists but selects *existing assets*, not definitions |
| Backend Execution | ✅ | `ExecutionMixin.execute_protocol` complete |
| WebSocket Logs | ✅ | Real-time log streaming implemented |
| Simulation Flag | ✅ | `is_simulation` param flows through stack |

### ❌ Critical Gap: Resource Binding

**Problem**: The `simple_transfer.py` protocol requires 3 assets:

- `source_plate: Plate`
- `dest_plate: Plate`
- `tip_rack: TipRack`

**Current Behavior**:

- `asset-selector` component searches **existing resource instances** (from `AssetService.getResources()`)
- User must have previously created resource instances matching these types
- No mechanism to create resources inline or select from ResourceDialog

**Required Behavior**:

- For each `plr_type` asset parameter, user should either:
  1. **Select existing resource** (if any match the type hint), OR
  2. **Create new resource** using `ResourceDialogComponent` (which browses `ResourceDefinition`s)

---

## 🔧 Implementation Steps

### Phase A.1: Minimum Viable Resource Binding

**Goal**: Allow protocol wizard to bind asset parameters to existing resources.

#### Frontend Tasks

##### A.1.1 Enhance `ParameterConfigComponent`

- **File**: `praxis/web-client/src/app/features/run-protocol/components/parameter-config/parameter-config.component.ts`
- **Changes**:
  - For asset parameters (those with `plr_type` metadata), use `asset-selector` type
  - Pass `assetType: 'resource'` and optionally `plrTypeFilter: param.plr_type` to filter by type

##### A.1.2 Enhance `AssetSelectorComponent`

- **File**: `praxis/web-client/src/app/shared/formly-types/asset-selector.component.ts`
- **Changes**:
  - Accept optional `plrTypeFilter` prop in `to` (template options)
  - Filter displayed resources by matching `resource_definition.name` or category against `plrTypeFilter`
  - Show "Create New" button that opens `ResourceDialogComponent`

##### A.1.3 Return ID from `AssetSelectorComponent`

- **File**: `praxis/web-client/src/app/shared/formly-types/asset-selector.component.ts`
- **Changes**:
  - Ensure form value is the `accession_id` string (not the full object)
  - Backend expects asset IDs to resolve during execution

---

### Phase A.2: Backend Asset Resolution

**Goal**: Ensure backend can resolve asset IDs to PLR instances.

#### Backend Tasks

##### A.2.1 Verify Asset Resolution in Orchestrator

- **File**: `praxis/backend/core/orchestrator/execution.py`
- **Check**: `_prepare_arguments` method resolves asset accession_ids to ORM objects
- **Check**: `_execute_protocol_main_logic` acquires assets via `AssetManager`

##### A.2.2 Ensure `AssetManager.acquire_asset` Handles Resource IDs

- **File**: `praxis/backend/core/asset_manager/` (mixin files)
- **Check**: Can acquire resource by `accession_id`
- **Check**: Returns a PLR-compatible object (or simulation stub)

---

### Phase A.3: Execution Flow Integration

**Goal**: Wire up the complete flow from wizard to execution.

#### Frontend Tasks

##### A.3.1 Update `startRun()` in `RunProtocolComponent`

- **File**: `praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts`
- **Changes**:
  - Collect asset accession_ids from `parametersFormGroup`
  - Pass to `ExecutionService.startRun()` with proper structure

##### A.3.2 Add `is_simulation` Toggle

- **File**: `praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts`
- **Changes**:
  - Add checkbox/toggle: "Run in Simulation Mode"
  - Default to `true` for safety
  - Pass to backend via `ExecutionService`

#### Backend Tasks

##### A.3.3 Update Run API Endpoint

- **File**: `praxis/backend/api/protocols.py` (or relevant endpoint)
- **Check**: Accepts `is_simulation` parameter
- **Check**: Accepts asset bindings in expected format

---

### Phase A.4: Verification & Polish

#### A.4.1 Manual E2E Test: Simple Transfer

1. Start backend with test DB
2. Run `POST /api/v1/discovery/sync-all`
3. Navigate to Protocol Library
4. Select "simple_transfer"
5. In Parameter Config:
   - Select/create a source plate
   - Select/create a destination plate
   - Select/create a tip rack
6. Proceed to Review & Run
7. Click "Start Execution" (simulation mode)
8. Verify:
   - Protocol run created (visible in dashboard)
   - Logs stream via WebSocket
   - Status progresses: PREPARING → RUNNING → COMPLETED
   - Final state shows transfer results

---

## 📁 Key Files Reference

| Purpose | File Path |
|---------|-----------|
| Protocol Wizard | `praxis/web-client/src/app/features/run-protocol/run-protocol.component.ts` |
| Parameter Config | `praxis/web-client/src/app/features/run-protocol/components/parameter-config/parameter-config.component.ts` |
| Asset Selector | `praxis/web-client/src/app/shared/formly-types/asset-selector.component.ts` |
| Resource Dialog | `praxis/web-client/src/app/features/assets/components/resource-dialog/resource-dialog.component.ts` |
| Execution Service | `praxis/web-client/src/app/features/run-protocol/services/execution.service.ts` |
| Backend Execution | `praxis/backend/core/orchestrator/execution.py` |
| Asset Manager | `praxis/backend/core/asset_manager/` |
| Example Protocol | `praxis/protocol/protocols/simple_transfer.py` |

---

## ⚠️ Constraints

1. **NO AI/LLM features** – All resource filtering must be deterministic
2. **Simulation first** – Real hardware integration deferred
3. **Reuse existing components** – `ResourceDialogComponent` already works for browsing definitions

---

## 📊 Estimated Effort

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| A.1 Minimum Resource Binding | 4-6 hours | None |
| A.2 Backend Asset Resolution | 2-3 hours | A.1 |
| A.3 Execution Flow Integration | 2-3 hours | A.1, A.2 |
| A.4 Verification & Polish | 2-3 hours | A.1, A.2, A.3 |
| **Total** | **10-15 hours** | |
