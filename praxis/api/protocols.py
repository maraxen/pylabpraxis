import os
import asyncio
from typing import List, Dict, Any, Optional

import aiofiles
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json

from praxis.core.orchestrator import Orchestrator
from praxis.protocol.protocol import Protocol

router = APIRouter()

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
        raise HTTPException(
            status_code=500, detail="Orchestrator is not initialized"
        )
    return orchestrator

class ProtocolStartRequest(BaseModel):
    protocol_name: str
    config_data: Dict[str, Any]
    deck_file: str
    liquid_handler_name: str
    manual_check_list: Optional[List[str]] = None
    user_info: Optional[Dict[str, Any]] = None

class ProtocolStatus(BaseModel):
    name: str
    status: str

@router.post("/upload_config_file")
async def upload_config_file(file: UploadFile = File(...)):
    """
    Uploads a protocol configuration file.
    """
    try:
        # Ensure the directory exists
        os.makedirs("protocol_configs", exist_ok=True)

        # Save the uploaded file
        file_path = os.path.join("protocol_configs", file.filename)
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()  # Read the file asynchronously
            await out_file.write(content)  # Write the file asynchronously

        return JSONResponse(
            content={"filename": file.filename, "path": file_path}, status_code=200
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error uploading file: {e}"
        )

@router.post("/upload_deck_file")
async def upload_deck_file(file: UploadFile = File(...)):
    """
    Uploads a deck layout file.
    """
    try:
        # Ensure the directory exists
        os.makedirs("deck_layouts", exist_ok=True)

        # Save the uploaded file
        file_path = os.path.join("deck_layouts", file.filename)
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()  # Read the file asynchronously
            await out_file.write(content)  # Write the file asynchronously

        return JSONResponse(
            content={"filename": file.filename, "path": file_path}, status_code=200
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error uploading file: {e}"
        )

@router.get("/deck_layouts", response_model=List[str])
async def get_deck_layouts(orchestrator: Orchestrator = Depends(get_orchestrator)):
    """
    Returns a list of available deck layout files.
    """
    deck_files = orchestrator.deck_manager.get_available_deck_files()
    return deck_files

@router.get("/", response_model=List[str])
async def list_protocols(orchestrator: Orchestrator = Depends(get_orchestrator)):
    """Lists all available protocols."""
    return list(orchestrator.protocols.keys())

@router.post("/start", response_model=ProtocolStatus)
async def start_protocol(
    protocol_name: str = Form(...),
    config_file: UploadFile = File(...),
    deck_file: UploadFile = File(...),
    liquid_handler_name: str = Form(...),
    manual_check_list: Optional[List[str]] = Form(None),
    orchestrator: Orchestrator = Depends(get_orchestrator),
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
        user_info = {}  # You can modify this to fetch actual user info if needed

        protocol = orchestrator.create_protocol(
            protocol_config_data,
            temp_deck_path,
            liquid_handler_name,
            manual_check_list,
            user_info,
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
    protocol_name: str, command: str, orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Sends a command to a running protocol."""
    try:
        orchestrator.send_command(protocol_name, command)
        return {
            "message": f"Command '{command}' sent to protocol '{protocol_name}'"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))