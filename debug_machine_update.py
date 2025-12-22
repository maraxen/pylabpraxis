
from praxis.backend.models.enums import AssetType
from praxis.backend.models.pydantic_internals.machine import MachineUpdate


def debug():
    u = MachineUpdate(asset_type=AssetType.MACHINE)
    print(f"MachineUpdate name: {u.name!r}")
    if u.name is None:
        print("Name is None.")
    else:
        print("Name is NOT None.")

if __name__ == "__main__":
    debug()
