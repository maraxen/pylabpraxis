# Agent Prompt: 19_execution_monitor_history

Examine `.agents/README.md` for development context.

**Status:** ✅ Complete  
**Batch:** [260109](./README.md)  
**Backlog:** [execution_monitor.md](../../backlog/execution_monitor.md)  

---

## Task

Implement the Run History Table for the Execution Monitor (Phase 3). Show paginated table of past runs with sorting and click-through to details.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [execution_monitor.md](../../backlog/execution_monitor.md) | Work item tracking (Phase 3) |
| `praxis/web-client/src/app/features/execution-monitor/` | Feature module |

---

## Implementation

### Service: `RunHistoryService`

```typescript
interface RunHistoryParams {
  status?: RunStatus[];
  protocol_id?: string;
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}
```

### Component: `RunHistoryTableComponent`

1. **Columns**:
   - Protocol Name
   - Status (with color badges)
   - Started (datetime)
   - Duration (formatted)
   - Machine used

2. **Features**:
   - Sortable column headers
   - Pagination controls (limit/offset)
   - Click row to navigate to detail

3. **Demo Mode**:
   - Add mock data to `DemoInterceptor`
   - Support filtering and pagination

---

## Expected Outcome

- Paginated history table with sorting
- Demo mode shows realistic test data
- Navigation to run details works

---

## Project Conventions

- **Frontend Tests**: `cd praxis/web-client && npm test`

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status (mark Phase 3 complete)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
