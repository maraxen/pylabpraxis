# ItemizedResource Analysis

Verified the structure of `ItemizedResource` in `external/pylabrobot` for generalized UI selector support.

## 1. Grid Dimensions
**Status: Supported**

`ItemizedResource` exposes properties to determine grid dimensions, derived from the resource's item ordering (expected in transposed Excel notation, e.g., "A1", "B1").

- **Properties**:
  - `num_items_x`: Integer count of columns.
  - `num_items_y`: Integer count of rows.
- **Logic**: These are calculated dynamically via `_get_grid_size(self._ordering)`.
- **Note**: The grid calculation strictly enforces a full grid structure based on the identifiers.

## 2. Type Inspection
**Status: Supported (with Generics)**

`ItemizedResource` is a Generic class: `class ItemizedResource(Resource, Generic[T], metaclass=ABCMeta)`.

- **Runtime Access**: The item type is accessible via the `__orig_bases__` attribute on the subclass (e.g., `Plate`, `TipRack`).
- **Caveat**: The type might be a `ForwardRef` (string) or a direct class reference depending on how it was defined in the subclass.
  - **Plate**: Uses `ItemizedResource["Well"]`, resulting in a `ForwardRef('Well')`.
  - **TipRack**: Uses `ItemizedResource[TipSpot]`, resulting in the `TipSpot` class.

### Inspection Snippet
To extract the item label ("Well", "TipSpot", etc.) at runtime:

```python
import typing
from typing import ForwardRef
from pylabrobot.resources.itemized_resource import ItemizedResource

def get_item_label(resource_cls):
    if hasattr(resource_cls, "__orig_bases__"):
        for base in resource_cls.__orig_bases__:
            if typing.get_origin(base) is ItemizedResource:
                args = typing.get_args(base)
                if not args: continue
                
                item_type = args[0]
                # Handle ForwardRef (e.g. 'Well') vs Class (e.g. TipSpot)
                if isinstance(item_type, ForwardRef):
                    return item_type.__forward_arg__
                if hasattr(item_type, "__name__"):
                    return item_type.__name__
                return str(item_type)
    return "Item"
```

## 3. Usage
**Status: Confirmed**

Both key container types inherit from `ItemizedResource`, enabling a unified UI approach.

- **Plate**: `class Plate(ItemizedResource["Well"])`
- **TipRack**: `class TipRack(ItemizedResource[TipSpot], metaclass=ABCMeta)`
