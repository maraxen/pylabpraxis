# Technical Debt / Missing Features

## Testing

- **Database Export/Import**: `tests/backend/api/test_database_export.py` contains stub tests marked `xfail`.
  - [ ] Implement Admin API for export/import

  - [x] Browser mode export button implementation (tested in `tests/integration/test_browser_export.py`)

## Playground

- **Programmatic Well Selection**: Support generic programmatic selection of wells (e.g., via API or Python context) instead of just UI interaction.
  - [ ] Define API for programmatic selection
  - [ ] Implement selection state synchronization
