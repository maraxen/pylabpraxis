# Prompt Batch: 260108

**Created:** 2026-01-08
**Status:** 🟡 In Progress (21 archived, 1 remaining)
**Archived:** [archive/prompts/260108/](../../archive/prompts/260108/)

---

## Active Prompts

| # | Prompt | Backlog Item | Priority | Difficulty | Status |
|---|--------|--------------|----------|------------|--------|

| 21 | [playground_enhancements](./21_playground_enhancements.md) | Playground rename & Inventory Dialog | P2 | M | 🟡 In Progress |

## Archived Prompts ✅ (21)

See [archive/prompts/260108/](../../archive/prompts/260108/) and [prompts_260108_batch1.md](../../archive/2026-01-08_completed/prompts_260108_batch1.md)

| #  | Prompt                                                                         | Description                                    |
|----|--------------------------------------------------------------------------------|------------------------------------------------|
| 11 | [e2e_data_seeding](../../archive/prompts/260108/11_e2e_data_seeding.md)         | Pre-populate DB for Playwright tests           |
| 12 | [e2e_protocol_execution](../../archive/prompts/260108/12_e2e_protocol_execution.md) | E2E Tests - Protocol execution flow            |
| 15 | [repo_cleanup](../../archive/prompts/260108/15_repo_cleanup.md)                 | Remove .pymon, debug files                     |
| 17 | [guided_deck_setup_ui](../../archive/prompts/260108/17_guided_deck_setup_ui.md) | Fix Guided Deck Setup UI issues                |
| 22 | [deck_view_investigation](../../archive/prompts/260108/22_deck_view_investigation.md) | Deck view inconsistency audit              |
| 02 | e2e_tests_asset_management                                                     | E2E Test Suite - Asset CRUD                    |
| 01 | schema_mismatch_fix                                                            | SQLite `inferred_requirements_json` column fix |
| 03 | unique_name_parsing                                                            | Filter chip unique name extraction             |
| 04 | ui_visual_tweaks                                                               | Registry/Machine tab spacing & gradients        |
| 05 | pre_merge_finalization                                                         | Archive & documentation cleanup                |
| 06 | repl_rendering_stability                                                       | REPL kernel refresh race condition              |
| 07 | ui_consistency_exec_monitor                                                    | Execution Monitor dropdown chips               |
| 08 | asset_management_ux                                                            | Add Machine/Resource flow refactor             |
| 09 | factory_orm_integration                                                        | Factory Boy FK population fixes                |
| 10 | browser_schema_scripts                                                         | Fix schema generation scripts                  |
| 16 | asset_management_ux_fix                                                        | Fix Add Machine regressions                    |
| 18 | angular_aria_multiselect                                                       | ARIA multiselect component                     |
| 19 | aria_well_selector_grid                                                        | ARIA Grid well selector                        |
| 20 | settings_stepper_polish                                                        | Settings icons, stepper theme                  |
| 13 | frontend_type_safety                                                           | Fix Blob casting & Window mocking              |
| 14 | jupyterlite_cleanup                                                            | Suppress 404s, optimize load                   |

---

## Selection Criteria

Items selected based on:

1. **Priority**: CRITICAL > P2 > P3
2. **Status**: 🟢 Planned items ready for work
3. **Dependencies**: Unblocked items first
4. **Agent dispatch suitability**: Well-specified, scoped tasks

---

## Execution Order

### Critical / P2 - Quality & Testing

1. **01_schema_mismatch_fix** (CRITICAL) ✅ - Blocking simulation data fetch
2. **02_e2e_tests_asset_management** (P2) 🟡 - Quality assurance foundation
3. **11_e2e_data_seeding** (P2) - Required for asset CRUD tests
4. **12_e2e_protocol_execution** (P2) - Protocol flow coverage
5. **09_factory_orm_integration** (P2) - Test infrastructure fix

### P2 - UI & UX

1. **03_unique_name_parsing** (P2) ✅ - Filter chip UX
2. **07_ui_consistency_exec_monitor** (P2) - Dropdown chip patterns
3. **08_asset_management_ux** (P2) - Add Machine/Resource flows

### P2 - Infrastructure

1. **06_repl_rendering_stability** (P2) - Kernel initialization
2. **10_browser_schema_scripts** (P2) - Schema generation fix

### P3 - Polish & Cleanup (Execute Last)

1. **04_ui_visual_tweaks** (P3) 🟡 - Visual polish
2. **13_frontend_type_safety** (P3) - Type fixes
3. **14_jupyterlite_cleanup** (P3) - 404 suppression
4. **15_repo_cleanup** (P3) - File cleanup
5. **05_pre_merge_finalization** (P3) - Archive & docs (execute last)

---

## Excluded Items

| Item | Reason |
|------|--------|
| Hamilton E2E Validation | Requires physical hardware |
| Machine Capabilities Verification | Requires physical hardware |
| Dataviz & Well Selection | Complex (🔴), needs planning |
| Code Quality Plan Execution | Extra Large (XL), break into sub-tasks |

---

## Notes

- All prompts follow [agent_prompt.md](../../templates/agent_prompt.md) template
- Items sourced from [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md), [ROADMAP.md](../../ROADMAP.md), and [TECHNICAL_DEBT.md](../../TECHNICAL_DEBT.md)
- Hardware-dependent items excluded from agent dispatch
