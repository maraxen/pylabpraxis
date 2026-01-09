# Playground Issues

**Created**: 2026-01-09
**Priority**: P1-P2

---

## P1: Initialization Flow Broken

**Status**: Open
**Difficulty**: Medium

### Problem
User must click "reload kernel" and then click "dismiss loading button" to use playground. There's also a "WebSerial not defined" error in the Pyodide session.

### Context
- JupyterLite kernel initialization has issues
- WebSerial polyfill may not be loaded correctly
- Previous race condition fixes may have regressed

### Tasks
- [ ] Investigate kernel auto-initialization
- [ ] Fix WebSerial polyfill loading order
- [ ] Remove need for manual dismiss/reload actions
- [ ] Test initialization in both browser and production modes

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

## P2: Inventory Filter Styling

**Status**: Completed
**Difficulty**: Easy

### Problem
Playground inventory filter menu should use our styled select components.

### Tasks
- [x] Replace current filter controls with shared styled components
- [x] Ensure consistency with other asset filter UI

---

## P2: Category Structure

**Status**: Open
**Difficulty**: Easy

### Problem
Categories need to be properly structured in the quick add inventory category filter.

### Tasks
- [ ] Review category hierarchy
- [ ] Implement proper nesting/grouping
- [ ] Test filter behavior

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
