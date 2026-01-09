# Workcell View Issues

**Created**: 2026-01-09
**Priority**: P2-P4

---

## P2: No Deck Visualizations

**Status**: Open
**Difficulty**: Hard

### Problem
The workcell view has no deck views for anything. This is related to a larger issue with dynamic deck mapping and using the deck catalog and linking decks to compatible machine backends.

### Root Cause
- Deck visualization depends on deck definitions linked to machines
- Dynamic deck mapping system incomplete
- Deck catalog not properly integrated

### Tasks

#### Investigation
- [ ] Audit current deck visualization pipeline
- [ ] Document deck catalog structure
- [ ] Map deck definition → machine backend compatibility

#### Implementation
- [ ] Fix deck data loading in workcell view
- [ ] Implement dynamic deck mapping
- [ ] Link deck catalog entries to compatible backends
- [ ] Add fallback/placeholder for machines without deck definitions

---

## P4: Workcell UI Redesign

**Status**: Open
**Difficulty**: Hard

### Problem
The workcell UI needs to be rethought and reworked.

### Context
- Current UI doesn't effectively communicate workcell state
- Deck visualizations are missing
- Machine status unclear

### Future Considerations
- Better spatial layout representation
- Real-time status updates
- Drag-and-drop configuration
- Integration with scheduler/execution monitor
