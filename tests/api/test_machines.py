"""Placeholder test file for praxis/backend/api/machines.py
"""
from fastapi.testclient import TestClient

from praxis.backend.api.machines import router

client = TestClient(router)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
