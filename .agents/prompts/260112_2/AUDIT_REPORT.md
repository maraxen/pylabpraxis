# Domain Model Relationship Audit Report

## Executive Summary

- **Total Models Audited**: 15 Files (~35 Models)
- **Critical Issues**: High (Missing Relationships for defined Foreign Keys)
- **Warnings**: Moderate (Orphaned Relationships or missing `back_populates`)
- **Status**: Significant gaps in ORM relationship definitions across the domain model layer. Most Foreign Key columns are defined but lack corresponding `Relationship` attributes, preventing `joinedload` and relationship navigation.

## Findings by File

### 1. `praxis/backend/models/domain/protocol.py`

**Status**: ⚠️ Critical Issues Found

| Model | Line | FK Column | Relationship Field | Severity | Notes |
|-------|------|-----------|-------------------|----------|-------|
| `FunctionProtocolDefinition` | 285 | `source_repository_accession_id` | ❌ Missing | Critical | Links to `ProtocolSourceRepository` |
| `FunctionProtocolDefinition` | 288 | `file_system_source_accession_id` | ❌ Missing | Critical | Links to `FileSystemProtocolSource` |
| `KeyParameter` | - | `protocol_definition_accession_id` (in `ParameterDefinition`) | ❌ Missing `parameters` list in Parent | Warning | `FunctionProtocolDefinition` lacks `parameters` relationship |
| `ProtocolRun` | 361 | `top_level_protocol_definition_accession_id` | ❌ Missing | Critical | Core link to `FunctionProtocolDefinition` |
| `ProtocolRun` | 364 | `previous_accession_id` | ❌ Missing | Critical | Self-referential (previous run) |
| `FunctionCallLog` | 419 | `protocol_run_accession_id` | ❌ Missing | Critical | Link to `ProtocolRun` |
| `FunctionCallLog` | 420 | `function_protocol_definition_accession_id` | ❌ Missing | Critical | Link to `FunctionProtocolDefinition` |
| `FunctionCallLog` | 423 | `parent_function_call_log_accession_id` | ❌ Missing | Critical | Self-referential (parent call) |

### 2. `praxis/backend/models/domain/schedule.py`

**Status**: ⚠️ Critical Issues Found

| Model | Line | FK Column | Relationship Field | Severity | Notes |
|-------|------|-----------|-------------------|----------|-------|
| `ScheduleEntry` | 71 | `protocol_run_accession_id` | ❌ Missing | Critical | Link to `ProtocolRun` |
| `AssetReservation` | 138 | `asset_accession_id` | ❌ Missing | Warning | "Soft FK" - consider Generic Relationship? |
| `AssetReservation` | 140 | `schedule_entry_accession_id` | ❌ Missing | Critical | Link to `ScheduleEntry` |
| `AssetReservation` | 143 | `protocol_run_accession_id` | ❌ Missing | Critical | Link to `ProtocolRun` |
| `ScheduleHistory` | 198 | `schedule_entry_accession_id` | ❌ Missing | Critical | Link to `ScheduleEntry` |

### 3. `praxis/backend/models/domain/machine.py`

**Status**: ⚠️ Critical Issues Found

| Model | Line | FK Column | Relationship Field | Severity | Notes |
|-------|------|-----------|-------------------|----------|-------|
| `MachineDefinition` | 77 | `resource_definition_accession_id` | ❌ Missing | Critical | Link to `ResourceDefinition` |
| `MachineDefinition` | 82 | `deck_definition_accession_id` | ❌ Missing | Critical | Link to `DeckDefinition` |
| `MachineDefinition` | 87 | `asset_requirement_accession_id` | ❌ Missing | Critical | Link to `AssetRequirement` |
| `Machine` | 179 | `resource_counterpart_accession_id` | ❌ Missing | Critical | Link to `Resource` |
| `Machine` | 184 | `deck_child_accession_id` | ❌ Missing | Critical | Link to `Deck` |
| `Machine` | 187 | `deck_child_definition_accession_id` | ❌ Missing | Critical | Link to `DeckDefinition` |
| `Machine` | 192 | `current_protocol_run_accession_id` | ❌ Missing | Critical | Link to `ProtocolRun` |
| `Machine` | 197 | `machine_definition_accession_id` | ❌ Missing | Critical | Link to `MachineDefinition` |

### 4. `praxis/backend/models/domain/resource.py`

**Status**: ⚠️ Critical Issues Found

| Model | Line | FK Column | Relationship Field | Severity | Notes |
|-------|------|-----------|-------------------|----------|-------|
| `ResourceDefinition` | 69 | `deck_definition_accession_id` | ❌ Missing | Critical | Link to `DeckDefinition` |
| `ResourceDefinition` | 75 | `asset_requirement_accession_id` | ❌ Missing | Critical | Link to `AssetRequirement` |
| `Resource` | 158 | `current_protocol_run_accession_id` | ❌ Missing | Critical | Commented out in code |

### 5. `praxis/backend/models/domain/outputs.py`

**Status**: ⚠️ Critical Issues Found

| Model | Line | FK Column | Relationship Field | Severity | Notes |
|-------|------|-----------|-------------------|----------|-------|
| `FunctionDataOutput` | 67 | `function_call_log_accession_id` | ❌ Missing | Critical | |
| `FunctionDataOutput` | 70 | `protocol_run_accession_id` | ❌ Missing | Critical | |
| `FunctionDataOutput` | 73 | `machine_accession_id` | ❌ Missing | Critical | |
| `FunctionDataOutput` | 76 | `resource_accession_id` | ❌ Missing | Critical | |
| `FunctionDataOutput` | 79 | `deck_accession_id` | ❌ Missing | Critical | |
| `FunctionDataOutput` | 82 | `derived_from_data_output_accession_id` | ❌ Missing | Critical | Self-ref |
| `WellDataOutput` | 161 | `function_data_output_accession_id` | ❌ Missing | Critical | |
| `WellDataOutput` | 164 | `resource_accession_id` | ❌ Missing | Critical | |
| `WellDataOutput` | 167 | `plate_resource_accession_id` | ❌ Missing | Critical | |

### 6. `praxis/backend/models/domain/resolution.py`

**Status**: ⚠️ Critical Issues Found

| Model | Line | FK Column | Relationship Field | Severity | Notes |
|-------|------|-----------|-------------------|----------|-------|
| `StateResolutionLog` | 45 | `schedule_entry_accession_id` | ❌ Missing | Critical | |
| `StateResolutionLog` | 48 | `protocol_run_accession_id` | ❌ Missing | Critical | |

### 7. Other Files

- **`deck.py`**: Reference implementation (✅ Good).
- **`workcell.py`**: Generally good. `decks` relationship commented out, but no `deck` FK column exists on `Workcell` (likely indirect via Machine).
- **`protocol_source.py`**: Relationships appear correct.
- **`user.py`**: Standalone, no relationships.

---

## Remediation Plan

The following models require updates to add `Relationship` fields. This should be prioritized to prevent downstream test failures and enable navigation.

### Priority 1: Core Execution & Scheduling

**Rationale**: Essential for Protocol Runner and Scheduler services.

- Update `praxis/backend/models/domain/protocol.py` (Add 8+ Relationships)
- Update `praxis/backend/models/domain/schedule.py` (Add 4+ Relationships)
- Update `praxis/backend/models/domain/resolution.py` (Add 2 Relationships)

### Priority 2: Inventory & Machines

**Rationale**: Essential for Inventory Management and Asset tracking.

- Update `praxis/backend/models/domain/machine.py` (Add 8+ Relationships)
- Update `praxis/backend/models/domain/resource.py` (Add 3+ Relationships)

### Priority 3: Data & Outputs

**Rationale**: Essential for Data Collection services.

- Update `praxis/backend/models/domain/outputs.py` (Add 9+ Relationships)

### Estimated Effort

- **High Complexity**: `protocol.py`, `machine.py` (Many FKs, some self-referential)
- **Medium Complexity**: `schedule.py`, `outputs.py`, `resource.py`
- **Low Complexity**: `resolution.py`
