import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from starlette.responses import RedirectResponse
import os

from praxis.api import protocols, auth
from praxis.core.orchestrator import Orchestrator
from praxis.configure import PraxisConfiguration
from praxis.api.auth import get_current_admin_user
from fastapi import Depends

# Create a Configuration instance
config_file = "praxis.ini"
config = PraxisConfiguration(config_file)

# Set up default protocol directory
DEFAULT_PROTOCOL_DIR = config.default_protocol_dir

# Create and initialize Orchestrator
orchestrator = Orchestrator(config)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Asynchronous context manager for lifespan events.
    Handles startup and shutdown events.
    """
    # Startup logic
    await orchestrator.initialize_dependencies()
    print(f"Application startup: Initializing dependencies.")
    print(f"Default protocol directory: {DEFAULT_PROTOCOL_DIR}")
    yield
    # Shutdown logic
    await orchestrator.registry.close()
    print("Application shutdown: Closing connections.")

app = FastAPI(lifespan=lifespan)

# Mount static files (for serving the frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routers
app.include_router(protocols.router, prefix="/api/protocols", tags=["protocols"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])


# Example of an endpoint that requires admin access
@app.post("/some_admin_only_endpoint", dependencies=[Depends(get_current_admin_user)])
async def admin_only_endpoint():
    # This endpoint can only be accessed by an authenticated admin user
    return {"message": "Admin access granted"}

# Redirect root URL to index.html
@app.get("/")
async def redirect_to_index():
    return RedirectResponse(url="/static/index.html")

# Add additional directories to the protocols section
config.additional_directories = ""
