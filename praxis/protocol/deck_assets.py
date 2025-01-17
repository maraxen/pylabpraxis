from typing import Dict, Type, Optional, Any, Union, Mapping
from dataclasses import dataclass
from pylabrobot.resources import Resource, Deck
from pylabrobot.machines import Machine

# Define a type alias for asset types
AssetType = Type[Union[Resource, Machine]]


@dataclass
class DeckAssetSpec:
    """Specification for a required deck asset (resource or machine).

    Attributes:
        name: Name of the asset on the deck
        type: Expected type of the asset (Resource or Machine)
        description: Optional description of what this asset is used for
        required: Whether this asset is required (defaults to True)
    """

    name: str
    type: AssetType
    description: Optional[str] = None
    required: bool = True


class DeckAssets:
    """Container for deck asset specifications and validation logic.

    This class handles both physical resources (plates, tips, etc.) and machines
    (liquid handlers, plate readers, etc.) that are part of the deck setup.
    """

    def __init__(
        self,
        assets: Optional[Mapping[str, Union[AssetType, Dict[str, Any]]]] = None,
    ):
        """Initialize deck assets.

        Args:
            assets: Optional mapping of asset names to either:
                   - Asset type (e.g., {"plate": Plate} or {"reader": PlateReader})
                   - Asset spec dict (e.g., {"plate": {"type": Plate, "description": "Sample plate"}})
        """
        self._assets: Dict[str, DeckAssetSpec] = {}
        if assets:
            self.load_from_dict(assets)

    def load_from_dict(
        self, assets: Mapping[str, Union[AssetType, Dict[str, Any]]]
    ) -> None:
        """Load assets from a dictionary.

        Args:
            assets: Mapping of asset names to either:
                   - Asset type (e.g., {"plate": Plate} or {"reader": PlateReader})
                   - Asset spec dict (e.g., {"plate": {"type": Plate, "description": "Sample plate"}})
        """
        for name, spec in assets.items():
            if isinstance(spec, type) and (issubclass(spec, (Resource, Machine))):
                self.add(name, spec)
            elif isinstance(spec, dict):
                type_ = spec["type"]
                if not isinstance(type_, type) or not issubclass(
                    type_, (Resource, Machine)
                ):
                    raise ValueError(f"Invalid type specification for {name}")
                self.add(
                    name,
                    type_,
                    description=spec.get("description"),
                    required=spec.get("required", True),
                )
            else:
                raise ValueError(f"Invalid asset specification for {name}")

    def add(
        self,
        name: str,
        type_: AssetType,
        description: Optional[str] = None,
        required: bool = True,
    ) -> None:
        """Add a required deck asset."""
        self._assets[name] = DeckAssetSpec(name, type_, description, required)

    def validate(self, deck: Optional[Deck]) -> None:
        """Validate that all required assets exist on the deck and are of correct type."""
        if deck is None:
            raise ValueError("Deck is not initialized")

        errors = []
        for name, spec in self._assets.items():
            # Skip optional assets that don't exist
            if not spec.required and not hasattr(deck, name):
                continue

            # Check if asset exists
            if not hasattr(deck, name):
                errors.append(f"Missing required deck asset: {name}")
                continue

            # Check asset type
            asset = getattr(deck, name)
            if not isinstance(asset, spec.type):
                errors.append(
                    f"Asset {name} must be of type {spec.type.__name__}, "
                    f"got {type(asset).__name__}"
                )

        if errors:
            raise ValueError("Deck validation failed:\n" + "\n".join(errors))

    def get_spec(self, name: str) -> DeckAssetSpec:
        """Get the specification for an asset by name."""
        return self._assets[name]

    def __iter__(self):
        return iter(self._assets.values())

    def __len__(self):
        return len(self._assets)

    def __contains__(self, name: str):
        return name in self._assets
