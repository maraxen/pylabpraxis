"""Core backend application for PyLabPraxis."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from praxis.backend.api import discovery, function_data_outputs, protocols, resources, workcell_api
from praxis.backend.api.scheduler_api import initialize_scheduler_components
from praxis.backend.configure import PraxisConfiguration
from praxis.backend.core.asset_manager import AssetManager
from praxis.backend.core.orchestrator import Orchestrator
from praxis.backend.core.workcell_runtime import WorkcellRuntime
from praxis.backend.services.deck_type_definition import DeckTypeDefinitionService
from praxis.backend.services.discovery_service import DiscoveryService
from praxis.backend.services.machine_type_definition import MachineTypeDefinitionService
from praxis.backend.services.praxis_orm_service import PraxisDBService
from praxis.backend.services.resource_type_definition import ResourceTypeDefinitionService
from praxis.backend.utils.db import (
  KEYCLOAK_DSN_FROM_CONFIG,
  AsyncSessionLocal,
  get_async_db_session,
  init_praxis_db_schema,
)
from praxis.backend.utils.db import (
  async_engine as praxis_async_engine,
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
  """Manage application startup and shutdown events.

  Initialize database connections, services, and the main orchestrator.

  This function is used to set up the application state and ensure that all
  necessary components are ready before the application starts handling requests.

  After the application is done, it will clean up resources such as closing
  database connections and disposing of the SQLAlchemy engine.

  Args:
    app: The FastAPI application instance.

  Yields:
    None.

  Raises:
    Exception: If any error occurs during the startup sequence, it will log the error
    and re-raise the exception to prevent the application from starting.

  """
  db_service_instance: PraxisDBService | None = None
  orchestrator: Orchestrator | None = None
  asset_manager: AssetManager | None = None
  workcell_runtime: WorkcellRuntime | None = None
  discovery_service: DiscoveryService | None = None
  try:
    logger.info("Application startup sequence initiated...")

    logger.info("Initializing Praxis database schema...")
    await init_praxis_db_schema()
    logger.info("Praxis database schema initialization complete.")

    logger.info("Initializing PraxisDBService...")
    assert KEYCLOAK_DSN_FROM_CONFIG, "Keycloak DSN must be configured in praxis.ini"
    db_service_instance = await PraxisDBService.initialize(
      keycloak_dsn=KEYCLOAK_DSN_FROM_CONFIG,
    )
    logger.info("PraxisDBService initialized successfully.")

    # Initialize AssetManager and WorkcellRuntime
    logger.info("Initializing AssetManager and WorkcellRuntime...")
    workcell_runtime = WorkcellRuntime(
      db_session_factory=AsyncSessionLocal,
      config=praxis_config,
    )
    logger.info("WorkcellRuntime initialized successfully.")
    async with AsyncSessionLocal() as db_session: # Use async with for session
      asset_manager = AssetManager(
        db_session=db_session, workcell_runtime=workcell_runtime,
      )

      # Initialize the new type definition services
      logger.info("Initializing type definition services...")
      resource_type_definition_service = ResourceTypeDefinitionService(db_session)
      machine_type_definition_service = MachineTypeDefinitionService(db_session)
      deck_type_definition_service = DeckTypeDefinitionService(db_session)
      logger.info("Type definition services initialized.")

      # Initialize DiscoveryService
      logger.info("Initializing DiscoveryService...")
      discovery_service = DiscoveryService(
        db_session_factory=AsyncSessionLocal,
        resource_type_definition_service=resource_type_definition_service,
        machine_type_definition_service=machine_type_definition_service,
        deck_type_definition_service=deck_type_definition_service,
      )
      logger.info("DiscoveryService initialized.")

      # Run initial discovery and synchronization
      logger.info("Running initial discovery and synchronization...")
      await discovery_service.discover_and_sync_all_definitions(
        protocol_search_paths=praxis_config.all_protocol_source_paths,
      )
      logger.info("Initial discovery and synchronization complete.")

      # Instantiate and initialize the Orchestrator with its dependencies
      logger.info("Initializing orchestrator...")
      orchestrator = Orchestrator(
        db_session_factory=AsyncSessionLocal,
        asset_manager=asset_manager,
        workcell_runtime=workcell_runtime,
      )
      logger.info("Orchestrator dependencies initialized.")

      # Initialize scheduler components (AssetLockManager, ProtocolScheduler)
      logger.info("Initializing scheduler components...")
      await initialize_scheduler_components(AsyncSessionLocal, praxis_config)

      # Store the fully initialized orchestrator and discovery service in the app state
      app.state.orchestrator = orchestrator
      app.state.discovery_service = discovery_service
      logger.info("Orchestrator and DiscoveryService attached to application state.")
      logger.info("Application startup complete.")

      yield  # The application is now running

  except Exception as e:
    logger.exception("Error during application startup: %s", str(e))
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
      logger.exception("Error during application shutdown: %s", str(e))


app = FastAPI(
  title="PyLabPraxis Backend",
  description="A comprehensive Python-based platform to automate and manage laboratory \
    workflows.",
  version="1.0.0",
  lifespan=lifespan,
)

# CORS Middleware Configuration
app.add_middleware(
  CORSMiddleware,
  allow_origins=[
    "http://localhost:5173",
    "http://localhost:4200",  # TODO: ensure this is the correct URL for your frontend
  ],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# --- API Router Inclusion ---
app.include_router(
  function_data_outputs.router, prefix="/api/v1/data-outputs", tags=["Data Outputs"],
)
app.include_router(protocols.router, prefix="/api/v1/protocols", tags=["Protocols"])
app.include_router(workcell_api.router, prefix="/api/v1/workcell", tags=["Workcell"])
app.include_router(resources.router, prefix="/api/v1/assets", tags=["Assets"])
app.include_router(discovery.router, prefix="/api/v1/discovery", tags=["Discovery"])


# --- Middleware and Root Endpoint ---


@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
  """Middleware to log incoming requests and their response status codes."""
  logger.info("Request: %s %s", request.method, request.url.path)
  response: Response = await call_next(request)
  logger.info(
    "Response: %s %s - Status %s",
    request.method,
    request.url.path,
    response.status_code,
  )
  return response


@app.get("/", include_in_schema=False)
async def root_redirect():
  """Redirects the root URL to the static index page."""
  return RedirectResponse(url="/docs")
