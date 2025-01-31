import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from starlette.responses import RedirectResponse
import os

from praxis.api import protocols, auth, assets
from praxis.core.orchestrator import Orchestrator
from praxis.configure import PraxisConfiguration
from praxis.api import get_current_admin_user
from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware

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
    assert orchestrator.db is not None
    await orchestrator.db.close()
    print("Application shutdown: Closing connections.")

app = FastAPI(lifespan=lifespan)

# Update CORS middleware with specific headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # More permissive for development
    expose_headers=["*"],
    max_age=3600,
)

# Include API routers with versioning
app.include_router(protocols.router, prefix="/api/v1/protocols", tags=["protocols"])
app.include_router(auth.router, tags=["auth"])  # Remove prefix as it's already in the router
app.include_router(assets.router, tags=["assets"])

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
