# Agent Prompt: Inventory Filter Styling - Use Styled Select Components

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260109](./README.md)
**Backlog Reference:** [playground.md](../../backlog/playground.md)

---

## 1. The Task

The Playground Inventory Dialog uses basic `mat-select` for the Quick Add filter controls, while other parts of the application use the custom `PraxisSelectComponent` and `PraxisMultiselectComponent` for consistent styling. The filter controls should be updated to use these shared styled components.

**User Value:** Consistent UI across the application; filters match the polished look of other asset management interfaces.

---

## 2. Technical Implementation Strategy

### Architecture

**Component:** `InventoryDialogComponent`

- Located at: `praxis/web-client/src/app/features/playground/components/inventory-dialog/inventory-dialog.component.ts`

**Current Implementation (lines 82-96):**

```html
<div class="filters-grid" filterContent>
  <mat-form-field appearance="outline">
    <mat-label>Asset Type</mat-label>
    <mat-select [formControl]="quickFilterType">
      <mat-option value="all">All Types</mat-option>
      <mat-option value="machine">Machines</mat-option>
      <mat-option value="resource">Resources</mat-option>
    </mat-select>
  </mat-form-field>

  <mat-form-field appearance="outline">
    <mat-label>Category</mat-label>
    <mat-select [formControl]="quickFilterCategory">
      <mat-option value="all">All Categories</mat-option>
      @for (cat of allCategories(); track cat) {
        <mat-option [value]="cat">{{ cat }}</mat-option>
      }
    </mat-select>
  </mat-form-field>
</div>
```

### Shared Styled Components

1. **`PraxisSelectComponent`** - Single select dropdown
   - Located at: `praxis/web-client/src/app/shared/components/praxis-select/praxis-select.component.ts`
   - Interface: `SelectOption { label: string; value: unknown; icon?: string; disabled?: boolean; }`

2. **`PraxisMultiselectComponent`** - Multi-select dropdown
   - Located at: `praxis/web-client/src/app/shared/components/praxis-multiselect/praxis-multiselect.component.ts`

### Proposed Changes

1. **Update imports:**

   ```typescript
   import { PraxisSelectComponent, SelectOption } from '@shared/components/praxis-select/praxis-select.component';
   ```

   Note: Already imported (line 27), just need to use it.

2. **Convert Asset Type filter:**

   ```html
   <div class="filter-group">
     <label class="text-xs font-medium text-sys-text-secondary uppercase tracking-wide mb-1 block">Asset Type</label>
     <app-praxis-select
       [options]="assetTypeOptions"
       [formControl]="quickFilterType"
       placeholder="All Types">
     </app-praxis-select>
   </div>
   ```

3. **Add options property:**

   ```typescript
   readonly assetTypeOptions: SelectOption[] = [
     { label: 'All Types', value: 'all' },
     { label: 'Machines', value: 'machine', icon: 'precision_manufacturing' },
     { label: 'Resources', value: 'resource', icon: 'science' }
   ];

   // Category options computed from allCategories()
   categoryOptions = computed(() => [
     { label: 'All Categories', value: 'all' },
     ...this.allCategories().map(cat => ({ label: cat, value: cat }))
   ]);
   ```

4. **Convert Category filter:**

   ```html
   <div class="filter-group">
     <label class="text-xs font-medium text-sys-text-secondary uppercase tracking-wide mb-1 block">Category</label>
     <app-praxis-select
       [options]="categoryOptions()"
       [formControl]="quickFilterCategory"
       placeholder="All Categories">
     </app-praxis-select>
   </div>
   ```

### Style Consistency

Follow the pattern from `AssetFiltersComponent` (lines 60-85) which uses the styled components with consistent labeling and layout.

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/playground/components/inventory-dialog/inventory-dialog.component.ts` | Update filter UI to use styled components |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/shared/components/praxis-select/praxis-select.component.ts` | Styled select component to use |
| `praxis/web-client/src/app/features/assets/components/asset-filters/asset-filters.component.ts` | Pattern reference for styled filters |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular commands
- **Frontend Path**: `praxis/web-client`
- **Styling**: Use existing Tailwind classes to match AssetFiltersComponent layout
- **Shared Components**: `PraxisSelectComponent` already imported, just need to use in template

---

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors:

   ```bash
   cd praxis/web-client && npm run build
   ```

2. Visual verification:
   - Navigate to Playground
   - Open Inventory Dialog
   - Go to "Quick Add" tab
   - Click "Filters" to expand
   - Verify selects match styling of other filters in the app:
     - Proper label above
     - Consistent border/background colors
     - Icons in options (if added)

3. Functional verification:
   - Select "Machines" in Asset Type filter
   - Verify only machines show in results
   - Select a category
   - Verify results filter correctly
   - "All" options clear their respective filters

4. Compare with reference:
   - Navigate to Assets → Machines
   - Compare filter styling between both locations
   - Should be visually consistent

---

## On Completion

- [ ] Commit changes with message: `feat(playground): use styled select components in inventory filters`
- [ ] Update backlog item status in [playground.md](../../backlog/playground.md)
- [ ] Mark this prompt complete in batch README, update DEVELOPMENT_MATRIX.md if applicable, and set the status in this prompt document to 🟢 Completed

---

## References

- `.agents/README.md` - Environment overview
- `.agents/codestyles/typescript.md` - TypeScript conventions
