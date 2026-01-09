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

- **High** — Asset Autoselection:
  - User reports autoselection "seems buggy".
  - Investigate auto-assignment logic in `AssetManager` or `ProtocolService`.
  - Verify if it is strictly selecting compatible resources or if fallback logic is flawed.
  - **Target**: [run_protocol_workflow.md](./backlog/run_protocol_workflow.md)

- **High** — Machine Backend Mismatch:
  - "Add Machine" lists 0 backends, but logs show 73 simulated backends loaded.
  - Likely due to excessive simulated frontends per category.
  - **Action**: Enforce singleton pattern for simulated frontends per category; investigate DB/processing.
  - **Target**: [asset_management_ux.md](./backlog/asset_management_ux.md)

### Medium Priority

- **Medium** — Resource dialog "More filters" facets are hardcoded. Dynamically derive facet definitions/options from resource definitions so the filter chip dropdown stays in sync with available metadata.

### Low Priority

- **Low** — Rename "REPL" to "Playground" throughout codebase. The JupyterLite-based notebook is not technically a REPL. Update component names, routes, nav labels, and documentation.

---

## Recently Resolved ✅

### 2026-01-09 Migration

| Item | Migrated To |
|------|-------------|
| Playwright Firefox E2E Limitation | [quality_assurance.md](./backlog/quality_assurance.md) |
| Resource Dialog Facets | [ui_consistency.md](./backlog/ui_consistency.md) |
| Add Machine Dialog Regressions | Already in [asset_management_ux.md](./backlog/asset_management_ux.md) (Phase 1) |
| Guided Deck Setup UI | Already in [run_protocol_workflow.md](./backlog/run_protocol_workflow.md) |
| Asset Autoselection | Already in [run_protocol_workflow.md](./backlog/run_protocol_workflow.md) |
| Machine Backend Mismatch | Already in [asset_management_ux.md](./backlog/asset_management_ux.md) (Phase 4) |
| Protocols "Not Analyzed" | Already in [run_protocol_workflow.md](./backlog/run_protocol_workflow.md) |
| Angular ARIA Migration | Already in [angular_aria_migration.md](./backlog/angular_aria_migration.md) |
| Settings Cards Visual Polish | Already in [ui_consistency.md](./backlog/ui_consistency.md) (Phase 3) |
| Rename REPL to Playground | Already in [repl_enhancements.md](./backlog/repl_enhancements.md) (Phase 6) |

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
