"""Unit tests for UUID utility functions."""

import uuid
from unittest.mock import patch

from praxis.backend.utils import uuid as praxis_uuid


def test_uuid7_generation() -> None:
  """Test that uuid7() generates a valid UUID object with version 7."""
  test_uuid_str = "018f3d6c-72e8-7a28-97a3-2def368c0759"

  with patch("uuid_utils.uuid7", return_value=test_uuid_str) as mock_lib_uuid7:
    generated_uuid = praxis_uuid.uuid7()

  mock_lib_uuid7.assert_called_once()

  assert isinstance(generated_uuid, uuid.UUID)

  assert str(generated_uuid) == test_uuid_str

  assert generated_uuid.version == 7


def test_uuid4_generation() -> None:
  """Test that uuid4() generates a valid UUID object with version 4."""
  generated_uuid = praxis_uuid.uuid4()

  assert isinstance(generated_uuid, uuid.UUID)

  assert generated_uuid.version == 4
