
from praxis.backend.models.enums import AssetType
from praxis.backend.models.pydantic_internals.machine import MachineUpdate


def debug():
    u = MachineUpdate(asset_type=AssetType.MACHINE)
    if u.name is None:
        pass
    else:
        pass

if __name__ == "__main__":
    debug()
