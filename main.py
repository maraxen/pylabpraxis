import asyncio
from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette.responses import RedirectResponse
import os
import logging  # Import logging.config


from praxis.api import protocols, assets, workcell_api
from praxis.core.orchestrator import Orchestrator
from praxis.configure import PraxisConfiguration
from praxis.utils.db import db


# Create a Configuration instance
config_file = "praxis.ini"
praxis_config = PraxisConfiguration(config_file)

# Configure logging from config file
logging.basicConfig(
    filename=praxis_config.log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)  # Get a logger for main.py

# Global instances
config = PraxisConfiguration("praxis.ini")
orchestrator = Orchestrator(config)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for application startup/shutdown."""
    try:
        # Startup
        logger.info("Starting application initialization...")
        logger.info(f"Default protocol directory: {config.default_protocol_dir}")

        # Initialize orchestrator and attach to app state
        await orchestrator.initialize_dependencies()
        app.state.orchestrator = orchestrator
        logger.info("Successfully initialized dependencies")

        yield

    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

    finally:
        # Shutdown
        logger.info("Starting application shutdown...")
        try:
            if orchestrator.db:
                await orchestrator.db.close()
            logger.info("Successfully closed database connections")
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")


app = FastAPI(lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# API routes
app.include_router(protocols.router, prefix="/api/v1/protocols", tags=["protocols"])
app.include_router(workcell_api.router, prefix="/api/v1/workcell", tags=["workcell"])
app.include_router(assets.router, prefix="/api/v1/assets", tags=["assets"])


@app.get("/")
async def redirect_to_index():
    """Redirect root to frontend."""
    return RedirectResponse(url="/static/index.html")


# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Query parameters: {dict(request.query_params)}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
