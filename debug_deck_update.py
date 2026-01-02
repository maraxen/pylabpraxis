
from praxis.backend.models.enums import AssetType
from praxis.backend.models.pydantic_internals.deck import DeckUpdate


def debug():
    u = DeckUpdate(asset_type=AssetType.DECK)
    if u.name is None:
        pass
    else:
        pass

if __name__ == "__main__":
    debug()
