# Agent Prompt: 08_execution_monitor_phase1

Examine `.agents/README.md` for development context.

**Status:** ✅ Complete  
**Batch:** [260109](./README.md)  
**Backlog:** [execution_monitor.md](../../backlog/execution_monitor.md)  

---

## Task

Add "Monitor" navigation item to sidebar and create basic execution monitor overview page (Phase 1 of execution monitor enhancement).

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [execution_monitor.md](../../backlog/execution_monitor.md) | Work item tracking |
| `praxis/web-client/src/app/layout/unified-shell.component.ts` | Sidebar navigation |
| `praxis/web-client/src/app/app.routes.ts` | Route definitions |
| `praxis/web-client/src/app/features/execution-monitor/` | Target feature module |

---

## Implementation

1. **Add Sidebar Navigation**:
   - Add "Monitor" nav item to `unified-shell.component.ts`
   - Icon: `monitor_heart` or `assessment`
   - Route: `/app/monitor`
   - Position: After "Run" in sidebar

2. **Create Feature Module**:
   - Create `execution-monitor` feature module if not exists
   - Create basic `ExecutionMonitorComponent` with placeholder content
   - Add routes to `app.routes.ts`

3. **Basic Layout**:
   - Split view layout (active runs panel + history table placeholder)
   - Header with filters placeholder
   - Empty state when no runs

---

## Expected Outcome

- Monitor accessible in 1 click from sidebar
- Route `/app/monitor` renders the new component
- Ready for Phase 2 (active runs panel) and Phase 3 (history table)

---

## Project Conventions

- **Frontend Tests**: `cd praxis/web-client && npm test`

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status (mark Phase 1 complete)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
