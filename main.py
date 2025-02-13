import asyncio
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette.responses import RedirectResponse
import os

from praxis.api import protocols, assets, workcell_api
from praxis.core.orchestrator import Orchestrator
from praxis.configure import PraxisConfiguration
from praxis.utils.db import db

# Global instances
config = PraxisConfiguration("praxis.ini")
orchestrator = Orchestrator(config)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for application startup/shutdown."""
    try:
        # Startup
        print("Starting application initialization...")
        print(f"Default protocol directory: {config.default_protocol_dir}")

        # Initialize orchestrator and attach to app state
        await orchestrator.initialize_dependencies()
        app.state.orchestrator = orchestrator
        print("Successfully initialized dependencies")

        yield

    except Exception as e:
        print(f"Error during startup: {str(e)}")
        raise

    finally:
        # Shutdown
        print("Starting application shutdown...")
        try:
            if orchestrator.db:
                await orchestrator.db.close()
            print("Successfully closed database connections")
        except Exception as e:
            print(f"Error during shutdown: {str(e)}")


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

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def redirect_to_index():
    """Redirect root to frontend."""
    return RedirectResponse(url="/static/index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
