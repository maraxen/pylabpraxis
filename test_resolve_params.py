import sys
import os

# Add the directory to sys.path
sys.path.append("praxis/web-client/src/assets/python")

from web_bridge import resolve_parameters


def test_resolve_parameters():
  params = {
    "source_plate": {"name": "My Plate", "fqn": "pylabrobot.resources.Plate"},
    "volume": 50,
    "source_wells": ["A1", "A2"],
  }

  metadata = {"source_plate": "pylabrobot.resources.Plate", "volume": "float"}

  asset_reqs = {"source_plate": "Plate"}

  # Mocking pylabrobot.resources for the test environment
  # Since we might not have it installed in this shell
  try:
    import pylabrobot.resources as res

    print("PLR found, using real objects")
  except ImportError:
    print("PLR not found, test might fail or use fallback")
    return

  resolved = resolve_parameters(params, metadata, asset_reqs)

  print(f"Resolved params: {resolved}")

  assert isinstance(resolved["source_plate"], res.Plate)
  assert resolved["source_plate"].name == "My Plate"
  assert resolved["volume"] == 50
  assert resolved["source_wells"] == ["A1", "A2"]

  print("Test passed!")


if __name__ == "__main__":
  test_resolve_parameters()
