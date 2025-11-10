# Model Configuration Issues

This document tracks model configuration issues discovered during Phase 1 testing (ORM and Pydantic model unit tests).

## Summary

Phase 1 testing successfully validated the test infrastructure and discovered critical model mismatches that would prevent successful API integration.

**Test Results:**
- ✅ 5/5 WorkcellOrm ORM tests passing
- ✅ 10/10 WorkcellResponse Pydantic tests passing
- ⚠️ 1 test skipped due to model mismatch

## Critical Issues

### 1. WorkcellOrm Missing `fqn` Field (BLOCKING)

**Severity:** HIGH - Blocks ORM-to-Pydantic conversion for API responses

**Description:**
WorkcellOrm does not have an `fqn` (fully qualified name) field, but WorkcellResponse requires it as a mandatory field. This prevents direct ORM-to-Pydantic conversion, which is critical for API endpoints.

**Root Cause:**
```python
# praxis/backend/models/orm/asset.py:47-54
class AssetOrm(Base):
    fqn: Mapped[str] = mapped_column(String, nullable=False, ...)  # Has fqn

# praxis/backend/models/orm/machine.py, resource.py
class MachineOrm(AssetOrm): ...  # Inherits fqn from AssetOrm
class ResourceOrm(AssetOrm): ...  # Inherits fqn from AssetOrm

# praxis/backend/models/orm/workcell.py
class WorkcellOrm(Base):  # Does NOT inherit from AssetOrm - no fqn field
    name: Mapped[str] = ...
    # Missing: fqn field

# praxis/backend/models/pydantic_internals/workcell.py:30
class WorkcellBase(PraxisBaseModel):
    fqn: str = Field(description="...")  # Required, no default
```

**Database Schema Confirmation:**
```sql
test_db=> \d workcells
-- No 'fqn' column present

test_db=> \d assets
-- Has 'fqn' column (machines and resources inherit from assets table)
```

**Impact:**
- API endpoints cannot convert WorkcellOrm instances to WorkcellResponse
- Current workaround unknown (needs investigation of service layer)
- May cause runtime errors in workcell API endpoints

**Fix Options:**

1. **Add `fqn` column to workcells table** (Recommended)
   - Requires Alembic migration
   - Add to WorkcellOrm: `fqn: Mapped[str] = mapped_column(String, nullable=False, index=True)`
   - Consider default value strategy (e.g., `default=name` or computed from hierarchy)

2. **Make `fqn` optional in Pydantic models**
   - Change `fqn: str` to `fqn: str | None = None` in WorkcellBase
   - Less ideal - breaks API contract for clients expecting fqn

3. **Add computed `fqn` property to WorkcellOrm**
   - Use SQLAlchemy hybrid_property
   - Computes fqn from name or other fields
   - No migration needed, but adds computational overhead

4. **Have WorkcellOrm inherit from AssetOrm**
   - Architectural change - are workcells "assets"?
   - Would require significant refactoring

**Test Coverage:**
- Test file: `tests/models/test_pydantic/test_workcell_pydantic.py:226-273`
- Test status: Skipped with detailed documentation
- Re-enable test after fix is implemented

**Tracked In:**
- Todo: "Document found issue: WorkcellOrm missing fqn field"

---

## Configuration Issues (Non-blocking)

### 2. Pydantic `use_enum_values=True` Behavior

**Severity:** LOW - Expected behavior, but requires test awareness

**Description:**
PraxisBaseModel uses `use_enum_values=True`, which causes enum fields to be stored as their string values rather than enum instances.

**Location:**
- `praxis/backend/models/pydantic_internals/pydantic_base.py:49`

**Impact:**
```python
# Expected by developers:
workcell.status == WorkcellStatusEnum.ACTIVE  # False!

# Actual behavior:
workcell.status == "active"  # True
workcell.status == WorkcellStatusEnum.ACTIVE.value  # True
```

**Resolution:**
- Tests updated to compare against `.value` attribute
- Documented in test comments
- This is intentional design for cleaner JSON serialization
- No code changes needed

### 3. SQLAlchemy Relationship Overlap Warning

**Severity:** LOW - Informational warning

**Description:**
SQLAlchemy warning about overlapping relationships between `WorkcellOrm.resources` and `WorkcellOrm.decks`.

**Fix Applied:**
Added `overlaps="decks"` parameter to WorkcellOrm.resources relationship in `praxis/backend/models/orm/workcell.py:90`.

**Status:** RESOLVED ✅

### 4. DeckOrm Inheritance `accession_id` Warning

**Severity:** LOW - Expected for joined-table inheritance

**Description:**
SQLAlchemy warning about implicitly combining `assets.accession_id` with `decks.accession_id`.

**Location:**
- `praxis/backend/models/orm/deck.py:58`

**Analysis:**
This is expected behavior for the joined-table inheritance pattern:
- DeckOrm → ResourceOrm → AssetOrm
- Each level redefines accession_id as FK to parent table

**Status:** DOCUMENTED - No action needed

---

## Testing Methodology

### Phase 1: Model Layer Tests (Current)

**Goal:** Test ORM and Pydantic models in isolation before API integration

**Test Structure:**
```
tests/models/
├── test_orm/
│   └── test_workcell_orm.py (5 tests)
└── test_pydantic/
    └── test_workcell_pydantic.py (11 tests, 1 skipped)
```

**Test Coverage:**
- ✅ ORM model creation with defaults
- ✅ ORM persistence and retrieval
- ✅ ORM constraint enforcement (unique names)
- ✅ ORM relationship initialization
- ✅ ORM custom field values (enum status)
- ✅ Pydantic model instantiation
- ✅ Pydantic serialization (to dict/JSON)
- ✅ Pydantic deserialization (from dict/JSON)
- ✅ Pydantic enum validation
- ✅ Pydantic roundtrip serialization
- ⚠️ ORM-to-Pydantic conversion (blocked by Issue #1)

**Key Learning:**
Testing models in isolation (Phase 1) before API integration (Phase 3) successfully identified configuration issues that would have been confusing to debug at the API layer.

---

## Next Steps

### Immediate Actions:

1. **Decision needed:** Choose fix approach for Issue #1 (WorkcellOrm fqn field)
   - Recommendation: Add fqn column with Alembic migration

2. **Investigate current workarounds:**
   - Check how existing API endpoints handle WorkcellOrm → WorkcellResponse conversion
   - May reveal undocumented workarounds or broken endpoints

3. **Expand Phase 1 testing:**
   - Create similar test suites for MachineOrm/MachineResponse
   - Create similar test suites for ResourceOrm/ResourceResponse
   - Create similar test suites for DeckOrm/DeckResponse

### Future Phases:

- **Phase 2:** Service layer tests (after model issues resolved)
- **Phase 3:** API layer tests (after service layer validated)
- **Phase 4:** Core component tests (orchestration, execution)
- **Phase 5:** Integration tests (end-to-end workflows)

---

## References

- Testing Strategy: `prerelease_dev_docs/TESTING_STRATEGY.md`
- Agent Guidelines: `prerelease_dev_docs/AGENTS.md`
- Test Files: `tests/models/`

---

*Last Updated: 2025-11-10*
*Phase 1 Status: In Progress (Workcell models complete)*
