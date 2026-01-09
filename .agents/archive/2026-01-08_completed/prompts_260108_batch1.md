# Archived Prompts: 260108 Batch 1

**Archived:** 2026-01-08
**Source:** `.agents/prompts/260108/`

---

## Summary

This archive consolidates completed prompts from the 260108 batch, covering schema fixes, UI standardization, and quality assurance improvements.

---

## Completed Prompts

### Critical / Infrastructure

| # | Prompt | Description | Completed |
|---|--------|-------------|-----------|
| 01 | schema_mismatch_fix | Fixed `inferred_requirements_json` column missing in browser SQLite | 2026-01-07 |
| 10 | browser_schema_scripts | Fixed `generate_browser_schema.py` and `generate_browser_db.py` | 2026-01-08 |

### UI & UX Standardization

| # | Prompt | Description | Completed |
|---|--------|-------------|-----------|
| 03 | unique_name_parsing | Implemented word-based name shortening for filter chips | 2026-01-08 |
| 06 | repl_rendering_stability | Fixed REPL kernel refresh race condition with ready signal | 2026-01-08 |
| 07 | ui_consistency_exec_monitor | Standardized dropdown chips in Execution Monitor | 2026-01-08 |
| 08 | asset_management_ux | Refactored Add Machine/Resource flows | 2026-01-08 |
| 16 | asset_management_ux_fix | Fixed Add Machine dialog regressions | 2026-01-08 |
| 18 | angular_aria_multiselect | Created AriaMultiselectComponent and AriaSelectComponent | 2026-01-08 |
| 19 | aria_well_selector_grid | Created WellSelectorComponent with ARIA Grid | 2026-01-08 |
| 20 | settings_stepper_polish | Fixed settings icons and stepper theme sync | 2026-01-08 |

### Quality Assurance

| # | Prompt | Description | Completed |
|---|--------|-------------|-----------|
| 09 | factory_orm_integration | Fixed Factory Boy FK population for ORM tests | 2026-01-08 |

---

## Files Affected

### Infrastructure

- `praxis/web-client/src/assets/browser-db/schema.sql`
- `praxis/web-client/src/app/core/services/sqlite.service.ts`
- `scripts/generate_browser_schema.py`
- `scripts/generate_browser_db.py`

### UI Components

- `praxis/web-client/src/app/shared/utils/name-parser.ts`
- `praxis/web-client/src/app/shared/components/filter-chip/`
- `praxis/web-client/src/app/shared/components/aria-select/`
- `praxis/web-client/src/app/shared/components/aria-multiselect/`
- `praxis/web-client/src/app/shared/components/aria-autocomplete/`
- `praxis/web-client/src/app/shared/components/well-selector/`
- `praxis/web-client/src/app/features/settings/`
- `praxis/web-client/src/app/features/assets/`
- `praxis/web-client/src/app/features/repl/`

### Testing

- `tests/factories.py`
- `tests/services/test_well_outputs.py`

---

## Related Documents

- [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [chip_filter_standardization.md](./chip_filter_standardization.md) (archived)
- [TECHNICAL_DEBT.md](../../TECHNICAL_DEBT.md)
