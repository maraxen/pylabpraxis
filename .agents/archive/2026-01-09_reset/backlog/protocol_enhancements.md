# Protocol Enhancements

**Priority**: P2-P3 (Mixed)
**Owner**: Full Stack
**Created**: 2026-01-06 (consolidated from 4 files)
**Status**: Active

---

## Overview

This document consolidates all protocol-related enhancement work.

---

## 1. Protocol Execution Improvements

### Run Workflow

- [x] **Asset Selection Step**: ✅ Complete (verified 2026-01-06)
  - See `run_protocol_workflow.md` for details

### Execution Monitor

- [ ] State delta display at each operation (Phase 8.4)
- [ ] Better error visualization

---

## 2. Protocol Inspection

### Static Analysis

- CST parsing ✅ Complete
- Computation graph ✅ Complete  
- Requirement inference ✅ Complete

### Remaining Work

- [ ] Edge case documentation ("sharp bits")
- [ ] Better error messages for invalid protocols

---

## 3. Protocol Setup Instructions

Deck setup wizard is ✅ Complete (archived).

### Remaining Work

- [ ] Improve instruction clarity for complex protocols
- [ ] Multi-machine protocol setup flow

---

## 4. Plate Reader Protocols (LH-less) ✅

**Status**: Implemented (2026-01-07)

### Completed Work

- [x] Update `ProtocolDefinitionService` to not mandate LH imports
- [x] Add `requires_deck` field to protocol definitions
- [x] Auto-detect based on parameter types (infer from LH/Deck presence)
- [x] Support explicit `@protocol_function(requires_deck=False)` override
- [x] Adapt Run Wizard to skip deck setup for no-deck protocols

### Example Use Case

```python
@protocol_function
async def measure_absorbance(pr: PlateReader, plate: Plate):
    """Standalone plate reader protocol."""
    return await pr.read_absorbance(plate, wavelength=450)
```

---

## Related Documents

- [simulation_ui_integration.md](./simulation_ui_integration.md) - Simulation results display
- [TECHNICAL_DEBT.md](../TECHNICAL_DEBT.md) - Plate reader protocols tracked
