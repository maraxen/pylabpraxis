# Prompt Batch: 260108

**Created:** 2026-01-08
**Status:** 🟢 Ready for Dispatch

---

## Prompts

| # | Prompt | Backlog Item | Priority | Difficulty | Status |
|---|--------|--------------|----------|------------|--------|
| 01 | [schema_mismatch_fix](./01_schema_mismatch_fix.md) | SQLite `inferred_requirements_json` column | CRITICAL | M | ✅ Complete |
| 02 | [e2e_tests_asset_management](./02_e2e_tests_asset_management.md) | E2E Test Suite - Asset CRUD | P2 | M | 🟢 Not Started |
| 03 | [unique_name_parsing](./03_unique_name_parsing.md) | Filter chip unique name extraction | P2 | M | 🟢 Not Started |
| 04 | [ui_visual_tweaks](./04_ui_visual_tweaks.md) | Registry/Machine tab spacing | P3 | S | 🟢 Not Started |
| 05 | [pre_merge_finalization](./05_pre_merge_finalization.md) | Archive & documentation cleanup | P3 | M | 🟢 Not Started |

---

## Selection Criteria

Items selected based on:

1. **Priority**: CRITICAL > P2 > P3
2. **Status**: 🟢 Planned items ready for work
3. **Dependencies**: Unblocked items first
4. **Agent dispatch suitability**: Well-specified, scoped tasks

---

## Execution Order

1. **01_schema_mismatch_fix** (CRITICAL) - Blocking simulation data fetch
2. **02_e2e_tests_asset_management** (P2) - Quality assurance foundation
3. **03_unique_name_parsing** (P2) - UX improvement
4. **04_ui_visual_tweaks** (P3) - Polish
5. **05_pre_merge_finalization** (P3) - Cleanup (execute last)

---

## Notes

- All prompts follow [agent_prompt.md](../../templates/agent_prompt.md) template
- Items sourced from [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md), [ROADMAP.md](../../ROADMAP.md), and [TECHNICAL_DEBT.md](../../TECHNICAL_DEBT.md)
