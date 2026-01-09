# Asset Management Issues

**Created**: 2026-01-09
**Priority**: P2

---

## P2: Machine Category Filters Include Backends

**Status**: Open
**Difficulty**: Easy

### Problem
Machine category filters in asset management include backends even though that doesn't make sense from a user perspective.

### Tasks
- [ ] Remove backends from category filter options
- [ ] Backend selection should be separate concern

---

## P2: Backend Names Too Long

**Status**: Open
**Difficulty**: Easy

### Problem
The backend selector has names that are too long to be useful.

### Tasks
- [ ] Implement name truncation with tooltips
- [ ] Consider abbreviated display names
- [ ] Show full name on hover

---

## P2: Backend Selector UX

**Status**: Open
**Difficulty**: Easy

### Problem
The backend selector should be disabled unless a category is selected, or we should move it to being an autocomplete which would be better.

### Recommendation
Convert to autocomplete for better UX.

### Tasks
- [ ] Implement autocomplete for backend selection
- [ ] Filter backends by selected category
- [ ] Show "Select category first" placeholder when no category

---

## P2: Add Asset Prompt Missing

**Status**: Open
**Difficulty**: Easy

### Problem
The add asset button when you're in the overview/spatial view tabs takes you to add machine when it should first prompt if you want to add a machine or resource.

### Tasks
- [ ] Add prompt dialog for asset type selection
- [ ] Options: "Add Machine" or "Add Resource"
- [ ] Navigate to appropriate flow based on selection

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
