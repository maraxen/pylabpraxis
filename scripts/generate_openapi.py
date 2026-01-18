#!/usr/bin/env python3
"""
Generate OpenAPI specification JSON from the FastAPI application.
This script initializes the FastAPI app in browser mode (to avoid DB connections)
and exports the OpenAPI schema to a JSON file.
"""

import json
import logging
import os
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Set environment variables to ensure clean startup without external dependencies
os.environ["STORAGE_BACKEND"] = "memory"
os.environ["PRAXIS_DB_DSN"] = "sqlite+aiosqlite:///:memory:"

# Patch the PraxisConfiguration class to avoid log file issues before importing main
import praxis.backend.configure as cfg

# Create a new property that returns /dev/null
type.__setattr__(cfg.PraxisConfiguration, "log_file", property(lambda self: "/dev/null"))

# Setup basic logging to console before app import
logging.basicConfig(
  level=logging.WARNING,
  format="%(levelname)s: %(message)s",
  handlers=[logging.StreamHandler()],
  force=True,
)

try:
  from praxis.backend.main import app

  print("Successfully imported FastAPI app.")
except ImportError as e:
  print(f"Error importing app: {e}")
  sys.exit(1)
except Exception as e:
  print(f"Error initializing app: {e}")
  sys.exit(1)


def generate_openapi_json():
  """Generate OpenAPI JSON and save it to the web client assets."""
  destination_dir = project_root / "praxis" / "web-client" / "src" / "assets" / "api"
  destination_file = destination_dir / "openapi.json"

  print(f"Ensuring directory exists: {destination_dir}")
  destination_dir.mkdir(parents=True, exist_ok=True)

  print("Generating OpenAPI schema...")
  openapi_schema = app.openapi()

  print(f"Writing schema to: {destination_file}")
  with open(destination_file, "w") as f:
    json.dump(openapi_schema, f, indent=2)

  print("Done.")


if __name__ == "__main__":
  generate_openapi_json()
