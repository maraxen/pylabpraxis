
import asyncio
import contextlib

import httpx


async def check_queue():
    async with httpx.AsyncClient() as client:
        with contextlib.suppress(Exception):
            await client.get("http://localhost:8000/api/v1/protocols/runs/queue")

if __name__ == "__main__":
    asyncio.run(check_queue())
