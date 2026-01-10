# Agent Prompt: Implement Protocol Library Filters

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Difficulty:** Medium
**Batch:** [260109](./README.md)
**Backlog Reference:** [protocol_workflow.md](../../backlog/protocol_workflow.md#p2-protocol-library-filters)

---

## 1. The Task

The Protocol Library currently only has a search bar. It needs filter chips to help users find protocols by category, author, tags, or resource requirements.

**Goal:** Implement filter controls in the Protocol Library consistent with other asset filter UIs in the application.

**User Value:** Users with many protocols can quickly find what they need using filters instead of scrolling through a long list.

---

## 2. Technical Implementation Strategy

**Frontend Components:**

The `FilterHeaderComponent` already supports a `filterContent` slot for additional filter controls. We need to:

1. Add filter state signals to `ProtocolLibraryComponent`
2. Add filter UI to the `FilterHeaderComponent` slot
3. Update `filteredProtocols` computed to incorporate filters

**Filters to Implement:**

1. **Category** - Filter by protocol category (if available)
2. **Type** - Filter by `is_top_level` (Top Level vs Sub-Protocol)
3. **Status** - Filter by simulation status (Passed/Failed/None)

**Data Flow:**

1. User selects filter options
2. Filter signals update
3. `filteredProtocols` computed re-evaluates
4. Table displays filtered results

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/protocols/components/protocol-library/protocol-library.component.ts` | Add filter state and UI |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/components/filter-header/filter-header.component.ts` | Filter header pattern to follow |
| `praxis/web-client/src/app/features/assets/components/machine-filters/machine-filters.component.ts` | Filter implementation pattern |
| `praxis/web-client/src/app/shared/components/praxis-select/praxis-select.component.ts` | Select component for filters |
| `praxis/web-client/src/app/shared/components/praxis-multiselect/praxis-multiselect.component.ts` | Multiselect for multi-option filters |
| `praxis/web-client/src/app/features/protocols/models/protocol.models.ts` | Protocol model with available fields |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular tasks
- **Frontend Path**: `praxis/web-client`
- **Styling**: Use Tailwind utilities, match existing filter styling
- **State**: Use Angular Signals
- **Components**: Reuse `PraxisSelectComponent` and `PraxisMultiselectComponent`

**Implementation Sketch:**

```typescript
// Add to component class
selectedCategory = signal<string>('');
selectedType = signal<'all' | 'top_level' | 'sub'>('all');
filterCount = computed(() => {
  let count = 0;
  if (this.selectedCategory()) count++;
  if (this.selectedType() !== 'all') count++;
  return count;
});

categoryOptions = computed<SelectOption[]>(() => {
  const cats = new Set<string>();
  this.protocols().forEach(p => {
    if (p.category) cats.add(p.category);
  });
  return [
    { label: 'All Categories', value: '' },
    ...Array.from(cats).sort().map(c => ({ label: c, value: c }))
  ];
});

typeOptions: SelectOption[] = [
  { label: 'All Types', value: 'all' },
  { label: 'Top Level', value: 'top_level' },
  { label: 'Sub-Protocol', value: 'sub' }
];

// Update filteredProtocols
filteredProtocols = computed(() => {
  const query = this.searchQuery().toLowerCase();
  const category = this.selectedCategory();
  const type = this.selectedType();

  return this.protocols().filter(protocol => {
    // Search filter
    const matchesSearch = !query ||
      protocol.name.toLowerCase().includes(query) ||
      protocol.description?.toLowerCase().includes(query);

    // Category filter
    const matchesCategory = !category || protocol.category === category;

    // Type filter
    const matchesType = type === 'all' ||
      (type === 'top_level' && protocol.is_top_level) ||
      (type === 'sub' && !protocol.is_top_level);

    return matchesSearch && matchesCategory && matchesType;
  });
});
```

**Template Addition:**

```html
<app-filter-header
  searchPlaceholder="Search protocols..."
  [filterCount]="filterCount()"
  [searchValue]="searchQuery()"
  (searchChange)="onSearchChange($event)"
  (clearFilters)="clearFilters()">

  <div class="filters-grid" filterContent>
    <div class="filter-group">
      <label class="text-xs font-medium text-sys-text-secondary uppercase tracking-wide mb-1 block">Category</label>
      <app-praxis-select
        [options]="categoryOptions()"
        [ngModel]="selectedCategory()"
        (ngModelChange)="selectedCategory.set($event)"
        placeholder="All Categories">
      </app-praxis-select>
    </div>

    <div class="filter-group">
      <label class="text-xs font-medium text-sys-text-secondary uppercase tracking-wide mb-1 block">Type</label>
      <app-praxis-select
        [options]="typeOptions"
        [ngModel]="selectedType()"
        (ngModelChange)="selectedType.set($event)"
        placeholder="All Types">
      </app-praxis-select>
    </div>
  </div>
</app-filter-header>
```

---

## 5. Verification Plan

**Definition of Done:**

1. Protocol Library shows Category and Type filter dropdowns
2. Selecting a category filters the list to matching protocols
3. Selecting a type filters Top Level vs Sub-Protocols
4. Search and filters work together (AND logic)
5. Clear filters resets all selections
6. Filter count badge shows number of active filters

**Verification Commands:**

```bash
cd praxis/web-client
npm run build
```

**Manual Verification:**
1. Navigate to Protocol Library
2. Verify filter dropdowns appear in filter header
3. Test category filtering
4. Test type filtering (Top Level vs Sub-Protocol)
5. Test combined search + filter
6. Test clear filters button

---

## On Completion

- [ ] Commit changes with message: `feat(protocols): add category and type filters to protocol library`
- [ ] Update backlog item status in `backlog/protocol_workflow.md`
- [ ] Update `DEVELOPMENT_MATRIX.md` if applicable
- [ ] Mark this prompt complete in batch README and set status to 🟢 Completed

---

## References

- `.agents/README.md` - Development context and agent workflow
- `backlog/protocol_workflow.md` - Full protocol workflow issue tracking
