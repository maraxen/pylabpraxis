import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from starlette.responses import RedirectResponse
import os
import logging

from praxis.api import protocols, auth
from praxis.core.orchestrator import Orchestrator
from praxis.configure import PraxisConfiguration
from praxis.api.auth import get_current_admin_user
from praxis.protocol.registry import initialize_registry
from praxis.api.initialization import initialize_all
from fastapi import Depends

# Set up logging
logger = logging.getLogger("praxis.main")
logger.setLevel(logging.DEBUG)

# Create handlers if they don't exist
if not logger.handlers:
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler("logs/main.log", mode="a")

    # Create formatters and add it to handlers
    log_format = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
    console_handler.setFormatter(log_format)
    file_handler.setFormatter(log_format)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Prevent the logger from propagating to the root logger
    logger.propagate = False

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
    logger.info("Application startup: Initializing dependencies.")
    logger.info(f"Default protocol directory: {DEFAULT_PROTOCOL_DIR}")

    # Initialize protocol registry
    registry = await initialize_registry(config)
    orchestrator.registry = registry

    # Initialize other dependencies
    await orchestrator.initialize_dependencies()

    # Initialize all resources
    logger.info("Initializing all resources...")
    app.state.initialization_state = await initialize_all(config)
    logger.info("Resource initialization complete.")

    # Log registered routes
    logger.info("\nRegistered routes:")
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            logger.info(f"{route.path} [{', '.join(route.methods)}]")

    yield

    # Shutdown logic
    await orchestrator.registry.close()
    logger.info("Application shutdown: Closing connections.")


# Create FastAPI app with debug logging
app = FastAPI(lifespan=lifespan, debug=True)


# Mount static files (for serving the frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routers
logger.info("\nMounting protocol router...")
app.include_router(protocols.router, prefix="/api/protocols", tags=["protocols"])
logger.info("Mounting auth router...")
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
logger.info("Routers mounted successfully\n")


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
