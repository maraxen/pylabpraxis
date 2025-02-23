import os
import asyncio
from typing import List, Dict, Any, Optional, TypeVar, Type, Generic

import aiofiles
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import importlib.util
from urllib.parse import unquote

import logging

from ..configure import PraxisConfiguration
from ..core.orchestrator import Orchestrator
from ..protocol.protocol import Protocol
from ..utils import db
from .dependencies import get_orchestrator

config = PraxisConfiguration("praxis.ini")
router = APIRouter()
P = TypeVar("P", bound=Protocol)

logging.basicConfig(
    filename=config.log_file,
    level=config.logging_level,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


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


class ProtocolInfo(BaseModel):
    name: str
    path: str
    description: str
    has_assets: Optional[bool] = False
    has_parameters: Optional[bool] = False


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


@router.get("/discover")
async def discover_protocols():
    """Discover available protocol files."""
    try:
        protocols = await db.discover_protocols([config.default_protocol_dir])
        return [ProtocolInfo(**p) for p in protocols]
    except Exception as e:
        logger.error(f"Error discovering protocols: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deck_layouts", response_model=List[str])
async def get_deck_layouts(orchestrator: Orchestrator = Depends(get_orchestrator)):
    """
    Returns a list of available deck layout files.
    """
    deck_files = await orchestrator.deck_manager.get_available_deck_files()
    return deck_files


@router.get("/details")
async def get_protocol_details(protocol_path: str) -> Dict:
    """Get details about a specific protocol using query parameter."""
    logger.info("=== Protocol Details Request ===")
    logger.info(f"Raw protocol path: {protocol_path}")

    try:
        if not protocol_path:
            raise HTTPException(status_code=400, detail="Protocol path is required")

        # Get project root directory (parent of praxis)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        logger.info(f"Project root: {project_root}")

        # Try to find the file in a few different ways
        possible_paths = [
            protocol_path,  # As-is
            os.path.join(project_root, protocol_path),  # Relative to project root
            os.path.join(
                project_root, protocol_path.lstrip("/")
            ),  # Strip leading slash
            os.path.join(
                config.default_protocol_dir, os.path.basename(protocol_path)
            ),  # Just filename in default dir
        ]

        protocol_path = ""
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            logger.info(f"Trying path: {abs_path}")
            if os.path.exists(abs_path):
                protocol_path = abs_path
                break

        if not protocol_path:
            logger.error("Protocol file not found in any of these locations:")
            for path in possible_paths:
                logger.error(f"- {os.path.abspath(path)}")
            raise HTTPException(
                status_code=404,
                detail="Protocol file not found in any of the expected locations",
            )

        logger.info(f"Found protocol at: {protocol_path}")

        # Verify it's within project directory
        if not os.path.commonpath([protocol_path, project_root]) == project_root:
            raise HTTPException(
                status_code=403, detail="Protocol path must be within project directory"
            )

        # Get protocol details from database
        details = await db.get_protocol_details(protocol_path)
        if not details:
            raise HTTPException(status_code=404, detail="Protocol not found")

        # Type safety checks
        expected_fields = {
            "name": str,
            "path": str,
            "description": str,
            "requires_config": bool,
            "parameters": dict,
            "assets": list,
            "has_assets": bool,
            "has_parameters": bool,
        }

        # Validate fields and types
        for field, expected_type in expected_fields.items():
            if field not in details:
                logger.error(f"Missing required field: {field}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Protocol details missing required field: {field}",
                )
            if not isinstance(details[field], expected_type):
                logger.error(
                    f"Invalid type for {field}: expected {expected_type}, got {type(details[field])}"
                )
                raise HTTPException(
                    status_code=500, detail=f"Invalid type for field {field}"
                )

        logger.info(f"Returning validated details: {details}")
        return details

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting protocol details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


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
