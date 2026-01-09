# Asset Management Issues

**Created**: 2026-01-09
**Priority**: P2

---

## P2: Machine Category Filters Include Backends

**Status**: Completed
**Difficulty**: Easy

### Problem
Machine category filters in asset management include backends even though that doesn't make sense from a user perspective.

### Tasks
- [x] Remove backends from category filter options
- [x] Backend selection should be separate concern

---

## P2: Backend Names Too Long

**Status**: Completed
**Difficulty**: Easy

### Problem
The backend selector has names that are too long to be useful.

### Tasks
- [x] Implement name truncation with tooltips
- [x] Consider abbreviated display names
- [x] Show full name on hover

---

## P2: Backend Selector UX

**Status**: Completed
**Difficulty**: Easy

### Problem
The backend selector should be disabled unless a category is selected, or we should move it to being an autocomplete which would be better.

### Recommendation
Implemented gating in MachineDialog stepper and added defensive UI.

### Tasks
- [x] Enforce linear stepper flow with gating
- [x] Add defensive UI for Step 2 when no category selected
- [x] Ensure "Next" button properly gates progression

---

## P2: Add Asset Prompt Missing

**Status**: Completed
**Difficulty**: Easy

### Problem
The add asset button when you're in the overview/spatial view tabs takes you to add machine when it should first prompt if you want to add a machine or resource.

### Tasks
- [x] Add prompt dialog for asset type selection
- [x] Options: "Add Machine" or "Add Resource"
- [x] Navigate to appropriate flow based on selection

---

## P2: Registry UI Issues

**Status**: Open
**Difficulty**: Medium

### Problem
The add machine button links to the add resource button. Add resource says "definitions are precinct in browser mode". We need a better UI for the registry.

### Tasks
- [ ] Fix navigation between add machine/resource
- [ ] Improve browser mode messaging for registry limitations
- [ ] Design clearer registry interface
- [ ] Consider read-only registry view for browser mode
