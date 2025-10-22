"""Smoke test to ensure the API can start and respond."""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_api_smoke():
    """Test that the API root returns 200 OK."""
    response = client.get("/")
    assert response.status_code == 200
