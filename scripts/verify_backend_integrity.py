
import asyncio
import sys
from httpx import AsyncClient

BASE_URL = "http://localhost:8000"

async def check_endpoint(client, path):
    try:
        response = await client.get(path, timeout=5.0)
        print(f"GET {path}: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  Response type: {type(data)}")
                if isinstance(data, list):
                    print(f"  Item count: {len(data)}")
                elif isinstance(data, dict):
                    print(f"  Keys: {list(data.keys())}")
                return True
            except Exception as e:
                print(f"  Failed to parse JSON: {e}")
        else:
            print(f"  Error response: {response.text[:200]}")
    except Exception as e:
        print(f"  Request failed: {e}")
    return False

async def main():
    async with AsyncClient(base_url=BASE_URL) as client:
        print("Starting Smoke Tests...")
        
        # 1. Protocols
        protocols_ok = await check_endpoint(client, "/api/v1/protocols")
        
        # 2. Machines
        machines_ok = await check_endpoint(client, "/api/v1/machines")
        
        if protocols_ok and machines_ok:
            print("\nSUCCESS: All smoke tests passed.")
            sys.exit(0)
        else:
            print("\nFAILURE: Some smoke tests failed.")
            sys.exit(1)

if __name__ == "__main__":
    try:
        import uvloop
        uvloop.install()
    except ImportError:
        pass
    asyncio.run(main())
