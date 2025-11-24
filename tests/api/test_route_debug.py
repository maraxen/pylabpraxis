"""Debug test to check if routes are registered."""
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_list_routes(client: AsyncClient):
    """List all registered routes in the app."""
    from main import app

    print("\n=== Registered Routes ===")
    for route in app.routes:
        if hasattr(route, 'methods'):
            print(f"{route.methods} {route.path}")
        else:
            print(f"MOUNT {route.path}")

    # Try to access the route
    response = await client.get("/api/v1/decks/")
    print(f"\nGET /api/v1/decks/ status: {response.status_code}")
