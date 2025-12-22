import asyncio
import uuid
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from praxis.backend.core.orchestrator import Orchestrator

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/execution/{run_id}")
async def websocket_endpoint(websocket: WebSocket, run_id: str):
    await websocket.accept()
    logger.info(f"WebSocket connected for run_id: {run_id}")

    try:
        run_uuid = uuid.UUID(run_id)
        orchestrator: Orchestrator = websocket.app.state.orchestrator

        # Polling loop
        last_status = None
        last_log_count = 0

        while True:
            # Fetch current status
            try:
                # get_protocol_run_status returns a dict with keys like 'status', 'progress', 'logs', etc.
                status_info = await orchestrator.protocol_run_service.get_protocol_run_status(run_uuid)

                # Prepare message payload
                current_status = status_info.get("status")
                current_progress = status_info.get("progress", 0)
                all_logs = status_info.get("logs", [])

                # 1. Send Status Update if changed
                if current_status != last_status:
                    await websocket.send_json({
                        "type": "status",
                        "payload": {
                            "status": current_status,
                            "step": status_info.get("current_step_name", "Initializing") # Assuming this field exists or similar
                        },
                        "timestamp": str(asyncio.get_event_loop().time()) # Placeholder timestamp
                    })
                    last_status = current_status

                # 2. Send Progress Update (every time or if changed? let's send if changed or active)
                # To minimize traffic, maybe only if changed
                # For now, let's send periodic progress
                await websocket.send_json({
                    "type": "progress",
                    "payload": {
                        "progress": current_progress
                    },
                    "timestamp": str(asyncio.get_event_loop().time())
                })

                # 3. Send New Logs
                if len(all_logs) > last_log_count:
                    new_logs = all_logs[last_log_count:]
                    for log_entry in new_logs:
                        # log_entry might be a dict or string, assuming string for simple implementation based on service
                        msg = log_entry if isinstance(log_entry, str) else str(log_entry)
                        await websocket.send_json({
                            "type": "log",
                            "payload": {
                                "message": msg,
                                "level": "INFO"
                            },
                            "timestamp": str(asyncio.get_event_loop().time())
                        })
                    last_log_count = len(all_logs)

                # 4. Check for completion or failure to close connection
                if current_status in ["COMPLETED", "FAILED", "CANCELLED"]:
                    # Send final complete/error message
                    if current_status == "COMPLETED":
                        await websocket.send_json({
                            "type": "complete",
                            "timestamp": str(asyncio.get_event_loop().time())
                        })
                    elif current_status == "FAILED":
                         await websocket.send_json({
                            "type": "error",
                            "payload": {"error": "Protocol execution failed"},
                            "timestamp": str(asyncio.get_event_loop().time())
                        })

                    # Break loop to close connection
                    break

            except Exception as e:
                logger.error(f"Error polling status for {run_id}: {e}")
                # Don't break immediately, maybe transient error?
                # But if ID is invalid, it will keep failing.
                # For now, let's wait and retry.

            # Poll interval
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for run_id: {run_id}")
    except ValueError:
        logger.error(f"Invalid UUID provided: {run_id}")
        await websocket.close(code=1003)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close(code=1011)
        except:
            pass
