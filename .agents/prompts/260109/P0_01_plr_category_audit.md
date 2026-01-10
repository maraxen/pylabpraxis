# Agent Prompt: PLR Category Architecture Audit (P0)

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P0 (Architectural Foundation)
**Batch:** [260109](README.md)
**Backlog Reference:** [plr_category_architecture.md](../../backlog/plr_category_architecture.md)
**Estimated Complexity:** High (application-wide)

---

## 1. The Task

Audit the entire application and fix ALL places that classify or filter resources by type. Replace fragile FQN string matching with reliable `plr_category` usage.

**User Value:** Consistent, bug-free resource filtering throughout the application. No more carriers appearing in plate selections, no more missing resources.

**Architectural Value:** Clear separation of concerns - backend owns classification, frontend consumes it.

---

## 2. Background: Why This Matters

### The Anti-Pattern (Current State)

```typescript
// FRAGILE: String matching on FQN
if (fqn.toLowerCase().includes('plate')) { ... }
// BUG: Matches "PlateCarrier", "plateHolder", etc.

// FRAGILE: Exclude patterns to work around the bug
if (fqn.includes('carrier')) return false;
// HACK: Keeps growing as new edge cases appear
```

### The Correct Pattern

```typescript
// RELIABLE: Use plr_category from backend
if (resource.plr_category === 'Plate') { ... }
// WORKS: PlateCarrier has plr_category: 'Carrier', not 'Plate'
```

### How plr_category Works

| Resource Type | FQN Example | plr_category |
|:--------------|:------------|:-------------|
| Corning Plate | `pylabrobot.resources.corning_costar.plates.Cor_96_wellplate_360ul_Fb` | `'Plate'` |
| Plate Carrier | `pylabrobot.resources.hamilton.carriers.PLT_CAR_L5AC_A00` | `'Carrier'` |
| Tip Rack | `pylabrobot.resources.hamilton.tips.HT_P_300uL_NTR_96` | `'TipRack'` |
| Trough | `pylabrobot.resources.agilent.troughs.Agilent_1_reservoir_290ml` | `'Reservoir'` |

---

## 3. Audit Scope

### Phase 1: Find All String Matching

Search for patterns that indicate FQN string matching:

```bash
# Find FQN string matching in frontend
grep -r "fqn.*includes\|includes.*fqn\|fqn.*toLowerCase\|toLowerCase.*fqn" praxis/web-client/src --include="*.ts"

# Find category inference based on strings
grep -r "plate\|tiprack\|carrier\|trough" praxis/web-client/src --include="*.ts" | grep -i "includes\|indexOf\|match"
```

### Phase 2: Known Problem Files

**High Priority (known bugs):**

| File | Issue |
|:-----|:------|
| `features/run-protocol/components/guided-setup/guided-setup.component.ts` | `matchesByCategory()` uses FQN string matching |
| `features/run-protocol/services/carrier-inference.service.ts` | May use string matching for carrier detection |
| `features/assets/utils/category-inference.ts` | Duplicates backend classification logic |

**Medium Priority (audit needed):**

| File | Reason to Check |
|:-----|:----------------|
| `features/assets/components/definitions-list/definitions-list.component.ts` | Filter logic |
| `features/assets/components/resource-accordion/resource-accordion.component.ts` | Category grouping |
| `features/playground/playground.component.ts` | Resource filtering |
| `features/playground/components/inventory-dialog/inventory-dialog.component.ts` | Inventory type filters |
| `features/run-protocol/components/deck-setup-wizard/` | Position compatibility |
| `features/run-protocol/services/consumable-assignment.service.ts` | Resource matching |

**Low Priority (backend, should be correct):**

| File | Reason |
|:-----|:-------|
| `praxis/backend/services/resource_type_definition.py` | Source of truth for plr_category |
| `praxis/backend/core/consumable_assignment.py` | Backend filtering |

---

## 4. Implementation Strategy

### Step 1: Create Shared Utility (Frontend)

Create a centralized utility for category-based filtering:

**File:** `praxis/web-client/src/app/core/utils/plr-category.utils.ts`

```typescript
/**
 * PLR Category Utilities
 *
 * Use these functions for ALL resource type filtering.
 * DO NOT use FQN string matching for category determination.
 */

export type PlrCategory = 'Plate' | 'TipRack' | 'Reservoir' | 'Carrier' | 'Tube' | 'Deck' | 'Resource';

/**
 * Check if a resource matches an expected category
 */
export function matchesCategory(resource: { plr_category?: string | null }, expected: PlrCategory): boolean {
  if (!resource.plr_category) return false;
  return resource.plr_category.toLowerCase() === expected.toLowerCase();
}

/**
 * Check if a resource is a consumable (not a carrier or infrastructure)
 */
export function isConsumable(resource: { plr_category?: string | null }): boolean {
  const consumableCategories: PlrCategory[] = ['Plate', 'TipRack', 'Reservoir', 'Tube'];
  return consumableCategories.some(cat => matchesCategory(resource, cat));
}

/**
 * Check if a resource is a carrier (holds other resources)
 */
export function isCarrier(resource: { plr_category?: string | null }): boolean {
  return matchesCategory(resource, 'Carrier');
}

/**
 * Get expected category from a type hint string
 * Used when we have a protocol requirement but no plr_category
 */
export function inferCategoryFromTypeHint(typeHint: string): PlrCategory | null {
  const hint = typeHint.toLowerCase();

  if (hint.includes('plate') && !hint.includes('carrier')) return 'Plate';
  if (hint.includes('tiprack') || hint.includes('tip_rack')) return 'TipRack';
  if (hint.includes('trough') || hint.includes('reservoir')) return 'Reservoir';
  if (hint.includes('tube') && !hint.includes('carrier')) return 'Tube';
  if (hint.includes('carrier')) return 'Carrier';
  if (hint.includes('deck')) return 'Deck';

  return null;
}
```

### Step 2: Fix Each Problem File

For each file, replace string matching with utility calls:

**Before:**
```typescript
if (fqn.toLowerCase().includes('plate')) {
  if (fqn.includes('carrier')) return false; // HACK
  return true;
}
```

**After:**
```typescript
import { matchesCategory, inferCategoryFromTypeHint } from '@core/utils/plr-category.utils';

// For filtering resources
if (matchesCategory(resource, 'Plate')) {
  return true;
}

// For matching requirements to resources
const requiredCategory = inferCategoryFromTypeHint(req.type_hint_str || '');
if (requiredCategory && matchesCategory(resource, requiredCategory)) {
  return true;
}
```

### Step 3: Ensure Data Availability

Verify `plr_category` is available in all contexts:

1. **Production Mode**: Check API responses include `plr_category`
2. **Browser Mode**: Check `plr-definitions.ts` has `plr_category` for all resources
3. **Resource Interface**: Ensure TypeScript interface includes `plr_category`

---

## 5. Verification Plan

### Automated Checks

```bash
# No FQN string matching for categories (excluding test files)
grep -r "fqn.*includes.*plate\|fqn.*includes.*carrier\|fqn.*includes.*tip" praxis/web-client/src --include="*.ts" | grep -v ".spec.ts" | grep -v "plr-category.utils.ts"
# Should return empty

# Verify utility is used
grep -r "matchesCategory\|inferCategoryFromTypeHint" praxis/web-client/src --include="*.ts" | wc -l
# Should be > 0
```

### Manual Testing

1. **Protocol Execution**:
   - Select protocol requiring `Plate`
   - Verify only plates appear (no carriers)
   - Verify ALL plate types appear (Corning, Greiner, etc.)

2. **Asset Management**:
   - Filter by category in asset list
   - Verify correct grouping

3. **Playground**:
   - Filter inventory by type
   - Verify correct filtering

---

## 6. Deliverables

1. New utility file: `core/utils/plr-category.utils.ts`
2. Refactored filtering in all identified files
3. Removed all carrier exclusion hacks
4. Updated tests if any exist for filtering logic

---

## 7. On Completion

- [ ] Commit: `refactor(core): implement plr_category-based resource filtering`
- [ ] Update backlog status in `backlog/plr_category_architecture.md`
- [ ] Mark this prompt complete in batch README
- [ ] Document pattern in `DEVELOPMENT_MATRIX.md` or similar

---

## 8. Success Criteria

| Metric | Target |
|:-------|:-------|
| FQN string matching for categories | 0 occurrences |
| Files using `plr-category.utils.ts` | All identified files |
| Carrier exclusion hacks | 0 occurrences |
| Test failures | 0 |
| Build errors | 0 |

---

## References

- PLR category extraction: `praxis/backend/services/resource_type_definition.py:172-191`
- Browser mode data: `praxis/web-client/src/assets/browser-data/plr-definitions.ts`
- Resource interface: `praxis/web-client/src/app/features/assets/models/asset.models.ts`
