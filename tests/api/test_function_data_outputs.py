"""Placeholder test file for praxis/backend/api/function_data_outputs.py."""
from fastapi.testclient import TestClient

from praxis.backend.api.function_data_outputs import router

client = TestClient(router)

def test_read_main() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
