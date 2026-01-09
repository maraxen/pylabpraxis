# Agent Prompt: Fix Playground Resource Filters

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Difficulty:** Medium
**Batch:** [260109](./README.md)
**Backlog Reference:** [playground.md](../../backlog/playground.md#p2-resource-filters-broken)

---

## 1. The Task

In asset selection and resource filtering within the Playground Inventory Dialog, the filters are not working correctly and have inconsistent styling compared to filters in other parts of the application.

**Goal:** Fix the filter functionality and align styling with the rest of the application's filter components.

**User Value:** Users can effectively filter and find resources when adding them to their playground inventory.

---

## 2. Technical Implementation Strategy

**Issue Analysis:**

The `InventoryDialogComponent` has category filtering in both:
1. Quick Add tab (using `quickFilterCategory`)
2. Browse & Add tab (using `categoryControl` in stepper)

The issues may include:
- Filter binding not properly connected to data filtering
- Category derivation not matching actual resource categories
- Styling inconsistencies with `PraxisSelectComponent`

**Frontend Components:**

1. Debug and fix the `categoryOptions` computed signal
2. Verify `filteredQuickAssets` properly applies category filter
3. Ensure styling matches other filter UIs (using shared components)

**Data Flow:**

1. Resources loaded via `AssetService`
2. Categories derived from resource `plr_definition.plr_category` or `asset_type`
3. Filter selection triggers `filteredQuickAssets` recomputation
4. Filtered list displayed in Quick Add tab

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/playground/components/inventory-dialog/inventory-dialog.component.ts` | Fix filter logic and styling |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/components/resource-filters/resource-filters.component.ts` | Reference implementation for resource filtering |
| `praxis/web-client/src/app/features/assets/utils/resource-category-groups.ts` | Category grouping utilities |
| `praxis/web-client/src/app/shared/components/praxis-select/praxis-select.component.ts` | Shared select component |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular tasks
- **Frontend Path**: `praxis/web-client`
- **State**: Use Angular Signals
- **Styling**: Use Tailwind utilities, match `FilterHeaderComponent` patterns

**Debug Steps:**

1. Add console logging to verify filter values are being set
2. Check that `getResourceCategory()` returns correct values
3. Verify `filteredQuickAssets` filtering logic

**Potential Fixes:**

```typescript
// Ensure category derivation is consistent
getResourceCategory(r: Resource): string {
  return r.plr_definition?.plr_category || r.asset_type || 'Other';
}

// Fix filteredQuickAssets to properly apply category filter
filteredQuickAssets = computed(() => {
  const typeFilter = this.quickFilterTypeValue();
  const catFilter = this.quickFilterCategoryValue();
  const search = this.quickSearch().toLowerCase();

  let all: (Machine | Resource)[] = [...(this.machines() || []), ...(this.resources() || [])];

  // Type filter
  if (typeFilter !== 'all') {
    all = all.filter(a => {
      if (typeFilter === 'machine') return 'machine_category' in a;
      return !('machine_category' in a);
    });
  }

  // Category filter - ensure this matches the category derivation
  if (catFilter !== 'all' && !catFilter.startsWith('HEADER_')) {
    all = all.filter(a => this.getCategory(a) === catFilter);
  }

  // Search filter
  if (search) {
    all = all.filter(a => a.name.toLowerCase().includes(search));
  }

  return all.slice(0, 10);
});
```

---

## 5. Verification Plan

**Definition of Done:**

1. Category filter in Quick Add tab filters resources correctly
2. Type filter (Machine/Resource) works correctly
3. Search + filters work together
4. Styling matches other filter UIs in the app
5. Category dropdown shows meaningful category names

**Verification Commands:**

```bash
cd praxis/web-client
npm run build
```

**Manual Verification:**
1. Navigate to Playground
2. Open Inventory Dialog
3. In Quick Add tab, try filtering by category
4. Verify results match selected category
5. Try filtering by type (Machine vs Resource)
6. Verify combined filters work correctly

---

## On Completion

- [ ] Commit changes with message: `fix(playground): fix resource filter functionality in inventory dialog`
- [ ] Update backlog item status in `backlog/playground.md`
- [ ] Update `DEVELOPMENT_MATRIX.md` if applicable
- [ ] Mark this prompt complete in batch README and set status to 🟢 Completed

---

## References

- `.agents/README.md` - Development context and agent workflow
- `backlog/playground.md` - Full playground issue tracking
