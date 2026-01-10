# Separation of Concerns: Backend/Frontend Architecture

**Created**: 2026-01-10
**Priority**: P0 (Architectural Foundation)
**Status**: Open

---

## Architectural Principle

> **The backend owns all PLR inspection and classification logic. The database is the single source of truth. The frontend consumes pre-computed data and performs only display/filtering operations using explicit fields—never inference.**

---

## The Problem

The frontend currently contains logic that duplicates or infers what the backend should provide:

### Anti-Patterns Found

| Location | Anti-Pattern | Impact |
|:---------|:-------------|:-------|
| `guided-setup.component.ts` | String matching on FQN to determine category | Carriers appear in plate lists |
| `category-inference.ts` | Frontend utility to classify resources | Duplicates backend logic |
| `carrier-inference.service.ts` | Infers carrier compatibility from names/FQNs | Fragile, can break |
| Various filters | Check if `fqn.includes('plate')` | PlateCarrier matches "plate" |

### Why This Happens

1. **Missing data**: Backend doesn't provide `required_plr_category` on `AssetRequirement`
2. **Incomplete schema**: Some fields that would make filtering trivial don't exist
3. **Expedient fixes**: String matching was quicker than schema changes
4. **Browser mode**: Offline data sometimes lacks fields production has

---

## The Solution

### Principle 1: Backend Computes, Frontend Displays

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   PyLabRobot    │  ──▶    │    Backend      │  ──▶    │    Frontend     │
│                 │         │                 │         │                 │
│  Classes with   │         │  Extracts and   │         │  Filters using  │
│  inheritance    │         │  stores:        │         │  explicit       │
│                 │         │  - plr_category │         │  fields only    │
│                 │         │  - is_carrier   │         │                 │
│                 │         │  - is_consumable│         │  NO string      │
│                 │         │  - etc.         │         │  matching       │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

### Principle 2: Requirements Include What They Need

When the backend analyzes a protocol with `plate: Plate`, it should store:

```python
AssetRequirement(
    name="plate",
    fqn="pylabrobot.resources.plate.Plate",
    type_hint_str="Plate",
    required_plr_category="Plate",  # ← Backend computes this
)
```

Frontend filtering becomes trivial:
```typescript
resources.filter(r => r.plr_category === req.required_plr_category)
```

### Principle 3: Browser Mode Has Same Data Shape

Browser mode data (`plr-definitions.ts`, `protocols.ts`, etc.) must have the same fields as production API responses. No special-casing.

---

## Audit Scope

### Phase 1: Schema Completeness

Ensure all entities have the fields needed for frontend operations:

| Entity | Field Needed | Purpose | Status |
|:-------|:-------------|:--------|:-------|
| `AssetRequirement` | `required_plr_category` | Filter compatible resources | ❌ Missing |
| `AssetRequirement` | `is_machine_requirement` | Separate machine vs resource reqs | ❓ Check |
| `ResourceDefinition` | `plr_category` | Category for filtering | ✅ Exists |
| `ResourceDefinition` | `is_consumable` | Consumable vs infrastructure | ✅ Exists |
| `Resource` (instance) | `plr_category` | Via definition join | ✅ Available |
| `MachineDefinition` | `machine_category` | Machine type filtering | ✅ Exists |

### Phase 2: Backend Service Updates

Ensure protocol analysis populates new fields:

| Service | Change Needed |
|:--------|:--------------|
| `protocol_definition.py` | Set `required_plr_category` during analysis |
| `resource_type_definition.py` | Ensure `plr_category` always set |
| API serializers | Include new fields in responses |

### Phase 3: Frontend Cleanup

Remove all inference/classification logic:

| File | Remove/Replace |
|:-----|:---------------|
| `category-inference.ts` | Delete or gut entirely |
| `guided-setup.component.ts` | Replace `matchesByCategory()` with field check |
| `carrier-inference.service.ts` | Audit for string matching |
| `resource-name-parser.ts` | Audit for category inference |
| All components | Search for `includes('plate')`, `includes('carrier')`, etc. |

### Phase 4: Browser Mode Data

Update offline data to match production schema:

| File | Update Needed |
|:-----|:--------------|
| `plr-definitions.ts` | Ensure all resources have `plr_category` |
| `protocols.ts` | Add `required_plr_category` to asset requirements |
| `resources.ts` | Include `plr_category` from definitions |
| Schema generation scripts | Include new fields |

---

## Success Criteria

### Quantitative

| Metric | Target |
|:-------|:-------|
| Frontend files with `includes('plate')` for filtering | 0 |
| Frontend files with `includes('carrier')` for filtering | 0 |
| Frontend files with `includes('tip')` for filtering | 0 |
| Category inference utilities | 0 (deleted) |
| `AssetRequirement` without `required_plr_category` | 0 |

### Qualitative

- [ ] Frontend developer can filter resources using only explicit fields
- [ ] No string parsing required for category determination
- [ ] Browser mode and production mode use identical data shapes
- [ ] Adding a new PLR category requires only backend changes

---

## Migration Strategy

### Step 1: Add Schema Fields (Non-Breaking)
- Add `required_plr_category` to `AssetRequirementOrm`
- Add migration
- Update Pydantic models
- Update TypeScript interfaces

### Step 2: Populate New Fields (Backend)
- Update protocol analysis to set `required_plr_category`
- Backfill existing protocols (one-time script or lazy update)
- Update browser mode data

### Step 3: Update Frontend (Replace Logic)
- Replace string matching with field checks
- Delete `category-inference.ts`
- Update tests

### Step 4: Verify & Clean Up
- Run full test suite
- Manual testing of all filtering scenarios
- Remove any dead code

---

## Related Items

- [P0_01_plr_category_audit.md](../prompts/260109/P0_01_plr_category_audit.md) - Frontend cleanup (subset of this)
- [P0_02_separation_of_concerns_audit.md](../prompts/260109/P0_02_separation_of_concerns_audit.md) - Full audit prompt
- [P1_02_asset_filtering_bugfix.md](../prompts/260109/P1_02_asset_filtering_bugfix.md) - Tactical fix (superseded by P0_02)

---

## Technical Notes

### How Backend Determines Category

From `resource_type_definition.py`:
```python
def _get_category_from_plr_class(self, plr_class: type[Any]) -> str | None:
    if hasattr(plr_class, "category"):
        category = plr_class.category
        # Normalization...
        return category
    return None
```

### How Backend Should Set required_plr_category

During protocol analysis when processing type hints:
```python
def _extract_asset_requirement(self, param_name: str, type_hint: type) -> AssetRequirementOrm:
    # ... existing logic ...

    # NEW: Determine required category from type hint
    required_category = self._get_category_from_type_hint(type_hint)

    return AssetRequirementOrm(
        name=param_name,
        fqn=fqn_from_hint(type_hint),
        type_hint_str=serialize_type_hint(type_hint),
        required_plr_category=required_category,  # ← New field
    )

def _get_category_from_type_hint(self, type_hint: type) -> str | None:
    """Get PLR category from a type hint (e.g., Plate -> 'Plate')."""
    if hasattr(type_hint, 'category'):
        return type_hint.category
    # Handle common base classes
    class_name = getattr(type_hint, '__name__', '')
    return class_name if class_name in {'Plate', 'TipRack', 'Trough', 'Carrier', 'Tube'} else None
```
