# main.py (Refactored for new DB setup)

from typing import Awaitable, AsyncGenerator # Added AsyncGenerator
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette.responses import RedirectResponse
import logging

# Praxis specific imports
from praxis.backend.api import protocols, resources, workcell_api
from praxis.backend.core.orchestrator import Orchestrator
from praxis.backend.configure import PraxisConfiguration

# New DB related imports
from praxis.backend.utils.db import init_praxis_db_schema, KEYCLOAK_DSN_FROM_CONFIG, async_engine as praxis_async_engine
from praxis.backend.services.praxis_orm_service import PraxisDBService # Assuming praxis_orm_service.py is in praxis/

# --- Configuration and Logging Setup ---
# This part remains largely the same
config_file = "praxis.ini"
praxis_config = PraxisConfiguration(config_file)

# Configure logging from config file - THIS SHOULD BE THE ONLY basicConfig CALL
logging.basicConfig(
    filename=praxis_config.log_file,
    level=logging.INFO, # Or get from praxis_config if defined there
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# --- Global Orchestrator Instance ---
# The Orchestrator will now need to be aware of PraxisDBService
# Option 1: Pass PraxisDBService instance to Orchestrator
# Option 2: Orchestrator instantiates PraxisDBService internally in its initialize_dependencies
# We'll assume Orchestrator will handle its db_service initialization.
orchestrator = Orchestrator(db_service=db_service_instance) # TODO: refactor Orchestrator to accept db_service_instance

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]: # Corrected type hint
    """Lifecycle manager for application startup/shutdown."""
    db_service_instance: Optional[PraxisDBService] = None
    try:
        logger.info("Starting application initialization...")

        # 1. Initialize Praxis Database Schema (SQLAlchemy ORM tables)
        logger.info("Initializing Praxis database schema...")
        await init_praxis_db_schema()
        logger.info("Praxis database schema initialization complete.")

        # 2. Initialize PraxisDBService (handles Praxis DB via SQLAlchemy & Keycloak via asyncpg)
        #    The KEYCLOAK_DSN_FROM_CONFIG is imported from praxis.utils.db
        logger.info("Initializing PraxisDBService...")
        db_service_instance = await PraxisDBService.initialize(keycloak_dsn=KEYCLOAK_DSN_FROM_CONFIG)
        if not db_service_instance:
            # This case should ideally be handled within PraxisDBService.initialize by raising an error
            logger.critical("Failed to initialize PraxisDBService. Application cannot start.")
            raise RuntimeError("Failed to initialize PraxisDBService.")
        logger.info("PraxisDBService initialized successfully.")

        # 3. Initialize Orchestrator and its dependencies
        #    The Orchestrator's initialize_dependencies method should now use the db_service_instance.
        #    Modify Orchestrator to accept/use this db_service_instance.
        #    For example, orchestrator.db could now point to db_service_instance.
        logger.info("Initializing orchestrator dependencies...")
        await orchestrator.initialize_dependencies(db_service=db_service_instance) # Pass the service
        app.state.orchestrator = orchestrator
        # Ensure orchestrator.db (or similar attribute) is set to db_service_instance
        # Example: if orchestrator.initialize_dependencies sets self.db_service = db_service
        logger.info("Successfully initialized orchestrator and its dependencies.")
        logger.info(f"Default protocol directory from config: {praxis_config.default_protocol_dir}")

        yield

    except Exception as e:
        logger.error(f"Error during application startup: {str(e)}", exc_info=True)
        # Depending on the severity, you might want to prevent the app from running
        raise
    finally:
        logger.info("Starting application shutdown...")
        try:
            # Close PraxisDBService (which handles Keycloak pool)
            if hasattr(orchestrator, 'db_service') and orchestrator.db_service: # Check if orchestrator has the service
                logger.info("Closing PraxisDBService (Keycloak pool)...")
                await orchestrator.db_service.close()
                logger.info("PraxisDBService closed.")
            elif db_service_instance: # Fallback if not on orchestrator but initialized here
                logger.info("Closing PraxisDBService (Keycloak pool) directly...")
                await db_service_instance.close()
                logger.info("PraxisDBService closed.")


            # Dispose of the SQLAlchemy engine for Praxis DB
            logger.info("Disposing of Praxis SQLAlchemy engine...")
            await praxis_async_engine.dispose()
            logger.info("Praxis SQLAlchemy engine disposed.")

            logger.info("Application shutdown complete.")
        except Exception as e:
            logger.error(f"Error during application shutdown: {str(e)}", exc_info=True)


app = FastAPI(lifespan=lifespan)

# CORS configuration (remains the same)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4200"], # TODO: based on config
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# API routes (remain the same)
app.include_router(protocols.router, prefix="/api/v1/protocols", tags=["protocols"])
app.include_router(workcell_api.router, prefix="/api/v1/workcell", tags=["workcell"])
app.include_router(resources.router, prefix="/api/v1/assets", tags=["assets"])


@app.get("/")
async def redirect_to_index():
    return RedirectResponse(url="/static/index.html")


@app.middleware("http")
async def log_requests(request: Request, call_next: Awaitable[Response]) -> Response: # Corrected Awaitable type
    logger.info(f"Request: {request.method} {request.url}")
    # Be cautious logging query_params if they can contain sensitive info
    # logger.info(f"Query parameters: {dict(request.query_params)}")
    response: Response = await call_next(request) # type: ignore # TODO: Check if type: ignore is needed
    logger.info(f"Response status: {response.status_code}") # type: ignore # TODO: Check if type: ignore is needed
    return response # type: ignore # TODO: Check if type: ignore is needed

# Removed the if __name__ == "__main__": block for uvicorn.run
# This is typically handled by a process manager or a run script (e.g., run.sh or Procfile)
# For local development, you'd run: uvicorn main:app --reload --host 0.0.0.0 --port 8000
