# Technical Debt / Missing Features

## Testing

- **Database Export/Import**: `tests/backend/api/test_database_export.py` contains stub tests marked `xfail`.
  - [ ] Implement Admin API for export/import
  - [x] Browser mode export button implementation (tested in `tests/integration/test_browser_export.py`)
