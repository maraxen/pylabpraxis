# Agent Prompt: Adopt Shared View Controls Across Tabs

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260114_frontend_feedback](./README.md)
**Difficulty:** 🟡 Intricate
**Type:** 🟢 Implementation
**Dependencies:** A-01 (Shared View Controls Component)
**Backlog Reference:** Group A - View Controls Standardization

---

## 1. The Task

Adopt the new `ViewControlsComponent` (from A-01) across all filterable areas of the application, replacing bespoke filter implementations with the shared component.

### User Feedback

> "we should overall have a consistent set of 'view' controls exposed to the user across menus"
> "I like these card based views. let's have toggle for view type in spatial machines resources and registry."

### Areas to Update

| Priority | Area | Current Implementation | Notes |
|:---------|:-----|:-----------------------|:------|
| 1 | Spatial View | `AssetFiltersComponent` | Primary use case |
| 2 | Machines Tab | `MachineFiltersComponent` | 390 lines to replace |
| 3 | Resources Tab | `ResourceFiltersComponent` | Similar to Machines |
| 4 | Registry Tab | Inline filters | Add consistent controls |
| 5 | Execution Monitor | `RunFiltersComponent` | Run history filters |
| 6 | Protocol Library | Inline filters | Search + status |
| 7 | Data Visualization | Inline filter bar | Complex, may need custom |

## 2. Technical Implementation Strategy

### Phase 1: Spatial View (Reference Implementation)

Update `SpatialViewComponent` to use `ViewControlsComponent`:

```typescript
// spatial-view.component.ts
import { ViewControlsComponent, ViewControlsConfig, ViewControlsState } from '@shared/components/view-controls';

@Component({
  // ...
  imports: [ViewControlsComponent, /* ... */],
})
export class SpatialViewComponent {
  viewConfig: ViewControlsConfig = {
    viewTypes: ['card', 'list'],
    groupByOptions: [
      { label: 'None', value: null },
      { label: 'Status', value: 'status' },
      { label: 'Category', value: 'category' },
      { label: 'Location', value: 'location' },
    ],
    filters: [
      {
        key: 'status',
        label: 'Status',
        type: 'multiselect',
        options: this.statusOptions,
      },
      {
        key: 'category',
        label: 'Category', 
        type: 'chips',
        options: this.categoryOptions,
      },
    ],
    sortOptions: [
      { label: 'Name', value: 'name' },
      { label: 'Created', value: 'created_at' },
      { label: 'Status', value: 'status' },
    ],
    storageKey: 'spatial-view',
  };
  
  viewState = signal<ViewControlsState>({
    viewType: 'card',
    groupBy: null,
    filters: {},
    sortBy: 'created_at',
    sortOrder: 'desc',
    search: '',
  });
  
  onViewStateChange(state: ViewControlsState) {
    this.viewState.set(state);
    this.applyFilters();
  }
}
```

### Phase 2: Machines Tab

```typescript
// machine-list.component.ts (or wherever machines are displayed)
viewConfig: ViewControlsConfig = {
  viewTypes: ['card', 'list', 'table'],
  groupByOptions: [
    { label: 'None', value: null },
    { label: 'Category', value: 'category' },
    { label: 'Status', value: 'status' },
    { label: 'Backend', value: 'backend' },
  ],
  filters: [
    { key: 'status', label: 'Status', type: 'multiselect', options: this.statusOptions },
    { key: 'category', label: 'Category', type: 'chips', options: this.categoryOptions },
    { key: 'simulated', label: 'Simulated', type: 'select', options: [
      { label: 'All', value: null },
      { label: 'Real', value: false },
      { label: 'Simulated', value: true },
    ]},
  ],
  storageKey: 'machines-tab',
};
```

### Phase 3-6: Remaining Areas

Follow same pattern for:

- Resources Tab
- Registry Tab  
- Execution Monitor
- Protocol Library

### Phase 7: Data Visualization

DataViz has specialized needs (protocol/run selection, well filtering). Options:

1. Use `ViewControlsComponent` for basic filters, keep specialized well selector
2. Create extended version with custom slots
3. Keep separate (document in TECHNICAL_DEBT.md)

## 3. Context & References

**Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/components/spatial-view/spatial-view.component.ts` | Replace AssetFilters |
| `praxis/web-client/src/app/features/assets/components/machine-list/machine-list.component.ts` | Replace MachineFilters |
| `praxis/web-client/src/app/features/assets/components/resource-list/resource-list.component.ts` | Replace ResourceFilters |
| `praxis/web-client/src/app/features/execution-monitor/` | Replace RunFilters |
| `praxis/web-client/src/app/features/protocols/components/protocol-library/protocol-library.component.ts` | Add consistent filters |

**Files to Deprecate (eventually remove):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/components/asset-filters/` | Replace with ViewControls |
| `praxis/web-client/src/app/features/assets/components/machine-filters/` | Replace with ViewControls |
| `praxis/web-client/src/app/features/assets/components/resource-filters/` | Replace with ViewControls |
| `praxis/web-client/src/app/features/execution-monitor/components/run-filters.component.ts` | Replace with ViewControls |

**Reference Files:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/shared/components/view-controls/` | New shared component (from A-01) |

## 4. Constraints & Conventions

- **Incremental Migration**: One area at a time, verify each before moving on
- **Feature Parity**: New implementation must support all existing filter options
- **Backward Compatible**: Don't remove old components until all migrations verified
- **Test Each**: Verify filtering still works after each migration

## 5. Verification Plan

**Definition of Done:**

1. All areas listed use `ViewControlsComponent`
2. View type toggle (card/list) works in all areas
3. Filters work correctly in all areas
4. User preferences persist across sessions
5. No regressions in functionality

**Test Commands:**

```bash
cd praxis/web-client
npx tsc --noEmit
npm run build
npm run test
```

**Manual Verification Checklist:**

For each area:

- [ ] View type toggle works (card/list/table)
- [ ] Group by works
- [ ] All filters work
- [ ] Search works
- [ ] Clear filters works
- [ ] Preferences persist after refresh

---

## On Completion

- [ ] All areas migrated to ViewControlsComponent
- [ ] Manual verification complete for all areas
- [ ] Old filter components marked for deprecation
- [ ] Update DEVELOPMENT_MATRIX.md (this unblocks Group B and H)
- [ ] Mark this prompt complete in batch README
- [ ] Set status in this document to 🟢 Completed

---

## References

- `.agents/README.md` - Environment overview
- `GROUP_A_view_controls_init.md` - Parent initiative
- `GROUP_B_ui_consistency_init.md` - Depends on this work
- `GROUP_H_dataviz_init.md` - Depends on this work
