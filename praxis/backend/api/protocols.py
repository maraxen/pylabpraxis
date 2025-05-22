import os
import asyncio
from pathlib import Path
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
from ..interfaces import WorkcellAssetsInterface
from ..protocol.parameter import ProtocolParameters
from ..protocol.jsonschema_utils import parameters_to_jsonschema
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
async def get_protocol_details(
    protocol_path: str, orchestrator: Orchestrator = Depends(get_orchestrator)
) -> Dict:
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

        protocol_module = await import_protocol_module(protocol_path)
        if not protocol_module:
            raise HTTPException(status_code=404, detail="Protocol not found")

        details = await get_protocol_details_from_module(protocol_module, protocol_path)

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

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting protocol details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def get_protocol_details_from_module(
    protocol_module: Any, protocol_path: str
) -> Dict:
    """Extract protocol details from a loaded module."""
    baseline_parameters = getattr(protocol_module, "baseline_parameters", {})
    required_assets = getattr(protocol_module, "required_assets", {})

    # Handle serialization if needed
    if isinstance(baseline_parameters, ProtocolParameters):
        baseline_parameters = baseline_parameters.serialize()
    if isinstance(required_assets, WorkcellAssetsInterface):
        required_assets = required_assets.serialize()

    # Ensure we have dictionaries
    if not isinstance(baseline_parameters, dict):
        baseline_parameters = {}
    if not isinstance(required_assets, dict):
        required_assets = {}

    # Convert parameters to frontend format
    parameters: dict[str, Any] = {}
    for name, config in baseline_parameters.items():
        param_type = config.get("type", str)
        param_type_name = (
            param_type.__name__ if hasattr(param_type, "__name__") else str(param_type)
        )

        # Create a copy of constraints and convert Python types to strings recursively
        constraints = config.get("constraints", {}).copy()

        # Process nested key_constraints and value_constraints
        for constraint_key in ["key_constraints", "value_constraints"]:
            if constraint_key in constraints:
                nested_constraints = constraints[constraint_key].copy()
                for key, value in nested_constraints.items():
                    if key == "type" and hasattr(value, "__name__"):
                        nested_constraints[key] = _map_python_type_to_frontend(
                            value.__name__
                        )
                    elif isinstance(value, type):  # Handle other type references
                        nested_constraints[key] = value.__name__.lower()
                    elif key == "subvariables" and isinstance(value, dict):
                        # Iterate through subvariables and convert their types to strings
                        for subvar_name, subvar_config in value.items():
                            if "type" in subvar_config:
                                subvar_type = subvar_config["type"]
                                if hasattr(subvar_type, "__name__"):
                                    subvar_config["type"] = subvar_type.__name__
                                else:
                                    subvar_config["type"] = str(subvar_type)
                constraints[constraint_key] = nested_constraints

        parameters[name] = {
            "type": _map_python_type_to_frontend(param_type_name),
            "required": config.get("required", False),
            "default": config.get("default"),
            "description": config.get("description", ""),
            "constraints": constraints,
        }

    # Convert assets to list format
    assets = []
    for name, config in required_assets.items():
        asset_type = config.get("type", str)
        assets.append(
            {
                "name": name,
                "type": (
                    asset_type.__name__
                    if hasattr(asset_type, "__name__")
                    else str(asset_type)
                ),
                "description": config.get("description", ""),
                "required": config.get("required", True),
            }
        )

    details: Dict[str, Any] = {
        "name": getattr(protocol_module, "__name__", ""),
        "path": protocol_path,
        "description": getattr(protocol_module, "__doc__", "No documentation found"),
        "parameters": parameters,  # Using frontend-expected key name
        "assets": assets,
        "has_assets": bool(assets),
        "has_parameters": bool(parameters),
        "requires_config": not (bool(parameters) or bool(assets)),
    }
    return details


def _map_python_type_to_frontend(python_type: str) -> str:
    """Map Python type names to frontend type names."""
    # First normalize the type name
    type_name = python_type.lower()

    # Handle class references
    if type_name == "<class 'str'>":
        type_name = "str"
    elif type_name == "<class 'int'>":
        type_name = "int"
    elif type_name == "<class 'float'>":
        type_name = "float"
    elif type_name == "<class 'bool'>":
        type_name = "bool"
    elif type_name == "<class 'list'>":
        type_name = "list"
    elif type_name == "<class 'dict'>":
        type_name = "dict"

    # Map normalized types to frontend types
    type_mapping = {
        "str": "string",
        "int": "integer",
        "float": "float",
        "bool": "boolean",
        "list": "array",
        "dict": "dict",
    }

    return type_mapping.get(type_name, "string")


async def import_protocol_module(protocol_path: str) -> Optional[Any]:
    """Import a protocol module from its file path."""
    try:
        logger.info("=== Protocol Details Request ===")
        logger.info(f"Raw protocol path: {protocol_path}")

        # Get absolute path relative to project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        logger.info(f"Project root: {project_root}")

        full_path = os.path.join(project_root, protocol_path)
        full_path = os.path.abspath(full_path)
        logger.info(f"Trying path: {full_path}")

        if os.path.exists(full_path):
            logger.info(f"Found protocol at: {full_path}")
            spec = importlib.util.spec_from_file_location(
                Path(protocol_path).stem, full_path
            )
            if spec is None or spec.loader is None:
                logger.error(f"Could not create spec for {full_path}")
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module

        else:
            logger.error(f"Protocol file not found at {full_path}")
            return None

    except Exception as e:
        logger.error(f"Error importing protocol module: {e}", exc_info=True)
        return None


@router.get("/schema")
async def get_protocol_schema(
    protocol_path: str, orchestrator: Orchestrator = Depends(get_orchestrator)
) -> Dict[str, Any]:
    """Get JSONSchema for a protocol's parameters.

    Args:
        protocol_path: Path to the protocol file
    Returns:
        JSONSchema dictionary for the protocol's parameters
    """
    try:
        # Get protocol details (reusing existing function)
        details = await get_protocol_details(protocol_path, orchestrator)
        if not details:
            raise HTTPException(status_code=404, detail="Protocol not found")

        # Get the ProtocolParameters from the module
        protocol_module = await import_protocol_module(protocol_path)
        if not protocol_module:
            raise HTTPException(status_code=404, detail="Protocol module not found")

        parameters = getattr(protocol_module, "baseline_parameters", None)
        if not parameters or not isinstance(parameters, ProtocolParameters):
            parameters = ProtocolParameters()

        # Generate JSONSchema
        schema = parameters_to_jsonschema(
            parameters,
            protocol_name=details["name"],
            protocol_description=details["description"],
        )

        return schema

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating protocol schema: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error generating protocol schema: {str(e)}"
        )


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
        details = await get_protocol_details_from_module(
            await import_protocol_module(request.protocol_path), request.protocol_path
        )
        if not details:
            raise HTTPException(status_code=404, detail="Protocol not found")

        # Load and validate parameters
        parameters = request.parameters or {}
        if details["parameters"]:
            # Add type coercion for numbers based on constraints
            for param_name, param_config in details["parameters"].items():
                if param_name in parameters:
                    if (
                        param_config["type"] == "number"
                        or param_config["type"] == "integer"
                    ):
                        try:
                            value = float(parameters[param_name])
                            # If integer_only is specified, round the value
                            if param_config.get("constraints", {}).get("integer_only"):
                                value = round(value)
                            parameters[param_name] = value
                        except (ValueError, TypeError):
                            raise HTTPException(
                                status_code=400,
                                detail=f"Invalid number format for parameter: {param_name}",
                            )

        # Validate parameters
        validated_params = details["parameters"]  # TODO: validate parameters

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
