# <filename>praxis/backend/api/protocols.py</filename>
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

import aiofiles
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, status
from fastapi.responses import JSONResponse
import importlib.util
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.configure import PraxisConfiguration
from praxis.backend.core.orchestrator import Orchestrator
from praxis.backend.api.dependencies import get_orchestrator, get_db
from praxis.backend.services import protocol_data_service
from ..services.praxis_orm_service import PraxisDBService
from praxis.backend.models import (
  FunctionProtocolDefinitionOrm,
  ProtocolInfo,
  ProtocolParameters,
)

from ..interfaces import (
  WorkcellAssetsInterface,
)  # Keep for type hint if used by orchestrator


config = PraxisConfiguration("praxis.ini")
router = APIRouter()


logging.basicConfig(
  filename=config.log_file,
  level=config.logging_level,
  format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Helper to get PraxisDBService instance (similar to assets.py)
async def get_praxis_db_service() -> PraxisDBService:
  keycloak_dsn = None  # Or get from config
  return await PraxisDBService.initialize(keycloak_dsn=keycloak_dsn)


@router.post("/upload_config_file")
async def upload_config_file(file: UploadFile = File(...)):
  try:
    os.makedirs("protocol_configs", exist_ok=True)
    if file.filename is None:
      raise HTTPException(status_code=400, detail="No file selected")
    if not file.filename.endswith(".json"):
      raise HTTPException(status_code=400, detail="Invalid file format. JSON only.")
    file_path = os.path.join("protocol_configs", file.filename)
    async with aiofiles.open(file_path, "wb") as out_file:
      content = await file.read()
      await out_file.write(content)
    return JSONResponse(
      content={"filename": file.filename, "path": file_path}, status_code=200
    )
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")


@router.post("/upload_deck_file")
async def upload_deck_file(file: UploadFile = File(...)):
  try:
    os.makedirs("deck_layouts", exist_ok=True)
    if file.filename is None:
      raise HTTPException(status_code=400, detail="No file selected")
    if not file.filename.endswith(".json"):
      raise HTTPException(status_code=400, detail="Invalid file format. JSON only.")
    file_path = os.path.join("deck_layouts", file.filename)
    async with aiofiles.open(file_path, "wb") as out_file:
      content = await file.read()
      await out_file.write(content)
    return JSONResponse(
      content={"filename": file.filename, "path": file_path}, status_code=200
    )
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")


@router.get("/discover", response_model=List[ProtocolInfo])
async def discover_protocols(db: AsyncSession = Depends(get_db)):
  """Discover available top-level protocol definitions from the database."""
  try:
    # Fetch top-level protocol definitions from the database
    # Assuming you want only top-level protocols to be "discovered" initially
    definitions_orm: List[
      FunctionProtocolDefinitionOrm
    ] = await protocol_data_service.list_protocol_definitions(
      db, is_top_level=True, include_deprecated=False
    )

    discovered_protocols = []
    for def_orm in definitions_orm:
      # The path might need adjustment if a relative path from project root is expected
      # def_orm.source_file_path is likely absolute or relative to a source root
      path_to_report = def_orm.source_file_path or "N/A"
      if def_orm.source_repository:
        path_to_report = (
          f"git:{def_orm.source_repository.name}/{def_orm.source_file_path}"
        )
      elif def_orm.file_system_source:
        path_to_report = (
          f"fs:{def_orm.file_system_source.name}/{def_orm.source_file_path}"
        )

      protocol_info = ProtocolInfo(
        protocol_definition_id=def_orm.id,
        name=def_orm.name or "Unnamed Protocol",
        path=path_to_report,
        description=def_orm.description or "No description.",
        has_assets=bool(def_orm.assets),
        has_parameters=bool(def_orm.parameters),
        version=def_orm.version,
      )
      discovered_protocols.append(protocol_info)
    return discovered_protocols
  except Exception as e:
    logger.error(f"Error discovering protocols from database: {e}", exc_info=True)
    raise HTTPException(
      status_code=500, detail=f"Failed to discover protocols: {str(e)}"
    )


@router.get("/deck_layouts", response_model=List[str])
async def get_deck_layouts(orchestrator: Orchestrator = Depends(get_orchestrator)):
  deck_files = await orchestrator.deck_manager.get_available_deck_files()
  return deck_files


@router.get(
  "/details", response_model=Dict
)  # Keep Dict for now, but could be a Pydantic model
async def get_protocol_details(
  protocol_definition_id: Optional[int] = None,  # Added to fetch by ID
  protocol_path: Optional[
    str
  ] = None,  # Kept for compatibility if needed, but ID is preferred
  db: AsyncSession = Depends(get_db),  # Added db session
) -> Dict:
  logger.info("=== Protocol Details Request ===")
  if not protocol_definition_id and not protocol_path:
    raise HTTPException(
      status_code=400, detail="protocol_definition_id or protocol_path is required."
    )

  try:
    def_orm: Optional[FunctionProtocolDefinitionOrm] = None
    if protocol_definition_id:
      def_orm = await protocol_data_service.get_protocol_definition(
        db, protocol_definition_id
      )
      if not def_orm:
        raise HTTPException(
          status_code=404,
          detail=f"Protocol definition with ID {protocol_definition_id} not found.",
        )
      protocol_path_for_module = (
        def_orm.source_file_path
      )  # Needed for module import if still used
    elif protocol_path:  # Legacy path-based loading, try to find in DB first
      # This part is complex: mapping a raw path back to a DB entry reliably is hard.
      # Best effort: search by name and path fragment if possible.
      # For now, prioritize ID-based loading. If path is given, try to load module directly
      # and extract, but this bypasses some DB benefits.
      logger.warning(
        "Fetching protocol details by path is less reliable; prefer protocol_definition_id."
      )
      protocol_module = await import_protocol_module(
        protocol_path
      )  # protocol_path here is the raw path
      if not protocol_module:
        raise HTTPException(
          status_code=404, detail=f"Protocol module not found at path: {protocol_path}"
        )
      details = await get_protocol_details_from_module(
        protocol_module, protocol_path
      )  # protocol_path is raw
      return details  # Bypasses DB Orm for details if only path given

    if not def_orm or not def_orm.source_file_path:
      raise HTTPException(
        status_code=404,
        detail="Protocol definition or its source path not found in DB.",
      )

    # Option 1: Reconstruct details from ORM (preferred)
    details = {
      "protocol_definition_id": def_orm.id,
      "name": def_orm.name,
      "path": def_orm.source_file_path,  # Or a more user-friendly representation
      "version": def_orm.version,
      "description": def_orm.description or "No documentation found.",
      "parameters": {
        p.name: {
          "type": _map_python_type_to_frontend(
            p.actual_type_str or p.type_hint_str or "unknown"
          ),
          "required": not p.optional,
          "default": p.default_value_repr,  # This might need parsing if it's a repr
          "description": p.description or "",
          "constraints": p.constraints_json or {},
        }
        for p in def_orm.parameters
      },
      "assets": [
        {
          "name": a.name,
          "type": a.actual_type_str or a.type_hint_str or "unknown",
          "description": a.description or "",
          "required": not a.optional,
        }
        for a in def_orm.assets
      ],
      "has_assets": bool(def_orm.assets),
      "has_parameters": bool(def_orm.parameters),
      # "requires_config" logic might need adjustment based on ORM fields
      "requires_config": not (bool(def_orm.parameters) or bool(def_orm.assets)),
      "module_name": def_orm.module_name,
      "function_name": def_orm.function_name,
      "category": def_orm.category,
      "tags": def_orm.tags.get("values") if def_orm.tags else [],
    }
    logger.info(f"Returning validated details from ORM: {details}")
    return details

  except HTTPException as e:
    raise e
  except Exception as e:
    logger.error(f"Error getting protocol details: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail=str(e))


async def get_protocol_details_from_module(
  protocol_module: Any,
  protocol_path: str,  # protocol_path is raw file path
) -> Dict:
  # This function is mostly for path-based loading if DB is not used.
  # It should ideally be deprecated in favor of ORM-based detail construction.
  baseline_parameters = getattr(protocol_module, "baseline_parameters", {})
  required_assets = getattr(protocol_module, "required_assets", {})

  if isinstance(baseline_parameters, ProtocolParameters):
    baseline_parameters = baseline_parameters.serialize()
  if isinstance(required_assets, WorkcellAssetsInterface):
    required_assets = required_assets.serialize()

  if not isinstance(baseline_parameters, dict):
    baseline_parameters = {}
  if not isinstance(required_assets, dict):
    required_assets = {}

  parameters: dict[str, Any] = {}
  # ... (parameter parsing logic from original file) ...
  for name, config in baseline_parameters.items():
    param_type = config.get("type", str)
    param_type_name = getattr(param_type, "__name__", str(param_type))
    constraints = config.get("constraints", {}).copy()
    # (constraint type mapping logic from original file)
    parameters[name] = {
      "type": _map_python_type_to_frontend(param_type_name),
      "required": config.get("required", False),
      "default": config.get("default"),
      "description": config.get("description", ""),
      "constraints": constraints,
    }

  assets = []
  for name, config in required_assets.items():
    asset_type = config.get("type", str)
    assets.append(
      {
        "name": name,
        "type": getattr(asset_type, "__name__", str(asset_type)),
        "description": config.get("description", ""),
        "required": config.get("required", True),
      }
    )

  return {
    "name": getattr(protocol_module, "__name__", Path(protocol_path).stem),
    "path": protocol_path,  # Original file path
    "description": getattr(protocol_module, "__doc__", "No documentation found"),
    "parameters": parameters,
    "assets": assets,
    "has_assets": bool(assets),
    "has_parameters": bool(parameters),
    "requires_config": not (bool(parameters) or bool(assets)),
  }


def _map_python_type_to_frontend(python_type: str) -> str:
  type_name = python_type.lower()
  mapping = {
    "str": "string",
    "int": "integer",
    "float": "float",
    "bool": "boolean",
    "list": "array",
    "dict": "dict",
    "<class 'str'>": "string",
    "<class 'int'>": "integer",
    "<class 'float'>": "float",
    "<class 'bool'>": "boolean",
    "<class 'list'>": "array",
    "<class 'dict'>": "dict",
  }
  return mapping.get(type_name, "string")  # Default to string


async def import_protocol_module(protocol_raw_path: str) -> Optional[Any]:
  # This function assumes protocol_raw_path is a resolvable file path
  try:
    logger.info(f"Attempting to import module from raw path: {protocol_raw_path}")
    # Ensure path is absolute for spec_from_file_location
    abs_path = Path(protocol_raw_path).resolve()
    if not abs_path.exists():
      logger.error(f"Protocol file not found at absolute path: {abs_path}")
      # Try relative to project root as a fallback if it's a relative-like path
      project_root = Path(__file__).resolve().parent.parent.parent
      abs_path = (project_root / protocol_raw_path).resolve()
      if not abs_path.exists():
        logger.error(
          f"Protocol file also not found relative to project root: {abs_path}"
        )
        return None

    logger.info(f"Using module path for import: {abs_path}")
    module_name = abs_path.stem
    spec = importlib.util.spec_from_file_location(module_name, str(abs_path))
    if spec is None or spec.loader is None:
      logger.error(f"Could not create spec for {abs_path}")
      return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
  except Exception as e:
    logger.error(
      f"Error importing protocol module from path '{protocol_raw_path}': {e}",
      exc_info=True,
    )
    return None


@router.get("/schema")
async def get_protocol_schema(
  protocol_definition_id: Optional[int] = None,
  protocol_path: Optional[str] = None,  # Kept for legacy, prefer ID
  db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
  try:
    def_orm: Optional[FunctionProtocolDefinitionOrm] = None
    protocol_name = "UnknownProtocol"
    protocol_description = "No description."
    parameters_obj = ProtocolParameters()  # Default empty

    if protocol_definition_id:
      def_orm = await protocol_data_service.get_protocol_definition(
        db, protocol_definition_id
      )
      if not def_orm:
        raise HTTPException(
          status_code=404,
          detail=f"Protocol definition ID {protocol_definition_id} not found.",
        )
      protocol_name = def_orm.name or protocol_name
      protocol_description = def_orm.description or protocol_description
      # Reconstruct ProtocolParameters object from ORM if schema generation needs it
      # This part might be complex if ProtocolParameters has rich internal structure
      # For now, assume parameters_to_jsonschema can work with a list of param dicts
      # or we adapt it. The original `get_protocol_details` already formats params.

      # Simplified: if parameters_to_jsonschema can take the ORM's parameter list directly or via a simple model
      # For now, let's assume we need to load the module to get the original ProtocolParameters instance
      if def_orm.source_file_path:
        protocol_module = await import_protocol_module(def_orm.source_file_path)
        if protocol_module:
          parameters_obj = getattr(
            protocol_module, "baseline_parameters", ProtocolParameters()
          )
        else:
          logger.warning(
            f"Could not load module for schema from {def_orm.source_file_path}"
          )
      else:
        logger.warning(
          f"No source_file_path for def ID {protocol_definition_id} to load module for schema."
        )

    elif protocol_path:  # Legacy
      logger.warning(
        "Fetching schema by path is less reliable; prefer protocol_definition_id."
      )
      protocol_module = await import_protocol_module(protocol_path)
      if not protocol_module:
        raise HTTPException(
          status_code=404, detail="Protocol module not found for schema generation."
        )
      parameters_obj = getattr(
        protocol_module, "baseline_parameters", ProtocolParameters()
      )
      protocol_name = getattr(protocol_module, "__name__", Path(protocol_path).stem)
      protocol_description = getattr(protocol_module, "__doc__", protocol_description)
    else:
      raise HTTPException(
        status_code=400, detail="protocol_definition_id or protocol_path is required."
      )

    if not isinstance(parameters_obj, ProtocolParameters):
      # If it's already a dict from somewhere, try to make it work or raise error
      # This case should be rare if loading from module
      logger.error(
        f"Loaded baseline_parameters is not a ProtocolParameters instance. Type: {type(parameters_obj)}"
      )
      raise HTTPException(
        status_code=500,
        detail="Internal error: Could not load protocol parameters correctly for schema.",
      )

    schema = parameters_to_jsonschema(
      parameters_obj,
      protocol_name=protocol_name,
      protocol_description=protocol_description,
    )
    return schema
  except HTTPException:
    raise
  except Exception as e:
    logger.error(f"Error generating protocol schema: {e}", exc_info=True)
    raise HTTPException(
      status_code=500, detail=f"Error generating protocol schema: {str(e)}"
    )


@router.get("/", response_model=List[str])  # This might change to List[ProtocolInfo]
async def list_protocols(orchestrator: Orchestrator = Depends(get_orchestrator)):
  # This endpoint lists names of protocols known to the orchestrator.
  # If orchestrator's list comes from DB discovery, it's indirectly updated.
  # No direct old_db_api usage here.
  return list(orchestrator.protocols.keys())


@router.post("/prepare", response_model=Dict[str, Any])
async def prepare_protocol(
  request: ProtocolPrepareRequest,  # request.protocol_path is a raw path
  orchestrator: Orchestrator = Depends(get_orchestrator),
  db_service: PraxisDBService = Depends(get_praxis_db_service),  # For asset lookup
  db: AsyncSession = Depends(get_db),  # For protocol def lookup
) -> Dict[str, Any]:
  try:
    # Step 1: Get protocol details. Prefer finding definition in DB.
    # This is tricky because request.protocol_path is a raw file path.
    # We need to map this path to a FunctionProtocolDefinitionOrm if possible,
    # or fall back to module loading.
    details: Optional[Dict[str, Any]] = None
    def_orm: Optional[FunctionProtocolDefinitionOrm] = None

    # Try to find by path in DB (this is a simplification, real matching might be harder)
    # A more robust way would be to require protocol_definition_id in ProtocolPrepareRequest
    possible_def = await db.execute(
      select(FunctionProtocolDefinitionOrm).filter(
        FunctionProtocolDefinitionOrm.source_file_path.like(
          f"%{Path(request.protocol_path).name}"
        )
      )
    )
    def_orm_candidate = possible_def.scalars().first()

    if (
      def_orm_candidate and def_orm_candidate.source_file_path
    ):  # Check if path matches somewhat
      # Use the get_protocol_details logic that constructs from ORM
      temp_details = await get_protocol_details(
        protocol_definition_id=def_orm_candidate.id, db=db
      )
      if (
        temp_details.get("path") == request.protocol_path
        or Path(temp_details.get("path", "")).name == Path(request.protocol_path).name
      ):
        details = temp_details
        def_orm = def_orm_candidate  # Found a match

    if not details:  # Fallback to raw path loading
      logger.warning(
        f"Could not find exact DB match for path {request.protocol_path}, falling back to module loading for details."
      )
      protocol_module = await import_protocol_module(request.protocol_path)
      if not protocol_module:
        raise HTTPException(
          status_code=404,
          detail=f"Protocol module not found at path: {request.protocol_path}",
        )
      details = await get_protocol_details_from_module(
        protocol_module, request.protocol_path
      )

    if not details:  # Should not happen if module loading works
      raise HTTPException(
        status_code=404, detail="Protocol details could not be determined."
      )

    parameters = request.parameters or {}
    # Parameter validation/coercion logic (from original file)
    if details.get("parameters"):
      for param_name, param_config in details["parameters"].items():
        if param_name in parameters:
          param_type_frontend = param_config.get("type", "string")
          if param_type_frontend == "number" or param_type_frontend == "integer":
            try:
              value = float(parameters[param_name])
              if (
                param_config.get("constraints", {}).get("integer_only")
                or param_type_frontend == "integer"
              ):
                value = round(value)
              parameters[param_name] = value
            except (ValueError, TypeError):
              raise HTTPException(f"Invalid number for {param_name}")
    validated_params = parameters  # Placeholder for actual validation

    # Match assets
    required_assets_list = details.get("assets", [])  # This is now a list of dicts
    asset_suggestions = None  # Initialize

    if required_assets_list:
      if (
        request.asset_assignments
      ):  # Keys are asset requirement names, values are asset instance names/IDs
        # Verify assigned assets exist and are suitable (simplified here)
        for (
          req_asset_name,
          assigned_asset_identifier,
        ) in request.asset_assignments.items():
          # Check if assigned_asset_identifier is a valid asset in the DB
          # The old code used `db.get_asset(asset_id)`. asset_id was a string name.
          # This should query the generic 'assets' table if that's what it referred to.
          asset_query = """
                        SELECT name, type, metadata, is_available FROM assets WHERE name = $1
                    """
          # Parameters for PraxisDBService SQL methods should be Dict[str, Any] like {"1": value1, "2": value2}
          asset_data = await db_service.fetch_one_sql(
            asset_query, params={"1": assigned_asset_identifier}
          )
          if not asset_data:
            raise HTTPException(
              status_code=400,
              detail=f"Assigned asset '{assigned_asset_identifier}' for requirement '{req_asset_name}' not found.",
            )
          # Further type checking against requirement could be added here.
      else:  # No assignments, try to get suggestions (orchestrator logic)
        # Orchestrator expects `required_assets` as Dict[str, Dict]
        required_assets_dict_for_orchestrator = {
          asset_req["name"]: {
            "type": asset_req["type"],
            "description": asset_req["description"],
            "required": asset_req["required"],
            # Add other fields if orchestrator.match_assets_to_requirements expects them
          }
          for asset_req in required_assets_list
        }
        asset_suggestions = await orchestrator.match_assets_to_requirements(
          {
            "protocol_name": details["name"],
            "required_assets": required_assets_dict_for_orchestrator,
            "parameters": validated_params,
          }
        )

    protocol_id_to_use = def_orm.id if def_orm else None  # For configuration

    config_to_validate = {
      "protocol_definition_id": protocol_id_to_use,  # For orchestrator if it uses ID
      "protocol_path": request.protocol_path,  # Keep original path for now
      "name": details["name"],
      "parameters": validated_params,
      "required_assets": request.asset_assignments
      or {},  # Asset requirement name -> instance name
    }

    validation = await orchestrator.validate_configuration(config_to_validate)
    if not validation["valid"]:
      return {
        "status": "invalid",
        "errors": validation["errors"],
        "config": config_to_validate,
      }

    return {
      "status": "ready",
      "config": validation["validated_config"],
      "asset_suggestions": asset_suggestions,
    }

  except HTTPException:
    raise
  except Exception as e:
    logger.error(f"Failed to prepare protocol: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail=f"Failed to prepare protocol: {str(e)}")


@router.post("/start", response_model=ProtocolStatus)
async def start_protocol(
  config_payload: Dict[
    str, Any
  ],  # Changed from 'config' to avoid conflict with 'config' module
  orchestrator: Orchestrator = Depends(get_orchestrator),
):
  try:
    # 'config_payload' is the validated configuration from /prepare
    # It should contain 'protocol_definition_id' or 'protocol_path'
    validation = await orchestrator.validate_configuration(config_payload)
    if not validation["valid"]:
      raise HTTPException(status_code=400, detail=validation["errors"])

    protocol = await orchestrator.create_protocol(
      validation["validated_config"]  # Pass the whole validated config
    )
    await orchestrator.run_protocol(protocol.name)
    return ProtocolStatus(
      name=protocol.name, status=str(protocol.status)
    )  # Ensure status is string
  except Exception as e:
    logger.error(f"Failed to start protocol: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail=f"Failed to start protocol: {str(e)}")


@router.get("/{protocol_name}", response_model=ProtocolStatus)
async def get_protocol_status(
  protocol_name: str, orchestrator: Orchestrator = Depends(get_orchestrator)
):
  protocol = orchestrator.get_protocol(protocol_name)
  if not protocol:
    raise HTTPException(status_code=404, detail="Protocol not found")
  return ProtocolStatus(
    name=protocol.name, status=str(protocol.status)
  )  # Ensure status is string


@router.post("/{run_guid}/command")
async def send_control_command_to_run(run_guid: str, command: str):
  from praxis.backend.utils.run_control import (
    send_control_command as send_control_command_to_redis,
    ALLOWED_COMMANDS,
  )

  cmd_upper = command.upper()
  if cmd_upper not in ALLOWED_COMMANDS:
    raise HTTPException(
      status_code=400, detail=f"Invalid command. Allowed: {ALLOWED_COMMANDS}"
    )
  try:
    success = send_control_command_to_redis(run_guid, cmd_upper)
    if success:
      return {"message": f"Command '{cmd_upper}' sent."}
    else:
      raise HTTPException(status_code=500, detail="Failed to send command via Redis.")
  except Exception as e:
    logger.error(f"Error sending command to run '{run_guid}': {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Unexpected error sending command.")
