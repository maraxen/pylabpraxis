# Agent Prompt: 05_ui_consistency_exec_monitor

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Batch:** [260107](./README.md)
**Backlog:** [ui_consistency.md](../../backlog/ui_consistency.md)

---

## Task

Standardize the Execution Monitor UI to use consistent dropdown chips, popup menus, and styling patterns matching the Protocol Library and Asset Management views.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [ui_consistency.md](../../backlog/ui_consistency.md) | Work item tracking (Phase 1) |
| [execution-monitor/](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/execution-monitor/) | Execution Monitor components |
| [filter-chip.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/shared/components/filter-chip/) | Existing chip component |
| [chip_filter_standardization.md](../../backlog/chip_filter_standardization.md) | Filter chip patterns |

---

## Implementation Details

### 1. Status Display Conversion

Convert status display to dropdown chip pattern:

```typescript
// Current: Plain text or badge
// Target: FilterChipComponent with status options
<app-filter-chip
  [options]="statusOptions"
  [selected]="selectedStatus"
  (selectionChange)="onStatusFilter($event)">
</app-filter-chip>
```

### 2. Audit Inventory Menus

Compare Execution Monitor menus with Asset Management:

- Selection behavior (single vs multi)
- Popup positioning
- Keyboard navigation

### 3. Standardize Popup Menus

Ensure consistent styling for:

- Filter dropdowns
- Action menus (Cancel, Retry, etc.)
- Context menus

### 4. Theme Consistency

Verify dark/light mode support matches other views.

---

## Project Conventions

- **Frontend Dev**: `cd praxis/web-client && npm start`
- **Frontend Tests**: `cd praxis/web-client && npm test`

See [codestyles/typescript.md](../../codestyles/typescript.md) for guidelines.

---

## On Completion

- [ ] Execution Monitor uses FilterChipComponent for status
- [ ] All menus match Asset Management patterns
- [ ] Dark/light mode verified
- [ ] Update [ui_consistency.md](../../backlog/ui_consistency.md) Phase 1
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md) "UI Consistency - Exec Monitor"
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md)
- [execution_monitor.md](../../backlog/execution_monitor.md) - Execution monitor backlog
