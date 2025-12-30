"""REPL API Endpoints."""

import asyncio
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from praxis.backend.core.repl_session import ReplSession
from praxis.backend.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.websocket("/session")
async def repl_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for interactive REPL session."""
    await websocket.accept()
    logger.info("REPL WebSocket connected")

    # Initialize a new session
    # TODO: Inject actual context (LiquidHandler, etc.)
    session = ReplSession(context={"msg": "Hello from Praxis REPL!"})

    try:
        while True:
            data = await websocket.receive_json()
            command_type = data.get("type")
            payload = data.get("payload", {})

            if command_type == "EXEC":
                code = payload.get("code", "")
                
                # Run in thread executor if blocking, but interactive console relies on state
                # For now run synchronously as code.InteractiveConsole is fast for simple steps
                # Long running tasks will block - acceptable for v1
                more, output, error = session.push(code)
                
                response: dict[str, Any] = {
                    "type": "RESULT",
                    "id": data.get("id"),
                    "payload": {
                        "more": more,
                        "output": output,
                    }
                }
                
                # If InteractiveConsole.push caught an exception it prints to stderr (captured in output)
                # If we caught something else, we send ERROR
                if error:
                    response["type"] = "ERROR"
                    response["payload"]["error"] = error
                
                await websocket.send_json(response)

            elif command_type == "COMPLETION":
                text = payload.get("code", "")  # or 'text'
                matches = session.get_completions(text)
                await websocket.send_json({
                    "type": "COMPLETION_RESULT",
                    "id": data.get("id"),
                    "payload": {
                        "matches": matches
                    }
                })

    except WebSocketDisconnect:
        logger.info("REPL WebSocket disconnected")
    except Exception as e:
        logger.error(f"REPL WebSocket error: {e}")
        try:
             await websocket.close(code=1011)
        except:
            pass
