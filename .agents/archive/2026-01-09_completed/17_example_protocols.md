# Agent Prompt: 17_example_protocols

Examine `.agents/README.md` for development context.

**Status:** ✅ Complete  
**Batch:** [260109](./README.md)  
**Backlog:** [run_protocol_workflow.md](../../backlog/run_protocol_workflow.md)  

---

## Task

Create example protocols demonstrating no-liquid-handler workflows and rich well selection scenarios.

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [run_protocol_workflow.md](../../backlog/run_protocol_workflow.md) | Work item tracking |
| [protocol_enhancements.md](../../backlog/protocol_enhancements.md) | Plate reader protocol patterns |
| `praxis/backend/protocols/` | Protocol directory |

---

## Implementation

### 1. No Liquid Handler Protocol

```python
@protocol_function(requires_deck=False)
async def plate_reader_assay(pr: PlateReader, plate: Plate):
    """Standalone plate reader - no LH/deck required."""
    absorbance = await pr.read_absorbance(plate, wavelength=450)
    return absorbance
```

### 2. Rich Well Selection Protocol

```python
@protocol_function
async def selective_transfer(lh: LiquidHandler, source: Plate, dest: Plate):
    """Demonstrates complex well selection UI."""
    # Uses wells_source and wells_dest parameters with grid selection
    # ...
```

---

## Expected Outcome

- 2-3 example protocols added to codebase
- Tests verify protocols are discovered and analyzed
- UI displays them in protocol library

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
