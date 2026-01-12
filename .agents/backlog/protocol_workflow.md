# Protocol Workflow Issues

## 📁 Archived Items

See: [ui_ux_improvements_jan_2026.md](../archive/ui_ux_improvements_jan_2026.md)

- P1: Well Selection Not Triggering
- P2: Protocol Dialog Asset Classification

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
