# Agent Prompt: Category Structure in Quick Add Filter

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed
**Priority:** P2
**Batch:** [260109](./README.md)
**Backlog Reference:** [playground.md](../../backlog/playground.md)

---

## 1. The Task

Categories in the Playground Inventory quick add filter need to be properly structured/nested. Currently, they may appear as a flat list without logical grouping. Categories should be organized hierarchically or grouped meaningfully (e.g., Machine categories separate from Resource categories).

**User Value:** Users can quickly find the category they need without scrolling through a long flat list; mental model matches the Machine vs Resource distinction.

---

## 2. Technical Implementation Strategy

### Architecture

**Component:** `InventoryDialogComponent`

- Located at: `praxis/web-client/src/app/features/playground/components/inventory-dialog/inventory-dialog.component.ts`

### Current Implementation Analysis

The `allCategories()` computed property likely combines machine and resource categories into a single flat list. We need to:

1. Identify how categories are sourced
2. Determine proper grouping structure
3. Implement grouped dropdown or optgroup support

### Category Sources

Categories come from two sources:

- **Machine categories:** From `MachineDefinition.machine_category`
- **Resource categories:** From `ResourceDefinition` (plates, tips, etc.)

### Proposed Solutions

**Option A: Use optgroup in mat-select**

```html
<mat-form-field appearance="outline">
  <mat-label>Category</mat-label>
  <mat-select [formControl]="quickFilterCategory">
    <mat-option value="all">All Categories</mat-option>
    <mat-optgroup label="Machines">
      @for (cat of machineCategories(); track cat) {
        <mat-option [value]="cat">{{ cat }}</mat-option>
      }
    </mat-optgroup>
    <mat-optgroup label="Resources">
      @for (cat of resourceCategories(); track cat) {
        <mat-option [value]="cat">{{ cat }}</mat-option>
      }
    </mat-optgroup>
  </mat-select>
</mat-form-field>
```

**Option B: Hierarchical data for PraxisSelect**
Extend `SelectOption` to support groups:

```typescript
interface GroupedSelectOption {
  group: string;
  options: SelectOption[];
}

categoryGroups = computed<GroupedSelectOption[]>(() => [
  { 
    group: 'Machines', 
    options: this.machineCategories().map(c => ({ label: c, value: c }))
  },
  { 
    group: 'Resources', 
    options: this.resourceCategories().map(c => ({ label: c, value: c }))
  }
]);
```

**Option C: Context-sensitive categories**
When Asset Type filter is set, only show relevant categories:

```typescript
filteredCategories = computed(() => {
  const type = this.quickFilterType.value;
  if (type === 'machine') return this.machineCategories();
  if (type === 'resource') return this.resourceCategories();
  return this.allCategories();
});
```

**Recommendation:** Combine Option A (optgroups) with Option C (context-sensitive). When "All Types" is selected, show grouped categories. When specific type selected, show only that type's categories.

### Implementation Steps

1. **Split category sources:**

   ```typescript
   machineCategories = computed(() => 
     [...new Set(this.machines().map(m => m.category))].filter(Boolean).sort()
   );
   
   resourceCategories = computed(() =>
     [...new Set(this.resources().map(r => this.getCategory(r)))].filter(Boolean).sort()
   );
   ```

2. **Create filtered/grouped computed:**

   ```typescript
   categoryOptions = computed(() => {
     const type = this.quickFilterType.value;
     if (type === 'machine') {
       return this.machineCategories().map(c => ({ label: c, value: c }));
     }
     if (type === 'resource') {
       return this.resourceCategories().map(c => ({ label: c, value: c }));
     }
     // Return grouped for 'all'
     return [
       { label: '— Machines —', value: null, disabled: true },
       ...this.machineCategories().map(c => ({ label: c, value: c })),
       { label: '— Resources —', value: null, disabled: true },
       ...this.resourceCategories().map(c => ({ label: c, value: c }))
     ];
   });
   ```

3. **Update template to use computed options**

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/playground/components/inventory-dialog/inventory-dialog.component.ts` | Add category grouping logic |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/services/asset.service.ts` | How machines/resources are fetched |
| `praxis/web-client/src/app/features/assets/components/machine-filters/machine-filters.component.ts` | Pattern for category filtering |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular commands
- **Frontend Path**: `praxis/web-client`
- **Styling**: Use Tailwind classes for any separator styling
- **UX**: Keep "All Categories" as first option always

---

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors:

   ```bash
   cd praxis/web-client && npm run build
   ```

2. Visual verification:
   - Navigate to Playground
   - Open Inventory Dialog → Quick Add tab
   - Open Category dropdown
   - Categories should be grouped:
     - Machine categories together (Liquid Handler, Plate Reader, etc.)
     - Resource categories together (Plates, Tips, Labware, etc.)
   - Groups should be visually distinct (separator, header, or optgroup)

3. Context-sensitive behavior:
   - Select "Machines" in Asset Type
   - Category dropdown shows only machine categories
   - Select "Resources" in Asset Type
   - Category dropdown shows only resource categories
   - Select "All Types"
   - Category dropdown shows grouped categories

4. Filter functionality:
   - Selecting a category filters results correctly
   - Switching Asset Type resets category if incompatible
   - "All Categories" always available and works

---

## On Completion

- [x] Commit changes with message: `feat(playground): organize category structure in quick add filter`
- [x] Update backlog item status in [playground.md](../../backlog/playground.md)
- [x] Mark this prompt complete in batch README, update DEVELOPMENT_MATRIX.md if applicable, and set the status in this prompt document to 🟢 Completed

---

## References

- `.agents/README.md` - Environment overview
- `.agents/codestyles/typescript.md` - TypeScript conventions
