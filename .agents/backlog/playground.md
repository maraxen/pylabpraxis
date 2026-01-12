# Playground Issues

## 📁 Archived Items

See: [ui_ux_improvements_jan_2026.md](../archive/ui_ux_improvements_jan_2026.md)

- P1: Initialization Flow Broken
- P2: Inventory Filter Styling
- P2: Category Structure

---

## P2: WebUSB/Polyfill Audit

**Status**: Open
**Difficulty**: Hard

### Problem

Need to audit the polyfill/webusb based communication to ensure it works correctly.

### Context

- Various polyfills are used for hardware communication
- Unclear if all paths are correctly implemented

### Tasks

- [ ] Document current polyfill implementation
- [ ] Audit WebUSB communication paths
- [ ] Test with simulated and real hardware
- [ ] Document any limitations

---

---

---

## P2: Resource Filters Broken

**Status**: Open
**Difficulty**: Medium

### Problem

In asset selection and resource filtering, none of the filters are working and they look different from filters in other tabs.

### Tasks

- [ ] Investigate filter binding issues
- [ ] Align styling with other filter components
- [ ] Test all filter combinations

---

## P2: Browser Tab Categories Blank

**Status**: Open
**Difficulty**: Medium

### Problem

For the browser add tab in playground inventory, once you go to categories it shows a blank area.

### Tasks

- [ ] Debug category view rendering
- [ ] Check data binding for category list
- [ ] Verify component initialization
