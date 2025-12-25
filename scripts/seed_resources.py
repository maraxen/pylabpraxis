#!/usr/bin/env python3
"""Seed script to create sample resources for testing the Protocol Wizard.

This creates basic plates, tip racks, and machines that can be used with
the simple_transfer protocol.
"""

import asyncio
import httpx

BASE_URL = "http://localhost:8000/api/v1"


async def get_definition_by_name_pattern(client: httpx.AsyncClient, pattern: str) -> dict | None:
    """Find a resource definition matching a name pattern."""
    response = await client.get("/resources/definitions", params={"limit": 500})
    if response.status_code != 200:
        print(f"Failed to get definitions: {response.status_code}")
        return None
    
    definitions = response.json()
    for defn in definitions:
        name = defn.get("name", "").lower()
        if pattern.lower() in name:
            return defn
    return None


async def create_resources():
    """Create sample resources via API."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30, follow_redirects=True) as client:
        print("Finding resource definitions...")
        
        # Find a plate definition
        plate_def = await get_definition_by_name_pattern(client, "wellplate")
        if not plate_def:
            plate_def = await get_definition_by_name_pattern(client, "plate")
        
        # Find a tip carrier/rack definition
        tip_def = await get_definition_by_name_pattern(client, "tiprack")
        if not tip_def:
            tip_def = await get_definition_by_name_pattern(client, "tip_car")
        
        print(f"  Plate definition: {plate_def.get('name') if plate_def else 'Not found'}")
        print(f"  Tip definition: {tip_def.get('name') if tip_def else 'Not found'}")
        
        resources_to_create = []
        
        if plate_def:
            resources_to_create.extend([
                {
                    "name": "Source Plate 1 (96-well)",
                    "description": f"Based on {plate_def['name']}",
                    "asset_type": "resource",
                    "resource_definition_accession_id": plate_def["accession_id"],
                },
                {
                    "name": "Destination Plate 1",
                    "description": f"Based on {plate_def['name']}",
                    "asset_type": "resource",
                    "resource_definition_accession_id": plate_def["accession_id"],
                },
                {
                    "name": "Working Plate A",
                    "description": f"General purpose plate - {plate_def['name']}",
                    "asset_type": "resource",
                    "resource_definition_accession_id": plate_def["accession_id"],
                },
            ])
        
        if tip_def:
            resources_to_create.extend([
                {
                    "name": "Tip Rack 1 (300µL)",
                    "description": f"Based on {tip_def['name']}",
                    "asset_type": "resource",
                    "resource_definition_accession_id": tip_def["accession_id"],
                },
                {
                    "name": "Tip Rack 2 (Backup)",
                    "description": f"Backup tips - {tip_def['name']}",
                    "asset_type": "resource",
                    "resource_definition_accession_id": tip_def["accession_id"],
                },
            ])
        
        print(f"\nCreating {len(resources_to_create)} sample resources...")
        
        for resource in resources_to_create:
            try:
                response = await client.post("/resources/", json=resource)
                if response.status_code in (200, 201):
                    data = response.json()
                    print(f"  ✓ Created: {resource['name']} ({data.get('accession_id', 'N/A')})")
                elif response.status_code == 422:
                    print(f"  ⚠ Validation error: {resource['name']} - {response.text[:100]}")
                else:
                    print(f"  ✗ Failed: {resource['name']} - {response.status_code}: {response.text[:100]}")
            except Exception as e:
                print(f"  ✗ Error creating {resource['name']}: {e}")


async def main():
    print("=" * 50)
    print("Seeding PyLabPraxis with sample resources")
    print("=" * 50)
    
    await create_resources()
    
    print("\nDone!")
    print("Refresh the Protocol Wizard to see the new resources.")


if __name__ == "__main__":
    asyncio.run(main())
