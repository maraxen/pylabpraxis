# SPLIT-06: Decompose resource_type_definition.py (Backend)

## Context

**File**: `backend/services/resource_type_definition.py`
**Current Size**: 701 lines
**Goal**: Extract into focused service modules

## Architecture Analysis

Resource type definition service likely contains:

1. **CRUD Operations**: Create, read, update, delete
2. **Validation**: Schema validation, constraints
3. **Serialization**: Model transformations
4. **Query Builders**: Complex lookups

## Requirements

### Phase 1: Analyze

1. Identify distinct responsibilities
2. Map database interactions
3. Note dependencies on other services

### Phase 2: Extract

1. `resource_type_crud.py` - CRUD operations
2. `resource_type_validation.py` - Validation logic
3. `resource_type_queries.py` - Complex queries
4. Main service file orchestrates these

### Phase 3: Verify

1. All tests pass
2. API endpoints still work
3. No changes to external behavior

## Acceptance Criteria

- [ ] Clear separation of CRUD, validation, queries
- [ ] Tests pass
- [ ] Commit: `refactor(backend/services): modularize resource_type_definition`

## Anti-Requirements

- Do NOT change API contracts
- Do NOT modify database schema
