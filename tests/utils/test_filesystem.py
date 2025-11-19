"""Tests for filesystem utilities in utils/filesystem.py."""

import tempfile
from pathlib import Path

import pytest

from praxis.backend.utils.filesystem import RealFileSystem


class TestRealFileSystem:
    """Tests for RealFileSystem class."""

    def test_can_instantiate(self) -> None:
        """Test that RealFileSystem can be instantiated."""
        fs = RealFileSystem()
        assert fs is not None
        assert isinstance(fs, RealFileSystem)

    def test_open_reads_file(self) -> None:
        """Test that open() can read a file."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.write("test content\n")
            tmp_path = tmp.name

        try:
            fs = RealFileSystem()
            with fs.open(tmp_path, "r") as f:
                content = f.read()
            assert content == "test content\n"
        finally:
            Path(tmp_path).unlink()

    def test_open_writes_file(self) -> None:
        """Test that open() can write to a file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            fs = RealFileSystem()
            with fs.open(tmp_path, "w") as f:
                f.write("new content\n")

            # Verify content was written
            with open(tmp_path, "r") as f:
                content = f.read()
            assert content == "new content\n"
        finally:
            Path(tmp_path).unlink()

    def test_open_with_encoding(self) -> None:
        """Test that open() respects encoding parameter."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as tmp:
            tmp.write("test with ñ unicode\n")
            tmp_path = tmp.name

        try:
            fs = RealFileSystem()
            with fs.open(tmp_path, "r", encoding="utf-8") as f:
                content = f.read()
            assert content == "test with ñ unicode\n"
            assert "ñ" in content
        finally:
            Path(tmp_path).unlink()

    def test_open_default_mode_is_read(self) -> None:
        """Test that open() defaults to read mode."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.write("default mode test\n")
            tmp_path = tmp.name

        try:
            fs = RealFileSystem()
            # Not passing mode should default to "r"
            with fs.open(tmp_path) as f:
                content = f.read()
            assert content == "default mode test\n"
        finally:
            Path(tmp_path).unlink()

    def test_open_nonexistent_file_raises_error(self) -> None:
        """Test that opening nonexistent file raises FileNotFoundError."""
        fs = RealFileSystem()
        with pytest.raises(FileNotFoundError):
            fs.open("/nonexistent/path/to/file.txt", "r")

    def test_open_returns_file_object(self) -> None:
        """Test that open() returns a file-like object."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.write("test\n")
            tmp_path = tmp.name

        try:
            fs = RealFileSystem()
            file_obj = fs.open(tmp_path, "r")

            # Check it's a file-like object with expected methods
            assert hasattr(file_obj, "read")
            assert hasattr(file_obj, "readline")
            assert hasattr(file_obj, "close")

            file_obj.close()
        finally:
            Path(tmp_path).unlink()

    def test_open_binary_mode(self) -> None:
        """Test that open() works in binary mode."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmp:
            tmp.write(b"binary content")
            tmp_path = tmp.name

        try:
            fs = RealFileSystem()
            with fs.open(tmp_path, "rb") as f:
                content = f.read()
            assert content == b"binary content"
            assert isinstance(content, bytes)
        finally:
            Path(tmp_path).unlink()

    def test_open_append_mode(self) -> None:
        """Test that open() works in append mode."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.write("initial\n")
            tmp_path = tmp.name

        try:
            fs = RealFileSystem()
            with fs.open(tmp_path, "a") as f:
                f.write("appended\n")

            # Verify both lines are present
            with open(tmp_path, "r") as f:
                content = f.read()
            assert content == "initial\nappended\n"
        finally:
            Path(tmp_path).unlink()
