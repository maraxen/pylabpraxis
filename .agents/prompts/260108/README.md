# Prompt Batch: 260108

**Created:** 2026-01-08
**Status:** 🟡 In Progress

---

## Prompts

| # | Prompt | Backlog Item | Priority | Difficulty | Status |
|---|--------|--------------|----------|------------|--------|
| 01 | [schema_mismatch_fix](./01_schema_mismatch_fix.md) | SQLite `inferred_requirements_json` column | CRITICAL | M | ✅ Complete |
| 02 | [e2e_tests_asset_management](./02_e2e_tests_asset_management.md) | E2E Test Suite - Asset CRUD | P2 | M | 🟡 In Progress |
| 03 | [unique_name_parsing](./03_unique_name_parsing.md) | Filter chip unique name extraction | P2 | M | ✅ Complete |
| 04 | [ui_visual_tweaks](./04_ui_visual_tweaks.md) | Registry/Machine tab spacing | P3 | S | 🟡 In Progress |
| 05 | [pre_merge_finalization](./05_pre_merge_finalization.md) | Archive & documentation cleanup | P3 | M | 🟢 Not Started |
| 06 | [repl_rendering_stability](./06_repl_rendering_stability.md) | REPL kernel refresh race condition | P2 | M | ✅ Complete |
| 07 | [ui_consistency_exec_monitor](./07_ui_consistency_exec_monitor.md) | Execution Monitor dropdown chips | P2 | M | ✅ Complete |
| 08 | [asset_management_ux](./08_asset_management_ux.md) | Add Machine/Resource flow refactor | P2 | M | ⚠️ Regressions |
| 09 | [factory_orm_integration](./09_factory_orm_integration.md) | Factory Boy FK population fixes | P2 | M | 🟢 Not Started |
| 10 | [browser_schema_scripts](./10_browser_schema_scripts.md) | Fix schema generation scripts | P2 | M | ✅ Complete |
| 11 | [e2e_data_seeding](./11_e2e_data_seeding.md) | Pre-populate DB for Playwright tests | P2 | M | 🟢 Not Started |
| 12 | [e2e_protocol_execution](./12_e2e_protocol_execution.md) | E2E Tests - Protocol execution flow | P2 | M | 🟢 Not Started |
| 13 | [frontend_type_safety](./13_frontend_type_safety.md) | Fix Blob casting & Window mocking | P3 | S | 🟢 Not Started |
| 14 | [jupyterlite_cleanup](./14_jupyterlite_cleanup.md) | Suppress 404s, optimize load | P3 | M | 🟢 Not Started |
| 15 | [repo_cleanup](./15_repo_cleanup.md) | Remove .pymon, debug files | P3 | S | 🟢 Not Started |
| 16 | [asset_management_ux_fix](./16_asset_management_ux_fix.md) | Fix Add Machine regressions | P2 | M | ✅ Partially Fixed |

- [x] [17_guided_deck_setup_ui.md](./17_guided_deck_setup_ui.md) - Fix Guided Deck Setup UI issues
| 18 | [angular_aria_multiselect](./18_angular_aria_multiselect.md) | ARIA multiselect component | P2 | L | 🟢 Not Started |
| 19 | [aria_well_selector_grid](./19_aria_well_selector_grid.md) | ARIA Grid well selector | P2 | L | 🟢 Not Started |
| 20 | [settings_stepper_polish](./20_settings_stepper_polish.md) | Settings icons, stepper theme | P3 | S | ✅ Complete |

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
