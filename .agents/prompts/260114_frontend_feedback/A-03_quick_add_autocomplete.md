# Agent Prompt: Quick Add Autocomplete

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed
**Priority:** P2
**Batch:** [260114_frontend_feedback](./README.md)
**Difficulty:** 🟢 Easy
**Type:** 🟢 Implementation
**Dependencies:** A-02 (Add Dialog Unification)
**Backlog Reference:** Group A - View Controls Standardization

---

## 1. The Task

Add autocomplete search functionality to the Add Asset dialog to allow users to quickly find and select definitions without navigating through categories.

### User Feedback

> "we should also have a quick add autocomplete for both (in both the + asset and the + machine +resource separate dialogue) for the + asset it should also be on the first (pick machine or resource dialog)"

### Requirements

1. **Autocomplete on first screen** of Add Asset dialog (before choosing Machine/Resource)
2. **Search across all definitions** (both machine and resource)
3. **Show type indicator** (Machine/Resource) in results
4. **Direct jump to config** when selecting from autocomplete
5. **Available in dedicated dialogs** too (if still used)

## 2. Technical Implementation Strategy

### Component: QuickAddAutocomplete

```typescript
@Component({
  selector: 'app-quick-add-autocomplete',
  standalone: true,
  imports: [
    MatAutocompleteModule,
    MatInputModule,
    MatIconModule,
    // ...
  ],
})
export class QuickAddAutocompleteComponent {
  @Output() definitionSelected = new EventEmitter<{
    type: 'machine' | 'resource';
    definition: MachineDefinition | ResourceDefinition;
  }>();
  
  searchControl = new FormControl('');
  
  // Combine machine and resource definitions for search
  allDefinitions = computed(() => [
    ...this.machineDefinitions().map(d => ({ type: 'machine' as const, def: d })),
    ...this.resourceDefinitions().map(d => ({ type: 'resource' as const, def: d })),
  ]);
  
  filteredDefinitions = computed(() => {
    const term = this.searchControl.value?.toLowerCase() || '';
    if (!term) return [];
    return this.allDefinitions()
      .filter(item => 
        item.def.name.toLowerCase().includes(term) ||
        item.def.category?.toLowerCase().includes(term)
      )
      .slice(0, 10); // Limit results
  });
  
  onSelect(item: {type: 'machine' | 'resource', def: any}) {
    this.definitionSelected.emit({
      type: item.type,
      definition: item.def,
    });
  }
}
```

### Template Structure

```html
<mat-form-field appearance="outline" class="quick-add-field">
  <mat-label>Quick search...</mat-label>
  <input matInput
    [formControl]="searchControl"
    [matAutocomplete]="auto"
    placeholder="Search machines and resources...">
  <mat-icon matPrefix>search</mat-icon>
  
  <mat-autocomplete #auto="matAutocomplete" (optionSelected)="onSelect($event.option.value)">
    @for (item of filteredDefinitions(); track item.def.accession_id) {
      <mat-option [value]="item">
        <div class="autocomplete-option">
          <mat-icon class="type-icon">
            {{ item.type === 'machine' ? 'precision_manufacturing' : 'inventory_2' }}
          </mat-icon>
          <span class="option-name">{{ item.def.name }}</span>
          <span class="option-type">{{ item.type | titlecase }}</span>
        </div>
      </mat-option>
    }
  </mat-autocomplete>
</mat-form-field>
```

### Integration into Add Asset Dialog

In `TypeSelectionStepComponent` (from A-02):

```html
<div class="type-selection-step">
  <!-- Quick Add Autocomplete -->
  <app-quick-add-autocomplete
    (definitionSelected)="onQuickSelect($event)">
  </app-quick-add-autocomplete>
  
  <div class="divider">
    <span>or choose category</span>
  </div>
  
  <!-- Existing type buttons -->
  <div class="type-buttons">
    <button mat-raised-button (click)="selectType('machine')">
      <mat-icon>precision_manufacturing</mat-icon>
      Add Machine
    </button>
    <button mat-raised-button (click)="selectType('resource')">
      <mat-icon>inventory_2</mat-icon>
      Add Resource
    </button>
  </div>
</div>
```

## 3. Context & References

**Files to Create:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/shared/components/quick-add-autocomplete/quick-add-autocomplete.component.ts` | New autocomplete component |

**Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/shared/dialogs/add-asset-dialog/steps/type-selection-step.component.ts` | Add autocomplete to first step |

**Reference Files:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/shared/components/praxis-autocomplete/praxis-autocomplete.component.ts` | Existing autocomplete pattern |
| `praxis/web-client/src/app/features/assets/services/asset.service.ts` | Definition data source |

## 4. Constraints & Conventions

- **Debouncing**: Use 200ms debounce on search input
- **Result Limit**: Show max 10 results to avoid overwhelming
- **Keyboard Navigation**: Ensure arrow keys work for selection
- **Mobile Friendly**: Touch-friendly option sizes

## 5. Verification Plan

**Definition of Done:**

1. Autocomplete component compiles without errors
2. Search returns relevant results
3. Selecting from autocomplete jumps to configuration step
4. Type indicator (Machine/Resource) visible in results

**Test Commands:**

```bash
cd praxis/web-client
npx tsc --noEmit
npm run build
```

**Manual Verification:**

1. Open Add Asset dialog
2. Type in search field
3. Verify machine and resource results appear
4. Verify type icons distinguish machine vs resource
5. Select a result and verify it jumps to config step

---

## On Completion

- [x] Autocomplete component created
- [x] Integrated into Add Asset dialog
- [x] Manual verification complete
- [x] Mark this prompt complete in batch README
- [x] Set status in this document to 🟢 Completed

---

## References

- `.agents/README.md` - Environment overview
- `GROUP_A_view_controls_init.md` - Parent initiative
