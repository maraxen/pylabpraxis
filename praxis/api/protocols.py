import os
import asyncio
from typing import List, Dict, Any, Optional, TypeVar, Type, Generic

import aiofiles
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import importlib.util

from ..configure import PraxisConfiguration
from ..core.orchestrator import Orchestrator
from ..protocol.protocol import Protocol
from ..utils import db
from .dependencies import get_orchestrator

config = PraxisConfiguration("praxis.ini")
router = APIRouter()
P = TypeVar("P", bound=Protocol)


class ProtocolStartRequest(BaseModel, Generic[P]):
    protocol_class: Type[P]
    config_data: Dict[str, Any]
    kwargs: Optional[Dict[str, Any]] = None


class ProtocolStatus(BaseModel):
    name: str
    status: str


class ProtocolDirectories(BaseModel):
    directories: List[str]


class ProtocolPrepareRequest(BaseModel):
    protocol_path: str
    parameters: Optional[Dict[str, Any]] = None
    asset_assignments: Optional[Dict[str, str]] = None


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
    """
    Returns a list of available deck layout files.
    """
    deck_files = await orchestrator.deck_manager.get_available_deck_files()
    return deck_files


@router.get("/", response_model=List[str])
async def list_protocols(orchestrator: Orchestrator = Depends(get_orchestrator)):
    """Lists all available protocols."""
    return list(orchestrator.protocols.keys())


@router.post("/prepare", response_model=Dict[str, Any])
async def prepare_protocol(
    request: ProtocolPrepareRequest,
    orchestrator: Orchestrator = Depends(get_orchestrator),
) -> Dict[str, Any]:
    """Prepare a protocol by loading its requirements and matching assets."""
    try:
        # Get protocol details
        details = await db.get_protocol_details(request.protocol_path)
        if not details:
            raise HTTPException(status_code=404, detail="Protocol not found")

        # Load and validate parameters
        parameters = request.parameters or {}
        if details["parameters"]:
            # Validate against schema
            try:
                validated_params = details["parameters"].validate(parameters)
            except ValueError as e:
                raise HTTPException(
                    status_code=400, detail=f"Invalid parameters: {str(e)}"
                )

        # Match assets
        required_assets = details["assets"]
        if required_assets:
            if request.asset_assignments:
                # Verify assigned assets are valid
                for name, asset_id in request.asset_assignments.items():
                    if name not in required_assets:
                        raise HTTPException(
                            status_code=400, detail=f"Unknown asset requirement: {name}"
                        )
                    asset = await db.get_asset(asset_id)
                    if not asset:
                        raise HTTPException(
                            status_code=400, detail=f"Asset not found: {asset_id}"
                        )
            else:
                # Get asset suggestions
                asset_matches = await orchestrator.match_assets_to_requirements(
                    {
                        "protocol_name": details["name"],
                        "required_assets": required_assets.to_dict(),
                        "parameters": validated_params,
                    }
                )

        # Construct configuration
        config = {
            "name": details["name"],
            "parameters": validated_params,
            "required_assets": request.asset_assignments or {},
            "protocol_path": request.protocol_path,
        }

        # Validate complete configuration
        validation = await orchestrator.validate_configuration(config)
        if not validation["valid"]:
            return {
                "status": "invalid",
                "errors": validation["errors"],
                "config": config,
            }

        return {
            "status": "ready",
            "config": validation["validated_config"],
            "asset_suggestions": (
                asset_matches if not request.asset_assignments else None
            ),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to prepare protocol: {str(e)}"
        )


@router.post("/start", response_model=ProtocolStatus)
async def start_protocol(
    config: Dict[str, Any], orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Start a protocol with a validated configuration."""
    try:
        # Final validation
        validation = await orchestrator.validate_configuration(config)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["errors"])

        # Create and start protocol
        protocol = await orchestrator.create_protocol(
            config["protocol_path"], validation["validated_config"]
        )

        await orchestrator.run_protocol(protocol.name)
        return ProtocolStatus(name=protocol.name, status=protocol.status)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start protocol: {str(e)}"
        )


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


@router.post("/discover")
async def discover_protocols(
    dirs: ProtocolDirectories,
):
    protocols = []

    # Add default directory to the list if not already included
    directories = list(dirs.directories)
    if (
        config.default_protocol_dir not in directories
    ):  # Use config instead of imported constant
        directories.append(config.default_protocol_dir)

    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    try:
                        filepath = os.path.join(root, file)
                        spec = importlib.util.spec_from_file_location(
                            file[:-3], filepath
                        )
                        if spec is None:
                            continue
                        module = importlib.util.module_from_spec(spec)
                        if spec.loader is None:
                            continue
                        spec.loader.exec_module(module)

                        # Look for Protocol subclasses
                        for item in dir(module):
                            obj = getattr(module, item)
                            if (
                                isinstance(obj, type)
                                and issubclass(obj, Protocol)
                                and obj != Protocol
                            ):
                                protocols.append(
                                    {
                                        "name": obj.__name__,
                                        "file": filepath,
                                        "description": obj.__doc__
                                        or "No description available",
                                    }
                                )
                    except Exception as e:
                        print(f"Error loading protocol from {file}: {e}")

    return protocols


"""@router.get("/settings")
async def get_settings() -> Dict[str, Any]:
    """ "Get application settings." """
    try:
        # Get protocol directories
        directories = []
        if os.path.exists(config.default_protocol_dir):
            directories.append(config.default_protocol_dir)

        additional_dirs = [d for d in config.get_protocol_directories() if d]
        directories.extend(additional_dirs)

        return {
            "default_protocol_dir": config.default_protocol_dir,
            "protocol_directories": directories,
            "user_settings": {
                "username": current_user["username"],
                "is_admin": current_user.get("is_admin", False),
            },
        }
    except Exception as e:
        print(f"Error in get_settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get settings: {str(e)}")"""


"""@router.get("/directories")
async def get_protocol_directories() -> Dict:
    """ "Get list of directories where protocols are searched for." """
    try:
        directories = []
        if os.path.exists(config.default_protocol_dir):
            directories.append(config.default_protocol_dir)

        for directory in await orchestrator.get_protocol_directories():
            if directory and os.path.exists(directory):
                directories.append(directory)

        return directories
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get directories: {str(e)}"
        )
""

@router.delete("/directories/{directory_path:path}")
async def remove_protocol_directory(
    directory_path: str,
):
    """ "Remove a protocol directory from the search paths." """
    if directory_path == config.default_protocol_dir:
        raise HTTPException(
            status_code=400, detail="Cannot remove default protocol directory"
        )

    try:
        config.remove_protocol_directory(directory_path)
        return {"status": "success", "message": f"Removed directory: {directory_path}"}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to remove directory: {str(e)}"
        )
"""


@router.get("/protocol/{protocol_path:path}")
async def get_protocol_details(
    protocol_path: str,
) -> Dict:
    """Get details about a specific protocol."""
    details = await db.get_protocol_details(protocol_path)
    return details
