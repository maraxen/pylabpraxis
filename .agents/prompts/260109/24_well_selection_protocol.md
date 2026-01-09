# Agent Prompt: 24_well_selection_protocol

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Batch:** [260109](./README.md)  
**Backlog:** [dataviz_well_selection.md](../../backlog/dataviz_well_selection.md)  

---

## Task

Create an example protocol that triggers the Well Selector Dialog in the protocol run workflow. Demonstrates rich well selection UX.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [visual_well_selection.md](../../backlog/visual_well_selection.md) | Requirements |
| `praxis/backend/protocols/` | Protocol directory |
| `praxis/web-client/src/app/features/run-protocol/` | Run workflow |

---

## Protocol Implementation

### Example: Selective Transfer

```python
from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.resources import Plate, Well
from praxis.backend.core.protocol import protocol_function

@protocol_function
async def selective_well_transfer(
    lh: LiquidHandler,
    source_plate: Plate,
    dest_plate: Plate,
    source_wells: list[Well],  # ← Triggers Well Selector
    dest_wells: list[Well],    # ← Triggers Well Selector
    volume: float = 100.0,
):
    """
    Transfer liquid from selected source wells to destination wells.
    
    This protocol demonstrates the rich well selection UI where users
    can visually pick wells from a plate grid.
    """
    for src, dst in zip(source_wells, dest_wells):
        await lh.aspirate([src], volume)
        await lh.dispense([dst], volume)
    
    return {"transferred_wells": len(source_wells)}
```

### Frontend Detection

The protocol analyzer should detect `list[Well]` parameter type and:

1. Infer which plate the wells belong to (via parameter name or metadata)
2. Render "Select Wells" button in parameter config step
3. Open Well Selector Dialog on click
4. Store selection as well identifiers

---

## Integration Flow

```
Protocol Selection → Parameter Config Step
                          ↓
                    [Select Source Wells] button
                          ↓
                    Well Selector Dialog opens
                          ↓
                    User selects A1-A6
                          ↓
                    Config shows "6 wells selected"
                          ↓
                    Continue to next step
```

---

## Testing

1. Protocol appears in library
2. Clicking "Select Wells" opens dialog
3. Selections persist across step navigation
4. Execution receives correct well list

---

## Project Conventions

- **Commands**: Use `uv run` for all Python commands
- **Backend Tests**: `uv run pytest tests/ -v`

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
