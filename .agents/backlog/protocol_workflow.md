# Protocol Workflow Issues

**Created**: 2026-01-09
**Priority**: P1-P2

---

## P1: Well Selection Not Triggering

**Status**: 🟡 In Progress (Assigned: [Prompt 13](../prompts/260109/13_protocol_well_selection_fix.md))
**Difficulty**: Medium

### Problem

Protocol run well selection is not triggering when expected.

### Context

- User reports the well selection step doesn't activate
- Possibly related to parameter type inference or form generation

### Tasks

- [ ] Investigate when well selection should trigger
- [ ] Check `isWellSelectionParameter` heuristic
- [ ] Verify form field generation for well-type parameters
- [ ] Test with various protocol signatures

---

## P1: Asset Filtering Not Working

**Status**: Open
**Difficulty**: Medium

### Problem

Autofill and asset selection is not filtered to the appropriate PyLabRobot class.

### Context

- When selecting assets for protocol execution, incompatible resources may appear
- Filter should respect PLR class hierarchy

### Tasks

- [ ] Review asset selection logic in protocol workflow
- [ ] Verify PLR class filtering in `AssetManager` or `ProtocolService`
- [ ] Ensure type compatibility checks are applied

---

## P2: Protocol Description Formatting

**Status**: Open
**Difficulty**: Easy

### Problem

Spacing and formatting of protocol description could be improved.

### Tasks

- [ ] Review protocol description display component
- [ ] Improve typography and spacing
- [ ] Ensure consistent styling with rest of UI

---

## P2: Protocol Library Filters

**Status**: Open
**Difficulty**: Medium

### Problem

No filters are implemented in the protocol library.

### Tasks

- [ ] Implement filter chips for protocol library
- [ ] Filter by: author, tags, resource requirements
- [ ] Search functionality for protocol names

---

## P2: Protocol Dialog Asset Classification

**Status**: Open
**Difficulty**: Easy

### Problem

In the dialog triggered when opening something in the protocol library, machines should be included in asset requirements, not in parameters.

### Tasks

- [ ] Review protocol detail dialog structure
- [ ] Move machine requirements to dedicated "Asset Requirements" section
- [ ] Keep only runtime parameters in "Parameters" section
