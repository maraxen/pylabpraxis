# Batch Box: Feature Enhancements (260115)

**Status:** 🟡 In Progress
**Created:** 2026-01-15
**Goal:** Implement state inspection backend, fix simulation machine visibility, browser resource initialization, and view controls UX improvements.

## Prompts

| Status | ID | Prompt Name | Description |
| :------- | :--- | :------------ | :------------ |
| 🔵 Ready | [01_state_inspection_I](./01_state_inspection_backend_I.md) | State Inspection (I) | Inspect current FunctionCallLog and state capture gaps |
| ⚪ Queued | [01_state_inspection_P](./01_state_inspection_backend_P.md) | State Inspection (P) | Plan schema updates and API endpoint |
| ⚪ Queued | [01_state_inspection_E](./01_state_inspection_backend_E.md) | State Inspection (E) | Implement state capture and history endpoint |
| 🔵 Ready | [02_browser_resources_I](./02_browser_resources_init_I.md) | Browser Resources (I) | Inspect current resource initialization in browser mode |
| ⚪ Queued | [02_browser_resources_P](./02_browser_resources_init_P.md) | Browser Resources (P) | Plan 1-of-each labware initialization |
| ⚪ Queued | [02_browser_resources_E](./02_browser_resources_init_E.md) | Browser Resources (E) | Implement browser mode resource seeding |
| 🔵 Ready | [03_view_controls_I](./03_view_controls_chips_I.md) | View Controls (I) | Inspect current dropdown and chip rendering |
| ⚪ Queued | [03_view_controls_P](./03_view_controls_chips_P.md) | View Controls (P) | Plan filter chip bar with icons and tooltips |
| ⚪ Queued | [03_view_controls_E](./03_view_controls_chips_E.md) | View Controls (E) | Implement unified filter chip bar |
| 🔵 Ready | [04_sim_machines_I](./04_sim_machines_visibility_I.md) | Sim Machines (I) | Inspect why backends show in inventory |
| ⚪ Queued | [04_sim_machines_P](./04_sim_machines_visibility_P.md) | Sim Machines (P) | Plan frontend-only simulation until instantiation |
| ⚪ Queued | [04_sim_machines_E](./04_sim_machines_visibility_E.md) | Sim Machines (E) | Implement deferred simulation instantiation |

## Completion Checklist

- [ ] All prompts marked as Completed
- [ ] Findings consolidated into `TECHNICAL_DEBT.md` or new backlog items
