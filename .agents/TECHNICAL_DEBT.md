# Technical Debt

> **Purpose**: Track issues that require resolution but are not currently planned in a backlog.
>
> 1. **Temporary Patches**: Solutions that work but need robust implementation.
> 2. **Known Issues**: Problems identified that would interrupt current workflow.
> 3. **Future Improvements**: Value-add items that don't fit a specific backlog yet.
>
> **Goal**: Keep this list short. If an item is critical, move it to a backlog file.

**Priority Levels**:

- **Critical**: Blocking or causing data integrity issues.
- **High**: Significant hindrance or major value add.
- **Medium**: Annoyance or maintenance burden.
- **Low**: Polish or nice-to-have refactor.

---

## Active Items

### High Priority

- **High** — Playwright: Firefox unsupported for Browser Mode E2E. Document limitation and align CI matrices to run Chromium/WebKit only until Firefox flakiness (overlays, intercepted clicks, stepper gating) is resolved. Add note to QA docs and Playwright config guidance.

- **High** — Add Machine Dialog Regressions (2026-01-08 verification):
  - Backends still listed in machine categories on add menu
  - Cannot deselect categories (clicking toggles incorrectly)
  - Stepper number circles not theme-synced (hardcoded white, same in light/dark)
  - Category/Model selection redundant with Backend selection in Step 2
  - No capability config form triggered for liquid handlers with Hamilton backend
  - Advanced JSON shows uneditable blob after selection
  - **Target**: [asset_management_ux.md](./backlog/asset_management_ux.md)

- **High** — Guided Deck Setup UI:
  - Continue/Next button not visible after adding carriers
  - Container scrolling unclear
  - **Target**: [run_protocol_workflow.md](./backlog/run_protocol_workflow.md)

### Medium Priority

- **Medium** — Resource dialog "More filters" facets are hardcoded. Dynamically derive facet definitions/options from resource definitions so the filter chip dropdown stays in sync with available metadata.

- **Medium** — Angular ARIA Migration:
  - Replace custom chip/dropdown components with `@angular/aria` primitives
  - Use `@angular/aria/combobox` + `@angular/aria/listbox` for multiselect filters
  - Use `@angular/aria/grid` for well selector component
  - Targets: Machine filters, Backend filters, Spatial view categories, Well selector
  - **Target**: NEW backlog `angular_aria_migration.md`

- **Medium** — Settings Cards Visual Polish:
  - Rounded corners cut off icons
  - Visual inconsistency in layout
  - **Target**: [ui_consistency.md](./backlog/ui_consistency.md)

### Low Priority

- **Low** — Rename "REPL" to "Playground" throughout codebase. The JupyterLite-based notebook is not technically a REPL. Update component names, routes, nav labels, and documentation.

---

## Recently Resolved ✅

### 2026-01-08 Migration

| Item | Migrated To |
|------|-------------|
| Prompt Folder Cleanup | [cleanup_finalization.md](./backlog/cleanup_finalization.md) (Implicit in cleanup) |
| Base Repo Cleanup | [cleanup_finalization.md](./backlog/cleanup_finalization.md) |
| JupyterLite 404s/Load | [repl_enhancements.md](./backlog/repl_enhancements.md) |
| pylibftdi Incompatibility | ✅ Obsolete (superseded by `ISerial` abstraction) |
| Browser Schema Scripts | [browser_mode.md](./backlog/browser_mode.md) |
| SqliteService Blob Cast | [quality_assurance.md](./backlog/quality_assurance.md) |
| SettingsComponent Tests | [quality_assurance.md](./backlog/quality_assurance.md) |
| E2E Asset Seeding | [quality_assurance.md](./backlog/quality_assurance.md) |

### 2026-01-07 Migration

The following items were migrated to formal tracking:

| Item | Migrated To |
|------|-------------|
| SQLite Schema Mismatch | [browser_mode.md](./backlog/browser_mode.md) |
| Test Factory ORM Issues | [quality_assurance.md](./backlog/quality_assurance.md) |
| JupyterLite REPL Issues | [repl_enhancements.md](./backlog/repl_enhancements.md) |
| Skipped Tests | [quality_assurance.md](./backlog/quality_assurance.md) |
| Execution Monitor UI | [ui_consistency.md](./backlog/ui_consistency.md) |
| Asset Management UX | [asset_management_ux.md](./backlog/asset_management_ux.md) |
| Dataviz & Well Selection | [dataviz_well_selection.md](./backlog/dataviz_well_selection.md) |
| Asset API Restructuring | [run_protocol_workflow.md](./backlog/run_protocol_workflow.md) |
| Consumables & Auto-Assignment | [run_protocol_workflow.md](./backlog/run_protocol_workflow.md) |
| POST /resources/ API Error | [run_protocol_workflow.md](./backlog/run_protocol_workflow.md) |
| Navigation Rail Hover Menus | [ui_consistency.md](./backlog/ui_consistency.md) |
| Resource Model Typing | [quality_assurance.md](./backlog/quality_assurance.md) |
| REPL Shim Loading | [repl_enhancements.md](./backlog/repl_enhancements.md) |
| Hardware VID/PID Matrix | [reference/hardware_matrix.md](./reference/hardware_matrix.md) |

---

## Related Documents

- [DEVELOPMENT_MATRIX.md](./DEVELOPMENT_MATRIX.md) - Priority tracking
- [ROADMAP.md](./ROADMAP.md) - Milestone tracking
- [backlog/](./backlog/) - Detailed work items
