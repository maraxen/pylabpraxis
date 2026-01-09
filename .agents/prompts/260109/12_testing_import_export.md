# Agent Prompt: Database Import/Export Tests

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed
**Priority:** P3
**Batch:** [260109](./README.md)
**Backlog Reference:** [testing.md](../../backlog/testing.md)

---

## 1. The Task

Review and complete the stub tests for database import/export functionality. Test files already exist but are marked `xfail` as the feature is not yet implemented.

**Current State:**
- `tests/backend/api/test_database_export.py` - Stub tests (118 lines, marked xfail)
- `tests/integration/test_browser_export.py` - Stub tests (marked xfail)
- **No API endpoints exist** for `/api/v1/admin/export` or `/api/v1/admin/import`

**Related Functionality:**
- `WorkcellRuntime` has `save_state_to_file()` for runtime state backup
- `WorkcellRuntime` config includes `backup_interval` and `num_backups` for rolling backups
- This is runtime state persistence, NOT full database export

**User Value:** Confidence that users can safely backup and restore their data without corruption or loss.

---

## 2. Technical Implementation Strategy

### Current Codebase Analysis

**What EXISTS:**
- `WorkcellRuntime.save_state_to_file(fn, indent)` - Saves runtime state to JSON
- `WorkcellRuntime` backup config (`backup_interval=60`, `num_backups=3`)
- Stub test files with expected test structure

**What does NOT EXIST:**
- Admin API endpoints for export/import
- Full database dump/restore functionality
- Version migration for imports

### Decision Required

**Option A: Update tests to match existing functionality**
- Convert stub tests to test `WorkcellRuntime.save_state_to_file()`
- Test the rolling backup mechanism
- Remove xfail markers for implemented features

**Option B: Document gap and keep stubs**
- Keep xfail tests as specification for future implementation
- Add TECHNICAL_DEBT.md entry for missing database export feature
- Create follow-up backlog item

### Recommended: Option A (Test What Exists)

Update tests to verify workcell state persistence:

\`\`\`python
# tests/backend/core/test_workcell_state_persistence.py

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from praxis.backend.core.workcell import WorkcellRuntime

class TestWorkcellStatePersistence:
    """Tests for workcell runtime state backup/restore."""

    @pytest.fixture
    def workcell_runtime(self):
        """Create a WorkcellRuntime with test configuration."""
        return WorkcellRuntime(
            workcell_accession_id="test-workcell-001",
            backup_interval=60,
            num_backups=3,
        )

    def test_save_state_to_file_creates_valid_json(self, workcell_runtime, tmp_path):
        """Test that save_state_to_file creates valid JSON."""
        filepath = tmp_path / "state.json"
        workcell_runtime.save_state_to_file(str(filepath))
        
        assert filepath.exists()
        with open(filepath) as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_backup_interval_configuration(self):
        """Test backup interval is properly configured."""
        runtime = WorkcellRuntime(
            workcell_accession_id="test",
            backup_interval=120,
            num_backups=5,
        )
        assert runtime.backup_interval == 120
        assert runtime.num_backups == 5

    def test_rolling_backup_counter(self, workcell_runtime, tmp_path):
        """Test backup_num increments for rolling backups."""
        initial_num = workcell_runtime.backup_num
        # Simulate backup cycle
        workcell_runtime.backup_num = (workcell_runtime.backup_num + 1) % workcell_runtime.num_backups
        assert workcell_runtime.backup_num == (initial_num + 1) % 3


class TestDatabaseExportStubs:
    """Stub tests for future database export API.
    
    These tests document the expected API contract for full database
    export/import. Remove xfail when the feature is implemented.
    """

    pytestmark = pytest.mark.xfail(reason="Database export API not implemented")

    async def test_export_endpoint_exists(self, async_client):
        """Export endpoint should exist at /api/v1/admin/export."""
        response = await async_client.get("/api/v1/admin/export")
        assert response.status_code != 404

    async def test_import_endpoint_exists(self, async_client):
        """Import endpoint should exist at /api/v1/admin/import."""
        response = await async_client.post("/api/v1/admin/import", json={})
        assert response.status_code != 404
\`\`\`

---

## 3. Context & References

**Files to Modify:**

| Path | Description |
|:-----|:------------|
| `tests/backend/api/test_database_export.py` | Update stub tests, clarify scope |
| `tests/integration/test_browser_export.py` | Update or keep as specification |

**Files to Create:**

| Path | Description |
|:-----|:------------|
| `tests/backend/core/test_workcell_state_persistence.py` | **NEW** - Test actual state save functionality |

**Reference Files:**

| Path | Description |
|:-----|:------------|
| `praxis/backend/core/workcell.py` | `WorkcellRuntime` with `save_state_to_file()` |
| `praxis/backend/services/state.py` | State service with JSON serialization |

---

## 4. Constraints & Conventions

- **Commands**: Use `uv run pytest` for testing
- **Backend Path**: `praxis/backend`
- **Test Path**: `tests/backend/core/` for state tests
- **xfail**: Keep for unimplemented features as living documentation
- **Async**: Use `pytest-asyncio` for API tests

---

## 5. Verification Plan

**Definition of Done:**

1. State persistence tests pass:

   \`\`\`bash
   uv run pytest tests/backend/core/test_workcell_state_persistence.py -v
   \`\`\`

2. Existing stub tests remain valid (still xfail):

   \`\`\`bash
   uv run pytest tests/backend/api/test_database_export.py -v
   \`\`\`

3. No regressions:

   \`\`\`bash
   uv run pytest tests/backend/ -v --ignore=tests/backend/integration
   \`\`\`

---

## On Completion

- [ ] Document database export gap in TECHNICAL_DEBT.md if not creating full implementation
- [ ] Commit changes with message: `test: add workcell state persistence tests, clarify export stubs`
- [ ] Update backlog item status in [testing.md](../../backlog/testing.md)
- [ ] Mark this prompt complete in batch README, update DEVELOPMENT_MATRIX.md if applicable, and set the status in this prompt document to 🟢 Completed

---

## Notes for Implementer

The original prompt assumed database export/import endpoints exist. Investigation revealed:
- Only runtime state persistence exists (`WorkcellRuntime.save_state_to_file()`)
- No admin API endpoints for full database export
- Stub test files already exist with xfail markers

Focus on testing what exists, keep stubs as specification for future work.

---

## References

- `.agents/README.md` - Environment overview
- `tests/TESTING_PATTERNS.md` - Project testing conventions
- `.agents/codestyles/python.md` - Python conventions
