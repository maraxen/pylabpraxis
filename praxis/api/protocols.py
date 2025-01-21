import os
import asyncio
import hashlib
from typing import List, Dict, Any, Optional, TypeVar, Type, Generic
import inspect
import logging

import aiofiles
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import importlib.util
import traceback

from praxis.configure import PraxisConfiguration
from praxis.core.orchestrator import Orchestrator
from praxis.protocol.protocol import Protocol
from praxis.protocol.parameter import ProtocolParameters
from praxis.api.auth import get_current_active_user, get_current_user

# Set up logging
# Create logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "protocol_discovery.log")

# Get logger for this module
logger = logging.getLogger("praxis.api.protocols")
logger.setLevel(logging.DEBUG)

# Create handlers
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler(log_file, mode="a")

# Create formatters and add it to handlers
log_format = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
console_handler.setFormatter(log_format)
file_handler.setFormatter(log_format)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Prevent the logger from propagating to the root logger
logger.propagate = False

# Test logging
logger.info("Protocol API module initialized")
logger.debug("Debug logging is enabled")

# Initialize router and configuration
print("\nInitializing protocol router...")
router = APIRouter()
config = PraxisConfiguration("praxis.ini")
orchestrator = Orchestrator(config)  # Initialize the Orchestrator instance
P = TypeVar("P", bound=Protocol)


# Dependency to get the Orchestrator instance
def get_orchestrator() -> Orchestrator:
    """
    FastAPI dependency to provide the Orchestrator instance to API endpoints.

    Replace this with your actual way of getting the Orchestrator instance.
    For example, you might use a global variable, a dependency injection
    framework, or a singleton pattern to manage the Orchestrator instance.
    """
    global orchestrator  # Access the global orchestrator instance (for now)

    if orchestrator is None:
        raise HTTPException(status_code=500, detail="Orchestrator is not initialized")
    return orchestrator


class ProtocolStartRequest(BaseModel, Generic[P]):
    protocol_class: Type[P]
    protocol_name: str
    config_data: Dict[str, Any]
    deck_file: str
    liquid_handler_name: str
    manual_check_list: Optional[List[str]] = None
    user_info: Optional[Dict[str, Any]] = None
    kwargs: Optional[Dict[str, Any]] = None


class ProtocolStatus(BaseModel):
    name: str
    status: str


class ProtocolDirectories(BaseModel):
    directories: List[str]


@router.post("/upload_config_file")
async def upload_config_file(file: UploadFile = File(...)):
    """
    Uploads a protocol configuration file.
    """
    try:
        # Ensure the directory exists
        os.makedirs("protocol_configs", exist_ok=True)

        # Save the uploaded file
        if file.filename is None:
            raise HTTPException(status_code=400, detail="No file selected")
        if not file.filename.endswith(".json"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Please upload a JSON file.",
            )
        if not isinstance(file.filename, str):
            raise HTTPException(
                status_code=400, detail="Invalid file name. Please upload a JSON file."
            )
        file_path = os.path.join("protocol_configs", file.filename)
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()  # Read the file asynchronously
            await out_file.write(content)  # Write the file asynchronously

        return JSONResponse(
            content={"filename": file.filename, "path": file_path}, status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")


@router.post("/upload_deck_file")
async def upload_deck_file(file: UploadFile = File(...)):
    """
    Uploads a deck layout file.
    """
    try:
        # Ensure the directory exists
        os.makedirs("deck_layouts", exist_ok=True)

        # Save the uploaded file
        if file.filename is None:
            raise HTTPException(status_code=400, detail="No file selected")
        if not file.filename.endswith(".json"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Please upload a JSON file.",
            )
        if not isinstance(file.filename, str):
            raise HTTPException(
                status_code=400, detail="Invalid file name. Please upload a JSON file."
            )

        # Save the uploaded file
        file_path = os.path.join("deck_layouts", file.filename)
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()  # Read the file asynchronously
            await out_file.write(content)  # Write the file asynchronously

        return JSONResponse(
            content={"filename": file.filename, "path": file_path}, status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")


@router.get("/deck_layouts", response_model=List[str])
async def get_deck_layouts(orchestrator: Orchestrator = Depends(get_orchestrator)):
    """Returns a list of available deck layout files."""
    try:
        deck_dir = config.deck_management.get("deck_directory", "./deck_layouts")
        if not os.path.exists(deck_dir):
            os.makedirs(deck_dir)

        # Create a test deck file if none exist
        if not any(f.endswith(".json") for f in os.listdir(deck_dir)):
            test_deck = {
                "name": "Test Deck",
                "description": "A test deck layout",
                "resources": [],
            }
            test_deck_path = os.path.join(deck_dir, "test_deck.json")
            async with aiofiles.open(test_deck_path, "w") as f:
                await f.write(json.dumps(test_deck, indent=2))

        # Get all JSON files in the deck directory
        deck_files = [f for f in os.listdir(deck_dir) if f.endswith(".json")]
        return deck_files
    except Exception as e:
        print(f"Error getting deck files: {str(e)}")
        print(f"Error traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get deck files: {str(e)}"
        )


@router.get("/", response_model=List[str])
async def list_protocols(orchestrator: Orchestrator = Depends(get_orchestrator)):
    """Lists all available protocols."""
    return list(orchestrator.protocols.keys())


@router.post("/start", response_model=ProtocolStatus)
async def start_protocol(
    protocol_class: Type[P] = Form(...),
    protocol_name: str = Form(...),
    config_file: UploadFile = File(...),
    deck_file: UploadFile = File(...),
    liquid_handler_name: str = Form(...),
    manual_check_list: Optional[List[str]] = Form(None),
    orchestrator: Orchestrator = Depends(get_orchestrator),
    **kwargs: Any,
):
    """Starts a new protocol instance."""
    try:
        # Save config file temporarily and load config data
        temp_config_path = f"temp_config_{config_file.filename}"
        async with aiofiles.open(temp_config_path, "wb") as temp_config:
            content = await config_file.read()
            await temp_config.write(content)

        with open(temp_config_path, "r") as f:
            protocol_config_data = json.load(f)

        # Save deck file temporarily
        temp_deck_path = f"temp_deck_{deck_file.filename}"
        async with aiofiles.open(temp_deck_path, "wb") as temp_deck:
            content = await deck_file.read()
            await temp_deck.write(content)

        # Get user info (currently, it's an empty dictionary)
        user_info = config.get_lab_users().get_user_info("admin")

        protocol = await orchestrator.create_protocol(
            protocol_class,
            protocol_config_data,
            temp_deck_path,
            manual_check_list or [],  # Provide empty list as default if None
            user_info,
            **kwargs,
        )
        asyncio.create_task(orchestrator.run_protocol(protocol.name))
        return ProtocolStatus(name=protocol.name, status=protocol.status)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        # Clean up temporary files
        if os.path.exists(temp_config_path):
            os.remove(temp_config_path)
        if os.path.exists(temp_deck_path):
            os.remove(temp_deck_path)


# Protocol discovery endpoints (register these before the {protocol_name} endpoint)
@router.get("/settings", response_model=Dict[str, Any], name="get_settings")
async def get_settings():
    """Get application settings."""
    try:
        print("\nHandling GET /settings request...")
        # Get protocol directories
        directories = []

        # Add default directory
        if os.path.exists(config.default_protocol_dir):
            print(f"Adding default protocol directory: {config.default_protocol_dir}")
            directories.append(config.default_protocol_dir)

        # Add additional directories from config
        additional_dirs = config.get_protocol_directories()
        print(f"Found additional directories in config: {additional_dirs}")
        for directory in additional_dirs:
            if directory and os.path.exists(directory):
                print(f"Adding additional directory: {directory}")
                directories.append(directory)

        # Scan directories for protocol files
        protocol_files = []
        for directory in directories:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(".py") and file != "__init__.py":
                        protocol_files.append(os.path.join(root, file))
        print(f"Found protocol files: {protocol_files}")

        response = {
            "default_protocol_dir": config.default_protocol_dir,
            "protocol_directories": directories,
            "protocol_files": protocol_files,
            "user_settings": {
                "username": "debug_user",
                "is_admin": True,
            },
        }
        print(f"Returning settings response: {response}")
        return response
    except Exception as e:
        print(f"Error in get_settings: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Error traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to get settings: {str(e)}")


@router.get(
    "/protocol_directories", response_model=List[str], name="get_protocol_directories"
)
async def get_protocol_directories():
    """Get list of directories where protocols are searched for."""
    try:
        print("\nHandling GET /protocol_directories request...")
        directories = []

        # Add default directory
        if os.path.exists(config.default_protocol_dir):
            print(f"Adding default protocol directory: {config.default_protocol_dir}")
            directories.append(config.default_protocol_dir)

        # Add additional directories from config
        for directory in config.get_protocol_directories():
            if directory and os.path.exists(directory):
                print(f"Adding additional directory: {directory}")
                directories.append(directory)

        print(f"Returning directories response: {directories}")
        return directories
    except Exception as e:
        print(f"Error in get_protocol_directories: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Error traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get directories: {str(e)}"
        )


def get_protocol_hash(protocol_class: Type[Protocol]) -> str:
    """Generate a hash of the protocol class based on its source code."""
    try:
        source = inspect.getsource(protocol_class)
        return hashlib.md5(source.encode()).hexdigest()
    except (TypeError, OSError):
        # If we can't get the source code, use the class name as fallback
        return hashlib.md5(protocol_class.__name__.encode()).hexdigest()


@router.post(
    "/discover", response_model=List[Dict[str, Any]], name="discover_protocols"
)
async def discover_protocols(
    dirs: ProtocolDirectories, current_user: Dict = Depends(get_current_active_user)
):
    """Discover protocols in the specified directories."""
    try:
        logger.info("\nHandling POST /discover request...")
        protocols: Dict[str, Dict[str, Any]] = (
            {}
        )  # Dict to store protocols, keyed by name
        init_protocols: Dict[str, Dict[str, Any]] = (
            {}
        )  # Store protocols from __init__.py files separately

        # Add default directory to the list if not already included
        directories = list(dirs.directories)
        if config.default_protocol_dir not in directories:
            logger.info(
                f"Adding default protocol directory: {config.default_protocol_dir}"
            )
            directories.append(config.default_protocol_dir)

        logger.info(f"Scanning directories: {directories}")
        for directory in directories:
            logger.info(f"Scanning directory: {directory}")
            for root, _, files in os.walk(directory):
                logger.debug(f"Walking directory: {root}")
                logger.debug(f"Found files: {files}")

                # First pass: process non-init files
                for file in files:
                    if file.endswith(".py") and file != "__init__.py":
                        try:
                            filepath = os.path.join(root, file)
                            logger.info(f"Loading protocol from: {filepath}")
                            spec = importlib.util.spec_from_file_location(
                                file[:-3], filepath
                            )
                            if spec is None:
                                logger.warning(f"Could not load spec for {filepath}")
                                continue

                            module = importlib.util.module_from_spec(spec)
                            if spec.loader is None:
                                logger.warning(f"Could not load module for {filepath}")
                                continue
                            spec.loader.exec_module(module)

                            # Look for Protocol subclasses
                            logger.debug(f"Looking for Protocol subclasses in {file}")
                            for item in dir(module):
                                obj = getattr(module, item)
                                try:
                                    if (
                                        isinstance(obj, type)
                                        and issubclass(obj, Protocol)
                                        and obj != Protocol
                                    ):
                                        logger.info(f"Found protocol: {obj.__name__}")

                                        logger.debug(
                                            "Looking for ProtocolParameters in the same module"
                                        )
                                        baseline_params = None
                                        for item in dir(module):
                                            param_obj = getattr(module, item)
                                            try:
                                                if isinstance(
                                                    param_obj, ProtocolParameters
                                                ):
                                                    logger.info(
                                                        f"Found ProtocolParameters instance: {param_obj}"
                                                    )
                                                    baseline_params = param_obj
                                                    break
                                            except Exception as e:
                                                logger.error(
                                                    f"Error loading protocol from {file}: {e}"
                                                )
                                                logger.error(f"Error type: {type(e)}")
                                                logger.error(
                                                    f"Error traceback: {traceback.format_exc()}"
                                                )

                                        if baseline_params is None:
                                            logger.warning(
                                                "No ProtocolParameters instance found"
                                            )
                                            params_for_ui = []
                                        else:
                                            params_for_ui = (
                                                baseline_params.get_parameters_for_ui()
                                            )
                                            logger.info(
                                                f"Params for UI: {params_for_ui}"
                                            )

                                        protocol_info = {
                                            "name": obj.__name__,
                                            "file": filepath,
                                            "description": obj.__doc__
                                            or "No description available",
                                            "parameters": params_for_ui,
                                            "config_fields": {
                                                "name": "",
                                                "details": "",
                                                "description": "",
                                                "machines": [],
                                                "liquid_handler_ids": [],
                                                "users": [],
                                                "directory": "",
                                                "deck": "",
                                                "needed_deck_resources": {},
                                                "other_args": {},
                                            },
                                        }

                                        protocols[obj.__name__] = protocol_info

                                except TypeError:
                                    continue
                        except Exception as e:
                            logger.error(f"Error loading protocol from {file}: {e}")
                            logger.error(f"Error type: {type(e)}")
                            logger.error(f"Error traceback: {traceback.format_exc()}")

        # Combine protocols and parameters, with direct imports taking precedence
        all_protocols = {**init_protocols, **protocols}
        logger.info(f"\nFinal protocols with parameters:")
        for name, protocol in all_protocols.items():
            logger.info(f"\n{name}:")
            logger.info(f"Parameters: {protocol.get('parameters', {})}")

        protocol_list = list(all_protocols.values())
        logger.info(f"\nReturning discovered protocols: {protocol_list}")
        return protocol_list
    except Exception as e:
        logger.error(f"Error in discover_protocols: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail=f"Failed to discover protocols: {str(e)}"
        )


@router.delete("/directories/{directory_path:path}")
async def remove_protocol_directory(
    directory_path: str, current_user: Dict = Depends(get_current_active_user)
):
    """Remove a protocol directory from the search paths."""
    if directory_path == config.default_protocol_dir:
        raise HTTPException(
            status_code=400, detail="Cannot remove default protocol directory"
        )

    try:
        config.remove_protocol_directory(directory_path)
        return {"status": "success", "message": f"Removed directory: {directory_path}"}
    except Exception as e:
        print(f"Error in remove_protocol_directory: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Failed to remove directory: {str(e)}"
        )


@router.get("/assets", response_model=List[Dict[str, Any]])
async def get_assets(current_user: Dict = Depends(get_current_active_user)):
    """Returns a list of available assets (machines and liquid handlers)."""
    try:
        # Get the asset database path from config
        asset_db = config.asset_db
        if not os.path.exists(os.path.dirname(asset_db)):
            os.makedirs(os.path.dirname(asset_db))

        # Create default assets if file doesn't exist or is empty
        if not os.path.exists(asset_db) or os.path.getsize(asset_db) == 0:
            default_assets = [
                {
                    "id": "lh1",
                    "name": "Liquid Handler 1",
                    "type": "liquid_handler",
                    "description": "Default liquid handler",
                },
                {
                    "id": "m1",
                    "name": "Machine 1",
                    "type": "machine",
                    "description": "Default machine",
                },
            ]
            async with aiofiles.open(asset_db, "w") as f:
                await f.write(json.dumps(default_assets, indent=2))
            return default_assets

        # Read and return assets from file
        async with aiofiles.open(asset_db, "r") as f:
            content = await f.read()
            return json.loads(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get assets: {str(e)}")


@router.get("/users", response_model=List[Dict[str, Any]])
async def get_users(current_user: Dict = Depends(get_current_active_user)):
    """Returns a list of available users."""
    try:
        print("\nHandling GET /users request...")
        print(f"Current user: {current_user}")

        # Get the users file path from config
        users_file = config.users
        print(f"Users file path: {users_file}")

        if not os.path.exists(os.path.dirname(users_file)):
            print(f"Creating directory: {os.path.dirname(users_file)}")
            os.makedirs(os.path.dirname(users_file))

        # Read users from file and convert to list format
        print("Reading users from file...")
        async with aiofiles.open(users_file, "r") as f:
            content = await f.read()
            print(f"File content: {content}")

            try:
                users_dict = json.loads(content)
                print(f"Parsed users: {users_dict}")

                # Convert users to list format, handling missing fields
                users_list = []
                for username, user_data in users_dict.items():
                    user_info = {
                        "username": username,
                        "display_name": user_data.get(
                            "display_name", username
                        ),  # Default to username
                        "is_admin": (
                            True
                            if username == "admin"
                            else user_data.get("is_admin", False)
                        ),  # Default admin user
                    }
                    users_list.append(user_info)

                print(f"Returning users list: {users_list}")
                return users_list
            except json.JSONDecodeError as je:
                print(f"JSON decode error: {je}")
                raise HTTPException(
                    status_code=500, detail=f"Invalid users file format: {str(je)}"
                )
    except Exception as e:
        print(f"Error getting users: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Error traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")


# Protocol management endpoints (register these after the discovery endpoints)
@router.get("/{protocol_name}", response_model=ProtocolStatus)
async def get_protocol_status(
    protocol_name: str, orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Gets the status of a specific protocol."""
    protocol = orchestrator.get_protocol(protocol_name)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    return ProtocolStatus(name=protocol.name, status=protocol.status)


@router.post("/{protocol_name}/command")
async def send_command(
    protocol_name: str,
    command: str,
    orchestrator: Orchestrator = Depends(get_orchestrator),
):
    """Sends a command to a running protocol."""
    try:
        orchestrator.send_command(protocol_name, command)
        return {"message": f"Command '{command}' sent to protocol '{protocol_name}'"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/validate_name/{protocol_name}")
async def validate_protocol_name(
    protocol_name: str, orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """
    Validates if a protocol name is available.
    """
    try:
        # Check if protocol exists in registry
        exists = await orchestrator.registry.protocol_exists(protocol_name)
        return {"valid": not exists}
    except Exception as e:
        print(f"Error validating protocol name: {str(e)}")
        print(f"Error traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail=f"Failed to validate protocol name: {str(e)}"
        )


# Initial protocol discovery
async def initialize_protocols():
    """Perform initial protocol discovery during startup."""
    logger.info("Performing initial protocol discovery...")
    try:
        # Get default and configured directories
        directories = [config.default_protocol_dir]
        directories.extend(config.get_protocol_directories())

        # Create ProtocolDirectories instance
        dirs = ProtocolDirectories(directories=directories)

        # Discover protocols
        protocols = await discover_protocols(
            dirs, {"username": "system", "is_admin": True}
        )
        logger.info(f"Initially discovered {len(protocols)} protocols")
        return protocols
    except Exception as e:
        logger.error(f"Error during initial protocol discovery: {e}")
        logger.error(traceback.format_exc())
        return []


print("Protocol endpoints registered\n")
