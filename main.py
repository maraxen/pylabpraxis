import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from starlette.responses import RedirectResponse
import os

from praxis.api import protocols, assets
from praxis.core.orchestrator import Orchestrator
from praxis.configure import PraxisConfiguration
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
    try:
        # Startup logic
        print("Starting application initialization...")
        print(f"Default protocol directory: {DEFAULT_PROTOCOL_DIR}")

        try:
            await orchestrator.initialize_dependencies()
            print("Successfully initialized dependencies")
        except ConnectionError as e:
            print(f"Failed to initialize database connections: {str(e)}")
            # You might want to exit here depending on your requirements
            raise
        except Exception as e:
            print(f"Unexpected error during initialization: {str(e)}")
            raise

        yield

    except Exception as e:
        print(f"Error during application startup: {str(e)}")
        raise

    finally:
        # Shutdown logic
        print("Starting application shutdown...")
        try:
            if orchestrator.db is not None:
                await orchestrator.db.close()
                print("Successfully closed database connections")
        except Exception as e:
            print(f"Error during database shutdown: {str(e)}")
        print("Application shutdown complete")


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
app.include_router(assets.router, prefix="/api/v1/assets", tags=["assets"])


# Redirect root URL to index.html
@app.get("/")
async def redirect_to_index():
    return RedirectResponse(url="/static/index.html")


# Add additional directories to the protocols section
config.additional_directories = ""
