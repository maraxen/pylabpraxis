"""Tests for core/filesystem.py."""

from pathlib import Path

import pytest

from praxis.backend.core.filesystem import FileSystem


class TestFileSystemOpen:

    """Tests for FileSystem.open() method."""

    def test_open_file_for_reading(self, tmp_path: Path) -> None:
        """Test that open() can open a file for reading."""
        fs = FileSystem()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        with fs.open(str(test_file), "r") as f:
            content = f.read()
            assert content == "test content"

    def test_open_file_for_writing(self, tmp_path: Path) -> None:
        """Test that open() can open a file for writing."""
        fs = FileSystem()
        test_file = tmp_path / "test.txt"

        with fs.open(str(test_file), "w") as f:
            f.write("new content")

        assert test_file.read_text() == "new content"

    def test_open_with_encoding(self, tmp_path: Path) -> None:
        """Test that open() respects encoding parameter."""
        fs = FileSystem()
        test_file = tmp_path / "test.txt"

        with fs.open(str(test_file), "w", encoding="utf-8") as f:
            f.write("UTF-8 content: ñ")

        with fs.open(str(test_file), "r", encoding="utf-8") as f:
            content = f.read()
            assert "ñ" in content

    def test_open_returns_file_object(self, tmp_path: Path) -> None:
        """Test that open() returns a file object."""
        fs = FileSystem()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        result = fs.open(str(test_file), "r")
        assert hasattr(result, "read")
        assert hasattr(result, "close")
        result.close()


class TestFileSystemExists:

    """Tests for FileSystem.exists() method."""

    def test_exists_returns_true_for_existing_file(self, tmp_path: Path) -> None:
        """Test that exists() returns True for existing file."""
        fs = FileSystem()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        assert fs.exists(str(test_file)) is True

    def test_exists_returns_false_for_nonexistent_file(self, tmp_path: Path) -> None:
        """Test that exists() returns False for nonexistent file."""
        fs = FileSystem()
        test_file = tmp_path / "nonexistent.txt"

        assert fs.exists(str(test_file)) is False

    def test_exists_returns_true_for_directory(self, tmp_path: Path) -> None:
        """Test that exists() returns True for existing directory."""
        fs = FileSystem()
        assert fs.exists(str(tmp_path)) is True


class TestFileSystemIsdir:

    """Tests for FileSystem.isdir() method."""

    def test_isdir_returns_true_for_directory(self, tmp_path: Path) -> None:
        """Test that isdir() returns True for directory."""
        fs = FileSystem()
        assert fs.isdir(str(tmp_path)) is True

    def test_isdir_returns_false_for_file(self, tmp_path: Path) -> None:
        """Test that isdir() returns False for file."""
        fs = FileSystem()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        assert fs.isdir(str(test_file)) is False

    def test_isdir_returns_false_for_nonexistent(self, tmp_path: Path) -> None:
        """Test that isdir() returns False for nonexistent path."""
        fs = FileSystem()
        nonexistent = tmp_path / "nonexistent"

        assert fs.isdir(str(nonexistent)) is False


class TestFileSystemListdir:

    """Tests for FileSystem.listdir() method."""

    def test_listdir_returns_directory_contents(self, tmp_path: Path) -> None:
        """Test that listdir() returns directory contents."""
        fs = FileSystem()
        (tmp_path / "file1.txt").write_text("test1")
        (tmp_path / "file2.txt").write_text("test2")

        result = fs.listdir(str(tmp_path))
        assert "file1.txt" in result
        assert "file2.txt" in result

    def test_listdir_returns_list(self, tmp_path: Path) -> None:
        """Test that listdir() returns a list."""
        fs = FileSystem()
        result = fs.listdir(str(tmp_path))
        assert isinstance(result, list)

    def test_listdir_empty_directory(self, tmp_path: Path) -> None:
        """Test that listdir() returns empty list for empty directory."""
        fs = FileSystem()
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        result = fs.listdir(str(empty_dir))
        assert result == []


class TestFileSystemMkdir:

    """Tests for FileSystem.mkdir() method."""

    def test_mkdir_creates_directory(self, tmp_path: Path) -> None:
        """Test that mkdir() creates a directory."""
        fs = FileSystem()
        new_dir = tmp_path / "newdir"

        fs.mkdir(str(new_dir))
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_mkdir_with_mode(self, tmp_path: Path) -> None:
        """Test that mkdir() respects mode parameter."""
        fs = FileSystem()
        new_dir = tmp_path / "newdir"

        fs.mkdir(str(new_dir), mode=0o755)
        assert new_dir.exists()

    def test_mkdir_raises_on_existing_directory(self, tmp_path: Path) -> None:
        """Test that mkdir() raises error for existing directory."""
        fs = FileSystem()
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()

        with pytest.raises(FileExistsError):
            fs.mkdir(str(existing_dir))


class TestFileSystemMakedirs:

    """Tests for FileSystem.makedirs() method."""

    def test_makedirs_creates_nested_directories(self, tmp_path: Path) -> None:
        """Test that makedirs() creates nested directories."""
        fs = FileSystem()
        nested_dir = tmp_path / "a" / "b" / "c"

        fs.makedirs(str(nested_dir))
        assert nested_dir.exists()
        assert nested_dir.is_dir()

    def test_makedirs_with_exist_ok_true(self, tmp_path: Path) -> None:
        """Test that makedirs() with exist_ok=True doesn't raise error."""
        fs = FileSystem()
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()

        # Should not raise
        fs.makedirs(str(existing_dir), exist_ok=True)
        assert existing_dir.exists()

    def test_makedirs_with_exist_ok_false_raises(self, tmp_path: Path) -> None:
        """Test that makedirs() with exist_ok=False raises error."""
        fs = FileSystem()
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()

        with pytest.raises(FileExistsError):
            fs.makedirs(str(existing_dir), exist_ok=False)


class TestFileSystemRemove:

    """Tests for FileSystem.remove() method."""

    def test_remove_deletes_file(self, tmp_path: Path) -> None:
        """Test that remove() deletes a file."""
        fs = FileSystem()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        fs.remove(str(test_file))
        assert not test_file.exists()

    def test_remove_raises_on_nonexistent_file(self, tmp_path: Path) -> None:
        """Test that remove() raises error for nonexistent file."""
        fs = FileSystem()
        nonexistent = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            fs.remove(str(nonexistent))

    def test_remove_raises_on_directory(self, tmp_path: Path) -> None:
        """Test that remove() raises error when trying to remove directory."""
        fs = FileSystem()
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()

        with pytest.raises((IsADirectoryError, PermissionError, OSError)):
            fs.remove(str(test_dir))


class TestFileSystemRmdir:

    """Tests for FileSystem.rmdir() method."""

    def test_rmdir_deletes_empty_directory(self, tmp_path: Path) -> None:
        """Test that rmdir() deletes an empty directory."""
        fs = FileSystem()
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()

        fs.rmdir(str(test_dir))
        assert not test_dir.exists()

    def test_rmdir_raises_on_nonempty_directory(self, tmp_path: Path) -> None:
        """Test that rmdir() raises error for non-empty directory."""
        fs = FileSystem()
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()
        (test_dir / "file.txt").write_text("test")

        with pytest.raises(OSError):
            fs.rmdir(str(test_dir))

    def test_rmdir_raises_on_nonexistent_directory(self, tmp_path: Path) -> None:
        """Test that rmdir() raises error for nonexistent directory."""
        fs = FileSystem()
        nonexistent = tmp_path / "nonexistent"

        with pytest.raises(FileNotFoundError):
            fs.rmdir(str(nonexistent))


class TestFileSystemIntegration:

    """Integration tests for FileSystem."""

    def test_create_write_read_delete_workflow(self, tmp_path: Path) -> None:
        """Test complete file workflow."""
        fs = FileSystem()
        test_file = tmp_path / "workflow.txt"

        # Create and write
        with fs.open(str(test_file), "w") as f:
            f.write("workflow test")

        # Verify exists
        assert fs.exists(str(test_file))

        # Read
        with fs.open(str(test_file), "r") as f:
            content = f.read()
            assert content == "workflow test"

        # Delete
        fs.remove(str(test_file))
        assert not fs.exists(str(test_file))

    def test_directory_operations_workflow(self, tmp_path: Path) -> None:
        """Test complete directory workflow."""
        fs = FileSystem()
        test_dir = tmp_path / "dir1" / "dir2"

        # Create nested directories
        fs.makedirs(str(test_dir))
        assert fs.exists(str(test_dir))
        assert fs.isdir(str(test_dir))

        # Create file in directory
        test_file = test_dir / "file.txt"
        with fs.open(str(test_file), "w") as f:
            f.write("test")

        # List directory
        contents = fs.listdir(str(test_dir))
        assert "file.txt" in contents

        # Clean up
        fs.remove(str(test_file))
        fs.rmdir(str(test_dir))
        assert not fs.exists(str(test_dir))
