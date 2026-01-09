import pytest
from httpx import AsyncClient

# These tests are expected to fail until the feature is implemented
pytestmark = pytest.mark.xfail(reason="Database export/import not implemented yet")


class TestDatabaseExport:
    """Tests for database export functionality."""

    async def test_export_endpoint_returns_valid_format(self, async_client: AsyncClient):
        """Test that export endpoint returns valid JSON/SQL dump."""
        # Using async_client as per project pattern (TestClient is often sync)
        response = await async_client.get("/api/v1/admin/export")
        assert response.status_code == 200
        # Verify response is valid JSON
        data = response.json()
        assert isinstance(data, dict)
        assert "version" in data
        assert "timestamp" in data

    async def test_export_includes_all_tables(
        self, async_client: AsyncClient, db_with_data
    ):
        """Test that export includes machines, resources, protocol_definitions, etc."""
        response = await async_client.get("/api/v1/admin/export")
        data = response.json()
        assert "machines" in data
        assert "resources" in data
        assert "protocol_definitions" in data
        assert isinstance(data["machines"], list)
        assert isinstance(data["resources"], list)

    async def test_export_excludes_sensitive_data(self, async_client: AsyncClient):
        """Test that export doesn't include credentials or tokens."""
        response = await async_client.get("/api/v1/admin/export")
        data = response.text
        assert "password" not in data.lower()
        assert "secret" not in data.lower()
        assert "token" not in data.lower()


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
            "protocol_definitions": [],
        }

    async def test_import_valid_data_succeeds(
        self, async_client: AsyncClient, valid_export_data
    ):
        """Test successful import of valid data."""
        response = await async_client.post(
            "/api/v1/admin/import", json=valid_export_data
        )
        assert response.status_code in [200, 201]

    async def test_import_invalid_format_rejected(self, async_client: AsyncClient):
        """Test that malformed data is rejected."""
        response = await async_client.post(
            "/api/v1/admin/import", json={"invalid": "data"}
        )
        assert response.status_code == 400

    async def test_import_preserves_data_integrity(
        self, async_client: AsyncClient, valid_export_data
    ):
        """Test that imported data matches original."""
        # Import data
        import_response = await async_client.post(
            "/api/v1/admin/import", json=valid_export_data
        )
        assert import_response.status_code in [200, 201]

        # Export it back
        export_response = await async_client.get("/api/v1/admin/export")
        exported = export_response.json()

        # Verify data integrity
        assert exported["machines"] == valid_export_data["machines"]


class TestVersionCompatibility:
    """Tests for cross-version import compatibility."""

    async def test_import_older_version_with_migration(self, async_client: AsyncClient):
        """Test importing data from older version triggers migration."""
        old_format_data = {
            "version": "0.9",  # Older version
            "machines": [],
        }
        response = await async_client.post(
            "/api/v1/admin/import", json=old_format_data
        )
        # Should either succeed with migration or fail gracefully with a specific error
        assert response.status_code in [200, 201, 400]
        if response.status_code == 400:
            assert "version" in response.json().get("detail", "").lower()

    async def test_import_newer_version_rejected(self, async_client: AsyncClient):
        """Test that future version data is rejected."""
        future_data = {
            "version": "99.0",
            "machines": [],
        }
        response = await async_client.post(
            "/api/v1/admin/import", json=future_data
        )
        assert response.status_code == 400
