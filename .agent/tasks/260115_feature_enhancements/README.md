# Task Batch: Feature Enhancements (260115)

**Status:** 🟡 In Progress
**Created:** 2026-01-15
**Goal:** Implement state inspection backend, fix simulation machine visibility, browser resource initialization, and view controls UX improvements.

## Tasks

| Status | ID | Task | Priority | Difficulty | Description |
| :------- | :--- | :------------ | :--- | :--- | :------------ |
| ⚪ Not Started | FE-01 | [state_inspection_backend](./state_inspection_backend/) | P1 | Hard | Post-run "time travel" for backend executions |
| ⚪ Not Started | FE-02 | [browser_resources_init](./browser_resources_init/) | P2 | Easy | Seed 1-of-each labware in browser mode |
| ⚪ Not Started | FE-03 | [view_controls_chips](./view_controls_chips/) | P2 | Medium | Unified filter chip bar with icons + tooltips |
| ⚪ Not Started | FE-04 | [sim_machines_visibility](./sim_machines_visibility/) | P1 | Hard | Frontend-only sim until instantiation |

## Recommended Execution Order

1. **FE-04** (sim_machines_visibility) - Blocks other UX work, high priority
2. **FE-01** (state_inspection_backend) - Backend foundation for monitoring
3. **FE-02** (browser_resources_init) - Quick win, easy implementation
4. **FE-03** (view_controls_chips) - UX polish

## Completion Checklist

- [ ] All tasks marked as ✅ Completed
- [ ] Findings consolidated into `TECHNICAL_DEBT.md` or new backlog items
- [ ] Archive batch when all tasks complete
