"""Unit tests for ProtocolCodeManager."""

import subprocess
import sys
import types
import uuid
from typing import NoReturn
from unittest import mock

import pytest

from praxis.backend.core.protocol_code_manager import (
  ProtocolCodeManager,
  temporary_sys_path,
)
from praxis.backend.models import FunctionProtocolDefinitionCreate


def make_protocol_def_orm(
  name: str = "test_protocol",
  version: str = "1.0.0",
  module_name: str = "dummy_module",
  function_name: str = "dummy_func",
  accession_id: uuid.UUID | None = None,
  source_repository_accession_id=None,
  source_repository=None,
  commit_hash=None,
  file_system_source_accession_id=None,
  file_system_source=None,
):
  """Create a dummy ORM protocol definition for testing."""
  if accession_id is None:
    accession_id = uuid.UUID("018f4a3b-3c48-7c87-8c4c-35e6a172c74d")
  orm = mock.Mock()
  orm.name = name
  orm.version = version
  orm.module_name = module_name
  orm.function_name = function_name
  orm.accession_id = accession_id
  orm.source_repository_accession_id = source_repository_accession_id
  orm.source_repository = source_repository
  orm.commit_hash = commit_hash
  orm.file_system_source_accession_id = file_system_source_accession_id
  orm.file_system_source = file_system_source
  return orm


def make_pydantic_def(
  accession_id: uuid.UUID | None = None,
  name: str = "test",
  version: str = "1.0.0",
  source_file_path: str = "/tmp/file.py",
  module_name: str = "dummy_module",
  function_name: str = "dummy_func",
) -> FunctionProtocolDefinitionCreate:
  """Create a dummy FunctionProtocolDefinitionCreate with only required fields."""
  if accession_id is None:
    accession_id = uuid.UUID("018f4a3b-3c48-7c87-8c4c-35e6a172c74d")
  return FunctionProtocolDefinitionCreate(
    accession_id=accession_id,
    name=name,
    version=version,
    source_file_path=source_file_path,
    module_name=module_name,
    function_name=function_name,
  )


def test_temporary_sys_path_adds_and_removes() -> None:
  """Test that temporary_sys_path adds and removes a path from sys.path."""
  dummy_path = "/tmp/dummy_path"
  sys_path_orig = list(sys.path)
  with temporary_sys_path(dummy_path):
    assert sys.path[0] == dummy_path
  assert sys.path == sys_path_orig


def test_temporary_sys_path_noop() -> None:
  """Test that temporary_sys_path does nothing if path is None."""
  sys_path_orig = list(sys.path)
  with temporary_sys_path(None):
    assert sys.path == sys_path_orig
  assert sys.path == sys_path_orig


def test_load_protocol_function_success(monkeypatch) -> None:
  """Test loading a protocol function with a valid _protocol_definition."""
  pcm = ProtocolCodeManager()
  module_name = "test_module"
  function_name = "test_func"

  def dummy_func() -> None:
    pass

  dummy_func._protocol_definition = make_pydantic_def()
  dummy_mod = types.ModuleType(module_name)
  setattr(dummy_mod, function_name, dummy_func)
  monkeypatch.setitem(sys.modules, module_name, dummy_mod)
  func, pdef = pcm._load_protocol_function(module_name, function_name)
  assert func is dummy_func
  assert isinstance(pdef, FunctionProtocolDefinitionCreate)


def test_load_protocol_function_missing_func(monkeypatch) -> None:
  """Test loading a protocol function that does not exist."""
  pcm = ProtocolCodeManager()
  module_name = "test_module2"
  dummy_mod = types.ModuleType(module_name)
  monkeypatch.setitem(sys.modules, module_name, dummy_mod)
  with pytest.raises(AttributeError):
    pcm._load_protocol_function(module_name, "not_found")


def test_load_protocol_function_invalid_protocol_def(monkeypatch) -> None:
  """Test loading a protocol function with invalid _protocol_definition."""
  pcm = ProtocolCodeManager()
  module_name = "test_module3"
  function_name = "test_func"

  def dummy_func() -> None:
    pass

  dummy_func._protocol_definition = None  # Not a valid pydantic def
  dummy_mod = types.ModuleType(module_name)
  setattr(dummy_mod, function_name, dummy_func)
  monkeypatch.setitem(sys.modules, module_name, dummy_mod)
  with pytest.raises(AttributeError):
    pcm._load_protocol_function(module_name, function_name)


@pytest.mark.asyncio
async def test_run_git_command_success(monkeypatch) -> None:
  """Test successful execution of a git command."""
  pcm = ProtocolCodeManager()
  dummy_result = mock.Mock(stdout="ok", stderr="", returncode=0)
  monkeypatch.setattr("subprocess.run", lambda *a, **k: dummy_result)
  out = await pcm._run_git_command(["git", "status"], cwd="/", suppress_output=True)
  assert out == "ok"


@pytest.mark.asyncio
async def test_run_git_command_failure(monkeypatch) -> None:
  """Test failure of a git command raises RuntimeError."""
  pcm = ProtocolCodeManager()

  def fail_run(*a, **k) -> NoReturn:
    raise subprocess.CalledProcessError(1, ["git", "fail"], output="", stderr="fail")

  monkeypatch.setattr("subprocess.run", fail_run)
  with pytest.raises(RuntimeError):
    await pcm._run_git_command(["git", "fail"], cwd="/", suppress_output=True)


@pytest.mark.asyncio
async def test_prepare_protocol_code_git(monkeypatch) -> None:
  """Test prepare_protocol_code with a git source."""
  pcm = ProtocolCodeManager()
  repo = mock.Mock()
  repo.git_url = "https://example.com/repo.git"
  repo.local_checkout_path = "/tmp/repo"
  repo.name = "repo"
  orm = make_protocol_def_orm(
    source_repository_accession_id="repo-acc",
    source_repository=repo,
    commit_hash="abc123",
  )
  monkeypatch.setattr(pcm, "_ensure_git_repo_and_fetch", mock.AsyncMock())
  monkeypatch.setattr(pcm, "_checkout_specific_commit", mock.AsyncMock())

  def dummy_func() -> None:
    pass

  monkeypatch.setattr(
    pcm,
    "_load_protocol_function",
    lambda *a, **k: (dummy_func, make_pydantic_def()),
  )
  func, pdef = await pcm.prepare_protocol_code(orm)
  assert callable(func)
  assert isinstance(pdef, FunctionProtocolDefinitionCreate)


@pytest.mark.asyncio
async def test_prepare_protocol_code_filesystem(monkeypatch, tmp_path) -> None:
  """Test prepare_protocol_code with a filesystem source."""
  pcm = ProtocolCodeManager()
  fs_source = mock.Mock()
  fs_source.base_path = str(tmp_path)
  fs_source.name = "fs"
  orm = make_protocol_def_orm(
    file_system_source_accession_id="fs-acc", file_system_source=fs_source,
  )

  def dummy_func() -> None:
    pass

  monkeypatch.setattr(
    pcm,
    "_load_protocol_function",
    lambda *a, **k: (dummy_func, make_pydantic_def()),
  )
  func, pdef = await pcm.prepare_protocol_code(orm)
  assert callable(func)
  assert isinstance(pdef, FunctionProtocolDefinitionCreate)


@pytest.mark.asyncio
async def test_prepare_protocol_code_direct_import(monkeypatch) -> None:
  """Test prepare_protocol_code with direct import (no source)."""
  pcm = ProtocolCodeManager()
  orm = make_protocol_def_orm()

  def dummy_func() -> None:
    pass

  monkeypatch.setattr(
    pcm,
    "_load_protocol_function",
    lambda *a, **k: (dummy_func, make_pydantic_def()),
  )
  func, pdef = await pcm.prepare_protocol_code(orm)
  assert callable(func)
  assert isinstance(pdef, FunctionProtocolDefinitionCreate)
