# Agent Prompt: 18_execution_monitor_active_runs

Examine `.agents/README.md` for development context.

**Status:** ✅ Complete  
**Batch:** [260109](./README.md)  
**Backlog:** [execution_monitor.md](../../backlog/execution_monitor.md)  

---

## Task

Implement the Active Runs Panel for the Execution Monitor (Phase 2). Show currently running protocols with real-time status updates.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [execution_monitor.md](../../backlog/execution_monitor.md) | Work item tracking (Phase 2) |
| `praxis/web-client/src/app/features/execution-monitor/` | Feature module |
| `praxis/web-client/src/app/core/services/execution.service.ts` | Execution WebSocket |

---

## Implementation

### Component: `ActiveRunsPanelComponent`

1. **Real-time Updates**:
   - Subscribe to `ExecutionService` for current runs
   - WebSocket updates for progress changes

2. **Display Fields**:
   - Protocol name
   - Status (RUNNING, QUEUED, PREPARING)
   - Progress percentage
   - Elapsed time
   - Click to view details

3. **Visual Indicators**:

| Status | Color | Icon |
|--------|-------|------|
| RUNNING | Green | `play_circle` |
| QUEUED | Amber | `schedule` |
| PREPARING | Blue | `hourglass_empty` |

1. **Queue Position**:
   - Show queue position for QUEUED runs
   - Estimated start time if available

---

## Expected Outcome

- Active runs show with real-time updates
- Visual status indicators match design spec
- Clicking a run navigates to detail view

---

## Project Conventions

- **Frontend Tests**: `cd praxis/web-client && npm test`

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status (mark Phase 2 complete)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
