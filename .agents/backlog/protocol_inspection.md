# Protocol Inspection with LibCST

**Priority**: HIGH
**Owner**: Full Stack
**Created**: 2025-12-30
**Status**: Phase 1 Complete, Phase 2 Next

---

## Overview

Migrate protocol inspection from stdlib `ast` to LibCST for safer, more robust parsing of `@protocol_function` decorated functions. This aligns with the existing PLR static analysis infrastructure that already uses LibCST for machine/backend/resource discovery.

**Current State**: `discovery_service.py` uses `ast.NodeVisitor` (`ProtocolVisitor`) to extract protocol metadata. This approach works but lacks the safety and flexibility of LibCST.

**Goal**: Unify all Python source parsing under LibCST, enabling:

1. **Consistent tooling** - One parsing framework across all static analysis
2. **Safer refactoring** - LibCST preserves formatting and enables codemods
3. **Richer analysis** - Type annotation resolution, docstring handling
4. **Integration** - Link `ProtocolRequirementExtractor` capability inference to discovery

---

## Phase 1: Replace ProtocolVisitor with LibCST (Immediate)

**Status**: ✅ Phase 1 Complete (2025-12-30)

### 1.1 Create LibCST Protocol Visitor

Create `praxis/backend/utils/plr_static_analysis/visitors/protocol_discovery.py`:

- [x] Define `ProtocolFunctionVisitor(cst.CSTVisitor)`
- [x] Handle `@protocol_function` decorator detection (simple name, call, attribute)
- [x] Extract function parameters with type hints
- [x] Extract function docstrings
- [x] Identify PLR asset parameters vs regular parameters
- [x] Build `ProtocolFunctionInfo` Pydantic model

### 1.2 Update Discovery Service

- [x] Replace `ProtocolVisitor` (ast) with LibCST-based visitor
- [x] Update `_extract_protocol_definitions_from_paths()` to use LibCST
- [x] Maintain backward compatibility with existing return format

### 1.3 Testing

- [x] Update `test_discovery_service.py` tests to verify new implementation
- [x] Add unit tests for `ProtocolFunctionVisitor` in `test_plr_static_analysis.py`

---

## Phase 2: Integrate Requirements Extraction (Short-term)

**Status**: ⏳ Next

### 2.1 Link to ProtocolRequirementExtractor

- [ ] After extracting function metadata, run `ProtocolRequirementExtractor` on function body
- [ ] Store `ProtocolRequirements` in `FunctionProtocolDefinitionCreate`
- [ ] ORM: Add `inferred_requirements` JSONB field to `FunctionProtocolDefinitionOrm`

### 2.2 Enrich Protocol Definitions

- [ ] Add `machine_type` to protocol definition (inferred from requirements)
- [ ] Add `capability_requirements` list to protocol definition
- [ ] API: Expose requirements in protocol definition responses

---

## Phase 3: Protocol DAG Extraction (Medium-term)

**Status**: ⏳ Deferred

### 3.1 Call Graph Analysis

- [ ] Extract function calls within protocol body
- [ ] Identify nested protocol function calls
- [ ] Build dependency DAG for protocol execution order

### 3.2 Resource Flow Analysis

- [ ] Track PLR resource usage through function body
- [ ] Identify resource allocation/deallocation patterns
- [ ] Detect potential resource conflicts

---

## Phase 4: Protocol Validation (Future)

**Status**: ⏳ Deferred

### 4.1 Static Validation

- [ ] Validate PLR type hints at parse time
- [ ] Check for undefined PLR resource references
- [ ] Validate capability requirements can be satisfied

### 4.2 Pre-execution Checks

- [ ] Match protocol requirements to available hardware
- [ ] Warn about missing capabilities before execution
- [ ] Suggest alternative hardware configurations

---

## Implementation Order

| Phase | Effort | Priority | Dependencies | Status |
|-------|--------|----------|--------------|--------|
| 1.1 LibCST Visitor | M | Immediate | None | ✅ Done |
| 1.2 Update Discovery | S | Immediate | 1.1 | ✅ Done |
| 1.3 Testing | S | Immediate | 1.2 | ✅ Done |
| 2.1 Requirements Link | M | Short-term | 1.x, Phase 4-5 capability_tracking | ⏳ Next |
| 2.2 Enrich Definitions | M | Short-term | 2.1 | ⏳ Pending |
| 3.x DAG Extraction | L | Medium-term | 2.x | ⏳ Deferred |
| 4.x Validation | L | Future | 3.x | ⏳ Deferred |

---

## Related Files

**Current Implementation:**

- `praxis/backend/services/discovery_service.py` - Contains `ProtocolVisitor` (AST-based)

**LibCST Infrastructure:**

- `praxis/backend/utils/plr_static_analysis/parser.py` - `PLRSourceParser`
- `praxis/backend/utils/plr_static_analysis/visitors/base.py` - Base visitor classes
- `praxis/backend/utils/plr_static_analysis/visitors/class_discovery.py` - Reference implementation
- `praxis/backend/utils/plr_static_analysis/visitors/protocol_requirement_extractor.py` - Requirement inference

**Tests:**

- `tests/services/test_discovery_service.py` - Protocol discovery tests
- `tests/utils/test_plr_static_analysis.py` - Static analysis tests

---

## Success Metrics

1. [x] All existing `test_discovery_service.py` tests pass with LibCST implementation
2. [x] Protocol discovery returns identical results to current AST-based implementation
3. [x] New unit tests cover LibCST visitor edge cases
4. [x] No runtime AST imports in discovery service

---

## Related Backlog Items

- [capability_tracking.md](./capability_tracking.md) - Phase 4-5 depend on this work
- [backend.md](./backend.md) - Service layer updates
