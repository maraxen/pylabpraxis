# Simulation Issues

**Created**: 2026-01-09
**Priority**: P2

---

## P2: Simulated Backend Clarity

**Status**: Resolved
**Closed**: 2026-01-14

### Problem

Unclear what the simulated backends are doing. We still have "demo" naming on simulated frontends. Are all simulated frontends using chatterbox backend? Need better frontend/backend separation.

### Context

- Current simulation architecture is confusing
- "Demo" terminology should be eliminated
- Need clear documentation of what each simulated component does

### Tasks

#### Investigation

- [x] Audit all simulated backend implementations
- [x] Document what each simulated frontend/backend pair does
- [x] Identify which use ChatterboxBackend vs other approaches

#### Cleanup

- [x] Remove all "demo" naming from simulated frontends
- [x] Use consistent "Simulated" prefix
- [x] Document simulation behavior in code comments

#### Architecture

- [x] Clarify frontend/backend separation in simulation
- [x] Consider singleton pattern for simulated frontends per category
- [x] Document simulation architecture for developers

---

## Related Technical Notes

### Current Known Issues

- Machine Backend Mismatch: "Add Machine" shows 0 backends but logs show 73 simulated backends loaded
- Likely caused by excessive simulated frontends per category

### Desired State

- Clear 1:1 mapping of simulated frontend to backend per machine category
- Consistent naming (SimulatedHamilton, SimulatedOT2, etc.)
- Documentation of what simulation provides (state tracking, timing, etc.)
