from typing import Dict, Type, Optional, Any, Union, Mapping
from dataclasses import dataclass
from pylabrobot.resources import Resource, Deck
from pylabrobot.machines import Machine
from ..workcell import Workcell

# Define a type alias for asset types
AssetType = Type[Union[Resource, Machine]]


@dataclass
class WorkcellAssetSpec:
    """Specification for a required workcell asset (resource or machine).

    Attributes:
        name: Name of the asset on the workcell
        type: Expected type of the asset (Resource or Machine)
        description: Optional description of what this asset is used for
        required: Whether this asset is required (defaults to True)
    """

    name: str
    type: AssetType
    description: Optional[str] = None
    required: bool = True


class WorkcellAssets:
    """Container for workcell asset specifications and validation logic.

    This class handles both physical resources (plates, tips, etc.) and machines
    (liquid handlers, plate readers, etc.) that are part of the workcell setup.
    """

    def __init__(
        self,
        assets: Optional[Mapping[str, Union[AssetType, Dict[str, Any]]]] = None,
    ):
        """Initialize workcell assets.

        Args:
            assets: Optional mapping of asset names to either:
                   - Asset type (e.g., {"plate": Plate} or {"reader": PlateReader})
                   - Asset spec dict (e.g., {"plate": {"type": Plate, "description": "Sample plate"}})
        """
        self._assets: Dict[str, WorkcellAssetSpec] = {}
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
        """Add a required workcell asset."""
        self._assets[name] = WorkcellAssetSpec(name, type_, description, required)

    def validate(self, workcell: Optional[Workcell]) -> None:
        """Validate that all required assets exist in the Workcell and are of correct type."""
        if workcell is None:
            raise ValueError("Deck is not initialized")

        errors = []
        for id, spec in self._assets.items():
            # Skip optional assets that don't exist
            if not spec.required and id not in workcell:
                continue

            # Check if asset exists
            if not id not in workcell:
                errors.append(f"Missing required workcell asset: {id}")
                continue

            # Check asset type
            asset = getattr(workcell, id)
            if not isinstance(asset, spec.type):
                errors.append(
                    f"Asset {id} must be of type {spec.type.__name__}, "
                    f"got {type(asset).__name__}"
                )

        if errors:
            raise ValueError("Deck validation failed:\n" + "\n".join(errors))

    def get_spec(self, id: str) -> WorkcellAssetSpec:
        """Get the specification for an asset by name."""
        return self._assets[id]

    def __iter__(self):
        return iter(self._assets.values())

    def __len__(self):
        return len(self._assets)

    def __contains__(self, id: str):
        return name in self._assets

