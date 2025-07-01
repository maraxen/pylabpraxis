"""Placeholder test file for praxis/backend/api/scheduler_api.py
"""
from fastapi.testclient import TestClient

from praxis.backend.api.scheduler_api import router

client = TestClient(router)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
