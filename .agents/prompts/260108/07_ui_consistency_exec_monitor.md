# Agent Prompt: 07_ui_consistency_exec_monitor

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Batch:** [260108](./README.md)  
**Backlog:** [ui_consistency.md](../../backlog/ui_consistency.md)  
**Priority:** P2

---

## Task

Standardize the Execution Monitor UI to match the patterns established in Protocol Library and Asset Management. Convert status displays to dropdown chips and audit menus for consistency.

---

## Implementation Steps

### 1. Convert Status Display to Dropdown Chip

Update `ExecutionMonitorComponent` to use the same dropdown chip pattern as Protocol Library:

```typescript
// Replace status text/badge with FilterChipComponent dropdown
// Allow filtering by: Running, Paused, Completed, Failed
```

### 2. Audit Inventory Menus

Compare popup menus in Execution Monitor with Asset Management patterns:

- Standardize action menu positioning
- Ensure consistent icons and labels
- Match hover/focus states

### 3. Standardize Multi-Item Selection

If Execution Monitor has multi-select capabilities, ensure popup menus match Asset Management:

- Selection checkboxes (if applicable)
- Bulk action menus
- Clear selection affordance

### 4. Visual Testing

Use browser subagent to capture before/after screenshots of Execution Monitor.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [ui_consistency.md](../../backlog/ui_consistency.md) | Backlog tracking |
| [execution-monitor.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/execution-monitor/execution-monitor.component.ts) | Main component |
| [filter-chip.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/shared/components/filter-chip/filter-chip.component.ts) | Reusable chip component |

---

## Project Conventions

- **Frontend Tests**: `cd praxis/web-client && npm test`

See [codestyles/typescript.md](../../codestyles/typescript.md) for conventions.

---

## On Completion

- [ ] Commit changes with message: `feat(execution-monitor): standardize UI patterns with dropdown chips`
- [ ] Update [ui_consistency.md](../../backlog/ui_consistency.md) - mark Phase 1 complete
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
