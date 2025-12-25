
import asyncio
import httpx
import sys

async def check_queue():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/api/v1/protocols/runs/queue")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_queue())
