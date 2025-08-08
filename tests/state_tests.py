import errno
import os
import shutil
import tempfile
import time
import unittest
from shelve import DbfilenameShelf

from praxis.utils.state import RuntimeState


class TestState(unittest.TestCase):

  def setUp(self) -> None:
    self.tempdir = tempfile.mkdtemp()
    self.temp_file = os.path.join(self.tempdir, "test_state")
    self.persistent_state: DbfilenameShelf = DbfilenameShelf(self.temp_file)
    fd = os.open(self.temp_file, os.O_CREAT | os.O_RDWR)
    os.close(fd)

  def tearDown(self) -> None:
    os.remove(self.temp_file)
    try:
        shutil.rmtree(self.tempdir)  # delete directory
    except OSError as exc:
        if exc.errno != errno.ENOENT:  # ENOENT - no such file or directory
            raise  # re-raise exception

  def test_runtime_state_init(self) -> None:
    with self.persistent_state as s:
      s["key"] = "value"
    runtime_state = RuntimeState(self.temp_file)
    assert runtime_state["key"] == "value"

  def test_runtime_state_set_get_item(self) -> None:
    with self.persistent_state as s:
      s["key"] = "value"
    runtime_state = RuntimeState(self.temp_file)
    runtime_state["key2"] = "value2"
    assert runtime_state["key2"] == "value2"
    s2: DbfilenameShelf
    with DbfilenameShelf(self.temp_file) as s2:
      assert s2["key2"] == "value2"

  def test_runtime_state_del_item(self) -> None:
    with self.persistent_state as s:
      s["key"] = "value"
    runtime_state = RuntimeState(self.temp_file)
    del runtime_state["key"]
    assert "key" not in runtime_state
    s2: DbfilenameShelf
    with DbfilenameShelf(self.temp_file) as s2:
      assert "key" not in s2

  def test_runtime_state_reinitialization(self) -> None:
    with self.persistent_state as s:
      s["key"] = "value"
    runtime_state = RuntimeState(self.temp_file)
    assert runtime_state["key"] == "value"
    assert "key2" not in runtime_state
    runtime_state["key2"] = "value2"
    del runtime_state
    time.sleep(1)
    runtime_state = RuntimeState(self.temp_file)
    assert "key" in runtime_state
    assert "key2" in runtime_state
    assert runtime_state["key"] == "value"
    assert runtime_state["key2"] == "value2"

  def test_runtime_state_iter_len(self) -> None:
    runtime_state = RuntimeState(self.persistent_state)
    runtime_state["key1"] = "value1"
    runtime_state["key2"] = "value2"
    assert len(runtime_state) == 2
    assert set(runtime_state) == {"key1", "key2"}
    runtime_state.close()

if __name__ == "__main__":
    unittest.main()
