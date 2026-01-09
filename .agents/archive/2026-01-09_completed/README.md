# Prompt Batch: 260109

**Created:** 2026-01-09
**Status:** 🔵 In Progress (18/37 complete)

---

## Active Prompts

| # | Prompt | Backlog Item | Priority | Difficulty | Status |
| :- | :----- | :----------- | :------- | :--------- | :----- |
| 01 | [protocol_analysis_status](./01_protocol_analysis_status.md) | Protocol "Not Analyzed" investigation | P2 | M | ✅ Done |
| 02 | [asset_autoselection_fix](./02_asset_autoselection_fix.md) | Fix buggy asset autoselection | P2 | M | ✅ Done |
| 03 | [machine_backend_mismatch](./03_machine_backend_mismatch.md) | 0 backends shown (73 loaded) | P2 | M | ✅ Done |
| 04 | [guided_deck_confirm_button](./04_guided_deck_confirm_button.md) | Confirm & Continue broken | P2 | S | ✅ Done |
| 05 | [resource_dialog_dynamic_facets](./05_resource_dialog_dynamic_facets.md) | Dynamic filter facets | P3 | M | 🟢 Not Started |
| 06 | [navigation_rename_deck](./06_navigation_rename_deck.md) | Deck → Workcell rename | P3 | S | ✅ Done |
| 07 | [repl_theme_sync](./07_repl_theme_sync.md) | JupyterLite theme sync | P3 | M | ✅ Done |
| 08 | [execution_monitor_phase1](./08_execution_monitor_phase1.md) | Monitor sidebar + basic page | P2 | M | ✅ Done |
| 09 | [browser_db_sync](./09_browser_db_sync.md) | DB sync & schema versioning | P1 | M | ✅ Done |
| 10 | [dataviz_backend_integration](./10_dataviz_backend_integration.md) | Visualization API endpoints | P2 | L | ✅ Done |
| 11 | [aria_interactive_states](./11_aria_interactive_states.md) | Fix ARIA component states | P3 | S | ✅ Done |
| 12 | [ty_type_checking](./12_ty_type_checking.md) | Run ty, fix type errors | P2 | M | ✅ Done |
| 13 | [visual_qa_checklist](./13_visual_qa_checklist.md) | Complete QA checklist | P2 | L | 🟢 Not Started |
| 14 | [hardware_vid_pid_sync](./14_hardware_vid_pid_sync.md) | Dynamic VID/PID from PLR | P3 | M | 🟢 Not Started |
| 15 | [ruff_remaining_fixes](./15_ruff_remaining_fixes.md) | Ruff errors < 20 | P2 | S | 🟢 Not Started |
| 16 | [stepper_navigation_relaxation](./16_stepper_navigation_relaxation.md) | Allow broader step navigation | P3 | S | 🟢 Not Started |
| 17 | [example_protocols](./17_example_protocols.md) | Add example protocols | P3 | S | ✅ Done |
| 18 | [execution_monitor_active_runs](./18_execution_monitor_active_runs.md) | Active Runs Panel (Phase 2) | P2 | M | ✅ Done |
| 19 | [execution_monitor_history](./19_execution_monitor_history.md) | Run History Table (Phase 3) | P2 | M | ✅ Done |
| 20 | [browser_schema_unique_constraint](./20_browser_schema_unique_constraint.md) | Fix UNIQUE constraint on name | P2 | S | ✅ Done |
| 21 | [machine_definition_schema_linkage](./21_machine_definition_schema_linkage.md) | Add definition_accession_id | P1 | S | ✅ Done |
| 22 | [aria_component_polish](./22_aria_component_polish.md) | ARIA focus, theme, sleek multiselect | P2 | M | ✅ Done |
| 23 | [well_selector_dialog](./23_well_selector_dialog.md) | Well dialog with row/col selection | P2 | L | ✅ Done |
| 24 | [well_selection_protocol](./24_well_selection_protocol.md) | Example protocol for well selection | P2 | M | 🟢 Not Started |
| 25 | [footer_navigation_layout](./25_footer_navigation_layout.md) | Eliminate header, add footer bar | P3 | S | ✅ Done |
| 26 | [protocol_workflow_debugging](./26_protocol_workflow_debugging.md) | Protocol workflow bugs & layout | P2 | M | ✅ Done (merged into 38) |
| 28 | [deck_type_dynamic](./28_deck_type_dynamic.md) | Fix hardcoded deck type | P2 | M | 🟢 Not Started |
| 29 | [protocol_detail_dialog](./29_protocol_detail_dialog.md) | Replace page with dialog | P2 | M | 🟢 Not Started |
| 30 | [demo_to_browser_mode](./30_demo_to_browser_mode.md) | Eliminate "Demo" terminology | P2 | S | 🟢 Not Started |
| 31 | [data_well_selection](./31_data_well_selection.md) | Use well selector in data viz | P2 | M | 🟢 Not Started |
| 32 | [inventory_dialog_redesign](./32_inventory_dialog_redesign.md) | Tabbed inventory dialog | P2 | L | ✅ Done |
| 33 | [docs_diagram_expand](./33_docs_diagram_expand.md) | Expandable Mermaid diagrams | P3 | S | 🟢 Not Started |
| 34 | [asset_search_filter_pattern](./34_asset_search_filter_pattern.md) | Consistent search+filter UX | P2 | M | ✅ Done |
| 35 | [workcell_machine_filter](./35_workcell_machine_filter.md) | Filter to liquid handlers | P2 | S | 🟢 Not Started |
| 36 | [css_hardcode_audit](./36_css_hardcode_audit.md) | Audit hardcoded CSS values | P3 | M | ✅ Done |
| 37 | [protocol_hydration_fix](./37_protocol_hydration_fix.md) | Protocol params/assets + arg filtering | **P1** | M | ✅ Done |
| 38 | [run_persistence_well_selection](./38_run_persistence_well_selection.md) | Run persistence + well selection step | **P2** | L | 🟢 Not Started |

---

## Selection Criteria

Items selected based on:

1. **Priority**: P1 > P2 > P3 (Critical first)
2. **Status**: 🟢 Planned items ready for work
3. **Dependencies**: Unblocked items first
4. **Agent dispatch suitability**: Well-specified, scoped tasks

---

## Execution Order

### Critical (P1) - Execute First

1. **37_protocol_hydration_fix** - Protocol params/assets hydration + machine arg filtering (NEW)
2. ~~**09_browser_db_sync**~~ - ✅ Done
3. ~~**21_machine_definition_schema_linkage**~~ - ✅ Done

### High Priority (P2) - Core Functionality

1. **01_protocol_analysis_status** - Protocols show "Not Analyzed"
2. **02_asset_autoselection_fix** - Autoselection buggy
3. **03_machine_backend_mismatch** - 0 backends displayed
4. **04_guided_deck_confirm_button** - Confirm broken
5. **08_execution_monitor_phase1** - Sidebar navigation
6. **18_execution_monitor_active_runs** - Active runs panel
7. **19_execution_monitor_history** - History table
8. **12_ty_type_checking** - Type checking
9. **15_ruff_remaining_fixes** - Linting fixes
10. **10_dataviz_backend_integration** - Visualization API
11. **13_visual_qa_checklist** - QA checklist
12. **20_browser_schema_unique_constraint** - UNIQUE constraint

### Medium Priority (P3) - Polish

1. **05_resource_dialog_dynamic_facets** - Dynamic facets
2. **06_navigation_rename_deck** - Deck → Workcell
3. **07_repl_theme_sync** - Theme sync
4. **11_aria_interactive_states** - ARIA state fix
5. **14_hardware_vid_pid_sync** - VID/PID sync
6. **16_stepper_navigation_relaxation** - Stepper UX
7. **17_example_protocols** - Example protocols

---

## Backlog Coverage

| Backlog | Items Covered |
| :------ | :------------ |
| [run_protocol_workflow.md](../../backlog/run_protocol_workflow.md) | 01, 02, 04, 16, 17, 26, 28 |
| [asset_management_ux.md](../../backlog/asset_management_ux.md) | 03, 34 |
| [ui_consistency.md](../../backlog/ui_consistency.md) | 05, 06, 11, 25, 36 |
| [repl_enhancements.md](../../backlog/repl_enhancements.md) | 07, 32 |
| [execution_monitor.md](../../backlog/execution_monitor.md) | 08, 18, 19 |
| [browser_mode.md](../../backlog/browser_mode.md) | 09, 20, 21, 30, 35 |
| [dataviz_well_selection.md](../../backlog/dataviz_well_selection.md) | 10, 23, 24, 31 |
| [quality_assurance.md](../../backlog/quality_assurance.md) | 12, 13, 15 |
| [hardware_connectivity.md](../../backlog/hardware_connectivity.md) | 14 |
| [angular_aria_migration.md](../../backlog/angular_aria_migration.md) | 22 |
| [ux_issues_260109.md](../../backlog/ux_issues_260109.md) | 28-36 (NEW) |

---

## Excluded Items

| Item | Reason |
|------|--------|
| Hamilton E2E Validation | Requires physical hardware |
| Machine Capabilities Verification | Requires physical hardware |
| Scheduler Full Implementation | Extra Large (XL), needs planning |
| Dataviz Phase 3 (charts) | Depends on Phase 1-2 completion |

---

## Notes

- All prompts follow [agent_prompt.md](../../templates/agent_prompt.md) template
- Items sourced from [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md), backlogs, and [TECHNICAL_DEBT.md](../../TECHNICAL_DEBT.md)
- Hardware-dependent items excluded from agent dispatch
- Remaining 260108 prompts (11, 13, 14, 17, 21, 22) still active
