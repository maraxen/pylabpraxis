"""Tests for core/protocol_code_manager.py."""

import os
import subprocess
import sys
from collections.abc import Callable
from unittest.mock import AsyncMock, Mock, patch

import pytest

from praxis.backend.core.protocol_code_manager import (
    ProtocolCodeManager,
    temporary_sys_path,
)
from praxis.backend.models import (
    FunctionProtocolDefinitionCreate,
)
from praxis.backend.utils.uuid import uuid7


class TestTemporarySysPath:
    """Tests for temporary_sys_path context manager."""

    def test_temporary_sys_path_adds_path(self) -> None:
        """Test that path is added to sys.path."""
        test_path = "/tmp/test_path_unique_12345"
        original_sys_path = list(sys.path)

        with temporary_sys_path(test_path):
            assert test_path in sys.path
            assert sys.path[0] == test_path

        assert sys.path == original_sys_path

    def test_temporary_sys_path_removes_path_on_exit(self) -> None:
        """Test that path is removed from sys.path on exit."""
        test_path = "/tmp/test_path_unique_67890"
        original_sys_path = list(sys.path)

        with temporary_sys_path(test_path):
            pass

        assert test_path not in sys.path
        assert sys.path == original_sys_path

    def test_temporary_sys_path_with_none(self) -> None:
        """Test that None path does nothing."""
        original_sys_path = list(sys.path)

        with temporary_sys_path(None):
            assert sys.path == original_sys_path

        assert sys.path == original_sys_path

    def test_temporary_sys_path_with_existing_path(self) -> None:
        """Test that existing path in sys.path is handled."""
        test_path = sys.path[0]  # Use existing path
        original_sys_path = list(sys.path)

        with temporary_sys_path(test_path):
            # Path already exists, should not be added again
            assert sys.path == original_sys_path

        assert sys.path == original_sys_path

    def test_temporary_sys_path_restores_on_exception(self) -> None:
        """Test that sys.path is restored even if exception occurs."""
        test_path = "/tmp/test_path_exception_99999"
        original_sys_path = list(sys.path)

        with pytest.raises(ValueError):
            with temporary_sys_path(test_path):
                assert test_path in sys.path
                raise ValueError("Test exception")

        assert test_path not in sys.path
        assert sys.path == original_sys_path


class TestProtocolCodeManagerInit:
    """Tests for ProtocolCodeManager initialization."""

    def test_protocol_code_manager_initialization(self) -> None:
        """Test that ProtocolCodeManager can be initialized."""
        manager = ProtocolCodeManager()
        assert isinstance(manager, ProtocolCodeManager)


class TestRunGitCommand:
    """Tests for _run_git_command method."""

    @pytest.mark.asyncio
    async def test_run_git_command_success(self) -> None:
        """Test successful Git command execution."""
        manager = ProtocolCodeManager()

        mock_result = Mock()
        mock_result.stdout = "success output"
        mock_result.stderr = ""

        with patch("asyncio.to_thread", return_value=mock_result):
            result = await manager._run_git_command(
                ["git", "status"],
                cwd="/tmp",
            )

        assert result == "success output"

    @pytest.mark.asyncio
    async def test_run_git_command_with_stderr(self) -> None:
        """Test Git command that produces stderr."""
        manager = ProtocolCodeManager()

        mock_result = Mock()
        mock_result.stdout = "output"
        mock_result.stderr = "warning message"

        with patch("asyncio.to_thread", return_value=mock_result):
            result = await manager._run_git_command(
                ["git", "fetch"],
                cwd="/tmp",
            )

        assert result == "output"

    @pytest.mark.asyncio
    async def test_run_git_command_suppress_output(self) -> None:
        """Test Git command with output suppression."""
        manager = ProtocolCodeManager()

        mock_result = Mock()
        mock_result.stdout = "suppressed output"
        mock_result.stderr = ""

        with patch("asyncio.to_thread", return_value=mock_result):
            result = await manager._run_git_command(
                ["git", "rev-parse", "HEAD"],
                cwd="/tmp",
                suppress_output=True,
            )

        assert result == "suppressed output"

    @pytest.mark.asyncio
    async def test_run_git_command_timeout(self) -> None:
        """Test Git command timeout handling."""
        manager = ProtocolCodeManager()

        timeout_error = subprocess.TimeoutExpired(
            cmd=["git", "fetch"],
            timeout=5,
        )
        timeout_error.stderr = b"timeout stderr"
        timeout_error.stdout = b"timeout stdout"

        with patch("asyncio.to_thread", side_effect=timeout_error):
            with pytest.raises(RuntimeError, match="timed out"):
                await manager._run_git_command(
                    ["git", "fetch"],
                    cwd="/tmp",
                    timeout=5,
                )

    @pytest.mark.asyncio
    async def test_run_git_command_called_process_error(self) -> None:
        """Test Git command CalledProcessError handling."""
        manager = ProtocolCodeManager()

        error = subprocess.CalledProcessError(
            returncode=128,
            cmd=["git", "checkout", "invalid"],
        )
        error.stderr = "fatal: invalid reference"
        error.stdout = ""

        with patch("asyncio.to_thread", side_effect=error):
            with pytest.raises(RuntimeError, match="failed with exit code"):
                await manager._run_git_command(
                    ["git", "checkout", "invalid"],
                    cwd="/tmp",
                )


class TestEnsureGitRepoAndFetch:
    """Tests for _ensure_git_repo_and_fetch method."""

    @pytest.mark.asyncio
    async def test_ensure_git_repo_existing_repo(self) -> None:
        """Test with existing Git repository."""
        manager = ProtocolCodeManager()

        # Mock Git commands
        async def mock_run_git_command(cmd, cwd, suppress_output=False):
            if cmd == ["git", "rev-parse", "--is-inside-work-tree"]:
                return "true"
            if cmd == ["git", "config", "--get", "remote.origin.url"]:
                return "https://github.com/test/repo.git"
            if cmd == ["git", "fetch", "origin", "--prune"]:
                return ""
            return ""

        manager._run_git_command = mock_run_git_command

        with patch("os.path.exists", return_value=True):
            await manager._ensure_git_repo_and_fetch(
                "https://github.com/test/repo.git",
                "/tmp/test_repo",
                "test_repo",
            )

    @pytest.mark.asyncio
    async def test_ensure_git_repo_mismatched_url(self) -> None:
        """Test with existing repo but mismatched URL."""
        manager = ProtocolCodeManager()

        async def mock_run_git_command(cmd, cwd, suppress_output=False):
            if cmd == ["git", "rev-parse", "--is-inside-work-tree"]:
                return "true"
            if cmd == ["git", "config", "--get", "remote.origin.url"]:
                return "https://github.com/wrong/repo.git"
            return ""

        manager._run_git_command = mock_run_git_command

        with patch("os.path.exists", return_value=True):
            with pytest.raises(ValueError, match="does not match"):
                await manager._ensure_git_repo_and_fetch(
                    "https://github.com/test/repo.git",
                    "/tmp/test_repo",
                    "test_repo",
                )

    @pytest.mark.asyncio
    async def test_ensure_git_repo_clone_new_repo(self) -> None:
        """Test cloning a new repository."""
        manager = ProtocolCodeManager()

        git_commands_called = []

        async def mock_run_git_command(cmd, cwd, suppress_output=False):
            git_commands_called.append(cmd)
            return ""

        manager._run_git_command = mock_run_git_command

        with patch("os.path.exists", return_value=False):
            with patch("os.makedirs"):
                await manager._ensure_git_repo_and_fetch(
                    "https://github.com/test/repo.git",
                    "/tmp/new_repo",
                    "new_repo",
                )

        # Should call git clone
        assert any("clone" in cmd for cmd in git_commands_called)

    @pytest.mark.asyncio
    async def test_ensure_git_repo_non_empty_non_git_dir(self) -> None:
        """Test with non-empty, non-Git directory."""
        manager = ProtocolCodeManager()

        async def mock_run_git_command(cmd, cwd, suppress_output=False):
            if cmd == ["git", "rev-parse", "--is-inside-work-tree"]:
                raise RuntimeError("Not a git repo")
            return ""

        manager._run_git_command = mock_run_git_command

        with patch("os.path.exists", return_value=True):
            with patch("os.listdir", return_value=["some_file.txt"]):
                with pytest.raises(ValueError, match="not empty"):
                    await manager._ensure_git_repo_and_fetch(
                        "https://github.com/test/repo.git",
                        "/tmp/non_empty",
                        "test_repo",
                    )


class TestCheckoutSpecificCommit:
    """Tests for _checkout_specific_commit method."""

    @pytest.mark.asyncio
    async def test_checkout_specific_commit_success(self) -> None:
        """Test successful commit checkout."""
        manager = ProtocolCodeManager()

        commit_hash = "abc123def456"

        async def mock_run_git_command(cmd, cwd, suppress_output=False):
            if cmd == ["git", "checkout", commit_hash]:
                return ""
            if cmd == ["git", "rev-parse", "HEAD"]:
                return commit_hash
            if cmd == ["git", "rev-parse", f"{commit_hash}^{{commit}}"]:
                return commit_hash
            return ""

        manager._run_git_command = mock_run_git_command

        await manager._checkout_specific_commit(
            "/tmp/repo",
            commit_hash,
            "test_repo",
        )

    @pytest.mark.asyncio
    async def test_checkout_specific_commit_verification_failed(self) -> None:
        """Test commit checkout with verification failure."""
        manager = ProtocolCodeManager()

        commit_hash = "abc123def456"

        async def mock_run_git_command(cmd, cwd, suppress_output=False):
            if cmd == ["git", "checkout", commit_hash]:
                return ""
            if cmd == ["git", "rev-parse", "HEAD"]:
                return "different_commit"
            if cmd == ["git", "rev-parse", f"{commit_hash}^{{commit}}"]:
                return commit_hash
            return ""

        manager._run_git_command = mock_run_git_command

        with pytest.raises(RuntimeError, match="Failed to checkout commit"):
            await manager._checkout_specific_commit(
                "/tmp/repo",
                commit_hash,
                "test_repo",
            )


class TestLoadProtocolFunction:
    """Tests for _load_protocol_function method."""

    def test_load_protocol_function_success(self) -> None:
        """Test successful protocol function loading."""
        manager = ProtocolCodeManager()

        # Create mock module and function
        mock_pydantic_def = FunctionProtocolDefinitionCreate(
            accession_id=uuid7(),
            name="test_protocol",
            fqn="test_module.test_function",
            version="1.0",
            source_file_path="/test/path/test_module.py",
            module_name="test_module",
            function_name="test_function",
            parameters=[],
            assets=[],
        )

        mock_function = Mock()
        mock_function._protocol_definition = mock_pydantic_def

        mock_module = Mock()
        mock_module.test_function = mock_function

        with patch("importlib.import_module", return_value=mock_module):
            func, pydantic_def = manager._load_protocol_function(
                "test_module",
                "test_function",
            )

        assert func == mock_function
        assert pydantic_def == mock_pydantic_def

    def test_load_protocol_function_not_found(self) -> None:
        """Test loading non-existent function."""
        manager = ProtocolCodeManager()

        mock_module = Mock()
        del mock_module.test_function  # Ensure function doesn't exist

        with patch("importlib.import_module", return_value=mock_module):
            with pytest.raises(AttributeError, match="Function 'test_function' not found"):
                manager._load_protocol_function(
                    "test_module",
                    "test_function",
                )

    def test_load_protocol_function_missing_definition(self) -> None:
        """Test loading function without protocol definition."""
        manager = ProtocolCodeManager()

        mock_function = Mock()
        # No _protocol_definition attribute

        mock_module = Mock()
        mock_module.test_function = mock_function

        with patch("importlib.import_module", return_value=mock_module):
            with pytest.raises(AttributeError, match="not a valid @protocol_function"):
                manager._load_protocol_function(
                    "test_module",
                    "test_function",
                )

    def test_load_protocol_function_with_module_path(self) -> None:
        """Test loading function with custom module path."""
        manager = ProtocolCodeManager()

        mock_pydantic_def = FunctionProtocolDefinitionCreate(
            accession_id=uuid7(),
            name="test_protocol",
            fqn="test_module.test_function",
            version="1.0",
            source_file_path="/test/path/test_module.py",
            module_name="test_module",
            function_name="test_function",
            parameters=[],
            assets=[],
        )

        mock_function = Mock()
        mock_function._protocol_definition = mock_pydantic_def

        mock_module = Mock()
        mock_module.test_function = mock_function

        with patch("importlib.import_module", return_value=mock_module):
            func, pydantic_def = manager._load_protocol_function(
                "test_module",
                "test_function",
                module_path="/custom/path",
            )

        assert func == mock_function
        assert isinstance(pydantic_def, FunctionProtocolDefinitionCreate)

    def test_load_protocol_function_reload_existing_module(self) -> None:
        """Test reloading existing module."""
        manager = ProtocolCodeManager()

        mock_pydantic_def = FunctionProtocolDefinitionCreate(
            accession_id=uuid7(),
            name="test_protocol",
            fqn="test_module.test_function",
            version="1.0",
            source_file_path="/test/path/test_module.py",
            module_name="test_module",
            function_name="test_function",
            parameters=[],
            assets=[],
        )

        mock_function = Mock()
        mock_function._protocol_definition = mock_pydantic_def

        mock_module = Mock()
        mock_module.test_function = mock_function

        # Simulate module already in sys.modules
        with patch.dict(sys.modules, {"test_module": mock_module}):
            with patch("importlib.reload", return_value=mock_module) as mock_reload:
                func, pydantic_def = manager._load_protocol_function(
                    "test_module",
                    "test_function",
                )

        mock_reload.assert_called_once()
        assert func == mock_function


class TestLoadCallableFromFqn:
    """Tests for _load_callable_from_fqn method."""

    def test_load_callable_from_fqn_success(self) -> None:
        """Test successful callable loading from FQN."""
        manager = ProtocolCodeManager()

        mock_callable = Mock()
        mock_module = Mock()
        mock_module.MyCallable = mock_callable

        with patch("importlib.import_module", return_value=mock_module):
            result = manager._load_callable_from_fqn("test.module.MyCallable")

        assert result == mock_callable

    def test_load_callable_from_fqn_invalid_fqn(self) -> None:
        """Test with invalid FQN."""
        manager = ProtocolCodeManager()

        with pytest.raises(ValueError, match="Invalid fully qualified name"):
            manager._load_callable_from_fqn("invalid_fqn")

    def test_load_callable_from_fqn_empty_string(self) -> None:
        """Test with empty FQN."""
        manager = ProtocolCodeManager()

        with pytest.raises(ValueError, match="Invalid fully qualified name"):
            manager._load_callable_from_fqn("")

    def test_load_callable_from_fqn_callable_not_found(self) -> None:
        """Test with callable not found in module."""
        manager = ProtocolCodeManager()

        mock_module = Mock()
        del mock_module.MyCallable  # Ensure callable doesn't exist

        with patch("importlib.import_module", return_value=mock_module):
            with pytest.raises(AttributeError):
                manager._load_callable_from_fqn("test.module.MyCallable")


class TestPrepareProtocolCode:
    """Tests for prepare_protocol_code method."""

    @pytest.mark.asyncio
    async def test_prepare_protocol_code_with_git_source(self) -> None:
        """Test prepare_protocol_code with Git repository source."""
        manager = ProtocolCodeManager()

        # Create shared accession_id
        shared_accession_id = uuid7()

        # Create mock protocol definition ORM
        mock_repo = Mock()
        mock_repo.name = "test_repo"
        mock_repo.git_url = "https://github.com/test/repo.git"
        mock_repo.local_checkout_path = "/tmp/test_repo"

        mock_protocol_def_orm = Mock()
        mock_protocol_def_orm.name = "test_protocol"
        mock_protocol_def_orm.version = "1.0"
        mock_protocol_def_orm.accession_id = shared_accession_id
        mock_protocol_def_orm.module_name = "test_module"
        mock_protocol_def_orm.function_name = "test_function"
        mock_protocol_def_orm.commit_hash = "abc123"
        mock_protocol_def_orm.source_repository_accession_id = uuid7()
        mock_protocol_def_orm.source_repository = mock_repo
        mock_protocol_def_orm.file_system_source_accession_id = None

        # Mock Git operations
        manager._ensure_git_repo_and_fetch = AsyncMock()
        manager._checkout_specific_commit = AsyncMock()

        # Mock function loading with same accession_id
        mock_pydantic_def = FunctionProtocolDefinitionCreate(
            accession_id=shared_accession_id,
            name="test_protocol",
            fqn="test_module.test_function",
            version="1.0",
            source_file_path="/test/path/test_module.py",
            module_name="test_module",
            function_name="test_function",
            parameters=[],
            assets=[],
        )

        mock_function = Mock()

        def mock_load_protocol_function(module_name, function_name, module_path=None):
            return mock_function, mock_pydantic_def

        manager._load_protocol_function = mock_load_protocol_function

        func, pydantic_def = await manager.prepare_protocol_code(mock_protocol_def_orm)

        assert func == mock_function
        assert isinstance(pydantic_def, FunctionProtocolDefinitionCreate)
        manager._ensure_git_repo_and_fetch.assert_called_once()
        manager._checkout_specific_commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_prepare_protocol_code_with_filesystem_source(self) -> None:
        """Test prepare_protocol_code with file system source."""
        manager = ProtocolCodeManager()

        # Create shared accession_id
        shared_accession_id = uuid7()

        # Create mock file system source
        mock_fs_source = Mock()
        mock_fs_source.name = "test_fs_source"
        mock_fs_source.base_path = "/tmp/test_path"

        mock_protocol_def_orm = Mock()
        mock_protocol_def_orm.name = "test_protocol"
        mock_protocol_def_orm.version = "1.0"
        mock_protocol_def_orm.accession_id = shared_accession_id
        mock_protocol_def_orm.module_name = "test_module"
        mock_protocol_def_orm.function_name = "test_function"
        mock_protocol_def_orm.source_repository_accession_id = None
        mock_protocol_def_orm.file_system_source_accession_id = uuid7()
        mock_protocol_def_orm.file_system_source = mock_fs_source

        # Mock function loading with same accession_id
        mock_pydantic_def = FunctionProtocolDefinitionCreate(
            accession_id=shared_accession_id,
            name="test_protocol",
            fqn="test_module.test_function",
            version="1.0",
            source_file_path="/test/path/test_module.py",
            module_name="test_module",
            function_name="test_function",
            parameters=[],
            assets=[],
        )

        mock_function = Mock()

        def mock_load_protocol_function(module_name, function_name, module_path=None):
            return mock_function, mock_pydantic_def

        manager._load_protocol_function = mock_load_protocol_function

        with patch("os.path.isdir", return_value=True):
            func, pydantic_def = await manager.prepare_protocol_code(mock_protocol_def_orm)

        assert func == mock_function
        assert isinstance(pydantic_def, FunctionProtocolDefinitionCreate)

    @pytest.mark.asyncio
    async def test_prepare_protocol_code_invalid_git_source(self) -> None:
        """Test prepare_protocol_code with incomplete Git source."""
        manager = ProtocolCodeManager()

        mock_repo = Mock()
        mock_repo.git_url = None  # Missing git_url
        mock_repo.local_checkout_path = None

        mock_protocol_def_orm = Mock()
        mock_protocol_def_orm.name = "test_protocol"
        mock_protocol_def_orm.version = "1.0"
        mock_protocol_def_orm.source_repository_accession_id = uuid7()
        mock_protocol_def_orm.source_repository = mock_repo
        mock_protocol_def_orm.commit_hash = None
        mock_protocol_def_orm.file_system_source_accession_id = None

        with pytest.raises(ValueError, match="Incomplete Git source info"):
            await manager.prepare_protocol_code(mock_protocol_def_orm)

    @pytest.mark.asyncio
    async def test_prepare_protocol_code_invalid_fs_source(self) -> None:
        """Test prepare_protocol_code with invalid file system source."""
        manager = ProtocolCodeManager()

        mock_fs_source = Mock()
        mock_fs_source.base_path = "/invalid/path"

        mock_protocol_def_orm = Mock()
        mock_protocol_def_orm.name = "test_protocol"
        mock_protocol_def_orm.version = "1.0"
        mock_protocol_def_orm.source_repository_accession_id = None
        mock_protocol_def_orm.file_system_source_accession_id = uuid7()
        mock_protocol_def_orm.file_system_source = mock_fs_source
        mock_protocol_def_orm.module_name = "test_module"
        mock_protocol_def_orm.function_name = "test_function"

        with patch("os.path.isdir", return_value=False):
            with pytest.raises(ValueError, match="Invalid base path"):
                await manager.prepare_protocol_code(mock_protocol_def_orm)

    @pytest.mark.asyncio
    async def test_prepare_protocol_code_with_matching_accession_id(self) -> None:
        """Test that prepare_protocol_code works when accession_ids match."""
        manager = ProtocolCodeManager()

        shared_accession_id = uuid7()

        mock_protocol_def_orm = Mock()
        mock_protocol_def_orm.name = "test_protocol"
        mock_protocol_def_orm.version = "1.0"
        mock_protocol_def_orm.accession_id = shared_accession_id
        mock_protocol_def_orm.module_name = "test_module"
        mock_protocol_def_orm.function_name = "test_function"
        mock_protocol_def_orm.source_repository_accession_id = None
        mock_protocol_def_orm.file_system_source_accession_id = None

        # Mock function loading with same accession_id
        mock_pydantic_def = FunctionProtocolDefinitionCreate(
            accession_id=shared_accession_id,
            name="test_protocol",
            fqn="test_module.test_function",
            version="1.0",
            source_file_path="/test/path/test_module.py",
            module_name="test_module",
            function_name="test_function",
            parameters=[],
            assets=[],
        )

        mock_function = Mock()

        def mock_load_protocol_function(module_name, function_name, module_path=None):
            return mock_function, mock_pydantic_def

        manager._load_protocol_function = mock_load_protocol_function

        func, pydantic_def = await manager.prepare_protocol_code(mock_protocol_def_orm)

        # Should return with same accession_id
        assert pydantic_def.accession_id == shared_accession_id
        assert func == mock_function


class TestProtocolCodeManagerIntegration:
    """Integration tests for ProtocolCodeManager."""

    def test_module_has_logger(self) -> None:
        """Test that module defines logger."""
        from praxis.backend.core import protocol_code_manager

        assert hasattr(protocol_code_manager, "logger")

    def test_temporary_sys_path_is_exported(self) -> None:
        """Test that temporary_sys_path is exported."""
        from praxis.backend.core import protocol_code_manager

        assert hasattr(protocol_code_manager, "temporary_sys_path")

    def test_protocol_code_manager_is_exported(self) -> None:
        """Test that ProtocolCodeManager is exported."""
        from praxis.backend.core import protocol_code_manager

        assert hasattr(protocol_code_manager, "ProtocolCodeManager")
