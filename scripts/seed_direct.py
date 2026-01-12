import asyncio
import sys

# Add project root to path
sys.path.append(".")

from sqlalchemy import select

from praxis.backend.models.enums import AssetType, MachineStatusEnum, ResourceStatusEnum
from praxis.backend.models.domain.machine import Machine
from praxis.backend.models.domain.resource import Resource, ResourceDefinition
from praxis.backend.utils.db import get_async_db_session


async def seed_direct():
    async for db in get_async_db_session():
        try:
            # Find definitions
            stmt = select(ResourceDefinition).limit(100)
            result = await db.execute(stmt)
            defs = result.scalars().all()

            plate_def = next((d for d in defs if "plate" in d.name.lower() and "carrier" not in d.name.lower()), None)
            tip_def = next((d for d in defs if "tip" in d.name.lower() and "rack" in d.name.lower()), None)
            if not tip_def:
                 tip_def = next((d for d in defs if "tip" in d.name.lower()), None)


            if not plate_def:
                return

            async def create_res_model(name, desc, def_id):
                # Check if exists
                stmt = select(Resource).filter_by(name=name)
                res = await db.execute(stmt)
                if res.scalar_one_or_none():
                    return

                new_res = Resource(
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
                except Exception:
                    await db.rollback()

            # Create Plates
            await create_res_model("Source Plate 1", "Seeded source plate (96-well)", plate_def.accession_id)
            await create_res_model("Dest Plate 1", "Seeded destination plate (96-well)", plate_def.accession_id)

            # Create Tips
            if tip_def:
               await create_res_model("Tip Rack 300uL", "Seeded tip rack", tip_def.accession_id)

            # Create Machine
            stmt = select(Machine).filter_by(name="Hamilton STARlet")
            res = await db.execute(stmt)
            if res.scalar_one_or_none():
                 pass
            else:
                mach = Machine(
                    name="Hamilton STARlet",
                    asset_type=AssetType.MACHINE,
                    status=MachineStatusEnum.AVAILABLE,
                )
                db.add(mach)
                try:
                    await db.commit()
                except Exception:
                    await db.rollback()

        except Exception:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(seed_direct())
