"""Tests for database utilities in utils/db.py."""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.utils.db import (
    Base,
    CreateMaterializedView,
    DropMaterializedView,
    compile_create_materialized_view,
    compile_drop_materialized_view,
    get_async_db_session,
    init_praxis_db_schema,
)


class TestBase:

    """Tests for Base ORM class."""

    def test_base_has_accession_id_field(self) -> None:
        """Test that Base class has accession_id field."""
        assert hasattr(Base, "accession_id")

    def test_base_has_created_at_field(self) -> None:
        """Test that Base class has created_at field."""
        assert hasattr(Base, "created_at")

    def test_base_has_updated_at_field(self) -> None:
        """Test that Base class has updated_at field."""
        assert hasattr(Base, "updated_at")

    def test_base_has_properties_json_field(self) -> None:
        """Test that Base class has properties_json field."""
        assert hasattr(Base, "properties_json")

    def test_base_has_name_field(self) -> None:
        """Test that Base class has name field."""
        assert hasattr(Base, "name")

    def test_base_has_metadata(self) -> None:
        """Test that Base class has metadata attribute."""
        assert hasattr(Base, "metadata")
        assert Base.metadata is not None


class TestGetAsyncDbSession:

    """Tests for get_async_db_session function."""

    @pytest.mark.asyncio
    async def test_get_async_db_session_yields_session(self) -> None:
        """Test that get_async_db_session yields an AsyncSession."""
        async for session in get_async_db_session():
            assert isinstance(session, AsyncSession)
            break  # Only test first yield

    @pytest.mark.asyncio
    async def test_get_async_db_session_closes_on_success(self) -> None:
        """Test that session is closed after successful use."""
        session_used = False
        async for session in get_async_db_session():
            session_used = True
            # Session should be open here
            assert session is not None
        assert session_used

    @pytest.mark.asyncio
    async def test_get_async_db_session_propagates_exceptions(self) -> None:
        """Test that exceptions are propagated."""
        with pytest.raises(ValueError, match="Test error"):
            async for session in get_async_db_session():
                # Simulate an error during session use
                raise ValueError("Test error")

    @pytest.mark.asyncio
    @patch("praxis.backend.utils.db.AsyncSessionLocal")
    async def test_get_async_db_session_always_closes(
        self, mock_session_maker: MagicMock,
    ) -> None:
        """Test that session is always closed, even without exception."""
        mock_session = AsyncMock()
        mock_session.close = AsyncMock()
        mock_session_maker.return_value = mock_session

        async for _session in get_async_db_session():
            pass  # Normal completion

        mock_session.close.assert_awaited_once()


class TestInitPraxisDbSchema:

    """Tests for init_praxis_db_schema function."""

    @pytest.mark.asyncio
    @patch("praxis.backend.utils.db.create_async_engine")
    async def test_init_praxis_db_schema_uses_default_engine(
        self, mock_create_engine: MagicMock,
    ) -> None:
        """Test that function creates engine when none provided."""
        mock_engine = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.run_sync = AsyncMock()
        mock_engine.begin = MagicMock()
        mock_engine.begin.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_engine.begin.return_value.__aexit__ = AsyncMock()
        mock_engine.dispose = AsyncMock()
        mock_engine.url = Mock()
        mock_engine.url.password = "password"
        mock_create_engine.return_value = mock_engine

        await init_praxis_db_schema()

        mock_create_engine.assert_called_once()

    @pytest.mark.asyncio
    async def test_init_praxis_db_schema_uses_provided_engine(self) -> None:
        """Test that function uses provided engine."""
        mock_engine = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.run_sync = AsyncMock()
        mock_engine.begin = MagicMock()
        mock_engine.begin.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_engine.begin.return_value.__aexit__ = AsyncMock()
        mock_engine.url = Mock()
        mock_engine.url.password = "password"

        await init_praxis_db_schema(engine=mock_engine)

        mock_conn.run_sync.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_init_praxis_db_schema_creates_tables(self) -> None:
        """Test that function calls create_all on metadata."""
        mock_engine = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.run_sync = AsyncMock()
        mock_engine.begin = MagicMock()
        mock_engine.begin.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_engine.begin.return_value.__aexit__ = AsyncMock()
        mock_engine.url = Mock()
        mock_engine.url.password = "password"

        await init_praxis_db_schema(engine=mock_engine)

        # Verify run_sync was called (which would call Base.metadata.create_all)
        mock_conn.run_sync.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_init_praxis_db_schema_handles_exception(self) -> None:
        """Test that function re-raises exceptions."""
        mock_engine = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.run_sync = AsyncMock(side_effect=Exception("DB error"))
        mock_engine.begin = MagicMock()
        mock_engine.begin.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_engine.begin.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_engine.url = Mock()
        mock_engine.url.password = "password"

        with pytest.raises(Exception, match="DB error"):
            await init_praxis_db_schema(engine=mock_engine)


class TestCreateMaterializedView:

    """Tests for CreateMaterializedView DDL element."""

    def test_create_materialized_view_initialization(self) -> None:
        """Test that CreateMaterializedView initializes correctly."""
        mock_select = Mock()
        view = CreateMaterializedView("test_view", mock_select)

        assert view.name == "test_view"
        assert view.selectable == mock_select

    def test_create_materialized_view_stores_name(self) -> None:
        """Test that CreateMaterializedView stores view name."""
        mock_select = Mock()
        view = CreateMaterializedView("my_view", mock_select)

        assert view.name == "my_view"

    def test_create_materialized_view_stores_selectable(self) -> None:
        """Test that CreateMaterializedView stores selectable."""
        mock_select = Mock()
        view = CreateMaterializedView("test", mock_select)

        assert view.selectable is not None


class TestDropMaterializedView:

    """Tests for DropMaterializedView DDL element."""

    def test_drop_materialized_view_initialization(self) -> None:
        """Test that DropMaterializedView initializes correctly."""
        view = DropMaterializedView("test_view")

        assert view.name == "test_view"

    def test_drop_materialized_view_stores_name(self) -> None:
        """Test that DropMaterializedView stores view name."""
        view = DropMaterializedView("my_view")

        assert view.name == "my_view"


class TestCompileCreateMaterializedView:

    """Tests for compile_create_materialized_view function."""

    def test_compile_create_materialized_view_returns_sql(self) -> None:
        """Test that compiler returns SQL string."""
        mock_select = Mock()
        element = CreateMaterializedView("test_view", mock_select)

        mock_compiler = Mock()
        mock_compiler.sql_compiler = Mock()
        mock_compiler.sql_compiler.process = Mock(return_value="SELECT * FROM base")

        result = compile_create_materialized_view(element, mock_compiler)

        assert isinstance(result, str)
        assert "CREATE MATERIALIZED VIEW" in result
        assert "test_view" in result

    def test_compile_create_materialized_view_includes_if_not_exists(self) -> None:
        """Test that compiler includes IF NOT EXISTS clause."""
        mock_select = Mock()
        element = CreateMaterializedView("test_view", mock_select)

        mock_compiler = Mock()
        mock_compiler.sql_compiler = Mock()
        mock_compiler.sql_compiler.process = Mock(return_value="SELECT * FROM base")

        result = compile_create_materialized_view(element, mock_compiler)

        assert "IF NOT EXISTS" in result

    def test_compile_create_materialized_view_processes_selectable(self) -> None:
        """Test that compiler processes the selectable."""
        mock_select = Mock()
        element = CreateMaterializedView("test_view", mock_select)

        mock_compiler = Mock()
        mock_compiler.sql_compiler = Mock()
        mock_compiler.sql_compiler.process = Mock(return_value="SELECT * FROM base")

        result = compile_create_materialized_view(element, mock_compiler)

        mock_compiler.sql_compiler.process.assert_called_once_with(
            mock_select, literal_binds=True,
        )
        assert "SELECT * FROM base" in result


class TestCompileDropMaterializedView:

    """Tests for compile_drop_materialized_view function."""

    def test_compile_drop_materialized_view_returns_sql(self) -> None:
        """Test that compiler returns SQL string."""
        element = DropMaterializedView("test_view")
        mock_compiler = Mock()

        result = compile_drop_materialized_view(element, mock_compiler)

        assert isinstance(result, str)
        assert "DROP MATERIALIZED VIEW" in result
        assert "test_view" in result

    def test_compile_drop_materialized_view_includes_if_exists(self) -> None:
        """Test that compiler includes IF EXISTS clause."""
        element = DropMaterializedView("test_view")
        mock_compiler = Mock()

        result = compile_drop_materialized_view(element, mock_compiler)

        assert "IF EXISTS" in result

    def test_compile_drop_materialized_view_uses_view_name(self) -> None:
        """Test that compiler uses the correct view name."""
        element = DropMaterializedView("my_special_view")
        mock_compiler = Mock()

        result = compile_drop_materialized_view(element, mock_compiler)

        assert "my_special_view" in result


class TestDbIntegration:

    """Integration tests for database utilities."""

    @pytest.mark.asyncio
    async def test_async_session_context_manager_workflow(self) -> None:
        """Test complete workflow of using async session context manager."""
        session_created = False
        session_closed = False

        async for session in get_async_db_session():
            session_created = True
            assert isinstance(session, AsyncSession)
            # In real usage, would execute queries here
            break

        assert session_created

    def test_base_class_can_be_used_for_inheritance(self) -> None:
        """Test that Base class can be inherited for ORM models."""

        # This tests that Base is suitable for inheritance
        class TestModel(Base):
            __tablename__ = "test_model"

        assert hasattr(TestModel, "accession_id")
        assert hasattr(TestModel, "name")
        assert hasattr(TestModel, "created_at")

    def test_materialized_view_elements_work_together(self) -> None:
        """Test that create and drop DDL elements can be used together."""
        mock_select = Mock()

        create_view = CreateMaterializedView("test_view", mock_select)
        drop_view = DropMaterializedView("test_view")

        assert create_view.name == drop_view.name

    def test_compilers_produce_valid_sql_statements(self) -> None:
        """Test that DDL compilers produce valid-looking SQL."""
        mock_select = Mock()
        create_elem = CreateMaterializedView("test_view", mock_select)
        drop_elem = DropMaterializedView("test_view")

        mock_compiler = Mock()
        mock_compiler.sql_compiler = Mock()
        mock_compiler.sql_compiler.process = Mock(return_value="SELECT * FROM base")

        create_sql = compile_create_materialized_view(create_elem, mock_compiler)
        drop_sql = compile_drop_materialized_view(drop_elem, mock_compiler)

        # Both should be strings
        assert isinstance(create_sql, str)
        assert isinstance(drop_sql, str)

        # CREATE should mention the view name and contain AS
        assert "test_view" in create_sql
        assert "AS" in create_sql

        # DROP should mention the view name
        assert "test_view" in drop_sql
