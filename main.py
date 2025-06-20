import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Awaitable, Optional

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

# Praxis specific imports
from praxis.backend.api import function_data_outputs, protocols, resources, workcell_api
from praxis.backend.configure import PraxisConfiguration
from praxis.backend.core.orchestrator import Orchestrator
from praxis.backend.core.asset_manager import AssetManager
from praxis.backend.core.workcell_runtime import WorkcellRuntime

# New DB related imports
from praxis.backend.services.praxis_orm_service import PraxisDBService
from praxis.backend.utils.db import (
  KEYCLOAK_DSN_FROM_CONFIG,
  async_engine as praxis_async_engine,
  init_praxis_db_schema,
  get_async_db_session,
  AsyncSessionLocal,
)

# --- Configuration and Logging Setup ---
config_file = "praxis.ini"
praxis_config = PraxisConfiguration(config_file)

# Configure logging from config file
logging.basicConfig(
  filename=praxis_config.log_file,
  level=logging.INFO,
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
  """
  Manages application startup and shutdown events.
  Initializes database connections, services, and the main orchestrator.
  """
  db_service_instance: Optional[PraxisDBService] = None
  orchestrator: Optional[Orchestrator] = None
  asset_manager: Optional[AssetManager] = None
  workcell_runtime: Optional[WorkcellRuntime] = None
  try:
    logger.info("Application startup sequence initiated...")

    # 1. Initialize Praxis Database Schema (SQLAlchemy ORM tables)
    logger.info("Initializing Praxis database schema...")
    await init_praxis_db_schema()
    logger.info("Praxis database schema initialization complete.")

    # 2. Initialize PraxisDBService (handles Praxis DB via SQLAlchemy & Keycloak via asyncpg)
    logger.info("Initializing PraxisDBService...")
    assert KEYCLOAK_DSN_FROM_CONFIG, "Keycloak DSN must be configured in praxis.ini"
    db_service_instance = await PraxisDBService.initialize(
      keycloak_dsn=KEYCLOAK_DSN_FROM_CONFIG
    )
    logger.info("PraxisDBService initialized successfully.")

    # 3. Initialize AssetManager and WorkcellRuntime
    logger.info("Initializing AssetManager and WorkcellRuntime...")
    workcell_runtime = WorkcellRuntime(
      db_session_factory=AsyncSessionLocal,
      workcell_name="praxis_workcell",
      workcell_save_file="workcell_state.json",  # TODO: have these populated from config
    )
    logger.info("WorkcellRuntime initialized successfully.")
    db_session = await anext(get_async_db_session())
    asset_manager = AssetManager(
      db_session=db_session, workcell_runtime=workcell_runtime
    )

    # 3. Instantiate and initialize the Orchestrator with its dependencies
    logger.info("Initializing orchestrator...")
    orchestrator = Orchestrator(
      db_session_factory=AsyncSessionLocal,
      asset_manager=asset_manager,
      workcell_runtime=workcell_runtime,
    )
    logger.info("Orchestrator dependencies initialized.")

    # 4. Store the fully initialized orchestrator in the app state
    # This makes it accessible to all API routes via the `request` object.
    app.state.orchestrator = orchestrator
    logger.info("Orchestrator attached to application state.")
    logger.info("Application startup complete.")

    yield  # The application is now running

  except Exception as e:
    logger.error(f"Error during application startup: {str(e)}", exc_info=True)
    # In a production scenario, you might want to exit or handle this more gracefully
    raise
  finally:
    logger.info("Application shutdown sequence initiated...")
    try:
      # Safely close the database services using the instance created during startup
      if db_service_instance:
        logger.info("Closing PraxisDBService (Keycloak pool)...")
        await db_service_instance.close()
        logger.info("PraxisDBService closed.")

      # Dispose of the SQLAlchemy engine for the main Praxis DB
      logger.info("Disposing of Praxis SQLAlchemy engine...")
      await praxis_async_engine.dispose()
      logger.info("Praxis SQLAlchemy engine disposed.")

      logger.info("Application shutdown complete.")
    except Exception as e:
      logger.error(f"Error during application shutdown: {str(e)}", exc_info=True)


# --- FastAPI App Initialization ---
app = FastAPI(
  title="PyLabPraxis Backend",
  description="A comprehensive Python-based platform to automate and manage laboratory workflows.",
  version="1.0.0",
  lifespan=lifespan,
)

# CORS Middleware Configuration
app.add_middleware(
  CORSMiddleware,
  allow_origins=[
    "http://localhost:5173",  # Default Vite dev port
    "http://localhost:4200",  # Default Angular dev port
  ],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# --- API Router Inclusion ---
app.include_router(
  function_data_outputs.router, prefix="/api/v1/data-outputs", tags=["Data Outputs"]
)
app.include_router(protocols.router, prefix="/api/v1/protocols", tags=["Protocols"])
app.include_router(workcell_api.router, prefix="/api/v1/workcell", tags=["Workcell"])
app.include_router(resources.router, prefix="/api/v1/assets", tags=["Assets"])


# --- Middleware and Root Endpoint ---


@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
  """Middleware to log incoming requests and their response status codes."""
  logger.info(f"Request: {request.method} {request.url.path}")
  response: Response = await call_next(request)
  logger.info(
    f"Response: {request.method} {request.url.path} - Status {response.status_code}"
  )
  return response


@app.get("/", include_in_schema=False)
async def root_redirect():
  """Redirects the root URL to the static index page."""
  return RedirectResponse(url="/docs")
