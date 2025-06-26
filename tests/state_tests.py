import errno
import os
import shutil
import tempfile
import time
import unittest
from shelve import DbfilenameShelf

from praxis.utils.state import RuntimeState


class TestState(unittest.TestCase):

  def setUp(self):
    self.tempdir = tempfile.mkdtemp()
    self.temp_file = os.path.join(self.tempdir, "test_state")
    self.persistent_state: DbfilenameShelf = DbfilenameShelf(self.temp_file)
    fd = os.open(self.temp_file, os.O_CREAT | os.O_RDWR)
    os.close(fd)

  def tearDown(self):
    os.remove(self.temp_file)
    try:
        shutil.rmtree(self.tempdir)  # delete directory
    except OSError as exc:
        if exc.errno != errno.ENOENT:  # ENOENT - no such file or directory
            raise  # re-raise exception

  def test_runtime_state_init(self):
    with self.persistent_state as s:
      s["key"] = "value"
    runtime_state = RuntimeState(self.temp_file)
    self.assertEqual(runtime_state["key"], "value")

  def test_runtime_state_set_get_item(self):
    with self.persistent_state as s:
      s["key"] = "value"
    runtime_state = RuntimeState(self.temp_file)
    runtime_state["key2"] = "value2"
    self.assertEqual(runtime_state["key2"], "value2")
    s2: DbfilenameShelf
    with DbfilenameShelf(self.temp_file) as s2:
      self.assertEqual(s2["key2"], "value2")

  def test_runtime_state_del_item(self):
    with self.persistent_state as s:
      s["key"] = "value"
    runtime_state = RuntimeState(self.temp_file)
    del runtime_state["key"]
    self.assertNotIn("key", runtime_state)
    s2: DbfilenameShelf
    with DbfilenameShelf(self.temp_file) as s2:
      self.assertNotIn("key", s2)

  def test_runtime_state_reinitialization(self):
    with self.persistent_state as s:
      s["key"] = "value"
    runtime_state = RuntimeState(self.temp_file)
    self.assertEqual(runtime_state["key"], "value")
    self.assertNotIn("key2", runtime_state)
    runtime_state["key2"] = "value2"
    del runtime_state
    time.sleep(1)
    runtime_state = RuntimeState(self.temp_file)
    self.assertIn("key", runtime_state)
    self.assertIn("key2", runtime_state)
    self.assertEqual(runtime_state["key"], "value")
    self.assertEqual(runtime_state["key2"], "value2")

  def test_runtime_state_iter_len(self):
    runtime_state = RuntimeState(self.persistent_state)
    runtime_state["key1"] = "value1"
    runtime_state["key2"] = "value2"
    self.assertEqual(len(runtime_state), 2)
    self.assertEqual(set(runtime_state), {"key1", "key2"})
    runtime_state.close()

if __name__ == "__main__":
    unittest.main()
