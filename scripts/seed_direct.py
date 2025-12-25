import asyncio
import sys
from uuid import uuid4

# Add project root to path
sys.path.append(".")

from praxis.backend.utils.db import get_async_db_session
from praxis.backend.models.enums import AssetType, ResourceStatusEnum, MachineStatusEnum
from sqlalchemy import select
from praxis.backend.models.orm.resource import ResourceDefinitionOrm, ResourceOrm
from praxis.backend.models.orm.machine import MachineOrm

async def seed_direct():
    print("Starting direct seed (ORM mode)...")
    async for db in get_async_db_session():
        try:
            # Find definitions
            stmt = select(ResourceDefinitionOrm).limit(100)
            result = await db.execute(stmt)
            defs = result.scalars().all()
            
            plate_def = next((d for d in defs if "plate" in d.name.lower() and "carrier" not in d.name.lower()), None)
            tip_def = next((d for d in defs if "tip" in d.name.lower() and "rack" in d.name.lower()), None)
            if not tip_def:
                 tip_def = next((d for d in defs if "tip" in d.name.lower()), None)
            
            print(f"Found plate def: {plate_def.name if plate_def else 'None'}")
            print(f"Found tip def: {tip_def.name if tip_def else 'None'}")
            
            if not plate_def:
                print("No plate definition found. Cannot seed plates.")
                return

            async def create_res_orm(name, desc, def_id):
                # Check if exists
                stmt = select(ResourceOrm).filter_by(name=name)
                res = await db.execute(stmt)
                if res.scalar_one_or_none():
                    print(f"  ⚠ Skipped (exists): {name}")
                    return

                new_res = ResourceOrm(
                    name=name,
                    asset_type=AssetType.RESOURCE,
                    resource_definition_accession_id=def_id,
                    status=ResourceStatusEnum.AVAILABLE_IN_STORAGE,
                    location=None,
                    status_details=desc
                )
                db.add(new_res)
                try:
                    await db.commit()
                    await db.refresh(new_res)
                    print(f"  ✓ Created: {new_res.name} ({new_res.accession_id})")
                except Exception as e:
                    await db.rollback()
                    print(f"  ✗ Failed {name}: {e}")

            # Create Plates
            await create_res_orm("Source Plate 1", "Seeded source plate (96-well)", plate_def.accession_id)
            await create_res_orm("Dest Plate 1", "Seeded destination plate (96-well)", plate_def.accession_id)
            
            # Create Tips
            if tip_def:
               await create_res_orm("Tip Rack 300uL", "Seeded tip rack", tip_def.accession_id)
            
            # Create Machine
            stmt = select(MachineOrm).filter_by(name="Hamilton STARlet")
            res = await db.execute(stmt)
            if res.scalar_one_or_none():
                 print(f"  ⚠ Skipped Machine (exists)")
            else:
                mach = MachineOrm(
                    name="Hamilton STARlet",
                    asset_type=AssetType.MACHINE,
                    status=MachineStatusEnum.AVAILABLE,
                )
                db.add(mach)
                try:
                    await db.commit()
                    print(f"  ✓ Created Machine: {mach.name}")
                except Exception as e:
                    await db.rollback()
                    print(f"  ✗ Failed Machine: {e}")

        except Exception as e:
            print("CRITICAL ERROR:")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(seed_direct())
