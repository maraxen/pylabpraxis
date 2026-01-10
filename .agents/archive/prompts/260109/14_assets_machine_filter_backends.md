# Agent Prompt: Remove Backends from Machine Category Filters

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed
**Priority:** P2
**Difficulty:** Easy
**Batch:** [260109](./README.md)
**Backlog Reference:** [asset_management.md](../../backlog/asset_management.md#p2-machine-category-filters-include-backends)

---

## 1. The Task

The machine category filters in asset management incorrectly include "backends" as a category option. Backends are implementation details (STAR, OT2, ChatterboxBackend, etc.) and should not appear as machine categories from a user perspective.

**Goal:** Remove backends from the category filter dropdown so only meaningful machine categories (LiquidHandler, PlateReader, HeaterShaker, etc.) are shown.

**User Value:** Users see clean, understandable filter options without confusing internal backend names.

---

## 2. Technical Implementation Strategy

**Frontend Components:**

The `MachineFiltersComponent` derives category options from the machines' `machine_category` field. The issue is that either:
1. Some machines have backend names set as their `machine_category`, or
2. Backend filtering is a separate axis that's getting confused with category filtering

**Approach:**

1. **Audit the category derivation** in `availableCategories` computed signal
2. **Filter out backend-like values** - Create a blocklist or allowlist for valid machine categories
3. **Keep backend filtering separate** - Backend filtering is already a separate control, ensure categories don't duplicate this

**Data Flow:**

1. `machines()` input provides machine data
2. `availableCategories` computed extracts unique `machine_category` values
3. Filter out any values that match known backend patterns (contain "Backend", match backend FQNs)
4. `mappedCategoryOptions` formats for display

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/components/machine-filters/machine-filters.component.ts` | Main filter component - modify `availableCategories` computed |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/models/asset.models.ts` | Machine model definitions |
| `praxis/web-client/src/app/features/assets/services/asset.service.ts` | Data source for machines |
| `praxis/web-client/src/app/features/assets/utils/category-inference.ts` | Existing category utilities |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular tasks
- **Frontend Path**: `praxis/web-client`
- **State**: Use Angular Signals for any new reactive state
- **Testing**: Update existing tests in `machine-filters.component.spec.ts` if present

**Implementation Options:**

Option A: Blocklist approach
```typescript
const BACKEND_PATTERNS = ['Backend', 'Chatterbox', 'Simulator'];
availableCategories = computed(() => {
  const cats = new Set<string>();
  this.machines().forEach(m => {
    if (m.machine_category && !BACKEND_PATTERNS.some(p => m.machine_category.includes(p))) {
      cats.add(m.machine_category);
    }
  });
  return Array.from(cats).sort();
});
```

Option B: Allowlist approach (if valid categories are well-defined)
```typescript
const VALID_CATEGORIES = ['LiquidHandler', 'PlateReader', 'HeaterShaker', 'Centrifuge', ...];
```

---

## 5. Verification Plan

**Definition of Done:**

1. Category filter dropdown shows only meaningful machine categories
2. Backend names (STAR, OT2Backend, ChatterboxBackend, etc.) do not appear in category filter
3. Backend filter remains separate and unaffected
4. No regressions in filter functionality

**Verification Commands:**

```bash
cd praxis/web-client
npm test -- --include="**/machine-filters*"
npm run build
```

**Manual Verification:**
1. Navigate to Assets > Machines tab
2. Open category filter dropdown
3. Verify only machine categories appear (LiquidHandler, PlateReader, etc.)
4. Verify backend filter still shows backend options separately

---

## On Completion

- [x] Commit changes with message: `fix(assets): remove backends from machine category filters`
- [x] Update backlog item status in `backlog/asset_management.md`
- [x] Update `DEVELOPMENT_MATRIX.md` if applicable
- [x] Mark this prompt complete in batch README and set status to 🟢 Completed

---

## References

- `.agents/README.md` - Development context and agent workflow
- `backlog/asset_management.md` - Full asset management issue tracking
