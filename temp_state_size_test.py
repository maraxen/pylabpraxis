
import json
import uuid
from unittest.mock import MagicMock, patch

import pytest

from praxis.backend.configure import PraxisConfiguration
from praxis.backend.services.state import PraxisState

def generate_complex_state_data():
    """Generates a dictionary with a complex structure to simulate real state."""
    return {
        "run_id": str(uuid.uuid4()),
        "parameters": {
            "sample_count": 96,
            "reagent_volumes": [10.5, 11.2, 10.9] * 32,
            "use_temp_control": True,
            "temp_setpoint": 37.5,
        },
        "deck_layout": {
            f"slot_{i}": {
                "name": f"plate_{i}",
                "type": "96-well",
                "contents": {
                    f"well_{chr(65+row)}{col}": {
                        "sample_id": f"s_{i}_{row}_{col}",
                        "volume": 100,
                        "concentration": (row * col) * 0.1,
                    }
                    for row in range(8) for col in range(12)
                }
            } for i in range(1, 12)
        },
        "status": "running",
        "step_history": [
            {"step": "aspirate", "plate": "plate_1", "volume": 50, "timestamp": f"2023-10-27T10:0{i}:00Z"}
            for i in range(10)
        ],
        "measurements": {
            f"measurement_{i}": {"type": "absorbance", "value": i * 0.01 + 0.05}
            for i in range(500)
        }
    }

@patch("praxis.backend.services.state.redis.Redis")
def test_snapshot_size_simulation(mock_redis):
    """Simulates the creation of a large state and measures its JSON size."""
    # Arrange
    mock_config = MagicMock(spec=PraxisConfiguration)
    mock_config.redis_host = "localhost"
    mock_config.redis_port = 6379
    mock_config.redis_db = 0

    client = MagicMock()
    # Mock Redis 'get' to return an empty state initially
    client.get.return_value = json.dumps({}).encode("utf-8")
    mock_redis.return_value = client

    # Act
    state = PraxisState(config=mock_config)
    large_data = generate_complex_state_data()
    state.update(large_data)

    # Serialize the data to JSON to measure its size
    json_snapshot = json.dumps(state.to_dict())
    snapshot_size_bytes = len(json_snapshot.encode("utf-8"))

    # Assert & Print
    print(f"Simulated snapshot size: {snapshot_size_bytes} bytes")
    print(f"Simulated snapshot size: {snapshot_size_bytes / 1024:.2f} KB")
    assert snapshot_size_bytes > 0

if __name__ == "__main__":
    test_snapshot_size_simulation()
