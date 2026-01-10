# Agent Prompt: Fix Blank Browser Tab Categories in Playground Inventory

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Difficulty:** Medium
**Batch:** [260109](./README.md)
**Backlog Reference:** [playground.md](../../backlog/playground.md#p2-browser-tab-categories-blank)

---

## 1. The Task

In the Playground Inventory Dialog's "Browse & Add" tab, when navigating to the category step (Step 2), the area shows blank/empty content instead of displaying the available categories.

**Goal:** Fix the category step in the Browse & Add stepper to properly display and allow selection of categories.

**User Value:** Users can browse and select assets by category when using the structured Browse & Add workflow.

---

## 2. Technical Implementation Strategy

**Issue Analysis:**

Looking at `InventoryDialogComponent`, the category step uses:
- `availableCategories()` computed signal to get categories based on selected type
- `mat-chip-listbox` with `categoryControl` FormControl

Potential issues:
1. `availableCategories()` may return empty array if type isn't properly set
2. Reactivity issue between `typeControl` changes and `availableCategories` computation
3. Data loading timing issue

**Frontend Components:**

1. Debug `availableCategories()` computed signal
2. Ensure `typeControl.valueChanges` properly triggers recomputation
3. Add fallback UI for empty categories state

**Data Flow:**

1. User selects type (Machine/Resource) in Step 1
2. `typeControl` updates
3. `availableCategories` should recompute based on type
4. Step 2 displays category chips

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/playground/components/inventory-dialog/inventory-dialog.component.ts` | Fix category step logic |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/models/asset.models.ts` | Asset model definitions |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular tasks
- **Frontend Path**: `praxis/web-client`
- **State**: Use Angular Signals
- **Material**: Use `mat-chip-listbox` as currently implemented

**Debug Steps:**

1. Add console.log in `availableCategories()` to verify it's being called
2. Check if `machines()` and `resources()` signals have data loaded
3. Verify `typeControl.value` is set when Step 2 is reached

**Potential Fixes:**

```typescript
// Issue: availableCategories depends on typeControl.value but may not recompute
// Solution: Make availableCategories depend on a signal version of typeControl

// Add a signal to track type selection
private selectedType = signal<'machine' | 'resource' | ''>('');

// Update in constructor or add effect:
effect(() => {
  const type = this.typeControl.value;
  this.selectedType.set(type);
});

// Update availableCategories to use the signal
availableCategories = computed(() => {
  const type = this.selectedType();
  const cats = new Set<string>();

  if (type === 'machine') {
    this.machines()?.forEach(m => {
      if (m.machine_category) cats.add(m.machine_category);
    });
  } else if (type === 'resource') {
    this.resources()?.forEach(r => {
      const cat = this.getResourceCategory(r);
      if (cat) cats.add(cat);
    });
  }

  const result = Array.from(cats).sort();
  console.log('[InventoryDialog] availableCategories:', type, result);
  return result;
});
```

**Alternative Fix - Use toSignal for typeControl:**

```typescript
import { toSignal } from '@angular/core/rxjs-interop';

// In component:
typeControlValue = toSignal(this.typeControl.valueChanges, { initialValue: '' });

availableCategories = computed(() => {
  const type = this.typeControlValue();
  // ... rest of logic
});
```

**Add Empty State Handling in Template:**

```html
<!-- Step 2: Category -->
<mat-step [stepControl]="categoryForm" [completed]="categoryForm.valid">
  <ng-template matStepLabel>Category</ng-template>
  <div class="step-wrapper">
    @if (availableCategories().length > 0) {
      <div class="chip-container">
        <mat-chip-listbox [formControl]="categoryControl">
          @for (cat of availableCategories(); track cat) {
            <mat-chip-option [value]="cat">
              <mat-icon matChipAvatar>{{ getCategoryIcon(cat) }}</mat-icon>
              {{ cat }}
            </mat-chip-option>
          }
        </mat-chip-listbox>
      </div>
    } @else {
      <div class="empty-state">
        <mat-icon>category</mat-icon>
        <p>No categories available. Please select an asset type first.</p>
      </div>
    }
    <!-- step actions -->
  </div>
</mat-step>
```

---

## 5. Verification Plan

**Definition of Done:**

1. Category step shows available categories after type selection
2. Machine categories appear when Machine type is selected
3. Resource categories appear when Resource type is selected
4. Category selection works and allows progression to Step 3
5. Empty state shown if no categories available

**Verification Commands:**

```bash
cd praxis/web-client
npm run build
```

**Manual Verification:**
1. Navigate to Playground
2. Open Inventory Dialog
3. Go to "Browse & Add" tab
4. Select "Machine" type, click Next
5. Verify machine categories appear (LiquidHandler, PlateReader, etc.)
6. Go back, select "Resource" type, click Next
7. Verify resource categories appear

---

## On Completion

- [ ] Commit changes with message: `fix(playground): fix blank category step in inventory browser`
- [ ] Update backlog item status in `backlog/playground.md`
- [ ] Update `DEVELOPMENT_MATRIX.md` if applicable
- [ ] Mark this prompt complete in batch README and set status to 🟢 Completed

---

## References

- `.agents/README.md` - Development context and agent workflow
- `backlog/playground.md` - Full playground issue tracking
