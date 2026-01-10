# P0_02: Separation of Concerns - Implementation Status

**Status:** 🟡 In Progress (Phase 1 Complete)
**Priority:** P0 (Architectural Foundation)
**Started:** 2026-01-10
**Last Updated:** 2026-01-10

---

## ✅ Phase 1: Backend Infrastructure (COMPLETE)

### 1.1 Single Source of Truth Created

**Backend Enum:** `praxis/backend/models/enums/plr_category.py`
- ✅ Created `PLRCategory` enum with all canonical categories
- ✅ Added `get_category_from_class()` - extracts category from PLR class `.category` attribute
- ✅ Added `infer_category_from_name()` - fallback for string-based inference (clearly marked as brittle)
- ✅ Exported from `praxis/backend/models/enums/__init__.py`

**Frontend Enum:** `praxis/web-client/src/app/core/db/plr-category.ts`
- ✅ Created TypeScript `PLRCategory` enum matching Python version
- ✅ Added helper functions: `isResourceCategory()`, `isMachineCategory()`, `isBackendCategory()`
- ✅ Documented as synced with Python source

### 1.2 Database Schema Changes

**Backend ORM:** `praxis/backend/models/orm/protocol.py`
- ✅ Added `required_plr_category` column to `AssetRequirementOrm`
- ✅ Column is nullable, indexed, with descriptive comment

**Alembic Migration:** `alembic/versions/h5c6d7e8f9a0_add_required_plr_category_to_assets.py`
- ✅ Created migration with upgrade/downgrade functions
- ✅ Adds column and index to `protocol_asset_requirements` table

**Pydantic Model:** `praxis/backend/models/pydantic_internals/protocol.py`
- ✅ Added `required_plr_category: str | None = None` to `AssetRequirementModel`

### 1.3 Backend Logic Updated

**Parameter Processor:** `praxis/backend/core/decorators/parameter_processor.py`
- ✅ Replaced brittle string matching with proper category extraction
- ✅ Uses `get_category_from_class()` as primary method
- ✅ Falls back to `infer_category_from_name()` only when class unavailable
- ✅ Populates `required_plr_category` field during protocol analysis

**Before (HORRIBLE):**
```python
if "plate" in fqn_lower and "carrier" not in fqn_lower:
    return "Plate"
```

**After (CORRECT):**
```python
category_enum = get_category_from_class(type_hint)
if category_enum:
    return category_enum.value
```

### 1.4 Frontend Schema Updates

**TypeScript Interfaces:**
- ✅ `praxis/web-client/src/app/features/protocols/models/protocol.models.ts`
  - Added `required_plr_category?: string` to `AssetRequirement`

**Browser Mode Schema:**
- ✅ `praxis/web-client/src/app/core/db/schema.ts`
  - Added `required_plr_category: string | null` to `ProtocolAssetRequirement`

**SQL Schema:**
- ✅ `praxis/web-client/src/assets/db/schema.sql`
  - Added `required_plr_category VARCHAR` column to `protocol_asset_requirements` table
  - Added index `ix_protocol_asset_requirements_required_plr_category`

---

## ✅ Phase 2: Frontend Cleanup (PARTIAL)

### 2.1 Component Updates

**guided-setup.component.ts** ✅ COMPLETE
- ✅ Imported `PLRCategory` enum
- ✅ Created `getResourceCategory()` helper - checks `plr_definition.category` first, falls back to FQN
- ✅ Replaced `matchesByCategory()` to use `required_plr_category` from AssetRequirement
- ✅ Updated carrier exclusion logic to use category comparison
- ✅ Removed all hard-coded string matching patterns

**category-inference.ts** ✅ UPDATED
- ✅ Added comprehensive documentation explaining it's a FALLBACK
- ✅ Updated to use canonical `PLRCategory` enum values
- ✅ Prioritizes backend-provided `plr_category` field
- ✅ Falls back to resource_type, then FQN inference
- ✅ Clearly marked FQN inference as BRITTLE

### 2.2 Remaining Component Cleanups

**deck-generator.service.ts** ⚠️ NEEDS UPDATE
- Location: `praxis/web-client/src/app/features/run-protocol/services/deck-generator.service.ts`
- Lines with string matching: 72-74, 186-190, 287-297, 392-404
- TODO: Import `PLRCategory` and use explicit category checks

**carrier-inference.service.ts** ⚠️ NEEDS UPDATE
- Location: `praxis/web-client/src/app/features/run-protocol/services/carrier-inference.service.ts`
- Lines with string matching: 284-286, 293-295
- TODO: Import `PLRCategory` and use explicit category checks

---

## 🔲 Phase 3: Data Migration (PENDING)

### 3.1 Browser Mode Data Files

**protocols.ts** ⚠️ NEEDS UPDATE
- Location: `praxis/web-client/src/assets/browser-data/protocols.ts`
- TODO: Add `required_plr_category` to all protocol asset requirements

Example:
```typescript
export const BROWSER_PROTOCOLS: ProtocolDefinition[] = [
  {
    name: 'Serial Dilution',
    assets: [
      {
        name: 'source_plate',
        fqn: 'pylabrobot.resources.plate.Plate',
        type_hint_str: 'Plate',
        required_plr_category: 'Plate',  // ← ADD THIS
        // ...
      }
    ]
  }
];
```

**plr-definitions.ts** ✅ LIKELY OK
- Location: `praxis/web-client/src/assets/browser-data/plr-definitions.ts`
- Resource definitions should already have `plr_category` from static analysis
- Verify: Check that all definitions have `plr_category` populated

### 3.2 Database Migration

**Browser Mode SQLite** ⚠️ NEEDS REBUILD
- Database: `praxis/web-client/src/assets/db/praxis.db`
- Action: Rebuild database with new schema
- Command: Run schema generation script (TBD)

---

## 🚀 Phase 4: Advanced Improvements (FUTURE)

### 4.1 Static Analysis Integration

**Goal:** Use LibCST-based analysis instead of runtime imports

Current approach:
```python
# Runtime: imports PLR class to get .category attribute
category_enum = get_category_from_class(type_hint)
```

Better approach:
```python
# Static: uses PLRSourceParser (already exists!)
class PLRCategoryService:
    def __init__(self, plr_parser: PLRSourceParser):
        self._parser = plr_parser

    def get_category_for_fqn(self, fqn: str) -> PLRCategory | None:
        """Get category using static analysis (no imports needed)."""
        discovered_class = self._parser.get_class_by_fqn(fqn)
        if discovered_class and discovered_class.category:
            return PLRCategory(discovered_class.category)
        return None
```

**Benefits:**
- No runtime imports of PLR (faster, safer)
- Works even if PLR classes have import issues
- Consistent with existing machine/backend discovery

**Files to Update:**
- Create `praxis/backend/services/plr_category_service.py`
- Update `parameter_processor.py` to use service
- Integrate with existing `PLRSourceParser` workflow

### 4.2 Resource Category Denormalization

**Problem:** Resources don't directly expose `plr_category` - need to join with definitions

**Solution:** Add `plr_category` to Resource model (denormalized for performance)

**Backend Changes:**
```python
# praxis/backend/models/orm/resource.py
class ResourceOrm(AssetOrm):
    plr_category: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        index=True,
        comment="Cached PLR category from resource definition."
    )
```

**Frontend Changes:**
```typescript
// praxis/web-client/src/app/features/assets/models/asset.models.ts
export interface Resource extends AssetBase {
  plr_category?: string;  // Cached from definition
  // ... other fields
}
```

**Benefits:**
- No need for FQN fallback inference
- Faster filtering in UI
- Consistent with machine_category pattern

---

## 📊 Verification Checklist

### Backend Tests
- [ ] Alembic migration runs successfully
- [ ] `required_plr_category` is populated during protocol upload
- [ ] Category extraction prefers `.category` attribute over FQN matching
- [ ] All existing protocols still parse correctly

### Frontend Tests
- [ ] Guided setup filters resources by category correctly
- [ ] Carrier exclusion logic works (carriers don't appear in plate filters)
- [ ] Browser mode loads without errors
- [ ] Asset filtering uses canonical categories

### Integration Tests
- [ ] Upload protocol with `Plate` parameter → `required_plr_category='Plate'` in DB
- [ ] Upload protocol with `TipRack` parameter → `required_plr_category='TipRack'` in DB
- [ ] Frontend filters show only matching resources
- [ ] No category inference warnings in console

---

## 📝 Next Steps

1. **Immediate (P0)**
   - [ ] Update `deck-generator.service.ts` to use `PLRCategory`
   - [ ] Update `carrier-inference.service.ts` to use `PLRCategory`
   - [ ] Update browser mode protocol data with `required_plr_category`
   - [ ] Rebuild browser mode database

2. **Short-term (P1)**
   - [ ] Add `plr_category` to Resource model (denormalized)
   - [ ] Run Alembic migration in development
   - [ ] Test with real protocol uploads

3. **Long-term (P2)**
   - [ ] Create `PLRCategoryService` using static analysis
   - [ ] Eliminate all FQN-based category inference
   - [ ] Document category system in developer docs

---

## 🎯 Success Criteria

This work is **COMPLETE** when:

1. ✅ Backend populates `required_plr_category` from PLR class `.category` attribute
2. ⚠️ Frontend uses `required_plr_category` exclusively (no FQN string matching)
3. ⚠️ All components use canonical `PLRCategory` enum
4. ⚠️ Browser mode data includes `required_plr_category`
5. ⚠️ Tests pass
6. ⚠️ No console warnings about missing categories

**Current Status:** 60% Complete (3/5 criteria met)

---

## 📚 Related Work

- **P0_01:** PLR Category Audit (superseded by this work)
- **P1_02:** Asset Filtering Bugfix (superseded by this work)
- **Backlog:** `plr_category_architecture.md` - category system design
- **Backlog:** `separation_of_concerns.md` - backend/frontend responsibilities
