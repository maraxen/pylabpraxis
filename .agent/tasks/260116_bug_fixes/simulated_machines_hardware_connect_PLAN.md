# Plan: Hide Simulated Machines in Hardware Connect

## Goal

Prevent "Simulated" machines (which are internal software constructs) from appearing in the "Connect to Hardware" dialog. This dialog is strictly for connecting to physical hardware (via WebSerial/WebUSB or Backend Driver).

## Context

- **Issue**: Simulated machines (e.g., "Simulated Liquid Handler") appear in the list of discovered devices.
- **Root Cause**: The current filter in `HardwareDiscoveryDialogComponent` checks `connectionType !== 'simulator'` and string matches on the backend name, but does not check the robust `is_simulated_frontend` flag present in `PlrMachineDefinition`.
- **Files**:
  - `praxis/web-client/src/app/shared/components/hardware-discovery-dialog/hardware-discovery-dialog.component.ts`
  - `praxis/web-client/src/assets/browser-data/plr-definitions.ts` (Reference only)

## User Review Required
>
> [!NOTE]
> This change strictly affects the visibility of devices in the "Hardware Discovery" dialog. It does not delete or alter the machines themselves.

## Proposed Changes

### Shared Components

#### [MODIFY] [hardware-discovery-dialog.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/shared/components/hardware-discovery-dialog/hardware-discovery-dialog.component.ts)

Update the `filteredDevices` computed signal to explicitly exclude devices where the associated PLR definition is marked as simulated.

```typescript
    readonly filteredDevices = computed(() => {
        return this.hardwareService.discoveredDevices().filter(d =>
            d.connectionType !== 'simulator' &&
            !(d.plrBackend && d.plrBackend.toLowerCase().includes('simulator')) &&
            // [NEW] Check generic definition flag
            !d.plrMachineDefinition?.is_simulated_frontend
        );
    });
```

## Verification Plan

### Automated Tests

- Run existing unit tests for the component (if any).
- If no unit tests exist for this component's filtering logic, we will rely on manual verification (see below) as adding complex unit tests for a dialog component in this phase might be out of scope, but we can check `hardware-discovery-dialog.component.spec.ts` if it exists.

### Manual Verification

1. **Launch Browser Mode**: `npm run start:browser`
2. **Open Hardware Connect**: Click the "Connect Hardware" button (USB icon) in the header.
3. **Verify**:
    - Ensure "Simulated Liquid Handler" and other simulated devices are **NOT** listed.
    - (Optional) If you have a real Serial device (or can mock one), ensure it **DOES** appear.
