# Hardware Discovery Menu Restoration Backlog

**Priority**: P2 (High)
**Owner**: Frontend
**Created**: 2026-01-04
**Status**: Planning

---

## Overview

The hardware discovery menu needs restoration and UX improvements. Currently, discovery is triggered via various buttons across the app, but the iconography is inconsistent (magnifying glass vs USB symbol), and the simulator backend appears in the discovery list when it should be always-available separately.

---

## Goals

1. **Consistent Icon**: All hardware discovery triggers use USB symbol, not magnifying glass
2. **Unified Menu**: Single discovery menu accessible from multiple locations
3. **Exclude Simulator**: Simulator backend is always-available, not in discovery results
4. **Quick Access**: Discovery accessible from Asset Management + Command Palette

---

## Phase 1: Icon Audit & Replacement

### Current State

Hardware discovery triggers may use different icons across the app:
- Some use `search` (magnifying glass) icon
- Some use `usb` icon
- Should all use USB icon for hardware discovery

### Tasks

- [ ] **Audit All Discovery Triggers**
  - Asset Management page
  - REPL sidebar
  - Run Protocol wizard
  - Command Palette
  - Home page quick actions

- [ ] **Replace Icons**
  - Change `search` / `find` / magnifying glass icons to `usb`
  - Use Material Symbol: `usb` or `cable`
  - Consistent tooltip: "Discover Hardware"

### Files to Check

```
praxis/web-client/src/app/features/assets/
praxis/web-client/src/app/features/repl/
praxis/web-client/src/app/features/run-protocol/
praxis/web-client/src/app/features/home/
praxis/web-client/src/app/shared/components/command-palette/
praxis/web-client/src/app/shared/components/hardware-discovery-button/
```

---

## Phase 2: Hardware Discovery Menu Restoration

### Current State

The `HardwareDiscoveryButtonComponent` exists and was integrated into several locations. The menu functionality needs to be verified/restored.

### Tasks

- [ ] **Verify Menu Functionality**
  - Opens discovery dialog on click
  - Shows scanning animation during discovery
  - Lists discovered devices
  - Allows adding discovered devices

- [ ] **Ensure Access Points Work**
  - Asset Management: Quick action button
  - Command Palette: "Discover Hardware" command
  - REPL: Sidebar action
  - Run Protocol: Before machine selection

- [ ] **Menu Contents**
  - Scanning indicator
  - List of discovered devices with type/name/address
  - "Add" button for each device
  - "Refresh" button
  - Empty state message when no devices found

---

## Phase 3: Simulator Backend Exclusion

### Current Behavior

The simulator backend appears in the hardware discovery results, but it should be:
1. Always available without discovery
2. Not shown in discovery results (since it's not physical hardware)

### Tasks

- [ ] **Frontend Filtering**
  - Filter out simulator backends from discovery results
  - Identify simulator by backend type or name pattern

- [ ] **Backend Configuration**
  - Mark simulator backends as `simulator: true`
  - Discovery service excludes simulators

- [ ] **Simulator Always-Available**
  - Add "Simulator" section in machine selection
  - Available without any discovery step
  - Clear labeling: "Simulated [Machine Type]"

### Simulator Identification

```typescript
// Possible patterns to identify simulators
const isSimulator = (backend: MachineBackend) => {
  return backend.type.includes('Simulator') ||
         backend.name.toLowerCase().includes('simulator') ||
         backend.simulator === true;
};
```

---

## Phase 4: Discovery Quick Access

### Tasks

- [ ] **Asset Management Quick Action**
  - Prominent "Discover Hardware" button in toolbar
  - USB icon
  - Opens discovery dialog

- [ ] **Command Palette Integration**
  - "Discover Hardware" command registered
  - Keyboard shortcut (e.g., Ctrl+Shift+H)
  - Opens same discovery dialog

- [ ] **Home Page Action**
  - Quick action card or button
  - "Connect to Hardware" or similar

---

## Technical Considerations

### Discovery Service

The discovery functionality should be centralized:
- `HardwareDiscoveryService` handles mDNS/serial enumeration
- Dialog component presents results
- Multiple trigger points all use same service/dialog

### Device Types

Discovery should detect:
- mDNS-advertised devices (network-connected)
- USB Serial devices (directly connected)
- Bluetooth devices (future?)

### Timeout & Error Handling

- Discovery timeout (5-10 seconds)
- Network error handling
- Partial results display

---

## Files to Modify

| File | Action |
|------|--------|
| `hardware-discovery-button.component.ts` | Update icon, verify functionality |
| `hardware-discovery-dialog.component.ts` | Ensure proper filtering |
| `assets.component.ts` | Add/verify discovery button |
| `command-palette.component.ts` | Add discovery command |
| `home.component.ts` | Add discovery quick action |
| `machine-selection.component.ts` | Add simulator section |

---

## Success Criteria

1. [ ] All hardware discovery triggers use USB icon
2. [ ] Discovery menu opens from Asset Management
3. [ ] Discovery menu opens from Command Palette
4. [ ] Simulator backend NOT in discovery results
5. [ ] Simulator always-available in machine selection
6. [ ] Consistent discovery UX across all entry points
