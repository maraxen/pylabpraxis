# Agent Prompt: Shared View Controls Component

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P1
**Batch:** [260114_frontend_feedback](./README.md)
**Difficulty:** 🔴 Complex
**Type:** 🟢 Implementation
**Dependencies:** None
**Backlog Reference:** Group A - View Controls Standardization

---

## 1. The Task

Create a **unified `ViewControlsComponent`** that provides consistent view controls across all filterable areas of the application. This is a **foundation component** that will replace 6+ disparate filter implementations.

### User Feedback

> "we should overall have a consistent set of 'view' controls exposed to the user across menus (this should be a shared component) this should have a groupby and filterby etc."

### Core Features

1. **View Type Toggle** - Switch between card/list/table views
2. **Group By** - Dynamic grouping options (by status, category, type, etc.)
3. **Filter By** - Composable filters with multiselect support
4. **Sort By** - Configurable sort options with direction toggle
5. **Search** - Text search with debouncing
6. **Clear Filters** - Reset all controls to defaults
7. **Preference Persistence** - Save user preferences to localStorage

## 2. Technical Implementation Strategy

### Component Architecture

```
shared/components/view-controls/
├── view-controls.component.ts      # Main orchestrating component
├── view-controls.component.html
├── view-controls.component.scss
├── view-controls.types.ts          # Interfaces and types
├── view-type-toggle.component.ts   # Card/List/Table toggle
├── group-by-select.component.ts    # Group by dropdown
└── index.ts                        # Public exports
```

### Type Definitions

```typescript
// view-controls.types.ts
export type ViewType = 'card' | 'list' | 'table';

export interface ViewControlsConfig {
  // Available view types (default: all)
  viewTypes?: ViewType[];
  
  // Available group-by options
  groupByOptions?: SelectOption[];
  
  // Available filter configurations
  filters?: FilterConfig[];
  
  // Available sort options
  sortOptions?: SelectOption[];
  
  // localStorage key for persistence
  storageKey?: string;
  
  // Initial values
  defaults?: Partial<ViewControlsState>;
}

export interface FilterConfig {
  key: string;
  label: string;
  type: 'multiselect' | 'select' | 'chips';
  options: FilterOption[];
  allowInvert?: boolean;
}

export interface ViewControlsState {
  viewType: ViewType;
  groupBy: string | null;
  filters: Record<string, unknown[]>;
  sortBy: string;
  sortOrder: 'asc' | 'desc';
  search: string;
}
```

### Component API

```typescript
@Component({
  selector: 'app-view-controls',
  standalone: true,
  // ...
})
export class ViewControlsComponent {
  // Configuration input
  @Input() config: ViewControlsConfig = {};
  
  // Current state (two-way bindable)
  @Input() state: ViewControlsState;
  @Output() stateChange = new EventEmitter<ViewControlsState>();
  
  // Individual change events for fine-grained control
  @Output() viewTypeChange = new EventEmitter<ViewType>();
  @Output() groupByChange = new EventEmitter<string | null>();
  @Output() filtersChange = new EventEmitter<Record<string, unknown[]>>();
  @Output() sortChange = new EventEmitter<{sortBy: string, sortOrder: 'asc'|'desc'}>();
  @Output() searchChange = new EventEmitter<string>();
}
```

### Persistence Strategy

```typescript
// Persist to localStorage using storageKey
private loadPersistedState(): Partial<ViewControlsState> {
  if (!this.config.storageKey) return {};
  const stored = localStorage.getItem(`viewControls.${this.config.storageKey}`);
  return stored ? JSON.parse(stored) : {};
}

private persistState(state: ViewControlsState): void {
  if (!this.config.storageKey) return;
  localStorage.setItem(`viewControls.${this.config.storageKey}`, JSON.stringify(state));
}
```

## 3. Context & References

**Files to Create:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/shared/components/view-controls/view-controls.component.ts` | Main component |
| `praxis/web-client/src/app/shared/components/view-controls/view-controls.types.ts` | Type definitions |
| `praxis/web-client/src/app/shared/components/view-controls/view-type-toggle.component.ts` | View toggle subcomponent |
| `praxis/web-client/src/app/shared/components/view-controls/group-by-select.component.ts` | Group by subcomponent |

**Reference Files (Existing Patterns):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/shared/components/filter-chip/filter-chip.component.ts` | Existing filter chip (297 lines) |
| `praxis/web-client/src/app/shared/components/praxis-multiselect/praxis-multiselect.component.ts` | Multiselect pattern (198 lines) |
| `praxis/web-client/src/app/shared/components/praxis-select/praxis-select.component.ts` | Select pattern |
| `praxis/web-client/src/app/features/assets/components/machine-filters/machine-filters.component.ts` | Example filter implementation (390 lines) |
| `praxis/web-client/src/app/features/assets/components/asset-filters/asset-filters.component.ts` | Example filter implementation (285 lines) |

**Files to Eventually Replace (in A-04):**

| Component | Location | Lines |
|:----------|:---------|:------|
| `AssetFiltersComponent` | `assets/components/asset-filters/` | 285 |
| `MachineFiltersComponent` | `assets/components/machine-filters/` | 390 |
| `ResourceFiltersComponent` | `assets/components/resource-filters/` | ~250 |
| `RunFiltersComponent` | `execution-monitor/components/` | 213 |
| DataViz inline filters | `data/data-visualization.component.ts` | embedded |
| Protocol filters | `protocols/components/protocol-library/` | embedded |

## 4. Constraints & Conventions

- **Styling**: Use existing design tokens from `styles/themes/`
- **State**: Use Angular Signals for reactive state
- **Components**: Standalone components only
- **Accessibility**: Include ARIA labels for all controls
- **Testing**: Include unit tests for state management
- **Dark Mode**: Ensure compatibility with dark theme

## 5. Verification Plan

**Definition of Done:**

1. All new components compile without errors
2. Component can be imported and used in a test harness
3. View type toggle persists preference
4. Filter state can be bound two-way
5. Clear filters resets all state

**Test Commands:**

```bash
cd praxis/web-client
npx tsc --noEmit
npm run build
npm run test -- --include='**/view-controls/**'
```

**Manual Verification:**

1. Create a simple test page that uses `ViewControlsComponent`
2. Verify view type toggle works
3. Verify filters emit correct state
4. Verify localStorage persistence
5. Verify clear filters works

---

## On Completion

- [ ] All files created and compiling
- [ ] Unit tests passing
- [ ] Mark this prompt complete in batch README
- [ ] Set status in this document to 🟢 Completed
- [ ] Proceed to A-04 for adoption across tabs

---

## References

- `.agents/README.md` - Environment overview
- `.agents/codestyles/typescript.md` - TypeScript conventions
- `GROUP_A_view_controls_init.md` - Parent initiative
