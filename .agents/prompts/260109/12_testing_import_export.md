# Agent Prompt: Import/Export Database Tests

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed
**Priority:** P3
**Batch:** [260109](./README.md)
**Backlog Reference:** [testing.md](../../backlog/testing.md)

---

## 1. The Task

Create tests for the database import and export functionality. This includes:

- Database export in browser mode (SQLite dump)
- Database import/restore functionality
- Data integrity verification after import
- Version compatibility handling

**User Value:** Confidence that users can safely backup and restore their data without corruption or loss.

---

## 2. Technical Implementation Strategy

### Architecture Analysis

**Browser Mode:** Uses SQLite (via Pyodide/sql.js) with in-memory or IndexedDB persistence.
**Production Mode:** Uses PostgreSQL with standard pg_dump/pg_restore.

The import/export functionality likely exists in:

- Frontend: Service that orchestrates export/download
- Backend: API endpoints for export/import

### Investigation Required

Before writing tests, locate the actual implementation:

1. **Search for export functionality:**

   ```bash
   grep -rn "export\|backup\|dump" praxis/backend/api/
   grep -rn "export\|backup" praxis/web-client/src/app/
   ```

2. **Check WorkcellRuntime for state backup:**
   - `praxis/backend/core/workcell.py` has backup_interval and num_backups
   - This may be runtime state, not full DB

3. **Browser mode persistence:**
   - Check Pyodide/sql.js integration
   - Look for IndexedDB interaction

### Test Structure

```python
# tests/backend/api/test_database_export.py

import pytest
import json
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

class TestDatabaseExport:
    """Tests for database export functionality."""

    async def test_export_endpoint_returns_valid_format(self, client: TestClient):
        """Test that export endpoint returns valid JSON/SQL dump."""
        response = client.get("/api/v1/admin/export")
        assert response.status_code == 200
        # Verify response is valid JSON or SQL
        # Check content-type header

    async def test_export_includes_all_tables(self, client: TestClient, db_with_data):
        """Test that export includes machines, resources, protocols, etc."""
        response = client.get("/api/v1/admin/export")
        data = response.json()
        assert "machines" in data
        assert "resources" in data
        assert "protocol_definitions" in data

    async def test_export_excludes_sensitive_data(self, client: TestClient):
        """Test that export doesn't include credentials or tokens."""
        response = client.get("/api/v1/admin/export")
        data = response.content.decode()
        assert "password" not in data.lower()
        assert "secret" not in data.lower()


class TestDatabaseImport:
    """Tests for database import/restore functionality."""

    @pytest.fixture
    def valid_export_data(self):
        """Create valid export data for testing import."""
        return {
            "version": "1.0",
            "timestamp": "2026-01-09T00:00:00Z",
            "machines": [],
            "resources": [],
            "protocol_definitions": []
        }

    async def test_import_valid_data_succeeds(self, client: TestClient, valid_export_data):
        """Test successful import of valid data."""
        response = client.post(
            "/api/v1/admin/import",
            json=valid_export_data
        )
        assert response.status_code in [200, 201]

    async def test_import_invalid_format_rejected(self, client: TestClient):
        """Test that malformed data is rejected."""
        response = client.post(
            "/api/v1/admin/import",
            json={"invalid": "data"}
        )
        assert response.status_code == 400

    async def test_import_preserves_data_integrity(self, client: TestClient, valid_export_data):
        """Test that imported data matches original."""
        # Import data
        client.post("/api/v1/admin/import", json=valid_export_data)
        
        # Export it back
        response = client.get("/api/v1/admin/export")
        exported = response.json()
        
        # Verify data integrity
        assert exported["machines"] == valid_export_data["machines"]


class TestVersionCompatibility:
    """Tests for cross-version import compatibility."""

    async def test_import_older_version_with_migration(self, client: TestClient):
        """Test importing data from older version triggers migration."""
        old_format_data = {
            "version": "0.9",  # Older version
            "machines": []
        }
        response = client.post("/api/v1/admin/import", json=old_format_data)
        # Should either succeed with migration or fail gracefully

    async def test_import_newer_version_rejected(self, client: TestClient):
        """Test that future version data is rejected."""
        future_data = {
            "version": "99.0",
            "machines": []
        }
        response = client.post("/api/v1/admin/import", json=future_data)
        assert response.status_code == 400
```

### Browser Mode Specific Tests

If browser mode has different export mechanism, create separate tests:

```python
# tests/integration/test_browser_export.py

class TestBrowserModeExport:
    """Tests for browser-mode specific export (SQLite/IndexedDB)."""

    async def test_sqlite_export_to_file(self):
        """Test SQLite database export to downloadable file."""
        pass

    async def test_indexeddb_persistence(self):
        """Test data persists across sessions in IndexedDB."""
        pass
```

---

## 3. Context & References

**Primary Files to Create:**

| Path | Description |
|:-----|:------------|
| `tests/backend/api/test_database_export.py` | **NEW** - Export/import API tests |
| `tests/integration/test_browser_export.py` | **NEW** - Browser mode tests (if applicable) |

**Reference Files to Investigate:**

| Path | Description |
|:-----|:------------|
| `praxis/backend/api/` | Look for admin or export endpoints |
| `praxis/backend/core/workcell.py` | Backup functionality reference |
| `praxis/web-client/src/app/core/services/` | Frontend export service |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run pytest` for testing
- **Backend Path**: `praxis/backend`
- **Test Path**: `tests/backend/api/` for API tests
- **Fixtures**: Use existing patterns from `tests/conftest.py`
- **Database**: Use test database fixtures for isolation

---

## 5. Verification Plan

**Definition of Done:**

1. Locate actual export/import implementation
2. All new tests pass:

   ```bash
   uv run pytest tests/backend/api/test_database_export.py -v
   ```

3. Integration tests (if applicable):

   ```bash
   uv run pytest tests/integration/test_browser_export.py -v
   ```

4. No regressions:

   ```bash
   uv run pytest tests/backend/api/ -v
   ```

---

## On Completion

- [ ] Document where export/import is implemented (may need to create if missing)
- [ ] Commit changes with message: `test: add database import/export tests`
- [ ] Update backlog item status in [testing.md](../../backlog/testing.md)
- [ ] Mark this prompt complete in batch README, update DEVELOPMENT_MATRIX.md if applicable, and set the status in this prompt document to 🟢 Completed

---

## Notes for Implementer

**If export/import doesn't exist yet:**
This prompt may reveal that the functionality needs to be implemented first. In that case:

1. Document the gap in TECHNICAL_DEBT.md
2. Create stub tests that mark expected behavior
3. Create a follow-up backlog item for implementation

---

## References

- `.agents/README.md` - Environment overview
- `tests/TESTING_PATTERNS.md` - Project testing conventions
- `.agents/codestyles/python.md` - Python conventions
