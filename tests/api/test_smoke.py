"""Smoke test to ensure the API can start and respond."""
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_api_smoke(client: AsyncClient):
    """Test that the API docs returns 200 OK."""
    response = await client.get("/docs")
    assert response.status_code == 200
