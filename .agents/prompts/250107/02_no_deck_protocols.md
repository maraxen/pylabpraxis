# No-Deck Protocols (Plate Reader Only)

**Backlog**: `protocol_enhancements.md`, `TECHNICAL_DEBT.md`
**Priority**: P1 (High)
**Effort**: Large

---

## Goal

Support protocols that do not require a Liquid Handler or deck layout (e.g., standalone plate reader measurements).

## Problem

Current architecture assumes:

1. Every protocol imports `LiquidHandler`
2. `ExecutionMonitor` requires a deck layout for visualization
3. Run workflow expects deck setup step

## Example Protocol

```python
@protocol_function
async def measure_absorbance(pr: PlateReader, plate: Plate):
    """Standalone plate reader protocol - no deck required."""
    return await pr.read_absorbance(plate, wavelength=450)
```

## Tasks

### Backend

1. **Update `ProtocolDefinitionService`**
   - Don't mandate `LiquidHandler` in protocol discovery
   - Add `requires_deck: bool` field to protocol definition
   - Infer from protocol parameters (if no LH parameter, `requires_deck=False`)

2. **Update Protocol Discovery**
   - Handle protocols with only auxiliary machine parameters
   - Correctly identify machine type without assuming LH

3. **Update Execution Service**
   - Allow running protocols without deck state tracking
   - Simplify state tracking for non-deck protocols

### Frontend

1. **Update Run Protocol Wizard**
   - Skip deck setup step if `requires_deck=False`
   - Show simplified asset selection for single-machine protocols

2. **Update Execution Monitor**
   - Handle runs without deck layout
   - Show machine-centric view instead of deck-centric view
   - Display plate reader results (absorbance tables, etc.)

3. **Update Browser Mode**
   - Ensure `SqliteService` handles protocols without deck requirements

## Files to Modify

| File | Action |
|------|--------|
| `praxis/backend/services/protocol.py` | Add `requires_deck` inference |
| `praxis/backend/models/pydantic_internals/protocol.py` | Add field |
| `praxis/backend/services/discovery.py` | Update discovery logic |
| `web-client/src/app/features/run-protocol/` | Conditional deck step |
| `web-client/src/app/features/execution-monitor/` | Machine-centric view |

## Success Criteria

- [ ] Plate reader-only protocol can be discovered
- [ ] Run wizard skips deck setup for no-deck protocols
- [ ] Execution monitor displays run without deck layout
- [ ] Example protocol works in browser mode
