# Technical Debt / Missing Features

## Testing

- **Database Export/Import**: `tests/backend/api/test_database_export.py` contains stub tests marked `xfail`.
  - [ ] Implement Admin API for export/import

  - [x] Browser mode export button implementation (tested in `tests/integration/test_browser_export.py`)

## Playground

- **Programmatic Well Selection**: Support generic programmatic selection of wells (e.g., via API or Python context) instead of just UI interaction.
  - [ ] Define API for programmatic selection
  - [ ] Implement selection state synchronization

## Simulation & Workcell Visualization

- **Deck Configuration Visualizer**: Improve the UX and robustness of the workcell deck configuration view.
  - [ ] Add validation to deck states to prevent invalid configurations.
  - [ ] Improve overall UX of the visualizer (interactions, layout, feedback).
  - [ ] Add missing deck definitions to simulation options (e.g., Vantage deck and others).

## Documentation & UX Stability

- **Missing Production Docs**: Many `*-production.md` files are missing from `docs/`, causing snackbar errors when navigated to.
  - [ ] Create missing `*-production.md` documentation files.
  - [ ] Silence 404 snackbar errors for missing doc files specifically in **browser mode**.

- **Unified Documentation View**: Currently using Sphinx for docs/API and Material for MkDocs for potential blog/guides.
  - [ ] Consolidate all documentation generation to a single tool (likely MkDocs) for consistent theming and easier maintenance.
  - [ ] Ensure the "Blog" section is integrated into the main documentation site.

## Agent / Task Infrastructure

- **Progressive Disclosure for Tasks**: Implement a progressive disclosure mechanism for task creation/management to allow for more in-depth notes without cluttering the primary view.
  - [ ] Design UX for progressive disclosure (e.g., expandable sections, modals, or drill-down).
  - [ ] Implement support for deep metadata/notes in `.agent/tasks`.

- **Standardized Agent Workflows**: Create and document standardized workflows (via `.agent/workflows/`) for core agent activities.
  - [ ] Inspection Workflow (e.g., `/inspect`)
  - [ ] Planning Workflow (e.g., `/plan`)
  - [ ] Execution Workflow (e.g., `/execute`)
  - [ ] Testing & Verification Workflow (e.g., `/verify`)
