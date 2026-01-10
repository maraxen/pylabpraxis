# Agent Prompt: Asset Selection Card Filters

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P1
**Batch:** [260109](README.md)
**Backlog Reference:** [protocol_workflow.md](../../backlog/protocol_workflow.md)
**Estimated Complexity:** Medium

---

## 1. The Task

Add filter controls to each asset selection card in the protocol workflow's asset selection step. Currently, users can only search via autocomplete. Adding explicit filter chips/dropdowns will help users quickly narrow down large inventories.

**User Value:** Faster, more intuitive asset selection for protocols with many requirements.

---

## 2. Technical Implementation Strategy

**Architecture:**

The asset selection is handled by `GuidedSetupComponent` which renders a card for each `AssetRequirement`. Each card currently has:
- Requirement info (name, type hint, FQN)
- An autocomplete dropdown (`PraxisAutocompleteComponent`)

**Enhancement:**

Add filter chips or a small filter bar above/beside each autocomplete that filters the options by:
1. **Status** - Available, In Use, Reserved (filter inventory before populating options)
2. **Category/Type** - Pre-filter based on requirement type (e.g., show only 96-well plates)

**Implementation Approach:**

1. **Add filter signals per requirement** in component state
2. **Modify `requirementsOptions` computed** to apply filters
3. **Add filter UI** above each autocomplete

**Proposed UI Pattern:**

```html
<div class="requirement-item">
  <div class="req-info">
    <!-- existing info -->
  </div>

  <div class="resource-select">
    <!-- NEW: Filter chips row -->
    <div class="filter-row flex gap-2 mb-2">
      <mat-chip-listbox 
        [multiple]="false"
        [ngModel]="getStatusFilter(req.accession_id)"
        (change)="setStatusFilter(req.accession_id, $event.value)">
        <mat-chip-option value="all">All</mat-chip-option>
        <mat-chip-option value="available">Available</mat-chip-option>
        <mat-chip-option value="in_use">In Use</mat-chip-option>
      </mat-chip-listbox>
    </div>

    <label class="text-xs font-medium text-gray-500 mb-1 block">Select Inventory Item</label>
    <app-praxis-autocomplete
      [options]="requirementsOptions()[req.accession_id] || []"
      [ngModel]="selectedAssets()[req.accession_id]"
      (ngModelChange)="updateSelection(req.accession_id, $event)"
      [placeholder]="'Search inventory...'"
    ></app-praxis-autocomplete>
  </div>
</div>
```

**State Management:**

```typescript
// Add filter state signal
statusFilters = signal<Record<string, string>>({});

// Getter/setter helpers
getStatusFilter(reqId: string): string {
  return this.statusFilters()[reqId] || 'all';
}

setStatusFilter(reqId: string, value: string) {
  this.statusFilters.update(current => ({
    ...current,
    [reqId]: value
  }));
}

// Modify generateOptionsForReq to apply filters
private generateOptionsForReq(req: AssetRequirement, inventory: Resource[]): SelectOption[] {
  const statusFilter = this.statusFilters()[req.accession_id] || 'all';
  
  // Apply status filter
  let filteredInventory = inventory;
  if (statusFilter !== 'all') {
    filteredInventory = inventory.filter(res => res.status === statusFilter);
  }

  const compatible = this.getCompatibleResourcesForInventory(req, filteredInventory);
  // ... rest of logic
}
```

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/run-protocol/components/guided-setup/guided-setup.component.ts` | Add filter signals, UI, and filtering logic |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/models/asset.models.ts` | `ResourceStatus` enum |
| `praxis/web-client/src/app/shared/components/praxis-select/praxis-select.component.ts` | Shared select component pattern |

**Required Imports:**

```typescript
import { MatChipsModule } from '@angular/material/chips';
```

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular CLI commands
- **Frontend Path**: `praxis/web-client`
- **Styling**: Use Tailwind utility classes for filter row layout
- **State**: Use Angular Signals for filter state
- **Linting**: Run `npm run lint` before committing

---

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors:

   ```bash
   cd praxis/web-client && npm run build
   ```

2. Filter chips appear above each asset selection autocomplete
3. Changing filter updates the available options in the autocomplete
4. Filters default to "All" showing all compatible resources

**Manual Testing:**

1. Open a protocol with asset requirements
2. In Asset Selection step:
   - Verify filter chips are visible for each requirement
   - Click "Available" filter - verify only available resources show
   - Click "In Use" filter - verify only in-use resources show
   - Click "All" - verify all compatible resources show
3. Ensure autofill still works correctly with filters

---

## On Completion

- [ ] Commit changes with message: "feat(protocol): add status filters to asset selection cards"
- [ ] Update backlog item status
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
- Angular Material Chips documentation
