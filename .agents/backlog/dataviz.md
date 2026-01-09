# Data Visualization Issues

**Created**: 2026-01-09
**Priority**: P2

---

## P2: Dashboard Not Responding to Selects

**Status**: Open
**Difficulty**: Medium

### Problem
The data visualization dashboard needs to actually respond to the selects we have for the x and y axis.

### Context
- Axis selectors are present in UI
- Changes to selectors don't update the visualization
- Likely a binding or subscription issue

### Tasks
- [ ] Debug selector → chart data binding
- [ ] Verify reactive subscription chain
- [ ] Test with different data configurations
- [ ] Add loading/error states for data fetching

---

## P2: Sample Data Seeding

**Status**: Open
**Difficulty**: Medium

### Problem
We should ship with some functional log well data outputs in the browser database proceeding from simulated runs.

### Context
- New users see empty visualizations
- Demo data helps users understand capabilities
- Simulated runs should produce viewable data

### Tasks
- [ ] Define sample dataset structure
- [ ] Create seed data from representative simulated runs
- [ ] Include varied well data (volumes, concentrations, etc.)
- [ ] Add to browser mode initialization
- [ ] Document sample data in user guide
