# Technical Debt / Missing Features

## Testing

- **Database Export/Import**: `tests/backend/api/test_database_export.py` contains stub tests marked `xfail`.
  - [ ] Implement Admin API for export/import

  - [x] Browser mode export button implementation (tested in `tests/integration/test_browser_export.py`)

## Playground

- **Programmatic Well Selection**: Support generic programmatic selection of wells (e.g., via API or Python context) instead of just UI interaction.
  - [ ] Define API for programmatic selection
  - [ ] Implement selection state synchronization

## Agent / Task Infrastructure

- **Progressive Disclosure for Tasks**: Implement a progressive disclosure mechanism for task creation/management to allow for more in-depth notes without cluttering the primary view.
  - [ ] Design UX for progressive disclosure (e.g., expandable sections, modals, or drill-down).
  - [ ] Implement support for deep metadata/notes in `.agent/tasks`.

- **Standardized Agent Workflows**: Create and document standardized workflows (via `.agent/workflows/`) for core agent activities.
  - [ ] Inspection Workflow (e.g., `/inspect`)
  - [ ] Planning Workflow (e.g., `/plan`)
  - [ ] Execution Workflow (e.g., `/execute`)
  - [ ] Testing & Verification Workflow (e.g., `/verify`)
