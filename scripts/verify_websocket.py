import asyncio
import json
import logging
import uuid

import websockets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ws_client")

async def test_websocket():
    # Generate a random run ID (it might fail lookup but should connect)
    run_id = str(uuid.uuid4())
    uri = f"ws://localhost:8000/api/v1/ws/execution/{run_id}"

    logger.info(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Connected!")

            # Listen for messages
            try:
                while True:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    logger.info(f"Received: {data}")

                    if data.get("type") in ["complete", "error"]:
                        break
            except asyncio.TimeoutError:
                logger.info("No message received for 5 seconds (expected if polling finds nothing/error)")

    except Exception as e:
        logger.error(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
