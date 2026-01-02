"""Debug test to check if routes are registered."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_routes(client: AsyncClient):
    """List all registered routes in the app."""
    from main import app

    for route in app.routes:
        if hasattr(route, "methods"):
            pass
        else:
            pass

    # Try to access the route
    await client.get("/api/v1/decks/")
