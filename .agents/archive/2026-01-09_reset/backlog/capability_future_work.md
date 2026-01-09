# Capability Tracking - Future Work (Phases 5-6)

**Status**: Deferred / Future
**Origin**: Extracted from `capability_tracking.md` on 2026-01-07

---

## Phase 5: Deep Protocol Inspection

Link protocol discovery to capability matching (see [protocol_inspection.md](./protocol_inspection.md) Phase 2):

- [ ] **Requirements Integration**: After extracting function metadata, run `ProtocolRequirementExtractor` on function body.
- [ ] **Requirement Storage**: Store `ProtocolRequirements` in `ProtocolFunctionInfo`.
- [ ] **ORM Mapping**: Add `hardware_requirements_json` JSONB field to `FunctionProtocolDefinitionOrm`.
- [ ] **Machine Type Inference**: Add `machine_type` to protocol definition (inferred from requirements).

### 5.1 Call Graph Analysis (Future)

- [ ] Extract function calls within protocol body.
- [ ] Identify nested protocol function calls.
- [ ] Build dependency DAG for protocol execution order.

### 5.2 Resource Flow Analysis (Future)

- [ ] Track PLR resource usage through function body.
- [ ] Identify resource allocation/deallocation patterns.
- [ ] Detect potential resource conflicts.

---

## Phase 6: Resource Capability & Constraint Matching (Future)

### 6.1 Resource Requirement Extraction

- [ ] Extract specific resource constraints from protocols (e.g., `num_wells`, `well_volume`, `bottom_type`).
- [ ] Infer required resource capabilities (e.g., "must be pierceable", "must be stackable").

### 6.2 Inventory Matching Service

- [ ] Match extracted protocol resource requirements against available Lab Assets (inventory).
- [ ] Validate if physical assets assigned to a protocol run satisfy the technical constraints of the protocol.

### 6.3 Placement Validation

- [ ] Real-time validation of resource placement on deck based on physical constraints and protocol needs.
