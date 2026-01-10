# Agent Prompt: Separation of Concerns Audit (P0)

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P0 (Architectural Foundation)
**Batch:** [260109](README.md)
**Backlog Reference:** [separation_of_concerns.md](../../backlog/separation_of_concerns.md)
**Estimated Complexity:** High (backend + frontend + data)
**Supersedes:** P0_01, P1_02 (this is the comprehensive fix)

---

## 1. The Architectural Principle

> **The backend owns all PLR inspection and classification logic. The database is the single source of truth. The frontend consumes pre-computed data and performs only display/filtering operations using explicit fields—never inference.**

**User Value:** Reliable, consistent behavior across the entire application. No more edge cases where carriers appear in plate lists or resources don't match because of naming conventions.

**Developer Value:** Clear ownership. Frontend devs never need to understand PLR class hierarchy. Backend changes don't require frontend updates.

---

## 2. Current State (Anti-Patterns)

### Frontend Contains Classification Logic

```typescript
// ANTI-PATTERN: Frontend infers category from FQN
if (fqn.toLowerCase().includes('plate')) {
  if (fqn.includes('carrier')) return false; // hack to fix previous hack
  return true;
}
```

### Missing Schema Fields

```typescript
// AssetRequirement is MISSING required_plr_category
interface AssetRequirement {
  fqn: string;              // "pylabrobot.resources.plate.Plate"
  type_hint_str: string;    // "Plate"
  // ❌ required_plr_category is MISSING
}

// Frontend has to INFER what category is needed
// This is the root cause of all filtering bugs
```

---

## 3. Target State

### Backend Provides Everything

```python
# AssetRequirement has all needed fields
class AssetRequirementOrm(Base):
    fqn: str                           # "pylabrobot.resources.plate.Plate"
    type_hint_str: str                 # "Plate"
    required_plr_category: str | None  # "Plate" ← NEW: Backend computes this
```

### Frontend Logic is Trivial

```typescript
// CORRECT: Frontend uses explicit field, zero inference
getCompatibleResources(req: AssetRequirement): Resource[] {
  if (!req.required_plr_category) return this.inventory();
  return this.inventory().filter(r =>
    r.plr_category === req.required_plr_category
  );
}
```

---

## 4. Implementation Plan

### Phase 1: Backend Schema Changes

**4.1 Add `required_plr_category` to AssetRequirement**

File: `praxis/backend/models/orm/protocol.py`

```python
class AssetRequirementOrm(Base):
    # ... existing fields ...

    required_plr_category: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        index=True,
        comment="PLR category required (Plate, TipRack, Carrier, etc). Computed during protocol analysis.",
        default=None,
    )
```

**4.2 Create Alembic Migration**

```bash
cd praxis/backend
alembic revision --autogenerate -m "add_required_plr_category_to_asset_requirements"
```

**4.3 Update Pydantic Models**

File: `praxis/backend/models/pydantic_internals/protocol.py`

```python
class AssetRequirementModel(BaseModel):
    # ... existing fields ...
    required_plr_category: str | None = None
```

### Phase 2: Backend Service Updates

**4.4 Update Protocol Analysis**

File: `praxis/backend/services/protocol_definition.py` (or wherever asset requirements are extracted)

Find where `AssetRequirementOrm` is created and add:

```python
def _extract_asset_requirements(self, func: Callable) -> list[AssetRequirementOrm]:
    requirements = []
    for param_name, param in signature(func).parameters.items():
        type_hint = param.annotation
        if self._is_asset_type(type_hint):
            req = AssetRequirementOrm(
                name=param_name,
                fqn=fqn_from_hint(type_hint),
                type_hint_str=serialize_type_hint(type_hint),
                required_plr_category=self._get_required_category(type_hint),  # ← ADD THIS
            )
            requirements.append(req)
    return requirements

def _get_required_category(self, type_hint: type) -> str | None:
    """Extract PLR category from a type hint."""
    # If it has a category attribute (PLR classes do)
    if hasattr(type_hint, 'category'):
        return type_hint.category

    # Handle base class names directly
    class_name = getattr(type_hint, '__name__', '')
    known_categories = {'Plate', 'TipRack', 'Trough', 'Carrier', 'Tube', 'Deck'}
    if class_name in known_categories:
        return class_name

    return None
```

**4.5 Backfill Existing Data (Optional Script)**

```python
# scripts/backfill_required_plr_category.py
async def backfill():
    async with get_session() as db:
        requirements = await db.execute(select(AssetRequirementOrm))
        for req in requirements.scalars():
            if req.required_plr_category is None:
                req.required_plr_category = infer_category_from_fqn(req.fqn)
        await db.commit()
```

### Phase 3: Frontend Schema Updates

**4.6 Update TypeScript Interface**

File: `praxis/web-client/src/app/features/protocols/models/protocol.models.ts`

```typescript
export interface AssetRequirement {
  accession_id: string;
  name: string;
  fqn: string;
  type_hint_str: string;
  optional: boolean;
  default_value_repr?: string;
  description?: string;
  constraints: AssetConstraints;
  location_constraints: LocationConstraints;
  required_plr_category?: string;  // ← ADD THIS
}
```

**4.7 Update Database Schema (Browser Mode)**

File: `praxis/web-client/src/app/core/db/schema.ts`

Add `required_plr_category` to the `ProtocolAssetRequirement` interface.

File: `praxis/web-client/src/assets/db/schema.sql`

```sql
-- Add to protocol_asset_requirements table
ALTER TABLE protocol_asset_requirements
ADD COLUMN required_plr_category TEXT;
```

### Phase 4: Frontend Cleanup

**4.8 Replace Filtering Logic**

File: `praxis/web-client/src/app/features/run-protocol/components/guided-setup/guided-setup.component.ts`

Replace `matchesByCategory()` entirely:

```typescript
/**
 * Filter resources by required category.
 * Uses backend-provided required_plr_category - NO inference.
 */
private matchesByCategory(req: AssetRequirement, res: Resource): boolean {
  // If no category requirement, don't filter by category
  if (!req.required_plr_category) return true;

  // Use explicit field - no string matching
  return res.plr_category?.toLowerCase() === req.required_plr_category.toLowerCase();
}
```

**4.9 Delete Inference Utilities**

File: `praxis/web-client/src/app/features/assets/utils/category-inference.ts`

Either delete entirely or gut to a no-op that throws if called:

```typescript
/**
 * @deprecated Category should come from backend. Do not use.
 */
export function inferCategory(): never {
  throw new Error('Category inference removed. Use backend-provided required_plr_category.');
}
```

**4.10 Audit and Remove All String Matching**

Search and replace all instances:

```bash
# Find all category inference in frontend
grep -rn "includes('plate')\|includes('carrier')\|includes('tip')\|includes('trough')" \
  praxis/web-client/src --include="*.ts" | grep -v ".spec.ts"
```

Each instance should be replaced with an explicit field check.

### Phase 5: Browser Mode Data

**4.11 Update Browser Data Files**

File: `praxis/web-client/src/assets/browser-data/protocols.ts`

Ensure all protocol asset requirements have `required_plr_category`:

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

**4.12 Update Schema Generation Script**

File: `scripts/generate_browser_schema.py`

Ensure it includes `required_plr_category` when generating TypeScript.

---

## 5. Verification Plan

### Automated Checks

```bash
# 1. No category inference in frontend (excluding tests)
grep -rn "includes('plate')\|includes('carrier')\|includes('tip')" \
  praxis/web-client/src --include="*.ts" | grep -v ".spec.ts" | grep -v "category-inference"
# Expected: 0 results

# 2. category-inference.ts is deleted or deprecated
ls praxis/web-client/src/app/features/assets/utils/category-inference.ts
# Expected: file not found OR contains only deprecation warning

# 3. Backend tests pass
cd praxis/backend && uv run pytest tests/services/test_protocol_definition_service.py -v

# 4. Frontend builds
cd praxis/web-client && npm run build
```

### Manual Testing

| Scenario | Expected Result |
|:---------|:----------------|
| Protocol requires `Plate` | Only `plr_category: 'Plate'` resources shown |
| Protocol requires `TipRack` | Only `plr_category: 'TipRack'` resources shown |
| Resource named `PLT_CAR_*` (carrier) | Does NOT appear in Plate selection |
| New vendor plate added | Appears automatically (has `plr_category: 'Plate'`) |

---

## 6. Files Modified Summary

### Backend (Create/Modify)

| File | Action |
|:-----|:-------|
| `models/orm/protocol.py` | Add `required_plr_category` field |
| `models/pydantic_internals/protocol.py` | Add to Pydantic model |
| `services/protocol_definition.py` | Set field during analysis |
| `alembic/versions/xxx_add_required_plr_category.py` | Migration |

### Frontend (Create/Modify)

| File | Action |
|:-----|:-------|
| `features/protocols/models/protocol.models.ts` | Add interface field |
| `core/db/schema.ts` | Add to TypeScript interface |
| `features/run-protocol/components/guided-setup/guided-setup.component.ts` | Replace filtering logic |
| `features/assets/utils/category-inference.ts` | Delete or deprecate |
| `assets/browser-data/protocols.ts` | Add field to data |
| `assets/db/schema.sql` | Add column |

---

## 7. On Completion

- [ ] All backend tests pass
- [ ] All frontend tests pass
- [ ] Build succeeds
- [ ] Manual testing complete
- [ ] Commit: `refactor: implement backend-first category classification`
- [ ] Update backlog status in `backlog/separation_of_concerns.md`
- [ ] Mark P0_01 and P1_02 as superseded
- [ ] Update batch README

---

## 8. Future Considerations

Once this pattern is established, apply to other areas:

- **Machine compatibility**: Backend should compute compatible machines, not frontend
- **Carrier-resource compatibility**: Backend should store which carriers fit which resources
- **Position compatibility**: Backend should define what can go where on a deck

This audit establishes the pattern; future work extends it.
