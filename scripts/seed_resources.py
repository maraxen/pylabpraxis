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

        # Find a plate definition
        plate_def = await get_definition_by_name_pattern(client, "wellplate")
        if not plate_def:
            plate_def = await get_definition_by_name_pattern(client, "plate")

        # Find a tip carrier/rack definition
        tip_def = await get_definition_by_name_pattern(client, "tiprack")
        if not tip_def:
            tip_def = await get_definition_by_name_pattern(client, "tip_car")


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


        for resource in resources_to_create:
            try:
                response = await client.post("/resources/", json=resource)
                if response.status_code in (200, 201):
                    response.json()
                elif response.status_code == 422:
                    pass
                else:
                    pass
            except Exception:
                pass


async def main():

    await create_resources()



if __name__ == "__main__":
    asyncio.run(main())
