# SPLIT-05: Decompose plr_inspection.py (Backend)

## Context

**File**: `backend/utils/plr_inspection.py`
**Current Size**: 716 lines
**Goal**: Extract inspection utilities into focused modules

## Architecture Analysis

PLR (PyLabRobot) inspection likely contains:

1. **Static Analysis**: AST parsing, type extraction
2. **Runtime Inspection**: Object introspection
3. **Documentation Extraction**: Docstring parsing
4. **Validation**: Schema validation, compatibility checks

## Requirements

### Phase 1: Analyze and Categorize

1. Read file and identify distinct functionalities
2. Map internal dependencies
3. Note which functions are public API

### Phase 2: Extract Modules

1. `plr_static.py` - Static analysis functions
2. `plr_runtime.py` - Runtime inspection
3. `plr_docs.py` - Documentation extraction
4. `plr_validation.py` - Validation utilities
5. Maintain `__init__.py` for backward compatibility

### Phase 3: Verification

1. `uv run pytest backend/utils/` passes
2. `uv run mypy backend/` passes
3. Integration with callers verified

## Acceptance Criteria

- [ ] Logical separation into focused modules
- [ ] All tests pass
- [ ] Backward-compatible imports
- [ ] Commit: `refactor(backend/plr_inspection): modularize inspection utilities`

## Anti-Requirements

- Do NOT change function signatures
- Do NOT alter inspection behavior
