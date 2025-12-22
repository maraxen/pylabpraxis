
from praxis.backend.models.enums import AssetType
from praxis.backend.models.pydantic_internals.deck import DeckUpdate


def debug():
    u = DeckUpdate(asset_type=AssetType.DECK)
    print(f"DeckUpdate name: {u.name!r}")
    if u.name is None:
        print("Name is None.")
    else:
        print("Name is NOT None.")

if __name__ == "__main__":
    debug()
